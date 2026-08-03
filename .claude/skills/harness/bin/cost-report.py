#!/usr/bin/env python3
"""Measure what a harness run actually cost, attributed per agent.

  cost-report.py [--project <dir>] [--session <id>] [--since <ISO date>]
                 [--yaml [--into <state.yaml>]] [--cross-check]

  (default)      human-readable breakdown per agent, per depth, per model
  --yaml         emit the `cost:` block for a run's state.yaml
  --into <path>  with --yaml, REPLACE that state.yaml's cost: block in place —
                 the correct way to fill a lead's `cost: pending_orchestrator`
                 placeholder. Never `>>` append: a second `cost:` key is silently
                 shadowed by the last one and violates INV-16 (DEC-156).
  --cross-check  compare the computed total against ccusage, if installed

WHY THIS EXISTS AND WHAT IT IS NOT
==================================
DEC-99 moved cost from a pre-build gate to the post-build signal, which makes
instrumentation mandatory: you cannot monitor what you do not log. SC-1 kills
the org above $50/feature, so the number has to be real.

**This script does NOT own the dollars — it owns the ATTRIBUTION.**

Claude Code already computes cost natively: `CLAUDE_CODE_ENABLE_TELEMETRY=1`
emits `claude_code.cost.usage` in USD over OpenTelemetry, and `ccusage`
(npx ccusage@latest, MIT, offline) reports the same from these very transcripts.
Both are better sources of a *total* than a hand-maintained rate table.

What neither gives you is **cost per harness agent**. The OTel `agent.name`
attribute documents that "Other user-defined agent names are replaced with
'custom'" — and all 16 harness agents are user-defined, so they collapse into a
single bucket. ccusage aggregates per session/model/day, not per agent role.
Per-agent, per-depth, per-team cost is precisely the axis DEC-99 wants watched,
and this script is the only thing that produces it.

So: use ccusage or OTel for ground truth, use this for the breakdown, and run
`--cross-check` to catch the rate table going stale.

THE MODELLING TRAP, MEASURED
============================
The four token classes have wildly different prices and MUST be priced apart:

    cache read      0.10x base input     <- usually the LARGEST volume
    5m cache write  1.25x
    1h cache write  2.00x                <- 1.6x the 5m write
    output          5.00x

A real dev-ops detection spawn (DEC-114): 862,903 cache-read tokens, 88,414
cache-write, 14,993 output, 79 input. Priced correctly on claude-fable-5 that is
$2.72. Priced with cache reads at base input rate it reads as $11.35 — a 4x
overstatement of the run, driven entirely by mispricing its biggest token class.

Zero dependencies. Exit 0 = reported. Exit 1 = could not price something.
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

CLASSES = ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read")


def find_config(start):
    """Walk up for .harness/harness.json — the rate table lives with the project."""
    d = os.path.abspath(start)
    while True:
        p = os.path.join(d, ".harness", "harness.json")
        if os.path.isfile(p):
            return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def rate_for(model, speed, geo, cm, on_date):
    """Resolved per-MTok rates for one (model, speed, inference_geo), or None.

    Returns None rather than guessing, for an unknown model OR an unknown
    modifier value. Both are UNPRICED and exit 1 — silently pricing an
    unrecognised combination at the standard rate is how a cost gate reports
    confident wrong numbers, which is worse than reporting none.
    """
    mods = cm.get("modifiers") or {}

    # Fast mode is not a multiplier: it has its own published rates, and only on
    # some models. An unlisted model at fast speed is unpriceable, not standard.
    base = None
    if speed and speed != "standard":
        spec = ((mods.get("speed") or {}).get(speed) or {}).get("rates") or {}
        if model not in spec:
            return None
        base = dict(spec[model])
    else:
        for period in (cm.get("rates") or {}).get(model, []):
            if period.get("from", "0000") <= on_date <= period.get("until", "9999"):
                base = {c: period[c] for c in CLASSES}
                break
    if base is None:
        return None

    geo_tbl = mods.get("inference_geo") or {}
    mult = geo_tbl.get(geo)
    if mult is None or not isinstance(mult, (int, float)):
        return None
    return {c: base[c] * mult for c in CLASSES}


def transcript_dir(project_dir):
    """Claude Code's per-project transcript dir: the path with / and . as dashes."""
    munged = re.sub(r"[/.]", "-", os.path.abspath(project_dir))
    return os.path.join(os.path.expanduser("~/.claude/projects"), munged)


def tally(path):
    """Sum the five token classes, keyed by (model, speed, inference_geo).

    Keying on model alone is a silent halving. `speed: "fast"` bills Opus 5 at
    $10/$50 instead of $5/$25 and is one `/fast` away in any session, and
    `inference_geo: "us"` applies 1.1x to every class. Both are recorded per
    message, so there is no excuse for assuming standard.

    cache_creation_input_tokens is the TOTAL of both write TTLs; the per-TTL
    split lives in the nested `cache_creation` object. Read the nested values
    and fall back to the total only when the breakdown is absent — attributing
    a 1h write at the 5m rate under-reports it by 37%.
    """
    per_model = defaultdict(lambda: defaultdict(int))
    first_ts = last_ts = None
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        msg = d.get("message") or {}
        usage = msg.get("usage")
        if not usage:
            continue
        ts = d.get("timestamp")
        if ts:
            first_ts = min(first_ts or ts, ts)
            last_ts = max(last_ts or ts, ts)
        u_speed = usage.get("speed") or "standard"
        u_geo = usage.get("inference_geo") or "not_available"
        t = per_model[(msg.get("model") or "unknown", u_speed, u_geo)]
        t["_turns"] += 1
        t["input"] += usage.get("input_tokens") or 0
        t["output"] += usage.get("output_tokens") or 0
        t["cache_read"] += usage.get("cache_read_input_tokens") or 0
        cc = usage.get("cache_creation") or {}
        w5 = cc.get("ephemeral_5m_input_tokens")
        w1 = cc.get("ephemeral_1h_input_tokens")
        if w5 is None and w1 is None:
            # No per-TTL breakdown. Attribute to 5m and say so — the cheaper of
            # the two, so the total is a floor rather than an inflated guess.
            t["cache_write_5m"] += usage.get("cache_creation_input_tokens") or 0
            t["_ttl_unknown"] += usage.get("cache_creation_input_tokens") or 0
        else:
            t["cache_write_5m"] += w5 or 0
            t["cache_write_1h"] += w1 or 0
    return per_model, first_ts, last_ts


def price(tokens, rate):
    return sum(tokens.get(c, 0) * rate[c] / 1_000_000 for c in CLASSES)


def splice_cost(path, block):
    """REPLACE the `cost:` block in a run's state.yaml; never append a second one (B-4).

    The docs used to say `--yaml >> state.yaml`. A lead sets `cost: pending_orchestrator`
    as its placeholder, so appending produced a SECOND top-level `cost:` key — which every
    YAML parser resolves to the last occurrence, silently shadowing the first, and which
    INV-16/DEC-156 rejects. The FEAT-02 audit found `cost:` twice in 12 of 15 state files.
    Making the splice mechanical removes the footgun instead of warning about it.
    """
    if not os.path.isfile(path):
        print(f"cost-report: no such state file: {path}", file=sys.stderr)
        return 1
    try:
        src = open(path, encoding="utf-8").read().splitlines()
    except OSError as e:
        print(f"cost-report: cannot read {path}: {e}", file=sys.stderr)
        return 1

    out, i, replaced = [], 0, 0
    while i < len(src):
        if re.match(r"^cost:", src[i]):
            replaced += 1
            i += 1
            # Consume the old block's indented continuation lines, so a placeholder and a
            # previously-written full block are both swallowed whole.
            while i < len(src) and (not src[i].strip() or src[i][:1] in (" ", "\t")):
                if not src[i].strip() and not any(
                        j < len(src) and src[j][:1] in (" ", "\t") and src[j].strip()
                        for j in range(i + 1, min(i + 3, len(src)))):
                    break          # a blank line ending the block, not one inside it
                i += 1
            # Emit at the FIRST occurrence only. Emitting per occurrence is how the first
            # version of this function left two cost: keys behind while reporting that it
            # had collapsed them — the exact defect it exists to remove.
            if replaced == 1:
                out.extend(block)
            continue
        out.append(src[i])
        i += 1

    if replaced == 0:
        # No placeholder to replace: append once, which is correct precisely because
        # there is no existing key to shadow.
        if out and out[-1].strip():
            out.append("")
        out.extend(block)
    elif replaced > 1:
        print(f"cost-report: {path} had {replaced} cost: keys — collapsed to one. "
              f"A repeated key was silently shadowing the others (INV-16).", file=sys.stderr)

    try:
        open(path, "w", encoding="utf-8").write("\n".join(out).rstrip("\n") + "\n")
    except OSError as e:
        print(f"cost-report: cannot write {path}: {e}", file=sys.stderr)
        return 1
    return 0


def main():
    args = list(sys.argv[1:])
    as_yaml = "--yaml" in args
    cross = "--cross-check" in args
    args = [a for a in args if a not in ("--yaml", "--cross-check")]

    def opt(name, default=None):
        if name in args:
            i = args.index(name)
            v = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]
            return v
        return default

    into = opt("--into")
    project = os.path.abspath(opt("--project", os.getcwd()))
    only_session = opt("--session")
    since = opt("--since", "0000-00-00")

    cfg_path = find_config(project)
    if not cfg_path:
        print(f"cost-report: no .harness/harness.json at or above {project}", file=sys.stderr)
        return 1
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    cm = cfg.get("cost_model") or {}
    rates = cm.get("rates") or {}
    budgets = cfg.get("budgets") or {}
    if not rates:
        print("cost-report: harness.json has no cost_model.rates — run /harness-init --upgrade.",
              file=sys.stderr)
        return 1

    tdir = transcript_dir(project)
    if not os.path.isdir(tdir):
        print(f"cost-report: no transcripts for this project at {tdir}", file=sys.stderr)
        return 1

    # agent label -> model -> token class -> count
    rows = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    spawns = defaultdict(int)
    latest = since

    for entry in sorted(os.listdir(tdir)):
        sess = entry[:-6] if entry.endswith(".jsonl") else entry
        if only_session and sess != only_session:
            continue
        # The main-session transcript: the orchestrator's own spend.
        main = os.path.join(tdir, sess + ".jsonl")
        if os.path.isfile(main):
            per_model, _, last = tally(main)
            for key, t in per_model.items():
                if last and last[:10] < since:
                    continue
                latest = max(latest, (last or "")[:10] or since)
                for k, v in t.items():
                    rows[("orchestrator", 0)][key][k] += v
        # Subagent transcripts, each with a meta.json naming the agent type.
        sub = os.path.join(tdir, sess, "subagents")
        if not os.path.isdir(sub):
            continue
        for f in sorted(os.listdir(sub)):
            if not f.endswith(".meta.json"):
                continue
            meta = json.load(open(os.path.join(sub, f), encoding="utf-8"))
            jl = os.path.join(sub, f[: -len(".meta.json")] + ".jsonl")
            if not os.path.isfile(jl):
                continue
            per_model, _, last = tally(jl)
            if last and last[:10] < since:
                continue
            latest = max(latest, (last or "")[:10] or since)
            key = (meta.get("agentType") or "unknown", meta.get("spawnDepth", 1))
            spawns[key] += 1
            for mkey, t in per_model.items():
                for k, v in t.items():
                    rows[key][mkey][k] += v

    if not rows:
        print("cost-report: no usage found for the requested scope.")
        return 0

    total = 0.0
    unpriced = []
    ttl_unknown = 0
    lines = []
    for (agent, depth), models in sorted(rows.items()):
        for key, t in sorted(models.items()):
            ttl_unknown += t.get("_ttl_unknown", 0)
            model, speed, geo = key
            r = rate_for(model, speed, geo, cm, latest)
            if not r:
                unpriced.append((agent, f"{model} speed={speed} geo={geo}"))
                continue
            c = price(t, r)
            total += c
            label = model if (speed == "standard" and geo in ("global", "not_available")) \
                else f"{model} [{speed}/{geo}]"
            lines.append((c, agent, depth, label, spawns.get((agent, depth), 1), dict(t)))
    lines.sort(reverse=True, key=lambda x: x[0])

    # Context watchdog (DEC-148): cache_read / turns ≈ average context re-read per
    # turn. Cost grows ~quadratically with session length, so a high ratio is the
    # early signal of a context that should have been relayed to a fresh spawn —
    # it shows up here months before it shows up as a four-digit cost line.
    cpt_threshold = int(budgets.get("context_per_turn_tokens") or 200_000)
    watchdog = []
    for c, agent, depth, model, n, t in lines:
        turns = t.get("_turns", 0)
        if turns >= 20:  # ratios over a handful of turns are noise
            cpt = t.get("cache_read", 0) // max(turns, 1)
            if cpt > cpt_threshold:
                watchdog.append((cpt, agent, depth, model, turns))
    watchdog.sort(reverse=True)

    if as_yaml:
        out = ["cost:",
               "  currency: usd",
               f"  total: {round(total, 4)}",
               f"  priced_on: {latest}",
               f"  rates_verified_on: {cm.get('verified_on', 'unknown')}",
               f"  spawns: {sum(spawns.values())}",
               "  by_agent:"]
        for c, agent, depth, model, n, t in lines:
            out.append(f"    - {{ agent: {agent}, depth: {depth}, spawns: {n}, "
                       f"model: {model}, usd: {round(c, 4)}, "
                       f"in: {t.get('input',0)}, out: {t.get('output',0)}, "
                       f"cw5m: {t.get('cache_write_5m',0)}, cw1h: {t.get('cache_write_1h',0)}, "
                       f"cr: {t.get('cache_read',0)} }}")
        if watchdog:
            out.append(f"  context_watchdog:   # avg cache-read/turn over {cpt_threshold:,} tokens — relay to a fresh spawn (DEC-148)")
            for cpt, agent, depth, model, turns in watchdog:
                out.append(f"    - {{ agent: {agent}, depth: {depth}, model: {model}, "
                           f"turns: {turns}, context_per_turn: {cpt} }}")
        if unpriced:
            out.append("  unpriced:")
            for a, m in unpriced:
                out.append(f"    - {{ agent: {a}, model: {m} }}")

        if into:
            rc = splice_cost(into, out)
            if rc:
                return rc
            print(f"cost-report: wrote the cost: block into {into}", file=sys.stderr)
            return 1 if unpriced else 0
        print("\n".join(out))
        return 1 if unpriced else 0

    print(f"\nharness cost — {project}")
    print(f"  rates verified {cm.get('verified_on','unknown')}, priced at {latest}")
    print(f"  {sum(spawns.values())} subagent spawn(s)\n")
    print(f"  {'agent':<28} {'d':>1} {'n':>3} {'model':<18} {'USD':>8}   tokens (in/out/w5m/w1h/read)")
    # `n` counts spawns per (agent, depth); a single spawn can span several models,
    # so print it once per agent and blank it on that agent's extra model rows —
    # repeating it reads as N spawns per model, which would inflate the count.
    seen_key = set()
    for c, agent, depth, model, n, t in lines:
        shown = "" if (agent, depth) in seen_key else str(n)
        seen_key.add((agent, depth))
        print(f"  {agent:<28} {depth:>1} {shown:>3} {model:<18} {c:>8.4f}   "
              f"{t.get('input',0):,}/{t.get('output',0):,}/"
              f"{t.get('cache_write_5m',0):,}/{t.get('cache_write_1h',0):,}/"
              f"{t.get('cache_read',0):,}")
    print(f"\n  {'TOTAL':<28} {'':>1} {'':>3} {'':<18} {total:>8.4f}")

    if watchdog:
        print(f"\n  CONTEXT WATCHDOG — avg cache-read/turn over {cpt_threshold:,} tokens (relay to a fresh spawn, DEC-148):")
        for cpt, agent, depth, model, turns in watchdog:
            print(f"    {agent:<28} {model:<18} {turns:>5} turns   {cpt:,}/turn")

    per_feature = budgets.get("per_feature_usd")
    if per_feature:
        frac = total / per_feature
        warn_at = budgets.get("warn_at_fraction", 0.7)
        flag = "OVER BUDGET" if frac >= 1 else ("approaching budget" if frac >= warn_at else "")
        print(f"  {frac * 100:.0f}% of the ${per_feature:.0f}/feature budget. {flag}")

    if ttl_unknown:
        print(f"\n  note: {ttl_unknown:,} cache-write tokens had no TTL breakdown and were "
              f"priced at the 5m rate — the total is a FLOOR for those.")
    if unpriced:
        print("\n  UNPRICED — these ran but could not be costed:")
        for a, m in unpriced:
            print(f"    {a} on {m}: no rate period covering {latest}")
        print("  Add the model (or a current rate period) to cost_model.rates in harness.json.")

    if cross:
        print("\n  cross-check against ccusage (ground truth for dollars):")
        try:
            r = subprocess.run(["npx", "--yes", "ccusage@latest", "--json"],
                               capture_output=True, text=True, timeout=180)
            if r.returncode != 0:
                print(f"    ccusage unavailable (exit {r.returncode}) — skipped, not a failure.")
            else:
                print("    ccusage reported (compare its total against ours; a gap beyond a few")
                print("    percent means THIS script's rate table is stale, not that ccusage is wrong):")
                print("    " + "\n    ".join(r.stdout.strip().splitlines()[:12]))
        except FileNotFoundError:
            print("    npx not found — ccusage is an optional cross-check, never a dependency.")
        except subprocess.TimeoutExpired:
            print("    ccusage timed out — skipped.")

    return 1 if unpriced else 0


if __name__ == "__main__":
    sys.exit(main())
