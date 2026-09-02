#!/usr/bin/env python3
"""Tests for the (not-yet-existent) DECISIONS-INDEX.md generator, written first
per FEAT-04-decisions-index T-01 — this is the RED deliverable.

Six tests. Four of them exercise the generator directly and fail-by-design at
T-01 because `gen-decisions-index.py` does not exist yet. Test 4 exercises the
already-shipped generator and is expected to be green today. Test 5
exercises the committed `.harness/harness/docs/DECISIONS-INDEX.md`, which does not
exist yet either, and SKIPs by design (file-absence only — see its docstring).

Each test is wrapped in its own try/except in main() so one test's exception
never prevents the other five from running and reporting.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))
DOCS_DIR = os.path.join(".harness", "harness", "docs")  # mirrors the generator's own constant
REAL_DECISIONS = os.path.join(REPO_ROOT, DOCS_DIR, "DECISIONS.md")
REAL_INDEX = os.path.join(REPO_ROOT, DOCS_DIR, "DECISIONS-INDEX.md")

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
    """Mirror the fence toggle exactly: a '## DEC-N'
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


def run_gen(tree, extra_env=None, args=None):
    # The generator resolves its root via harness_boundary.resolve_root, which reads
    # HARNESS_PROJECT_DIR only and requires the override to carry team-config.yaml
    # (MARKER) — CLAUDE_PROJECT_DIR no longer redirects it at all (FEAT-42 T-05).
    os.makedirs(os.path.join(tree, ".harness"), exist_ok=True)
    marker = os.path.join(tree, ".harness", "team-config.yaml")
    if not os.path.exists(marker):
        open(marker, "w", encoding="utf-8").write("")
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    env["HARNESS_PROJECT_DIR"] = tree
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, GEN] + list(args or []),
        cwd=tree, capture_output=True, text=True, env=env
    )


def make_authority(tmp, decisions, bodies=None):
    """decisions: list of (number:int, title:str). Writes .harness/harness/docs/DECISIONS.md.

    bodies: optional {number: body_text} to override a decision's placeholder body,
    for the cases where the BODY is what is under test (supersession prose, B-3).
    """
    bodies = bodies or {}
    docs_dir = os.path.join(tmp, DOCS_DIR)
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

        # ASSERT THE RELATIONSHIP, NEVER A FROZEN TOTAL (issue #5). Zero fenced
        # duplicates is a legitimate state of the live document, so this checks a
        # relationship (harvested ids never exceed the raw count, and never repeat)
        # rather than pinning the duplicate count to any one figure.
        #
        # So the live file now carries only the invariants that must always hold,
        # and the fence guard is proven against a SYNTHETIC fixture below — which is
        # stronger, because it fails when the guard breaks rather than when someone
        # edits an unrelated decision.
        if len(raw) < len(distinct):
            print(f"FAIL - {name}: fence-guarded parse harvested MORE ids than the raw "
                  f"regex ({len(distinct)} > {len(raw)}) — the guard is adding ids")
            return False
        if len(distinct) != len(set(distinct)):
            print(f"FAIL - {name}: fence-guarded parse yielded duplicate ids")
            return False

        # The guard itself: a heading inside a fence must NOT be harvested.
        planted = text + "\n\n```\n## DEC-9999 — fenced, must not be harvested\n```\n"
        if "DEC-9999" in fence_guarded_dec_headings(planted):
            print(f"FAIL - {name}: fence guard harvested a heading inside a code fence")
            return False
        if "DEC-9999" not in re.findall(r"^## (DEC-\d+)", planted, re.M):
            print(f"FAIL - {name}: the planted fixture is wrong — the raw regex should see it")
            return False

        if not os.path.exists(GEN):
            print(f"FAIL - {name}: generator not found at {GEN}")
            return False

        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = os.path.join(tmp, DOCS_DIR)
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


def test_strips_inline_ok_stale_marker_on_a_row():
    """The marker is STRIPPED, never preserved — the revival vector, closed.

    This test used to assert the opposite: that a hand-written row carrying
    `<!-- ok-stale -->` survived regeneration byte-identical. That was correct while
    the propagation checker existed. DEC-188 struck the checker whole, and a live
    plant then proved the emitter was a revival vector — the marker propagated
    through regeneration while check-state.sh and the whole unit suite stayed green.
    Now the hand-written RULING must survive and the dead marker must not."""
    name = "test_strips_inline_ok_stale_marker_on_a_row"
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
            if "ok-stale" in dec3_rows[0]:
                print(f"FAIL - {name}: the ok-stale marker survived regeneration — "
                      f"the revival vector DEC-188 closed is open again: {dec3_rows[0]!r}")
                return False
            if dec3_rows[0] != marked_row.replace(" <!-- ok-stale -->", "").replace("<!-- ok-stale -->", "").rstrip():
                print(f"FAIL - {name}: the hand-written ruling did not survive the strip "
                      f"unchanged: {dec3_rows[0]!r}")
                return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_committed_index_matches_a_fresh_regeneration():
    """The committed index must BE what the generator produces. Nothing checked this.

    Found by mutant testing during the #202 review. Two mutants against the committed
    file: a DELETED row and a SPURIOUS row for a decision with no heading. The whole
    suite stayed green for both, because every other test regenerates into a tmp dir
    and compares counts — none of them reads REAL_INDEX and diffs it.

    Only half the gap was real. The generator ALREADY exits 1 on the spurious row
    (`ORPHAN: … has a ruling in the index but no live heading`), measured. The deleted
    row is the silent one, and it self-heals on the next regeneration — so the window
    is narrow, and this test closes it rather than guarding a disaster.

    THE COST, STATED SO NOBODY IS SURPRISED BY IT: this goes red when someone edits
    DECISIONS.md and has not yet run the generator. That is the "punishes writing a
    decision rather than catching a defect" trap this file warns about elsewhere, and
    it is accepted here because the remedy is one command the failure message names.
    """
    name = "test_committed_index_matches_a_fresh_regeneration"
    try:
        if not os.path.exists(GEN):
            print(f"FAIL - {name}: generator not found at {GEN}")
            return False
        if not os.path.isfile(REAL_INDEX):
            print(f"FAIL - {name}: {REAL_INDEX} not found")
            return False

        r = subprocess.run([sys.executable, GEN, "--stdout"],
                           cwd=REPO_ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL - {name}: generator exited {r.returncode} — the committed index "
                  f"cannot be reproduced: {r.stderr.strip()[:300]}")
            return False

        fresh = r.stdout.splitlines()
        committed = open(REAL_INDEX, encoding="utf-8").read().splitlines()
        if fresh != committed:
            only_committed = [l for l in committed if l not in fresh and l.startswith("- DEC-")]
            only_fresh = [l for l in fresh if l not in committed and l.startswith("- DEC-")]
            detail = ""
            if only_committed:
                detail += f" rows in the file the generator does not produce: {only_committed[:3]}"
            if only_fresh:
                detail += f" rows the generator produces that the file lacks: {only_fresh[:3]}"
            print(f"FAIL - {name}: .harness/harness/docs/DECISIONS-INDEX.md is not what the generator "
                  f"produces.{detail or ' (difference is outside the DEC rows)'} "
                  f"Fix: .agents/skills/harness/bin/gen-decisions-index.py")
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
                f"appended without its ruling. Run .agents/skills/harness/bin/gen-decisions-index.py "
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
            non_ws = re.sub(r"\s+", "", ruling)
            if len(non_ws) < 20:
                thin.append(dec_id)
            word_count = len(ruling.split())
            if word_count > 30:
                over_cap.append((dec_id, word_count))
        if thin or over_cap:
            if thin:
                print(
                    f"FAIL - {name}: {len(thin)} row(s) below the 20-non-whitespace-character prose "
                    f"floor: {', '.join(thin)}"
                )
            if over_cap:
                over_cap.sort(key=lambda pair: pair[1], reverse=True)
                offenders = ", ".join(f"{dec_id} ({wc})" for dec_id, wc in over_cap)
                print(
                    f"FAIL - {name}: {len(over_cap)} row(s) in {REAL_INDEX} exceed the 30-word "
                    f"ruling cap — shorten the ruling after ' :: ' on each listed row: {offenders}"
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


def test_refs_graph_omits_ids_with_no_live_heading():
    """CHANGE 2 (FEAT-38 T-06): the refs graph must never name a DEC with no live
    heading. Standing defect at 7ebfc9e: the generator scraped DEC ids out of
    prose that merely DESCRIBES a deletion, so a row could cite a DEC with no
    '## DEC-NNN' heading anywhere in DECISIONS.md.

    Both directions are asserted against a SYNTHETIC fixture built here, never
    the live document: a cited-but-headingless id must be OMITTED from refs,
    and the same fixture with the heading present must INCLUDE it — a filter
    that drops everything would pass the first half alone.
    """
    name = "test_refs_graph_omits_ids_with_no_live_heading"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = [(1, "First")]
            bodies = {1: "**Chose:** cites DEC-99, which has no live heading in this fixture."}
            docs_dir = make_authority(tmp, decisions, bodies)
            r = run_gen(tmp)
            if r.returncode != 0:
                print(f"FAIL - {name}: generator exited {r.returncode}: {r.stderr[:200]}")
                return False
            rows = {ROW_RE.match(l).group(1): l
                    for l in read_index_rows(docs_dir) if ROW_RE.match(l)}
            dec1_left = rows.get("DEC-1", "").split(" :: ", 1)[0]
            if "DEC-99" in dec1_left:
                print(f"FAIL - {name}: refs graph names DEC-99 though it has no live "
                      f"heading: {rows.get('DEC-1')!r}")
                return False

        with tempfile.TemporaryDirectory() as tmp:
            decisions = [(1, "First"), (99, "Ninety-nine")]
            bodies = {1: "**Chose:** cites DEC-99, which HAS a live heading in this fixture."}
            docs_dir = make_authority(tmp, decisions, bodies)
            r = run_gen(tmp)
            if r.returncode != 0:
                print(f"FAIL - {name}: generator exited {r.returncode}: {r.stderr[:200]}")
                return False
            rows = {ROW_RE.match(l).group(1): l
                    for l in read_index_rows(docs_dir) if ROW_RE.match(l)}
            dec1_left = rows.get("DEC-1", "").split(" :: ", 1)[0]
            if "DEC-99" not in dec1_left:
                print(f"FAIL - {name}: refs graph drops DEC-99 though it has a live "
                      f"heading — a filter that drops everything would also pass the "
                      f"first half of this test: {rows.get('DEC-1')!r}")
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
            r = run_gen(tmp, args=[".harness/harness/docs/DECISIONS-INDEX.md"])
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


def test_root_resolves_through_harness_boundary_not_the_retired_variable():
    """FEAT-42 T-05: the generator's root comes from `harness_boundary.resolve_root`,
    never from CLAUDE_PROJECT_DIR or a bare cwd fallback.

    (a) An override that does not carry team-config.yaml (MARKER) must not be silently
    honoured — the old chain would `os.chdir` straight into it and either crash on a
    missing DECISIONS.md or, worse, quietly walk back to whatever `os.getcwd()` was.
    The new resolver discards it LOUDLY on stderr (naming both candidates) rather than
    chdir-ing into it, and falls back to the real repo root, which does carry MARKER.
    (b) CLAUDE_PROJECT_DIR alone (the retired name) must NOT redirect the root at all
    — only HARNESS_PROJECT_DIR does. A tmp dir with no marker, addressed only via
    CLAUDE_PROJECT_DIR, must fall through to the real derived root rather than error,
    proving the retired variable is inert.
    (c) HARNESS_PROJECT_DIR pointing at a directory that DOES carry the marker must be
    honoured — the generator reads and writes inside that tree, not the real repo.
    """
    name = "test_root_resolves_through_harness_boundary_not_the_retired_variable"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # (a) HARNESS_PROJECT_DIR set, no marker -> discarded loudly, falls back to
            # the real repo root (which carries MARKER), matches the real --stdout output.
            env = dict(os.environ)
            env.pop("CLAUDE_PROJECT_DIR", None)
            env["HARNESS_PROJECT_DIR"] = tmp
            r = subprocess.run([sys.executable, GEN, "--stdout"], cwd=tmp,
                                capture_output=True, text=True, env=env)
            if r.returncode != 0:
                print(f"FAIL - {name} (a): a markerless HARNESS_PROJECT_DIR override "
                      f"exited {r.returncode}: {r.stderr.strip()[:200]}")
                return False
            if "team-config.yaml" not in r.stderr:
                print(f"FAIL - {name} (a): discarding the markerless override did not "
                      f"name the missing marker on stderr: {r.stderr.strip()[-300:]!r}")
                return False
            real_stdout = subprocess.run([sys.executable, GEN, "--stdout"], cwd=REPO_ROOT,
                                          capture_output=True, text=True).stdout
            if r.stdout != real_stdout:
                print(f"FAIL - {name} (a): fallback root did not produce the real repo's "
                      f"own output")
                return False

        with tempfile.TemporaryDirectory() as tmp:
            # (b) CLAUDE_PROJECT_DIR alone (retired name) does not redirect the root.
            docs_dir = os.path.join(tmp, DOCS_DIR)
            os.makedirs(docs_dir, exist_ok=True)
            shutil.copy(REAL_DECISIONS, os.path.join(docs_dir, "DECISIONS.md"))
            env = dict(os.environ)
            env.pop("HARNESS_PROJECT_DIR", None)
            env["CLAUDE_PROJECT_DIR"] = tmp
            r = subprocess.run([sys.executable, GEN, "--stdout"], cwd=tmp,
                                capture_output=True, text=True, env=env)
            if r.returncode != 0:
                print(f"FAIL - {name} (b): expected the real repo's DECISIONS.md to be "
                      f"read (CLAUDE_PROJECT_DIR ignored), generator exited "
                      f"{r.returncode}: {r.stderr.strip()[:200]}")
                return False
            real_stdout = subprocess.run([sys.executable, GEN, "--stdout"], cwd=REPO_ROOT,
                                          capture_output=True, text=True).stdout
            if r.stdout != real_stdout:
                print(f"FAIL - {name} (b): CLAUDE_PROJECT_DIR redirected the root — "
                      f"output diverged from the real repo's own --stdout")
                return False

        with tempfile.TemporaryDirectory() as tmp:
            # (c) HARNESS_PROJECT_DIR + marker IS honoured.
            docs_dir = os.path.join(tmp, DOCS_DIR)
            os.makedirs(docs_dir, exist_ok=True)
            shutil.copy(REAL_DECISIONS, os.path.join(docs_dir, "DECISIONS.md"))
            os.makedirs(os.path.join(tmp, ".harness"), exist_ok=True)
            open(os.path.join(tmp, ".harness", "team-config.yaml"), "w",
                 encoding="utf-8").write("")
            env = dict(os.environ)
            env.pop("CLAUDE_PROJECT_DIR", None)
            env["HARNESS_PROJECT_DIR"] = tmp
            r = subprocess.run([sys.executable, GEN, "--stdout"], cwd=tmp,
                                capture_output=True, text=True, env=env)
            if r.returncode != 0:
                print(f"FAIL - {name} (c): marker-carrying HARNESS_PROJECT_DIR exited "
                      f"{r.returncode}: {r.stderr.strip()[:300]}")
                return False
            if "- DEC-01 " not in r.stdout:
                print(f"FAIL - {name} (c): did not regenerate against the tmp tree: "
                      f"{r.stdout[:200]!r}")
                return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_no_amendment_construct_survives_in_the_authority():
    """FEAT-38 T-10: the generator's amendment machinery was deleted entirely, so a
    line in the LIVE authority that starts a new amendment construct would be revived
    as a live am.N token by nobody — it just gets silently ignored. Guard the authority
    itself, not the generator, since the generator no longer has any code to police.
    """
    name = "test_no_amendment_construct_survives_in_the_authority"
    try:
        path = os.path.join(REPO_ROOT, gdi.DECISIONS_PATH)
        lines = open(path, encoding="utf-8").read().splitlines()

        heading_hits = [
            n for n, line in enumerate(lines, 1)
            if re.match(r"^###\s+DEC-[0-9]+\s+amendment", line)
        ]
        if heading_hits:
            print(f"FAIL - {name}: '### DEC-N amendment' heading found at "
                  f"{path}:{heading_hits}")
            return False

        bold_hits = [
            n for n, line in enumerate(lines, 1)
            if re.match(r"^\*\*Amendment", line)
        ]
        if bold_hits:
            print(f"FAIL - {name}: '**Amendment' line found at {path}:{bold_hits}")
            return False

        am_dot_hits = [
            n for n, line in enumerate(lines, 1)
            if re.search(r"am\.\d", line)
        ]
        if am_dot_hits:
            print(f"FAIL - {name}: 'am.<digit>' token found at {path}:{am_dot_hits}")
            return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


# T-06 lands the Claude Code lifecycle-safety decision as DEC-210; if that number is
# already taken when T-06 runs, T-06 takes the next free number and this constant
# moves with it.
QUARANTINE_DEC = "DEC-210"


def _dec_region(text, dec):
    """Return the live-authority slice from the '## <dec>' heading to the next
    '## DEC-N' heading outside a fence, or to end of file — bounded on BOTH sides so
    a later entry's text can never satisfy a clause meant for this one. Mirrors
    fence_guarded_dec_headings's fence toggle exactly so a heading inside a ```
    fence is never taken as a region boundary. Returns None when <dec> has no live
    heading."""
    lines = text.splitlines()
    start = None
    infence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            infence = not infence
            continue
        if infence:
            continue
        if start is None:
            if re.match(rf"^##\s+{re.escape(dec)}\b", line):
                start = i
            continue
        if re.match(r"^##\s+DEC-\d+", line):
            return "\n".join(lines[start:i])
    if start is None:
        return None
    return "\n".join(lines[start:])


def test_dec_210_entry_names_both_enforcement_points():
    """T-08 (SC-09): a DEC-210 entry that omits the plan-sign-gate.sh half ships
    graded met unless something asserts its content. Guards the LIVE authority, not a
    fixture, and checks each clause separately so the clauses that hold never blind
    the check to the one that does not."""
    name = "test_dec_210_entry_names_both_enforcement_points"
    try:
        path = os.path.join(REPO_ROOT, gdi.DECISIONS_PATH)
        text = open(path, encoding="utf-8").read()
        region = _dec_region(text, QUARANTINE_DEC)
        if region is None:
            print(f"FAIL - {name}: no '## {QUARANTINE_DEC}' heading found in {path}")
            return False

        if "check-domain.sh" not in region:
            print(f"FAIL - {name}: 'check-domain.sh' not found in the "
                  f"{QUARANTINE_DEC} region of {path}")
            return False

        if "plan-sign-gate.sh" not in region:
            print(f"FAIL - {name}: 'plan-sign-gate.sh' not found in the "
                  f"{QUARANTINE_DEC} region of {path}")
            return False

        if "quarantine.py adopt" not in region:
            print(f"FAIL - {name}: 'quarantine.py adopt' not found in the "
                  f"{QUARANTINE_DEC} region of {path}")
            return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_dec_210_entry_states_the_bash_write_route_for_plan_yaml():
    """Same region as test_dec_210_entry_names_both_enforcement_points, newlines
    collapsed to single spaces so a sentence wrapped across lines still matches.
    Requires 'plan.yaml' and 'plan-merge.py' to occur in ONE sentence — a
    whole-region search for both names is satisfied by two unrelated sentences,
    which is exactly the entry this test exists to reject."""
    name = "test_dec_210_entry_states_the_bash_write_route_for_plan_yaml"
    try:
        path = os.path.join(REPO_ROOT, gdi.DECISIONS_PATH)
        text = open(path, encoding="utf-8").read()
        region = _dec_region(text, QUARANTINE_DEC)
        if region is None:
            print(f"FAIL - {name}: no '## {QUARANTINE_DEC}' heading found in {path}")
            return False

        collapsed = re.sub(r"\n+", " ", region)

        if not re.search(r"\bBash\b", collapsed):
            print(f"FAIL - {name}: 'Bash' not found as a whole word in the "
                  f"{QUARANTINE_DEC} region of {path}")
            return False

        sentences = collapsed.split(". ")
        if not any("plan.yaml" in s and "plan-merge.py" in s for s in sentences):
            print(f"FAIL - {name}: no single sentence in the {QUARANTINE_DEC} "
                  f"region of {path} names both 'plan.yaml' and 'plan-merge.py'")
            return False

        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_dec_210_index_row_names_the_compatibility_host_in_the_ruling():
    """Closes SC-09's last ungraded clause: the DECISIONS-INDEX.md row must name the
    compatibility host in the hand-written ruling half, ROW_RE group(2) — not merely
    anywhere in the row, since the generated left half (group(1) onward, before the
    ' :: ' separator) is a failure a whole-row search cannot see."""
    name = "test_dec_210_index_row_names_the_compatibility_host_in_the_ruling"
    try:
        lines = open(REAL_INDEX, encoding="utf-8").read().splitlines()
        row = None
        for line in lines:
            m = ROW_RE.match(line)
            if m and m.group(1) == QUARANTINE_DEC:
                row = m
                break
        if row is None:
            print(f"FAIL - {name}: no ROW_RE row for {QUARANTINE_DEC} found in "
                  f"{REAL_INDEX}")
            return False

        ruling = row.group(2)
        if "Claude Code" not in ruling:
            print(f"FAIL - {name}: 'Claude Code' not found in the ruling half of "
                  f"the {QUARANTINE_DEC} row in {REAL_INDEX}")
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
    test_refs_graph_omits_ids_with_no_live_heading,
    test_preserves_hand_written_rulings_by_dec_number,
    test_strips_inline_ok_stale_marker_on_a_row,
    test_committed_index_matches_a_fresh_regeneration,
    test_committed_index_is_complete_and_within_budget,
    test_orphaned_ruling_is_reported_not_silently_dropped,
    test_root_resolves_through_harness_boundary_not_the_retired_variable,
    test_no_amendment_construct_survives_in_the_authority,
    test_dec_210_entry_names_both_enforcement_points,
    test_dec_210_entry_states_the_bash_write_route_for_plan_yaml,
    test_dec_210_index_row_names_the_compatibility_host_in_the_ruling,
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
