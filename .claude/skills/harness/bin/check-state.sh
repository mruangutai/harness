#!/usr/bin/env bash
# Deterministic state-invariant checker. Run at every /harness entry.
#
# WHY THIS EXISTS: the orchestrator is an LLM performing ~15 bookkeeping duties
# per cycle with nothing validating any of them. A skipped duty is silent, and a
# bad STATE.md write poisons every subsequent spawn. The precedent is DEC-19 —
# prose guarding a safety claim is unenforceable — so the same answer applies:
# judgment routes, a script audits the bookkeeping.
#
# Exit 0 = all invariants hold. Exit 1 = violations found (printed).
# This gates the ORCHESTRATOR, not a tool call, so exit 1 is correct here;
# the exit-2 rule applies only to PreToolUse hooks.
set -uo pipefail
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$root"

python3 - "$root" <<'PY'
import sys, os, re, glob, json

root = sys.argv[1]
H = os.path.join(root, ".harness")
bad, warn = [], []

def read(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception:
        return None

if not os.path.isdir(H):
    print("harness: no .harness/ — project not onboarded. Run /harness-init.")
    sys.exit(1)

# BRIEF/PLAN are PER-FEATURE since DEC-129 — .harness/features/<FEAT>/{BRIEF,PLAN}.md.
# Root-level singletons collided the moment a second feature existed.
briefs = {os.path.basename(os.path.dirname(p)): read(p)
          for p in glob.glob(os.path.join(H, "features", "*", "BRIEF.md"))}
plans  = {os.path.basename(os.path.dirname(p)): read(p)
          for p in glob.glob(os.path.join(H, "features", "*", "PLAN.md"))}
# STATE.md is per-feature since DEC-120; read them all.
states = {os.path.basename(os.path.dirname(p)): read(p)
          for p in glob.glob(os.path.join(H, "features", "*", "STATE.md"))}

def approved(txt):
    if not txt: return False
    m = re.search(r"^##\s+Approval\s*$(.*?)(?=^##\s|\Z)", txt, re.M | re.S)
    return bool(m) and re.search(r"status:\s*approved", m.group(1), re.I) is not None

def has_approval_block(txt):
    return bool(txt) and re.search(r"^##\s+Approval\s*$", txt, re.M) is not None

# --- INV-1/2: every feature's goal of record must be signed before its flows run.
# Onboarding itself is signalled by harness.json + team-config.yaml (DEC-129), not a BRIEF:
# a freshly-onboarded project legitimately has zero features yet.
if not os.path.isfile(os.path.join(H, "harness.json")):
    bad.append(".harness/harness.json missing — not onboarded (or half-onboarded). Run /harness-init.")
for feat, brief in briefs.items():
    if not has_approval_block(brief):
        bad.append(f"{feat}/BRIEF.md has no '## Approval' section — cannot tell if the goal is signed.")
    elif not approved(brief):
        bad.append(f"{feat}/BRIEF.md is NOT approved — halt that flow and surface to the user.")
for feat in states:
    if feat not in briefs:
        bad.append(f"{feat} has STATE.md but no BRIEF.md — a flow is running with no goal of record.")

# --- INV-3: a plan must be signed too, and re-planning must reset that signature.
for feat, plan in plans.items():
    if not has_approval_block(plan):
        bad.append(f"{feat}/PLAN.md has no '## Approval' section.")
    elif not approved(plan):
        warn.append(f"{feat}/PLAN.md approval is pending — awaiting the user.")

    # --- INV-4: every task must carry change_type or the qa gate cannot apply.
    # Tasks may be list items (`- T-01:`) or headings (`### T-01 —`) — the smoke's pm
    # wrote headings and the list-only regex made this check silently vacuous (DEC-129).
    tasks = re.findall(r"^(?:-\s*|#+\s*)(T-\d+)\b(.*?)(?=^(?:-\s*|#+\s*)T-\d+\b|\Z)",
                       plan, re.M | re.S)
    if not tasks and re.search(r"\bT-\d+\b", plan):
        bad.append(f"{feat}/PLAN.md mentions T-NN ids but none parse as tasks — "
                   f"INV-4/5 would be vacuous. Fix the task format.")
    for tid, body in tasks:
        if "change_type:" not in body:
            bad.append(f"{feat}: {tid} has no change_type: — the qa gate cannot be applied to it.")

    # --- INV-5: no flow's STATE may point at a task its plan does not contain.
    state = states.get(feat)
    if state:
        plan_ids = {tid for tid, _ in tasks}
        for tid in set(re.findall(r"\bT-\d+\b", state)):
            if tid not in plan_ids:
                bad.append(f"{feat}/STATE.md references {tid}, which is absent from its PLAN.md.")

# --- INV-6..8: per-feature execution facts.
for fy in glob.glob(os.path.join(H, "features", "*", "feature.yaml")):
    feat = os.path.basename(os.path.dirname(fy))
    txt = read(fy) or ""
    def val(k):
        m = re.search(rf"^{k}:\s*(\S+)", txt, re.M)
        return m.group(1) if m else None

    runs = re.findall(r"\{\s*id:\s*([^,]+),\s*squad:\s*([^,]+),\s*verdict:\s*([^\s}]+)", txt)

    # INV-6: reviewers must diff a pinned SHA, never a moving HEAD (DEC-50).
    if any(sq.strip() == "validator" for _, sq, _ in runs) and not val("review_sha"):
        bad.append(f"{feat}: a validator run exists but review_sha is not pinned "
                   f"— reviewers would diff HEAD (the GAP-7 failure).")

    # INV-7: the fix-loop bound must actually count the failures it bounds.
    fails = sum(1 for _, _, v in runs if v.strip().upper() == "FAIL")
    cu = val("cycles_used")
    if cu is not None and cu.isdigit() and int(cu) < fails:
        bad.append(f"{feat}: cycles_used={cu} but {fails} FAIL run(s) recorded "
                   f"— the fix loop is no longer bounded.")

    # INV-8: a referenced run dir must exist, or resume has nothing to read.
    for rid, _, _ in runs:
        d = os.path.join(os.path.dirname(fy), "runs", rid.strip())
        if not os.path.isdir(d):
            warn.append(f"{feat}: run {rid.strip()} is referenced but its dir is absent "
                        f"(pruned, or never created).")

# --- INV-9: platform prerequisites that fail SILENTLY if absent (DEC-100).
sett = None
for p in (".claude/settings.json", ".claude/settings.local.json"):
    t = read(os.path.join(root, p))
    if t:
        try: sett = (sett or {}) | json.loads(t)
        except Exception: warn.append(f"{p} is not valid JSON.")
if sett is None:
    bad.append("No .claude/settings.json — the spawn-depth and Expertise-injection "
               "prerequisites are unset, and both degrade silently.")
else:
    depth = (sett.get("env") or {}).get("CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH")
    if depth != "3":
        bad.append(f"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH is {depth!r}, expected \"3\". "
                   f"The org needs 3 layers below the main session: orchestrator, lead, "
                   f"member (DEC-120). At 2 the members layer cannot be reached.")
    hooks = sett.get("hooks") or {}
    if not hooks.get("SubagentStart"):
        bad.append("No SubagentStart hook — every agent starts with NO Expertise, "
                   "and no error is raised.")
    # Agent-frontmatter PreToolUse does not fire (DEC-110), so this registration is
    # the ONLY thing enforcing domains. Its absence is silent and fail-open.
    stop = hooks.get("SubagentStop") or []
    if not any("validate-digest" in str(h) for h in stop):
        bad.append("No SubagentStop validate-digest hook — malformed digests are accepted "
                   "silently and the runner routes on fields that are not there (DEC-122).")
    pre = hooks.get("PreToolUse") or []
    if not any("check-domain" in str(h) for h in pre):
        bad.append("No PreToolUse check-domain hook — domain enforcement is ABSENT "
                   "and every agent can write anywhere. Frontmatter hooks do not "
                   "fire (DEC-110), so settings.json is the only place this works.")

# --- INV-11: cost is the post-build signal (DEC-99), so an unmetered completed run
# is a hole in the only evidence SC-1 will be judged on. Cheap to enforce, and the
# failure is otherwise invisible — a run with no cost block looks exactly like a free one.
cfg = read(os.path.join(H, "harness.json"))
if cfg:
    try:
        cj = json.loads(cfg)
    except Exception:
        cj = {}
        bad.append(".harness/harness.json is not valid JSON.")
    if cj and not (cj.get("cost_model") or {}).get("rates"):
        bad.append("harness.json has no cost_model.rates — runs cannot be costed, and cost "
                   "is the post-build signal (DEC-99). Run /harness-init --upgrade.")
    vo = (cj.get("cost_model") or {}).get("verified_on")
    if vo:
        # Prices change. A rate table nobody re-checks reports confident wrong numbers.
        import datetime
        try:
            age = (datetime.date.today() - datetime.date.fromisoformat(vo)).days
            if age > 90:
                warn.append(f"cost_model rates were last verified {age} days ago ({vo}) — "
                            f"re-check them against the pricing page.")
        except Exception:
            warn.append(f"cost_model.verified_on is not an ISO date: {vo!r}")

for sy in glob.glob(os.path.join(H, "features", "*", "runs", "*", "state.yaml")):
    txt = read(sy) or ""
    if re.search(r"^status:\s*complete", txt, re.M) and not re.search(r"^cost:", txt, re.M):
        rel = os.path.relpath(sy, H)
        bad.append(f"{rel}: run is complete but has no cost: block — "
                   f"run bin/cost-report.py --yaml and record it.")

# --- INV-10: docs must not contradict a decision that superseded them (DEC-103).
docs = os.path.join(root, "docs", "harness", "DECISIONS.md")
if os.path.isfile(docs):
    import subprocess
    cd = os.path.join(root, ".claude/skills/harness/bin/check-docs.sh")
    # NEVER skip silently. This used to be `if os.access(cd, X_OK):` with no else,
    # so a checker that lost its exec bit — or went missing in a partial deploy —
    # made INV-10 pass. An invariant that reports "all state invariants hold"
    # because it could not run is worse than one that fails: it is DEC-110's
    # fail-open-and-silent shape inside the thing built to catch it. Three separate
    # agents flagged it independently before it was fixed.
    if not os.path.isfile(cd):
        bad.append(f"INV-10 could not run: {os.path.relpath(cd, root)} is missing. "
                   f"Doc propagation is UNCHECKED — likely a partial deploy.")
    elif not os.access(cd, os.X_OK):
        bad.append(f"INV-10 could not run: {os.path.relpath(cd, root)} is not executable. "
                   f"Doc propagation is UNCHECKED. Fix with `chmod +x`.")
    else:
        r = subprocess.run([cd], capture_output=True, text=True, cwd=root)
        if r.returncode == 1:
            bad.append("docs contain statements a superseding decision invalidated "
                       "— run bin/check-docs.sh for the list.")
        elif r.returncode != 0:
            # Exit 1 is "found stale statements". Anything else is the checker
            # itself failing, which must not read as a clean bill of health.
            bad.append(f"INV-10 could not run: check-docs.sh exited {r.returncode}. "
                       f"Doc propagation is UNCHECKED. stderr: "
                       f"{(r.stderr or '').strip().splitlines()[-1] if r.stderr.strip() else '(none)'}")

for m in bad:  print(f"  VIOLATION  {m}")
for m in warn: print(f"  note       {m}")
if not bad and not warn:
    print("  all state invariants hold.")
sys.exit(1 if bad else 0)
PY
