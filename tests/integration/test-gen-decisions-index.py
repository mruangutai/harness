#!/usr/bin/env python3
"""Tests for gen-decisions-index.py, the generator of .harness/harness/docs/DECISIONS-INDEX.md.

Most tests run the generator on synthetic authorities in a tmp tree: row-per-decision,
ruling preservation, the ok-stale strip, malformed and orphaned rows, the refs graph, argv
handling and root resolution. The rest guard the committed index and the live authority:
the index matches a fresh regeneration and stays within budget, and the authority carries no
amendment construct and keeps the DEC-233 record. main() runs each test as one check, so one
test's exception never stops the others from running and reporting.
"""
from integration_support import ROOT, BIN  # first import: puts bin/ and tests/ on sys.path
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from functools import cache

from check_support import Checks

REPO_ROOT = str(ROOT)

# Overridable so a fix can be proven RED against a reverted copy — the same
# CHECK_STATE_BIN escape test-check-state.py uses.
GEN = os.environ.get("GEN_DECISIONS_INDEX_BIN") or str(BIN / "gen-decisions-index.py")

# The row grammar is IMPORTED, never restated (B-2). This test used to carry two of its
# own variants — `^- (DEC-\d+)\b(.*)$` and `^- (DEC-\d+).*?::\s*(.*)$` — and both were
# looser than the generator's about the ' :: ' separator, so a row the test happily
# parsed was one the generator silently treated as absent. Same importlib-by-path
# mechanism the other hyphenated-module tests use. Importing it is also the check that
# GEN exists.
_spec = importlib.util.spec_from_file_location("gen_decisions_index", GEN)
gdi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gdi)
DOCS_DIR = os.path.join(".harness", "harness", "docs")  # mirrors the generator's own constant
REAL_DECISIONS = os.path.join(REPO_ROOT, DOCS_DIR, "DECISIONS.md")
REAL_INDEX = os.path.join(REPO_ROOT, DOCS_DIR, "DECISIONS-INDEX.md")
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


def copy_real_authority(tmp):
    docs_dir = os.path.join(tmp, DOCS_DIR)
    os.makedirs(docs_dir, exist_ok=True)
    shutil.copy(REAL_DECISIONS, os.path.join(docs_dir, "DECISIONS.md"))
    return docs_dir


@cache
def real_stdout():
    """The real repo's `--stdout` run, computed once: no test writes to the real repo."""
    return subprocess.run([sys.executable, GEN, "--stdout"],
                          cwd=REPO_ROOT, capture_output=True, text=True)


def read_index_rows(docs_dir):
    path = os.path.join(docs_dir, "DECISIONS-INDEX.md")
    if not os.path.isfile(path):
        return None
    return [
        l for l in open(path, encoding="utf-8").read().splitlines()
        if l.startswith("- DEC-")
    ]


def test_row_per_distinct_dec_matches_authority():
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
        raise AssertionError(f"fence-guarded parse harvested MORE ids than the raw "
                             f"regex ({len(distinct)} > {len(raw)}) — the guard is adding ids")

    # The guard itself: a heading inside a fence must NOT be harvested.
    planted = text + "\n\n```\n## DEC-9999 — fenced, must not be harvested\n```\n"
    if "DEC-9999" in fence_guarded_dec_headings(planted):
        raise AssertionError("fence guard harvested a heading inside a code fence")
    if "DEC-9999" not in re.findall(r"^## (DEC-\d+)", planted, re.M):
        raise AssertionError("the planted fixture is wrong — the raw regex should see it")

    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = copy_real_authority(tmp)
        index_path = os.path.join(docs_dir, "DECISIONS-INDEX.md")
        r = run_gen(tmp)
        if r.returncode != 0:
            raise AssertionError(f"generator exited {r.returncode}: {r.stderr.strip()[:200]}")
        if not os.path.isfile(index_path):
            raise AssertionError(f"{index_path} not written")
        rows = read_index_rows(docs_dir)
        if len(rows) != len(distinct):
            raise AssertionError(f"expected {len(distinct)} rows (distinct DEC count), got {len(rows)}")


def test_preserves_hand_written_rulings_by_dec_number():
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
            raise AssertionError(f"generator exited {r.returncode}: {r.stderr.strip()[:200]}")

        new_rows = read_index_rows(docs_dir)
        if new_rows is None:
            raise AssertionError("index not written")

        by_dec = {}
        for row in new_rows:
            m = ROW_RE.match(row)
            if m:
                by_dec[m.group(1)] = m.group(2)

        for n in (1, 2, 3, 4, 5):
            dec = f"DEC-{n}"
            if dec not in by_dec:
                raise AssertionError(f"{dec} row missing after regeneration")
            if rulings[n] not in by_dec[dec]:
                raise AssertionError(f"{dec}'s hand-written ruling not preserved byte-identical")

        if "DEC-6" not in by_dec:
            raise AssertionError("DEC-6 row missing")
        if "RULING PENDING" not in by_dec["DEC-6"]:
            raise AssertionError("DEC-6 row missing RULING PENDING sentinel")


def test_strips_inline_ok_stale_marker_on_a_row():
    """The marker is STRIPPED, never preserved — the revival vector, closed.

    This test used to assert the opposite: that a hand-written row carrying
    `<!-- ok-stale -->` survived regeneration byte-identical. That was correct while
    the propagation checker existed. DEC-188 struck the checker whole, and a live
    plant then proved the emitter was a revival vector — the marker propagated
    through regeneration while check-state.py and the whole unit suite stayed green.
    Now the hand-written RULING must survive and the dead marker must not."""
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
            raise AssertionError(f"baseline generator run exited {r0.returncode}: {r0.stderr.strip()[:200]}")
        baseline_rows = read_index_rows(docs_dir)
        if not baseline_rows:
            raise AssertionError("baseline index not written or empty")
        dec3_baseline = next((row for row in baseline_rows if row.startswith("- DEC-3 ")), None)
        if dec3_baseline is None:
            raise AssertionError("baseline DEC-3 row missing")
        if " :: " not in dec3_baseline:
            raise AssertionError("baseline DEC-3 row has no ' :: ' separator")

        # Splice the hand-written ruling and marker into the generator's own
        # rendering of the DEC-3 row's left side.
        dec3_left, _ = dec3_baseline.split(" :: ", 1)
        expected = f"{dec3_left} :: Superseded wording retained for the migration map."
        marked_row = expected + " <!-- ok-stale -->"

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
            raise AssertionError(f"generator exited {r.returncode}: {r.stderr.strip()[:200]}")

        new_rows = read_index_rows(docs_dir)
        if new_rows is None:
            raise AssertionError("index not written")
        dec3_rows = [r_ for r_ in new_rows if r_.startswith("- DEC-3 ")]
        if not dec3_rows:
            raise AssertionError("DEC-3 row missing after regeneration")
        if "ok-stale" in dec3_rows[0]:
            raise AssertionError(f"the ok-stale marker survived regeneration — "
                                 f"the revival vector DEC-188 closed is open again: {dec3_rows[0]!r}")
        if dec3_rows[0] != expected:
            raise AssertionError(f"the hand-written ruling did not survive the strip "
                                 f"unchanged: {dec3_rows[0]!r}")


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
    if not os.path.isfile(REAL_INDEX):
        raise AssertionError(f"{REAL_INDEX} not found")

    r = real_stdout()
    if r.returncode != 0:
        raise AssertionError(f"generator exited {r.returncode} — the committed index "
                             f"cannot be reproduced: {r.stderr.strip()[:300]}")

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
        raise AssertionError(f".harness/harness/docs/DECISIONS-INDEX.md is not what the generator "
                             f"produces.{detail or ' (difference is outside the DEC rows)'} "
                             f"Fix: .agents/skills/harness/bin/gen-decisions-index.py")


def test_committed_index_is_complete_and_within_budget():
    # MF-2: the skip predicate is file-absence ONLY. A sentinel-bearing row
    # or a short ruling FAILS, never skips.
    if not os.path.isfile(REAL_INDEX):
        print("SKIP test_committed_index_is_complete_and_within_budget")
        return

    text = open(REAL_INDEX, encoding="utf-8").read()
    lines = text.splitlines()

    if "<!-- index-contract v1 -->" not in text:
        raise AssertionError("missing <!-- index-contract v1 --> marker")
    if len(lines) > 260:
        raise AssertionError(f"{len(lines)} lines exceeds 260-line budget")
    if "RULING PENDING" in text:
        unwritten = [
            m.group(1) for l in lines
            for m in [re.match(r"^- (DEC-\d+)", l)]
            if m and "RULING PENDING" in l
        ]
        raise AssertionError(f"{len(unwritten)} row(s) unwritten in {REAL_INDEX} — a decision was "
                             f"appended without its ruling. Run .agents/skills/harness/bin/gen-decisions-index.py "
                             f"and write the ruling after ' :: ' on each listed row, in this commit (REQ-09). "
                             f"Offending: {', '.join(unwritten)}"
                             )

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
    problems = []
    if thin:
        problems.append(
            f"{len(thin)} row(s) below the 20-non-whitespace-character prose "
            f"floor: {', '.join(thin)}"
        )
    if over_cap:
        over_cap.sort(key=lambda pair: pair[1], reverse=True)
        offenders = ", ".join(f"{dec_id} ({wc})" for dec_id, wc in over_cap)
        problems.append(
            f"{len(over_cap)} row(s) in {REAL_INDEX} exceed the 30-word "
            f"ruling cap — shorten the ruling after ' :: ' on each listed row: {offenders}"
        )
    if problems:
        raise AssertionError("\n".join(problems))


def test_orphaned_ruling_is_reported_not_silently_dropped():
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
            raise AssertionError("expected non-zero exit for orphaned DEC-99 ruling, got 0")
        if "DEC-99" not in r.stderr:
            raise AssertionError(f"DEC-99 not named on stderr: {r.stderr.strip()[:200]}")
        after = open(index_path, encoding="utf-8").read()
        if after != before:
            raise AssertionError("index file was rewritten despite the orphan error")

        # Delete the orphan row; same fixture must now exit 0.
        rows_without_orphan = rows_with_orphan[:-1]
        write_index(docs_dir, rows_without_orphan)
        r2 = run_gen(tmp)
        if r2.returncode != 0:
            raise AssertionError(f"expected exit 0 once orphan row is removed, got {r2.returncode}: {r2.stderr.strip()[:200]}")


def test_malformed_row_is_reported_not_silently_dropped():
    """B-2: a line meant as a row but not matching the grammar must be a LOUD error.

    The old behaviour treated it as 'no prior row', so the DEC's hand-written ruling was
    replaced by the RULING PENDING sentinel and the index was rewritten — data loss
    recoverable only from git, and invisible in the exit code.
    """
    with tempfile.TemporaryDirectory() as tmp:
        decisions = [(1, "First"), (2, "Second")]
        docs_dir = make_authority(tmp, decisions)
        r0 = run_gen(tmp)
        if r0.returncode != 0:
            raise AssertionError(f"baseline run exited {r0.returncode}")
        rows = read_index_rows(docs_dir)
        good = next(r for r in rows if r.startswith("- DEC-2 "))
        left, _ = good.split(" :: ", 1)
        # A single missing space around the separator is the whole defect.
        broken = f"{left} ::A ruling a human wrote and must not lose."
        write_index(docs_dir, [rows[0], broken])
        before = open(os.path.join(docs_dir, "DECISIONS-INDEX.md"), encoding="utf-8").read()

        r = run_gen(tmp)
        if r.returncode == 0:
            raise AssertionError("generator exited 0 on a malformed row")
        after = open(os.path.join(docs_dir, "DECISIONS-INDEX.md"), encoding="utf-8").read()
        if after != before:
            raise AssertionError("index was rewritten despite the error — "
                                 "the hand-written ruling must survive a refusal")
        err = r.stderr
        # The message must quote the line (so the fix is local) and must NOT tell the
        # reader to regenerate — regenerating is what destroys the other rulings.
        if "::A ruling a human wrote" not in err:
            raise AssertionError(f"stderr does not quote the offending line: {err[:300]}")
        if "Repair" not in err:
            raise AssertionError(f"stderr does not say to repair the line: {err[:300]}")


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
    with tempfile.TemporaryDirectory() as tmp:
        decisions = [(1, "First")]
        bodies = {1: "**Chose:** cites DEC-99, which has no live heading in this fixture."}
        docs_dir = make_authority(tmp, decisions, bodies)
        r = run_gen(tmp)
        if r.returncode != 0:
            raise AssertionError(f"generator exited {r.returncode}: {r.stderr[:200]}")
        rows = {ROW_RE.match(l).group(1): l
                for l in read_index_rows(docs_dir) if ROW_RE.match(l)}
        dec1_left = rows.get("DEC-1", "").split(" :: ", 1)[0]
        if "DEC-99" in dec1_left:
            raise AssertionError(f"refs graph names DEC-99 though it has no live "
                                 f"heading: {rows.get('DEC-1')!r}")

    with tempfile.TemporaryDirectory() as tmp:
        decisions = [(1, "First"), (99, "Ninety-nine")]
        bodies = {1: "**Chose:** cites DEC-99, which HAS a live heading in this fixture."}
        docs_dir = make_authority(tmp, decisions, bodies)
        r = run_gen(tmp)
        if r.returncode != 0:
            raise AssertionError(f"generator exited {r.returncode}: {r.stderr[:200]}")
        rows = {ROW_RE.match(l).group(1): l
                for l in read_index_rows(docs_dir) if ROW_RE.match(l)}
        dec1_left = rows.get("DEC-1", "").split(" :: ", 1)[0]
        if "DEC-99" not in dec1_left:
            raise AssertionError(f"refs graph drops DEC-99 though it has a live "
                                 f"heading — a filter that drops everything would also pass the "
                                 f"first half of this test: {rows.get('DEC-1')!r}")


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

    def fixture(tmp):
        docs_dir = make_authority(tmp, [(1, "First"), (2, "Second")])
        r0 = run_gen(tmp)
        assert r0.returncode == 0, f"baseline run exited {r0.returncode}: {r0.stderr[:200]}"
        # Rewrite the index in a form that still PARSES (so no run dies on MalformedRow
        # for the wrong reason) but that the generator would not reproduce.
        write_index(docs_dir, read_index_rows(docs_dir))
        path = os.path.join(docs_dir, "DECISIONS-INDEX.md")
        return path, open(path, encoding="utf-8").read()

    # (a) --help must print usage and touch nothing. THE red case.
    with tempfile.TemporaryDirectory() as tmp:
        path, before = fixture(tmp)
        r = run_gen(tmp, args=["--help"])
        if open(path, encoding="utf-8").read() != before:
            raise AssertionError("(a) --help REWROTE the index")
        if r.returncode != 0:
            raise AssertionError(f"(a) --help exited {r.returncode}")
        if "--stdout" not in r.stdout or "--help" not in r.stdout:
            raise AssertionError(f"(a) usage on stdout does not document both "
                                 f"flags: {r.stdout[:300]!r}")

    # (b) An unknown flag must refuse loudly, not fall through to the write.
    with tempfile.TemporaryDirectory() as tmp:
        path, before = fixture(tmp)
        r = run_gen(tmp, args=["--check"])
        if open(path, encoding="utf-8").read() != before:
            raise AssertionError("(b) --check REWROTE the index")
        if r.returncode == 0:
            raise AssertionError("(b) unknown flag exited 0")
        # NOT `"--check" in r.stderr`: parse_argv dumps the whole docstring to
        # stderr and that docstring now contains the literal `--check`, so the
        # assertion passed on the docstring rather than on the error line. A
        # generic message naming no token satisfied it. Assert on the error LINE.
        first = r.stderr.strip().splitlines()[0] if r.stderr.strip() else ""
        if "--check" not in first:
            raise AssertionError(f"(b) the error LINE does not name the rejected "
                                 f"flag: {first!r}")

    # (b2) A SINGLE-DASH unknown flag. THE GAP THE REVIEW FOUND: every unknown-flag
    # case above uses a double-dashed token, so `[a for a in argv if
    # a.startswith("--") and a != "--stdout"]` — a plausible wrong implementation —
    # passed the entire suite while still rewriting the index on `-x`. Reproduced:
    # mutant rc=0, index 45 -> 14914 bytes; shipped rc=2, untouched.
    with tempfile.TemporaryDirectory() as tmp:
        path, before = fixture(tmp)
        r = run_gen(tmp, args=["-x"])
        if open(path, encoding="utf-8").read() != before:
            raise AssertionError("(b2) a single-dash unknown flag REWROTE the index")
        if r.returncode == 0:
            raise AssertionError("(b2) single-dash unknown flag exited 0")

    # (b3) A POSITIONAL argument — no dash at all. Same class as (b2): a check
    # keyed on a leading `--` never sees it.
    with tempfile.TemporaryDirectory() as tmp:
        path, before = fixture(tmp)
        r = run_gen(tmp, args=[".harness/harness/docs/DECISIONS-INDEX.md"])
        if open(path, encoding="utf-8").read() != before:
            raise AssertionError("(b3) a positional argument REWROTE the index")
        if r.returncode == 0:
            raise AssertionError("(b3) positional argument exited 0")

    # (b4) `-h` is documented as an alias and was never exercised.
    with tempfile.TemporaryDirectory() as tmp:
        path, before = fixture(tmp)
        r = run_gen(tmp, args=["-h"])
        if open(path, encoding="utf-8").read() != before:
            raise AssertionError("(b4) -h REWROTE the index")
        if r.returncode != 0:
            raise AssertionError(f"(b4) -h exited {r.returncode}")

    # (c) Regression guard: --stdout still prints the index and still writes nothing.
    with tempfile.TemporaryDirectory() as tmp:
        path, before = fixture(tmp)
        r = run_gen(tmp, args=["--stdout"])
        if r.returncode != 0:
            raise AssertionError(f"(c) --stdout exited {r.returncode}: {r.stderr[:200]}")
        if "- DEC-1 " not in r.stdout:
            raise AssertionError(f"(c) --stdout printed no rows: {r.stdout[:200]!r}")
        if open(path, encoding="utf-8").read() != before:
            raise AssertionError("(c) --stdout wrote the index")

    # (d) Regression guard: no arguments still WRITES. Without this the whole fix
    # could be "never write", which passes (a)-(c) and breaks the only real caller.
    with tempfile.TemporaryDirectory() as tmp:
        path, before = fixture(tmp)
        r = run_gen(tmp)
        if r.returncode != 0:
            raise AssertionError(f"(d) no-args exited {r.returncode}: {r.stderr[:200]}")
        after = open(path, encoding="utf-8").read()
        if after == before or "# DECISIONS — index" not in after:
            raise AssertionError("(d) no-args did not regenerate the index")


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
    with tempfile.TemporaryDirectory() as tmp:
        # (a) HARNESS_PROJECT_DIR set, no marker -> discarded loudly, falls back to
        # the real repo root (which carries MARKER), matches the real --stdout output.
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        env["HARNESS_PROJECT_DIR"] = tmp
        r = subprocess.run([sys.executable, GEN, "--stdout"], cwd=tmp,
                            capture_output=True, text=True, env=env)
        if r.returncode != 0:
            raise AssertionError(f"(a) a markerless HARNESS_PROJECT_DIR override "
                                 f"exited {r.returncode}: {r.stderr.strip()[:200]}")
        if "team-config.yaml" not in r.stderr:
            raise AssertionError(f"(a) discarding the markerless override did not "
                                 f"name the missing marker on stderr: {r.stderr.strip()[-300:]!r}")
        if r.stdout != real_stdout().stdout:
            raise AssertionError("(a) fallback root did not produce the real repo's "
                                 "own output")

    with tempfile.TemporaryDirectory() as tmp:
        # (b) CLAUDE_PROJECT_DIR alone (retired name) does not redirect the root.
        copy_real_authority(tmp)
        env = dict(os.environ)
        env.pop("HARNESS_PROJECT_DIR", None)
        env["CLAUDE_PROJECT_DIR"] = tmp
        r = subprocess.run([sys.executable, GEN, "--stdout"], cwd=tmp,
                            capture_output=True, text=True, env=env)
        if r.returncode != 0:
            raise AssertionError(f"(b) expected the real repo's DECISIONS.md to be "
                                 f"read (CLAUDE_PROJECT_DIR ignored), generator exited "
                                 f"{r.returncode}: {r.stderr.strip()[:200]}")
        if r.stdout != real_stdout().stdout:
            raise AssertionError("(b) CLAUDE_PROJECT_DIR redirected the root — "
                                 "output diverged from the real repo's own --stdout")

    with tempfile.TemporaryDirectory() as tmp:
        # (c) HARNESS_PROJECT_DIR + marker IS honoured.
        copy_real_authority(tmp)
        r = run_gen(tmp, args=["--stdout"])
        if r.returncode != 0:
            raise AssertionError(f"(c) marker-carrying HARNESS_PROJECT_DIR exited "
                                 f"{r.returncode}: {r.stderr.strip()[:300]}")
        if "- DEC-01 " not in r.stdout:
            raise AssertionError(f"(c) did not regenerate against the tmp tree: "
                                 f"{r.stdout[:200]!r}")


def test_no_amendment_construct_survives_in_the_authority():
    """FEAT-38 T-10: the generator's amendment machinery was deleted entirely, so a
    line in the LIVE authority that starts a new amendment construct would be revived
    as a live am.N token by nobody — it just gets silently ignored. Guard the authority
    itself, not the generator, since the generator no longer has any code to police.
    """
    path = os.path.join(REPO_ROOT, gdi.DECISIONS_PATH)
    lines = open(path, encoding="utf-8").read().splitlines()

    patterns = [
        (r"^###\s+DEC-[0-9]+\s+amendment", "'### DEC-N amendment' heading"),
        (r"^\*\*Amendment", "'**Amendment' line"),
        (r"am\.\d", "'am.<digit>' token"),
    ]
    found = []
    for pattern, label in patterns:
        hits = [n for n, line in enumerate(lines, 1) if re.search(pattern, line)]
        if hits:
            found.append(f"{label} found at {path}:{hits}")
    if found:
        raise AssertionError("; ".join(found))


HOST_REMOVAL_DEC = "DEC-233"


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


def test_dec_233_entry_names_every_removed_enforcement_point():
    """DEC-233 deleted DEC-210 whole (DEC-205: supersession is deletion). The live
    authority must carry no DEC-210 heading, and the DEC-233 region must name each
    enforcement point it removed, so a re-added branch has a recorded ruling to
    contradict. Each clause is checked separately."""
    path = os.path.join(REPO_ROOT, gdi.DECISIONS_PATH)
    text = open(path, encoding="utf-8").read()
    if _dec_region(text, "DEC-210") is not None:
        raise AssertionError(f"'## DEC-210' still has a live heading in {path}")
    region = _dec_region(text, HOST_REMOVAL_DEC)
    if region is None:
        raise AssertionError(f"no '## {HOST_REMOVAL_DEC}' heading found in {path}")
    for needle in ("check-domain.py", "plan-sign-gate.py", "validate-digest.py",
                   "quarantine.py", "dispatch-guard.py", "SUSPENDED", "INV-9"):
        if needle not in region:
            raise AssertionError(f"'{needle}' not found in the "
                                 f"{HOST_REMOVAL_DEC} region of {path}")


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
    test_dec_233_entry_names_every_removed_enforcement_point,
]


def main():
    C = Checks()
    for t in TESTS:
        try:
            t()
            C.check(t.__name__, True)
        except Exception as e:
            C.check(t.__name__, False, f"{type(e).__name__}: {e}")
    sys.exit(C.report())


if __name__ == "__main__":
    main()
