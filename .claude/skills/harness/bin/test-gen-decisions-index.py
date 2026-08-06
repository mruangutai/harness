#!/usr/bin/env python3
"""Tests for the (not-yet-existent) DECISIONS-INDEX.md generator, written first
per FEAT-04-decisions-index T-01 — this is the RED deliverable.

Six tests. Four of them exercise the generator directly and fail-by-design at
T-01 because `gen-decisions-index.py` does not exist yet. Test 4 exercises the
already-shipped `check-docs.sh` and is expected to be green today. Test 5
exercises the committed `docs/harness/DECISIONS-INDEX.md`, which does not
exist yet either, and SKIPs by design (file-absence only — see its docstring).

Each test is wrapped in its own try/except in main() so one test's exception
never prevents the other five from running and reporting.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))
REAL_DECISIONS = os.path.join(REPO_ROOT, "docs", "harness", "DECISIONS.md")
REAL_INDEX = os.path.join(REPO_ROOT, "docs", "harness", "DECISIONS-INDEX.md")
CHECK_DOCS = os.path.join(BIN_DIR, "check-docs.sh")

# Overridable so a fix can be proven RED against a reverted copy — the same
# CHECK_STATE_BIN escape test-check-state.py uses.
GEN = os.environ.get("GEN_DECISIONS_INDEX_BIN") or os.path.join(
    BIN_DIR, "gen-decisions-index.py"
)

# The row grammar is IMPORTED, never restated (B-2). This test used to carry two of its
# own variants — `^- (DEC-\d+)\b(.*)$` and `^- (DEC-\d+).*?::\s*(.*)$` — and both were
# looser than the generator's about the ' :: ' separator, so a row the test happily
# parsed was one the generator silently treated as absent. Same importlib-by-path
# mechanism test-render-brief.py uses for a hyphenated module.
import importlib.util   # noqa: E402 — must follow BIN_DIR

_spec = importlib.util.spec_from_file_location("gen_decisions_index", GEN)
gdi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gdi)
ROW_RE = gdi.ROW_RE


def fence_guarded_dec_headings(text):
    """Mirror check-docs.sh's fence toggle (:44-48) exactly: a '## DEC-N'
    heading seen while inside a ``` code fence is documentation of the format,
    not a live declaration, and must not be harvested."""
    owners = []
    infence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            infence = not infence
            continue
        if infence:
            continue
        m = re.match(r"^##\s+(DEC-\d+)", line)
        if m:
            owners.append(m.group(1))
    return owners


def strip_ruling_prose(s):
    """Drop all trailing '— SUPERSEDED BY DEC-N' clauses (repeatable — DEC-19
    carries two) and any trailing <!-- ok-stale --> marker, then return what's
    left. Used to measure hand-written prose, not generator-written clauses."""
    cur = s.strip()
    prev = None
    while prev != cur:
        prev = cur
        cur = re.sub(r"—\s*SUPERSEDED BY DEC-\d+\s*$", "", cur).strip()
        cur = re.sub(r"<!--\s*ok-stale\s*-->\s*$", "", cur).strip()
    return cur


def run_gen(tree, extra_env=None, args=None):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = tree
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, GEN] + list(args or []),
        cwd=tree, capture_output=True, text=True, env=env
    )


def make_authority(tmp, decisions, bodies=None):
    """decisions: list of (number:int, title:str). Writes docs/harness/DECISIONS.md.

    bodies: optional {number: body_text} to override a decision's placeholder body,
    for the cases where the BODY is what is under test (supersession prose, B-3).
    """
    bodies = bodies or {}
    docs_dir = os.path.join(tmp, "docs", "harness")
    os.makedirs(docs_dir, exist_ok=True)
    body = []
    for n, title in decisions:
        text = bodies.get(n, f"**Chose:** placeholder body text for DEC-{n}.")
        body.append(f"## DEC-{n} — {title}\n\n{text}\n")
    with open(os.path.join(docs_dir, "DECISIONS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(body))
    return docs_dir


def write_index(docs_dir, rows):
    """rows: list of raw row strings (each '- DEC-N ... :: ruling')."""
    with open(os.path.join(docs_dir, "DECISIONS-INDEX.md"), "w", encoding="utf-8") as f:
        f.write("<!-- index-contract v1 -->\n\n")
        f.write("\n".join(rows) + "\n")


def read_index_rows(docs_dir):
    path = os.path.join(docs_dir, "DECISIONS-INDEX.md")
    if not os.path.isfile(path):
        return None
    return [
        l for l in open(path, encoding="utf-8").read().splitlines()
        if l.startswith("- DEC-")
    ]


def test_row_per_distinct_dec_matches_authority():
    name = "test_row_per_distinct_dec_matches_authority"
    try:
        text = open(REAL_DECISIONS, encoding="utf-8").read()
        raw = re.findall(r"^## (DEC-\d+)", text, re.M)
        fenced = fence_guarded_dec_headings(text)
        distinct = sorted(set(fenced))

        # Documented divergence (D-04): ## DEC-83 appears a second time inside a
        # code fence at DECISIONS.md:1583. The raw regex harvests it; the
        # fence-guarded parse the generator must use does not.
        # Assert the RELATIONSHIP, never frozen totals (issue #5): a literal count
        # reddens this gate on the next appended decision, which punishes writing a
        # decision rather than catching a parser defect. What D-04 actually claims is
        # that the raw regex over-harvests by exactly the fenced duplicates.
        fenced_dupes = len(raw) - len(distinct)
        if fenced_dupes != 1:
            print(f"FAIL - {name}: raw regex should over-harvest fence-guarded by exactly 1 "
                  f"(the DEC-83 duplicate inside a code fence), got {fenced_dupes} "
                  f"(raw={len(raw)}, distinct={len(distinct)})")
            return False
        if len(distinct) != len(set(distinct)):
            print(f"FAIL - {name}: fence-guarded parse yielded duplicate ids")
            return False

        if not os.path.exists(GEN):
            print(f"FAIL - {name}: generator not found at {GEN}")
            return False

        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = os.path.join(tmp, "docs", "harness")
            os.makedirs(docs_dir, exist_ok=True)
            shutil.copy(REAL_DECISIONS, os.path.join(docs_dir, "DECISIONS.md"))
            index_path = os.path.join(docs_dir, "DECISIONS-INDEX.md")
            r = run_gen(tmp)
            if r.returncode != 0:
                print(f"FAIL - {name}: generator exited {r.returncode}: {r.stderr.strip()[:200]}")
                return False
            if not os.path.isfile(index_path):
                print(f"FAIL - {name}: {index_path} not written")
                return False
            rows = read_index_rows(docs_dir)
            if len(rows) != len(distinct):
                print(f"FAIL - {name}: expected {len(distinct)} rows (distinct DEC count), got {len(rows)}")
                return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_preserves_hand_written_rulings_by_dec_number():
    name = "test_preserves_hand_written_rulings_by_dec_number"
    try:
        if not os.path.exists(GEN):
            print(f"FAIL - {name}: generator not found at {GEN}")
            return False

        with tempfile.TemporaryDirectory() as tmp:
            decisions = [(1, "First"), (2, "Second"), (3, "Third"), (4, "Fourth"), (5, "Fifth")]
            docs_dir = make_authority(tmp, decisions)
            rulings = {
                1: "Chose Postgres for durability guarantees over the alternative.",
                2: "Rejected in favor of the existing hook mechanism, see DEC-1.",
                3: "Adopted the fence-guarded parse to avoid the DEC-83 double count.",
                4: "Kept the old field name for backward compatibility with clients.",
                5: "Deferred to the next quarter pending the migration spike results.",
            }
            rows = [f"- DEC-{n} @1 [] refs:  :: {rulings[n]}" for n, _ in decisions]
            write_index(docs_dir, rows)

            # Insert a 6th decision BETWEEN existing ones.
            decisions_after = [
                (1, "First"), (2, "Second"), (3, "Third"), (6, "Sixth"),
                (4, "Fourth"), (5, "Fifth"),
            ]
            make_authority(tmp, decisions_after)

            r = run_gen(tmp)
            if r.returncode != 0:
                print(f"FAIL - {name}: generator exited {r.returncode}: {r.stderr.strip()[:200]}")
                return False

            new_rows = read_index_rows(docs_dir)
            if new_rows is None:
                print(f"FAIL - {name}: index not written")
                return False

            by_dec = {}
            for row in new_rows:
                m = ROW_RE.match(row)
                if m:
                    by_dec[m.group(1)] = m.group(2)

            for n in (1, 2, 3, 4, 5):
                dec = f"DEC-{n}"
                if dec not in by_dec:
                    print(f"FAIL - {name}: {dec} row missing after regeneration")
                    return False
                if rulings[n] not in by_dec[dec]:
                    print(f"FAIL - {name}: {dec}'s hand-written ruling not preserved byte-identical")
                    return False

            if "DEC-6" not in by_dec:
                print(f"FAIL - {name}: DEC-6 row missing")
                return False
            if "RULING PENDING" not in by_dec["DEC-6"]:
                print(f"FAIL - {name}: DEC-6 row missing RULING PENDING sentinel")
                return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_preserves_inline_ok_stale_marker_on_a_row():
    name = "test_preserves_inline_ok_stale_marker_on_a_row"
    try:
        if not os.path.exists(GEN):
            print(f"FAIL - {name}: generator not found at {GEN}")
            return False

        with tempfile.TemporaryDirectory() as tmp:
            decisions = [(1, "First"), (2, "Second"), (3, "Third"), (4, "Fourth"), (5, "Fifth")]
            docs_dir = make_authority(tmp, decisions)

            # Run once with no index present to get the generator's own canonical
            # rendering of each row. Everything left of ' :: ' (the @<line> anchor,
            # tag-list, refs spacing) is generator-computed, not ours to guess at —
            # so the expectation must be derived from the generator's own output,
            # not hand-written (see send-back on T-01, test 3).
            r0 = run_gen(tmp)
            if r0.returncode != 0:
                print(f"FAIL - {name}: baseline generator run exited {r0.returncode}: {r0.stderr.strip()[:200]}")
                return False
            baseline_rows = read_index_rows(docs_dir)
            if not baseline_rows:
                print(f"FAIL - {name}: baseline index not written or empty")
                return False
            dec3_baseline = next((row for row in baseline_rows if row.startswith("- DEC-3 ")), None)
            if dec3_baseline is None:
                print(f"FAIL - {name}: baseline DEC-3 row missing")
                return False
            if " :: " not in dec3_baseline:
                print(f"FAIL - {name}: baseline DEC-3 row has no ' :: ' separator")
                return False

            # Splice the hand-written ruling and marker into the generator's own
            # rendering of the DEC-3 row's left side.
            dec3_left, _ = dec3_baseline.split(" :: ", 1)
            marked_row = (
                f"{dec3_left} :: Superseded wording retained for the migration map. "
                "<!-- ok-stale -->"
            )

            rows = []
            for row in baseline_rows:
                if row.startswith("- DEC-3 "):
                    rows.append(marked_row)
                else:
                    left, _ = row.split(" :: ", 1)
                    rows.append(f"{left} :: hand-written ruling for regeneration.")
            write_index(docs_dir, rows)

            r = run_gen(tmp)
            if r.returncode != 0:
                print(f"FAIL - {name}: generator exited {r.returncode}: {r.stderr.strip()[:200]}")
                return False

            new_rows = read_index_rows(docs_dir)
            if new_rows is None:
                print(f"FAIL - {name}: index not written")
                return False
            dec3_rows = [r_ for r_ in new_rows if r_.startswith("- DEC-3 ")]
            if not dec3_rows:
                print(f"FAIL - {name}: DEC-3 row missing after regeneration")
                return False
            if dec3_rows[0] != marked_row:
                print(f"FAIL - {name}: DEC-3 row not byte-identical (ok-stale marker or text altered)")
                return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_checker_scans_root_level_markdown():
    """check-docs.sh must see CLAUDE.md — the file read at EVERY session start (issue #139).

    Its scan roots were docs/harness, .harness, .claude/skills, .claude/commands and
    .claude/agents. The REPO ROOT was not among them, so the propagation checker was blind
    to the file with the widest blast radius in the tree. Verified before the fix by
    planting a live stale phrase in the real CLAUDE.md: zero hits.

    The second half of this case is as load-bearing as the first: the root tier must be
    NON-RECURSIVE. Globbing `**` from `.` would walk .git, node_modules and
    .claude/worktrees/, scanning every file of every other checkout as if it were this one.
    """
    name = "test_checker_scans_root_level_markdown"
    try:
        phrase = "another fabricated placeholder phrase"
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = os.path.join(tmp, "docs", "harness")
            os.makedirs(docs_dir, exist_ok=True)
            with open(os.path.join(docs_dir, "DECISIONS.md"), "w", encoding="utf-8") as f:
                f.write("## DEC-01 — Single test decision\n\n"
                        f'<!-- stale: "{phrase}" -->\n\n**Chose:** placeholder body.\n')
            with open(os.path.join(tmp, "CLAUDE.md"), "w", encoding="utf-8") as f:
                f.write(f"# Project\n\nThis file repeats the {phrase} on purpose.\n")
            # A decoy one level down that the root tier must NOT reach, or the tier is
            # recursive and the case above would pass for the wrong reason.
            deep = os.path.join(tmp, "vendor", "someones-node-modules")
            os.makedirs(deep, exist_ok=True)
            with open(os.path.join(deep, "README.md"), "w", encoding="utf-8") as f:
                f.write(f"Vendored text mentioning the {phrase}.\n")

            env = dict(os.environ)
            env["CLAUDE_PROJECT_DIR"] = tmp
            r = subprocess.run([CHECK_DOCS], cwd=tmp, capture_output=True, text=True, env=env)
            out = r.stdout + r.stderr
            assert "CLAUDE.md" in out, f"root CLAUDE.md was not scanned:\n{out}"
            assert r.returncode == 1, f"expected exit 1, got {r.returncode}:\n{out}"
            assert "someones-node-modules" not in out, (
                f"the root tier recursed into a subdirectory — it must be depth-0 only:\n{out}")
        print(f"ok   {name}")
        return True
    except AssertionError as e:
        print(f"FAIL {name}: {e}")
        return False


def test_checker_flags_planted_stale_phrase_in_index():
    name = "test_checker_flags_planted_stale_phrase_in_index"
    try:
        phrase = "fabricated placeholder phrase"
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = os.path.join(tmp, "docs", "harness")
            os.makedirs(docs_dir, exist_ok=True)
            with open(os.path.join(docs_dir, "DECISIONS.md"), "w", encoding="utf-8") as f:
                f.write(
                    "## DEC-01 — Single test decision\n\n"
                    f'<!-- stale: "{phrase}" -->\n\n'
                    "**Chose:** placeholder body text.\n"
                )
            index_row = f"- DEC-01 @1 [] refs:  :: This ruling repeats the {phrase} on purpose."
            with open(os.path.join(docs_dir, "DECISIONS-INDEX.md"), "w", encoding="utf-8") as f:
                f.write("<!-- index-contract v1 -->\n\n" + index_row + "\n")

            env = dict(os.environ)
            env["CLAUDE_PROJECT_DIR"] = tmp
            r = subprocess.run([CHECK_DOCS], cwd=tmp, capture_output=True, text=True, env=env)
            # check-docs.sh cd's into CLAUDE_PROJECT_DIR and reports paths relative
            # to it, not absolute.
            rel_index_path = os.path.join("docs", "harness", "DECISIONS-INDEX.md")
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1 on planted phrase, got {r.returncode}\n{r.stdout}\n{r.stderr}")
                return False
            if rel_index_path not in r.stdout:
                print(f"FAIL - {name}: stdout does not name {rel_index_path}")
                return False
            if "DEC-01" not in r.stdout:
                print(f"FAIL - {name}: stdout does not name DEC-01")
                return False

            # Now mark the same row ok-stale and assert exit 0.
            marked_row = index_row + " <!-- ok-stale -->"
            with open(os.path.join(docs_dir, "DECISIONS-INDEX.md"), "w", encoding="utf-8") as f:
                f.write("<!-- index-contract v1 -->\n\n" + marked_row + "\n")
            r2 = subprocess.run([CHECK_DOCS], cwd=tmp, capture_output=True, text=True, env=env)
            if r2.returncode != 0:
                print(f"FAIL - {name}: expected exit 0 after <!-- ok-stale -->, got {r2.returncode}\n{r2.stdout}\n{r2.stderr}")
                return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_committed_index_is_complete_and_within_budget():
    name = "test_committed_index_is_complete_and_within_budget"
    try:
        # MF-2: the skip predicate is file-absence ONLY. A sentinel-bearing row
        # or a short ruling FAILS, never skips.
        if not os.path.isfile(REAL_INDEX):
            print(f"SKIP {name}")
            return True

        text = open(REAL_INDEX, encoding="utf-8").read()
        lines = text.splitlines()

        if "<!-- index-contract v1 -->" not in text:
            print(f"FAIL - {name}: missing <!-- index-contract v1 --> marker")
            return False
        if len(lines) > 260:
            print(f"FAIL - {name}: {len(lines)} lines exceeds 260-line budget")
            return False
        if "RULING PENDING" in text:
            unwritten = [
                m.group(1) for l in lines
                for m in [re.match(r"^- (DEC-\d+)", l)]
                if m and "RULING PENDING" in l
            ]
            print(
                f"FAIL - {name}: {len(unwritten)} row(s) unwritten in {REAL_INDEX} — a decision was "
                f"appended without its ruling. Run .claude/skills/harness/bin/gen-decisions-index.py "
                f"and write the ruling after ' :: ' on each listed row, in this commit (REQ-09). "
                f"Offending: {', '.join(unwritten)}"
            )
            return False

        thin = []
        over_cap = []
        for l in lines:
            m = ROW_RE.match(l)
            if not m:
                continue
            dec_id, ruling = m.groups()
            stripped = strip_ruling_prose(ruling)
            non_ws = re.sub(r"\s+", "", stripped)
            if len(non_ws) < 20:
                thin.append(dec_id)
            word_count = len(stripped.split())
            if word_count > 30:
                over_cap.append((dec_id, word_count))
        if thin or over_cap:
            if thin:
                print(
                    f"FAIL - {name}: {len(thin)} row(s) below the 20-non-whitespace-character prose "
                    f"floor after stripping SUPERSEDED/ok-stale clauses: {', '.join(thin)}"
                )
            if over_cap:
                over_cap.sort(key=lambda pair: pair[1], reverse=True)
                offenders = ", ".join(f"{dec_id} ({wc})" for dec_id, wc in over_cap)
                print(
                    f"FAIL - {name}: {len(over_cap)} row(s) in {REAL_INDEX} exceed the 30-word "
                    f"ruling cap after stripping SUPERSEDED/ok-stale clauses — shorten the ruling "
                    f"after ' :: ' on each listed row: {offenders}"
                )
            return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_orphaned_ruling_is_reported_not_silently_dropped():
    name = "test_orphaned_ruling_is_reported_not_silently_dropped"
    try:
        if not os.path.exists(GEN):
            print(f"FAIL - {name}: generator not found at {GEN}")
            return False

        with tempfile.TemporaryDirectory() as tmp:
            decisions = [(1, "First"), (2, "Second"), (3, "Third")]
            docs_dir = make_authority(tmp, decisions)
            rows_with_orphan = [
                "- DEC-1 @1 [] refs:  :: Chose Postgres for durability guarantees.",
                "- DEC-2 @1 [] refs:  :: Rejected in favor of the existing hook mechanism.",
                "- DEC-3 @1 [] refs:  :: Adopted the fence-guarded parse for correctness.",
                "- DEC-99 @1 [] refs:  :: This decision was renumbered or deleted upstream.",
            ]
            write_index(docs_dir, rows_with_orphan)
            index_path = os.path.join(docs_dir, "DECISIONS-INDEX.md")
            before = open(index_path, encoding="utf-8").read()

            r = run_gen(tmp)
            if r.returncode == 0:
                print(f"FAIL - {name}: expected non-zero exit for orphaned DEC-99 ruling, got 0")
                return False
            if "DEC-99" not in r.stderr:
                print(f"FAIL - {name}: DEC-99 not named on stderr: {r.stderr.strip()[:200]}")
                return False
            after = open(index_path, encoding="utf-8").read()
            if after != before:
                print(f"FAIL - {name}: index file was rewritten despite the orphan error")
                return False

            # Delete the orphan row; same fixture must now exit 0.
            rows_without_orphan = rows_with_orphan[:-1]
            write_index(docs_dir, rows_without_orphan)
            r2 = run_gen(tmp)
            if r2.returncode != 0:
                print(f"FAIL - {name}: expected exit 0 once orphan row is removed, got {r2.returncode}: {r2.stderr.strip()[:200]}")
                return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_malformed_row_is_reported_not_silently_dropped():
    """B-2: a line meant as a row but not matching the grammar must be a LOUD error.

    The old behaviour treated it as 'no prior row', so the DEC's hand-written ruling was
    replaced by the RULING PENDING sentinel and the index was rewritten — data loss
    recoverable only from git, and invisible in the exit code.
    """
    name = "test_malformed_row_is_reported_not_silently_dropped"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = [(1, "First"), (2, "Second")]
            docs_dir = make_authority(tmp, decisions)
            r0 = run_gen(tmp)
            if r0.returncode != 0:
                print(f"FAIL - {name}: baseline run exited {r0.returncode}")
                return False
            rows = read_index_rows(docs_dir)
            good = next(r for r in rows if r.startswith("- DEC-2 "))
            left, _ = good.split(" :: ", 1)
            # A single missing space around the separator is the whole defect.
            broken = f"{left} ::A ruling a human wrote and must not lose."
            write_index(docs_dir, [rows[0], broken])
            before = open(os.path.join(docs_dir, "DECISIONS-INDEX.md"), encoding="utf-8").read()

            r = run_gen(tmp)
            if r.returncode == 0:
                print(f"FAIL - {name}: generator exited 0 on a malformed row")
                return False
            after = open(os.path.join(docs_dir, "DECISIONS-INDEX.md"), encoding="utf-8").read()
            if after != before:
                print(f"FAIL - {name}: index was rewritten despite the error — "
                      f"the hand-written ruling must survive a refusal")
                return False
            err = r.stderr
            # The message must quote the line (so the fix is local) and must NOT tell the
            # reader to regenerate — regenerating is what destroys the other rulings.
            if "::A ruling a human wrote" not in err:
                print(f"FAIL - {name}: stderr does not quote the offending line: {err[:300]}")
                return False
            if "Repair" not in err:
                print(f"FAIL - {name}: stderr does not say to repair the line: {err[:300]}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_supersession_declared_in_body_prose_is_harvested():
    """B-3: DEC-120 supersedes DEC-102 in BODY prose, not in its title, so DEC-102's row
    carried no marker and a reader could act on a dead ruling.

    The negative half matters as much: a false marker tells a reader to ignore a LIVE
    decision, so a mid-sentence mention must not mark anything.
    """
    name = "test_supersession_declared_in_body_prose_is_harvested"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = [(1, "First"), (2, "Second"), (3, "Third")]
            bodies = {
                2: "**Supersedes DEC-1's conclusion** that the old shape was right.",
                # Narrative, not a declaration: must NOT mark DEC-2.
                3: "This one supersedes DEC-2 in spirit only, and refines DEC-1.",
            }
            docs_dir = make_authority(tmp, decisions, bodies)
            r = run_gen(tmp)
            if r.returncode != 0:
                print(f"FAIL - {name}: generator exited {r.returncode}: {r.stderr[:200]}")
                return False
            rows = {ROW_RE.match(l).group(1): l
                    for l in read_index_rows(docs_dir) if ROW_RE.match(l)}
            if "SUPERSEDED BY DEC-2" not in rows.get("DEC-1", ""):
                print(f"FAIL - {name}: DEC-1 lacks its body-declared marker: "
                      f"{rows.get('DEC-1')}")
                return False
            if "SUPERSEDED BY" in rows.get("DEC-2", ""):
                print(f"FAIL - {name}: DEC-2 was marked from a mid-sentence mention — "
                      f"a false marker hides a LIVE decision: {rows.get('DEC-2')}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_argv_is_validated_and_only_the_write_path_writes():
    """#140: every unrecognized flag — `--help` included — fell through to the WRITE path.

    The one command a reader runs to learn what the script does was the command that
    rewrote the repo. It fired during a review of PR #138 and mutated the reviewer's
    working tree, and because the index is generated the damage reads as a legitimate
    regeneration rather than an accident.

    Asserted on the file's BYTES, never on the exit code: pre-fix `--help` already exits
    0, so an exit-code assertion passes against the defect and proves nothing. The
    fixture's on-disk index is deliberately NOT what the generator emits (valid rows,
    but written without the HEADER) — against a byte-identical file the write path is
    indistinguishable from the read-only one and the test would be vacuous.
    """
    name = "test_argv_is_validated_and_only_the_write_path_writes"

    def fixture(tmp):
        docs_dir = make_authority(tmp, [(1, "First"), (2, "Second")])
        r0 = run_gen(tmp)
        assert r0.returncode == 0, f"baseline run exited {r0.returncode}: {r0.stderr[:200]}"
        # Rewrite the index in a form that still PARSES (so no run dies on MalformedRow
        # for the wrong reason) but that the generator would not reproduce.
        write_index(docs_dir, read_index_rows(docs_dir))
        path = os.path.join(docs_dir, "DECISIONS-INDEX.md")
        return path, open(path, encoding="utf-8").read()

    try:
        # (a) --help must print usage and touch nothing. THE red case.
        with tempfile.TemporaryDirectory() as tmp:
            path, before = fixture(tmp)
            r = run_gen(tmp, args=["--help"])
            if open(path, encoding="utf-8").read() != before:
                print(f"FAIL - {name} (a): --help REWROTE the index")
                return False
            if r.returncode != 0:
                print(f"FAIL - {name} (a): --help exited {r.returncode}")
                return False
            if "--stdout" not in r.stdout or "--help" not in r.stdout:
                print(f"FAIL - {name} (a): usage on stdout does not document both "
                      f"flags: {r.stdout[:300]!r}")
                return False

        # (b) An unknown flag must refuse loudly, not fall through to the write.
        with tempfile.TemporaryDirectory() as tmp:
            path, before = fixture(tmp)
            r = run_gen(tmp, args=["--check"])
            if open(path, encoding="utf-8").read() != before:
                print(f"FAIL - {name} (b): --check REWROTE the index")
                return False
            if r.returncode == 0:
                print(f"FAIL - {name} (b): unknown flag exited 0")
                return False
            # NOT `"--check" in r.stderr`: parse_argv dumps the whole docstring to
            # stderr and that docstring now contains the literal `--check`, so the
            # assertion passed on the docstring rather than on the error line. A
            # generic message naming no token satisfied it. Assert on the error LINE.
            first = r.stderr.strip().splitlines()[0] if r.stderr.strip() else ""
            if "--check" not in first:
                print(f"FAIL - {name} (b): the error LINE does not name the rejected "
                      f"flag: {first!r}")
                return False

        # (b2) A SINGLE-DASH unknown flag. THE GAP THE REVIEW FOUND: every unknown-flag
        # case above uses a double-dashed token, so `[a for a in argv if
        # a.startswith("--") and a != "--stdout"]` — a plausible wrong implementation —
        # passed the entire suite while still rewriting the index on `-x`. Reproduced:
        # mutant rc=0, index 45 -> 14914 bytes; shipped rc=2, untouched.
        with tempfile.TemporaryDirectory() as tmp:
            path, before = fixture(tmp)
            r = run_gen(tmp, args=["-x"])
            if open(path, encoding="utf-8").read() != before:
                print(f"FAIL - {name} (b2): a single-dash unknown flag REWROTE the index")
                return False
            if r.returncode == 0:
                print(f"FAIL - {name} (b2): single-dash unknown flag exited 0")
                return False

        # (b3) A POSITIONAL argument — no dash at all. Same class as (b2): a check
        # keyed on a leading `--` never sees it.
        with tempfile.TemporaryDirectory() as tmp:
            path, before = fixture(tmp)
            r = run_gen(tmp, args=["docs/harness/DECISIONS-INDEX.md"])
            if open(path, encoding="utf-8").read() != before:
                print(f"FAIL - {name} (b3): a positional argument REWROTE the index")
                return False
            if r.returncode == 0:
                print(f"FAIL - {name} (b3): positional argument exited 0")
                return False

        # (b4) `-h` is documented as an alias and was never exercised.
        with tempfile.TemporaryDirectory() as tmp:
            path, before = fixture(tmp)
            r = run_gen(tmp, args=["-h"])
            if open(path, encoding="utf-8").read() != before:
                print(f"FAIL - {name} (b4): -h REWROTE the index")
                return False
            if r.returncode != 0:
                print(f"FAIL - {name} (b4): -h exited {r.returncode}")
                return False

        # (c) Regression guard: --stdout still prints the index and still writes nothing.
        with tempfile.TemporaryDirectory() as tmp:
            path, before = fixture(tmp)
            r = run_gen(tmp, args=["--stdout"])
            if r.returncode != 0:
                print(f"FAIL - {name} (c): --stdout exited {r.returncode}: {r.stderr[:200]}")
                return False
            if "- DEC-1 " not in r.stdout:
                print(f"FAIL - {name} (c): --stdout printed no rows: {r.stdout[:200]!r}")
                return False
            if open(path, encoding="utf-8").read() != before:
                print(f"FAIL - {name} (c): --stdout wrote the index")
                return False

        # (d) Regression guard: no arguments still WRITES. Without this the whole fix
        # could be "never write", which passes (a)-(c) and breaks the only real caller.
        with tempfile.TemporaryDirectory() as tmp:
            path, before = fixture(tmp)
            r = run_gen(tmp)
            if r.returncode != 0:
                print(f"FAIL - {name} (d): no-args exited {r.returncode}: {r.stderr[:200]}")
                return False
            after = open(path, encoding="utf-8").read()
            if after == before or "# DECISIONS — index" not in after:
                print(f"FAIL - {name} (d): no-args did not regenerate the index")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


TESTS = [
    test_row_per_distinct_dec_matches_authority,
    test_argv_is_validated_and_only_the_write_path_writes,
    test_malformed_row_is_reported_not_silently_dropped,
    test_supersession_declared_in_body_prose_is_harvested,
    test_preserves_hand_written_rulings_by_dec_number,
    test_preserves_inline_ok_stale_marker_on_a_row,
    test_checker_scans_root_level_markdown,
    test_checker_flags_planted_stale_phrase_in_index,
    test_committed_index_is_complete_and_within_budget,
    test_orphaned_ruling_is_reported_not_silently_dropped,
]


def main():
    results = []
    for t in TESTS:
        try:
            results.append(t())
        except Exception as e:
            print(f"FAIL - {t.__name__}: {type(e).__name__}: {e}")
            results.append(False)

    if all(results):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
