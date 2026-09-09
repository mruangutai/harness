#!/usr/bin/env python3
"""check-domain.sh: approval-gated writes to a plan or a brief.

Slice of the former test-check-domain.py (issue #1527) — T-09's plan/brief approval
denials across every write route, T-14's main_session.writes exclusion and FEAT-51's
orphan-write quarantine. Issue #1304's claim-set guard, which shared this section but
not this surface, is test-check-domain-claims.py. Shared fixtures and the block driver
live in check_domain_support.py.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json, os, shutil, subprocess, sys, tempfile

# The station value a legal plan carries, and one that is not in the vocabulary at all. The
# LEGAL word is read from factory_config rather than typed, so this fixture cannot drift from
# the declaration the way a six-key mapping once did (FEAT-41 T-01).
import factory_config as _fc09
from check_domain_support import (FIXTURE_MANIFEST, HERE, HOOK, ROOT, _env, _fire_edit,
    _legal_feature_json, drive, fire_post, fixture)


# ---------------------------------------------------------------------------
# T-14 — the approval exclusion, sourced from main_session.writes (D-10).
# Every case gets its OWN fixture root. Each asserts the exit code AND a
# distinguishing string, so a crash cannot satisfy it.
# ---------------------------------------------------------------------------

T14 = []


def t14(name, ok, detail=""):
    T14.append((name, ok, detail))


# harness-pm and harness-orchestrator must be GRANTED these paths, or every case below
# is an ordinary DOMAIN denial that never reaches the approval guard and the suite reports
# exit 2 for the wrong reason. FEAT-31 T-15 hit this exact trap with this exact fixture.
APPROVAL_MANIFEST = FIXTURE_MANIFEST.replace(
    "shared:\n",
    "  - name: plan\n"
    "    members:\n"
    "      - name: harness-pm\n"
    "        domain:\n"
    "          - { path: .harness/*/features/*/plan.yaml, upsert: true }\n"
    "          - { path: .harness/*/features/*/BRIEF.md, upsert: true }\n"
    "          - { path: .harness/*/features/*/PLAN.md, upsert: true }\n"
    "      - name: harness-orchestrator\n"
    "        domain:\n"
    "          - { path: .harness/*/features/**, upsert: true }\n"
    "          - { path: .harness/logs/**, upsert: true }\n"
    "main_session:\n"
    "  writes:\n"
    '    - ".harness/*/features/*/BRIEF.md ## Approval"\n'
    '    - ".harness/*/features/*/PLAN.md ## Approval"\n'
    '    - ".harness/*/features/*/plan.yaml approval:"\n'
    '    - ".harness/logs/**"\n'
    "shared:\n"
    "  - { path: .harness/*/features/*/quarantine/** }\n")


PLAN_ON_DISK = (
    "schema: plan/1\n"
    "feature: FEAT-99-fixture\n"
    "\n"
    "approval:\n"
    "  status: pending\n"
    "  approved_by: <name>\n"
    "  date: <YYYY-MM-DD>\n"
    "\n"
    "tasks:\n"
    "  - id: T-01\n"
    "    change_type: logic\n"
    "    status: pending\n"
    "  - id: T-02\n"
    "    change_type: logic\n"
    "    status: pending\n")


BRIEF_ON_DISK = (
    "# Brief\n"
    "\n"
    "## Goal\n"
    "\n"
    "Do the thing.\n"
    "\n"
    "## Approval\n"
    "\n"
    "status: pending\n"
    "approved-by: <name>\n")


REL_PLAN = ".harness/harness/features/FEAT-99-fixture/plan.yaml"


REL_BRIEF = ".harness/harness/features/FEAT-99-fixture/BRIEF.md"


REL_PLANMD = ".harness/harness/features/FEAT-99-fixture/PLAN.md"


MARK = "may not change"


def _approval_root(manifest_text=None, rel=REL_PLAN, body=PLAN_ON_DISK):
    root = fixture(APPROVAL_MANIFEST if manifest_text is None else manifest_text)
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(body)
    return root, full


def _fire_write(root, full, content, agent="harness-pm"):
    payload = {"agent_type": agent, "tool_name": "Write",
               "tool_input": {"file_path": full, "content": content}}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def t09(name, ok, detail=""):
    global _T09_FAILS
    if ok:
        print(f"ok    {name}")
    else:
        _T09_FAILS += 1
        print(f"FAIL  {name}\n      {detail}")
    return ok


_T09_FAILS = 0


_PLAN_LEGAL = (
    "schema: plan/1\n"
    "feature: FEAT-99-fixture\n"
    f"status: {_fc09.MANDATED_STATIONS[3]}\n"
    "tasks:\n"
    "  - id: T-01\n"
    f"    status: {_fc09.MANDATED_STATIONS[5]}\n"
    "    verify: python3 test.py\n"
    # T-02 IS DELIBERATELY NOT TERMINAL. T-01 is `done`, and under FEAT-54's B-1 satisfaction
    # rule a handoff whose every authority is already satisfied binds nothing and is refused —
    # so a fixture handoff citing T-01 alone reds for a reason its own case never names. Any
    # case here that needs a LEGAL handoff body cites T-02.
    "  - id: T-02\n"
    f"    status: {_fc09.MANDATED_STATIONS[3]}\n"
    "    verify: python3 test.py\n"
)


_PLAN_ILLEGAL = _PLAN_LEGAL.replace(
    f"    status: {_fc09.MANDATED_STATIONS[5]}", "    status: Sideways")


# A plan with NO top-level status at all — the UN-MIGRATED shape the sweep meets while T-07 is
# pending. T-09 and T-07 are unordered, so this must be LEGAL or the sweep reports every plan
# that has not been migrated yet.
_PLAN_NO_TOP = "\n".join(l for l in _PLAN_LEGAL.splitlines()
                          if not l.startswith("status:")) + "\n"


# FEAT-41 T-09's cases, SPLIT BY CASE GROUP (FEAT-41 F-05). This began as one `run_t09` and grew
# a case group per finding until it graded 1 against a test bar of 3, driven by ABC alone — 61.1
# worth of fixture calls in one body, with cyclomatic at 7 and cognitive at 6. Nothing here was
# hard to read line by line; there was simply too much of it in one place. The groups are the
# ones the numbered comments already named, so the split follows a boundary the file had.
#
# THEY SHARE `t09()`, which counts into the module-level tally, so each group asserts freely and
# only the aggregator resets and reports.
def _t09_edit_denial():
    """1. THE EDIT ROUTE IS DENIED, and the message routes the reader to the verb."""

    # ---- 1. THE EDIT ROUTE IS DENIED, and the message routes the reader to the verb -------
    root, full = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    r = _fire_edit(root, full, "T-01", "T-02", agent="harness-orchestrator")
    t09("T-09 1: an AGENT's Edit of plan.yaml is DENIED", r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")
    err = r.stderr
    t09("T-09 1: the denial names set-task-station — the write an agent will actually attempt",
        "set-task-station" in err, f"stderr={err[:400]!r}")

    # THE REASON CLAUSE IS LOAD-BEARING, NOT DECORATION. A denial that says only what to use
    # instead is indistinguishable from a stuck or over-broad gate, and a reader who takes it
    # for a harness malfunction routes around it through a shell write of a legal value — the
    # one channel the sweep admits it cannot attribute to an author.
    t09("T-09 1: the denial STATES THE REASON — one writer, because stations are validated "
        "before they land",
        "one writer" in err.lower() and "validate" in err.lower(),
        f"stderr={err[:400]!r}")

    # THE BASENAME IS THE ONE ON DISK, read from the bin directory rather than retyped.
    t09("T-09 1: the denial names the writer script by the basename that EXISTS on disk",
        "plan-merge.py" in err and os.path.isfile(os.path.join(HERE, "plan-merge.py")),
        f"stderr={err[:400]!r}")

    # ONE ROUTING SENTENCE PER FINDING. deny() appends the module-level ROUTING constant,
    # which speaks about STATE.md, digests and notes/ — a different file class entirely.
    # Emitting it beside a plan.yaml refusal puts two contradictory routing sentences in one
    # stderr stream. Asserted by a distinctive substring of that constant.
    t09("T-09 1: the denial does NOT carry the STATE.md ROUTING sentence",
        "STATE.md" not in err, f"stderr={err[:400]!r}")


def _t09_binds_every_author():
    """2-4. Every author is bound, both write routes are denied, and a sibling is not."""

    # ---- 2. THE MAIN SESSION IS DENIED TOO ------------------------------------------------
    # DEC-180 makes the shape gate independent of domain and binding on EVERY author. The
    # domain region would have been the wrong home precisely because check-domain exits 0 for
    # a payload with no agent_type, which would exempt the one author most likely to hand-edit.
    root2, full2 = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    r2 = _fire_edit(root2, full2, "T-01", "T-02", agent=None)
    t09("T-09 2: an Edit with NO agent_type is denied too — the shape gate binds every author",
        r2.returncode == 2, f"exit {r2.returncode}, stderr={r2.stderr.strip()[:300]!r}")

    # ---- 3. THE WRITE ROUTE IS DENIED -----------------------------------------------------
    root3, full3 = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    r3 = _fire_write(root3, full3, _PLAN_LEGAL, agent="harness-orchestrator")
    t09("T-09 3: a Write of plan.yaml is DENIED", r3.returncode == 2,
        f"exit {r3.returncode}, stderr={r3.stderr.strip()[:300]!r}")

    # ---- 4. NEGATIVE CONTROL: a SIBLING file in the same directory is untouched -----------
    # Without this the whole group passes against a gate that denies the feature directory.
    root4, _ = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    brief = os.path.join(root4, REL_BRIEF)
    os.makedirs(os.path.dirname(brief), exist_ok=True)
    with open(brief, "w") as f:
        f.write(BRIEF_ON_DISK)
    r4 = _fire_edit(root4, brief, "Goal", "Goal", agent="harness-orchestrator")
    t09("T-09 4: NEGATIVE CONTROL — BRIEF.md beside it is NOT denied by this rule",
        r4.returncode != 2 or "set-task-station" not in r4.stderr,
        f"exit {r4.returncode}, stderr={r4.stderr.strip()[:300]!r}")


def _t09_post_sweep():
    """5-7. What a shell write LANDS is read after the fact, and an un-migrated plan is legal."""

    # ---- 5. THE POST SWEEP'S VOCABULARY RULE ----------------------------------------------
    # A shell write cannot be denied before the fact, so the sweep reads what LANDED. It
    # catches a dead word or a broken file; it CANNOT catch a shell write of a legal value,
    # because it reads disk and cannot attribute an author.
    def _bash_sweep(body):
        root_s, full_s = _approval_root(rel=REL_PLAN, body=body)
        payload = {"agent_type": "harness-orchestrator", "tool_name": "Bash",
                   "hook_event_name": "PostToolUse",
                   "tool_input": {"command": "sed -i '' s/a/b/ " + full_s}}
        return fire_post(root_s, payload)

    r5 = _bash_sweep(_PLAN_ILLEGAL)
    t09("T-09 5: a Bash write landing an ILLEGAL station value is REPORTED by the post sweep",
        r5.returncode == 2 and "Sideways" in r5.stderr,
        f"exit {r5.returncode}, stderr={r5.stderr.strip()[:400]!r}")
    t09("T-09 5: and the report names the FILE as well as the offending value",
        "plan.yaml" in r5.stderr, f"stderr={r5.stderr.strip()[:400]!r}")

    r6 = _bash_sweep(_PLAN_LEGAL)
    t09("T-09 6: NEGATIVE CONTROL — a Bash write landing a LEGAL station value is NOT reported",
        r6.returncode == 0, f"exit {r6.returncode}, stderr={r6.stderr.strip()[:400]!r}")

    # ---- 7. AN UN-MIGRATED PLAN IS LEGAL --------------------------------------------------
    # T-07 adds the top-level key and is NOT a dependency of T-09, so the two are unordered.
    # A rule that REQUIRED the key would report a violation on every plan the sweep meets
    # before T-07 lands. An absent TASK status is legal for the same reason: T-04 leaves it
    # out of REQUIRED_TASK_FIELDS and an absent one reads as the not-started station.
    r7 = _bash_sweep(_PLAN_NO_TOP)
    t09("T-09 7: a plan.yaml carrying NO top-level status is NOT reported — the un-migrated "
        "shape is legal",
        r7.returncode == 0, f"exit {r7.returncode}, stderr={r7.stderr.strip()[:400]!r}")


def _t09_spelling():
    """8. The spelling of the filename is not a route (FEAT-41 F-04)."""

    # ---- 8. THE SPELLING OF THE FILENAME IS NOT A ROUTE (FEAT-41 F-04) --------------------
    # Panel finding F-04, high. RE_PLAN_YAML matched lowercase only, and this workstation's
    # filesystem is case-INSENSITIVE: measured, `echo x > Plan.yaml` overwrites plan.yaml and
    # reports the SAME INODE. So `Plan.yaml` was a write to the real plan that the route denial
    # did not see, and it exited 0 with no stderr at all.
    #
    # HALF OF THE FINDING DID NOT REPRODUCE, and this paragraph WAS TOO WIDE WHEN FIRST WRITTEN
    # -- cycle 1's panel found the hole it had talked past, so it is corrected here rather than
    # deleted, because the wrong version is what a reader would otherwise trust.
    #
    # STILL TRUE: replacing shape-matching WITH realpath would WEAKEN the gate. `./` prefix, a
    # `notes/..` traversal, a doubled slash, an absolute path and a SYMLINKED FEATURE DIRECTORY
    # are all denied already, because the path as written still ends `[^/]+/plan.yaml` and the
    # pattern matches SHAPE. Where such a path resolves is irrelevant.
    #
    # WHAT WAS WRONG: "even a symlinked feature directory" was read as covering symlinks in
    # general, and it does not. A symlinked FILE is the opposite shape -- `notes/innocent.md ->
    # plan.yaml` is innocent at every component, so no pattern matches what was typed, while the
    # write lands in the plan. Case 9 below closes that, by ADDING resolved candidates to the
    # shape test rather than substituting resolution for it.
    #
    # THE FIX DENIES ON A CASE-SENSITIVE FILESYSTEM TOO, where `Plan.yaml` is a genuinely
    # different file. That asymmetry is deliberate: a loud refusal of a file nobody legitimately
    # writes is a far better error than a silent bypass of the one write denial in this gate.
    for spelling in ("Plan.yaml", "PLAN.YAML", "plan.YAML"):
        rel8 = f".harness/harness/features/FEAT-99-fixture/{spelling}"
        root8, full8 = _approval_root(rel=rel8, body=_PLAN_LEGAL)
        r8 = _fire_write(root8, full8, _PLAN_LEGAL, agent="harness-orchestrator")
        t09(f"T-09 8 / F-04: a Write of {spelling} is DENIED — on a case-insensitive "
            f"filesystem it lands on the same inode as plan.yaml",
            r8.returncode == 2, f"exit {r8.returncode}, stderr={r8.stderr.strip()[:300]!r}")

    # NEGATIVE CONTROL. Case-folding the plan pattern must not swallow a sibling whose name
    # merely contains it -- `plan.yaml.bak` and `myplan.yaml` are not the plan.
    for benign in ("plan.yaml.bak", "myplan.yaml"):
        rel8b = f".harness/harness/features/FEAT-99-fixture/{benign}"
        root8b, full8b = _approval_root(rel=rel8b, body=_PLAN_LEGAL)
        r8b = _fire_write(root8b, full8b, _PLAN_LEGAL, agent="harness-orchestrator")
        t09(f"T-09 8 NEGATIVE CONTROL: {benign} is still ALLOWED — the rule is anchored, not "
            f"a substring match",
            r8b.returncode == 0, f"exit {r8b.returncode}, stderr={r8b.stderr.strip()[:300]!r}")


def _t09_symlink():
    """9. A symlink is a route, and its name is not (FEAT-41 H-01)."""

    # ---- 9. A SYMLINK IS A ROUTE, AND ITS NAME IS NOT (FEAT-41 H-01) ----------------------
    # Cycle 1's panel, high, and it is the half of F-04 that case 8 above dismissed TOO WIDELY.
    # Case 8 says a symlinked feature DIRECTORY is already denied, which is true and stays
    # true: the written path still ends `<something>/plan.yaml`, so the shape match sees it.
    #
    # A SYMLINKED FILE IS THE OPPOSITE SHAPE. `notes/innocent.md -> plan.yaml` is a path whose
    # spelling is innocent at every component, so no pattern can match it, while the write
    # lands in plan.yaml. MEASURED BOTH HALVES before fixing:
    #   this runtime's Write tool follows a symlink -- the link stayed a link and the TARGET's
    #     bytes changed, so the route is real and not theoretical
    #   plan.yaml -> exit 2 DENIED; innocent.md -> exit 0 ALLOWED
    # That is a forged approval through a path every squad member is already granted.
    #
    # WHY SHAPE-MATCHING THE TARGET IS NOT THE REALPATH FIX CASE 8 REFUSED. Case 8 refused to
    # replace shape-matching WITH realpath, because resolution would have weakened `./`, `..`,
    # doubled slashes and absolute paths, all of which the shape already denies. This ADDS the
    # resolved target as a second thing to shape-match. Nothing denied today becomes allowed.
    root9, full9 = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                  body=_PLAN_LEGAL)
    link_abs = os.path.join(root9, ".harness", "harness", "features", "FEAT-99-fixture",
                            "notes", "innocent.md")
    os.makedirs(os.path.dirname(link_abs), exist_ok=True)
    os.symlink(os.path.join("..", "plan.yaml"), link_abs)

    r9 = _fire_write(root9, link_abs, _PLAN_LEGAL, agent="harness-orchestrator")
    t09("T-09 9: a Write to a SYMLINK whose name is not plan.yaml is DENIED — the write lands "
        "in the plan, so the link is a route",
        r9.returncode == 2, f"exit {r9.returncode}, stderr={r9.stderr.strip()[:300]!r}")
    # AND THE REFUSAL NAMES THE REAL FILE, not only the link the author typed. A denial that
    # says `innocent.md` is not a route would read as a malfunction -- the exact failure the
    # reason clause in the production denial exists to prevent.
    #
    # ASSERTED ON THE RESOLVED PATH, NOT THE WORD `plan.yaml`. The denial's own prose contains
    # "plan.yaml has exactly ONE writer" whatever it refuses, so a bare substring check would
    # have passed vacuously -- it would have gone green against a message naming only the link.
    t09("T-09 9: the refusal names the feature's plan.yaml, the file the write would reach",
        ".harness/harness/features/FEAT-99-fixture/plan.yaml" in r9.stderr,
        f"stderr={r9.stderr.strip()[:300]!r}")
    # NEGATIVE CONTROL. A symlink pointing at something that is NOT the plan stays allowed --
    # the rule follows the link to a shape test, it does not refuse links as a class.
    root9b, _full9b = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                     body=_PLAN_LEGAL)
    ord_abs = os.path.join(root9b, ".harness", "harness", "features", "FEAT-99-fixture",
                           "notes", "ordinary.md")
    os.makedirs(os.path.dirname(ord_abs), exist_ok=True)
    # THE TARGET CARRIES NO RULES OF ITS OWN, deliberately. Pointing it outside the feature
    # trips the DOMAIN rule and pointing it at BRIEF.md trips that file's `## Approval` shape
    # rule — either way the case would pass for a reason that has nothing to do with routes.
    real_abs = os.path.join(root9b, ".harness", "harness", "features", "FEAT-99-fixture",
                            "notes", "real.md")
    with open(real_abs, "w") as _f:
        _f.write("# note\n")
    os.symlink("real.md", ord_abs)
    r9b = _fire_write(root9b, ord_abs, "# note\n", agent="harness-orchestrator")
    t09("T-09 9 NEGATIVE CONTROL: a symlink to a file that is not the plan is still ALLOWED — "
        "links are followed to a shape test, not refused as a class",
        r9b.returncode == 0, f"exit {r9b.returncode}, stderr={r9b.stderr.strip()[:300]!r}")

    # AND THE POST REPORTER CLASSIFIES BY WHERE THE WRITE LANDED. POST opens the path, which
    # follows the link, so it read the plan's bytes and then looked up rules under the link's
    # innocent name and found none. PRE now refuses this route for every editor tool, so this
    # case defends the REPORTING side against drifting away from the denial beside it.
    root9c, _f9c = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                  body=_PLAN_LEGAL)
    post_link = os.path.join(root9c, ".harness", "harness", "features", "FEAT-99-fixture",
                             "notes", "innocent.md")
    os.makedirs(os.path.dirname(post_link), exist_ok=True)
    os.symlink(os.path.join("..", "plan.yaml"), post_link)
    # An ILLEGAL station value, landed through the link, is what the vocabulary net must see.
    _plan9c = os.path.join(root9c, ".harness", "harness", "features", "FEAT-99-fixture",
                           "plan.yaml")
    with open(_plan9c, "w") as _f:
        _f.write(_PLAN_LEGAL.replace("status: building", "status: Sideways"))
    # THE NAMED-FILE POST BRANCH, not the Bash glob sweep. The sweep finds plan.yaml by GLOB, so
    # it catches a landed illegal value whatever route reached it; this branch is the one that
    # looked up rules by the path it was HANDED, and so exited 0 on the link.
    r9c = fire_post(root9c, {"agent_type": "harness-orchestrator", "tool_name": "Write",
                             "hook_event_name": "PostToolUse",
                             "tool_input": {"file_path": post_link, "content": "x"}})
    t09("T-09 9: the POST reporter follows the link and the vocabulary net speaks — a landed "
        "illegal station is reported even though the path written carries no rules",
        r9c.returncode == 2 and "Sideways" in r9c.stderr,
        f"exit {r9c.returncode}, stderr={r9c.stderr.strip()[:300]!r}")


def _t09_other_routes():
    """11. Hardlink, linked parent directory, and a chain too long (FEAT-41 C2-02)."""

    # ---- 11. THE THREE ROUTES H-01's FIRST FIX STILL LEFT OPEN (FEAT-41 C2-02) ------------
    # Cycle 2's panel, high, all three reproduced live by its security reviewer. H-01 closed the
    # symlinked-FILE case it was shown and stopped there, which is the same mistake in kind that
    # F-04's record made -- fixing the demonstrated instance and reading it as the class.
    #
    #   (a) HARDLINK. `os.path.islink` is False for one, so the hop loop broke immediately and
    #       only the as-typed spelling was matched. A hardlink has NO target to read: it IS the
    #       file, under another name, so no amount of path resolution can see it. Identity can.
    #   (b) LINKED PARENT DIRECTORY. Only the full path was resolved, never an intermediate
    #       component, so `notes-link/innocent.md` where `notes-link -> ../notes` was invisible.
    #   (c) A CHAIN LONGER THAN THE HOP CAP FAILED **OPEN** -- the worst of the three. The real
    #       plan.yaml never entered the candidate list, so the shape test found nothing and the
    #       write was PERMITTED. A cap that runs out must refuse, not shrug.
    #
    # ONE MECHANISM PER QUESTION, and that is why the fix is not three patches: resolution
    # answers "what path does this become" (b, c), and inode identity answers "is this the same
    # file" (a). A hardlink is unanswerable by the first and trivial for the second.
    base9 = ".harness/harness/features/FEAT-99-fixture"
    for label, build, expect in (
        ("a hardlink to plan.yaml", "hardlink", 2),
        ("an innocent file under a LINKED parent directory", "dirlink", 2),
        ("a symlink chain longer than the hop cap", "deepchain", 2),
        ("a hardlink to a file that is NOT the plan", "hardlink_benign", 0),
    ):
        root, plan = _approval_root(rel=f"{base9}/plan.yaml", body=_PLAN_LEGAL)
        featd = os.path.join(root, ".harness", "harness", "features", "FEAT-99-fixture")
        notes = os.path.join(featd, "notes")
        os.makedirs(notes, exist_ok=True)
        if build == "hardlink":
            target = os.path.join(notes, "innocent.md")
            os.link(plan, target)
        elif build == "dirlink":
            # THE LINK ADDS A SEGMENT, and that is what defeats the pattern. `RE_PLAN_YAML`
            # anchors on `features/<one segment>/plan.yaml`, so
            # `features/FEAT-99-fixture/alias/plan.yaml` matches NOTHING even though its final
            # component is spelled plan.yaml and the write lands in another feature's real plan.
            #
            # MY FIRST FIXTURE HERE WAS WRONG and passed for the wrong reason: I made the final
            # component a symlink too, so the existing hop walk resolved it and the case went
            # green while the directory route was still open. A linked DIRECTORY needs the
            # innocent segment to be the directory, never the file.
            other = os.path.join(root, ".harness", "harness", "features", "FEAT-98-other")
            os.makedirs(other, exist_ok=True)
            with open(os.path.join(other, "plan.yaml"), "w") as _f:
                _f.write(_PLAN_LEGAL)
            os.symlink(os.path.join("..", "FEAT-98-other"), os.path.join(featd, "alias"))
            target = os.path.join(featd, "alias", "plan.yaml")
        elif build == "deepchain":
            prev = os.path.join("..", "plan.yaml")
            for i in range(12):
                link = os.path.join(notes, f"hop{i}.md")
                os.symlink(prev, link)
                prev = f"hop{i}.md"
            target = os.path.join(notes, "hop11.md")
        else:
            other = os.path.join(featd, "BRIEF.md")
            with open(other, "w") as _f:
                _f.write("# BRIEF\n")
            target = os.path.join(notes, "innocent2.md")
            os.link(other, target)
        r = _fire_write(root, target, _PLAN_LEGAL, agent="harness-orchestrator")
        verb = "DENIED" if expect == 2 else "still ALLOWED"
        t09(f"T-09 11: a Write through {label} is {verb} — identity and resolution are "
            f"different questions and the plan needs both answered",
            r.returncode == expect,
            f"exit {r.returncode} (want {expect}), stderr={r.stderr.strip()[:300]!r}")


# Path, over-budget body, and the word the refusal must carry. ONE ROW PER `_I`-WIDENED PATTERN
# except RE_PLAN_YAML, which case 8 above already covers with its own case-fold case.
_FOLD_ROWS = (
    ("features/FEAT-99-fixture/{}", "Feature.json", "feature.json", 301, "{}\n", "300"),
    ("features/FEAT-99-fixture/notes/{}", "Handoff-Build.md", "handoff-build.md", 61,
     "# h\n", "60"),
    ("features/FEAT-99-fixture/{}", "State.md", "STATE.md", 121, "# s\n", "120"),
)


def _t09_case_fold():
    """10. Every `_I`-widened pattern is tested, not only the one F-04 fixed."""

    # ---- 10. THE OTHER FOUR `_I` PATTERNS ARE TESTED TOO ----------------------------------
    # Cycle 1's QA, med, and MUTATION-PROVEN by them: removing `_I` from RE_FEATURE_JSON alone
    # produced zero failures across this whole suite. F-04 widened six patterns and only
    # RE_PLAN_YAML -- the one the finding was about -- got a case-fold case. The other five were
    # defence-in-depth that the suite could not tell from dead code.
    #
    # THE DISCRIMINATOR IS THE PAIR, and it is why both spellings are asserted rather than only
    # the folded one: the canonical path proves the BODY genuinely violates the budget, so when
    # the folded path is also refused, the refusal is attributable to `_I` and to nothing else.
    # Drop `_I` from any row's pattern and exactly that row's folded case reds while its
    # canonical case stays green.
    for tmpl, folded, canonical, nlines, unit, budget in _FOLD_ROWS:
        body = unit * nlines
        for spelling, folded_case in ((canonical, False), (folded, True)):
            rel = ".harness/harness/" + tmpl.format(spelling)
            root, full = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
            abs_p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(abs_p), exist_ok=True)
            r = _fire_write(root, abs_p, body, agent="harness-orchestrator")
            t09(f"T-09 10: {spelling} over budget is DENIED"
                + (" — the SPELLING is not a way past a budget" if folded_case else
                   " — the canonical control, proving the body really violates it"),
                r.returncode == 2 and budget in r.stderr,
                f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")

    # NEGATIVE CONTROL, ONE PER FOLDED SPELLING. A case-folded path carrying a LEGAL body is
    # still allowed, so `_I` widened WHICH PATHS ARE MEASURED and did not turn a spelling into a
    # denial of its own.
    #
    # EACH BODY IS LEGAL FOR ITS OWN FILE, and getting that wrong is how these first failed:
    # `{}` repeated is over-budget-free but SCHEMA-invalid for feature.json, and three heading
    # lines are within 60 but violate the handoff's five-section rule. Both refusals were real
    # and had nothing to do with the fold, so the controls would have gone red for a reason that
    # could not distinguish the fix from its absence.
    _legal_bodies = {
        "Feature.json": _legal_feature_json(20),
        "Handoff-Build.md": "\n".join(
            ["## Next", "## Trust"] + ["x"] * 10 + ["## Dead ends", "## Working set",
             "## Done when", "Scope: fixture", "Authority: plan-task:T-02.verify"]) + "\n",
        "State.md": "## Current\n" + "x" * 3 + "\n",
    }
    for tmpl, folded, _canon, _n, _unit, _b in _FOLD_ROWS:
        rel = ".harness/harness/" + tmpl.format(folded)
        root, _full = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
        abs_p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(abs_p), exist_ok=True)
        r = _fire_write(root, abs_p, _legal_bodies[folded], agent="harness-orchestrator")
        t09(f"T-09 10 NEGATIVE CONTROL: {folded} within budget is still ALLOWED — the fold "
            f"widened what is measured, not what is refused",
            r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")


def _t09_unresolvable():
    """12. An unresolvable path refuses, and does not take the hook down (FEAT-41 MF-2/MF-5)."""

    # ---- 12. UNRESOLVABLE MEANS REFUSE, NOT CRASH AND NOT SHRUG (FEAT-41 MF-2 + MF-5) -----
    # Cycle 3's panel, two findings that are one bug, and the panel saw a coupling neither of its
    # own reviewers could: the obvious fix for the crash lands inside the dead branch.
    #
    #   MF-2: `os.path.realpath` raises ValueError -- NOT OSError -- on an embedded NUL, so it
    #         escaped `_resolved_rel`'s except and propagated out of the whole Python body. By
    #         this file's own header, exit 1 is NON-blocking, so the write PROCEEDS. And
    #         `_plan_route` is called unconditionally, so a NUL took budgets and domain grants
    #         down with it, not only the plan route.
    #   MF-5: the `islink` fail-closed branch was DEAD, and the docstring's claim that realpath
    #         "raises on a loop" was FALSE. MEASURED both: realpath on a symlink loop RETURNS
    #         (`/private/tmp/loopt/a`, non-strict), and `os.path.islink` on a NUL path is False.
    #         So widening the except to return None would have routed to a branch that never
    #         fires -- the hole reopening two lines away from its own fix.
    #
    # THE FIX IS THAT UNRESOLVABLE IS ITS OWN ANSWER. Not None, which means "not the plan", but a
    # refusal. Non-strict realpath succeeds for paths that merely do not exist, so the only ways
    # to be unresolvable are pathological -- a NUL, or an OS-level path error. Ordinary work never
    # produces one, which is what makes refusing safe rather than obstructive.
    root12, _p12 = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                  body=_PLAN_LEGAL)
    nul = os.path.join(root12, ".harness", "harness", "features", "FEAT-99-fixture",
                       "innocent\x00.md")
    payload = {"agent_type": "harness-orchestrator", "tool_name": "Write",
               "tool_input": {"file_path": nul, "content": _PLAN_LEGAL}}
    r12 = subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                         text=True, env=_env(root12))
    t09("T-09 12: a NUL-bearing path is REFUSED at exit 2, not exit 1 — exit 1 is non-blocking "
        "here, so a crash is a fail-OPEN",
        r12.returncode == 2, f"exit {r12.returncode}, stderr={r12.stderr.strip()[:300]!r}")
    t09("T-09 12: and it does not crash — no traceback reaches the operator",
        "Traceback" not in r12.stderr, f"stderr={r12.stderr.strip()[:300]!r}")

    # NEGATIVE CONTROL. A path that simply DOES NOT EXIST is resolvable (realpath is non-strict)
    # and must stay allowed, or every first write of a new note would be refused.
    root12b, _p12b = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                    body=_PLAN_LEGAL)
    fresh = os.path.join(root12b, ".harness", "harness", "features", "FEAT-99-fixture",
                         "notes", "brand-new.md")
    os.makedirs(os.path.dirname(fresh), exist_ok=True)
    r12b = _fire_write(root12b, fresh, "# new\n", agent="harness-orchestrator")
    t09("T-09 12 NEGATIVE CONTROL: a path that does not exist yet is still ALLOWED — realpath is "
        "non-strict, so absence is not unresolvable",
        r12b.returncode == 0, f"exit {r12b.returncode}, stderr={r12b.stderr.strip()[:300]!r}")

    # AND A SYMLINK LOOP, which the docstring wrongly claimed realpath raises on. It RESOLVES,
    # so the loop is not the unresolvable case and must not be reported as one.
    root12c, _p12c = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                    body=_PLAN_LEGAL)
    featc = os.path.join(root12c, ".harness", "harness", "features", "FEAT-99-fixture")
    os.makedirs(os.path.join(featc, "notes"), exist_ok=True)
    os.symlink("loop-b.md", os.path.join(featc, "notes", "loop-a.md"))
    os.symlink("loop-a.md", os.path.join(featc, "notes", "loop-b.md"))
    r12c = _fire_write(root12c, os.path.join(featc, "notes", "loop-a.md"), "x\n",
                       agent="harness-orchestrator")
    t09("T-09 12: a symlink LOOP is allowed, not refused — realpath resolves it rather than "
        "raising, which the old docstring had backwards",
        r12c.returncode == 0, f"exit {r12c.returncode}, stderr={r12c.stderr.strip()[:300]!r}")


def run_t09():
    """FEAT-41 T-09: plan.yaml has exactly ONE writer, and the editor routes are refused."""
    global _T09_FAILS
    _T09_FAILS = 0
    _t09_edit_denial()
    _t09_binds_every_author()
    _t09_post_sweep()
    _t09_spelling()
    _t09_symlink()
    _t09_other_routes()
    _t09_case_fold()
    _t09_unresolvable()
    return _T09_FAILS


def run_t14():
    APPROVED = PLAN_ON_DISK.replace("status: pending\n  approved_by",
                                    "status: approved\n  approved_by")

    # 1. the flip is DENIED, and the message names the fragment and the route
    root, full = _approval_root()
    r = _fire_write(root, full, APPROVED)
    t14("1: a governed agent flipping approval.status is DENIED", r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t14("1: the denial names the approval mapping", MARK in r.stderr and "approval:" in r.stderr,
        r.stderr.strip()[:200])
    t14("1: the denial names the plan-merge route", "plan-merge.py" in r.stderr,
        r.stderr.strip()[:200])

    # FEAT-41 T-09 CLOSED THE EDITOR ROUTE, so every ALLOW below is INVERTED rather than
    # deleted, and this paragraph is why. This group was written when plan.yaml had no shape
    # rule (DEC-182) and the approval_guard was the only thing standing between an agent and
    # the approval mapping — so the guard's ALLOW direction was observable through Write and
    # Edit, and cases 2, 4, 5e, 6, 7, 8, 9, 10a and 10b measured exactly that.
    #
    # T-09 gives plan.yaml exactly ONE writer. The shape gate now refuses Write, Edit and
    # NotebookEdit on that path for EVERY author, including the main session (DEC-180), so no
    # editor write of a plan can be allowed by anything downstream of it. The approval_guard
    # itself is UNCHANGED and still first in line — cases 1, 3 and 5a-5d still see its own
    # message, which is why they still assert MARK.
    #
    # NOTHING LEGITIMATE LOST, and this was verified rather than assumed: `plan-merge.py apply`
    # CREATES a plan.yaml whole when the base does not exist (its step 3), so case 6's route was
    # redundant, not load-bearing. Run at execution time against a fresh legal path: APPLIED,
    # file created.
    #
    # THEY ARE KEPT BECAUSE THE ALLOW DIRECTION STILL MATTERS, just at a different gate: each
    # one now proves the shape denial reaches a case the approval_guard would have permitted,
    # which is the only remaining way to tell "denied by the route rule" from "denied by the
    # approval rule". A deleted case proves neither.

    # 2. INVERTED (T-09). The approval mapping is byte-identical, so the approval_guard has
    # nothing to say — and the ROUTE rule denies it anyway. The assertion that it is NOT the
    # approval message is what distinguishes the two gates.
    root, full = _approval_root()
    added = PLAN_ON_DISK + "  - id: T-03\n    change_type: logic\n    status: pending\n"
    r = _fire_write(root, full, added)
    t14("2 (T-09): adding a task through Write is DENIED BY THE ROUTE RULE, not the approval "
        "guard — plan.yaml has one writer",
        r.returncode == 2 and MARK not in r.stderr and "set-task-station" in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")

    # 3. the ORCHESTRATOR is governed too, and is not the signer (D-10)
    root, full = _approval_root()
    r = _fire_write(root, full, APPROVED, agent="harness-orchestrator")
    t14("3: the orchestrator flipping approval is DENIED too",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 4. THE CASE THE WHOLE DESIGN TURNS ON. No agent_type -> the main session -> allowed.
    root, full = _approval_root()
    payload = {"tool_name": "Write", "tool_input": {"file_path": full, "content": APPROVED}}
    r = subprocess.run([HOOK], input=json.dumps(payload), capture_output=True, text=True,
                       env=_env(root))
    # INVERTED (T-09), AND THIS IS THE CASE THE DESIGN NOW TURNS ON THE OTHER WAY. The main
    # session is still ungoverned by the DOMAIN region — that mechanism is untouched — but the
    # SHAPE gate binds every author by design (DEC-180), because exempting the one author most
    # likely to hand-edit a plan is exactly what T-09 exists to prevent. The main session signs
    # through `plan-merge.py sign-approval`, which T-08 gates on identity so that only it can.
    t14("4 (T-09): the MAIN SESSION's editor write is DENIED TOO — the shape gate binds every "
        "author, and signing is a verb now",
        r.returncode == 2, f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")

    # 5a. TARGETED
    root, full = _approval_root()
    r = _fire_edit(root, full, "  status: pending", "  status: approved")
    t14("5a: a targeted Edit of the signature is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5b. THE MID-LINE-START EVASION. Its FIRST line carries ZERO leading spaces, so any
    # rule anchored on a two-space line start is blind to it. The obvious implementation
    # ALLOWS this, which is why the case exists.
    root, full = _approval_root()
    r = _fire_edit(root, full, "status: pending\n  approved_by:", "status: approved\n  approved_by:")
    t14("5b: the mid-line-start evasion is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5c. THE ACCIDENTAL SWEEP. replace_all over a substring that occurs several times,
    # one of them the signature. Also invisible to an indent rule.
    root, full = _approval_root()
    r = _fire_edit(root, full, "status: pending", "status: approved", replace_all=True)
    t14("5c: the accidental replace_all sweep is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5d. LIMB B: INTRODUCING a block rather than replacing one.
    root, full = _approval_root()
    r = _fire_edit(root, full, "tasks:", "approval:\n  status: approved\ntasks:")
    t14("5d: an Edit INTRODUCING an approval block at column zero is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5e. THE ALLOW DIRECTION for Edit, and it is the case a deny-everything build fails.
    root, full = _approval_root()
    r = _fire_edit(root, full, "    change_type: logic\n    status: pending",
                   "    change_type: docs\n    status: done")
    t14("5e (T-09): an Edit touching only a task body is DENIED by the route rule",
        r.returncode == 2 and "set-task-station" in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 6. no file on disk -> no signature to destroy
    root = fixture(APPROVAL_MANIFEST)
    full = os.path.join(root, REL_PLAN)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    r = _fire_write(root, full, APPROVED)
    # INVERTED (T-09). Creation does not go through an editor: `plan-merge.py apply` writes a
    # plan whole when the base does not exist, which was measured at execution time.
    t14("6 (T-09): a plan.yaml that does not exist yet is DENIED too — creation goes through "
        "apply, not Write",
        r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 7. an unparseable proposal is ALLOWED and SAYS SO. A silent allow and a reported
    # allow are different gates.
    root, full = _approval_root()
    r = _fire_write(root, full, "approval:\n  status: [unclosed\n")
    t14("7 (T-09): an unparseable proposal is DENIED by the route rule — the shape gate never "
        "parses, so unparseable and legal are refused alike",
        r.returncode == 2, f"exit {r.returncode}")
    t14("7: and stderr SAYS the parse failed",
        "could not parse" in r.stderr, r.stderr.strip()[:200])

    # 8. a whitespace-only reflow loads to the same value. A text-comparing build fails here.
    root, full = _approval_root()
    reflowed = PLAN_ON_DISK.replace("  status: pending\n", "  status:   pending\n")
    r = _fire_write(root, full, reflowed)
    t14("8 (T-09): a whitespace-only reflow is DENIED by the route rule, though still NOT by "
        "the approval guard",
        r.returncode == 2 and MARK not in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 9. THE ONLY CASE THAT DISCRIMINATES READING THE RECORD FROM REIMPLEMENTING IT.
    # A hardcoded plan.yaml pattern passes 1-8 and fails this.
    dropped = APPROVAL_MANIFEST.replace(
        '    - ".harness/*/features/*/plan.yaml approval:"\n', "")
    assert dropped != APPROVAL_MANIFEST
    root, full = _approval_root(manifest_text=dropped)
    r = _fire_write(root, full, APPROVED)
    # INVERTED (T-09). Dropping the list entry still disarms the APPROVAL guard — that is the
    # property the intent protects by leaving the entry in place — but the ROUTE rule does not
    # read that list, so the write is refused regardless. Asserted by the message, not the code.
    t14("9 (T-09): dropping the entry from main_session.writes stops the APPROVAL denial but "
        "not the ROUTE denial",
        r.returncode == 2 and MARK not in r.stderr and "one writer" in r.stderr.lower(),
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 10. THE LOUD FAIL-OPEN, both shapes.
    # Derived from APPROVAL_MANIFEST, NOT from FIXTURE_MANIFEST: the grants must stay so
    # the write reaches the guard. Built from the bare fixture it is an ordinary domain
    # denial and this case reports exit 2 for entirely the wrong reason.
    import re as _re
    no_ms = _re.sub(r"main_session:\n(?:  .*\n|    .*\n)+", "", APPROVAL_MANIFEST)
    assert "main_session" not in no_ms, "the main_session stanza was not removed"
    root, full = _approval_root(manifest_text=no_ms)
    r = _fire_write(root, full, APPROVED)
    t14("10a (T-09): no main_session key at all -> still DENIED by the route rule",
        r.returncode == 2 and MARK not in r.stderr, f"exit {r.returncode}")
    t14("10a: and stderr says the exclusion list was unreadable",
        "exclusion list was unreadable" in r.stderr, r.stderr.strip()[:200])
    empty = no_ms.replace("shared:\n", "main_session:\n  writes: []\nshared:\n")
    root, full = _approval_root(manifest_text=empty)
    r = _fire_write(root, full, APPROVED)
    t14("10b (T-09): an empty writes list -> still DENIED by the route rule",
        r.returncode == 2 and MARK not in r.stderr, f"exit {r.returncode}")
    t14("10b: and stderr says the exclusion list was unreadable",
        "exclusion list was unreadable" in r.stderr, r.stderr.strip()[:200])

    # 11. A FRAGMENT-LESS ENTRY CONTRIBUTES NO DENIAL. Assert the ABSENCE of the fragment
    # marker rather than exit 0 -- that path may be refused by ordinary domain rules for
    # unrelated reasons, and a bare exit assertion would pass for the wrong reason.
    root = fixture(APPROVAL_MANIFEST)
    full = os.path.join(root, ".harness", "logs", "2026-01-01.md")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write("# log\n")
    r = _fire_write(root, full, "# log\nchanged\n")
    t14("11: a fragment-less entry (.harness/logs/**) contributes NO fragment denial",
        MARK not in r.stderr, r.stderr.strip()[:200])

    # 12. THE GENERALISATION, BRIEF.md, BOTH DIRECTIONS. This is the half that FAILS before
    # the task: team-config granted pm BRIEF.md whole and "except ## Approval" was a comment.
    root, full = _approval_root(rel=REL_BRIEF, body=BRIEF_ON_DISK)
    flipped = BRIEF_ON_DISK.replace("status: pending", "status: approved")
    r = _fire_write(root, full, flipped)
    t14("12: flipping BRIEF.md's ## Approval body is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t14("12: the denial names the ## Approval heading", "## Approval" in r.stderr,
        r.stderr.strip()[:200])
    root, full = _approval_root(rel=REL_BRIEF, body=BRIEF_ON_DISK)
    goal_only = BRIEF_ON_DISK.replace("Do the thing.", "Do the other thing.")
    r = _fire_write(root, full, goal_only)
    t14("12: changing only ## Goal, leaving ## Approval identical, is ALLOWED",
        r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 13. THE GENERALISATION, PLAN.md. Same hole as case 12.
    root, full = _approval_root(rel=REL_PLANMD, body=BRIEF_ON_DISK)
    r = _fire_write(root, full, BRIEF_ON_DISK.replace("status: pending", "status: approved"))
    t14("13: flipping PLAN.md's ## Approval body is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 14. THE REPOSITORY'S OWN RECORD, not a fixture. This is why T-14 depends_on T-15:
    # T-15 SUPPLIES the entry. It runs here as well as in T-15's verify because this file
    # runs in the integration kind on every CI run, so it is what keeps noticing if the
    # entry is ever deleted.
    # ROOT, NOT THE ENVIRONMENT. What stood here was the retired two-name chain falling
    # through to "." — the cwd — so this case read a different file depending on where the
    # runner was launched from, and reported the repository's own record missing when it
    # was not. That is half of #556. ROOT comes from __file__ and cannot move (FEAT-42).
    real = os.path.join(ROOT, ".harness", "team-config.yaml")
    try:
        import yaml as _y
        w = (_y.safe_load(open(real)) or {}).get("main_session", {}).get("writes") or []
    except Exception as exc:
        w = []
        t14("14: the real team-config.yaml is readable", False, repr(exc))
    t14("14: the real record carries the plan.yaml approval: entry",
        any(g.endswith("plan.yaml approval:") for g in w), repr(w))
    t14("14: and still carries the BRIEF.md ## Approval entry",
        any(g.endswith("BRIEF.md ## Approval") for g in w), repr(w))
    t14("14: and still carries the PLAN.md ## Approval entry",
        any(g.endswith("PLAN.md ## Approval") for g in w), repr(w))

    fails = 0
    for name, ok, detail in T14:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print("FAIL  %s" % (name,))
            print("      | %s" % (detail,))
    print("\n%d/%d T-14 cases passed." % (len(T14) - fails, len(T14)))
    return fails


def _feat51_root(reg, agent=None, runtime=None, supervisor_pid=None):
    root, _ = _approval_root(rel=REL_BRIEF, body=BRIEF_ON_DISK)
    if agent:
        reg.claim_with_receipt(
            root, agent, "harness-product-lead", root,
            feature="FEAT-99-fixture",
            session=("feat51-writer" if agent == "harness-orchestrator"
                     else "other-session"),
            runtime=runtime,
            supervisor_pid=supervisor_pid,
        )
    return root


def _feat51_fire(root, rel, hook=None):
    content = BRIEF_ON_DISK if rel == REL_BRIEF else "replacement\n"
    payload = {
        "agent_type": "harness-orchestrator",
        "session_id": "feat51-writer",
        "tool_name": "Write",
        "tool_input": {"file_path": os.path.join(root, rel), "content": content},
    }
    return subprocess.run(
        [hook or HOOK], input=json.dumps(payload), capture_output=True,
        text=True, env=_env(root),
    )


def _feat51_result(name, result, want, mention=None):
    ok = result.returncode == want and (mention is None or mention in result.stderr)
    return name, ok, f"exit {result.returncode}: {result.stderr}"


def _feat51_refusal_cases(reg, quarantine):
    root = _feat51_root(reg, "harness-qa")
    brief_path = os.path.join(root, REL_BRIEF)
    before = open(brief_path, "rb").read()
    refused = _feat51_fire(root, REL_BRIEF)
    after = open(brief_path, "rb").read()
    return [
        _feat51_result("an orphan canonical write is quarantined",
                       refused, 2, quarantine),
        ("the refused orphan write does not modify the canonical artifact",
         before == after, "canonical BRIEF.md changed"),
        _feat51_result(
            "NEGATIVE CONTROL: with the registry healthy an orphan canonical write is still refused",
            _feat51_fire(root, REL_BRIEF), 2, quarantine),
    ], root


def _feat51_fail_open_cases(reg, root):
    registry_path = os.path.join(root, reg.REGISTRY_REL)
    os.remove(registry_path)
    os.mkdir(registry_path)
    fired = _feat51_fire(root, REL_BRIEF)
    raising = _feat51_result(
        "an existing-but-unreadable registry (a directory) is refused fail-closed at the "
        "BUG-1304 claim boundary before the quarantine branch (REQ-05/SC-10 supersede this "
        "FEAT-51 fixture; quarantine fail-open stays pinned by the unimportable case below "
        "and by test-plan-sign-gate.py)",
        fired, 2, "claim registries are unreadable")
    names_file = (
        "the unreadable-registry refusal names the registry file to repair (REQ-05)",
        reg.REGISTRY_REL in fired.stderr, fired.stderr)

    root = _feat51_root(reg, "harness-qa")
    copybin = tempfile.mkdtemp()
    shutil.copytree(HERE, copybin, dirs_exist_ok=True)
    os.remove(os.path.join(copybin, "inflight_registry.py"))
    unimportable = _feat51_result(
        "an unimportable inflight_registry fails OPEN at the check-domain.sh quarantine branch",
        _feat51_fire(root, REL_BRIEF, hook=os.path.join(copybin, "check-domain.sh")),
        0, "boundary was not enforced")
    return [raising, names_file, unimportable]


def _feat51_omp_case(reg):
    supervisor = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"]
    )
    try:
        root = _feat51_root(
            reg, "harness-qa", runtime="omp", supervisor_pid=supervisor.pid
        )
        return _feat51_result(
            "an omp-runtime writer is never quarantined",
            _feat51_fire(root, REL_BRIEF), 0)
    finally:
        supervisor.terminate()
        supervisor.wait()


def _feat51_allow_cases(reg, quarantine):
    own = _feat51_root(reg, "harness-orchestrator")
    empty = _feat51_root(reg)
    orphan = _feat51_root(reg, "harness-qa")
    notes = ".harness/harness/features/FEAT-99-fixture/notes/report.txt"
    return [
        _feat51_result("the writer own live claim allows the canonical write",
                       _feat51_fire(own, REL_BRIEF), 0),
        _feat51_result("a feature with no live claim allows the canonical write",
                       _feat51_fire(empty, REL_BRIEF), 0),
        _feat51_omp_case(reg),
        _feat51_result("an orphan write to notes is allowed",
                       _feat51_fire(orphan, notes), 0),
        _feat51_result("an orphan write to the quarantine path is allowed",
                       _feat51_fire(orphan, quarantine), 0),
    ], orphan


def _feat51_route_cases(root):
    result = _feat51_fire(root, REL_PLAN)
    return [
        _feat51_result("an orphan Write of plan.yaml keeps the FEAT-41 route denial",
                       result, 2, "exactly ONE writer"),
        ("the plan.yaml route denial does not mention quarantine",
         "quarantine" not in result.stderr, result.stderr),
    ]


def _report_feat51_results(results):
    fails = 0
    for name, ok, detail in results:
        print(("ok    " if ok else "FAIL  ") + name)
        if not ok:
            fails += 1
            print("      " + detail[:500])
    return fails


def run_feat51_orphan_write():
    sys.path.insert(0, HERE)
    import inflight_registry as reg

    quarantine = (
        ".harness/harness/features/FEAT-99-fixture/quarantine/"
        "harness-orchestrator-feat51-w/BRIEF.md"
    )
    refusal, refused_root = _feat51_refusal_cases(reg, quarantine)
    allowed, orphan_root = _feat51_allow_cases(reg, quarantine)
    results = refusal + _feat51_fail_open_cases(reg, refused_root) + allowed
    results += _feat51_route_cases(orphan_root)
    return _report_feat51_results(results)


def main():
    return drive(globals())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
