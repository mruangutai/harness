#!/usr/bin/env python3
"""check-state.py at session entry: INV-21, INV-24.

Sliced out of tests/integration/test-check-state.py (issue #1527). The mirrored feature with
no recorded parent (INV-21), factory claims against the fleet (INV-24), the
cost-log silence, the two enforcement scripts' agreement on every duplicated number, and
the crash shapes a malformed tree must report instead of dying on. No test invokes a real
`gh` binary. INV-9 was retired under DEC-233; INV-28 and INV-30 under DEC-252.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import shutil
import subprocess
import sys
import tempfile
import harness_yaml
from check_state_support import (HARNESS_JSON_SYNC_OFF, HARNESS_JSON_SYNC_ON, SCRIPT, check_state_source,
    make_fixture, run, _run_with_gh, _run_with_gh_streams)


def case_a():
    """sync: true, issues recorded, no numeric parent -> INV-21 note appears, and
    warn-level means it does not by itself change the exit code (checked against
    case_b, whose only difference is a recorded parent)."""
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, HARNESS_JSON_SYNC_ON, "  parent: none")
        code, out = run(tmp)
        ok = "INV-21" in out
        print(f"{'ok' if ok else 'FAIL'} - case (a): INV-21 note appears when parent is unrecorded")
        return ok, code


def case_b():
    """sync: true, issues recorded, parent: 40 -> no INV-21 note."""
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, HARNESS_JSON_SYNC_ON, "  parent: 40")
        code, out = run(tmp)
        ok = "INV-21" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (b): no INV-21 note when parent is recorded")
        return ok, code


def case_c():
    """sync: false, issues recorded, no parent -> no INV-21 note (vacuous when sync is off)."""
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, HARNESS_JSON_SYNC_OFF, "  parent: none")
        code, out = run(tmp)
        ok = "INV-21" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (c): no INV-21 note when github.sync is false")
        return ok, code



RUNS_WITH_VALIDATOR_ENTRY = """{
  "feature_id": "FEAT-TEST",
  "cycles_used": 0,
  "runs": [
    {
      "id": "2026-08-03-01-validator",
      "squad": "validator",
      "verdict": "FAIL"
    }
  ],
  "github": {
    "parent": 40,
    "issues": {"T-01": 41}
  }
}
"""


def case_e():
    """Issue #11, behavioural: a trailing `#` comment on a run's `id:` or `squad:`
    line must not make the run invisible.

    The historical label is retained in the printed byte baseline, but this fixture now
    reaches the same invariant through strict JSON. The canonical reader must preserve the
    observable run semantics: a validator run with no usable review_sha makes INV-6 fire.

    Asserted through the invariant rather than the parser: this fixture has a validator
    run and NO `review_sha`, so a correct parse MUST report INV-6. Pre-fix the run
    vanished and check-state.py said nothing at all — which is why a parser-level
    assertion would be the weaker test.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write(RUNS_WITH_VALIDATOR_ENTRY)
        code, out = run(tmp)
        ok = "review_sha is not pinned" in out
        print(f"{'ok' if ok else 'FAIL'} - case (e): issue #11 — a commented squad:/id: "
              f"line still yields the run, so INV-6 fires")
        if not ok:
            print("        INV-6 was silent: the run was dropped and the gate failed OPEN")
        return ok


def case_f():
    """A feature.json that does not parse is a VIOLATION, never a silent skip.

    DEC-171 removed the fallback deliberately: there is no quieter mode. Before
    T-07 an unparseable file was indistinguishable from one with no runs, which is the
    same fail-open with a different cause.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write("runs: [ {id: a, squad: b ## eaten\nnext_key: 1\n")
        code, out = run(tmp)
        ok = "does not parse" in out and code == 1
        print(f"{'ok' if ok else 'FAIL'} - case (f): an unparseable feature.json is "
              f"reported and exits 1 (got exit {code})")
        return ok


def case_k():
    """FEAT-08 / DEC-178, BOTH directions in one case — the two halves are only
    meaningful together.

    (1) A run that is `status: complete` and carries NO `cost:` block is CLEAN.
        The removed completed-run invariant made exactly this a violation, on the
        grounds that an unmetered run looked identical to a free one. This half is
        the DETECTOR: it fails before the removal, which is why the case exists at
        all — without it, nothing proves the invariant is gone rather than merely
        unreached.
    (2) A run that DOES carry a `cost:` block is ALSO clean. `cost` stays in
        CHECKPOINT_KEYS (D-03) because all 67 pre-FEAT-08 run state.yaml files have
        one and :401 flags any key outside that set. Drop it from the whitelist and
        every historical run becomes a violation. This half is a REGRESSION guard —
        green before and after — and it is what stops a later tidy-up removing the
        entry as dead.
    """
    results = []
    for label, cost_block in (("no cost: block", ""), ("with a cost: block", "cost:\n  usd: 12.83\n")):
        with tempfile.TemporaryDirectory() as tmp:
            h = os.path.join(tmp, ".harness")
            rundir = os.path.join(h, "harness", "features", "FEAT-TEST", "runs", "2026-08-05-01-product")
            os.makedirs(rundir, exist_ok=True)
            with open(os.path.join(h, "harness.json"), "w") as f:
                f.write(HARNESS_JSON_SYNC_OFF)
            with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
                json.dump(
                    {"feature_id": "FEAT-TEST", "review_sha": "none", "runs": []}, f)
            with open(os.path.join(rundir, "state.yaml"), "w") as f:
                f.write("schema_version: 1\n"
                        "run_id: 2026-08-05-01-product\n"
                        "feature: FEAT-TEST\n"
                        "squad: product\n"
                        "host: harness-product-lead\n"
                        "status: complete\n"
                        "steps: []\n" + cost_block)
            with open(os.path.join(rundir, "digest.md"), "w") as f:
                f.write("# digest\n")
            code, out = run(tmp)
            # Assert on the SPECIFIC message, not the exit code: this fixture is
            # minimal and unrelated invariants may legitimately warn.
            hit = "has no cost: block" in out or "unknown top-level key" in out
            results.append(not hit)
            print(f"{'ok' if not hit else 'FAIL'} - case (k) {label}: no cost violation")
            if hit:
                print(f"        output was: {out.strip()[:200]}")
    return all(results)



def case_t():
    """A crash shape: exit 1 with EMPTY stdout.

    The /harness gate reads a non-zero exit as "violations found" and prints nothing for the
    operator to act on, and every invariant after the raise never runs. A plain FILE named
    `runs` under a feature dir: glob matches files as well as directories, and os.listdir on
    a file raises NotADirectoryError.

    The assertion is diagnosis-shaped, not exit-code-shaped: exit 1 is the CORRECT outcome
    once it is reported, so only non-empty output distinguishes a report from a crash.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        fdir = os.path.join(tmp, ".harness", "harness", "features", "FEAT-CRASH")
        os.makedirs(fdir, exist_ok=True)
        with open(os.path.join(fdir, "runs"), "w") as f:   # a FILE, not a directory
            f.write("not a directory\n")
        _code, out = run(tmp)
        ok = out.strip() != "" and "Traceback" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (t): a plain file named `runs` does not "
              f"crash INV-18 (empty stdout means the checker crashed)")
        if not ok:
            print(f"       | stdout: {out.strip()[:200]!r}")
        return ok


def case_r():
    """(r) A project with NO harness.json must not CRASH check-state.

    Pre-existing, reproduced on main before it was fixed: `cj` was assigned only inside
    `if cfg:`, so an absent harness.json left the name unbound and every later consumer
    raised NameError. A crash exits 1 — the same code a real violation exits — so /harness
    entry reported "violations found" for a missing config, with a traceback where the
    diagnosis should be. check-state.py's own header records the identical shape being
    fixed once already, for a bad _selfdir.

    Found while landing DEC-182, because a plan.yaml fixture legitimately carries none.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"))
        # deliberately NO harness.json
        _code, out = run(tmp)
        # ASSERT ON WHAT A HEALTHY RUN PRODUCES, not on the absence of a traceback.
        # The first draft checked `"NameError" not in out` — and `run()` returns STDOUT
        # ONLY, while a traceback goes to STDERR, so it searched a stream that could never
        # contain the thing it looked for. It reported ok against the crashing build.
        # A crash produces NO invariant output at all, so the presence of the diagnosis
        # this fixture is supposed to earn is the discriminator.
        ok = "harness.json missing" in out
        print(f"{'ok' if ok else 'FAIL'} - case (r): no harness.json is DIAGNOSED, not a "
              f"crash (a crash prints nothing to stdout)")
        if not ok:
            print(f"       | stdout was: {out.strip()[:200]!r}")
        return ok


FLEET_YAML = """schema: factory-fleet/1
repos:
  - name: acme/widget
    default_branch: main
workspace_root: /tmp/acme-factories
"""


def _factory_tree(tmp, features, fleet=FLEET_YAML):
    """Build a fixture with N features, each optionally carrying a `factory` block.

    `features` is {feature_id: factory_block_yaml_or_None}. The legacy case
    vocabulary is converted to JSON here so every feature.json reaches the
    canonical strict reader.
    """
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_OFF)
    if fleet is not None:
        os.makedirs(os.path.join(h, "factory"), exist_ok=True)
        with open(os.path.join(h, "factory", "fleet.yaml"), "w") as f:
            f.write(fleet)
    for feat, block in features.items():
        d = os.path.join(h, "harness", "features", feat)
        os.makedirs(d, exist_ok=True)
        document = (
            harness_yaml.load_str(block, f"{feat} factory fixture")
            if block else {"branch": "none"}
        )
        with open(os.path.join(d, "feature.json"), "w") as f:
            json.dump(document, f)
            f.write("\n")
    return h


def _inv24_output_lines(output, strict_rejection):
    lines = [line for line in output.splitlines() if "INV-24" in line]
    if strict_rejection:
        subject = [
            line for line in output.splitlines()
            if "feature.json invalid" in line and "FEAT-CONTROL" not in line
        ]
    else:
        subject = [line for line in lines if "FEAT-CONTROL" not in line]
    return lines, subject


def _inv24_case_passes(lines, subject, expect_hit, needles, require_control):
    expected_subject = bool(subject) == expect_hit
    required_text = all(
        any(needle in line for line in subject) for needle in needles
    )
    control_found = (
        not require_control
        or any("FEAT-CONTROL" in line for line in lines)
    )
    return expected_subject and required_text and control_found


def case_s():
    """INV-24 factory claims, including strict-reader rejection at its input boundary."""
    results = []
    control_block = "factory:\n  repo: acme/nope\n  issues:\n    T-99: 999\n"

    def check(label, features, expect_hit, needles=(), fleet=FLEET_YAML, control=True,
              strict_rejection=False):
        feats = dict(features)
        require_control = not expect_hit and control and fleet is not None
        if require_control:
            feats["FEAT-CONTROL"] = control_block
        with tempfile.TemporaryDirectory() as tmp:
            _factory_tree(tmp, feats, fleet=fleet)
            _code, out = run(tmp)
        lines, subject = _inv24_output_lines(out, strict_rejection)
        ok = _inv24_case_passes(
            lines, subject, expect_hit, needles, require_control)
        print(f"{'ok' if ok else 'FAIL'} - case (s) INV-24: {label}")
        if not ok:
            print(f"       | INV-24 lines: {lines!r}")
        results.append(ok)

    listed = "factory:\n  repo: acme/widget\n  parent: 10\n  issues:\n    T-01: 11\n"
    check("a listed repository passes", {"FEAT-A": listed}, False)
    check("an UNLISTED repository is a violation naming the repo",
          {"FEAT-A": "factory:\n  repo: acme/nope\n  issues:\n    T-01: 11\n"},
          True, needles=("acme/nope",))
    check("two features recording one repo+issue names BOTH",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: 11\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  issues:\n    T-09: 11\n"},
          True, needles=("FEAT-A", "FEAT-B"))
    check("one feature's PARENT equal to another's issue names BOTH",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: 11\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  parent: 11\n  issues:\n    T-09: 12\n"},
          True, needles=("FEAT-A", "FEAT-B"))
    check("two features sharing one PARENT names BOTH",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  parent: 10\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  parent: 10\n"},
          True, needles=("FEAT-A", "FEAT-B"))
    check("a block with NO parent key is silent",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: 11\n"}, False)
    check("factory state with NO fleet file names the FLEET as the problem",
          {"FEAT-A": listed}, True, needles=("FEAT-A", "fleet.yaml", "is absent"), fleet=None)
    check("a null factory.repo is a violation, not a silent pass (C1)",
          {"FEAT-A": "factory:\n  repo: null\n  issues:\n    T-01: 11\n"},
          True, needles=("not a repository name",))
    check("a null issue number is named, not treated as a collision (C1)",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: null\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  issues:\n    T-09: null\n"},
          True, needles=("not a recorded issue number",), strict_rejection=True)
    check("a feature whose own parent equals its own task issue fires, and names BOTH sides (C2)",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  parent: 11\n  issues:\n    T-01: 11\n"},
          True, needles=("twice within its own factory", "task T-01", "the parent"))
    check("a quoted issue number is a number here, as it is for INV-21 (D-03)",
          {"FEAT-A": 'factory:\n  repo: acme/widget\n  parent: "40"\n  issues:\n    T-01: "41"\n'},
          False)
    check("a quoted number still collides across features (D-03 does not weaken the check)",
          {"FEAT-A": 'factory:\n  repo: acme/widget\n  issues:\n    T-01: "41"\n',
           "FEAT-B": "factory:\n  repo: acme/widget\n  issues:\n    T-02: 41\n"},
          True, needles=("both record acme/widget issue 41",))
    check("an issues block that is neither a mapping nor a list is reported, not skipped",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues: 42\n"},
          True, needles=("not a JSON object",), strict_rejection=True)
    check("a tree with no factory blocks at all is silent",
          {"FEAT-A": None, "FEAT-B": None}, False, control=False)
    return all(results)


def case_o():
    """The two enforcement scripts must AGREE on every number and key they both carry.

    Nothing shares these — deliberately (D-02): check-domain.py measures a write payload,
    check-state.py measures a file on disk, and merging the mechanisms is what let a
    malformed file pass unread once already. What is NOT deliberate is the two drifting
    apart in silence, where check-domain blocks at 201 lines while check-state warns at
    251 and no reader can tell which number is the budget.

    Issue #132 tripled the exposure: before it, only the handoff cap of 60 appeared in
    both files. This case is the drift detector that duplication now owes.
    """
    import re as _re
    here = _anchor_bin
    # CHECK_DOMAIN_BIN, not a hard-coded name — the same override this case's own
    # comment demands one line below, and it was hard-coded here anyway. Review pointed
    # CHECK_DOMAIN_BIN at a mutant saying "budget is 999" and this case printed ok,
    # having opened the real file instead.
    dom = open(os.environ.get("CHECK_DOMAIN_BIN")
               or os.path.join(here, "check-domain.py"), encoding="utf-8").read()
    # SCRIPT, not a hard-coded "check-state.py". This case reads source rather than running
    # it, so a literal path here would keep reading the REAL file while CHECK_STATE_BIN
    # pointed the rest of the suite at a mutant — the case would report ok against a copy
    # it never opened, which is the failure mode the override exists to expose.
    sta = check_state_source()                # FEAT-69: the entry plus every package file

    def budget(text, label, pat):
        m = _re.findall(pat, text)
        return sorted({int(x) for x in m}), label

    checks, ok_all = [], True
    for what, dpat, spat in (
        # The feature.json pair is GONE because the DUPLICATE is gone: FEAT-54's B-4 moved
        # the number and the counting rule into feature_schema.FEATURE_JSON_LINE_BUDGET, and
        # both gates now import it. That pair is policed by its own block below, which
        # asserts the single source AND that neither gate's fallback literal disagrees with
        # it — a fallback that drifts is the same defect this case exists to catch, just
        # hidden one branch deeper.
        #
        # The comment-line budget pair is GONE, not relaxed. T-06 removed the check from
        # both files because JSON has no comments, so it could never fire — and a pair of
        # numbers that can never be printed is a duplicate this case cannot police.
        ("STATE.md lines",      r"STATE\.md is \{len\(lines\)\} lines — budget is (\d+)",
                                r"STATE\.md'\)\} is \{len\(sl\)\} lines — budget is (\d+)"),
        # Issue #139 made this the fourth number in both files, so it joins the detector in
        # the same commit that duplicates it — not in a later one nobody writes.
        ("CLAUDE.md lines",     r"CLAUDE\.md is \{len\(lines\)\} lines — budget is (\d+)",
                                r"CLAUDE\.md is \{len\(_cml\)\} lines — budget is (\d+)"),
    ):
        a, _ = budget(dom, what, dpat)
        b, _ = budget(sta, what, spat)
        good = bool(a) and a == b
        ok_all &= good
        checks.append(f"{what}: check-domain {a or 'NOT FOUND'} vs check-state {b or 'NOT FOUND'}")

    # THE feature.json BUDGET, NOW SINGLE-SOURCED (FEAT-54 B-4). Three things must hold or
    # the de-duplication is worse than the duplication it replaced: the constant exists, both
    # gates read it BY NAME, and every fallback literal they carry for an unimportable helper
    # equals it. The third is the one a reader would miss — a fallback saying 250 would
    # silently enforce a different budget on exactly the path nobody tests.
    schema_src = open(os.path.join(here, "feature_schema.py"), encoding="utf-8").read()
    declared = _re.search(r"^FEATURE_JSON_LINE_BUDGET = (\d+)$", schema_src, _re.M)
    fallbacks = sorted({int(x) for x in
                        _re.findall(r"_(?:inv23_)?budget = (\d+)", dom + sta)})
    reads_constant = ("FEATURE_JSON_LINE_BUDGET" in dom
                      and "FEATURE_JSON_LINE_BUDGET" in sta)
    fgood = (declared is not None and reads_constant
             and fallbacks in ([], [int(declared.group(1))]))
    ok_all &= fgood
    checks.append(
        f"feature.json budget: declared "
        f"{declared.group(1) if declared else 'NOT FOUND'}, both gates read the constant "
        f"{reads_constant}, fallback literals {fallbacks or 'none'}")

    # AND THE COUNTING RULE ITSELF IS SHARED, not merely the number. Either gate counting
    # whole-file lines while the other excludes the ledger would enforce two budgets under
    # one name, which is exactly the drift class above with the numbers still matching.
    counts_journal = ("journal_lines" in dom and "journal_lines" in sta
                      and "def journal_lines" in schema_src)
    ok_all &= counts_journal
    checks.append(f"feature.json counting rule shared: {counts_journal}")

    # The checkpoint vocabulary, the oldest deliberate duplicate in the pair.
    va = set(_re.findall(r'"([a-z_]+)"',
                         _re.search(r"ALLOWED = \{(.*?)\}", dom, _re.S).group(1)))
    vb = set(_re.findall(r'"([a-z_]+)"',
                         _re.search(r"CHECKPOINT_KEYS = \{(.*?)\n\}", sta, _re.S).group(1)))
    vgood = bool(va) and va == vb
    ok_all &= vgood
    checks.append(f"checkpoint keys: {len(va)} vs {len(vb)}, "
                  f"diff {sorted(va ^ vb) or 'none'}")

    # The handoff contract, in THREE copies — the two scripts plus the template a human
    # fills in. The template is the one that matters most and is the one no gate reads:
    # rename a heading there and every future handoff is written to a shape check-domain
    # rejects, with the rejection pointing at templates/HANDOFF.md as the authority.
    # Compared case-insensitively, because check-state lowercases and check-domain does not.
    tpl = open(os.path.join(here, "..", "templates", "HANDOFF.md"), encoding="utf-8").read()
    ha = {h.lower() for h in _re.findall(r'"(## [^"]+)"',
          _re.search(r'required = \[(.*?)\]', dom, _re.S).group(1))}
    hb_ordered = [h.lower() for h in _re.findall(r'"(## [^"]+)"',
                  _re.search(r"HANDOFF_SECTIONS = \[(.*?)\]", sta, _re.S).group(1))]
    hb = set(hb_ordered)
    narrative_is_prefix = bool(_re.search(
        r"HANDOFF_NARRATIVE_HEADINGS\s*=\s*HANDOFF_SECTIONS\[:4\]", sta))
    hc = {h.strip().lower() for h in _re.findall(r"^(## .+)$", tpl, _re.M)}
    hgood = (bool(ha) and ha == hb and ha <= hc and narrative_is_prefix
             and hb_ordered[-1:] == ["## done when"])
    ok_all &= hgood
    checks.append(f"handoff headings: check-domain {sorted(ha)}, check-state {sorted(hb)}, "
                  f"narrative-prefix {narrative_is_prefix}, template {sorted(hc)}")

    print(f"{'ok' if ok_all else 'FAIL'} - case (o): check-domain.py, check-state.py and "
          f"HANDOFF.md agree on every duplicated budget, key and heading")
    if not ok_all:
        for c in checks:
            print(f"       | {c}")
    return ok_all


def case_no_root_replays_resolver_stderr():
    """An unconfigured isolated copy keeps the resolver's full traceback.

    The former shell entry point replayed stderr from its isolated root-resolution
    helper. Replacing that traceback with only ``str(exc)`` loses the failure's
    source and violates the conversion's byte-preservation contract.
    """
    with tempfile.TemporaryDirectory() as tmp:
        isolated = os.path.join(tmp, "bin")
        shutil.copytree(_anchor_bin, isolated)
        script = os.path.join(isolated, "check-state.py")
        env = os.environ.copy()
        env.pop("HARNESS_PROJECT_DIR", None)
        result = subprocess.run(
            [script], cwd=isolated, env=env, capture_output=True, text=True)
        lines = result.stderr.splitlines()
        ok = (
            result.returncode == 2
            and not result.stdout
            and bool(lines)
            and lines[0].startswith(
                "check-state.py: no harness root could be resolved from ")
            and "Traceback (most recent call last):" in result.stderr
            and "ValueError: no harness root found:" in result.stderr
            and "check-state.py: no harness root found:" not in result.stderr
        )
        print(f"{'ok' if ok else 'FAIL'} - no-root refusal replays the resolver traceback")
        return ok


def case_canonical_reader_rejects_duplicate_harness_json():
    """The enforcement reader must not inherit json.loads' last-key-wins behavior."""
    duplicate = (
        '{"github":{"sync":false,"repo":null},'
        '"github":{"sync":true,"repo":"org/repo"}}\n')
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, duplicate, "  parent: 40")
        code, out = run(tmp)
        ok = (
            code == 1
            and "harness.json is not valid JSON" in out
            and "duplicate key" in out
        )
        if not ok:
            print("FAIL - canonical harness.json reader accepted duplicate keys")
        return ok


def main():
    results = []
    ok, code_a = case_a()
    results.append(ok)
    ok, code_b = case_b()
    results.append(ok)
    ok, _code_c = case_c()
    results.append(ok)
    results.append(case_e())
    results.append(case_f())
    results.append(case_k())
    results.append(case_o())
    results.append(case_r())
    results.append(case_s())
    results.append(case_t())
    results.append(case_no_root_replays_resolver_stderr())
    results.append(case_canonical_reader_rejects_duplicate_harness_json())
    ok_exit_unchanged = code_a == code_b
    print(
        f"{'ok' if ok_exit_unchanged else 'FAIL'} - exit code unchanged by INV-21 "
        f"(a: {code_a}, b: {code_b})"
    )
    results.append(ok_exit_unchanged)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
