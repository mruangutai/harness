#!/usr/bin/env python3
"""Mirror a feature to GitHub Issues — outbound but for one read, never a gate (DEC-138).

  gh-sync.py open  <feature-dir>          plan approved -> milestone + parent + one issue per T-NN
  gh-sync.py start-task <feature-dir> T-NN    task moved to building -> sub-issue's station
                                           -> Building, then the parent's derived station (FEAT-18)
  gh-sync.py abandon <feature-dir> --reason-file <path> [--yes]  feature abandoned ->
                                           WITHOUT --yes it prints every write it would make
                                           and makes none; WITH --yes it closes every sub-issue
                                           AND the parent not_planned, labels them abandoned,
                                           closes the milestone and posts the reason
  gh-sync.py ship  <feature-dir> [--body-file <path>] [--pr <n>]  shipped -> writes the
                                           board's done station on every recorded card
                                           (children first, skipping any card with an open
                                           child), closes the milestone, posts --body-file on
                                           any recorded parent if given, THEN records the pr
                                           (T-03, FEAT-26). It closes NO issue: GitHub's
                                           Auto-close issue workflow does that (DEC-203)
  gh-sync.py record-pr <feature-dir> [--pr <n>]  derive the pull request number from the
                                           recorded branch's exactly-one merged PR and
                                           record it, or record --pr directly (T-03,
                                           FEAT-26) — idempotent, never overwrites
  gh-sync.py status <feature-dir> <Status>  phase transition -> records feature.json's
                                         `status` FIRST, then performs exactly the
                                         station writes THAT event implies (Ready moves
                                         every recorded sub-issue; Review moves the
                                         parent AND every sub-issue; Plan/Done/Abandoned
                                         write no station) (T-13, D-16)

TRUTH DIRECTION IS THE POINT. PLAN.md is approval-gated and is the only source; this
script projects it outward. It reads GitHub state back exactly ONCE — `record-pr` asks
for the merged pull request on a recorded branch and writes the number into
feature.json's `pr` (FEAT-26, DEC-200). No read-back ever reaches an approval-gated
artifact: a wiki-editable UI feeding one is the DEC-19 bypass shape, and that stays
refused. DEC-138 am.7 refuses a discovery read for the PARENT number because the parent
has a local receipt and a second source would contradict it; the pull request number has
no local receipt, because the harness never opens the pull request.

NEVER A GATE, and since FEAT-18 that is a FOUR-WAY split, not two (D-02, and FEAT-24
adds the fourth). An ENVIRONMENTAL PRECONDITION — sync off, no repo pinned, gh missing,
gh unauthenticated, network down, or `github.board` declared as an EXPLICIT null —
prints one loud line and exits 0 for the WHOLE invocation, because a flow that fails on
its *mirror* has inverted its priorities (SPEC §12 precedent for branch/PR ops). An
explicit null board (FEAT-24 D-07) prints one plain line, station writes are not
attempted, and the issue lifecycle (open, abandon, ship) runs
unchanged — the whole invocation is never abandoned for it. An UNUSABLE board
declaration — `github.board` absent, present but not a mapping, or malformed in any
field `factory_config.validate_board` checks — is NOT an environmental precondition
(FEAT-24 T-04): it is a loud failure of the WHOLE invocation, one line on stderr and
exit 2, because a misconfiguration a human must fix is not the same state as a project
that has declared it has no board. A failure of a STATION WRITE while gh itself works —
an unknown project, a station name the board does not carry, a network blip mid-call —
prints one line to STDERR beginning `gh-sync: ERROR -`, naming the issue, the station
attempted and the underlying message, and the run CONTINUES to its remaining writes;
the exit status stays 0. Nothing on that path is ever re-attempted. An issue close
that fails stays on `gh()`, which SKIPs (exits 0) on the spot rather than continuing —
the parent's station write is ordered before the close specifically so that
termination can never swallow it (T-03 step 4). Exit 1 is reserved for caller errors
(bad args, missing files): those are bugs in the dispatch, not the environment, and
must be visible.

REPO IS PINNED, NEVER INFERRED. Every gh call passes --repo/-R from harness.json's
`github.repo`, recorded once at init under the user's eyes. Inferring from the cwd's
origin remote works right up until a fork or renamed remote publishes issues to the
wrong org silently — the one failure here that is both outward-facing and quiet.

LABELS DERIVE, MECHANICALLY (DEC-138 am.3): change_type config/scaffolding/infra/ci
-> `chore`; bugfix -> `bug`; anything else unlabeled. `harness` marks provenance on
every issue. No agent judgment at sync time.

IDEMPOTENT. `open` records issue numbers into feature.json (`github:` block) as it
creates; a re-run (resume after interruption — DEC-131 taught us flows die mid-step)
skips anything already recorded rather than duplicating.

Testable offline: GH_SYNC_GH overrides the gh binary (test-gh-sync.py points it at a
fake that logs calls and returns canned JSON).
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from gh_issues import (internal_id_args, attach_sub_issue_args, sub_issues_args,
                       detach_sub_issue_args)

import feature_json_write
import harness_merge
import factory_config
import factory_gh
import board_lifecycle
import gh_board
import gh_cost_log
import harness_yaml

GH = os.environ.get("GH_SYNC_GH", "gh")

CHORE_TYPES = {"config", "scaffolding", "infra", "ci"}

# T-13: the closed set `status` accepts, matching check-state.sh:494's STATUS_ORDER and
# feature-schema.json's own status enum. A value outside this set is a caller error (exit 2),
# not silently accepted with a lower-case spelling.
STATUS_VALUES = ("Backlog", "Plan", "Ready", "Building", "Review", "Done", "Abandoned")


def skip(msg):
    """Environmental no-go: one loud line, exit 0. The mirror never gates."""
    print(f"gh-sync: SKIP — {msg}")
    sys.exit(0)


def die(msg):
    """Caller error: the dispatch itself is wrong. Visible, exit 1."""
    print(f"gh-sync: ERROR — {msg}")
    sys.exit(1)


def refuse(msg):
    """T-13's `status` subcommand refusals: a value or precondition failed validation,
    distinct from `die`'s exit 1 (a malformed dispatch) and from `skip`'s exit 0 (an
    environmental precondition). Exit 2, one line, naming the offending value."""
    print(f"gh-sync: REFUSED — {msg}")
    sys.exit(2)


def post_body_path(path, flag):
    """Validate a --body-file-style path argument (DEC-138 am.6: the mirror never composes
    text — the path itself is passed to gh, never its contents). Every failure here is a
    caller error, never environmental: an empty or unreadable file would otherwise reach
    gh(), get rejected, and be reported as a SKIP that silently posts no reason at all."""
    if path is None:
        die(f"{flag} is required")
    if not os.path.isfile(path):
        die(f"{path} is not a file")
    if os.path.getsize(path) == 0:
        die(f"{path} is empty")
    try:
        open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        # UnicodeDecodeError is a ValueError, NOT an OSError, so a binary or
        # mis-encoded file escaped this handler and surfaced as a traceback instead
        # of a clean caller error (FEAT-03 B-1). It was ranked first in that
        # briefing on irreversibility, not severity: this path feeds `gh issue
        # comment`, and a wrong file posted to a tracker cannot be un-posted.
        die(f"{path} is unreadable ({e})")
    return path


def gh(args, capture=True):
    with gh_cost_log.measured(args) as _cost:
        r = subprocess.run([GH] + args, capture_output=True, text=True)
        _cost.returncode = r.returncode
    if r.returncode != 0:
        # Mid-flight environmental failure (network, auth expiry). Still not a gate.
        skip(f"gh {' '.join(args[:3])}… failed: {(r.stderr or r.stdout).strip()[:200]}")
    return r.stdout.strip() if capture else ""


def gh_try(args):
    """`gh` WITHOUT `skip()`. Returns `(ok, stdout)`; on failure returns `(False, stderr)`.

    `gh()` turns any non-zero exit into `skip()`, which prints the literal `gh-sync: SKIP` and
    calls `sys.exit(0)`. That is right for a mid-flight environmental failure of the whole
    invocation, and WRONG for `cmd_ship`'s per-card child read: it would abandon a ship that
    had already written most of its cards, and `post-merge-sweep.sh` greps that exact literal
    to decide whether to keep the worktree, so a single unreadable child list would silently
    change worktree behaviour on an otherwise healthy run."""
    with gh_cost_log.measured(args) as _cost:
        r = subprocess.run([GH] + args, capture_output=True, text=True)
        _cost.returncode = r.returncode
    if r.returncode != 0:
        return (False, (r.stderr or r.stdout).strip()[:200])
    return (True, r.stdout.strip())


# ---------- config ----------

def load_config(root):
    """Return `(repo, board)`. `board` is `gh_board.load_board(root)` — a dict, or None when
    `github.board` is an EXPLICIT null. An explicit null is the ONLY environmental precondition
    left (D-02, D-07): the issue lifecycle (open, abandon, ship)
    still runs; only station writes are skipped.

    Every OTHER unusable board shape — the `github` block absent, `board` key absent, or any
    field `factory_config.validate_board` rejects — raises `factory_config.FleetError` from
    `gh_board.load_board`, and THIS FUNCTION does not catch it; `main()` does, exiting 2 with
    the error on stderr. That is a loud failure of the WHOLE invocation, not a skipped station
    write — an unusable declaration is a misconfiguration to fix, not an absence to tolerate."""
    p = os.path.join(root, ".harness", "harness.json")
    if not os.path.isfile(p):
        skip("no .harness/harness.json — project not onboarded")
    try:
        cfg = json.load(open(p))
    except Exception as e:
        skip(f"harness.json unreadable ({e})")
    g = cfg.get("github") or {}
    if not g.get("sync"):
        skip("github.sync is not enabled for this project")
    repo = g.get("repo")
    if not repo or "/" not in str(repo):
        skip("github.repo is not pinned — run /harness-init --upgrade to record it")
    if shutil.which(GH) is None:
        skip(f"{GH} not on PATH")
    if subprocess.run([GH, "auth", "status"], capture_output=True).returncode != 0:
        skip("gh is not authenticated")
    board = gh_board.load_board(root)
    if board is None:
        print("gh-sync: no github.board configured — station writes are not attempted")
    return repo, board


def _feature_status(feat_dir):
    """feature.json's top-level `status`, or None if absent/unreadable/not a string.

    The ONLY read of feature.json's status outside the `github:` block, and it feeds
    EXACTLY one comparison (the Done terminal exemption, D-03/D-04) — nothing else."""
    path = os.path.join(feat_dir, "feature.json")
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict):
        return None
    status = doc.get("status")
    return status if isinstance(status, str) else None


def _apply_parent_rule(feat_dir, repo, board):
    """THE PARENT RULE (T-03, D-03/D-04) — called at the end of `start-task`, which is now
    its ONLY caller. The per-commit subcommand that used to be the second one was deleted
    under DEC-203 item 8: it closed an issue while writing no station. This stays a separate
    function rather than being folded into its one caller, because the derivation is
    deliberately caller-independent and the next caller must inherit that, not re-derive it.

    THE DERIVATION PRESUPPOSES THE PLAN IS ALREADY UPDATED. The caller reads plan.yaml from
    disk, so the CALLER (the orchestrator) must have recorded the task's new status in
    plan.yaml BEFORE invoking this subcommand — this function never infers the transition
    from which subcommand called it, because that would make the subcommand a second status
    record, which is exactly the drift D-03 removes.
    """
    if _feature_status(feat_dir) in ("Done", "Abandoned"):
        # Terminal exemption: `ship` wrote the parent's card to the done station and
        # recorded the terminal status, while the plan-derived station would still say
        # Review. Without this exemption every shipped feature is a permanent false
        # violation. The CONDITION is unchanged -- it still keys on feature.json's status.
        return
    plan_path = os.path.join(feat_dir, "plan.yaml")
    if not os.path.isfile(plan_path):
        # No plan.yaml (a PLAN.md-only feature) carries no task-derived verdict at all.
        return
    try:
        plan_doc = harness_yaml.load_plan(plan_path)
    except harness_yaml.YamlParseError:
        # An unparseable plan carries no derivable verdict either — same as no verdict.
        return
    station = gh_board.derive_station(plan_doc, board)
    if station is None:
        return
    rec = load_recorded(feat_dir)
    if rec["parent"] is None:
        # INV-21 already warns on this shape (a recorded task issue with no parent) —
        # this must not become a second report of it.
        print(f"gh-sync: no parent recorded for {os.path.basename(os.path.abspath(feat_dir))} "
              f"— parent station not written", file=sys.stderr)
        return
    try:
        gh_board.set_station(board, repo, rec["parent"], station)
        print(f"gh-sync: parent #{rec['parent']} -> {station}")
    except gh_board.BoardError as e:
        print(f"gh-sync: ERROR - {e}", file=sys.stderr)


# ---------- parsing (same hand-rolled discipline as the rest of bin/ — stdlib only) ----------

def read(p):
    if not os.path.isfile(p):
        die(f"{p} does not exist")
    return open(p, encoding="utf-8").read()


def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def parse_brief(feat_dir):
    t = read(os.path.join(feat_dir, "BRIEF.md"))
    feat = os.path.basename(os.path.abspath(feat_dir))
    scs = re.findall(r"^- (SC-\d+):\s*(.+?)(?=^- SC-\d+:|\Z)", section(t, "Success Criteria"),
                     re.M | re.S)
    h1 = t.split("\n", 1)[0]
    parts = h1.split("—", 2)
    phrase = parts[2].strip() if len(parts) >= 3 else ""
    return {
        "feat": feat,
        "phrase": phrase,
        "problem": section(t, "Problem"),
        "goal": section(t, "Goal"),
        "scs": [(sid, " ".join(body.split())[:200]) for sid, body in scs],
    }


def parse_tasks(feat_dir):
    """Tasks from plan.yaml if present, else PLAN.md's two markdown shapes (DEC-129/182).

    plan.yaml FIRST and by the loader, not a regex. The issue body becomes the task's
    `intent:` rather than its whole raw block — a deliberate behaviour change: intent is the
    dispatch prompt, and it is the half of a task a human reading a GitHub issue actually
    wants. Issues already opened from a PLAN.md carry the old whole-body text; they are not
    rewritten, so the corpus is mixed. Stated here rather than discovered later.
    """
    yml = os.path.join(feat_dir, "plan.yaml")
    if os.path.isfile(yml):
        import harness_yaml
        try:
            doc = harness_yaml.load_plan(yml)
        except harness_yaml.YamlParseError as e:
            die(f"{yml} does not load: {e}")
        out = []
        for t_ in doc["tasks"]:
            traces = t_.get("traces") or []
            out.append({
                "id": str(t_["id"]),
                "title": t_.get("title") or str(t_["id"]),
                "body": (t_.get("intent") or "").strip(),
                "change_type": t_.get("change_type", ""),
                # A LIST, joined for the issue body. The old field was a raw string, so a
                # caller expecting text still gets text.
                "traces": ", ".join(str(x) for x in traces) if isinstance(traces, list)
                          else str(traces),
                "absorbs": [str(a).lstrip("#") for a in (t_.get("absorbs") or [])],
                # T-03 (FEAT-18): an absent status is legal in plan.yaml and reads as pending
                # (harness-backend-dev, D-03's precedent in gh_board.derive_station).
                "status": t_.get("status") or "pending",
            })
        return out

    t = read(os.path.join(feat_dir, "PLAN.md"))
    tasks = []
    for m in re.finditer(r"^(?:###\s*|-\s*)(T-\d+)\b[ —:-]*(.*?)$(.*?)(?=^(?:###\s*|-\s*)T-\d+\b|^## |\Z)",
                         t, re.M | re.S):
        tid, title, body = m.group(1), m.group(2).strip(" —:-"), m.group(3)
        def field(name):
            f = re.search(rf"^\s*-?\s*{name}:\s*(.+)$", body, re.M)
            return f.group(1).strip() if f else ""
        absorbs = re.findall(r"#(\d+)", field("absorbs"))
        # This corpus predates the status field entirely — there is no third value to
        # read here, so every PLAN.md task is unconditionally pending (T-03, FEAT-18).
        tasks.append({"id": tid, "title": title or tid, "body": body.strip(),
                      "change_type": field("change_type"), "traces": field("traces"),
                      "absorbs": absorbs, "status": "pending"})
    if not tasks:
        die(f"no T-NN tasks parse from {feat_dir}/PLAN.md")
    return tasks


def parse_source_issues(feat_dir):
    """plan.yaml's own top-level `source_issues` — the tickets a plan traces back to,
    made machine-readable (T-02, FEAT-26). The plan is the truth; feature.json's
    `github.source_issues` is only ever a mirror of what this function returns, refreshed
    by `cmd_open` on every run so a re-plan that changes the tickets is picked up by a
    re-run.

    Returns `[]` — never raises — when plan.yaml is absent, when it carries no
    `source_issues` key, when the value is not a list, or when the feature is still on
    the PLAN.md format (no plan.yaml at all, same absence check). Members that are not
    real integers (bool excluded — an int subclass in Python, same exclusion `_opt_int`
    documents) are dropped silently, in the order plan.yaml wrote them; a malformed
    field here must not block issue creation, which is the whole reason this reader is
    tolerant rather than loud.

    A plan.yaml that does not PARSE is a different failure: `harness_yaml.load_file`
    raises loudly and this function does not catch it — that failure already exists
    everywhere else this module reads plan.yaml, and is left unchanged here."""
    path = os.path.join(feat_dir, "plan.yaml")
    if not os.path.isfile(path):
        return []
    doc = harness_yaml.load_file(path)
    if not isinstance(doc, dict):
        return []
    si = doc.get("source_issues")
    if not isinstance(si, list):
        return []
    return [n for n in si if isinstance(n, int) and not isinstance(n, bool)]


def type_label(change_type):
    if change_type in CHORE_TYPES:
        return "chore"
    if change_type == "bugfix":
        return "bug"
    return None


# ---------- feature.json github block ----------
# The header used to read "text ops — no yaml dependency", which T-06 made false and
# F-04 caught still standing: load_recorded PARSES with harness_yaml (DEC-171).
# T-05 (FEAT-14) moved the writer off text splicing too: JSON has no comments to
# preserve, so save_recorded is a read-modify-write over the whole document.
#
# FEAT-14 fix1 (panel HIGH): two more defects, found composing. `save_recorded` opened
# feature.json with a truncating `open(p, "w")` — the file was OBSERVABLY ZERO BYTES the
# instant that call returned, before any data was written, on EVERY call, and `:394`
# calls it inside the per-issue create loop. `load_recorded` then read that zero-byte
# window as "nothing is mirrored", which re-creates GitHub issues that already exist.
# Fixed by converging on json.load/json.dump (B-5, matching factory_decompose.py's
# reader) and matching factory_decompose.py:142-186's write_factory shape exactly:
# same-directory tempfile.mkstemp + fsync + os.replace, so feature.json is never
# observable partial or empty. And by making an empty/unparseable/non-mapping document a
# loud SystemExit rather than "nothing recorded" — three states stay distinct: file
# absent (or present with no `github` key) is a legitimate first sync; file present but
# empty/non-mapping/unparseable is an error; file present with a `github` mapping loads
# as today. A `github` key that IS present but is not itself a mapping is treated as the
# error case too — refusing to sync beats guessing what is mirrored.

def _opt_int(v):
    """A recorded issue/milestone number as int, or None for `none`/absent/junk.

    Tolerates the quoted form the old `(\\d+)` regex silently read as ABSENT — and
    "absent" here meant `gh-sync` believed nothing was recorded and would create a
    duplicate parent or milestone. bool is excluded explicitly: it is an int subclass
    in Python, so `parent: true` would otherwise become 1."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    s = str(v).strip()
    return int(s) if s.isdigit() else None


def load_recorded(feat_dir):
    """Read the `github:` block from feature.json with json.load (B-5: converged with
    factory_decompose.py's reader; this file has no comments to tolerate).

    Three states stay distinct on purpose (fix1 Part B) — collapsing either pair
    reproduces a real bug:

    - file ABSENT, or present as a mapping with no `github` key -> a legitimate FIRST
      SYNC. Return the all-None default; nothing is mirrored yet because nothing has
      run yet.
    - file present but empty, unparseable, or not a JSON mapping -> ERROR, loud,
      SystemExit. This is what a truncating `open(p, "w")` produced for an
      OBSERVABLE INSTANT on every past call (the defect this fix exists for): reading
      that window as "nothing recorded" re-creates issues, milestones and the parent
      that already exist on GitHub.
    - file present with a `github` mapping -> load it, as today.

    A fourth state the spec's three-row table does not name: `github` IS present but is
    NOT itself a mapping (a string or a list). Treated as the error case, not as
    "nothing recorded" — the point is refusing to sync when what is mirrored cannot be
    known, and a non-mapping `github:` value cannot be read as an empty record without
    reproducing the exact bug shape this fix removes. (Non-blocking open_question filed
    for the operator — this state was not in the spec's own table.)
    """
    path = os.path.join(feat_dir, "feature.json")
    rec = {"milestone": None, "parent": None, "attached": [], "issues": {},
           "source_issues": []}
    # ABSENCE is checked before parsing, not caught after it (review finding 4) — a
    # missing feature.json is a legitimate first sync, never an error.
    if not os.path.exists(path):
        return rec
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise SystemExit(f"gh-sync: {path} could not be read, so what is already mirrored "
                         f"cannot be known. Refusing to sync rather than risk duplicate "
                         f"issues.\n  {e}")
    try:
        doc = json.loads(text)
    except (ValueError, UnicodeDecodeError) as e:
        # Covers a genuinely empty file too: `json.loads("")` raises JSONDecodeError,
        # never returns None the way `yaml.load("")` silently did — that silent-None
        # path was the exact defect this fix removes, so the JSON reader must not
        # reintroduce it under a different parser.
        raise SystemExit(f"gh-sync: {path} does not parse, so what is already mirrored "
                         f"cannot be known. Refusing to sync rather than risk duplicate "
                         f"issues.\n  {e}")
    # A parses-but-is-not-a-mapping document (a bare list or scalar) is not an error
    # json.loads raises, so the type must be guarded explicitly, same rule M-02 found
    # in manifest_domains: parsing successfully is not the same as parsing usefully.
    if not isinstance(doc, dict):
        raise SystemExit(f"gh-sync: {path} parsed but is not a JSON mapping "
                         f"(got {type(doc).__name__}), so what is already mirrored "
                         f"cannot be known. Refusing to sync rather than risk duplicate "
                         f"issues.")
    if "github" not in doc:
        # Row 1: a legitimate first sync — the document exists, it just has nothing
        # recorded yet.
        return rec
    gh = doc.get("github")
    if not isinstance(gh, dict):
        # The fourth state: present but not a mapping. Same refusal as row 2 — see the
        # docstring above.
        raise SystemExit(f"gh-sync: {path}'s github: key is present but is not a "
                         f"mapping (got {type(gh).__name__}), so what is already "
                         f"mirrored cannot be known. Refusing to sync rather than risk "
                         f"duplicate issues.")

    rec["milestone"] = _opt_int(gh.get("milestone"))
    rec["parent"] = _opt_int(gh.get("parent"))
    # THE PARENT'S ORIGIN IS NOT RECORDED (DEC-203 item 4). A github block written before
    # this feature may still carry that key; it is read without complaint and never
    # surfaced, because the record has no such field any more. Where a parent came from is
    # not part of any decision the mirror makes.

    attached = gh.get("attached")
    if isinstance(attached, list):
        rec["attached"] = [str(x).strip() for x in attached if str(x).strip()]
    elif isinstance(attached, str) and attached.strip():
        rec["attached"] = [x.strip() for x in attached.split(",") if x.strip()]

    issues = gh.get("issues")
    if isinstance(issues, dict):
        for k, v in issues.items():
            n = _opt_int(v)
            if n is not None and re.fullmatch(r"T-\d+", str(k).strip()):
                rec["issues"][str(k).strip()] = n

    # T-02 (FEAT-26): source_issues is a MIRROR of plan.yaml's own top-level field (D-01 of
    # that task — the plan is truth, feature.json just reflects it), so a malformed value
    # here does not put issue creation at risk: a non-list value, or a non-integer member,
    # is dropped silently rather than raising, the same tolerance _opt_int already documents
    # for bool (an int subclass in Python).
    si = gh.get("source_issues")
    if isinstance(si, list):
        rec["source_issues"] = [n for n in si if isinstance(n, int) and not isinstance(n, bool)]
    return rec


def _record_status(feat_dir, status):
    """Set feature.json's top-level `status` to the exact string `status` (Done or Abandoned,
    T-01/FEAT-23), through feature_json_write.write_feature_json (stale-anchor-write-hazard
    T-c2): the same lock, same-directory tempfile, fsync and os.replace `_atomic_write` gave
    it, now shared with every other Python writer of feature.json (DEC-199) instead of a
    second copy of the primitive. A feature.json that is absent or unreadable is not an
    error here (mirrors `_feature_status`'s own tolerance): both `cmd_ship` and `cmd_abandon`
    are idempotent and the mirror never gates, so this prints one plain line and returns
    rather than raising. This does NOT create a document when one is absent — the schema's
    eight required keys (DEC-191) make a fresh single-key document invalid. `save_recorded`
    (T-02, FEAT-26) refuses the absent-file case too rather than creating one, so this is not
    a second, incompatible first-sync path alongside it — the two are aligned on the same
    refusal.

    The absent/unreadable/non-mapping decision is made HERE, on a plain read, before
    write_feature_json (and its require_destination check) is ever called — so a bad path
    shape never masquerades as this function's own tolerant "not recorded" message, and a
    genuinely absent file never reaches require_destination's differently-worded refusal."""
    path = os.path.join(feat_dir, "feature.json")
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        print(f"gh-sync: {path} could not be read — status not recorded")
        return
    if not isinstance(doc, dict):
        print(f"gh-sync: {path} is not a JSON mapping — status not recorded")
        return

    def transform(base):
        # Re-read under the lock rather than reusing `doc`: another writer may have
        # landed a change between the plain read above and the lock acquire, and the
        # whole point of routing through the locked core is to never clobber it.
        if base is None:
            raise harness_merge.MergeRefusal(9, [f"{path}: vanished before the write landed"])
        current = json.loads(base.decode("utf-8"))
        current["status"] = status
        return json.dumps(current, indent=2) + "\n"

    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal:
        print(f"gh-sync: {path} could not be read — status not recorded")
        return
    print(f"gh-sync: feature.json status -> {status}")


def _record_pr(feat_dir, repo, pr_arg=None):
    """Set feature.json's top-level `pr` to the number of the branch's exactly-one merged
    pull request (T-03, FEAT-26) — the mirror image of `_record_status`: same read pattern,
    same locked write through feature_json_write.write_feature_json, same one-line-and-return
    on every failure path, and it NEVER creates a document either.

    IDEMPOTENT: an already-recorded int `pr` is never overwritten, on any path — not even
    when `pr_arg` disagrees with it — which is what makes a backfill re-run safe. The
    idempotency check runs TWICE: once here (before the `gh pr list` network call, so an
    already-recorded pr costs no API call) and again inside the locked transform against a
    FRESH read (so a second writer that landed a `pr` between this function's read and its
    lock acquire is still respected, closing the exact race the earlier single-read
    `_atomic_write` version could not).

    EXACTLY ONE is the rule, not first-match: the branch feat/harness-native-foundation
    carries two merged pull requests, 15 and 4, so a first-match rule would record the
    wrong one. Zero or two-or-more merged pull requests, and a gh failure or unparseable
    output, are all the same shape — one printed line, no write — and every path here
    returns normally so the process exits 0; the mirror never gates a flow.
    """
    path = os.path.join(feat_dir, "feature.json")
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        print(f"gh-sync: {path} could not be read — pr not recorded")
        return
    if not isinstance(doc, dict):
        print(f"gh-sync: {path} is not a JSON mapping — pr not recorded")
        return
    existing = doc.get("pr")
    if isinstance(existing, int) and not isinstance(existing, bool):
        print(f"gh-sync: pr already recorded as #{existing} — not overwritten")
        return
    if pr_arg is not None:
        number = int(pr_arg)
    else:
        branch = doc.get("branch")
        if not isinstance(branch, str) or branch == "none":
            print("gh-sync: branch is unset — pr not recorded")
            return
        args = ["pr", "list", "--repo", repo, "--head", branch, "--state", "merged",
                "--limit", "10", "--json", "number"]
        with gh_cost_log.measured(args) as _cost:
            r = subprocess.run([GH] + args, capture_output=True, text=True)
            _cost.returncode = r.returncode
        if r.returncode != 0:
            # A gh failure here is deliberately NOT routed through gh()/skip() — skip()
            # exits the whole process, which would swallow cmd_ship's remaining work
            # (the status write). It is the same "no write" shape as zero results.
            print(f"gh-sync: no merged pull request found on branch {branch} "
                  f"(gh pr list failed: {(r.stderr or r.stdout).strip()[:200]})")
            return
        try:
            found = json.loads(r.stdout)
        except (ValueError, TypeError):
            found = None
        if not isinstance(found, list) or not found:
            print(f"gh-sync: no merged pull request found on branch {branch}")
            return
        if len(found) > 1:
            nums = ", ".join(str(x.get("number")) for x in found if isinstance(x, dict))
            print(f"gh-sync: branch {branch} is ambiguous — merged pull requests {nums}")
            return
        number = found[0].get("number") if isinstance(found[0], dict) else None
        if not isinstance(number, int) or isinstance(number, bool):
            print(f"gh-sync: no merged pull request found on branch {branch}")
            return

    outcome = {}

    def transform(base):
        if base is None:
            raise harness_merge.MergeRefusal(9, [f"{path}: vanished before the write landed"])
        current = json.loads(base.decode("utf-8"))
        current_existing = current.get("pr")
        if isinstance(current_existing, int) and not isinstance(current_existing, bool):
            outcome["skipped"] = current_existing
            return base  # no-op replace: another writer already recorded it first
        current["pr"] = number
        return json.dumps(current, indent=2) + "\n"

    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal:
        print(f"gh-sync: {path} could not be read — pr not recorded")
        return

    if "skipped" in outcome:
        print(f"gh-sync: pr already recorded as #{outcome['skipped']} — not overwritten")
    else:
        print(f"gh-sync: {os.path.basename(os.path.abspath(feat_dir))} pr -> #{number}")


def save_recorded(feat_dir, rec):
    """Read-modify-write the `github:` key into feature.json through
    feature_json_write.write_feature_json (DEC-199): the same lock, same-directory
    tempfile, fsync and os.replace `_atomic_write` gave it, matching factory_decompose.py's
    write_factory (`:142-186`) in shape for the file that exists — load the document,
    tolerating a not-a-JSON-mapping document by starting from `{}` (B-5's
    exists->load-else-{} form) -> set `github` -> replace the WHOLE document atomically.
    A genuinely ABSENT feature.json is REFUSED (T-02, FEAT-26), not started from `{}` — see
    the inline comment below for why. feature.json itself is opened only for reading, never
    in a truncating mode: every observer sees either the previous complete file or the next
    one, never a partial or zero-byte one — the truncating `open(p, "w")` fix1 replaced made
    a zero-byte window OBSERVABLE on every call, which `load_recorded` then read as "nothing
    recorded", re-creating issues that already exist.

    The absent-file refusal is raised TWICE, verbatim: once here on a plain existence check
    (before write_feature_json's require_destination can fire and substitute its own,
    differently-worded destination refusal for this one), and again inside the locked
    transform if the file vanishes between that check and the lock acquire — the same
    narrow race `_record_status`/`_record_pr` close the same way.
    """
    p = os.path.join(feat_dir, "feature.json")
    absent_message = (
        f"gh-sync: {p} is absent. The orchestrator instantiates feature.json from "
        f".agents/skills/harness/templates/feature.json on its first cycle; writing "
        f"one here would produce a document missing the schema's eight required "
        f"keys. Run this feature through the orchestrator's normal cycle first."
    )
    # T-02 (FEAT-26), absorbs #289: an absent feature.json is REFUSED, not silently
    # started from `{}`. A document started here from `{}` would carry only the
    # `github` key this function sets, missing every one of feature-schema.json's eight
    # required keys.
    #
    # Accepted ordering gap: on a hand-run of `open` against a directory with no
    # feature.json, this refusal fires AFTER the milestone create (cmd_open calls
    # save_recorded immediately after creating the milestone), so the milestone is
    # orphaned by this exit. The existing 422 title-lookup recovery in cmd_open
    # resolves it on the next run once the file exists — accepted rather than moved
    # earlier, because checking for feature.json before the milestone create would be
    # a SECOND first-sync policy in a file that has already been bitten by having two.
    if not os.path.exists(p):
        raise SystemExit(absent_message)

    def transform(base):
        if base is None:
            raise SystemExit(absent_message)
        doc = json.loads(base.decode("utf-8"))
        if not isinstance(doc, dict):
            # A file that exists and is already being replaced wholesale — same
            # tolerance load_recorded applies to a non-mapping document, kept here
            # because this branch is a real file, not the absent-file path above.
            doc = {}
        doc["github"] = {
            "milestone": rec["milestone"],
            "parent": rec["parent"],
            "attached": rec["attached"],
            "issues": dict(sorted(rec["issues"].items())),
            "source_issues": list(rec["source_issues"]),
        }
        return json.dumps(doc, indent=2) + "\n"

    feature_json_write.write_feature_json(p, transform)


# ---------- commands ----------

def ensure_labels(repo, labels):
    """Create any missing labels first. LIVE SMOKE FINDING #1: GitHub rejects an issue
    create naming a label the repo does not define — new repos ship `bug` but not
    `harness`/`chore`. Errors here are swallowed (label already exists is the common
    case); the create call below is what surfaces a genuinely broken repo."""
    # "abandoned": b60205 is THIS function's colour for the label. factory_gh.ensure_labels
    # (a separate implementation, D-04 — three stay three) creates the same label name with
    # `--force` and its own single _LABEL_COLOR, so a run that goes through THAT function
    # after this one has run would silently overwrite this colour. Named here so a later
    # reader finds the collision rather than rediscovering it.
    colors = {"harness": "5319e7", "chore": "cccccc", "bug": "d73a4a", "enhancement": "a2eeef",
              "abandoned": "b60205"}
    for l in labels:
        subprocess.run([GH, "label", "create", l, "--repo", repo,
                        "--color", colors.get(l, "ededed"),
                        "--description", "created by harness gh-sync"],
                       capture_output=True)


def cmd_open(feat_dir, repo, parent_arg=None):
    brief, tasks, rec = parse_brief(feat_dir), parse_tasks(feat_dir), load_recorded(feat_dir)
    # T-02 (FEAT-26): refreshed from the plan on EVERY run — a re-plan that changes the
    # source tickets is picked up by a re-run, because the plan is the truth and
    # feature.json's github.source_issues is only ever the mirror.
    rec["source_issues"] = parse_source_issues(feat_dir)
    ensure_labels(repo, {"harness"} | {l for tk in tasks if (l := type_label(tk["change_type"]))})

    if rec["milestone"] is None:
        desc = (f"{brief['problem']}\n\n**Goal:** {brief['goal']}\n\n## Definition of done\n"
                + "\n".join(f"- [ ] {sid}: {txt}" for sid, txt in brief["scs"]))
        r = subprocess.run([GH, "api", "-X", "POST", f"repos/{repo}/milestones",
                            "-f", f"title={brief['feat']}", "-f", f"description={desc}"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            rec["milestone"] = json.loads(r.stdout)["number"]
            print(f"gh-sync: milestone #{rec['milestone']} created for {brief['feat']}")
        else:
            # LIVE SMOKE FINDING #3: 422 when the title already exists — a previous run
            # created it and died before recording (or a human made one). Resolve by
            # lookup instead of failing; anything else is a real environmental skip.
            out = gh(["api", f"repos/{repo}/milestones", "-q",
                      f'[.[] | select(.title == "{brief["feat"]}") | .number] | first'])
            if not out or out == "null":
                skip(f"milestone create failed and no existing one matches: "
                     f"{(r.stderr or r.stdout).strip()[:200]}")
            rec["milestone"] = int(out)
            print(f"gh-sync: milestone #{rec['milestone']} recovered by title lookup")
        # LIVE SMOKE FINDING #2: record the milestone IMMEDIATELY. The first live run
        # created it, hit a downstream failure, exited before saving — and the re-run
        # 422'd on the orphan. The record-after-every-create rule applies to the
        # milestone too, not just issues (DEC-131, applied fully this time).
        save_recorded(feat_dir, rec)
    else:
        print(f"gh-sync: milestone #{rec['milestone']} already recorded — skipping")

    # D-01: the parent is adopted-or-created, its number recorded, never discovered.
    if rec["parent"] is not None:
        print(f"gh-sync: parent #{rec['parent']} already recorded — skipping")
    elif parent_arg is not None:
        rec["parent"] = int(parent_arg)
        save_recorded(feat_dir, rec)   # DEC-131: record immediately, same call as the number
        print(f"gh-sync: parent #{rec['parent']} adopted")
    else:
        title = f"{brief['feat']} — {brief['phrase']}" if brief["phrase"] else brief["feat"]
        body = f"{brief['problem']}\n\n**Goal:** {brief['goal']}"
        url = gh(["issue", "create", "--repo", repo, "--title", title,
                  "--body", body, "--label", "harness"])
        rec["parent"] = int(url.rstrip("/").rsplit("/", 1)[-1])
        save_recorded(feat_dir, rec)
        print(f"gh-sync: parent #{rec['parent']} created")

    for task in tasks:
        if task["id"] in rec["issues"]:
            print(f"gh-sync: {task['id']} already issue #{rec['issues'][task['id']]} — skipping")
        else:
            body = task["body"]
            if task["absorbs"]:
                body += "\n\nabsorbs: " + ", ".join(f"#{n}" for n in task["absorbs"])
            labels = ["harness"] + ([type_label(task["change_type"])] if type_label(task["change_type"]) else [])
            args = ["issue", "create", "--repo", repo,
                    "--title", f"{brief['feat']} — {task['id']} — {task['title']}", "--body", body,
                    "--milestone", brief["feat"]]
            for l in labels:
                args += ["--label", l]
            url = gh(args)
            num = int(url.rstrip("/").rsplit("/", 1)[-1])
            rec["issues"][task["id"]] = num
            save_recorded(feat_dir, rec)   # after EVERY create — a crash mid-loop must not orphan issues
            print(f"gh-sync: {task['id']} -> issue #{num} [{', '.join(labels)}]")

        # Attach to the parent — a separate receipt from the create, so a crash between
        # recording the issue and attaching it is resumed rather than repeated or lost.
        if task["id"] in rec["attached"]:
            continue
        child_num = rec["issues"][task["id"]]
        child_id = gh(internal_id_args(repo, child_num))
        gh(attach_sub_issue_args(repo, rec["parent"], child_id), capture=False)
        rec["attached"].append(task["id"])
        save_recorded(feat_dir, rec)
        print(f"gh-sync: {task['id']} (issue #{child_num}) attached to parent #{rec['parent']}")
    save_recorded(feat_dir, rec)


def cmd_start_task(feat_dir, tid, repo, board):
    """`start-task <feature-dir> T-NN` — the orchestrator fires this in the same act it
    records the task's status as `building` in plan.yaml (D-04). Sets T-NN's OWN sub-issue
    station to `board["stations"]["building"]`, then applies the parent rule (step 3) — never
    routed through gh(), since a failed station write must not terminate the process (D-02).

    GUARDS AGAINST DRIVING A CLOSED CARD BACKWARDS (T-07). Measured on #642 and #643: the
    card closed, github-project-automation[bot] set it to Done a second later, and this
    command — invoked afterward on a stale "was it open when the run started" assumption —
    set it back to Building. The guard reads the issue's CURRENT state, not what it was when
    the run started: refuse the station write when EITHER `gh issue view` reports the issue
    CLOSED, or the card's CURRENT station already equals `board["stations"]["done"]`. On
    refusal, print one line and return without calling `set_station` or `_apply_parent_rule`
    — the parent rule would otherwise write a Building parent for a task this guard just
    refused. A refusal is NOT a failure: exit code and control flow are unchanged (DEC-146
    keeps the station flip best-effort; DEC-138 forbids the mirror from gating a flow).

    ADDED COST: start-task now performs ONE board read (`gh_board.board_stations`, reused for
    both halves of the guard — no second board read) and ONE issue read (`factory_gh.issue_view`
    for `state`) before its writes, where before it performed none. Squarely inside DEC-186's
    second sanctioned purpose — learning which station an item is at.

    A gh or network failure during EITHER read must not gate either: caught, printed as one
    line, and control falls through to the ORIGINAL behaviour (attempt the write) rather than
    refusing — a guard that cannot see the board must not silently stop moving cards.
    """
    rec = load_recorded(feat_dir)
    if tid not in rec["issues"]:
        skip(f"{tid} has no recorded issue — nothing to start (was `open` run?)")
    if board is not None:
        issue_num = rec["issues"][tid]
        building = board["stations"]["building"]
        refused = False
        try:
            stations = gh_board.board_stations(board, repo)
            current_station, _ = gh_board.read_station(stations, issue_num)
            state = (factory_gh.issue_view(repo, issue_num, ["state"]) or {}).get("state")
            if state == "CLOSED" or current_station == board["stations"]["done"]:
                reason = "issue is CLOSED" if state == "CLOSED" else "card is already Done"
                print(f"gh-sync: refusing #{issue_num} ({tid}) -> {building}: "
                      f"current station is {current_station!r}, {reason}")
                refused = True
        except factory_gh.GhError as e:
            print(f"gh-sync: ERROR - guard read failed for #{issue_num} ({tid}): {e} "
                  f"— proceeding without the guard", file=sys.stderr)
        if refused:
            return
        try:
            gh_board.set_station(board, repo, issue_num, building)
            print(f"gh-sync: issue #{issue_num} ({tid}) -> {building}")
        except gh_board.BoardError as e:
            print(f"gh-sync: ERROR - {e}", file=sys.stderr)
        _apply_parent_rule(feat_dir, repo, board)


def _status_plan_doc(feat_dir):
    """plan.yaml, loaded and validated, or None on any failure (absent file, unparseable,
    or schema-invalid). `status`'s two guarded transitions (Ready, Review) both need this
    and both treat a failure to load as "the precondition is not met" rather than raising —
    an unreadable plan cannot prove a signature or prove every task is done."""
    path = os.path.join(feat_dir, "plan.yaml")
    if not os.path.isfile(path):
        return None
    try:
        return harness_yaml.load_plan(path)
    except harness_yaml.YamlParseError:
        return None


def cmd_status(feat_dir, status, repo, board):
    """`status <feature-dir> <Status>` (T-13, D-16) — couples recording a feature's phase
    status to the station writes THAT EVENT implies, so a station write cannot be forgotten
    separately from the phase record.

    ORDER IS FIXED: the status write to feature.json happens FIRST and is never conditional
    on any board write (step 4) — a failed board write must never leave the recorded status
    behind, because the recorded status is what the audit grades the card against. Every
    refusal below (step 5) therefore runs BEFORE `_record_status`, since a refusal must leave
    NOTHING recorded.

    STATION WRITES, exactly what step 2 specifies and nothing else:
    - Ready: every recorded T-NN sub-issue (never the parent — D-18, THE PARENT MUST NEVER
      REACH THE READY COLUMN) moves to `board["stations"]["ready"]`. Zero recorded sub-issues
      prints one line and writes nothing — no fallback to the parent.
    - Review: the PARENT and every recorded T-NN sub-issue move to
      `board["stations"]["review"]` (operator ruling, D-23) — one `gh_board.set_station` call
      each. A parent that is not recorded prints one stderr line and the sub-issue writes
      still proceed; this does not raise and does not restate INV-21's finding.
    - Plan, Done, Abandoned: no station write at all (Plan is board-station.py's own write;
      Done is written by `ship` alone, which is the only writer of the done station, so a
      Done feature's cards are already there by the time this runs; Abandoned has no column
      at all, D-03/DEC-203).

    FAILURE POSTURE, unchanged from every other station write in this file: a `BoardError`
    from one card prints one stderr line and the remaining cards still get written — a bulk
    write must not stop at the first failure (step 4).

    `board is None` (no github.board configured) skips every station write below — the
    status is still recorded.
    """
    if status not in STATUS_VALUES:
        refuse(f"unknown status {status!r} — must be one of {', '.join(STATUS_VALUES)}")

    if status == "Ready":
        plan_doc = _status_plan_doc(feat_dir)
        approval = (plan_doc or {}).get("approval") or {}
        if approval.get("status") != "approved":
            refuse("status Ready refused — plan.yaml's approval.status is not 'approved'")

    if status == "Review":
        plan_doc = _status_plan_doc(feat_dir)
        tasks = (plan_doc or {}).get("tasks") or []
        all_done = bool(tasks) and all((t.get("status") or "pending") == "done" for t in tasks)
        if not all_done:
            refuse("status Review refused — not every task in plan.yaml carries status done")

    _record_status(feat_dir, status)

    if board is None or status in ("Plan", "Done", "Abandoned"):
        return

    rec = load_recorded(feat_dir)

    if status == "Ready":
        numbers = sorted(rec["issues"].values())
        if not numbers:
            print("gh-sync: status Ready — no sub-issues recorded, nothing to move")
            return
        ready = board["stations"]["ready"]
        for num in numbers:
            try:
                gh_board.set_station(board, repo, num, ready)
                print(f"gh-sync: issue #{num} -> {ready}")
            except gh_board.BoardError as e:
                print(f"gh-sync: ERROR - {e}", file=sys.stderr)
    elif status == "Review":
        review = board["stations"]["review"]
        if rec["parent"] is None:
            print(f"gh-sync: no parent recorded for "
                  f"{os.path.basename(os.path.abspath(feat_dir))} — parent station not "
                  f"written", file=sys.stderr)
        else:
            try:
                gh_board.set_station(board, repo, rec["parent"], review)
                print(f"gh-sync: parent #{rec['parent']} -> {review}")
            except gh_board.BoardError as e:
                print(f"gh-sync: ERROR - {e}", file=sys.stderr)
        for num in sorted(rec["issues"].values()):
            try:
                gh_board.set_station(board, repo, num, review)
                print(f"gh-sync: issue #{num} -> {review}")
            except gh_board.BoardError as e:
                print(f"gh-sync: ERROR - {e}", file=sys.stderr)


def _detach_from_parent(repo, parent, num):
    """Break the sub-issue link so an abandoned ticket stops holding its parent open.

    Best-effort, like every other write here: a failure prints one stderr line and the close
    still runs. An attached-but-closed ticket is a worse outcome than a detached one, but it
    is far better than not closing it at all."""
    ok, out = gh_try(internal_id_args(repo, num))
    if not ok:
        print(f"gh-sync: ERROR - could not read #{num}'s internal id, left attached to "
              f"#{parent}: {out}", file=sys.stderr)
        return
    ok, out = gh_try(detach_sub_issue_args(repo, parent, out.strip()))
    if not ok:
        print(f"gh-sync: ERROR - could not detach #{num} from #{parent}: {out}",
              file=sys.stderr)
        return
    print(f"gh-sync: detached #{num} from parent #{parent}")


def _to_backlog(board, repo, num):
    """Return an abandoned card to the backlog station, AFTER its close.

    THE ORDER IS THE WHOLE POINT and is measured, not assumed. Probe #860, 2026-08-25:
    `gh api -X PATCH ... state=closed state_reason=not_planned` moved the card to the done
    station at t+0s, and a `Backlog` write made after that stuck. A write made BEFORE the
    close would be overwritten by GitHub's own workflow, silently.

    Abandoned work is not done work, and the board is the surface the operator reads."""
    if board is None:
        return
    backlog = board["stations"]["backlog"]
    try:
        gh_board.set_station(board, repo, num, backlog)
        print(f"gh-sync: issue #{num} -> {backlog} (abandoned, not done)")
    except gh_board.BoardError as e:
        print(f"gh-sync: ERROR - {e}", file=sys.stderr)


def _abandon_plan(rec):
    """Every write `abandon` would make, in the order `cmd_abandon` performs them, as a list
    of (kind, number, line).

    ONE renderer, called by BOTH paths. The dry run prints these lines prefixed
    `gh-sync: would `; the real run walks the SAME list to decide what it closes. Two
    renderers drift, and the drift here is invisible until it destroys the wrong ticket --
    the operator confirms a list and a different list executes.

    THE PARENT IS LABELLED AS THE PARENT, never as one more number. Under DEC-203 it closes
    UNCONDITIONALLY where it previously turned on where the parent came from, so a reader
    skimming a column of issue numbers has no way to see that the epic is in the list."""
    plan = []
    if rec["parent"] is not None:
        plan.append(("comment", rec["parent"],
                     f"post the abandon reason on parent #{rec['parent']}"))
    for tid, num in sorted(rec["issues"].items()):
        plan.append(("issue", num,
                     f"detach issue #{num} for {tid} from parent "
                     f"#{rec['parent']}, close it (not_planned), label it abandoned and "
                     f"return its card to the backlog"
                     if rec["parent"] is not None else
                     f"close issue #{num} for {tid} (not_planned), label it abandoned and "
                     f"return its card to the backlog"))
    if rec["milestone"] is not None:
        plan.append(("milestone", rec["milestone"],
                     f"close milestone #{rec['milestone']}"))
    if rec["parent"] is not None:
        plan.append(("parent", rec["parent"],
                     f"close parent #{rec['parent']} (not_planned), label it abandoned and "
                     f"return its card to the backlog"))
    return plan


def cmd_abandon(feat_dir, repo, board, reason_file, yes=False):
    """Terminal state: closes every recorded sub-issue and the PARENT `not_planned`, closes
    the milestone, posts the signed reason, and labels everything it closed `abandoned`.

    ABANDON REPORTS AND ASKS. Without `--yes` it prints every write it WOULD make and makes
    none of them, and does not record the status. `--yes` is what executes it.

    THE CONFIRMATION IS THE FLAG AND NOTHING ELSE (DESIGN.md Contract 3). No `isatty()`
    branch, no default-on-no-TTY, no stdin read. No script in this directory calls `input()`,
    and `ship` is already invoked with captured output by `post-merge-sweep.sh`, so a TTY
    prompt would be both a first for this codebase and unanswerable from the sweep.

    THE PARENT CLOSES WHATEVER ITS HISTORY. Where it came from is no longer recorded at all
    (DEC-203 item 4). The operator's confirmation is what replaces the old origin gate, and it
    is a better guard because a human looked at the list. That gate answered "did we create
    this?", which is a fact about the past rather than about the ticket.

    THE DRY RUN EXITS 0, deliberately. Nothing wraps `abandon` today -- its only references in
    the tree are this file's usage line and `github-mirror.md`'s prose -- so no caller can
    misread 0 as "abandoned". If an automated caller is ever written, the dry run needs its
    own exit code at that point, not before.

    AN ABANDONED CARD GOES BACK TO THE BACKLOG, NOT TO DONE, and this is a correction the
    operator made on 2026-08-25. Measured the same day on probe #860: closing an issue moves
    its card to the done station IMMEDIATELY, `not_planned` included. So before this, every
    abandoned ticket landed at Done and the board could not tell dropped work from shipped
    work. The station write therefore runs AFTER the close, deliberately -- measured on the
    same probe, a write after the close sticks, and a write before it is overwritten by
    GitHub's own workflow.

    IT ALSO DETACHES EACH SUB-ISSUE FROM THE PARENT. Under DEC-203 a ticket is open while its
    card is not at the done station, so an abandoned ticket sitting at the backlog reads as
    OPEN -- and `ship` refuses to move a parent that has an open child. Left attached, one
    abandoned child would hold its parent forever, with no way out, because the Bash gate
    refuses a hand close. Detaching is what makes the backlog station safe rather than a trap.
    The ticket survives, labelled and closed, for the operator to clean up later.

    `_record_status(feat_dir, "Abandoned")` stays the LAST STATEMENT of the successful path
    and runs only under `--yes`."""
    reason_file = post_body_path(reason_file, "--reason-file")
    rec = load_recorded(feat_dir)
    if rec["milestone"] is None and not rec["issues"]:
        skip("no recorded milestone or issues — nothing to abandon (was `open` run?)")

    plan = _abandon_plan(rec)

    if not yes:
        for _kind, _num, line in plan:
            print(f"gh-sync: would {line}")
        print("gh-sync: abandon is a decision the operator makes — re-run with --yes to "
              "close the issues listed above")
        return

    ensure_labels(repo, {"abandoned"})

    # NOTHING IN THIS LOOP MAY EXIT, and that is the whole shape of it. Every write used to
    # go through `gh()`, which calls `skip()` -- print `gh-sync: SKIP` and `sys.exit(0)` --
    # on any non-zero return. So a single failed `--add-label` after a SUCCESSFUL close
    # abandoned the run mid-batch: the backlog write never ran, and probe #860 measured that
    # a close moves the card to the DONE station at t+0s, so the dropped ticket came to rest
    # at Done. That is exactly the state DEC-203's backlog rule exists to prevent, reached by
    # the command that implements the rule. `_record_status` never ran either, and every
    # later issue in the batch was left untouched with no report. `gh_try` returns instead.
    failed = []

    def _close_and_reseat(num, what):
        """Close one ticket as not_planned, then put its card back in the backlog.

        THE ORDER IS THE POINT. The close is the one irreversible act, so it goes first and
        its failure costs nothing. The backlog write is the state CORRECTION and follows it
        immediately -- before the label, which is cosmetic by comparison -- so no cosmetic
        failure can leave a card at Done."""
        ok, out = gh_try(["api", "-X", "PATCH", f"repos/{repo}/issues/{num}",
                          "-f", "state=closed", "-f", "state_reason=not_planned"])
        if not ok:
            print(f"gh-sync: ERROR - could not close {what} #{num}: {out}", file=sys.stderr)
            failed.append(num)
            return
        print(f"gh-sync: {what} #{num} closed (not_planned)")
        _to_backlog(board, repo, num)
        ok, out = gh_try(["issue", "edit", str(num), "--repo", repo,
                          "--add-label", "abandoned"])
        if not ok:
            print(f"gh-sync: ERROR - #{num} closed but not labelled `abandoned`: {out}",
                  file=sys.stderr)

    for kind, num, _line in plan:
        if kind == "comment":
            ok, out = gh_try(["issue", "comment", str(num), "--repo", repo,
                              "--body-file", reason_file])
            if ok:
                print(f"gh-sync: reason posted on parent #{num}")
            else:
                print(f"gh-sync: ERROR - reason not posted on parent #{num}: {out}",
                      file=sys.stderr)
        elif kind == "issue":
            if rec["parent"] is not None:
                _detach_from_parent(repo, rec["parent"], num)
            _close_and_reseat(num, "issue")
        elif kind == "milestone":
            ok, out = gh_try(["api", "-X", "PATCH", f"repos/{repo}/milestones/{num}",
                              "-f", "state=closed"])
            if ok:
                print(f"gh-sync: milestone #{num} closed")
            else:
                print(f"gh-sync: ERROR - milestone #{num} not closed: {out}",
                      file=sys.stderr)
        elif kind == "parent":
            _close_and_reseat(num, "parent")

    if failed:
        nums = ", ".join(f"#{n}" for n in failed)
        print(f"gh-sync: FAILED {len(failed)} of {len(plan)} — {nums} did not close and "
              f"nothing downstream reports it")

    if rec["parent"] is None:
        print("gh-sync: no parent recorded — reason not posted")
    if rec["milestone"] is None:
        print("gh-sync: no milestone recorded — nothing to close")

    # LAST STATEMENT of the successful path (T-01/FEAT-23) — structural, not re-gated on
    # the milestone check above (that guard is a conjunction with the issues check, not
    # this write's business). Reaching here already proves `skip()` did not fire.
    _record_status(feat_dir, "Abandoned")


def cmd_backlog(feat_dir, repo, items):
    """User-accepted residual findings -> plain backlog issues (DEC-138 am.4).

    Called by the MAIN SESSION after the briefing decision, with one arg per accepted
    residual as `nature:title` (nature: bug|chore|enhancement). No milestone — these
    belong to no feature yet; a later plan cycle may absorb them. This is the only
    entry point for findings: digests never write to GitHub directly.
    """
    feat = os.path.basename(os.path.abspath(feat_dir))
    for item in items:
        nature, _, title = item.partition(":")
        if nature not in ("bug", "chore", "enhancement") or not title.strip():
            die(f"backlog item must be nature:title (bug|chore|enhancement), got {item!r}")
        labels = ["harness"] + ([nature] if nature != "enhancement" else [])
        args = ["issue", "create", "--repo", repo, "--title", title.strip(),
                "--body", f"Residual finding from {feat}, accepted at the ship briefing."]
        for l in labels:
            args += ["--label", l]
        url = gh(args)
        print(f"gh-sync: backlog issue #{url.rstrip('/').rsplit('/', 1)[-1]} [{', '.join(labels)}] — {title.strip()}")


def cmd_ship(feat_dir, repo, board, body_file=None, pr_arg=None):
    """Terminal state: lands every recorded card at the board's DONE STATION, and closes no
    issue at all. GitHub's own `Auto-close issue` workflow turns each station write into a
    close (DEC-203 items 1-4). Measured on board 3 on 2026-08-25: probe #847 moved to `Done`
    at 19:06:14Z and read CLOSED at 19:06:20Z.

    THE OPEN-CHILD TEST APPLIES TO `source_issues` AND THE PARENT ONLY, and the exemption for
    the task sub-issues is DECIDED, not omitted (D-10). REQ-03 states the rule unconditionally,
    so a later reader has to be able to see why this group is out of it. `cmd_open` is the only
    writer of `rec["issues"]`, and it creates each sub-issue FLAT, with no sub-issue of its own,
    so that group's recursion has depth 1 BY CONSTRUCTION. Checking each would add one
    `sub_issues` read per task sub-issue -- thirteen extra network calls on FEAT-34's
    acceptance run -- to prove a set that is empty by construction.

    THE MILESTONE PATCH STAYS. A milestone is not a card and has no station, so closing it is
    still the only way to record it finished.

    FAILURE POSTURE, unchanged (DEC-146): best-effort per card. A `BoardError` on one card
    prints one stderr line and the loop continues, the exit status stays 0, and there is no
    transaction across N `project_field_set` calls. git ignores a post-merge hook's exit status
    anyway, which is why `post-merge-sweep.sh` greps this function's OUTPUT rather than its exit
    code.

    ORDER: `_record_pr` runs before `_record_status(feat_dir, "Done")`, and that status write
    stays the LAST STATEMENT of the successful path (T-01/FEAT-23) -- `skip()` calls
    `sys.exit(0)`, so reaching it is itself the proof no early-exit branch fired."""
    if body_file is not None:
        body_file = post_body_path(body_file, "--body-file")
    rec = load_recorded(feat_dir)
    if rec["milestone"] is None:
        skip("no recorded milestone — nothing to close")

    # The comment is UNCONDITIONAL: posts on any recorded parent whatever its origin.
    if body_file is not None and rec["parent"] is not None:
        gh(["issue", "comment", str(rec["parent"]), "--repo", repo,
            "--body-file", body_file], capture=False)
        print(f"gh-sync: ship review posted on parent #{rec['parent']}")

    if board is None:
        print("gh-sync: no board configured — no card was moved")
        _ship_close_milestone(feat_dir, repo, rec, pr_arg)
        return

    done = board["stations"]["done"]

    # Step 2 — the three groups, in the order they are written.
    children = sorted(rec["issues"].values())
    sources = list(rec["source_issues"])
    parents = [rec["parent"]] if rec["parent"] is not None else []

    # Step 3 — ONE targeted, cost-1 board read for every card's current station.
    try:
        stations = gh_board.board_stations(board, repo)
    except Exception as e:  # factory_gh.GhError and anything it wraps
        print(f"gh-sync: ERROR - board read failed, no card moved: {e}", file=sys.stderr)
        stations = None

    held = []      # (card number, the child that held it)
    failed = []    # card numbers whose station write failed

    def write_done(num):
        """Write one card's done station and, ON SUCCESS, REFRESH THE MAP IN PLACE.

        The refresh lives HERE, in the one helper every write site goes through, rather than
        after step 4's loop, so no future write site can forget it. It is not a tidiness
        point: a `source_issues` entry can itself be a child of the parent, or of a source
        evaluated later in the same pass. A map refreshed only for step 4's writes would still
        read such a card as open and skip a parent that should have landed."""
        try:
            gh_board.set_station(board, repo, num, done)
        except gh_board.BoardError as e:
            print(f"gh-sync: ERROR - {e}", file=sys.stderr)
            failed.append(num)
            return False
        if stations is not None:
            stations[int(num)] = done
        print(f"gh-sync: issue #{num} -> {done}")
        return True

    # Step 4 — the task sub-issues. No child check: see the docstring's D-10 paragraph.
    for num in children:
        write_done(num)

    def first_open_child(num):
        """(child number, parenthetical) for the LOWEST-numbered open child, or None.

        Raises on a failed `sub_issues` read: an UNKNOWN child set is never treated as
        childless, because that is the one error that would close someone else's live epic.

        A child counts as OPEN when its card is not at the done station. Both of
        `gh_board.read_station`'s failure reasons count as open, and they are DISTINGUISHED in
        the parenthetical so the operator can tell an unstationed child from a missing one
        without running a second command."""
        ok, raw = gh_try(sub_issues_args(repo, num))
        if not ok:
            raise RuntimeError(raw)
        kids = json.loads(raw) if raw and raw.strip() else []
        numbers = sorted(int(k["number"]) for k in kids
                         if isinstance(k, dict) and k.get("number") is not None)
        for kid in numbers:
            station, reason = gh_board.read_station(stations or {}, kid)
            if station == done:
                continue
            note = "not on the board" if reason == "not on the board" else f"not at {done}"
            return (kid, note)
        return None

    # Step 5 — the source issues, then the parent. Only after step 4, so a parent whose only
    # open children are cards THIS RUN lands can still reach done in this run.
    for num in sources + parents:
        if stations is None:
            print(f"gh-sync: ERROR - #{num} not evaluated, the board read failed",
                  file=sys.stderr)
            failed.append(num)
            continue
        try:
            blocker = first_open_child(num)
        except Exception as e:
            # SAME BUCKET as the board-read failure four lines above, and for the same
            # reason: this card did not reach done, and nothing downstream reports it. An
            # earlier cut printed and continued WITHOUT recording it, so the run exited 0
            # with no `FAILED` line -- which post-merge-sweep.sh reads as a clean ship and
            # removes the worktree on. A network blip on one child list would have left the
            # ticket open and said nothing.
            print(f"gh-sync: ERROR - #{num} child list unreadable, card not moved: {e}",
                  file=sys.stderr)
            failed.append(num)
            continue
        if blocker is not None:
            kid, note = blocker
            print(f"gh-sync: HELD — #{num} waiting on open child #{kid} ({note})")
            held.append((num, kid))
            continue
        write_done(num)

    # Step 7 — the batch summary. TWO LINES, never one merged list.
    total = len(children) + len(sources) + len(parents)
    if held:
        pairs = ", ".join(f"#{n} (child #{c})" for n, c in held)
        print(f"gh-sync: HELD {len(held)} of {total} — {pairs}")
    if failed:
        names = ", ".join(f"#{n}" for n in failed)
        print(f"gh-sync: FAILED {len(failed)} of {total} — {names} did not reach Done and "
              f"nothing downstream reports it")
    if not held and not failed:
        print(f"gh-sync: every recorded card is at {done}")

    # Step 7c — REQ-06's compensating control (D-13). Runs ONCE per feature, HERE and nowhere
    # else, and AFTER every station write of this run, so a card this run moved to done does
    # not report itself as a STATION finding.
    #
    # WHY HERE. The Bash gate cannot see a close typed in another terminal or made in the web
    # UI, and this audit's STATION class is the only detector of what such a close leaves
    # behind. Running it at each station write was rejected: the leak happens when the harness
    # is NOT writing a station, so a station-change trigger catches it no sooner in practice,
    # at several times the cost.
    #
    # SHIP NEVER GATES ON THE AUDIT. A read failure means the audit COULD NOT RUN, which is
    # not a failed write: one stderr line, and the ship carries on at exit 0.
    _ship_audit(repo)

    _ship_close_milestone(feat_dir, repo, rec, pr_arg)


def _ship_audit(repo):
    """Run the board audit and print each finding under ship's own prefix.

    No audit line may carry the substring `gh-sync: SKIP` or `gh-sync: FAILED`.
    `post-merge-sweep.sh` greps ship's combined output for both, and an audit finding is
    neither an environmental no-go nor a failed write -- a line carrying either literal would
    silently change worktree behaviour on a healthy run."""
    try:
        findings = board_lifecycle.audit_findings(repo)
    except Exception as e:
        print(f"gh-sync: ERROR - the board audit could not run: {e}", file=sys.stderr)
        return
    for f in findings:
        print(f"gh-sync: audit — {f.message}")
    print(f"gh-sync: audit — {len(findings)} finding(s)")


def _ship_close_milestone(feat_dir, repo, rec, pr_arg):
    """The tail every ship path shares: the milestone PATCH, then the pr, then the terminal
    status. A milestone is not a card, so it is closed rather than stationed."""
    gh(["api", "-X", "PATCH", f"repos/{repo}/milestones/{rec['milestone']}",
        "-f", "state=closed"])
    print(f"gh-sync: milestone #{rec['milestone']} closed")

    # T-03 (FEAT-26): recorded BEFORE the terminal status write, never after — that final
    # write must remain the LAST STATEMENT of the successful path (T-01/FEAT-23).
    _record_pr(feat_dir, repo, pr_arg)

    # LAST STATEMENT of the successful path (T-01/FEAT-23) — structural, not re-gated on
    # the milestone check above. Reaching here already proves `skip()` did not fire.
    _record_status(feat_dir, "Done")


def main():
    # Review finding 1: the module's documented gate had ZERO production callers,
    # so a missing PyYAML surfaced as a raw traceback instead of INSTALL_COMMAND.
    # First statement, before any parse can be attempted.
    harness_yaml.require_or_die()
    argv = sys.argv[1:]
    parent_arg = None
    if "--parent" in argv:
        i = argv.index("--parent")
        if i + 1 >= len(argv):
            die("--parent needs a value")
        parent_arg = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    reason_file = None
    if "--reason-file" in argv:
        i = argv.index("--reason-file")
        if i + 1 >= len(argv):
            die("--reason-file needs a value")
        reason_file = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    body_file = None
    if "--body-file" in argv:
        i = argv.index("--body-file")
        if i + 1 >= len(argv):
            die("--body-file needs a value")
        body_file = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    pr_arg = None
    if "--pr" in argv:
        i = argv.index("--pr")
        if i + 1 >= len(argv):
            die("--pr needs a value")
        pr_arg = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
        # MF-1: a non-numeric --pr is a caller mistake at the PARSE boundary, not an
        # uncaught ValueError from int(pr_arg) inside _record_pr — fixing it here keeps
        # _record_pr's own never-die contract (T-03) intact for its internal callers
        # (cmd_ship).
        try:
            int(pr_arg)
        except ValueError:
            die(f"--pr needs an integer, got {pr_arg!r}")
    # STRIPPED BY NAME-SEARCH, BEFORE THE POSITIONAL PARSE, exactly as the four flags above
    # are. It takes NO VALUE, so this removes one element rather than two. Without the strip,
    # `abandon --yes <dir>` reads `--yes` as the feature directory and dies with "--yes is not
    # a directory" -- at precisely the moment the operator is being careful. Both orders must
    # behave identically, and that is its own test assertion.
    yes_flag = False
    if "--yes" in argv:
        i = argv.index("--yes")
        yes_flag = True
        argv = argv[:i] + argv[i + 1:]
    if len(argv) < 2:
        die("usage: gh-sync.py open|start-task|abandon|ship|backlog|record-pr|"
            "status "
            "<feature-dir> [T-NN | nature:title ... | <Status>] [--parent <n>] "
            "[--reason-file <path>] [--body-file <path>] [--pr <n>] [--yes]")
    cmd, feat_dir = argv[0], argv[1]
    # A flag that silently does nothing teaches the operator it is harmless everywhere, and
    # the next place they try it is the one that closes tickets. It is a caller error.
    if yes_flag and cmd != "abandon":
        die(f"--yes is only accepted by abandon, not {cmd!r}")
    if not os.path.isdir(feat_dir):
        die(f"{feat_dir} is not a directory")
    # DEPTH-AGNOSTIC ROOT (FEAT-21 T-10): the old three-level climb was right for
    # .harness/features/<FEAT> and wrong for .harness/<repo>/features/<FEAT> — and a
    # fixed depth is wrong for one of the two in every era. Walk UP from the feature
    # dir to the first ancestor holding the MANIFEST, .harness/team-config.yaml —
    # the established root-probe convention (check-plan-routes.py probes exactly
    # this file, and harness_boundary.py calls it "this hook's probe"), enforced by
    # test-check-plan-routes.py case_20 so every walk-up agrees on what proves a
    # directory is a harness root. An onboarded tree always carries the manifest;
    # harness.json is then read (or skipped over, loudly) by load_config from the
    # resolved root. If no ancestor qualifies, fall back to the old arithmetic so
    # an un-onboarded tree still reaches skip() with the message it prints today.
    _abs = os.path.abspath(feat_dir)
    _d = _abs
    while (not os.path.isfile(os.path.join(_d, ".harness", "team-config.yaml"))
           and _d != os.path.dirname(_d)):
        _d = os.path.dirname(_d)
    if os.path.isfile(os.path.join(_d, ".harness", "team-config.yaml")):
        root = _d
    else:
        # today's behaviour, three parents up — spelled via dirname so the verify's
        # assertion (no fixed join-climb as the PRIMARY derivation) stays meaningful
        root = os.path.dirname(os.path.dirname(os.path.dirname(_abs)))
    try:
        repo, board = load_config(root)
    except factory_config.FleetError as e:
        # An unusable board declaration is a LOUD failure of the whole invocation (D-01,
        # D-02, D-07) — never a printed note followed by business as usual. Exit code 2
        # matches board-station.py's pinned value and factory_cli.EXIT_REFUSED's wider
        # convention for exactly this class of expected refusal; die() (exit 1) and
        # skip() (exit 0) are both wrong here, the first because this is not a caller
        # mistake in the dispatch and the second because an unusable config must not
        # read as an environmental precondition. str(e) is printed verbatim — it is
        # already built by factory_cli.body(what, value, next_step), so composing a
        # new line would drop the next_step that tells the operator what to do.
        print(f"gh-sync: {e}", file=sys.stderr)
        sys.exit(2)
    if cmd == "open":
        cmd_open(feat_dir, repo, parent_arg)
    elif cmd == "start-task":
        if len(argv) < 3:
            die("start-task needs a T-NN")
        cmd_start_task(feat_dir, argv[2], repo, board)
    elif cmd == "abandon":
        cmd_abandon(feat_dir, repo, board, reason_file, yes_flag)
    elif cmd == "ship":
        cmd_ship(feat_dir, repo, board, body_file, pr_arg)
    elif cmd == "backlog":
        if len(argv) < 3:
            die("backlog needs at least one nature:title item")
        cmd_backlog(feat_dir, repo, argv[2:])
    elif cmd == "record-pr":
        _record_pr(feat_dir, repo, pr_arg)
    elif cmd == "status":
        if len(argv) < 3:
            die("status needs a Status value")
        cmd_status(feat_dir, argv[2], repo, board)
    else:
        die(f"unknown command {cmd!r}")


if __name__ == "__main__":
    main()
