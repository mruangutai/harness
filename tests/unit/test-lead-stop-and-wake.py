#!/usr/bin/env python3
"""Guards three not-yet-shipped invariants of FEAT-37 (lead-stop-and-wake):

  playbook  — harness-team/SKILL.md's step (d) carries the lead-tier never-wait rule, its
              wake half, and the inoculation against the dispatch tool's "continue other
              work in the meantime" nudge, and the loop's across-turns/on-waking framing
              already surrounding step (d) is not disturbed.
  bound     — the once-only "a stop refusal fires at most once" claim, wherever it still
              appears, is qualified per-stop-sequence or lives inside a STRUCK entry —
              never left as a bare, falsifiable, un-scoped claim.
  coverage  — DECISIONS-INDEX.md's DEC-201 row, DECISIONS.md's DEC-201 heading, and some
              single sentence of the DEC-201 entry name the LEAD tier, not only the
              orchestrator.

All three groups are expected to FAIL today — nothing this test guards has shipped. The
`--self-check` path proves the playbook detectors discriminate at all, using a synthetic
skeleton this file authors itself, never a copy of the shipped text (so a reword of the
shipped sentence cannot make the self-check vacuous).

T-03, which would have added an "orchestrator" group reading
.claude/skills/harness/SKILL.md, was STRUCK AT SIGNATURE (plan.yaml D-12, issue #903). No
group here reads that file, and none should be added back without restoring T-03.

Stdlib only, no subprocess. Repo root is derived from this file's own path — never the
caller's cwd — exactly as test-orchestrator-playbook.py does.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import re
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

TEAM_PLAYBOOK_DEFAULT = os.path.join(ROOT, ".claude", "skills", "harness-team", "SKILL.md")
DECISIONS_PATH = os.path.join(ROOT, ".harness", "harness", "docs", "DECISIONS.md")
DECISIONS_INDEX_PATH = os.path.join(ROOT, ".harness", "harness", "docs", "DECISIONS-INDEX.md")
INFLIGHT_REGISTRY_PATH = os.path.join(ROOT, ".claude", "skills", "harness", "bin", "inflight_registry.py")

# FEAT-51 superseded inflight_registry.py's recurring-refusal prose with a
# nonterminal suspension. The once-only floor still binds the decision authority,
# where the old claim remains struck and qualified; it no longer binds the runtime.
BOUND_SITES = [DECISIONS_PATH]

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def read_text(path):
    """Returns the file's text, or None on any read failure — never raises."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


_SENTENCE_SPLIT_RE = re.compile(r"(\. )|(\n\n+)")


def _sentences(text):
    """Spans of `text` split on a period-space boundary (period stays with the sentence
    to its left) or a newline-newline boundary (belongs to neither side)."""
    spans = []
    start = 0
    for m in _SENTENCE_SPLIT_RE.finditer(text):
        if m.group(1) is not None:
            end = m.start() + 1
        else:
            end = m.start()
        spans.append((start, end))
        start = m.end()
    spans.append((start, len(text)))
    return spans


def sentence_containing(text, pos):
    for s, e in _sentences(text):
        if s <= pos <= e:
            return text[s:e]
    return text


def line_number(text, pos):
    return text.count("\n", 0, pos) + 1


def letter_line_re(letter):
    return re.compile(r"^\*\*" + re.escape(letter) + r"\. ", re.MULTILINE)


D_LINE_RE = letter_line_re("d")
E_LINE_RE = letter_line_re("e")
DEC_HEADING_RE = re.compile(r"^## DEC-\d+", re.MULTILINE)

# ---------------------------------------------------------------------------
# GROUP "playbook" detectors
# ---------------------------------------------------------------------------

STOP_RE = re.compile(
    r"end your turn|ends its turn|end the turn|ending your turn|stop your turn", re.I
)
WAKE_RE = re.compile(r"wakes|waking|woken|wake you|resumes you|resumed you", re.I)
EXPECT_RE = re.compile(
    r"is expected|to be expected|will be refused|expect the refusal|expect to be refused", re.I
)
AGAIN_RE = re.compile(
    r"end your turn again|stop again|return again|end the turn again|do it again", re.I
)
RECUR_RE = re.compile(
    r"recurs?|re-fires|refires|again on a later wake|on each wake|every wake"
    r"|per stop sequence|each stop sequence|consecutive stop sequence",
    re.I,
)
NUDGE_RE = re.compile(
    r"continue other work|other work in the meantime|respond to the user in the meantime"
    r"|in the meantime",
    re.I,
)
DENY_RE = re.compile(
    r"is not licence|is not a licence|not licence to|does not apply|does not mean"
    r"|is not permission|not an invitation|overrides|override that|ignore that|does not license",
    re.I,
)

ACROSS_TURNS_RE = re.compile(
    r"across turns|each wake|on waking|every wake|re-entering|re-enter", re.I
)
STATE_YAML_RE = re.compile(r"state\.yaml", re.I)
ON_WAKING_RE = re.compile(
    r"on waking|when you wake|after the turn ended|after your turn ended"
    r"|on being woken|on resuming",
    re.I,
)

REGION_CASE_NAMES = [
    "case1_stop_half",
    "case2_wake_half",
    "case3_halves_adjacent",
    "claude_code_suspension_contract",
    "claude_code_suspension_zero_polling",
    "claude_code_suspension_same_parent",
    "claude_code_suspension_quarantine_adoption",
]


def find_d_to_e_region(text):
    dm = D_LINE_RE.search(text)
    if not dm:
        return None
    em = E_LINE_RE.search(text, dm.end())
    if not em:
        return None
    return text[dm.start() : em.start()]


def playbook_cases(text):
    """Cases 0-9 against `text`. Never touches module-level state — every case is
    derived fresh from the passed-in text, which is what lets --self-check exercise the
    exact same detectors the live group uses."""
    results = []

    region = find_d_to_e_region(text)
    if region is None:
        results.append(("case0_region_markers_present", False, "d or e marker line not found"))
        for name in REGION_CASE_NAMES:
            results.append((name, False, "region unavailable — no case0 marker"))
    else:
        results.append(("case0_region_markers_present", True, ""))

        m1 = STOP_RE.search(region)
        results.append(
            ("case1_stop_half", bool(m1), "" if m1 else "STOP_RE not found in d-to-e region")
        )

        m2 = WAKE_RE.search(region)
        results.append(
            ("case2_wake_half", bool(m2), "" if m2 else "WAKE_RE not found in d-to-e region")
        )

        adjacent = bool(m1) and bool(m2) and abs(m1.start() - m2.start()) <= 600
        results.append(
            (
                "case3_halves_adjacent",
                adjacent,
                ""
                if adjacent
                else "stop/wake matches missing, or more than 600 chars apart",
            )
        )

        suspension_checks = (
            (
                "claude_code_suspension_contract",
                re.search(r"VERDICT:?\s*`?\s*SUSPENDED.*awaiting.*live child",
                          region, re.I | re.S),
            ),
            (
                "claude_code_suspension_zero_polling",
                re.search(r"Do not poll.*sleep.*heartbeat.*invent.*zero",
                          region, re.I | re.S),
            ),
            (
                "claude_code_suspension_same_parent",
                re.search(r"same parent.*registry.*replacement parent",
                          region, re.I | re.S),
            ),
            (
                "claude_code_suspension_quarantine_adoption",
                re.search(
                    r"quarantine\.py list.*adopt.*discard.*default.*timer.*non-canonical",
                    region, re.I | re.S,
                ),
            ),
        )
        for name, match in suspension_checks:
            results.append(
                (name, bool(match), "" if match else f"{name} not found in d-to-e region")
            )

    idx8 = text.find("Until every step is terminal")
    if idx8 == -1:
        results.append(
            ("case8_loop_spans_turns", False, "marker 'Until every step is terminal' not found")
        )
    else:
        window8 = text[idx8 : idx8 + 400]
        ok8 = bool(ACROSS_TURNS_RE.search(window8)) and bool(STATE_YAML_RE.search(window8))
        results.append(
            (
                "case8_loop_spans_turns",
                ok8,
                "" if ok8 else "400-char window misses across-turns alternation or state.yaml",
            )
        )

    idx9 = text.find("e. Collect returns")
    if idx9 == -1:
        results.append(
            ("case9_collect_on_waking", False, "marker 'e. Collect returns' not found")
        )
    else:
        window9 = text[idx9 : idx9 + 400]
        ok9 = bool(ON_WAKING_RE.search(window9))
        results.append(
            (
                "case9_collect_on_waking",
                ok9,
                "" if ok9 else "400-char window misses on-waking alternation",
            )
        )

    return results


# ---------------------------------------------------------------------------
# GROUP "bound" detectors
# ---------------------------------------------------------------------------

ONCE_RE = re.compile(
    r"fires at most once|fires once|refusal fires once|a second identical return will ship"
    r"|a second identical return ships|one-correction-round",
    re.I,
)
QUALIFIER_RE = re.compile(
    r"per consecutive stop sequence|per stop sequence|each stop sequence"
    r"|consecutive stop sequence|re-fires|refires|on each wake|every wake",
    re.I,
)


def struck_entry_covers(text, pos):
    """True when `pos` falls inside a level-two `## DEC-` entry whose body — up to the
    next level-two `## DEC-` heading — contains the literal STRUCK."""
    headings = list(DEC_HEADING_RE.finditer(text))
    heading_before = None
    for m in headings:
        if m.start() <= pos:
            heading_before = m
        else:
            break
    if heading_before is None:
        return False
    start = heading_before.start()
    end = len(text)
    for m in headings:
        if m.start() > start:
            end = m.start()
            break
    return "STRUCK" in text[start:end]


def bound_site_cases(path, results):
    rel = os.path.relpath(path, ROOT)
    site_key = os.path.basename(path)
    text = read_text(path)
    if text is None:
        results.append((f"case_floor_{site_key}", False, f"cannot read {rel}"))
        return

    occurrences = list(ONCE_RE.finditer(text))
    if not occurrences:
        results.append(
            (f"case_floor_{site_key}", False, f"zero once-only occurrences found in {rel}")
        )
        return
    results.append((f"case_floor_{site_key}", True, f"{len(occurrences)} occurrence(s) in {rel}"))

    is_decisions = os.path.abspath(path) == os.path.abspath(DECISIONS_PATH)
    for idx, m in enumerate(occurrences, start=1):
        sent = sentence_containing(text, m.start())
        ok = bool(QUALIFIER_RE.search(sent))
        if not ok and is_decisions:
            ok = struck_entry_covers(text, m.start())
        ln = line_number(text, m.start())
        # idx disambiguates two occurrences the once-only alternation matches on the
        # same line (e.g. "fires ONCE" and "a second identical return will ship" in one
        # sentence) — without it their case names collide and the second silently
        # overwrites the first in any name-keyed view of the results.
        name = f"case_occurrence_{site_key}_{ln}_{idx}"
        results.append(
            (
                name,
                ok,
                ""
                if ok
                else f"{rel}:{ln} once-only phrasing lacks a qualifier and is not inside a "
                f"STRUCK entry: {sent.strip()!r}",
            )
        )


def bound_cases(only_path=None):
    sites = BOUND_SITES
    results = []
    if only_path is not None:
        matches = [s for s in sites if s == only_path or os.path.relpath(s, ROOT) == only_path]
        if not matches:
            available = ", ".join(os.path.relpath(s, ROOT) for s in sites)
            results.append(
                (
                    "case_only_matched_no_site",
                    False,
                    f"--only {only_path!r} matched no bound site; available: {available}",
                )
            )
            return results
        sites = matches
    for path in sites:
        print(f"reading bound site from {path}")
        bound_site_cases(path, results)
    return results


# ---------------------------------------------------------------------------
# GROUP "coverage" detectors
# ---------------------------------------------------------------------------

LEAD_RE = re.compile(r"\bleads?\b|\bdomain lead\b|\blead tier\b", re.I)
ENDTURN_RE = re.compile(
    r"ends its turn|end its turn|ends the turn|end the turn|ends their turn|end your turn", re.I
)
DEC201_INDEX_ROW_RE = re.compile(r"^- DEC-201\b", re.MULTILINE)
DEC201_HEADING_RE = re.compile(r"^## DEC-201\b", re.MULTILINE)


def coverage_cases():
    results = []
    print(f"reading coverage index from {DECISIONS_INDEX_PATH}")
    print(f"reading coverage entry from {DECISIONS_PATH}")

    index_text = read_text(DECISIONS_INDEX_PATH)
    if index_text is None:
        results.append(("case_index_row", False, f"cannot read {DECISIONS_INDEX_PATH}"))
    else:
        m = DEC201_INDEX_ROW_RE.search(index_text)
        if not m:
            results.append(("case_index_row", False, "DEC-201 row not found in DECISIONS-INDEX.md"))
        else:
            line_end = index_text.find("\n", m.start())
            if line_end == -1:
                line_end = len(index_text)
            row = index_text[m.start() : line_end]
            if "::" not in row:
                results.append(("case_index_row", False, f"DEC-201 row has no :: separator: {row!r}"))
            else:
                right = row.split("::", 1)[1]
                ok = bool(LEAD_RE.search(right))
                results.append(
                    (
                        "case_index_row",
                        ok,
                        "" if ok else f"right of :: lacks LEAD_RE: {right.strip()!r}",
                    )
                )

    dec_text = read_text(DECISIONS_PATH)
    if dec_text is None:
        results.append(("case_entry_heading", False, f"cannot read {DECISIONS_PATH}"))
        results.append(("case_entry_scope", False, f"cannot read {DECISIONS_PATH}"))
        return results

    hm = DEC201_HEADING_RE.search(dec_text)
    if not hm:
        results.append(("case_entry_heading", False, "DEC-201 level-two heading not found"))
        results.append(("case_entry_scope", False, "DEC-201 level-two heading not found"))
        return results

    line_end = dec_text.find("\n", hm.start())
    if line_end == -1:
        line_end = len(dec_text)
    heading_line = dec_text[hm.start() : line_end]
    ok_heading = bool(LEAD_RE.search(heading_line))
    results.append(
        (
            "case_entry_heading",
            ok_heading,
            "" if ok_heading else f"heading lacks LEAD_RE: {heading_line.strip()!r}",
        )
    )

    end = len(dec_text)
    for m2 in DEC_HEADING_RE.finditer(dec_text):
        if m2.start() > hm.start():
            end = m2.start()
            break
    body = dec_text[hm.start() : end]

    ok_scope = False
    for s, e in _sentences(body):
        sent = body[s:e]
        if LEAD_RE.search(sent) and ENDTURN_RE.search(sent):
            ok_scope = True
            break
    results.append(
        (
            "case_entry_scope",
            ok_scope,
            ""
            if ok_scope
            else "no single sentence of the DEC-201 entry matches both LEAD_RE and ENDTURN_RE",
        )
    )
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def report(results, failures):
    for name, ok, detail in results:
        if ok:
            print(f"PASS {name}")
        else:
            print(f"FAIL {name} {detail}")
            failures.append(name)


def run_playbook_group(failures):
    path = os.environ.get("TEAM_PLAYBOOK_PATH", TEAM_PLAYBOOK_DEFAULT)
    print(f"reading playbook from {path}")
    text = read_text(path)
    if text is None:
        print(f"FAIL case0_region_markers_present cannot read {path}")
        failures.append("case0_region_markers_present")
        return
    report(playbook_cases(text), failures)


def run_bound_group(failures, only_path=None):
    report(bound_cases(only_path), failures)


def run_coverage_group(failures):
    report(coverage_cases(), failures)


# ---------------------------------------------------------------------------
# --self-check — proves the playbook detectors discriminate, off a synthetic skeleton
# ---------------------------------------------------------------------------

VARIANT_B_TEXT = (
    "You never wait for a member. Having dispatched, end your turn - the platform wakes you "
    "when the member completes. The dispatch tool will tell you to continue other work in the "
    "meantime; that is not licence to manufacture activity, and this rule overrides it. The "
    "stop refusal on that return is EXPECTED, not a bar - end your turn again, and expect it "
    "to recur on each later wake while a child is still live."
)

VARIANT_D_TEXT = (
    "You never wait for a member. Having dispatched, end your turn - the platform wakes you "
    "when the member completes."
)

VARIANT_E_TEXT = (
    "You never wait for a member. Having dispatched, end your turn - the platform wakes you "
    "when the member completes. The dispatch tool will tell you to continue other work in the "
    "meantime; that is not licence to manufacture activity, and this rule overrides it. The "
    "stop refusal on that return is EXPECTED, not a bar - expect it "
    "to recur on each later wake while a child is still live."
)

VARIANT_F_TEXT = (
    "You never wait for a member. Having dispatched, end your turn - the platform wakes you "
    "when the member completes. The "
    "stop refusal on that return is EXPECTED, not a bar - end your turn again, and expect it "
    "to recur on each later wake while a child is still live."
)


def build_skeleton(inoculation):
    return (
        "### 3. Loop\n\n"
        "Until every step is terminal, or you halt: The loop iterates across turns; each wake "
        "re-enters it, and state.yaml carries its position.\n\n"
        "**c. Serialize anything that mutates the repo.** placeholder c text.\n\n"
        "**d. Dispatch the rest of the ready set in one turn** placeholder d text.\n\n"
        + (inoculation + "\n\n" if inoculation else "")
        + "**e. Collect returns.** on waking, after the turn ended placeholder e text.\n\n"
        "**f. Apply on_fail.** placeholder f text.\n"
    )


def self_check_variants():
    return [
        ("A", build_skeleton(""), False),
        ("B", build_skeleton(VARIANT_B_TEXT), True),
        ("C", build_skeleton("") + "\n" + VARIANT_B_TEXT + "\n", False),
        ("D", build_skeleton(VARIANT_D_TEXT), False),
        ("E", build_skeleton(VARIANT_E_TEXT), False),
        ("F", build_skeleton(VARIANT_F_TEXT), False),
    ]


def run_self_check():
    overall_ok = True
    for label, text, expect_pass in self_check_variants():
        results = playbook_cases(text)
        failing = [name for name, ok, _ in results if not ok]
        got_pass = not failing
        verdict_ok = got_pass == expect_pass
        status = "PASS" if verdict_ok else "FAIL"
        print(
            f"SELFCHECK {status} variant {label} "
            f"(expected_pass={expect_pass} got_pass={got_pass} failing={failing})"
        )
        if not verdict_ok:
            overall_ok = False

    # bound_cases() with an --only value that matches no BOUND_SITES entry must return a
    # non-empty, failing result set — never the empty list a plain filter would produce,
    # which a bare loop-and-report would silently grade as ALL PASS. This never opens a
    # live file: the empty-match branch returns before any bound_site_cases()/read_text()
    # call, so it belongs under --self-check.
    bogus_results = bound_cases(only_path="/no/such/site/path/for/self-check.md")
    bogus_ok = bool(bogus_results) and all(not ok for _name, ok, _detail in bogus_results)
    status = "PASS" if bogus_ok else "FAIL"
    print(
        f"SELFCHECK {status} variant bound_only_unmatched "
        f"(results={bogus_results})"
    )
    if not bogus_ok:
        overall_ok = False

    return 0 if overall_ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

USAGE = (
    "usage: test-lead-stop-and-wake.py [--self-check | --group "
    "{playbook,bound,coverage} [--only PATH]]"
)


def main(argv):
    args = list(argv)

    if args == ["--self-check"]:
        return run_self_check()

    only_path = None
    group = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--group":
            if i + 1 >= len(args):
                print(USAGE, file=sys.stderr)
                return 2
            group = args[i + 1]
            i += 2
        elif a == "--only":
            if i + 1 >= len(args):
                print(USAGE, file=sys.stderr)
                return 2
            only_path = args[i + 1]
            i += 2
        else:
            print(USAGE, file=sys.stderr)
            return 2

    if only_path is not None and group != "bound":
        print("--only is valid with --group bound only", file=sys.stderr)
        return 2

    if group is not None and group not in ("playbook", "bound", "coverage"):
        print(USAGE, file=sys.stderr)
        return 2

    failures = []
    if group is None:
        run_playbook_group(failures)
        run_bound_group(failures)
        run_coverage_group(failures)
    elif group == "playbook":
        run_playbook_group(failures)
    elif group == "bound":
        run_bound_group(failures, only_path)
    elif group == "coverage":
        run_coverage_group(failures)

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
