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
# _selfdir is resolved BEFORE the cd. BASH_SOURCE may be relative to the ORIGINAL
# working directory, so computing it after `cd "$root"` resolves it against the wrong
# base and the heredoc dies with ModuleNotFoundError. That is a crash, and this script
# exits 1 on crash exactly as it does on a real violation — so /harness entry would
# report "violations found" for a missing module. Found while fixing F-02; the original
# ordering passed every check I ran only because I always ran from the repo root.
_selfdir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$root"
PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" python3 - "$root" <<'PY'
import sys, os, re, glob, json

import harness_yaml

# Review finding 1: `require_or_die` is the module's documented gate for exactly
# this script and had ZERO production callers, so a missing PyYAML surfaced as
# every file "does not parse" and exit 1 — /harness entry reporting "violations
# found" for an absent dependency. It gates the ORCHESTRATOR, not a write, so a
# hard block here costs no recovery path (D-06); the bootstrap escape is for the
# two hooks only.
harness_yaml.require_or_die()

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
    # T-07 / issue #11 — a REAL parser, not a regex over two hand-listed shapes.
    #
    # What the regexes could not do: the block form required `\s*\n` after the `id:`
    # and `squad:` captures, so a trailing `# comment` on either line — legal YAML,
    # and the house style on 45 lines of FEAT-03's feature.yaml — silently dropped the
    # ENTIRE run, failing INV-6, INV-7 and INV-8 open at exit 0. Reproduced before the
    # fix. It had never fired only because those two lines happened to carry no
    # comments, and one author who hit it wrote a warning into the data file
    # (feature.yaml:63-64) instead of fixing the parser. Same defect class as DEC-123
    # and DEC-129; DEC-171 reverses the no-dependency clause that forced it.
    try:
        doc = harness_yaml.load_file(fy) or {}
    except Exception as e:
        # A file that does not parse is a VIOLATION, never a silent skip — the whole
        # point of DEC-171 am.1 is that there is no quieter mode. Report and move on
        # so one broken feature cannot hide every other feature's invariants.
        bad.append(f"{feat}/feature.yaml does not parse, so INV-6..8 and INV-12 "
                   f"cannot be checked for it: {e}")
        continue
    if not isinstance(doc, dict):
        bad.append(f"{feat}/feature.yaml is not a YAML mapping.")
        continue

    def val(k):
        """A scalar field as a string, or None. safe_load returns TYPED values, so
        every consumer below would otherwise break on an int: `cycles_used: 6` is an
        int and the old code called `.isdigit()` on it."""
        v = doc.get(k)
        return None if v is None else str(v)

    # `runs:` entries, whatever YAML shape the author used — inline flow mapping,
    # block mapping, comments anywhere. The parser handles all of it; we only assert
    # the three fields the invariants need.
    runs = []
    for entry in (doc.get("runs") or []):
        if not isinstance(entry, dict):
            bad.append(f"{feat}: a runs: entry is not a mapping ({entry!r}).")
            continue
        runs.append((str(entry.get("id", "")).strip(),
                     str(entry.get("squad", "")).strip(),
                     str(entry.get("verdict", "")).strip()))

    # INV-6: reviewers must diff a pinned SHA, never a moving HEAD (DEC-50).
    # A placeholder is not a pin: val() returns str(v), so `review_sha: none` is a
    # truthy string and only an ABSENT key used to trip this (issue #16).
    _sha = (val("review_sha") or "").strip().lower()
    if any(sq == "validator" for _, sq, _ in runs) and (
            _sha == "" or _sha in harness_yaml.PLACEHOLDER_UNSET):
        bad.append(f"{feat}: a validator run exists but review_sha is not pinned "
                   f"— reviewers would diff HEAD (the GAP-7 failure).")

    # INV-7: the fix-loop bound must actually count the failures it bounds.
    fails = sum(1 for _, _, v in runs if v.upper() == "FAIL")
    cu = val("cycles_used")
    if cu is not None and cu.isdigit() and int(cu) < fails:
        bad.append(f"{feat}: cycles_used={cu} but {fails} FAIL run(s) recorded "
                   f"— the fix loop is no longer bounded.")

    # INV-8: a referenced run dir must exist, or resume has nothing to read.
    recorded = set()
    for rid, _, _ in runs:
        recorded.add(rid)
        d = os.path.join(os.path.dirname(fy), "runs", rid)
        if not os.path.isdir(d):
            warn.append(f"{feat}: run {rid} is referenced but its dir is absent "
                        f"(pruned, or never created).")
    # INV-12: the INVERSE — a run dir nothing records. Observed live (DEC-131): an
    # interrupt killed the orchestrator's view while its orphaned subtree ran on and
    # wrote a whole run. Work on disk that no orchestrator knows about is invisible
    # to resume unless something surfaces it.
    for d in glob.glob(os.path.join(os.path.dirname(fy), "runs", "*")):
        rid = os.path.basename(d)
        if os.path.isdir(d) and rid not in recorded:
            warn.append(f"{feat}: run dir {rid} exists on disk but feature.yaml does not "
                        f"record it — orphaned work (interrupted flow?). A resume must "
                        f"reconcile it, not rediscover it by luck.")

# --- INV-9: platform prerequisites that fail SILENTLY if absent (DEC-100).
sett = None
for p in (".claude/settings.json", ".claude/settings.local.json"):
    t = read(os.path.join(root, p))
    if t:
        try:
            # DEEP merge, one level into hooks/env. A shallow `|` let any `hooks` key
            # in settings.local.json wholesale shadow settings.json's, so INV-9 then
            # reported every OTHER hook as missing and blocked /harness entry on a
            # correctly configured project -- a false diagnosis sending the reader to
            # re-run merge-settings for hooks already present (review of PR #4).
            nxt = json.loads(t)
            if sett is None:
                sett = nxt
            else:
                for k, v in nxt.items():
                    if k in ("hooks", "env") and isinstance(v, dict) and isinstance(sett.get(k), dict):
                        for ek, ev in v.items():
                            # union the per-event lists: presence anywhere is what INV-9 asks
                            if isinstance(ev, list) and isinstance(sett[k].get(ek), list):
                                sett[k][ek] = sett[k][ek] + ev
                            else:
                                sett[k][ek] = ev
                    else:
                        sett[k] = v
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
    if not any("branch-create-gate" in str(h) for h in pre):
        bad.append("No PreToolUse branch-create-gate hook — branch creation is ungated "
                   "(self-gating on github.sync, so registration is safe everywhere; DEC-144).")
    if not any("dispatch-guard" in str(h) for h in pre):
        bad.append("No PreToolUse dispatch-guard hook — a lead can silently override a "
                   "member's pinned model per-dispatch (DEC-155/156); the org's tier "
                   "design is unenforced.")
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

import subprocess

# --- INV-17 (DEC-159): per-phase orchestrators hand off through notes/handoff-<phase>.md.
# A feature whose phase: sits past a seam with no handoff note for the crossing lost the
# predecessor's working memory — recoverable (disk-only is supported) but never silent.
# Only enforced when the feature declares phase: at all, so pre-DEC-159 features stay quiet.
PHASE_ORDER = ["plan", "build", "validate", "ship"]
HANDOFF_HEADINGS = ["## next", "## trust", "## dead ends", "## working set"]
for fy in glob.glob(os.path.join(H, "features", "*", "feature.yaml")):
    feat = os.path.basename(os.path.dirname(fy))
    # F-02: parsed, not regex-scanned. `^phase:\s*(\S+)` misses a quoted value and a
    # block scalar, both legal YAML — and a miss here is silent: the feature is skipped
    # entirely by `continue`, so the invariant never runs and never says why.
    try:
        _doc = harness_yaml.load_file(fy) or {}
    except Exception as e:
        bad.append(f"{feat}/feature.yaml does not parse, so its phase invariants "
                   f"cannot be checked: {e}")
        continue
    _phase = str(_doc.get("phase", "")).strip() if isinstance(_doc, dict) else ""
    if _phase not in PHASE_ORDER:
        continue
    idx = PHASE_ORDER.index(_phase)
    for prev in PHASE_ORDER[:idx]:
        hp = os.path.join(os.path.dirname(fy), "notes", f"handoff-{prev}.md")
        if not os.path.isfile(hp):
            # M-01: this said `pm_.group(1)` — a leftover from the regex the F-02
            # conversion deleted when it renamed the parsed value to `_phase`. Used
            # once, assigned nowhere, so it raised NameError on the ONE condition
            # INV-17 exists to detect, aborting INV-11/13/15/16/18/21 and INV-10 with
            # no "could not run" message. A crash exits 1, which is what a real
            # violation exits, so /harness entry reported "violations found" for a
            # typo. Introduced by the fix for F-02 and caught by the re-review, not by
            # any gate.
            bad.append(f"{feat}: phase is '{_phase}' but notes/handoff-{prev}.md is "
                       f"missing — the {prev} seam was crossed without a handoff; the "
                       f"successor is on the disk-only path (DEC-159).")
            continue
        hl = [l.strip().lower() for l in (read(hp) or "").splitlines()]
        miss = [h for h in HANDOFF_HEADINGS if h not in hl]
        if miss or len(hl) > 60:
            why = []
            if miss: why.append(f"missing section(s) {miss}")
            if len(hl) > 60: why.append(f"{len(hl)} lines vs cap 60")
            bad.append(f"{feat}: notes/handoff-{prev}.md fails the shape ({'; '.join(why)}) "
                       f"— a freeform handoff drifts like an unvalidated digest did "
                       f"(DEC-159/160).")

# --- INV-18 (DEC-160): a feature with run dirs but no feature.yaml is invisible to
# every feature-keyed invariant (INV-8/12/17) — a whole phase can run unchecked.
# Observed live: FEAT-03's plan phase ran to completion before feature.yaml existed.
for rd in glob.glob(os.path.join(H, "features", "*", "runs")):
    fdir = os.path.dirname(rd)
    if os.listdir(rd) and not os.path.isfile(os.path.join(fdir, "feature.yaml")):
        bad.append(f"{os.path.basename(fdir)}: has runs/ but no feature.yaml — the feature is "
                   f"invisible to run reconciliation and phase checks; instantiate it from the "
                   f"template (the playbook's first-cycle duty).")

# --- INV-15 (DEC-156): a complete lead-hosted run's digest.md is the durable copy a
# successor reads — it must exist and satisfy the lead digest contract. The SubagentStop
# hook checks it at source but fails open when it cannot resolve the path (worktrees,
# cwd drift); this sweep runs from repo root and cannot be fooled.
# --- INV-16 (DEC-154, mechanized): state.yaml is a checkpoint — identifiers, enums,
# counters, paths, sequence markers. Top-level keys come from this whitelist, and no key
# repeats (the FEAT-02 audit found `cost:` written twice in 12 of 15 files — the second
# key silently shadows the first in any YAML parser).
LEADS = {"harness-product-lead", "harness-eng-lead", "harness-validator-lead"}
CHECKPOINT_KEYS = {
    # seed (harness-team §2)
    "schema_version", "run_id", "feature", "squad", "host", "status", "steps",
    # loop bookkeeping
    "cycles_used", "cost",
    # pins and context markers
    "flow", "task", "team", "branch", "worktree",
    "review_sha", "pinned_sha", "base_sha", "head_sha", "tip_sha", "commits",
    # roll-up enums and the report pointer — matchable values, so checkpoint-legal
    "verdict", "severity_max", "digest",
}
vd = os.path.join(root, ".claude/skills/harness/bin/validate-digest.py")
for sy in glob.glob(os.path.join(H, "features", "*", "runs", "*", "state.yaml")):
    rel = os.path.relpath(sy, H)
    rundir = os.path.dirname(sy)
    # F-02, and this one had a LIVE fail-open the panel reproduced: `status: "complete"`
    # — quoted, legal YAML — does not match `^status:\s*complete`, so `complete` was
    # False and INV-11 (an unmetered completed run) silently never fired.
    try:
        sdoc = harness_yaml.load_file(sy) or {}
    except Exception as e:
        bad.append(f"{rel}: state.yaml does not parse, so INV-11/15/16 cannot be "
                   f"checked for this run: {e}")
        continue
    if not isinstance(sdoc, dict):
        bad.append(f"{rel}: state.yaml is not a YAML mapping.")
        continue
    complete = str(sdoc.get("status", "")).strip() == "complete"

    # INV-11: cost is the post-build signal (DEC-99) — an unmetered completed run is a
    # hole in the only evidence SC-1 is judged on, and looks exactly like a free one.
    if complete and "cost" not in sdoc:
        bad.append(f"{rel}: run is complete but has no cost: block — "
                   f"run bin/cost-report.py --yaml and record it.")

    # INV-16: shape.
    #
    # Q3, found by the re-review: the duplicate-key TEXT SCAN that used to live here was
    # DEAD CODE, and its comment told future readers to preserve it for a property it no
    # longer had. `load_file` above uses the strict loader, which RAISES DuplicateKeyError
    # before control ever reaches this point — and that path `continue`s, so INV-16's own
    # DEC-156 message never fired. Keeping a scan that cannot run, guarded by a comment
    # forbidding its removal, is worse than either fixing or deleting it: the next reader
    # trusts the comment.
    #
    # Removed, because the loader's raise is strictly better — it catches a duplicate at
    # ANY nesting depth, where the column-0 scan saw only top-level ones.
    #
    # CORRECTED (review finding 5): this comment used to claim the DEC-156 wording was
    # "preserved at the raise site", and it was NOT — DuplicateKeyError's message was
    # a bare `duplicate key 'x'`, so the guidance an author actually needs ("replace the
    # placeholder; never append a second copy") vanished from this file entirely. A
    # comment asserting a preserved message that was in fact dropped is worse than no
    # comment, in a repo whose convention is that comments are load-bearing.
    #
    # It is true NOW because the guidance was moved INTO the exception's message
    # (harness_yaml.py's DuplicateKeyError.__init__), so every caller renders it whether
    # or not it has a dedicated handler.
    # The UNKNOWN half reads the PARSED keys (F-02): a quoted key is a real key the
    # text scan misses, a `#`-commented line is not a key at all, and YAML 1.1 resolves
    # `on:`/`no:` to booleans — so str() both sides, as T-17 does in check-domain.sh.
    unknown = sorted({str(k) for k in sdoc if str(k) not in CHECKPOINT_KEYS})
    if unknown:
        bad.append(f"{rel}: non-checkpoint top-level key(s) {unknown} — state.yaml carries "
                   f"only identifiers, enums, counters, paths and sequence markers "
                   f"(DEC-154). Findings and assessment prose belong in that run's "
                   f"digest.md; a one-line note: per step entry is the ceiling.")

    # INV-15: the durable digest.
    _host = str(sdoc.get("host", "")).strip()
    if complete and _host in LEADS:
        dg = os.path.join(rundir, "digest.md")
        if not os.path.isfile(dg):
            bad.append(f"{os.path.relpath(rundir, H)}: run is complete but digest.md is "
                       f"missing — the lead's report artifact never landed (DEC-156).")
        elif not os.path.isfile(vd):
            bad.append(f"INV-15 could not run: {os.path.relpath(vd, root)} is missing. "
                       f"Digest files are UNCHECKED — likely a partial deploy.")
        else:
            r = subprocess.run([sys.executable, vd, "lead", dg],
                               capture_output=True, text=True)
            if r.returncode != 0:
                bad.append(f"{os.path.relpath(dg, H)}: does not satisfy the lead digest "
                           f"contract — a successor reads this file, not the transcript "
                           f"(DEC-156). Run bin/validate-digest.py lead on it for reasons.")

# --- INV-14: real code with no codebase map (DEC-140). The map moved into init
# after the first real onboarding built a feature UNMAPPED — "run the map first"
# as prose is the forgettable class. Greenfield is fine: the heuristic only fires
# when meaningful source exists. A warn, not a violation — flows still run.
SRC_EXT = (".py",".ts",".tsx",".js",".jsx",".go",".rb",".rs",".java",".kt",".swift",".php",".c",".cc",".cpp")
if not os.path.isfile(os.path.join(H, "codebase", "INDEX.md")):
    n_src = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")
                       and d not in ("node_modules","vendor","dist","build","docs")]
        n_src += sum(1 for f in filenames if f.endswith(SRC_EXT))
        if n_src > 5:
            break
    if n_src > 5:
        warn.append("codebase has real source but no map (.harness/codebase/INDEX.md) — "
                    "run mission map (/harness \"map the codebase\"). Every unmapped spawn "
                    "re-derives structure the map would have carried (DEC-140).")

# --- INV-19 (DEC-162): a mapped codebase without a glossary means the ubiquitous
# language lives nowhere — "create lazily" fired zero times across three shipped
# features while enums and status vocabularies were being pinned. Warn-level, like
# INV-14: flows still run, but pm's next map/plan pass owes the file.
if os.path.isfile(os.path.join(H, "codebase", "INDEX.md")) and \
   not os.path.isfile(os.path.join(H, "codebase", "glossary.md")):
    warn.append("codebase is mapped but has no glossary.md — the domain's ubiquitous language "
                "is unrecorded (DEC-162). pm authors it (mission map assigns it; or seed it "
                "from shipped features' pinned vocabulary).")

# --- INV-20 (DEC-163): a test kind with cmd: null is an HONEST record of no runner — but
# when the product HAS that surface, it is also a silent hole: qa resolves the kind to a soft
# skip, so an SC resting on it can never fail loudly, and pm quietly stops writing SCs against
# it. The discriminating check is the codebase map, which already records which surfaces exist:
# a null runner matters exactly when its surface view is more than a self-scoped-out stub.
# Warn-level (INV-14's level) — flows still run; the point is that the gap reaches a human.
KIND_SURFACE = {"ui": "ui-surface.md", "component": "ui-surface.md",
                "eval": "llm-patterns.md", "integration": "data-flows.md"}
if cj:
    kinds = cj.get("test_kinds") or {}
    for kind, view in KIND_SURFACE.items():
        spec = kinds.get(kind)
        if not isinstance(spec, dict) or spec.get("cmd"):
            continue
        vp = os.path.join(H, "codebase", view)
        vt = read(vp)
        # A self-scoped-out view is a line or two ("no UI surface here"); a real one is long.
        if vt and len(vt.splitlines()) > 20:
            warn.append(f"test kind '{kind}' has cmd: null but {view} describes a real surface "
                        f"({len(vt.splitlines())} lines) — SCs cannot rest on '{kind}' and qa "
                        f"records it as a soft skip, so the gap is invisible at ship time "
                        f"(DEC-163). Either stand up a runner (a dev-ops task) or accept it "
                        f"explicitly in the BRIEF's verification-gaps line.")

# --- INV-21 (D-05): a mirrored feature whose task issues are recorded but whose
# container (parent) never was — `ship`/`abandon` cannot close it and `open` will not
# re-derive it (the mirror is write-only, DEC-138). Warn, not violation (D-05): the
# GitHub Issues sync is never a gate, and a re-run of `open` fixes it (INV-20's
# precedent). Vacuous when github.sync is off — the check costs nothing then.
if cj and (cj.get("github") or {}).get("sync"):
    for fy in glob.glob(os.path.join(H, "features", "*", "feature.yaml")):
        feat = os.path.basename(os.path.dirname(fy))
        # F-02: the last of the seven. This carried the SAME four defects gh-sync.py's
        # reader did, and T-06 fixed them there while leaving the twin here — which is
        # the divergence D-03 exists to prevent, in a second pair of files:
        #   - `^\s{4}T-\d+:\s*\d+` hardcoded a four-space indent
        #   - `parent:\s*\d+` accepted only bare digits, so `parent: "40"` read as absent
        #   - `^github:\s*$(.*?)(?=^\S|\Z)` sliced by indentation, so a comment at
        #     column 0 inside the block truncated the rest
        # A miss here is silent by construction: `continue` skips the feature entirely.
        try:
            gdoc = harness_yaml.load_file(fy) or {}
        except Exception as e:
            bad.append(f"{feat}/feature.yaml does not parse, so INV-21 cannot be "
                       f"checked for it: {e}")
            continue
        gblk = gdoc.get("github") if isinstance(gdoc, dict) else None
        if not isinstance(gblk, dict):
            continue
        _issues = gblk.get("issues")
        has_issue = bool(isinstance(_issues, dict) and any(
            re.fullmatch(r"T-\d+", str(k).strip()) and str(v).strip().isdigit()
            for k, v in _issues.items()))
        has_parent = str(gblk.get("parent", "")).strip().isdigit()
        if has_issue and not has_parent:
            warn.append(f"INV-21: {feat} has recorded task issues but no numeric "
                        f"parent — ship/abandon cannot close the container and open "
                        f"will not re-derive it (D-05). Re-run `open` to record it.")

# --- INV-13: the GitHub mirror is either configured or explicitly off — never limbo
# (DEC-138). `sync: true` with no pinned repo would make every gh-sync call skip
# silently, which reads exactly like a working mirror to anyone not tailing logs.
# A missing `github` block means the project predates the feature: surface it once.
if cj:
    gh_ = cj.get("github")
    if gh_ is None:
        warn.append("harness.json has no `github` block — predates DEC-138. Run "
                    "/harness-init --upgrade to decide the Issues mirror once (sync on/off).")
    elif gh_.get("sync") and not gh_.get("repo"):
        bad.append("github.sync is ON but github.repo is not pinned — every sync will "
                   "silently SKIP. Pin the repo (from `gh repo view`) or turn sync off.")

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
