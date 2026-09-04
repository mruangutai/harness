#!/usr/bin/env bash
# Deterministic state-invariant checker. Run at every /harness entry.
#
# WHY THIS EXISTS: the orchestrator is an LLM performing ~15 bookkeeping duties
# per cycle with nothing validating any of them. A skipped duty is silent, and a
# bad STATE.md write poisons every subsequent spawn. The precedent:
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

# THE ROOT COMES FROM harness_boundary, reached through this script's own directory, never
# from the environment and never from the caller's cwd (FEAT-42 T-12). What stood here was a
# two-name chain with a pwd fallback, and this is the canonical pre-commit gate for the whole
# repository: a state checker that silently examines the wrong checkout reports a clean tree
# while the real one is broken, and nothing says so.
#
# REFUSING IS THE POINT — exit 2, never a fallback. The file's contract is 0 clean, 1 findings,
# so an unresolvable root needs a code that cannot be read as either. Do not name the retired
# variables here even in prose: the invariant that keeps them gone counts the name in every
# tracked source file.
# THE RESOLVER'S OWN STDERR IS KEPT AND REPLAYED, never swallowed. Two different things
# arrive on it and both matter: the discard notice for an override that carries no MARKER,
# and the ImportError when harness_boundary.py is not beside this script at all. Sending
# either to /dev/null turns a refusal into "no harness root could be resolved", which names
# the symptom and not the cause.
_rooterr="$(mktemp)"
root="$(python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary; print(harness_boundary.resolve_root(sys.argv[1]))' "$_selfdir" 2>"$_rooterr")"
if [ -z "$root" ] || [ ! -d "$root" ]; then
  echo "check-state.sh: no harness root could be resolved from $_selfdir — refusing to run." >&2
  cat "$_rooterr" >&2
  rm -f "$_rooterr"
  exit 2
fi
cat "$_rooterr" >&2
rm -f "$_rooterr"
cd "$root" || exit 2
PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" python3 -c 'import sys; sys.path.pop(0); exec(compile(sys.stdin.read(), "<stdin>", "exec"))' "$root" "$_selfdir" <<'PY'
import sys, os, re, glob, json, subprocess

sys.path.insert(0, sys.argv[2])
import harness_yaml
try:
    import handoff_done_when
except Exception as _handoff_done_when_error:
    handoff_done_when = None

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

# THE STATION VOCABULARY IS DERIVED, NEVER SPELLED (FEAT-41 T-01/T-07). Both names below come
# from factory_config so this script cannot drift from harness.json's declaration — the drift
# that made a six-key mapping and a validator disagree, which is why FEAT-41 exists.
import factory_config

TERMINAL_MARKER = factory_config.TERMINAL_MARKER

# THE FEATURE'S STATION, READ FROM THE ONE FILE THAT RECORDS IT (FEAT-41 T-07). Every site
# below that used to read feature.json's `status` now calls this, so the vocabulary and the
# file live in exactly one place in this script instead of six.
#
# `station_of` takes the feature DIRECTORY, not a file, because every caller already holds one
# and the two callers that iterate feature.json globs still need that document for its OTHER
# keys (INV-28's `pr`, INV-6's shape). Splitting the station read from the document read is
# what lets those sites keep one open() each rather than gaining a second.
#
# RETURNS "" FOR EVERY UNKNOWABLE CASE — no plan, unparseable plan, no station, a station that
# is not a string. "" is the same value the old code produced from an absent feature.json
# status, so each caller's existing posture carries over unchanged rather than being redesigned
# alongside the migration.
def station_of(feat_dir):
    try:
        doc = harness_yaml.load_file(os.path.join(feat_dir, "plan.yaml")) or {}
    except Exception:
        return ""
    if not isinstance(doc, dict):
        return ""
    # `status: done  # with a trailing comment` is a shape the live corpus carries, so take the
    # first whitespace-delimited token — the same normalisation the feature.json reads used.
    token = str(doc.get("status", "")).split()
    return token[0] if token else ""


if not os.path.isdir(H):
    print("harness: no .harness/ — project not onboarded. Run /harness-init.")
    sys.exit(1)

# D-08 (FEAT-21 T-05), the OTHER half of the signed trade: dict KEYS stay bare basenames
# (qualify one of the two name-derivation shapes and not the other and the station mirror
# silently skips every feature), but a finding that names a PATH carries the DISCOVERED
# segment-qualified path, so a reader can open exactly what the label names.
_feat_dirs = {os.path.basename(_d): os.path.relpath(_d, root)
              for _d in glob.glob(os.path.join(H, "*", "features", "*"))
              if os.path.isdir(_d)}
def fpath(feat, tail=""):
    _b = _feat_dirs.get(feat) or os.path.join(".harness", "?", "features", feat)
    return _b + (os.sep + tail if tail else "")

# BRIEF/PLAN are PER-FEATURE since DEC-129 — .harness/<repo>/features/<FEAT>/{BRIEF,PLAN}.md.
# Root-level singletons collided the moment a second feature existed.
briefs = {os.path.basename(os.path.dirname(p)): read(p)
          for p in glob.glob(os.path.join(H, "*", "features", "*", "BRIEF.md"))}
plans  = {os.path.basename(os.path.dirname(p)): read(p)
          for p in glob.glob(os.path.join(H, "*", "features", "*", "PLAN.md"))}
# plan.yaml (DEC-182) is loaded, never read as text. Kept in a SEPARATE dict rather than
# merged into `plans`: every check below either reads markdown or reads a mapping, and one
# dict holding both shapes is how a regex ends up running over a dict repr. A feature with
# both files is refused by check-plan-routes; here the yaml simply wins, because a feature
# mid-migration should be judged by the artifact its author is maintaining.
plan_docs = {}
for _p in glob.glob(os.path.join(H, "*", "features", "*", "plan.yaml")):
    _feat = os.path.basename(os.path.dirname(_p))
    try:
        plan_docs[_feat] = harness_yaml.load_plan(_p)
        plans.pop(_feat, None)
    except harness_yaml.YamlParseError as _e:
        # A plan that does not load is a VIOLATION, never a silent skip — the whole point
        # of DEC-182 is that a malformed plan stops being something a regex half-reads.
        bad.append(f"{fpath(_feat, 'plan.yaml')} does not load, so INV-3/4/5 cannot be checked "
                   f"for it: {_e}")

# --- INV-35 (issue #251): a plan.yaml plain scalar carrying a space then a `#` immediately
# followed by a digit truncates SILENTLY under YAML's plain-scalar comment rule -- `#217`
# embedded in `title: close out the fix for #217` stops the scalar exactly at the `#` and the
# loss is invisible: the file still parses, `harness_yaml.load_plan` returns cleanly, and
# nothing downstream can tell a truncated value from one that never mentioned the number.
#
# THIS WALKS THE RAW SOURCE, NEVER THE PARSED DOC. The parsed doc is the wrong side of the
# loss to look from -- by the time safe_load has run, the deleted text is already gone, so a
# check keyed on plan_docs above cannot see what it exists to catch.
#
# EVERY CHECK IS ANCHORED TO THE VALUE, NEVER THE RAW LINE. `_line_value` strips the leading
# indentation, an optional sequence dash and an optional `key: ` prefix, and every downstream
# decision -- block-scalar-open, quoted-vs-plain -- is made against what remains. A validator
# review of an earlier cut of this invariant found TWO live false negatives from skipping this
# step and matching against the raw line instead, both reproduced against this repo's own
# tree before the fix:
#   (1) `_BLOCK_SCALAR_OPEN.search(line)` matched a coincidental `key:>value` substring
#       anywhere in the line -- e.g. `title: fix #217 for the ratio:>5` -- misreading an
#       ordinary line as a block-scalar opener and skipping the real truncation earlier on
#       it. A `.fullmatch` against the isolated value cannot be fooled by a substring.
#   (2) The prior quote tracker toggled `in_quote` on EVERY `'`/`"` character anywhere on the
#       line, so a plain scalar with an odd count of apostrophes before the truncation point
#       (`the operator's design note for #806`, live in
#       FEAT-34-worktree-act3-enforced/plan.yaml D-03 at review time) flipped the scanner into
#       treating the real ` #806` as quoted and reported nothing.
#
# THE FIX RESTS ON ONE YAML FACT: only the FIRST character of a value can open a quoted
# scalar. If it is not `'`/`"`, the value is plain for its ENTIRE remaining length and no
# quote character appearing later has any special meaning at all -- it is literal text, full
# stop. So a plain value needs no quote-tracking whatsoever; it needs only the first
# whitespace-preceded (or value-initial) `#`, which is where YAML's comment actually starts.
# A quoted value tracks its own delimiter to the close (a doubled quote is YAML's escape for
# a literal one), and nothing after that close can be lost data -- a proper quoted scalar's
# close ends the value; what follows is comment or malformed, never truncated content.
#
# BLOCK SCALARS ARE EXEMPT BY THE YAML SPEC ITSELF: a `|`/`>` block's content is literal, and a
# `#` inside it is data, never a comment. `_block_indent` tracks the opening key's indentation
# and skips every more-indented (or blank) line that follows, so a `verify: |` body can freely
# quote an issue number without tripping this.
#
# STOPS AT THE FIRST UNQUOTED `#` in a plain value, never scans past it. That hash is where
# YAML's comment actually starts, whether or not a digit follows it -- everything after it is
# already comment text, so a second `#<digit>` deeper in an ordinary trailing comment
# (`# see issue #217`) must not be mistaken for a second truncation point.
#
# A MULTI-LINE QUOTED SCALAR IS THE ONE KNOWN GAP: this tracks a quote's close only within its
# own physical line, so a `'`/`"` scalar that legitimately wraps onto a following line could
# misread that continuation. Not a false negative -- an unterminated quote returns None, the
# same silence as a closed one -- and this repo's own corpus uses block scalars exclusively
# for multi-line prose, never a multi-line flow-quoted one, so it is unreached here. Documented
# rather than chased, per this invariant's own asymmetric design (a false deny is recoverable,
# a false allow is not, so what remains unchecked here is a false ALLOW risk and is named as
# such rather than left implicit).
#
# THE KEY ITSELF CAN BE QUOTED OR HYPHENATED, and `_KEY_PREFIX` must recognise both or the
# strip fails silently in the dangerous direction. A validator's second pass (cycle 2, PR
# #1145) proved this live: an earlier cut matched only a bare identifier key, so a quoted key
# (`"my-key": value #217`) fell through the optional key group entirely, and
# `_unquoted_hash_digit` then read the key's OWN opening quote as `value[0]`, tracked to the
# key's own closing quote, and returned None -- silently swallowing the real truncation that
# followed. `_KEY_PREFIX` now recognises three key shapes: a bare identifier (now including
# `-`, since a hyphenated unquoted key hit the same fall-through in the block-scalar-open
# direction, a false POSITIVE rather than a silence but the same root cause), a
# double-quoted key, or a single-quoted key.
_KEY_PREFIX = re.compile(
    r'^\s*(?:-\s+)?(?:(?:[A-Za-z_][A-Za-z0-9_-]*|"[^"]*"|\'[^\']*\'):\s+)?'
)
_BLOCK_SCALAR_VALUE = re.compile(r"^[|>][+\-]?\d*\s*(#.*)?$")


def _line_value(line):
    return line[_KEY_PREFIX.match(line).end():]


def _unquoted_hash_digit(value):
    if value[:1] in ("'", '"'):
        q = value[0]
        i = 1
        while i < len(value):
            if value[i] == q:
                if i + 1 < len(value) and value[i + 1] == q:
                    i += 2
                    continue
                return None
            i += 1
        return None
    for i, ch in enumerate(value):
        if ch == "#" and (i == 0 or value[i - 1].isspace()):
            if i + 1 < len(value) and value[i + 1].isdigit():
                return i
            return None
    return None


for _p in sorted(glob.glob(os.path.join(H, "*", "features", "*", "plan.yaml"))):
    _feat = os.path.basename(os.path.dirname(_p))
    _txt = read(_p)
    if _txt is None:
        continue
    _block_indent = None
    for _lineno, _line in enumerate(_txt.splitlines(), start=1):
        _stripped = _line.strip()
        _indent = len(_line) - len(_line.lstrip(" "))
        if _block_indent is not None:
            if _stripped == "" or _indent > _block_indent:
                continue
            _block_indent = None
        if not _stripped or _stripped.startswith("#"):
            continue
        _value = _line_value(_line)
        if _BLOCK_SCALAR_VALUE.fullmatch(_value.rstrip()):
            _block_indent = _indent
            continue
        _hit = _unquoted_hash_digit(_value)
        if _hit is not None:
            _num = re.match(r"\d+", _value[_hit + 1:]).group(0)
            bad.append(
                f"INV-35: {fpath(_feat, 'plan.yaml')}:{_lineno} carries an unquoted scalar with "
                f"` #{_num}` -- YAML's plain-scalar comment rule truncates everything from that "
                f"`#` onward, silently, even though the file still parses. Quote the value so "
                f"the issue number stays in the data: {_line.strip()!r}."
            )
# STATE.md is per-feature since DEC-120; read them all.
states = {os.path.basename(os.path.dirname(p)): read(p)
          for p in glob.glob(os.path.join(H, "*", "features", "*", "STATE.md"))}


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
# AN ABANDONED FEATURE'S BRIEF IS NEVER APPROVED, and that is the point rather than a
# defect: it was planned and retired without being signed. Halting /harness entry over an
# unapproved brief on a feature nobody will build trains the operator to ignore the gate,
# which is the failure a gate exists to prevent. Read from plan.yaml's station (FEAT-41 T-07),
# never inferred — and the try/except that guarded the old json.load is gone with it, because
# `station_of` already returns "" for every unreadable and unparseable shape.
_abandoned = set()
for _fd in sorted(glob.glob(os.path.join(H, "*", "features", "*"))):
    if not os.path.isdir(_fd):
        continue
    if station_of(_fd) == TERMINAL_MARKER:
        _abandoned.add(os.path.basename(_fd))
for feat, brief in briefs.items():
    if feat in _abandoned:
        continue
    if not has_approval_block(brief):
        bad.append(f"{fpath(feat, 'BRIEF.md')} has no '## Approval' section — cannot tell if the goal is signed.")
    elif not approved(brief):
        bad.append(f"{fpath(feat, 'BRIEF.md')} is NOT approved — halt that flow and surface to the user.")
for feat in states:
    if feat not in briefs:
        bad.append(f"{feat} has STATE.md but no BRIEF.md — a flow is running with no goal of record.")

# --- INV-3/4/5 on plan.yaml (DEC-182). Same three invariants, read from a mapping
# instead of scraped out of prose. load_plan has already guaranteed every task carries the
# fields REQUIRED_TASK_FIELDS names, so INV-4's "no change_type" case cannot reach here —
# it is a load error now, caught above. What remains is what the loader does not police:
# the approval block, and STATE.md pointing at a task the plan does not contain.
# A STATION-ONLY RECORD IS OUT OF SCOPE FOR BOTH (FEAT-41 T-19). Neither question applies to it:
# it declares a station and no tasks, so it HAS no goal to sign and no task ids for STATE.md to
# name. Backfilling twelve of them made these two checks visible for directories that had been
# skipped for as long as they carried no plan at all -- 31 lines, none of them a real finding.
#
# THIS IS SCOPING, NOT A FAIL-OPEN, and the alternative shows why: the only way to satisfy the
# approval check here would be to write an `approval:` block into each of the twelve, which would
# FABRICATE twelve signatures nobody gave. A check that can only be passed by inventing a record
# is measuring the wrong thing.
#
# KEYED ON THE POSITIVE DECLARATION, NEVER ON THE ABSENCE OF TASKS (FEAT-41 MF-3). The first
# version tested `if not doc["tasks"]`, and cycle 3 proved end to end what that cost: a Bash write
# emptied a SIGNED plan's `tasks:` while keeping its `approval:` and `status:`, the document
# inherited this exemption, and a real dangling-STATE.md-task violation went SILENT. An emptied
# plan carries no `station_only:` marker, so it now fails to LOAD -- which is already a violation,
# so the forged state is louder than the check it was escaping.
#
# AN ABSENCE CANNOT BE A CREDENTIAL. A checker must be TOLD a fact, never infer one from a missing
# field; that is the same shape as the B-7 fail-open the loader's own comment records.
#
# THE EXEMPTION CANNOT WIDEN SILENTLY, and the guarantee is that the MARKER IS NOT MINTABLE: a
# plan carrying tasks cannot wear it, enforced at `harness_yaml.load_plan` because that is the one
# chokepoint every reader passes through -- a writer-side guard would leave the unmediated Bash
# route open, which the BRIEF itself discloses.
#
# THIS COMMENT PREVIOUSLY CITED case (inv34.d) AS ASSERTING THAT, AND IT DID NOT (FEAT-41 HIGH-1).
# Two of cycle 4's reviewers checked at source: (inv34.d)'s fixture carries no marker, so the test
# named here never tested the guarantee claimed here. A false citation is worse than a missing test
# -- it stops the next reader looking. Cases (inv34.e) and (inv34.f) cover the two forgeries.
for feat, doc in plan_docs.items():
    if doc.get("station_only") is True:
        continue
    _appr = doc.get("approval")
    if not isinstance(_appr, dict):
        bad.append(f"{fpath(feat, 'plan.yaml')} has no `approval:` block — cannot tell if the goal "
                   f"is signed.")
    elif str(_appr.get("status", "")).strip().lower() != "approved":
        warn.append(f"{fpath(feat, 'plan.yaml')} approval is pending — awaiting the user.")

    _plan_ids = {str(t["id"]) for t in doc["tasks"]}
    _state = states.get(feat)
    if _state:
        for _tid in set(re.findall(r"\bT-[0-9A-Za-z]+\b", _state)):
            if _tid not in _plan_ids:
                bad.append(f"{fpath(feat, 'STATE.md')} references {_tid}, which is absent from its "
                           f"plan.yaml.")

# INV-32 ERA RESOLUTION BEGIN (BUG-1071)
# WHY AN ERA GUARD EXISTS AT ALL. FEAT-45 T-07 shipped INV-32 with no era boundary, so it
# graded every plan ever signed: all 32 approved plans in this tree failed it, and NONE
# could pass, because a plan signed before the adversarial panel existed cannot carry a
# record of it. FEAT-45's own plan was among the 32. An invariant that fires on 100% of a
# corpus and admits nothing does not enforce a rule -- it only trains its reader to ignore
# the gate, which is the failure mode this file exists to prevent (see the INV-10 note at
# the foot of this script on the cost of a dead invariant). The rule was right; its
# retroactive reach was the defect.
#
# THE BOUNDARY IS PER-PROJECT CONFIG, NOT A LITERAL (panel finding F2). This file is
# COPIED INTO EVERY ONBOARDED PROJECT by /harness-init, so a hardcoded date would export
# one repository's history as another's gate: a project whose plans predate 2026-08-31
# would have every one of them silently exempted, for a reason belonging to somebody
# else's git log. `panel_era_start` is stamped per project and merged into an existing
# config additively by upgrade-config.py, whose whole contract is "template fills gaps,
# project values win".
#
# RESOLVED ONCE, ABOVE THE LOOP. The first cut assigned the boundary inside the per-plan
# loop, which re-derived it 32 times and would have reported a single config defect once
# per plan. A config defect is one finding.
_era_cfg = read(os.path.join(H, "harness.json"))
_MISSING = object()
if not _era_cfg:
    # NO CONFIG AT ALL IS NOT THIS CHECK'S FINDING. INV-1 above already reports "not
    # onboarded" by name, and a second violation for the same cause is noise. With no
    # project to speak for, there is no pre-panel era to honour: grade everything, which
    # is the fail-CLOSED direction.
    _era_start = None
else:
    try:
        _era_raw = json.loads(_era_cfg).get("panel_era_start", _MISSING)
    except Exception:
        # The JSON-validity violation is raised on its own merit further down (`cj`), so
        # this only decides what INV-32 does meanwhile. Unparseable config cannot exempt.
        _era_raw = None
    if _era_raw is _MISSING:
        # A CONFIG THAT PREDATES THIS KEY IS A VIOLATION, NOT A SILENT DEFAULT. Either
        # answer picked here would be wrong for somebody: defaulting to "grade
        # everything" reddens every pre-panel plan in an un-upgraded project, and
        # defaulting to "exempt everything" disables INV-32 there without saying so. So
        # it says so, once, and names the command that fixes it.
        bad.append("INV-32: .harness/harness.json has no `panel_era_start`, so no panel "
                   "era can be resolved. Run /harness-init --upgrade (upgrade-config.py) "
                   "to merge the key in, then set it to the date the adversarial panel "
                   "became available here, or null if this project never predated it.")
        _era_start = None
    elif _era_raw is None:
        # null means THIS PROJECT HAS NO PRE-PANEL ERA -- the template default, and the
        # truth for a project onboarded after FEAT-45. Every approved plan is graded.
        _era_start = None
    elif isinstance(_era_raw, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", _era_raw.strip()):
        _era_start = _era_raw.strip()
    else:
        bad.append(f"INV-32: .harness/harness.json `panel_era_start` is {_era_raw!r}, "
                   f"which is neither null nor a YYYY-MM-DD date. Nothing is exempted "
                   f"while it is unreadable.")
        _era_start = None
# INV-32 ERA RESOLUTION END (BUG-1071)

# INV-32 BEGIN (FEAT-45 T-07)
# A signed plan must carry the adversarial panel record the operator reviewed.
for feat, doc in plan_docs.items():
    approval = doc.get("approval")
    if not isinstance(approval, dict) or str(approval.get("status", "")).strip().lower() != "approved":
        continue
# INV-32 ERA BEGIN (BUG-1071)
    # The boundary itself is resolved ONCE from `panel_era_start`, above this loop; see
    # the ERA RESOLUTION block for why it is config rather than a literal. `_era_start` is
    # either a YYYY-MM-DD string or None, and None means THIS PROJECT HAS NO PRE-PANEL
    # ERA, so nothing below exempts anything.
    #
    # THE PER-PLAN KEY IS approval.date -- the only durable signature timestamp in the
    # document. Lexicographic comparison on YYYY-MM-DD is chronological, which is why the
    # format is validated rather than parsed.
    signed = str(approval.get("date", "")).strip()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", signed):
        # AN UNPLACEABLE ERA IS A VIOLATION (panel finding F1, closed at the operator's
        # ruling). This branch WARNED in the first cut of this guard, and that was a
        # fail-open on a fail-closed invariant: an approved plan with no `approval.date`
        # was never graded, the exemption never expired, and nothing else in this file or
        # in harness_yaml requires the key -- INV-3/4/5 check `approval.status` only. So
        # omitting one line bought permanent silence from INV-32.
        #
        # It is safe to fail here because the tree has no undated approval left:
        # FEAT-40-harness-writes-done was the only one, and BUG-1071 backfilled it from
        # the commit that signed it (2938a5c, 2026-08-25) rather than from memory. Fixing
        # the data BEFORE closing the hole is what keeps this from re-reddening the gate.
        #
        # IT FIRES EVEN WHEN _era_start IS None. An undated signature is a record defect
        # in its own right, not merely an obstacle to placing an era, so a project with no
        # pre-panel era still owes the date.
        # The recovery command NAMES THE FILE (cycle-1 ui finding). It printed a literal
        # `<this plan.yaml>` placeholder, which is the one thing an operator cannot paste:
        # a diagnostic whose remedy has to be hand-edited before it runs is a diagnostic
        # that will be retyped wrong. The glob matches the tree's real layout,
        # `.harness/*/features/*/`, so it resolves in a served repository too.
        bad.append(f"INV-32: {feat} is approved but approval.date is missing or "
                   f"malformed ({signed!r}), so its panel era cannot be placed. "
                   f"Add the signature date; recover it with "
                   f"git log -S'status: approved' -- "
                   f".harness/*/features/{feat}/plan.yaml")
        continue
    if _era_start is not None and signed < _era_start:
        warn.append(f"INV-32: {feat} was signed {signed}, before the adversarial panel "
                    f"became available here ({_era_start}, harness.json "
                    f"panel_era_start); not graded. A plan signed before the panel "
                    f"existed cannot carry a record of it.")
        continue
# INV-32 ERA END (BUG-1071)
    panel = doc.get("panel")
    if not isinstance(panel, dict) or not str(panel.get("last_run", "")).strip() or not isinstance(panel.get("findings"), list):
        # THE MESSAGE NAMES THE ERA KEY (cycle-1 Q1/Q2). This is the line a migrating
        # legacy project sees, once per historical plan, the first time it upgrades: the
        # template merges `panel_era_start: null`, null means "no pre-panel era", and every
        # plan signed before that project's panel arrived is suddenly graded. The finding
        # is correct and fail-closed, but WITHOUT this sentence its cause is invisible --
        # the operator reads "no panel result recorded" against a plan signed months before
        # the panel existed and has no reason to look at config. Naming the key here is
        # what makes the residual self-diagnosing rather than merely reversible.
        bad.append(f"INV-32: {feat} plan is approved with no complete panel result "
                   f"recorded. If this plan predates the adversarial panel in this "
                   f"project, set harness.json `panel_era_start` to the date the panel "
                   f"became available here instead of recording one.")
        continue
    findings = panel.get("findings", [])
    finding_ids = {
        str(item.get("id", "")).strip()
        for item in findings if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    rulings = approval.get("rulings", [])
    if not isinstance(rulings, list):
        bad.append(f"INV-32: {feat} approval.rulings is malformed; expected a list.")
        rulings = []
    accepted_risks = set()
    for ruling in rulings:
        if not isinstance(ruling, dict):
            bad.append(f"INV-32: {feat} has a malformed approval ruling.")
            continue
        fid = str(ruling.get("finding", "")).strip()
        who = str(ruling.get("who", "")).strip()
        date = str(ruling.get("date", "")).strip()
        reason = str(ruling.get("reason", "")).strip()
        complete = bool(fid and who and reason and re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date
        ))
        if not complete:
            bad.append(
                f"INV-32: {feat} risk acceptance for {fid or '<missing>'} must carry "
                "finding, who, a valid date, and a non-empty reason."
            )
        if fid not in finding_ids:
            bad.append(f"INV-32: {feat} STALE RISK ACCEPTANCE {fid or '<missing>'}: a reworded "
                       f"finding gets a NEW content-hash id, so the old acceptance stopped "
                       f"applying and the operator is asked again.")
        elif complete:
            accepted_risks.add(fid)
    for item in findings:
        if not isinstance(item, dict):
            bad.append(f"INV-32: {feat} has a malformed panel finding.")
            continue
        fid = str(item.get("id", "")).strip() or "<missing>"
        severity = str(item.get("severity", "")).strip().lower()
        disposition = str(item.get("disposition", "")).strip().lower()
        if disposition == "resolved":
            warn.append(f"INV-32: {feat} finding {fid} disposition resolved.")
        elif fid in accepted_risks:
            warn.append(f"INV-32: {feat} operator accepted risk for finding {fid}.")
        elif severity not in {"info", "low", "med"}:
            bad.append(f"INV-32: {feat} finding {fid} is {severity or 'unrated'} and remains "
                       "open without operator risk acceptance.")
    expected_readers = {"should-not-exist", "scope", "goalcheck"}
    readers = panel.get("readers")
    if not isinstance(readers, list):
        readers = []
    by_reader = {
        str(item.get("reader", "")).strip(): item
        for item in readers if isinstance(item, dict) and str(item.get("reader", "")).strip()
    }
    for reader in sorted(expected_readers):
        item = by_reader.get(reader)
        status = str(item.get("status", "")).strip().lower() if isinstance(item, dict) else ""
        if status not in {"ran", "skipped"}:
            bad.append(f"INV-32: {feat} reader {reader} never ran or was not recorded; an unrecorded "
                       f"reader is not a clean reader.")
        elif status == "skipped":
            persona = str(item.get("persona", "")).strip()
            reason = str(item.get("reason", "")).strip()
            if not persona or not reason:
                bad.append(f"INV-32: {feat} reader {reader} was skipped without persona and reason; "
                           f"the record cannot show why it never ran.")
            else:
                warn.append(f"INV-32: {feat} reader {reader} skipped persona {persona}: {reason}")
# INV-32 END (FEAT-45 T-07)

# --- INV-3: a plan must be signed too, and re-planning must reset that signature.
for feat, plan in plans.items():
    if not has_approval_block(plan):
        bad.append(f"{fpath(feat, 'PLAN.md')} has no '## Approval' section.")
    elif not approved(plan):
        warn.append(f"{fpath(feat, 'PLAN.md')} approval is pending — awaiting the user.")

    # --- INV-4: every task must carry change_type or the qa gate cannot apply.
    # Tasks may be list items (`- T-01:`) or headings (`### T-01 —`) — the smoke's pm
    # wrote headings and the list-only regex made this check silently vacuous (DEC-129).
    tasks = re.findall(r"^(?:-\s*|#+\s*)(T-\d+)\b(.*?)(?=^(?:-\s*|#+\s*)T-\d+\b|\Z)",
                       plan, re.M | re.S)
    if not tasks and re.search(r"\bT-\d+\b", plan):
        bad.append(f"{fpath(feat, 'PLAN.md')} mentions T-NN ids but none parse as tasks — "
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
                bad.append(f"{fpath(feat, 'STATE.md')} references {tid}, which is absent from its PLAN.md.")

# THE GIT TOP LEVEL, resolved ONCE for INV-33 below (FEAT-41 T-14 / issue #867).
#
# RELATIVE TO THE GIT TOP LEVEL, NEVER TO `root`, and the reason CHANGED with the rebase while
# the requirement did not. `root` is no longer CLAUDE_PROJECT_DIR: since FEAT-42 T-12 this script
# resolves it through harness_boundary.resolve_root(_selfdir). That is the HARNESS root, which
# still need not be the repository top level — a worktree checkout is the everyday case, and this
# very file is being edited in one. `git show <sha>:<path>` takes a path relative to the
# repository, so using `root` would silently miss every plan in a worktree.
#
# ONE subprocess for the whole run, not one per feature. None on failure, which is one of
# INV-33's five deliberate silences: no git work tree is a state it cannot speak to.
try:
    _tl = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    _git_top = _tl.stdout.strip() if _tl.returncode == 0 else None
except Exception:
    _git_top = None

# --- INV-6..8: per-feature execution facts.
for fy in glob.glob(os.path.join(H, "*", "features", "*", "feature.json")):
    feat = os.path.basename(os.path.dirname(fy))
    # T-07 / issue #11 — a REAL parser, not a regex over two hand-listed shapes.
    #
    # What the regexes could not do: the block form required `\s*\n` after the `id:`
    # and `squad:` captures, so a trailing `# comment` on either line — legal YAML,
    # and the house style on 45 lines of FEAT-03's feature.json — silently dropped the
    # ENTIRE run, failing INV-6, INV-7 and INV-8 open at exit 0. Reproduced before the
    # fix. It had never fired only because those two lines happened to carry no
    # comments, and one author who hit it wrote a warning into the data file
    # (feature.json:63-64) instead of fixing the parser. Same defect class as DEC-123
    # and DEC-129; DEC-171 reverses the no-dependency clause that forced it.
    try:
        doc = harness_yaml.load_file(fy) or {}
    except Exception as e:
        # A file that does not parse is a VIOLATION, never a silent skip — the whole
        # point of DEC-171 is that there is no quieter mode. Report and move on
        # so one broken feature cannot hide every other feature's invariants.
        bad.append(f"{fpath(feat, 'feature.json')} does not parse, so INV-6..8 and INV-12 "
                   f"cannot be checked for it: {e}")
        continue
    if not isinstance(doc, dict):
        bad.append(f"{fpath(feat, 'feature.json')} is not a YAML mapping.")
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
    #
    # `runs` stays a 3-tuple on purpose: INV-7 and the INV-22 loop below unpack it as
    # exactly three, so widening it here would break two invariants to serve one.
    # BUG-1080's exemption gets its own list instead.
    runs = []
    code_reviewing_runs = []
    for entry in (doc.get("runs") or []):
        if not isinstance(entry, dict):
            bad.append(f"{feat}: a runs: entry is not a mapping ({entry!r}).")
            continue
        _squad = str(entry.get("squad", "")).strip()
        runs.append((str(entry.get("id", "")).strip(),
                     _squad,
                     str(entry.get("verdict", "")).strip()))
        # BUG-1080: a validator run that graded no CODE has no commit to pin. DEC-207
        # legalises exactly that run and spells it `code_grade: n_a`, so the record
        # states what was reviewed and INV-6 reads the claim rather than guessing.
        #
        # ABSENCE MEANS CODE REVIEW, so a pin is required. That is fail-CLOSED and it
        # is the OPPOSITE default from the `agent` key, where FEAT-31 made absence
        # deliberately benign — every run recorded before this key existed reviewed
        # code, and a silent exemption would retire the invariant on the whole corpus.
        # EXACT match, no strip and no case fold, so this test and
        # feature-schema.json's `enum: ["n_a"]` cannot disagree (panel Q2). A document
        # must never be schema-invalid and gate-exempt at the same time: any deviation
        # fails BOTH, which is the fail-closed direction.
        if _squad == "validator" and entry.get("code_grade") != "n_a":
            code_reviewing_runs.append(entry)

    # INV-6: reviewers must diff a pinned SHA, never a moving HEAD (DEC-50).
    # A placeholder is not a pin: val() returns str(v), so `review_sha: none` is a
    # truthy string and only an ABSENT key used to trip this (issue #16).
    #
    # The exemption is keyed on the RUN, never on approval.status (BUG-1080). Keying it
    # on a pending approval would turn green at signature and red again for the whole
    # build: the plan-phase runs stay in runs: while review_sha is unpinned until the
    # Building -> Review seam. One exempt run never silences a code-reviewing sibling.
    _sha = (val("review_sha") or "").strip().lower()
    if code_reviewing_runs and (
            _sha == "" or _sha in harness_yaml.PLACEHOLDER_UNSET):
        bad.append(f"{feat}: a validator run reviewed code but review_sha is not pinned "
                   f"— reviewers would diff HEAD (the GAP-7 failure). A run that graded a "
                   f"plan and no code carries `code_grade: n_a` and needs no pin (DEC-207).")

    # INV-33: a pin that is STALE, not merely absent (FEAT-41 T-14, closing issue #867).
    #
    # INV-6 above asserts a pin EXISTS. This asserts the pin is CURRENT. An absent pin is
    # honest — it says nobody reviewed this. A stale pin makes a CLAIM, that this text was
    # reviewed at this commit, and once the text has moved that claim is false while looking
    # byte-identical to a true one. Measured live on FEAT-41 itself: feature.json read one sha
    # while plan.yaml had been committed later, and a full run reported no INV-6 line for it.
    #
    # WHY A SEPARATE NUMBER, not a second INV-6 finding. The two have different PRECONDITIONS —
    # INV-6 needs only feature.json, this needs a git work tree and a plan file — and therefore
    # different silences, so folding them together would put two fail-open surfaces behind one
    # grep-able string. Six existing cases assert INV-6's exact text; a distinct number leaves
    # them untouched and makes each invariant separately searchable.
    #
    # A BYTE COMPARISON, NEVER A COMMIT COMPARISON. Comparing the pin to the last commit that
    # touched the plan reports a plan changed and changed back, and reports any feature reviewed
    # before an unrelated commit landed on that path. The bytes are what the pin actually
    # claims. Case (inv32.b) exists to kill the commit-equality implementation.
    #
    # SILENT, DELIBERATELY, ON FIVE STATES, four of which this invariant simply cannot speak to:
    # no git work tree; a pin that does not resolve; no plan file on disk; THE PLAN FILE EXISTS
    # BUT NOT AT THAT PATH IN THE PINNED COMMIT; and a TERMINAL station.
    #
    #   THE PATH-ABSENT SILENCE IS THE LARGEST IN THE TREE. Re-measured at execution time: 19 of
    #   44 feature directories sit in it, from layout history — the docs-layout migration and the
    #   PLAN.md-to-plan.yaml move each changed where a plan lives, and every one of those pins
    #   was honest about the path that existed when it was taken. The ONLY thing silencing it is
    #   the both-reads-succeed clause below, so an implementation that reads an absent object at
    #   the pin as evidence of staleness reds all nineteen at once. All nineteen are also
    #   terminal today, so live exposure is ZERO — which is exactly why case (inv32.d) pins the
    #   clause with a NON-TERMINAL fixture. Nothing in the tree can currently make it fail.
    #
    #   THE TERMINAL SCOPE IS LOAD-BEARING FOR FOUR SHIPPED FEATURES (operator answer Q6): a
    #   shipped plan is a record rather than a contract, and shipped history stays unrepaired.
    #   Without it this goes red on four of them the moment it lands.
    #
    # A VALIDATOR RUN IS NOT ONE OF THE SILENCES. That precondition was dropped deliberately: a
    # recorded run is a LAGGING indicator that can only fire after a panel has already read the
    # wrong text, which is how this feature's own divergence survived.
    if _git_top and _sha and _sha not in harness_yaml.PLACEHOLDER_UNSET \
            and station_of(os.path.dirname(fy)) not in ("done", TERMINAL_MARKER):
        _pf = os.path.join(os.path.dirname(fy), "plan.yaml")
        if not os.path.isfile(_pf):
            _pf = os.path.join(os.path.dirname(fy), "PLAN.md")
        if os.path.isfile(_pf):
            # REALPATH BOTH SIDES. `git rev-parse --show-toplevel` returns the resolved
            # path, and on macOS the temp dir every fixture uses is a symlink
            # (/var -> /private/var). Mixing the two makes relpath emit a
            # `../../..`-prefixed path, `git show` fail, and this invariant go SILENT —
            # measured, and the same mismatch T-07 hit in worktree_terminal.
            _prel = os.path.relpath(os.path.realpath(_pf), os.path.realpath(_git_top))
            _shown = subprocess.run(["git", "-C", root, "show", f"{_sha}:{_prel}"],
                                    capture_output=True)
            try:
                with open(_pf, "rb") as _pfh:
                    _disk = _pfh.read()
            except OSError:
                _disk = None
            # BOTH reads must succeed. See the path-absent paragraph above — this one clause is
            # what keeps 19 honest pins quiet.
            if _shown.returncode == 0 and _disk is not None and _shown.stdout != _disk:
                # THE FINDING NAMES THREE THINGS: the feature, the pinned sha, and the last
                # commit to touch that plan. A finding that says only "stale" makes the reader
                # redo the measurement.
                _last = subprocess.run(
                    ["git", "-C", root, "log", "-1", "--format=%h", "--", _prel],
                    capture_output=True, text=True)
                _lastsha = _last.stdout.strip() or "(unknown)"
                bad.append(f"{feat}: review_sha {_sha} is STALE — {os.path.basename(_pf)} has "
                           f"changed since it was pinned, last at {_lastsha}, so the review "
                           f"claim covers text that is no longer there (INV-33).")

    # INV-7: the fix-loop bound must actually count the failures it bounds.
    fails = sum(1 for _, _, v in runs if v.upper() == "FAIL")
    cu = val("cycles_used")
    if cu is not None and cu.isdigit() and int(cu) < fails:
        bad.append(f"{feat}: cycles_used={cu} but {fails} FAIL run(s) recorded "
                   f"— the fix loop is no longer bounded.")

    # INV-22: RUNS are counted, because cycles do not count them (issue #79).
    # DEC-157 makes a cycle REWORK ONLY, so a first-pass run contributes zero however
    # many steps it has. That is right for what the cycle budget guards, and it left
    # total runs unbounded AND uncounted: FEAT-03 ran 19 times against a 6-cycle count
    # and tripped nothing. Cost was the other long-feature signal and DEC-178 deleted
    # it, so without this nothing at all notices a feature running long.
    #
    # DELIBERATELY A NOTE, NOT A VIOLATION. A high run count is not itself a defect —
    # a long feature is fine when each run is efficient, resolves issues and advances
    # the SCs. A third HARD budget that stops work needs a much stronger case than one
    # that flags, so this one flags and names those three questions.
    #
    # THE COUNT IS A FLOOR, not a total: a main-session-direct segment is not a run and
    # never appears in runs: — on FEAT-07 that hid eight of ten tasks. Said in the
    # message so nobody reads the number as complete.
    # A BUDGET THIS INVARIANT CANNOT RESOLVE IS REPORTED, NEVER SILENTLY DROPPED.
    # First cut read the key and fell through on anything unexpected, so a harness.json
    # that PARSES FINE but has no `budgets.max_total_runs` disabled INV-22 with no
    # diagnostic — and the shipped templates/examples/harness.kaya-ai.json is exactly
    # that shape, so a project onboarded from it got a check that never ran. DEC-160
    # records the identical config lag for max_total_cycles. Worse, `true` satisfied
    # isinstance(x, int) — bool subclasses int in Python — so it "worked" while "20"
    # and 20.0 did not.
    def _as_budget(v):
        """int, or None with a reason. bool is rejected BEFORE the int check."""
        if isinstance(v, bool):
            return None, f"{v!r} is a boolean"
        if isinstance(v, int):
            return (v, None) if v >= 0 else (None, f"{v} is negative")
        if isinstance(v, float):
            return (int(v), None) if v.is_integer() and v >= 0 else (None, f"{v!r} is not a whole number")
        if isinstance(v, str) and v.strip().isdigit():
            return int(v.strip()), None
        return None, ("absent" if v is None else f"{v!r} is not a number")

    _budget, _why = None, "harness.json could not be read"
    try:
        _hj = json.load(open(os.path.join(H, "harness.json"), encoding="utf-8"))
        _budget, _why = _as_budget((_hj.get("budgets") or {}).get("max_total_runs"))
    except Exception as e:
        _budget, _why = None, f"harness.json could not be read ({type(e).__name__})"
    _declared = val("max_total_runs")
    if _declared is not None:                 # a per-feature value outranks the default
        _d, _dwhy = _as_budget(_declared.strip() if isinstance(_declared, str) else _declared)
        if _d is None:
            warn.append(f"INV-22 {feat}: its own max_total_runs is unusable ({_dwhy}) — "
                        f"falling back to the harness.json default.")
        else:
            _budget, _why = _d, None
    if _budget is None:
        warn.append(f"INV-22 {feat}: run counting is INACTIVE — budgets.max_total_runs "
                    f"{_why}. {len(runs)} runs recorded and nothing is watching them. "
                    f"Set it in .harness/harness.json (default 20).")
    elif len(runs) > _budget:
        warn.append(f"INV-22 {feat}: {len(runs)} runs recorded against a {_budget}-run budget "
                    f"(cycles_used={val('cycles_used')} counts REWORK only, DEC-157, so it "
                    f"does not see this). Not a defect by itself — check each run is "
                    f"efficient, is resolving issues, and is advancing the SCs. The count "
                    f"is a FLOOR: main-session-direct segments are not runs.")

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
            warn.append(f"{feat}: run dir {rid} exists on disk but feature.json does not "
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
    # SEPARATE EVENT, SEPARATE ASSERTION (issue #132). The PreToolUse check above passes
    # on a tree where the PostToolUse half was never installed — and that half is the
    # only one covering Edit, Bash and the main session, so its absence restores the
    # 1-of-4 coverage the issue measured while every other line here stays green.
    # THE MATCHER IS PART OF THE ASSERTION, not decoration. A reviewer narrowed this
    # registration to `Write` in all three copies and every gate stayed green, which
    # reverts issue #132 entirely while the tree reports itself correct: `Write` alone is
    # the ONE route that already worked. So name the tools and check for them.
    # EXISTENTIAL, NOT FIRST-MATCH. `next(...)` read only the FIRST entry mentioning
    # check-domain, so prepending a compliant decoy and narrowing the real registration
    # back to `Write` passed all four gates while restoring the 1-of-4 coverage issue #132
    # measured — two lines in one file, defeating the assertion this change added. Coverage
    # is unioned across every entry that runs the script, the same shape merge-settings.py's
    # hook_present uses, because a project may legitimately split one requirement in two.
    post = hooks.get("PostToolUse") or []
    def _runs_cd(entry):
        # TOKEN, not substring — `check-domain.sh.disabled` contains the name and runs
        # nothing. A decoy entry naming a disabled copy widened this check's coverage set
        # and let the real registration be narrowed to `Write` with all four gates green.
        for _h in (entry.get("hooks") or []):
            for _tok in str(_h.get("command", "")).split():
                if os.path.basename(_tok) == "check-domain.sh":
                    return True
        return False

    _pts = [e for e in post if _runs_cd(e)]
    _want = {"Write", "Edit", "Bash"}
    _have = set()
    for _e in _pts:
        _m = str(_e.get("matcher", "")).strip()
        if _m in ("", "*", ".*"):
            _have |= _want
        else:
            # A matcher is user-authored text, not a guaranteed regex — `Bash(git:*)` is
            # the permission-rule form people paste in, and it raises. An UNCAUGHT raise
            # here exits 1 with EMPTY stdout, which the /harness gate reads as "violations
            # found" with nothing to read, and every invariant below this line never runs.
            # A bad matcher is a finding, not a crash: it matches no tool, so report it AND
            # leave those tools uncovered.
            try:
                _have |= {t for t in _want if re.search(_m, t)}
            except re.error as _re:
                bad.append(f"INV-9: the PostToolUse check-domain matcher {_m!r} is not a "
                           f"valid regular expression ({_re}) — Claude Code matches nothing "
                           f"with it, so the shape gate covers no tool through this entry. "
                           f"Correct the matcher in .claude/settings.json.")
    _pt = _pts[0] if _pts else None
    if _pt is None:
        bad.append("No PostToolUse check-domain hook — the DEC-150 state-file SHAPE "
                   "budgets bind only a `Write` by a harness agent (1 of 4 routes); "
                   "Edit, Bash and the main session write over budget in silence "
                   "(issue #132). INV-23 below still sweeps, one entry late.")
    elif not _want <= _have:
        bad.append(f"PostToolUse check-domain is registered across {len(_pts)} entry/entries "
                   f"but nothing matches {sorted(_want - _have)}. "
                   f"The shape gate only reaches the tools it matches, so a narrowed "
                   f"matcher restores the 1-of-4 coverage issue #132 measured, silently.")
    elif not any(" --post" in str(_e) for _e in _pts):
        bad.append("PostToolUse check-domain is registered without ` --post`. Mode also "
                   "resolves from hook_event_name, so this is not fatal — but the flag is "
                   "the half we control, and a registration missing it degrades to "
                   "pre-mode the moment the platform field changes (issue #132).")

# OMP-native port invariant. Legacy/consumer projects without `.omp/config.yml`
# continue through the Claude compatibility checks above; once a project opts into
# the native surface, every canonical source and adapter must stay coherent.
_omp_cfg = os.path.join(root, ".omp", "config.yml")
if os.path.isfile(_omp_cfg):
    _omp_check = os.path.join(root, ".agents", "skills", "harness", "bin", "check-omp-port.py")
    if not os.path.isfile(_omp_check):
        bad.append("OMP port is configured but check-omp-port.py is missing.")
    else:
        _omp_result = subprocess.run(
            [sys.executable, _omp_check, root],
            text=True,
            capture_output=True,
        )
        if _omp_result.returncode != 0:
            for _line in (_omp_result.stderr or "").splitlines():
                if _line.strip():
                    bad.append(_line.strip())

# `cj` is the parsed harness.json, consumed below by the test_kinds, github.sync and
# gh-config checks. The JSON-validity violation is kept on its own merit — a config
# that does not parse silently disables every check that reads it.
# BOUND UNCONDITIONALLY. `cj` used to be assigned only inside the `if cfg:` below, so a
# project with NO harness.json reached the consumers further down with the name unbound and
# died with `NameError: name 'cj' is not defined`. That is a CRASH, and a crash exits 1 —
# the same code a real violation exits — so /harness entry reported "violations found" for
# an absent config file, with a traceback where a diagnosis should be.
#
# Pre-existing and reproduced on main at the same fixture before being fixed here; found
# while landing DEC-182 because a plan.yaml fixture legitimately carries no harness.json.
# Fixed in passing rather than left in a file this change already opens: check-state.sh is
# a DEC-174 carve-out, so the next person to touch it pays the full carve-out cost, and
# leaving a known landmine for them is worse than a two-line diff here. The absent-config
# case is already reported by the INV-1 check above; this only stops the crash.
cj = {}
cfg = read(os.path.join(H, "harness.json"))
if cfg:
    try:
        cj = json.loads(cfg)
    except Exception:
        cj = {}
        bad.append(".harness/harness.json is not valid JSON.")
_handoff_baseline = set()
for _entry in cj.get("handoff_done_when_baseline", []) if isinstance(cj, dict) else []:
    if not isinstance(_entry, str):
        continue
    _path = os.path.relpath(_entry, root) if os.path.isabs(_entry) else _entry
    _handoff_baseline.add(os.path.normpath(_path).replace(os.sep, "/"))

import subprocess

# --- INV-17 (DEC-159): squad seams hand off through notes/handoff-<stem>.md.
# A feature whose status: sits past a seam with no handoff note for the crossing lost the
# predecessor's working memory — recoverable (disk-only is supported) but never silent.
#
# This block was keyed on a `phase` field until DEC-150/D-12 (FEAT-14). phase and status
# collapsed into ONE field whose values are the GitHub board's six columns, and phase was
# deleted from every feature file. The old constant — named PHASE_ORDER, holding
# plan/build/validate/ship — is recorded here because leaving it standing was the actual
# hazard: with phase gone from the corpus the read returns the empty string on every
# feature, the membership test fails on every feature, and the loop `continue`s on every
# feature. INV-17 would stop examining anything at all while check-state.sh went on exiting
# exactly as it does today. A gate that examines nothing reports nothing wrong.
#
# THE STEMS ARE LOWERCASE LITERALS AND ARE DELIBERATELY NOT DERIVED FROM THE STATION NAMES.
# The next editor's first instinct is to build the filename from the station; do not. The stems
# are seam names — plan, build, validate — and the stations are positions. They now happen to
# share a case, which is exactly what makes deriving look safe and still be wrong: `ready` and
# `building` both require notes/handoff-plan.md, and no station is named `validate` at all.
# Keeping the stems as their own literals also renames no file on disk.
#
# THE RESIDUAL LOSS, RECORDED RATHER THAN HIDDEN: validate and ship both folded into
# review, so the validate-to-ship crossing is no longer separately observable and
# handoff-validate.md cannot be demanded at review. It is demanded at done instead — the
# next boundary that proves review completed. One seam moves later; none is dropped.
#
# A STATION OUTSIDE STATUS_ORDER IS NOW A VIOLATION, NOT A SILENT SKIP (FEAT-41 T-07, A-03).
# It was a deliberate silent skip on the grounds that status was schema-required with a closed
# enum, so an unknown value was already denied at write time and a branch here would have been
# a second enforcement point for a rule the schema owned. THAT COMPENSATING CONTROL IS GONE:
# T-07 deleted the key from feature-schema.json, and the station now lives in plan.yaml, whose
# schema does not constrain the top-level `status` value at all. What denies an illegal station
# today is plan-merge.py's set-feature-station, which validates before it opens the file — an
# enforcement point on the WRITE ROUTE, not on the document. A hand-edited plan therefore
# reaches this loop with a station nothing has checked, and the old skip would have taken every
# such feature out of INV-17 without a word. It is reported instead.
#
# Despite the name, STATUS_ORDER is used as a SET — the membership test below is its only
# reader and nothing indexes it. So the marker sitting at the end implies no progression.
#
# STATUS_ORDER AND SEAM_NOTES ARE ONE VOCABULARY AND MOVE TOGETHER. SEAM_NOTES is indexed by a
# BARE SUBSCRIPT below, guarded only by that membership test, so rekeying one without the other
# does not degrade to a skip — it is a KeyError in the project's own state gate, for every
# well-formed feature on disk. Derived from factory_config rather than spelled, which makes the
# pairing structural: both are built from MANDATED_STATIONS, so neither can be rekeyed alone.
STATUS_ORDER = list(factory_config.MANDATED_STATIONS) + [TERMINAL_MARKER]
SEAM_NOTES = {
    "backlog":  [],
    "plan":     [],
    "ready":    ["plan"],
    "building": ["plan"],
    "review":   ["plan", "build"],
    "done":     ["plan", "build", "validate"],
    # THE TERMINAL MARKER REQUIRES NO HANDOFF, and that is the whole difference from done. A
    # feature planned and never built crossed no seam, so there is no honest handoff note to
    # write and none will be fabricated. Keyed EXPLICITLY rather than omitted: an omitted key is
    # now a KeyError rather than a silent skip, since the station passes the membership test
    # above by construction.
    TERMINAL_MARKER: [],
}
# EVERY STATION IN THE VOCABULARY HAS A SEAM ROW, asserted here rather than trusted. The two
# structures are derived from the same source, so the only way they can disagree is a hand-typed
# SEAM_NOTES key — and this is the check that catches it at startup instead of at the subscript,
# on whichever feature happens to sit at that station.
_missing_seam_rows = [_s for _s in STATUS_ORDER if _s not in SEAM_NOTES]
if _missing_seam_rows:
    bad.append("check-state.sh: SEAM_NOTES has no row for station(s) %s — the seam table and "
               "the station vocabulary have drifted, and INV-17 would raise KeyError on the "
               "first feature at one of them." % ", ".join(_missing_seam_rows))
HANDOFF_SECTIONS = ["## next", "## trust", "## dead ends", "## working set", "## done when"]
HANDOFF_NARRATIVE_HEADINGS = HANDOFF_SECTIONS[:4]

# The literal exemption set. FEAT-01 and FEAT-02 are Done, carry zero handoff notes, and
# finished before DEC-159 existed: no seam was crossed, so no honest handoff note can be
# written for them and none will be fabricated (PRINCIPLES rule 15). A finite list, not an
# inferred rule — no future feature can join it.
#
# Matched by PREFIX because a feature directory is FEAT-01-<slug>, and FEAT-01's happens to
# be bare today. Exact equality would pass every fixture and still raise three violations
# on the live corpus the moment either directory gained a slug.
#
# This one is a SILENT skip, unlike the plan-keyed exemption below, which reports. The
# difference is deliberate: reporting exists so a WRONGLY granted exemption is visible, and
# a two-element list that cannot grow has nothing to grant wrongly.
HANDOFF_EXEMPT_LITERAL = ("FEAT-01", "FEAT-02")

def _handoff_exempt(fdir):
    """The plan-keyed exemption (DEC-174). Returns a reason string when the feature owes no
    handoff notes, or "" when it does. The second value is a detail to append to the
    violation when the plan could not be read.

    A feature built entirely main-session-direct runs no squad, crosses no seam and is owed
    no note. THREE CONJOINED CONDITIONS, all necessary: (1) a plan.yaml exists — a PLAN.md
    does NOT qualify and is never read here; (2) its tasks: list is present and NON-EMPTY;
    (3) EVERY task carries an explicit execution_mode of exactly main-session-direct.

    KEYED ON THE PLAN'S EXECUTION MODES, NEVER ON THE NOTES' ABSENCE. Keyed on absence, the
    invariant would be satisfied by the exact condition it exists to detect.

    Condition 2 is a vacuity guard and excludes nobody in today's corpus — every plan.yaml
    on disk has a non-empty tasks: list. It is kept because "every task is
    main-session-direct" is VACUOUSLY TRUE over an empty list, so a stub plan, a
    half-written one, or one whose tasks: key was mistyped would otherwise be silently
    exempted from a seam invariant. What actually excludes FEAT-01 through FEAT-05 is
    condition 1, in all five cases.

    A DELIBERATE FALSE NEGATIVE: FEAT-06 and FEAT-07 are all-main-session-direct too, but on
    PLAN.md, so condition 1 keeps them non-exempt and they keep owing their notes. That is
    the safe direction and costs nothing — both already carry every note their status
    demands. Do not widen condition 1 to reach PLAN.md.

    FAIL CLOSED: any read error, parse error or non-mapping task entry is NOT exempt.
    """
    pp = os.path.join(fdir, "plan.yaml")
    if not os.path.isfile(pp):
        return "", ""
    try:
        pdoc = harness_yaml.load_file(pp) or {}
    except Exception as e:
        return "", f" (its plan.yaml does not parse, so no exemption could be evaluated: {e})"
    if not isinstance(pdoc, dict):
        return "", " (its plan.yaml is not a mapping, so no exemption could be evaluated)"
    tasks = pdoc.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return "", ""
    for t in tasks:
        if not isinstance(t, dict):
            return "", (" (its plan.yaml has a task that is not a mapping, so no "
                        "exemption could be evaluated)")
        if str(t.get("execution_mode", "")).strip() != "main-session-direct":
            return "", ""
    return (f"every task in its plan.yaml is execution_mode main-session-direct (DEC-174), "
            f"so no squad ran and no seam was crossed"), ""

for fy in glob.glob(os.path.join(H, "*", "features", "*", "feature.json")):
    feat = os.path.basename(os.path.dirname(fy))
    # F-02: parsed, not regex-scanned. `^status:\s*(\S+)` misses a quoted value and a
    # block scalar, both legal YAML — and a miss here is silent: the feature is skipped
    # entirely by `continue`, so the invariant never runs and never says why.
    #
    # The feature.json read STAYS, because this loop still needs the document to report an
    # unparseable one; only the STATION now comes from plan.yaml (FEAT-41 T-07).
    try:
        _doc = harness_yaml.load_file(fy) or {}
    except Exception as e:
        bad.append(f"{fpath(feat, 'feature.json')} does not parse, so its seam invariants "
                   f"cannot be checked: {e}")
        continue
    _status = station_of(os.path.dirname(fy))
    if not _status:
        # NO STATION AT ALL is still a skip, and deliberately so: a feature directory with no
        # plan.yaml is a PLAN.md-era record, and INV-3 already reports a plan that should exist
        # and does not. Reporting it here too would double every such line.
        continue
    if _status not in STATUS_ORDER:
        # LOUD, per A-03: nothing denies this value at write time any more. See the comment
        # above STATUS_ORDER for why the old silent skip's justification no longer holds.
        bad.append(f"{fpath(feat, 'plan.yaml')} records station '{_status}', which is not in "
                   f"the station vocabulary ({', '.join(STATUS_ORDER)}), so its seam "
                   f"invariants cannot be checked. Set it with `plan-merge.py "
                   f"set-feature-station`, which validates the station before it writes.")
        continue
    _lit = feat.startswith(HANDOFF_EXEMPT_LITERAL)
    # Evaluated LAZILY — only when a required note is actually found missing, never for
    # every feature on every run — and cached, so a feature owing three notes reads its
    # plan once and emits ONE line rather than three near-identical ones.
    _ex_why, _ex_detail, _ex_stems = None, "", []
    for prev in SEAM_NOTES[_status]:
        hp = os.path.join(os.path.dirname(fy), "notes", f"handoff-{prev}.md")
        if not os.path.isfile(hp):
            if _lit:
                continue
            if _ex_why is None:
                _ex_why, _ex_detail = _handoff_exempt(os.path.dirname(fy))
            if _ex_why:
                _ex_stems.append(prev)
                continue
            # M-01: this said `pm_.group(1)` — a leftover from the regex the F-02
            # conversion deleted when it renamed the parsed value. Used once, assigned
            # nowhere, so it raised NameError on the ONE condition INV-17 exists to
            # detect, aborting INV-13/15/16/18/21 and INV-10 with no "could not run"
            # message. A crash exits 1, which is what a real violation exits, so
            # /harness entry reported "violations found" for a typo. Introduced by the
            # fix for F-02 and caught by the re-review, not by any gate.
            bad.append(f"{feat}: status is '{_status}' but notes/handoff-{prev}.md is "
                       f"missing — the {prev} seam was crossed without a handoff; the "
                       f"successor is on the disk-only path (DEC-159).{_ex_detail}")
            continue
    # INV-17 handoff shape pass, all stems (FEAT-31 T-14)
    # ONE call site for the shape check, by STRUCTURE and not by an ordering rule: the loop
    # above now owns only the missing-note question, and this glob owns only the shape
    # question. Because the glob finds every note including the seam stems, no file can be
    # reported twice — there is no second place that could report it.
    #
    # WHY A GLOB. check-domain.sh's RE_HANDOFF already accepts handoff-[a-z0-9-]+.md, so a
    # mid-phase note is already legal to write and was, until now, never opened. Measured at
    # cf51dce in the FEAT-31 worktree: 74 notes match, 71 on seam stems and THREE on
    # non-seam stems newly in reach — FEAT-09/handoff-ship.md (56 lines),
    # FEAT-22/handoff-t09-rotation.md (50), FEAT-24/handoff-ship.md (60, exactly on the cap
    # with no headroom). All 74 carry the four headings and are within the cap, so this pass
    # adds ZERO violations at that sha. The plan measured 69 at 7299669; the five-note gap
    # reconciles exactly — FEAT-30's three notes plus FEAT-29's handoff-validate.md plus
    # FEAT-31's own handoff-build.md all landed after that reading.
    #
    # EXEMPTIONS DO NOT REACH HERE, deliberately. HANDOFF_EXEMPT_LITERAL and
    # _handoff_exempt gate the missing-note branch above only: they answer whether a note is
    # OWED. Once a file exists its shape is checked whoever wrote it and whatever the
    # feature's status.
    for hp in sorted(glob.glob(os.path.join(os.path.dirname(fy), "notes", "handoff-*.md"))):
        _text = read(hp) or ""
        hl = [l.strip().lower() for l in _text.splitlines()]
        _rel_handoff = os.path.normpath(os.path.relpath(hp, root)).replace(os.sep, "/")
        miss = [h for h in HANDOFF_NARRATIVE_HEADINGS if h not in hl]
        if "## done when" not in hl and _rel_handoff not in _handoff_baseline:
            miss.append("## done when")
        # INV-17 empty-body check (FEAT-31 T-10)
        # SC-15 requires the relay be SHOWN TO FAIL when "## Next" is emptied. Until now it
        # could not be: `miss` tests only that the HEADING is present, so a note carrying all
        # four headings and nothing under any of them passed. A heading with no body is the
        # shape of a handoff that satisfies the gate and tells the successor nothing.
        #
        # A body runs from its heading to the next line whose stripped form starts with two
        # hash characters, or end of file, and is EMPTY when every one of those lines is blank
        # after stripping. Only headings actually PRESENT are examined — an absent heading is
        # already `miss`'s finding and must not be reported twice under a second name.
        #
        # MIGRATION, re-measured at 1929774 in the FEAT-31 worktree rather than copied from
        # the plan: 74 notes match, and ZERO have an empty required section. The three
        # non-seam stems T-14's glob newly reaches carry 13, 6 and 8 non-blank lines under
        # "## Next" (FEAT-09/handoff-ship.md, FEAT-22/handoff-t09-rotation.md,
        # FEAT-24/handoff-ship.md) — the same figures the plan measured at 7299669. So this
        # adds zero violations.
        _empty = []
        for _i, _l in enumerate(hl):
            if _l not in HANDOFF_NARRATIVE_HEADINGS:
                continue
            _body = []
            for _n in hl[_i + 1:]:
                if _n.startswith("##"):
                    break
                _body.append(_n)
            if not any(_b for _b in _body):
                _empty.append(_l)
        _done_when_problems = []
        if "## done when" in hl:
            if handoff_done_when is None:
                _done_when_problems.append(
                    "handoff_done_when.py could not be imported: "
                    f"{type(_handoff_done_when_error).__name__}: {_handoff_done_when_error}")
            else:
                _done_when_problems.extend(
                    handoff_done_when.problems(_rel_handoff, _text, root, resolve=False))
        if miss or len(hl) > 60 or _empty or _done_when_problems:
            why = []
            if miss:
                why.append(f"missing section(s) {miss}; follow templates/HANDOFF.md")
            if len(hl) > 60: why.append(f"{len(hl)} lines vs cap 60")
            if _empty: why.append(f"empty section(s) {_empty}")
            why.extend(_done_when_problems)
            bad.append(f"{feat}: notes/{os.path.basename(hp)} fails the shape "
                       f"({'; '.join(why)}) — a freeform handoff drifts like an "
                       f"unvalidated digest did (DEC-159/160).")
    if _ex_stems:
        # Reported, never silent: a wrongly granted exemption must be VISIBLE rather than
        # look like a pass. It goes through warn and its text must NOT carry the word that
        # marks a violation — the shipping gate builds a baseline from those lines, and a
        # note worded as one would pollute that diff.
        warn.append(f"INV-17 {feat}: exempt from handoff notes — {_ex_why}. Suppressed "
                    + ", ".join(f"handoff-{s}" for s in _ex_stems) + ".")

# --- INV-18 (DEC-160): a feature with run dirs but no feature.json is invisible to
# every feature-keyed invariant (INV-8/12/17) — a whole phase can run unchecked.
# Observed live: FEAT-03's plan phase ran to completion before feature.json existed.
for rd in glob.glob(os.path.join(H, "*", "features", "*", "runs")):
    fdir = os.path.dirname(rd)
    # isdir FIRST: glob matches a plain file named `runs` too, and os.listdir on it raises
    # NotADirectoryError — exit 1, empty stdout, every later invariant skipped.
    if os.path.isdir(rd) and os.listdir(rd) and not os.path.isfile(os.path.join(fdir, "feature.json")):
        bad.append(f"{os.path.basename(fdir)}: has runs/ but no feature.json — the feature is "
                   f"invisible to run reconciliation and phase checks; instantiate it from "
                   f".agents/skills/harness/templates/feature.json (the playbook's first-cycle "
                   f"duty).")

# --- INV-34 (FEAT-41 T-19): every feature directory carries a plan.yaml, because that is the
# ONLY place a station may be recorded and a feature without one cannot record its own.
#
# OPERATOR-DIRECTED, after this feature proved the hole by falling into it. T-07 deleted
# `status: Review` from BUG-1030 -- plan-less and non-terminal -- and it could not be put back:
# feature.json refuses the key (undeclared, exit 11) and, before T-19, plan.yaml refused to exist
# without tasks. The record was representable NOWHERE. Twelve directories were backfilled with
# station-only plans; this is what stops the thirteenth reintroducing the hole in silence.
#
# A STATION-ONLY PLAN SATISFIES IT. The check is that the record EXISTS, not that it carries
# tasks: a feature that predates the format, or a bug fix opened without a plan, honestly has no
# tasks to record and inventing some to pass a schema would be fabrication.
for fy in sorted(glob.glob(os.path.join(H, "*", "features", "*", "feature.json"))):
    _fdir = os.path.dirname(fy)
    if not os.path.isfile(os.path.join(_fdir, "plan.yaml")):
        bad.append(f"INV-34: {os.path.basename(_fdir)} has no plan.yaml, so it has nowhere to "
                   f"record its station — feature.json cannot hold one (the schema declares no "
                   f"`status` key). Create a station-only record: `schema: plan/1`, `feature:`, "
                   f"`status: <station>`, `station_only: true`, `tasks: []`, written through "
                   f"plan-merge.py apply. The marker is REQUIRED and is not inferred from an "
                   f"empty `tasks:` — an emptied plan is not a station-only record.\n"
                   f"    FIRST CHECK WHETHER A REAL PLAN WAS DELETED: `git log --diff-filter=D "
                   f"-- {os.path.join(os.path.relpath(_fdir, root), 'plan.yaml')}`. If this "
                   f"feature HAD tasks, restore that plan instead — a station-only stub would "
                   f"record the station and silently discard the task history.")

# --- INV-23 (DEC-150, mechanized — issue #132): the feature.json and STATE.md budgets,
# swept from DISK. check-domain.sh enforces the same numbers on a WRITE payload, which is
# where they can still be prevented; this reads the file as it actually is, so no tool and
# no author identity can route around it — including a session where the PostToolUse half
# of that hook was never registered, which is the case INV-9 above reports.
#
# WARN, not bad, and the reason is measured rather than tidy: run against this tree the
# day it landed, it found FEAT-05/STATE.md at 165 lines against a 120 budget and five
# illegal sections, and FEAT-02/STATE.md with five more — both predating the gate. Making
# them halt /harness entry would convert a reporting backstop into an unrelated cleanup
# that has to land first. The write-time gate is the one with teeth; this one's job is
# that the drift reaches a human.
#
# VOCABULARY stays in sync with check-domain.sh; the MECHANISM deliberately does not
# (D-02) — that one measures a payload, this one measures a file.
for fy in sorted(glob.glob(os.path.join(H, "*", "features", "*", "feature.json"))):
    _ftext = read(fy) or ""
    fl = _ftext.splitlines()
    feat = os.path.basename(os.path.dirname(fy))
    # 300, not 200: FEAT-10 measures 173 lines with 32 runs, roughly 5 lines per run.
    #
    # THE COUNT EXCLUDES `runs:` (FEAT-54 backlog B-4), through the SAME helper the
    # write-time gate uses — the vocabulary sync this block's header promises now covers the
    # definition of a counted line, not only the wording of the message.
    try:
        import feature_schema as _fs_inv23
        _inv23_budget = _fs_inv23.FEATURE_JSON_LINE_BUDGET
        _inv23_count = _fs_inv23.journal_lines(_ftext)
        _inv23_basis = "excluding the runs ledger"
    except Exception:
        _inv23_budget = 300
        _inv23_count = len(fl)
        _inv23_basis = "whole file — feature_schema was not importable"
    if _inv23_count > _inv23_budget:
        warn.append(f"INV-23 {fpath(feat, 'feature.json')} is {_inv23_count} lines "
                    f"({_inv23_basis}) — budget is {_inv23_budget}. It is "
                    f"data a script parses, not a journal (DEC-150).")
    # The comment-line budget is GONE, not relaxed: JSON has no comments, so it could never
    # fire, and a check that cannot fire is a check a reader trusts.

# CLAUDE.md (issue #139), swept from disk like its peers. The write-time gate in
# check-domain.sh is the one with teeth; this is the backstop for a session where the
# PostToolUse half was never registered, exactly as for the four state files below.
_cm = os.path.join(root, "CLAUDE.md")
_cml = (read(_cm) or "").splitlines()
if _cml and len(_cml) > 80:
    warn.append(f"INV-23 CLAUDE.md is {len(_cml)} lines — budget is 80 (DEC-181). It is "
                f"preloaded into EVERY session, so a line here costs more than a line "
                f"anywhere else; rationale belongs in .harness/harness/docs/DECISIONS.md.")

for sm in sorted(glob.glob(os.path.join(H, "*", "features", "*", "STATE.md"))):
    sl = (read(sm) or "").splitlines()
    feat = os.path.basename(os.path.dirname(sm))
    if len(sl) > 120:
        warn.append(f"INV-23 {fpath(feat, 'STATE.md')} is {len(sl)} lines — budget is 120. It holds no "
                    f"history: ## Current is replaced, never appended (DEC-150).")
    illegal = [l.strip() for l in sl
               if l.startswith("## ") and l.strip() not in ("## Current", "## Open Questions")]
    if illegal:
        warn.append(f"INV-23 {fpath(feat, 'STATE.md')} has illegal section(s) {illegal} — STATE.md is "
                    f"`## Current` + `## Open Questions` and nothing else (SPEC §2).")

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
    "cycles_used",
    # The money key below is HISTORICAL-ONLY (DEC-178): nothing produces it any more,
    # but all 67 pre-FEAT-08 run state.yaml files carry it and :401 flags any key not
    # in this set — drop it and every historical run becomes a violation. Named
    # without its quoted spelling because this task's verify: counts that spelling.
    "cost",
    # pins and context markers
    "flow", "task", "team", "branch", "worktree",
    "review_sha", "pinned_sha", "base_sha", "head_sha", "tip_sha", "commits",
    # roll-up enums and the report pointer — matchable values, so checkpoint-legal
    "verdict", "severity_max", "digest",
}
vd = os.path.join(root, ".agents/skills/harness/bin/validate-digest.py")
# INV-15 used to fork one interpreter per completed lead run. Measured on this tree: 103
# spawns costing 3.02s of a 3.45s run — 87% of the time the operator waits at every
# /harness entry, and it grows with run history because historical digests are re-validated
# forever. Load the module ONCE instead. `validate()` is a pure function of (persona, text)
# and the CLI lives behind `if __name__ == "__main__":`, so importing runs nothing.
# _vd_mod is None when the file is absent or will not import; the loop below then reports
# digests as UNCHECKED rather than passing them silently.
_vd_mod = None
_vd_import_err = None
if os.path.isfile(vd):
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("harness_validate_digest", vd)
        _vd_mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_vd_mod)
        if not callable(getattr(_vd_mod, "validate", None)):
            _vd_mod, _vd_import_err = None, "it defines no validate() function"
    except Exception as _e:
        _vd_mod, _vd_import_err = None, str(_e)
for sy in glob.glob(os.path.join(H, "*", "features", "*", "runs", "*", "state.yaml")):
    rel = os.path.relpath(sy, H)
    rundir = os.path.dirname(sy)
    # F-02, and this one had a LIVE fail-open the panel reproduced: `status: "complete"`
    # — quoted, legal YAML — does not match `^status:\s*complete`, so `complete` was
    # False and the completed-run checks below silently never fired.
    try:
        sdoc = harness_yaml.load_file(sy) or {}
    except Exception as e:
        bad.append(f"{rel}: state.yaml does not parse, so INV-15/16 cannot be "
                   f"checked for this run: {e}")
        continue
    if not isinstance(sdoc, dict):
        bad.append(f"{rel}: state.yaml is not a YAML mapping.")
        continue
    complete = str(sdoc.get("status", "")).strip() == "complete"

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
        elif _vd_mod is None:
            bad.append(f"INV-15 could not run: {os.path.relpath(vd, root)} "
                       f"{'is missing' if not os.path.isfile(vd) else 'will not import (' + str(_vd_import_err) + ')'}. "
                       f"Digest files are UNCHECKED — likely a partial deploy.")
        else:
            try:
                _errs = _vd_mod.validate("lead", open(dg, encoding="utf-8", errors="replace").read())
            except Exception as _e:
                _errs = [f"validate() raised: {_e}"]
            if _errs:
                bad.append(f"{os.path.relpath(dg, H)}: does not satisfy the lead digest "
                           f"contract — a successor reads this file, not the transcript "
                           f"(DEC-156). Run bin/validate-digest.py lead on it for reasons.")

# --- INV-19 (DEC-162): no glossary means the domain's ubiquitous language lives
# nowhere — "create lazily" fired zero times across three shipped features while
# enums and status vocabularies were being pinned. Warn-level: flows still run, but
# pm's next plan pass owes the file. The map precondition went with the map tier.
if not os.path.isfile(os.path.join(H, "glossary.md")):
    warn.append("no .harness/glossary.md — the domain's ubiquitous language is unrecorded "
                "(DEC-162). pm authors it, seeded from shipped features' pinned vocabulary.")

# --- INV-21 (D-05): a mirrored feature whose task issues are recorded but whose
# container (parent) never was — `ship`/`abandon` cannot close it and `open` will not
# re-derive it (the mirror is write-only, DEC-138). Warn, not violation (D-05): the
# GitHub Issues sync is never a gate, and a re-run of `open` fixes it. Vacuous
# when github.sync is off — the check costs nothing then.
if cj and (cj.get("github") or {}).get("sync"):
    for fy in glob.glob(os.path.join(H, "*", "features", "*", "feature.json")):
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
            bad.append(f"{fpath(feat, 'feature.json')} does not parse, so INV-21 cannot be "
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

# --- INV-24 (DEC-203): a feature that records factory state must name a repository the
# fleet declares, and no two features may claim one issue. The factory writes exactly one
# harness file — a feature's own `factory` block — so that block is the only place the
# harness can disagree with the board about what is in flight.
# The parent is counted alongside the task issues, not separately: gh-sync.py's `open`
# ALSO adopts or creates a container for the same feature in the same repository, so a
# container published beside one the factory created is D-12's collision, and comparing
# parents and issues in one list is the only place in this increment it becomes visible.
# A feature.json with no `factory` block contributes nothing and is not a violation.
_fac_pairs = {}
for fy in glob.glob(os.path.join(H, "*", "features", "*", "feature.json")):
    feat = os.path.basename(os.path.dirname(fy))
    try:
        fdoc = harness_yaml.load_file(fy) or {}
    except harness_yaml.YamlParseError:
        continue  # the parse failure is already a violation elsewhere; do not double-report
    fac = fdoc.get("factory")
    if not isinstance(fac, dict):
        continue
    fleet_p = os.path.join(H, "factory", "fleet.yaml")
    if not os.path.isfile(fleet_p):
        bad.append(f"INV-24 {feat}: records factory state but {os.path.relpath(fleet_p, root)} "
                   f"is absent — no fleet declares the repository it claims work in. "
                   f"Write the fleet declaration, or clear the feature's factory block.")
        continue
    try:
        fleet = harness_yaml.load_file(fleet_p) or {}
    except harness_yaml.YamlParseError as _e:
        bad.append(f"INV-24 {feat}: records factory state but the fleet file does not parse: "
                   f"{_e} — fix .harness/factory/fleet.yaml before any factory run.")
        continue
    # TYPES ARE VALIDATED, NOT ASSUMED (panel2 C1). Both halves of this used to read
    # straight off the YAML: a `repos:` entry with no `name` put None in the allow-list,
    # so `factory.repo: null` matched it and passed BOTH checks silently — a fail-open
    # inside an invariant checker. The mirror defect pointed the other way: an issue
    # number of null stringified to "None", so two unrelated features both keyed
    # (repo, "None") and were reported as colliding when nothing collided.
    names = [r["name"] for r in (fleet.get("repos") or [])
             if isinstance(r, dict) and isinstance(r.get("name"), str) and r["name"]]
    repo = fac.get("repo")
    if not isinstance(repo, str) or not repo:
        bad.append(f"INV-24 {feat}: factory.repo is {repo!r}, not a repository name — "
                   f"set it to an owner/name string the fleet declares, or remove the "
                   f"factory block if this feature claims no work.")
        continue
    if repo not in names:
        bad.append(f"INV-24 {feat}: records factory repo {repo!r}, which the fleet does not "
                   f"declare — fleet names: {', '.join(names) or '(none)'}. Add it to "
                   f".harness/factory/fleet.yaml, or correct the feature's factory.repo.")
        continue
    # Each number carries WHERE IT CAME FROM. Re-deriving the label later from
    # `n == fac.get("parent")` renders the duplicate message as "(parent and parent)" in
    # the exact container-equals-task case this check exists for, because both sides of
    # the comparison are then true.
    nums = []
    issues = fac.get("issues")
    if isinstance(issues, dict):
        nums.extend((v, f"task {k}") for k, v in issues.items())
    elif isinstance(issues, list):
        nums.extend((v, "a task") for v in issues)
    elif issues is not None:
        # The CONTAINER type was assumed while its contents were validated: `issues: 42`
        # left nums empty, so no collision check ran and nothing was reported at all.
        bad.append(f"INV-24 {feat}: factory.issues is {issues!r}, which is neither a "
                   f"T-NN-to-number mapping nor a list of numbers — no issue in this "
                   f"block can be checked for collision. Re-run `factory publish` to "
                   f"rewrite it, or correct it by hand.")
    if fac.get("parent") is not None:
        nums.append((fac.get("parent"), "the parent"))
    # WITHIN a feature as well as across features (panel2 C2). The comparison used to be
    # `!= feat`, so a feature whose own parent equalled one of its own task issues never
    # fired — which is exactly D-12's container collision, in the one shape this check
    # was written to make visible.
    _seen_here = {}
    for n, _src in nums:
        # A DIGIT STRING IS A NUMBER HERE. INV-21 thirty lines above accepts `parent: "40"`
        # deliberately — gh-sync.py's reader was widened to it because bare-digits-only
        # read a quoted number as absent. Rejecting the same shape here would make one
        # legal feature.json pass one invariant and hard-block on its twin (D-03).
        if isinstance(n, bool) or not (isinstance(n, int) or str(n).strip().isdigit()):
            bad.append(f"INV-24 {feat}: records issue number {n!r} for {repo}, which is not "
                       f"an integer — re-run `factory publish` to rewrite the block, or "
                       f"correct it by hand.")
            continue
        n = int(n)
        key = (repo, n)
        if key in _seen_here:
            bad.append(f"INV-24 {feat}: records {repo} issue {n} twice within its own factory "
                       f"block ({_seen_here[key]} and {_src}) — a container that is also a "
                       f"task issue is D-12's collision. "
                       f"Re-run `factory publish` after correcting the block.")
            continue
        _seen_here[key] = _src
        if key in _fac_pairs and _fac_pairs[key] != feat:
            bad.append(f"INV-24: {_fac_pairs[key]} and {feat} both record {repo} issue {n} — "
                       f"two features claiming one issue means the board and the harness "
                       f"disagree about what is in flight. Decide which feature owns it and "
                       f"clear the other's factory block.")
        else:
            _fac_pairs[key] = feat

# --- INV-28 (FEAT-26 T-05, REQ-04): a feature that shipped but whose pull request
# number was never recorded. WARN, not violation: the mirror is never a gate (DEC-138),
# and the remedy is one command that can be run at any time.
#
# THE FAILURE THIS MAKES VISIBLE IS A HABIT DECAYING, NOT A BUG. `feature.json`'s `pr`
# was filled by hand for thirteen features and then the hand stopped; five ran null before
# anyone noticed (#492). Nothing checked, so nothing complained.
#
# ONE LINE PER FEATURE, never an aggregate count. A per-feature check that reports a
# single total cannot tell the operator WHICH feature to run the remedy on, which makes
# the report unactionable at exactly the moment it matters.
#
# GATED ON github.sync, like INV-21 above: a repository with no mirror has no pull
# requests to record, and the remedy needs a working `gh`.
#
# THE TERMINAL MARKER IS TERMINAL AND IS SILENT HERE, deliberately. It asserts that no seam was
# crossed and nothing shipped, so there is no pull request to have missed. Only the `done`
# station is checked, read from plan.yaml (FEAT-41 T-07) — the feature.json read below stays,
# because this invariant is ABOUT that document's `pr` key.
if cj and (cj.get("github") or {}).get("sync"):
    for fy in glob.glob(os.path.join(H, "*", "features", "*", "feature.json")):
        feat = os.path.basename(os.path.dirname(fy))
        try:
            pdoc = harness_yaml.load_file(fy) or {}
        except Exception as e:
            bad.append(f"{fpath(feat, 'feature.json')} does not parse, so INV-28 cannot be "
                       f"checked for it: {e}")
            continue
        if not isinstance(pdoc, dict):
            continue
        if station_of(os.path.dirname(fy)) != "done":
            continue
        _pr = pdoc.get("pr")
        # `isinstance(True, int)` is True in Python, so the bool exclusion is load-bearing:
        # `pr: true` is not a pull request number and must not read as one.
        if isinstance(_pr, int) and not isinstance(_pr, bool):
            continue
        warn.append(f"INV-28: {feat} is Done but its pull request number was never "
                    f"recorded — the linkage from the feature to the change that shipped "
                    f"it is missing. Record it with `gh-sync.py record-pr "
                    f"{os.path.relpath(os.path.dirname(fy), root)}`.")

# --- INV-25 (issue #103): the environment itself must not contain an out-of-place
# worktree. The write guards now REFUSE writes into such a tree and refuse a session
# rooted in one, so an environment holding one is broken rather than merely unusual —
# which is why every branch below goes to `bad` and not to `warn`. A warning is the same
# silence in a quieter font.
#
# THE ONE PLACE A GIT SUBPROCESS IS ACCEPTABLE. The cost objection that kept this out of
# both hooks was that they run on EVERY governed write; check-state runs once per
# session. If git is absent or the command fails, record nothing: this invariant must
# never turn an unrelated environment into a red gate.
# THE IMPORT IS A VIOLATION WHEN IT FAILS, NOT A SILENT SKIP. Found by the review panel:
# this absorbed the ImportError into `_wt_seg = None`, `if _wt_seg:` then skipped every
# INV-25 branch, and a session holding a pre-existing out-of-place worktree printed
# "all state invariants hold" and exited 0. That is the fourth import route — the three
# in the two write guards fail closed, this one did not.
#
# It is a VIOLATION rather than a note because the module ships with the repository: it
# being unimportable is a defect in the tree, never a property of the environment. That
# is the opposite of the git-absent case below, which correctly records nothing.
try:
    import harness_boundary as _hb
    _wt_seg = _hb.WORKTREES_SEGMENT
except Exception as _hbe:
    _wt_seg = None
    bad.append("INV-25 CANNOT RUN: harness_boundary.py did not import (%s: %s), so a "
               "pre-existing out-of-place worktree would go unreported. The module ships "
               "with this repository — restore "
               ".agents/skills/harness/bin/harness_boundary.py."
               % (type(_hbe).__name__, _hbe))

if _wt_seg:
    try:
        _wtp = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root,
                              capture_output=True, text=True, timeout=10)
        _wt_out = _wtp.stdout if _wtp.returncode == 0 else None
    except Exception:
        _wt_out = None

    if _wt_out:
        # Porcelain records are blank-line separated; `worktree <path>` opens each one and
        # `prunable` appears on its own, with no --verbose flag needed.
        _entries = []
        for _rec in _wt_out.split("\n\n"):
            _path, _prunable = None, False
            for _line in _rec.splitlines():
                if _line.startswith("worktree "):
                    _path = _line[len("worktree "):].strip()
                elif _line.strip() == "prunable" or _line.startswith("prunable "):
                    _prunable = True
            if _path:
                _entries.append((_path, _prunable))

        if _entries:
            # THE BASE IS DERIVED ONCE, FROM THE MAIN CHECKOUT, AND USED FOR BOTH THE
            # COMPARISON AND THE MESSAGE. The first porcelain entry is always the main
            # checkout, even when the command runs from inside a linked worktree, and a
            # repository with no linked worktrees returns itself — so the derivation is
            # total.
            #
            # NEVER <root>/.claude/worktrees/. `root` is CLAUDE_PROJECT_DIR or the cwd, so
            # in exactly the session this invariant exists to catch — one whose root IS an
            # out-of-place worktree — that base would mark every LEGITIMATE worktree under
            # the main checkout as out of place and hand it destructive removal guidance.
            _main = os.path.realpath(_entries[0][0])
            _legal_home = os.path.realpath(os.path.join(_main, _wt_seg))
            _real_root = os.path.realpath(root)

            def _inside_legal(p):
                try:
                    return os.path.commonpath([p, _legal_home]) == _legal_home
                except ValueError:      # different drives / unrelated roots
                    return False

            # The first entry plays two SEPARATE parts and they must not be fused: it is
            # skipped as the main checkout, and it supplied the base above.
            for _wpath, _prunable in _entries[1:]:
                _rp = os.path.realpath(_wpath)
                if _inside_legal(_rp):
                    continue
                _where = (f"INV-25: {_wpath} is a git worktree outside {_legal_home}{os.sep}, "
                          f"where worktrees belong. A worktree elsewhere silently disables "
                          f"the harness machinery for every session opened in it.")
                if _rp == _real_root:
                    # THIS BRANCH TESTS AGAINST THE SESSION ROOT, not against the legitimate
                    # location above. They answer different questions — am I standing in
                    # this tree, versus does this tree belong where it is — and they stay
                    # two comparisons.
                    #
                    # NO REMOVAL GUIDANCE HERE. `git worktree remove` exits 0 when run from
                    # inside the tree it removes, so telling this session to remove this
                    # entry is telling it, at session entry, to delete the ground it is
                    # standing on.
                    bad.append(_where + " This session is rooted in it: start the session "
                                        "from the main checkout, or from a checkout under "
                                        "that location, instead.")
                elif _prunable:
                    # A prunable entry is a stale administrative record whose tree is
                    # already gone from disk, so it can never be a live cwd.
                    bad.append(_where + " The entry is stale — clear it with "
                                        "`git worktree prune`.")
                else:
                    # The session is not standing in it, so removal guidance is correct
                    # here and it STAYS. Deleting it everywhere would be the opposite
                    # defect.
                    bad.append(_where + f" Remove it with `git worktree remove {_wpath}`.")

# --- INV-29 (FEAT-34 T-06, REQ-01..REQ-06): a worktree must not survive its feature
# reaching a terminal state. INV-25's SIBLING, deliberately placed next to it: INV-25 asks
# whether a worktree belongs where it is, INV-29 asks whether it should still exist at all.
# Two different questions, so INV-25 above is untouched — the brief lists its enumeration
# under "already built — do not strike, do not rebuild".
#
# THE ENUMERATION IS NOT REPEATED HERE. `git worktree list` is run by worktree_terminal, the
# single shared predicate this gate and post-merge-sweep.sh both cross (D-02), so the gate and
# the hook can never disagree about what is eligible. A second copy of the walk in this file
# is exactly what D-02 exists to prevent.
#
# classify_all, NEVER classify (D-10). classify covers ONE repository — it runs one
# `git worktree list` with cwd=root, and feature-worktree.py joins WORKTREES_SEGMENT only to a
# resolved owner_root, so a served repository's worktrees live inside a DIFFERENT git
# repository that a list in this checkout can never report. An INV-29 built on classify would
# satisfy every other criterion and fail SC-04, which grades an INV-29 line for a SECOND
# repository produced by ONE run of this script.
#
# THE IMPORT FAILING IS ITSELF A VIOLATION, exactly as INV-25 at :1109 and INV-26 at :1203.
# The module ships with this repository, so being unimportable is a defect in the tree and
# never a property of the environment.
try:
    import worktree_terminal as _wt29
except Exception as _wt29e:
    _wt29 = None
    bad.append("INV-29 CANNOT RUN: worktree_terminal.py did not import (%s: %s), so a "
               "worktree surviving its feature's terminal state would go unreported. The "
               "module ships with this repository — restore "
               ".agents/skills/harness/bin/worktree_terminal.py."
               % (type(_wt29e).__name__, _wt29e))

if _wt29 is not None:
    # The fleet path is read as a CONSTANT, not re-derived. It is one of the two things that
    # tells a repository-level record apart from a worktree record — see the discriminator
    # below — and reading it here duplicates none of classify_all's resolution logic.
    try:
        import factory_config as _fc29
        _fleet_path29 = os.path.realpath(_fc29.FLEET_PATH)
    except Exception:
        _fleet_path29 = None

    # A raise here is caught rather than allowed to abort the interpreter. classify_all
    # already handles the three failure shapes D-10 specifies; an unexpected exception is a
    # defect, and letting it propagate would take EVERY other invariant's findings down with
    # it — the gate would print a traceback and report nothing at all.
    try:
        _recs29 = _wt29.classify_all(root)
    except Exception as _ce29:
        _recs29 = []
        bad.append("INV-29 CANNOT RUN: worktree_terminal.classify_all raised (%s: %s), so a "
                   "worktree surviving its feature's terminal state would go unreported."
                   % (type(_ce29).__name__, _ce29))

    _real_root29 = os.path.realpath(root)

    def _root_is_inside29(worktree_path):
        """Is this session standing inside the worktree the record describes?"""
        try:
            return os.path.commonpath([_real_root29, os.path.realpath(worktree_path)]) == \
                   os.path.realpath(worktree_path)
        except ValueError:      # different drives / unrelated roots
            return False

    for _r29 in _recs29:
        if _r29["klass"] == "exempt_absent":
            # The feature directory is genuinely absent from the default branch. Nothing to
            # report: that is the abandoned-flow case, and it is silence by design.
            continue

        # THE DISCRIMINATOR KEYS ON MORE THAN feature_id, AND IT HAS TO. A worktree whose path
        # is not under WORKTREES_SEGMENT emits feature_id None / repo None / unresolved
        # (worktree_terminal.py:202-206) — identical on class AND on feature_id to the
        # fleet-load record (:303-306). Keying on feature_id alone would classify a REAL
        # worktree as a repository-level failure and withhold the removal command from it.
        # What separates them: a repository-level record either names a declared repository
        # (repo is set) or IS the fleet file itself.
        _repo_level29 = (
            _r29["feature_id"] is None
            and (_r29["repo"] is not None
                 or (_fleet_path29 is not None
                     and os.path.realpath(_r29["path"]) == _fleet_path29))
        )

        if _repo_level29:
            # D-10's repository-level shape. BLOCKING for D-10's reason — the enumeration
            # failed there, so a terminal worktree could be standing and unreported.
            #
            # NO REMOVAL COMMAND, EVER, ON THIS BRANCH. The path is a repository root or the
            # fleet declaration, not a worktree. A removal command pointed at a repository
            # root would be actively dangerous, and there is nothing there to remove.
            _what29 = ("the fleet declaration"
                       if _fleet_path29 is not None
                       and os.path.realpath(_r29["path"]) == _fleet_path29
                       else "repository %s" % _r29["repo"])
            bad.append("INV-29: cross-repository enumeration failed at %s (%s) — %s. A "
                       "worktree surviving its feature's terminal state could be standing "
                       "there and unreported. No removal command is given: this path is not "
                       "a worktree."
                       % (_r29["path"], _what29, _r29["reason"]))
            continue

        # From here every record describes an actual worktree.
        if _r29["klass"] == "terminal":
            _head29 = ("INV-29: %s is a standing worktree whose feature %s reached a terminal "
                       "state on the default branch. Act 3 is not optional — the checkout is "
                       "removed once the work has landed."
                       % (_r29["path"], _r29["feature_id"]))
        else:
            # unresolved, at the worktree level. THE FAILED LOOKUP IS NOT AN EXEMPTION, and
            # the message says so outright: a reader who mistook this for the abandoned-flow
            # case would treat the loudest branch as the quietest one.
            _head29 = ("INV-29: %s is a standing worktree whose terminal status could not be "
                       "determined — %s. A lookup that FAILED is not an exemption; the "
                       "worktree is reported rather than passed over."
                       % (_r29["path"], _r29["reason"]))

        # THE DIRTY CLAUSE IS ITS OWN SENTENCE, not folded into the command line. SC-03 grades
        # the two claims one at a time: that the tree is dirty, and that remove will decline.
        if _r29["dirty"]:
            _head29 += (" The tree is dirty: `remove` will DECLINE until those changes are "
                        "committed, landed or discarded.")

        if _root_is_inside29(_r29["path"]):
            # INV-25's precedent at :1173, for the same mechanical reason: `git worktree
            # remove` exits 0 from inside the tree it deletes, so handing this session that
            # command is telling it to delete the ground it is standing on. The finding still
            # prints; only the guidance is withheld.
            bad.append(_head29 + " This session is rooted in it, so no removal command is "
                                 "given here: run it from the main checkout instead.")
        elif _r29["repo"] is not None and _r29["feature_id"] is not None:
            # THE COMMAND CARRIES THIS WORKTREE'S OWN IDENTITY, composed from this record's
            # own repo segment and id — never a bare command, and never another worktree's.
            # feature-worktree.py remove is named rather than `git worktree remove` because it
            # declines a dirty tree at exit 4 and an unlanded artifact directory at exit 5,
            # and it has no force flag. Raw git would take --force.
            # THE --id IS THE WORKTREE DIRECTORY'S OWN NAME, never the record's feature_id.
            # They differ for a SHORT-NAMED worktree: feature_id is the LANDED directory on the
            # default branch, which is the full name, while `remove` matches the checkout. Printing
            # feature_id there gives a command that exits "not a linked worktree" for a directory
            # plainly sitting in front of the reader. post-merge-sweep.sh:150 already derives it
            # this way; this is the same derivation, not a second rule.
            bad.append(_head29 + " Remove it with `python3 "
                                 ".agents/skills/harness/bin/feature-worktree.py remove "
                                 "--repo %s --id %s` (path: %s)."
                                 % (_r29["repo"],
                                    os.path.basename(_r29["path"].rstrip(os.sep)),
                                    _r29["path"]))
        else:
            # An out-of-segment worktree: there is no repo/id pair to build the command from,
            # because the path never resolved to one. INV-25 above reports the same tree with
            # its own removal guidance, so nothing is lost by withholding it here.
            bad.append(_head29 + " Its path did not resolve to a repository and id, so no "
                                 "removal command can be composed for it.")

# --- INV-26 BEGINS — the marker T-05's verify slices on. Without it the slice is EMPTY and
# every literal-absence grep below trivially passes, which is the vacuous-grep failure this
# feature exists to remove. The verify's positive control requires derive_station INSIDE the
# slice for exactly that reason.
# --- INV-26 (issue #277): the board must agree with the plan on disk.
#
# THIS INVARIANT CARRIES THE GUARANTEE. A failed station write is loud only on stderr, and
# the operator accepted that stderr inside a subagent run is not something they read — so a
# board that drifted is caught HERE or it is not caught at all. Every finding goes to `bad`:
# the operator's view of the factory being wrong is the condition the ticket opens with, and
# a warning is the same silence in a quieter font.
#
# THE IMPORT IS A VIOLATION WHEN IT FAILS — INV-25's precedent, and for its reason: gh_board
# ships with the repository, so being unimportable is a defect in the tree, never a property
# of the environment. Everything else below records NOTHING, because an offline or
# unconfigured environment must never become a red gate.
try:
    import gh_board as _gb
    # factory_config comes with it because load_board now RAISES FleetError rather than
    # returning None on an unusable declaration (T-04), and a caller that wants to catch it
    # must import the module that defines it. One try, not two: both ship with this
    # repository, so either being unimportable is the same defect in the tree.
    import factory_config as _fc26
except Exception as _gbe:
    _gb = None
    _fc26 = None
    bad.append("INV-26 CANNOT RUN: gh_board.py did not import (%s: %s), so a board that "
               "disagrees with the plan would go unreported. The module ships with this "
               "repository — restore .agents/skills/harness/bin/gh_board.py."
               % (type(_gbe).__name__, _gbe))

# THE BINARY IS OVERRIDABLE OR THIS CANNOT BE TESTED. FACTORY_GH is the variable factory_gh
# already honours, so ONE fake serves both the module and this invariant. A third variable
# name would be a third thing to get wrong.
_gh_bin = os.environ.get("FACTORY_GH") or "gh"

_inv26_board = None
if _gb is not None:
    _g26 = cj.get("github") if isinstance(cj, dict) else None
    _repo26 = (_g26 or {}).get("repo")
    if isinstance(_g26, dict) and _g26.get("sync") is True and _repo26:
        # AN UNUSABLE BOARD IS A VIOLATION, NOT SILENCE — the exact inverse of the behaviour
        # this task removes. load_board used to return None for both "no board declared" and
        # "board declared and broken", so a typo made INV-26 vacuous and left the gate GREEN.
        # It now raises for everything except an explicit null, and the gate must COMPLETE
        # and report rather than abort: one entry, then the rest of INV-26 is skipped.
        try:
            _inv26_board = _gb.load_board(root)
        except Exception as _be26:
            _inv26_board = None
            if _fc26 is not None and isinstance(_be26, _fc26.FleetError):
                bad.append("INV-26 CANNOT RUN: %s — the board declaration is unusable, so a "
                           "card that disagrees with the plan would go unreported." % _be26)
            else:
                raise

if _inv26_board:
    # gh absent or unauthenticated is an environmental precondition (DEC-138's verbatim
    # clause), so it records nothing. Same posture as INV-25's git-absent branch.
    try:
        _auth = subprocess.run([_gh_bin, "auth", "status"],
                               capture_output=True, text=True, timeout=15)
        _gh_ok = _auth.returncode == 0
    except Exception:
        _gh_ok = False

    _stations = None
    if _gh_ok:
        # A FAILED OR TRUNCATED BOARD READ RECORDS NOTHING. board_stations already refuses a
        # truncated page by raising, which is what keeps a partial read from being reported
        # as an empty column — but the remedy here is silence, not a red gate, because the
        # network is not the tree.
        try:
            os.environ["FACTORY_GH"] = _gh_bin
            _stations = _gb.board_stations(_inv26_board, _repo26)
        except Exception:
            _stations = None

    if _stations is not None:
        # THE PLACEMENT RULE IS NOT HERE ANY MORE (FEAT-41 T-06, D-11). The two lookup tables
        # that stood here are DELETED, not lowercased: the rule they encoded — which card
        # belongs at which station, and when — now lives in gh_board.project and nowhere else,
        # so this file holds the COMPARE side only. It asks project where a card belongs and
        # reports the cards that disagree.
        #
        # What went with them: a status-to-COLUMN mapping, which was the last thing in this file
        # translating between two vocabularies, and a three-key lookup whose ready-to-backlog
        # exception D-11 removed outright. plan.yaml and the board now carry the same word with
        # the same meaning and nothing is derived between them.
        #
        # Their names are deliberately not written here. This task's verify greps the whole file
        # for both identifiers and fails on a COMMENT as readily as on code — a dead name in
        # prose is still a reader's next false lead.

        for _fp in sorted(glob.glob(os.path.join(H, "*", "features", "*"))):
            _feat = os.path.basename(_fp)
            _pdoc = plan_docs.get(_feat)
            if not _pdoc:
                # No plan.yaml, or one that did not load. Other invariants own both — the
                # load failure is already a violation above, and restating it here would
                # report one defect twice.
                continue

            # THE FEATURE.JSON READ STAYS — this block reads `github.issues`, `github.parent`
            # and `factory.issues` off `_fj` further down. Only the STATION moved to plan.yaml.
            try:
                _fj = json.load(open(os.path.join(_fp, "feature.json"), encoding="utf-8"))
            except Exception:
                _fj = {}

            # THE TERMINAL EXEMPTION. `ship` writes the parent's card to the done station and
            # records the terminal station, while the plan-derived station would still say
            # review — so without this every shipped feature is a permanent false violation.
            #
            # THE CONDITION NOW KEYS ON plan.yaml's STATION (FEAT-41 T-07) rather than
            # feature.json's status, which is the only change here: one file records the station.
            if station_of(_fp) in ("done", TERMINAL_MARKER):
                continue

            _derived = _gb.derive_station(_pdoc)

            # A None derivation silences the PARENT claim ONLY. It used to `continue` here
            # and skip the whole feature, which took the per-task comparison with it — and
            # that comparison never needed the parent derivation, since project places each
            # task's card from that task's own status. The cost was exact: a plan with one task
            # `done` and
            # the rest `pending` derives None, so the mis-columned `done` card SC-05 names
            # went unreported. That is the ordinary window between two tasks, not a corner,
            # and every INV-26 fixture was single-task so the suite could not see it.
            # An absent status reads as the NOT-STARTED STATION (FEAT-41 T-04). The PLAN.md
            # corpus predates the field, so absence still has to mean something, and what it
            # means is `ready`.
            _statuses = [(_t.get("status") or "ready")
                         for _t in (_pdoc.get("tasks") or [])
                         if isinstance(_t, dict) and _t.get("id")]
            # THIS GUARD INVERTS UNDER THE RENAME IF IT IS COPIED LITERALLY (FEAT-41 T-04).
            # It read `not any(_s != "pending")` — true only when every task is unstarted. The
            # migration rewrote every such task to `ready`, so a literal rename would leave the
            # test comparing against a word no file carries: `_s != "pending"` is true for
            # EVERY task, `not any(...)` is false for every feature, and the skip would stop
            # firing everywhere at once. Written against the not-started station instead.
            if _derived is None and all(_s == "ready" for _s in _statuses):
                # Nothing has started. No card can be wrong yet, so no claim is right.
                continue

            _issues = ((_fj.get("github") or {}).get("issues") or {})

            # THE MIRROR-NEVER-RAN CLAUSE — the ticket's own third gap. A mirror that never
            # ran and one that ran cleanly are otherwise indistinguishable from outside.
            # INV-21 warns on a DIFFERENT shape (recorded issues, no parent); these stay
            # two findings and neither restates the other.
            if not _issues:
                # THE OTHER LANE (issue #349). A feature published by factory_decompose
                # records its issues under `factory.issues` and nothing under
                # `github.issues` — its cards live on the PRODUCT's board, which this
                # invariant does not read. Without this, the clause below orders the
                # operator to run `gh-sync.py open` on product work, mirroring it onto
                # harness's own board. Keys on RECORDED issues, not the block's presence:
                # a factory block with an empty map is still a feature nobody published.
                if ((_fj.get("factory") or {}).get("issues")):
                    continue
                _claim = (f"plan derives {_derived}" if _derived is not None
                          else "the plan has tasks under way")
                bad.append(f"INV-26 {_feat}: tasks are in flight or finished ({_claim}"
                           f") but feature.json records no mirrored issues, so the "
                           f"board cannot be telling the truth about this feature. The mirror "
                           f"never ran — run `gh-sync.py open` for it.")
                continue

            _tstat = {}
            for _t in (_pdoc.get("tasks") or []):
                if isinstance(_t, dict) and _t.get("id"):
                    _tstat[_t["id"]] = _t.get("status") or "ready"

            # ONE CALL, INSIDE THE TRY THAT ALREADY TREATS A gh_board FAILURE AS A VIOLATION.
            # `rec` is the shape gh-sync.load_recorded returns, built from the feature.json this
            # loop already has. source_issues is empty because this invariant compares TASK
            # cards and the parent, and a source issue's card is the parent's station — already
            # covered by the parent claim above.
            try:
                _projected = _gb.project(_pdoc, {"issues": _issues,
                                                 "parent": (_fj.get("github") or {}).get("parent"),
                                                 "source_issues": []})
            except Exception as _pe26:
                # A VOCABULARY MISS IS A VIOLATION, NOT A SKIP. project raises FleetError
                # naming the task and the value, which is the defect this feature exists to
                # end — reporting it as silence would be the fail-open D-11 removes.
                bad.append(f"INV-26 {_feat}: the plan carries a station the vocabulary does not "
                           f"contain, so no card can be checked against it — {_pe26}")
                continue

            for _tid in sorted(_issues):
                _num = _issues[_tid]
                # THE FAIL-OPEN IS DELETED (D-11). This read `if _want is None: continue`, so a
                # recorded sub-issue that the placement rule did not place went unexamined. A
                # card project declines to place is now a violation naming the feature, the task
                # and the station the plan carries.
                _want = _projected.get(_num)
                if _want is None:
                    bad.append(f"INV-26 {_feat} {_tid} (issue #{_num}): the plan carries station "
                               f"{_tstat.get(_tid, 'ready')!r} and no card placement follows from "
                               f"it, so the board cannot be checked against the plan.")
                    continue
                # D-24, on the operator's ruling 4 of 2026-08-23 (FEAT-33 T-22). Under
                # D-23 a done task's sub-issue is deliberately left OPEN so it can hold its
                # column through the whole Review phase.
                #
                # THE ORIGINAL JUSTIFICATION HERE WAS FALSE and is corrected rather than
                # deleted. It argued that GitHub's native `Item closed` workflow lands a
                # closed issue's card in the done column by itself, and cited board 3 never
                # having held a card at Review as the measurement. Measured 2026-08-25:
                # FEAT-34's thirteen sub-issues #818 through #830 are ALL CLOSED and ALL sit
                # at Review. A closed issue's card stays where it is.
                #
                # What is actually true, and what this widening rests on now: `ship` — not a
                # close — is what writes the done station (DEC-203). So while a feature's own
                # station is review, a done task's card may legitimately read the done, review
                # OR building station: done if ship has already run, and review or building
                # because those are what the review phase itself leaves behind.
                #
                # BOUNDED ON THAT STATION ON PURPOSE, unchanged in force: an unconditional
                # widening would silence the mis-columned done card the invariant was
                # extended to catch. The station is read from plan.yaml now (FEAT-41 T-07),
                # the same file `_pdoc` came from.
                _accept = {_want}
                if _tstat.get(_tid) == "done" and station_of(_fp) == "review":
                    _accept |= {"review", "building"}
                _wanttxt = (_want if len(_accept) == 1
                            else ", ".join(sorted(_accept)[:-1]) + " or " + sorted(_accept)[-1])
                _found, _reason = _gb.read_station(_stations, _num)
                if _reason:
                    # CANNOT VERIFY, NOT CLEAN. A lookup that misses leaves both sides of
                    # the comparison empty and every record then compares equal — which is
                    # precisely the silence this invariant exists to break.
                    bad.append(f"INV-26 CANNOT VERIFY {_feat} {_tid} (issue #{_num}): "
                               f"{_reason}. The plan says {_tstat.get(_tid, 'pending')}, so "
                               f"the card should read {_wanttxt}.")
                elif _found not in _accept:
                    bad.append(f"INV-26 {_feat} {_tid} (issue #{_num}): plan says "
                               f"{_tstat.get(_tid, 'pending')}, so the card should read "
                               f"{_wanttxt} — the board reads {_found}.")

            # THE PARENT. A derived station with no recorded parent is INV-21's finding,
            # not this one.
            # `_derived is None` reaches here now, and the parent is the ONE comparison it
            # must still silence — there is no station to expect, so any read compares equal
            # to nothing and would report a false violation.
            _parent = (_fj.get("github") or {}).get("parent")
            if isinstance(_parent, int) and _derived is not None:
                _pfound, _preason = _gb.read_station(_stations, _parent)
                if _preason:
                    bad.append(f"INV-26 CANNOT VERIFY {_feat} parent (issue #{_parent}): "
                               f"{_preason}. The plan derives {_derived}.")
                elif _pfound != _derived:
                    bad.append(f"INV-26 {_feat} parent (issue #{_parent}): the plan derives "
                               f"{_derived} — the board reads {_pfound}.")
# --- INV-30 (FEAT-34 T-08, REQ-12): a feature recorded `Done` whose milestone is still OPEN.
#
# IT KEYS ON THE MILESTONE, NEVER ON THE STATUS AGREEING WITH ITSELF. `status: Done` has more
# than one path that can write it — the 2026-08-24 repair wrote ten by hand — so a Done status
# corroborating a Done status proves nothing. The milestone has exactly ONE writer,
# `gh-sync.py`'s `cmd_ship`, which PATCHes it closed unconditionally once entered. So an OPEN
# milestone on a Done feature is proof that `ship` never ran.
#
# THE OFFLINE POSTURE IS INV-26's, NOT A NEW ONE. The IMPORT failing is a violation, because
# the module ships with this repository. Everything else — `gh` absent, unauthenticated, the
# network unreachable, a milestone that 404s — records NOTHING. `check-state.sh` runs before
# every commit, and an offline environment must never become a red gate.
#
# ONE `gh` CALL, NOT ONE PER FEATURE. 24 features carry a recorded milestone at 9165162; a
# request each would make the pre-commit gate pay 24 round trips for a check that one paginated
# list answers. The whole milestone list is fetched once and matched by number in memory.
try:
    import gh_board as _gb30
    _inv30_import_ok = True
except Exception as _gbe30:
    _inv30_import_ok = False
    bad.append("INV-30 CANNOT RUN: gh_board.py did not import (%s: %s), so a feature recorded "
               "Done whose milestone is still open would go unreported. The module ships with "
               "this repository — restore .agents/skills/harness/bin/gh_board.py."
               % (type(_gbe30).__name__, _gbe30))

_g30 = cj.get("github") if isinstance(cj, dict) else None
_repo30 = (_g30 or {}).get("repo")

if _inv30_import_ok and (_g30 or {}).get("sync") and _repo30:
    # THE CANDIDATE SET IS BUILT FROM DISK FIRST, so the network is touched only if there is
    # something to ask about. A tree with no Done-and-milestoned feature makes no gh call at all.
    _cand30 = []
    for _fy30 in sorted(glob.glob(os.path.join(H, "*", "features", "*", "feature.json"))):
        _feat30 = os.path.basename(os.path.dirname(_fy30))
        try:
            _doc30 = harness_yaml.load_file(_fy30) or {}
        except Exception:
            # INV-28 above already reports an unparseable feature.json. Restating it here would
            # report one defect twice.
            continue
        if not isinstance(_doc30, dict):
            continue
        # The `done` station and nothing else, read from plan.yaml (FEAT-41 T-07). The terminal
        # marker is terminal and silent here for INV-28's reason: nothing shipped, so there is
        # no milestone that ship should have closed. The feature.json read above stays — this
        # invariant needs `github.milestone` off that document.
        if station_of(os.path.dirname(_fy30)) != "done":
            continue
        _ms30 = (_doc30.get("github") or {}).get("milestone")
        if _ms30 is None:
            # A Done feature with no recorded milestone is outside this invariant's reach, not a
            # finding. Eight features are in that state at 9165162 and none of them is a defect
            # INV-30 can speak to.
            continue
        try:
            _cand30.append((_feat30, int(_ms30)))
        except (TypeError, ValueError):
            continue

    if _cand30:
        # SAME RESOLUTION AS INV-26 at :1371 — FACTORY_GH first. A fixture that stubs
        # `gh` through that variable must reach this invariant too, or INV-30 would be
        # untestable offline while claiming an offline posture.
        _gh_bin30 = os.environ.get("FACTORY_GH") or "gh"
        _open30 = None
        try:
            _auth30 = subprocess.run([_gh_bin30, "auth", "status"],
                                     capture_output=True, text=True, timeout=15)
            _gh_ok30 = _auth30.returncode == 0
        except Exception:
            _gh_ok30 = False

        if _gh_ok30:
            # `--paginate` rather than a bare per_page: the list is small today and silently
            # truncating it later would make this invariant quietly stop firing on the oldest
            # features, which is the decay shape INV-28 was written to catch.
            try:
                _r30 = subprocess.run(
                    [_gh_bin30, "api", "--paginate",
                     "repos/%s/milestones?state=open&per_page=100" % _repo30,
                     "-q", ".[].number"],
                    capture_output=True, text=True, timeout=60)
                if _r30.returncode == 0:
                    _open30 = {int(x) for x in _r30.stdout.split() if x.strip().isdigit()}
            except Exception:
                _open30 = None

        # None means "we could not ask", which is NOT the same as "nothing is open" and must
        # never be treated as one. Silence here is the whole offline posture.
        if _open30 is not None:
            for _feat30, _num30 in _cand30:
                if _num30 not in _open30:
                    continue
                bad.append(
                    "INV-30 %s: status is Done but milestone #%d is still OPEN, so "
                    "`gh-sync.py ship` never ran for it. The status is not evidence — it has "
                    "several writers and the milestone has one. Close it with `python3 "
                    ".agents/skills/harness/bin/gh-sync.py ship %s`."
                    % (_feat30, _num30, fpath(_feat30)))

# --- INV-26 ENDS

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

# --- INV-27 (FEAT-20): every layout surface speaks one language. The detector is
# layout_migration.py; this block composes findings from its STRUCTURED RESULT and
# never re-parses its CLI text. A NOT APPLICABLE root (no control-plane marker —
# a product checkout, or a test fixture) appends nothing, and a clean result appends
# nothing. The verdict is computed by the module, which is a DEC-174 carve-out by
# content for exactly that reason.
#
# THE IMPORT IS A VIOLATION WHEN IT FAILS — INV-25's precedent, and for its reason:
# the module ships with the repository, so it being unimportable is a defect in the
# tree, never a property of the environment.
try:
    import layout_migration as _lmod
except Exception as _lme:
    _lmod = None
    bad.append("INV-27 CANNOT RUN: layout_migration.py did not import (%s: %s), so a "
               "half-migrated layout would go unreported. The module ships with this "
               "repository — restore .agents/skills/harness/bin/layout_migration.py."
               % (type(_lme).__name__, _lme))

if _lmod is not None:
    try:
        _lres = _lmod.scan(root)
    except Exception as _lse:
        _lres = None
        bad.append("INV-27 CANNOT RUN: the layout scan raised (%s: %s) — fix "
                   "layout_migration.py or its reader table before trusting this gate."
                   % (type(_lse).__name__, _lse))
    if _lres is not None and _lres.applicable:
        # Every entry ends with a remedy — house style; a finding an operator cannot
        # act on is a finding they will learn to skip. The form-set tag on each reader
        # path is load-bearing: [legacy] on a migrated tree means FINISH the reader,
        # [migrated] on a legacy tree means REVERT it, and the paths are identical
        # without the tag.
        _lrem = ("Finish or revert this surface inside one atomic commit; the form "
                 "rows are data in layout_migration.py.")
        # THE CAUSE TABLE IS CLOSED AND THE LOOKUP FAILS LOUD (code-review finding:
        # the earlier if/elif chain had no else, so a fifth cause value would have
        # appended nothing and this gate — the surface operators actually see —
        # would have passed clean while CI stayed red).
        # Wording and blame both come from the module — cause_text/blame_text are
        # the single owners (see layout_migration.blame, #379); this block adds only
        # the INV-27 framing and the remedy.
        for _sname in sorted(_lres.surfaces):
            _srep = _lres.surfaces[_sname]
            if _srep.verdict == "MIXED":
                _ev = "+".join(sorted(_srep.evidence)) if _srep.evidence else "none"
                bad.append(f"INV-27 {_sname}: layout is MIXED — evidence {_ev}; "
                           f"readers {_lmod.blame_text(_srep)}. {_lrem}")
            elif _srep.verdict == "CANNOT_VERIFY":
                _named = _lmod.blame_text(_srep)
                _suffix = f"; readers: {_named}" if _named else ""
                bad.append(f"INV-27 CANNOT VERIFY {_sname}: "
                           f"{_lmod.cause_text(_srep, root)}{_suffix}. {_lrem}")

# --- INV-31 (FEAT-40 T-08, REQ-02/REQ-09): this clone's merge hook is not installed.
#
# WHY IT EXISTS AT ALL. The setup step lives in `.claude/skills/harness-init/SKILL.md`, and an
# already-onboarded clone NEVER RE-RUNS IT. A doc step reaches a clone once; an invariant
# reaches every clone, every run. Measured at cc84b29 on this very checkout,
# `core.hooksPath` read `/Users/molchairuangutai/GitHub/harness/.git/hooks`, a directory
# holding fourteen files every one of which is a `.sample` — so `gh-sync.py ship` never ran at
# a merge, and NOTHING SAID SO. After this feature `ship` is the only thing that closes
# tickets and the post-merge sweep is the only thing that runs `ship`, so a clone without the
# hook silently stops closing tickets altogether.
#
# BOTH FINDINGS APPEND TO `bad`, NEVER `warn`, and that is a deliberate departure from INV-28,
# which warns on the stated ground that the mirror is never a gate. This is not a mirror fact.
# It is whether THIS MACHINE runs the hook that runs ship.
#
# SCOPE, decided rather than omitted: this invariant does NOT check whether a card is closed
# but away from the done station. `board_lifecycle.py`'s audit already reports exactly that as
# its STATION finding class, and a second detector for one fact is two rules that will drift.
# What was missing there was a RUNNER, not a detector, and that runner now sits inside `ship`,
# once per feature (DEC-203 item 8) — deliberately not here, where the audit's four network
# calls would fall on every run of the state checker.
_HOOKS_REL = os.path.join(".claude", "skills", "harness", "hooks")

try:
    _hp = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                         cwd=root, capture_output=True, text=True)
    _hp_ok = True
except Exception as _hpe:
    _hp_ok = False
    # CANNOT RUN IS A VIOLATION, NOT A PASS — the same posture INV-25, INV-26 and INV-29 take
    # for an import failure. An unreadable git config is not evidence the hook is installed.
    bad.append("INV-31 CANNOT RUN: git config could not be read (%s: %s), so an uninstalled "
               "merge hook would go unreported. Fix: make git runnable in this checkout."
               % (type(_hpe).__name__, _hpe))

if _hp_ok:
    _found_hp = _hp.stdout.strip() if _hp.returncode == 0 else ""
    _want_abs = os.path.realpath(os.path.join(root, _HOOKS_REL))
    # RESOLVED AND COMPARED AS REAL PATHS, so an ABSOLUTE value naming the same directory
    # passes and a RELATIVE one naming a different directory fails. Comparing the strings
    # would report a working clone as broken and vice versa.
    _found_abs = os.path.realpath(os.path.join(root, _found_hp)) if _found_hp else ""
    if _found_abs != _want_abs:
        _shown = "unset" if not _found_hp else '"%s"' % _found_hp
        bad.append("INV-31: core.hooksPath is %s, not %s — no harness hook runs on this "
                   "clone. Fix: git config core.hooksPath %s"
                   % (_shown, _HOOKS_REL, _HOOKS_REL))
    else:
        # A SECOND FINDING WITH A DIFFERENT SUBJECT, never a variable tail on the first. One
        # is a misconfigured clone; this one is a damaged checkout. They have different fixes,
        # so they are different lines.
        _pm = os.path.join(_want_abs, "post-merge")
        if not os.path.isfile(_pm):
            bad.append("INV-31: %s/post-merge is missing — the hook path resolves but the "
                       "merge sweep cannot run. Fix: restore it" % _HOOKS_REL)
        elif not os.access(_pm, os.X_OK):
            bad.append("INV-31: %s/post-merge is not executable (mode %o) — the hook path "
                       "resolves but the merge sweep cannot run. Fix: chmod +x it"
                       % (_HOOKS_REL, os.stat(_pm).st_mode & 0o777))

# INV-10 IS GONE, AND THE NUMBER IS RETIRED WITH IT. It ran check-docs.sh, the
# propagation checker, which no longer exists: the operator struck the whole
# stale-marker mechanism and replaced detection with deletion — a decision the tree
# flatly contradicts is struck from the record and removed from every gate, so
# nothing survives to contradict. Do NOT reuse "INV-10" for a new invariant; the
# number appears in shipped digests and reviews, and reusing it makes that history
# read as being about something it never was.
#
# What this costs, stated plainly so nobody rediscovers it as a surprise: nothing
# mechanical now checks that a doc statement a later decision falsified was actually
# removed. The replacement rule holds only while the striking really happens every
# time, and its enforcement is a human reading a diff.

for m in bad:  print(f"  VIOLATION  {m}")
for m in warn: print(f"  note       {m}")
if not bad and not warn:
    print("  all state invariants hold.")
sys.exit(1 if bad else 0)
PY
