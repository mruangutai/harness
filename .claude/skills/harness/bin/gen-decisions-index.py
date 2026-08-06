#!/usr/bin/env python3
"""Generate docs/harness/DECISIONS-INDEX.md from docs/harness/DECISIONS.md.

Usage:
    gen-decisions-index.py            write docs/harness/DECISIONS-INDEX.md in place
    gen-decisions-index.py --stdout   write the index to stdout, touch nothing
    gen-decisions-index.py --help     print this and exit, touch nothing (also -h)

There is no --check: to check for drift without writing, pipe the read-only mode into
diff — `gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md`.

See FEAT-04-decisions-index PLAN.md T-02 for the full contract. Everything left
of ' :: ' on a row is generated; everything right of it is hand-written and
preserved verbatim across regeneration.
"""
import os
import re
import sys

DOCS_DIR = os.path.join("docs", "harness")
DECISIONS_PATH = os.path.join(DOCS_DIR, "DECISIONS.md")
INDEX_PATH = os.path.join(DOCS_DIR, "DECISIONS-INDEX.md")

HEADING_RE = re.compile(r"^##\s+(DEC-(\d+))\b")
AMEND_HEADING_RE = re.compile(r"^###\s+DEC-(\d+)\s+amendment(?:\s+(\d+))?\b")
AMEND_BOLD_RE = re.compile(r"^\*\*Amendment(?:\s+(\d+))?\b")
DEC_REF_RE = re.compile(r"DEC-(\d+)")
SUPERSESSION_VERB_RE = re.compile(r"^(SUPERSEDES|CORRECTS|INVERTS)\s+(DEC-\d+)")
# A supersession declared in BODY PROSE rather than in the title (B-3). DEC-120 supersedes
# DEC-102 this way, and DEC-102's row carried no marker — so a reader could act on a dead
# ruling, which is the one failure the marker exists to prevent.
#
# Anchored deliberately hard: line-start, inside the bold run that opens the paragraph, and
# the verb must govern the DEC directly. Narrative mentions ("this supersedes nothing",
# "DEC-99 supersedes an earlier draft" mid-sentence) must NOT mark a row, because a false
# marker tells a reader to ignore a LIVE decision — worse than the missing marker it fixes.
BODY_SUPERSESSION_RE = re.compile(
    r"^\*\*(Supersedes|Corrects|Inverts|SUPERSEDES|CORRECTS|INVERTS)\s+(DEC-\d+)",
    re.M,
)

TOPIC_VOCAB = {
    "org": ("org",),
    "cost": ("cost",),
    "gates": ("gates",),
    "tests": ("tests",),
    "tdd": ("tdd",),
    "skills": ("skills",),
    "hooks": ("hooks",),
    "domain": ("domain",),
    "github": ("github",),
    "expertise": ("expertise",),
    "docs": ("docs",),
    "map": ("map",),
    "orchestrator": ("orchestrator",),
    "dispatch": ("dispatch",),
    "digest": ("digest",),
    "approval": ("approval",),
    "security": ("security",),
    "deploy": ("deploy",),
    "state": ("state",),
    "brief": ("brief",),
    "plan": ("plan",),
    "qa": ("qa",),
    "worktree": ("worktree",),
    "budget": ("budget",),
}

HEADER = """<!-- index-contract v1 -->
<!-- GENERATED except the text after ` :: ` on each row.
     Regenerate: .claude/skills/harness/bin/gen-decisions-index.py -->

# DECISIONS — index

**A row is an open-or-skip filter, never the rule itself.** Its only job is to answer "do I open this
entry?" Never act on a ruling here: open `docs/harness/DECISIONS.md` at the `@line` anchor and read
the entry. Rows written during the one-time backfill are second-hand paraphrase.

**Never read the authority whole (DEC-150).** Grep this index, then open the two or three entries that
bear on your task. Decisions cited in a dispatch are a floor, not a ceiling.

**Adding a decision:** its author writes its ruling here, in the same commit that appends the entry.

Row: `- DEC-NN @<line> [am-span] [tags] refs: <graph> :: <ruling>`.
The `am-span` token appears only on a decision carrying amendments — `am.1`, a contiguous
`am.1-am.N`, or an enumerated `am.1,am.3` that never hides a gap.
A row ending `— SUPERSEDED BY DEC-NN` is one you must not act on.
"""

                                       # THE row grammar, single-sourced. The unit test
                                       # imports these two by path rather than restating
                                       # them: a test carrying its own copy of the grammar
                                       # agreed with nothing, and the disagreement surfaced
                                       # only as a silently-dropped ruling (B-2).
ROW_RE = re.compile(r"^- (DEC-\d+) .*? :: (.*)$")
# Deliberately looser than ROW_RE: anything a human or agent MEANT as a row. A line that
# looks like a row but does not parse as one is an error, never a non-row — treating it as
# "no prior row" is what silently discarded a hand-written ruling and replaced it with
# RULING PENDING, a data loss recoverable only from git.
ROW_LOOKALIKE_RE = re.compile(r"^\s*-\s*(DEC-\d+)\b")


def defenced_lines(text):
    """Return [(orig_line_no, line), ...] for lines NOT inside a ``` code fence.

    A '## DEC-N' heading (or anything else) shown inside a fence is
    documentation of the format, not a live declaration, and must not be
    harvested. This must run BEFORE all extraction: headings, amendments,
    the reference graph, and tag scoring all see the de-fenced body.
    """
    out = []
    infence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            infence = not infence
            continue
        if infence:
            continue
        out.append((lineno, line))
    return out


def parse_decisions(text):
    """Return dict: key (e.g. 'DEC-83') -> {"num": int, "line": int, "body": str}."""
    lines = defenced_lines(text)
    headings = []  # (index_into_lines, key, num, orig_lineno)
    for idx, (lineno, line) in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            headings.append((idx, m.group(1), int(m.group(2)), lineno))

    decisions = {}
    for i, (idx, key, num, lineno) in enumerate(headings):
        if key in decisions:
            print(f"COLLISION: duplicate decision key {key} after fence-stripping", file=sys.stderr)
            sys.exit(1)
        end_idx = headings[i + 1][0] if i + 1 < len(headings) else len(lines)
        body_lines = [l for (_, l) in lines[idx:end_idx]]
        decisions[key] = {
            "num": num,
            "line": lineno,
            "title": lines[idx][1],
            "body": "\n".join(body_lines),
        }
    return decisions, lines, headings


def compute_amendments(lines, headings):
    """Return dict: key -> sorted list[int] of amendment numbers."""
    # Map int(DEC number) -> key, for owner lookups.
    num_to_key = {num: key for (_, key, num, _) in headings}
    heading_positions = sorted(h[0] for h in headings)

    def owner_key_for(idx):
        owner_num = None
        for (h_idx, key, num, _) in headings:
            if h_idx <= idx:
                owner_num = num
            else:
                break
        return num_to_key.get(owner_num)

    heading_amend_nums = {}   # key -> set(int)
    bold_amend_entries = {}   # key -> list of (idx, explicit_num_or_None)

    for idx, (lineno, line) in enumerate(lines):
        m = AMEND_HEADING_RE.match(line)
        if m:
            target_num = int(m.group(1))
            target_key = num_to_key.get(target_num)
            if target_key is None:
                continue
            n = int(m.group(2)) if m.group(2) else 1
            heading_amend_nums.setdefault(target_key, set()).add(n)
            continue
        m = AMEND_BOLD_RE.match(line)
        if m:
            owner_key = owner_key_for(idx)
            if owner_key is None:
                continue
            explicit = int(m.group(1)) if m.group(1) else None
            bold_amend_entries.setdefault(owner_key, []).append(explicit)

    result = {}
    keys = set(heading_amend_nums) | set(bold_amend_entries)
    for key in keys:
        heading_nums = heading_amend_nums.get(key, set())
        bold_list = bold_amend_entries.get(key, [])
        nums = set(heading_nums)
        if heading_nums and bold_list:
            # Heading form's numbers win; inline (bold) ones continue past the
            # highest heading number, in order of appearance.
            next_n = max(heading_nums) + 1
            for _ in bold_list:
                nums.add(next_n)
                next_n += 1
        elif bold_list:
            # No heading form for this owner: use each bold entry's own
            # number, defaulting missing ones positionally starting at 1.
            next_default = 1
            for explicit in bold_list:
                n = explicit if explicit is not None else next_default
                nums.add(n)
                next_default = n + 1
        if nums:
            result[key] = sorted(nums)
    return result


def format_amendment_span(nums):
    if not nums:
        return ""
    # contiguous run -> am.1-am.N ; single -> am.1 ; else enumerated, no gaps hidden
    if nums == list(range(nums[0], nums[-1] + 1)):
        if len(nums) == 1:
            return f"am.{nums[0]}"
        return f"am.{nums[0]}-am.{nums[-1]}"
    return "am." + ",am.".join(str(n) for n in nums)


def compute_refs(body, own_num):
    seen = {}
    for m in DEC_REF_RE.finditer(body):
        n = int(m.group(1))
        if n == own_num:
            continue
        if n not in seen:
            seen[n] = m.group(0)
    return [seen[n] for n in sorted(seen)]


def compute_supersession_target(title):
    segments = title.split("—")
    if len(segments) < 2:
        return None
    last = segments[-1].strip()
    first_clause = last.split(",", 1)[0].strip()
    m = SUPERSESSION_VERB_RE.match(first_clause)
    if not m:
        return None
    return m.group(2)


def compute_tags(body):
    body_lower = body.lower()
    scores = {}
    for tag, substrs in TOPIC_VOCAB.items():
        score = sum(body_lower.count(sub) for sub in substrs)
        if score > 0:
            scores[tag] = score
    tags = sorted(scores, key=lambda t: (-scores[t], t))[:4]
    return tags


def strip_trailing_clauses(ruling):
    """Repeatedly strip trailing SUPERSEDED BY / ok-stale clauses. Returns
    (stripped_prose, had_ok_stale: bool)."""
    cur = ruling.strip()
    had_ok_stale = False
    prev = None
    while prev != cur:
        prev = cur
        new = re.sub(r"—\s*SUPERSEDED BY DEC-\d+\s*$", "", cur).strip()
        if new != cur:
            cur = new
            continue
        m = re.search(r"<!--\s*ok-stale\s*-->\s*$", cur)
        if m:
            had_ok_stale = True
            cur = cur[: m.start()].strip()
    return cur, had_ok_stale


def build_index(text, existing_rows):
    decisions, lines, headings = parse_decisions(text)
    amendments = compute_amendments(lines, headings)

    # Supersession: for each decision whose title names a target, that
    # target's row gains a trailing '-- SUPERSEDED BY DEC-<owner>'.
    superseded_by = {}  # target_num (int) -> list of owner keys, ascending by owner num
    for key, dec in sorted(decisions.items(), key=lambda kv: kv[1]["num"]):
        # Title first, then body prose (B-3). A decision may declare both; dedupe, and
        # never let a decision supersede itself (a body line quoting its own number).
        targets = []
        t = compute_supersession_target(dec["title"])
        if t:
            targets.append(t)
        targets += [m.group(2) for m in BODY_SUPERSESSION_RE.finditer(dec["body"])]
        for target in dict.fromkeys(targets):
            target_num = int(DEC_REF_RE.search(target).group(1))
            if target_num == dec["num"]:
                continue
            if key not in superseded_by.setdefault(target_num, []):
                superseded_by[target_num].append(key)

    # Orphan detection: existing rows with non-sentinel ruling text whose DEC
    # number has no live heading. Hard error, never a silent drop.
    orphans = []
    for key, raw_ruling in existing_rows.items():
        if key in decisions:
            continue
        prose, _ = strip_trailing_clauses(raw_ruling)
        if prose and prose != "\N{WARNING SIGN} RULING PENDING":
            orphans.append((key, raw_ruling))
    if orphans:
        for key, raw_ruling in orphans:
            print(
                f"ORPHAN: {key} {raw_ruling!r} has a ruling in the index but "
                f"no live heading in {DECISIONS_PATH}",
                file=sys.stderr,
            )
        return None

    rows = []
    for key, dec in sorted(decisions.items(), key=lambda kv: kv[1]["num"]):
        num = dec["num"]
        tags = compute_tags(dec["body"])
        refs = compute_refs(dec["body"], num)
        amend_nums = amendments.get(key, [])
        amend_span = format_amendment_span(amend_nums)

        if key in existing_rows:
            prose, had_ok_stale = strip_trailing_clauses(existing_rows[key])
        else:
            prose, had_ok_stale = "\N{WARNING SIGN} RULING PENDING", False

        clauses = [prose]
        for owner_key in superseded_by.get(num, []):
            owner_num = decisions[owner_key]["num"]
            clauses.append(f"— SUPERSEDED BY DEC-{owner_num}")
        # Re-sort supersession clauses ascending by owner DEC number.
        if len(clauses) > 1:
            body_prose = clauses[0]
            supersede_clauses = sorted(
                clauses[1:],
                key=lambda c: int(DEC_REF_RE.search(c).group(1)),
            )
            clauses = [body_prose] + supersede_clauses
        if had_ok_stale:
            clauses.append("<!-- ok-stale -->")
        ruling = " ".join(clauses)

        left = f"- {key} @{dec['line']}"
        if amend_span:
            left += f" {amend_span}"
        left += f" [{','.join(tags)}] refs: {' '.join(refs)}"
        rows.append(f"{left} :: {ruling}")

    return rows


def parse_existing_index(text):
    """{'DEC-NN': ruling}. Raises MalformedRow rather than skipping a broken row."""
    rows, malformed = {}, []
    for n, line in enumerate(text.splitlines(), 1):
        m = ROW_RE.match(line)
        if m:
            rows[m.group(1)] = m.group(2)
        elif ROW_LOOKALIKE_RE.match(line):
            malformed.append((n, line))
    if malformed:
        raise MalformedRow(malformed)
    return rows


class MalformedRow(Exception):
    """A line in the index means to be a row but does not parse as one."""

    def __init__(self, rows):
        self.rows = rows
        super().__init__(f"{len(rows)} malformed row(s)")


def parse_argv(argv):
    """Return True for stdout mode, False for the write path — or exit.

    Unvalidated argv used to mean every unrecognized flag, `--help` first among them,
    fell through to the WRITE path (#140): the one command a reader runs to learn what
    this script does was the command that rewrote the repo, and it fired mid-review on
    PR #138. An unknown flag must therefore refuse LOUDLY rather than default to the
    only branch that touches the tree — silence here is indistinguishable from a
    legitimate regeneration, because the file is generated.
    """
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        sys.exit(0)
    unknown = [a for a in argv if a != "--stdout"]
    if unknown:
        print(f"gen-decisions-index: unrecognized argument(s): {' '.join(unknown)}. "
              f"Wrote nothing.", file=sys.stderr)
        print(f"\n{__doc__.strip()}", file=sys.stderr)
        sys.exit(2)
    return "--stdout" in argv


def main():
    stdout_mode = parse_argv(sys.argv[1:])

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    os.chdir(project_dir)

    if not os.path.isfile(DECISIONS_PATH):
        print(f"gen-decisions-index: {DECISIONS_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    text = open(DECISIONS_PATH, encoding="utf-8").read()

    existing_rows = {}
    if os.path.isfile(INDEX_PATH):
        existing_text = open(INDEX_PATH, encoding="utf-8").read()
        try:
            existing_rows = parse_existing_index(existing_text)
        except MalformedRow as e:
            # REPAIR, never regenerate: this script is the only thing that can rebuild the
            # index, so telling the reader to regenerate would tell them to destroy the
            # hand-written rulings on every other row. Quote the line so the fix is local.
            print(f"gen-decisions-index: {INDEX_PATH} has "
                  f"{len(e.rows)} malformed row(s). Wrote nothing.", file=sys.stderr)
            for n, line in e.rows:
                print(f"  {INDEX_PATH}:{n}: {line}", file=sys.stderr)
            print("\nEach line above is meant to be a row but does not match the grammar:\n"
                  "  - DEC-NN @<line> [am-span] [tags] refs: <graph> :: <ruling>\n"
                  "Repair those lines in place — the ' :: ' separator, with a single space on "
                  "each side, is what carries the hand-written ruling. Do NOT regenerate to "
                  "fix this; regenerating cannot recover a ruling it could not read.",
                  file=sys.stderr)
            sys.exit(1)

    rows = build_index(text, existing_rows)
    if rows is None:
        # Orphan detected; already reported to stderr. Write nothing.
        sys.exit(1)

    output = HEADER + "\n" + "\n".join(rows) + "\n"

    if stdout_mode:
        sys.stdout.write(output)
        return

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(output)


if __name__ == "__main__":
    main()
