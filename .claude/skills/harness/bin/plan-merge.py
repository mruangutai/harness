#!/usr/bin/env python3
"""plan-merge.py — the second plan writer that adds tasks and never deletes them
(FEAT-32 T-03, D-01..D-04, DEC-182, DEC-120).

Reproduces and fixes #628: two whole-file writes to the same plan.yaml, one after another,
silently lose whatever the first one added. This CLI never does a whole-file rewrite of an
existing plan.yaml. It SPLICES TEXT — never re-renders through a YAML dumper (D-03) — keyed on
each task/decision's `id`, under harness_merge.locked_update so the replace stays atomic and the
lock stays the one shared with every other write route in this feature.

    plan-merge.py apply             --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py add-tasks         --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py set-task-station  --file <plan.yaml> --task T-NN --station <name>
    plan-merge.py set-feature-station --file <plan.yaml> --station <name>
    plan-merge.py sign-approval     --file <plan.yaml> --by <name> --date <YYYY-MM-DD>

FIVE VERBS, ONE WRITE ROUTE (FEAT-41 T-03). Every verb goes through
harness_merge.locked_update and the text splice, and require_destination (exit 9) guards every
path. ADD-ONLY IS A PROPERTY OF `apply` AND ITS ALIAS, NOT OF THE TOOL: the lock and the splice
are what fix #628 and they hold for all five, while never deleting a task is a promise those two
verbs alone make.

`set-task-station` and `set-feature-station` validate the station against the vocabulary
factory_config declares — MANDATED_STATIONS plus TERMINAL_MARKER, imported, never respelled —
resolved through the harness.json of the checkout the target plan.yaml belongs to. The check runs
BEFORE the lock is taken, so a refused value never opens the file.

`approval:` is written by EXACTLY ONE VERB, `sign-approval` (D-04, amended by FEAT-41 T-03).
Every other verb leaves the base file's approval bytes byte for byte. The main session — nobody
else — signs approval, and now does so through this tool rather than by hand. A proposal
that carries an approval mapping which PARSES differently from the base's is a REFUSAL (exit 8),
not a silent drop: `apply` must be INCAPABLE of writing a signature (step 7) and must also NOTICE
a caller that tried to sneak one past it (step 7b) — two different jobs, so two different guards.

THAT PROHIBITION IS UNCHANGED IN FORCE AND NARROWER IN SCOPE. Before FEAT-41 T-03 the tool had
one verb, so "apply cannot sign" and "this tool cannot sign" were the same sentence; they are not
any more. Signing moved from a hand edit into `sign-approval` so that it happens under the same
lock as every other plan write — a signature spliced by hand while another writer held the file
was the remaining unguarded route into plan.yaml. `apply` still cannot sign, and still refuses a
proposal that tries.

Exit codes are the interface:
    0  applied — stdout lists ADDED/PRESERVED ids, an IGNORED-APPROVAL line if the proposal
       carried an approval block, and a final APPLIED line
    3  the task id named by --task is absent from the plan (the message names the ids present)
    4  the value given to --station is not a legal station (the message lists the legal ones)
    5  a side (base or proposal) failed to parse as YAML
    6  the lock could not be acquired within the retry budget (harness_merge)
    7  the same id, or the same top-level key, carries two different loaded values
    8  the proposal's approval mapping parses differently from the base's
    9  --file does not resolve to a plan.yaml this tool owns

python3 stdlib plus PyYAML (DEC-171 requires it here; imported plainly, never through
harness_yaml.py — that divergence is raised upward as a decision question, not resolved here).
"""
import argparse
import hashlib
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_config  # noqa: E402  (local import, after sys.path fix-up)
import gh_board  # noqa: E402
import harness_boundary  # noqa: E402
import harness_yaml  # noqa: E402
import harness_merge  # noqa: E402

# Module-level literals. Each is mutated BY NAME in a copy of the tree by the test's red proofs.
# Nothing outside this file's source text ever flips one — no environment variable, no flag.

# Guards step 6 (task/decision union merge). False reproduces today's naive last-writer-wins:
# the proposal's bytes replace the file whole, with no comparison against the base at all.
UNION_MERGE = True

# Guards step 7 (approval is always the base's bytes, verbatim). False renders the WHOLE output
# through yaml.safe_dump instead of splicing text — what a naive implementation does, and what
# the byte-identity test must reject: a dumper round trip destroys comments and normalises
# quoting.
PRESERVE_BASE_BYTES = True

# Guards step 7b (the structural refusal). False skips the parsed-approval comparison entirely,
# so step 7 alone decides and a proposal carrying a different signed approval is silently
# dropped instead of refused.
APPROVAL_REFUSAL = True

# A features directory either directly under a .harness segment or nested one segment deeper
# (repo-tier), a FEAT- or BUG- prefixed directory, and the literal filename plan.yaml. Matched
# on the RESOLVED path only (harness_merge.require_destination), never the literal argument.
PLAN_TAIL = re.compile(
    r"(?:^|/)\.harness/(?:[^/]+/)?features/(?:FEAT|BUG)-[^/]+/plan\.yaml$"
)

TOP_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):")
DASH_RE = re.compile(r"^(\s*)-\s")

UNION_KEYS = ("tasks", "decisions")


def _resolve_plan(file_path):
    """require_destination on the RESOLVED path, or print the refusal and exit its code.

    Extracted so all five verbs share ONE destination guard. A second copy would be a second
    place for exit 9 to stop being true."""
    try:
        return harness_merge.require_destination(
            file_path,
            PLAN_TAIL,
            "a plan.yaml under a features directory",
            [
                "  a legal path looks like .harness/features/FEAT-NN-slug/plan.yaml or",
                "  .harness/<repo>/features/FEAT-NN-slug/plan.yaml.",
                "  This tool merges plan.yaml only.",
            ],
        )
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def _harness_root(start):
    """Walk up from `start` to the checkout whose manifest declares a harness, or None.

    THE PROBE NAMES THE MANIFEST, NEVER THE `.harness` DIRECTORY. A probe for the directory
    resolves $HOME as a root in the global install — B-7 verbatim — and
    test-check-plan-routes.py's case_20 asserts that no copy of this idiom regresses.

    Extracted from `_legal_stations` (FEAT-41 F-05), whose docstring already described this as
    its own named step. It is a walk with a termination condition, which is a different kind of
    thing from choosing a vocabulary, and the two were interleaved in one body at grade 3.
    """
    root = start
    while True:
        if os.path.isfile(os.path.join(root, harness_boundary.MARKER)):
            return root
        parent = os.path.dirname(root)
        if parent == root:
            return None
        root = parent


def _legal_stations(resolved):
    """The station vocabulary the target plan.yaml's own checkout declares, plus the terminal
    marker, as an ordered tuple.

    IMPORTED, NEVER RESPELLED (FEAT-41 T-03). factory_config owns MANDATED_STATIONS and
    TERMINAL_MARKER; declaring either here would be a second vocabulary, and since this module
    is imported by nothing, check-plan-routes.py and check-domain.sh would each respell it as a
    bare literal and D-05's claim that the marker is declared once in code would be false the
    day it landed.

    The board is read from the harness.json of the checkout the plan belongs to. A checkout with
    no board declared — every test fixture, and any project that has not onboarded a board — is
    NOT a licence to accept anything: the mandate still applies, because MANDATED_STATIONS is
    what a declaration is checked against in the first place.

    THE ROOT PROBE NAMES THE MANIFEST, NEVER THE `.harness` DIRECTORY. A probe for the directory
    resolves $HOME as a root in the global install — B-7 verbatim — and
    test-check-plan-routes.py's case_20 asserts that no copy of this idiom regresses. The walk
    starts from the plan.yaml's own directory rather than from this script's location, because
    the vocabulary that governs a write belongs to the checkout being written to, not to
    whichever checkout happens to be running the tool.
    """
    root = _harness_root(os.path.dirname(os.path.abspath(resolved)))
    stations = None
    if root is not None:
        try:
            board = gh_board.load_board(root)
            if board is not None:
                stations = factory_config.station_names(board)
        except factory_config.FleetError:
            # An unusable board declaration is not this tool's error to report — the state gate
            # and every board writer already name it loudly. Fall back to the mandate so a
            # station write is still validated rather than waved through.
            stations = None
    if stations is None:
        stations = factory_config.MANDATED_STATIONS
    return tuple(stations) + (factory_config.TERMINAL_MARKER,)


def _refuse_illegal_station(station, legal):
    """Exit 4, naming the offending value and every legal one.

    CALLED BEFORE THE LOCK IS TAKEN, deliberately: a refused value must never open the file, so
    a typo cannot contend for the lock or leave a partial write behind."""
    print(
        f"plan-merge: {station!r} is not a legal station — expected one of: "
        + ", ".join(legal),
        file=sys.stderr,
    )
    sys.exit(4)



def _index_top_keys(text):
    """Return (lines, order, ranges, preamble_lines).

    lines:     text.splitlines(keepends=True)
    order:     top-level key names in file order (first occurrence only)
    ranges:    {key: (start_line, end_line)} half-open, end exclusive
    preamble:  every line before the first top-level key (comments, blank lines) — always
               carried from the BASE side untouched; a proposal's preamble is never consulted.
    """
    lines = text.splitlines(keepends=True)
    positions = []
    seen = set()
    for i, line in enumerate(lines):
        m = TOP_KEY_RE.match(line)
        if m and m.group(1) not in seen:
            positions.append((m.group(1), i))
            seen.add(m.group(1))
    order = [name for name, _ in positions]
    ranges = {}
    for idx, (name, start) in enumerate(positions):
        end = positions[idx + 1][1] if idx + 1 < len(positions) else len(lines)
        ranges[name] = (start, end)
    preamble_end = positions[0][1] if positions else len(lines)
    return lines, order, ranges, lines[:preamble_end]


def _index_list_items(lines, key_range):
    """Within key_range=(start,end), find each list item's (start,end) by locating every dash
    line at the SAME indent as the first dash line found. Returns [(start,end), ...] in text
    order; the caller zips this against the already-safe_load-ed list for that key, in the
    order PyYAML preserves for a block sequence."""
    start, end = key_range
    dash_lines = []
    indent = None
    for i in range(start, end):
        m = DASH_RE.match(lines[i])
        if m:
            cur = m.group(1)
            if indent is None:
                indent = cur
            if cur == indent:
                dash_lines.append(i)
    ranges = []
    for idx, s in enumerate(dash_lines):
        e = dash_lines[idx + 1] if idx + 1 < len(dash_lines) else end
        ranges.append((s, e))
    return ranges


def _field_lines(indent, key, value):
    """Emit `<indent><key>: <value>` as YAML, quoting ONLY when the value needs it.

    FEAT-41 F-02. `sign-approval` is the one verb that writes a free-form operator string:
    every other verb's value is validated against a closed vocabulary before the lock is taken,
    so it cannot carry syntax. `--by` used to be interpolated raw, and a signer name with a
    colon wrote an unparseable SIGNED plan.yaml and exited 0.

    WHY `safe_dump` AND NOT A QUOTING RULE OF OUR OWN. Three of the six failures are not syntax
    errors and no hand-written escape would have caught them: `#845 owner` is swallowed as a
    comment, a bare `yes` reloads as the boolean True, and an embedded newline can open a
    sibling key. PyYAML already knows the whole set; a local rule would only re-derive part of
    it, and would drift from the parser that actually reads the file back.

    QUOTING ONLY WHEN NEEDED IS PART OF THE CONTRACT, not an aesthetic. This document is signed
    and read by a human, and `approved_by: 'Mike Ruangutai'` on every plan would be a visible
    change to every signature for no benefit. test-plan-merge.py asserts the bare form survives.

    A multi-line emission is indented per line so a continuation cannot escape the mapping.
    """
    dumped = yaml.safe_dump({key: value}, default_flow_style=False,
                            width=10 ** 9, allow_unicode=True)
    return "".join(f"{indent}{line}\n" if line else "\n"
                   for line in dumped.rstrip("\n").split("\n"))


def _verify_signature(spliced_bytes, resolved, fields):
    """Refuse rather than write a signature that does not reload as the one that was asked for.

    FEAT-41 F-02, the second half. `_field_lines` above fixes the cause; this catches anything
    it misses, and the two are NOT redundant: the failures where the value is silently coerced
    rather than corrupted (`yes` -> True, `#845 owner` -> None) leave a document that parses
    perfectly, so a check that only asked "does it load" would pass them all.

    IT COMPARES VALUES, NOT SYNTAX. That is the only check that can tell the difference between
    a signature and something that merely looks like one. Exit 5 is the same code the splice
    defect this mirrors already uses -- an unwritable result, not a bad argument.
    """
    try:
        reloaded = yaml.safe_load(spliced_bytes.decode("utf-8"))
    except yaml.YAMLError as exc:
        raise harness_merge.MergeRefusal(
            5,
            [
                "UNPARSEABLE: the signed plan does not load — REFUSING to write it.",
                f"  {exc}",
                "  this is a splice defect, not a bad signature: the base parsed.",
            ],
        )
    if not isinstance(reloaded, dict) or not isinstance(reloaded.get("approval"), dict):
        raise harness_merge.MergeRefusal(
            5, [f"UNPARSEABLE: {resolved} has no approval mapping after signing — "
                "REFUSING to write it."]
        )
    got = reloaded["approval"]
    for key, want in fields.items():
        if got.get(key) != want:
            raise harness_merge.MergeRefusal(
                5,
                [
                    f"REFUSED: the signature does not reload as written — approval.{key} "
                    "would not say what was signed.",
                    f"  asked for: {want!r}",
                    f"  reloads as: {got.get(key)!r}",
                ],
            )



def _reload_or_refuse(spliced_bytes):
    """The spliced document, or a refusal naming the splice as the fault."""
    try:
        return yaml.safe_load(spliced_bytes.decode("utf-8"))
    except yaml.YAMLError as exc:
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the amended plan does not load — REFUSING to write it.",
                f"  {exc}",
                "  this is a splice defect, not a bad value: the base parsed."])


def _sole_item(reloaded, key, iid):
    """The one item under `key` whose id is `iid`, or a refusal.

    Exactly one is required: a duplicate id cannot be amended unambiguously, and binding to
    the first match silently is what the code-reviewer found in cycle 0.
    """
    items = (reloaded or {}).get(key)
    if not isinstance(items, list):
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: {key}: is not a list after the amendment — REFUSING to write it."])
    got = [it for it in items if isinstance(it, dict) and it.get("id") == iid]
    if len(got) != 1:
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: {iid} appears {len(got)} time(s) under {key}: after the amendment; "
                "exactly one is required. A duplicate id cannot be amended unambiguously."])
    return got[0]


def _verify_amend(spliced_bytes, key, iid, field, want):
    """Refuse rather than write an amendment that does not reload as the one asked for.

    THE DISCIPLINE `cmd_sign_approval` ALREADY HELD, and `amend` did not inherit (BUG-1128
    panel V3). The compare-and-swap protects CONTENT: it proves the block being replaced is
    the block that was read. It says nothing about LOCATION or RESULT, because both hashes are
    computed over whatever the locator returned — so they agree perfectly on the wrong block,
    and a splice into the wrong field reports success at exit 0.

    IT COMPARES VALUES, NOT SYNTAX, for the same reason `_verify_signature` does: a wrong-field
    write and a silently re-formed value both leave a document that parses.

    It CANNOT see a boundary error — `_trim_tail` owns that (panel N1) — because a deleted
    adjacent comment leaves the amended value exactly as asked.
    """
    reloaded = _reload_or_refuse(spliced_bytes)
    item = _sole_item(reloaded, key, iid)
    if item.get(field) != want:
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: the amendment does not reload as written — {iid}.{field} would not "
                "say what was asked for. This is the wrong-field write the content hash cannot "
                "see.",
                f"  asked for: {want!r}",
                f"  reloads as: {item.get(field)!r}"])
    return reloaded


def _schema_error(doc):
    """The plan-schema complaint about `doc`, or None when it satisfies the schema.

    ONE HOME FOR THE SCHEMA, called through `harness_yaml.validate_plan_doc` -- the same function
    `load_plan` uses (FEAT-41 HIGH-1). A copy of the rules here would be a second place for them
    to stop being true, which is the defect this feature keeps finding in its own work.
    """
    try:
        harness_yaml.validate_plan_doc(doc, "the merged plan")
    except harness_yaml.PlanSchemaError as exc:
        return exc
    return None



def _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids):
    """Refuse rather than return a splice that does not reload as the merge it reported."""
    try:
        reloaded = yaml.safe_load(spliced_bytes.decode("utf-8"))
    except yaml.YAMLError as exc:
        raise harness_merge.MergeRefusal(
            5,
            [
                "UNPARSEABLE: the merged plan does not load — REFUSING to write it.",
                f"  {exc}",
                "  this is a splice defect, not a bad proposal: both inputs parsed.",
            ],
        )
    if not isinstance(reloaded, dict):
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the merged plan is not a mapping — REFUSING to write it."]
        )
    # AND IT MUST BE A LEGAL PLAN, NOT MERELY LEGAL YAML (FEAT-41 HIGH-1). `safe_load` above
    # answers "is this YAML"; the schema answers "can a reader act on it". Without this, `apply`
    # minted `station_only: true` onto a task-bearing signed plan, reported APPLIED, exited 0, and
    # left a document no reader can load. Same shape as the splice defect STEP 9 exists for.
    #
    # THE SCHEMA HAS ONE HOME. `validate_plan_doc` is the function `load_plan` itself calls, so
    # the writer cannot drift from the reader; a copy of the rules here would be a second place
    # for them to stop being true.
    # DO NO HARM, RATHER THAN DEMAND PERFECTION. Refusing every merge whose RESULT fails the
    # schema would block legitimate repair of a plan that was already non-conforming -- measured:
    # 21 existing cases went red that way, all with bases whose tasks predate REQUIRED_TASK_FIELDS.
    # So the test is whether this MERGE introduces a violation: valid before, invalid after.
    if _schema_error(base_doc) is None:
        _err = _schema_error(reloaded)
        if _err is not None:
            raise harness_merge.MergeRefusal(
                5,
                ["ILLEGAL PLAN: this merge would make a legal plan illegal — REFUSING to write it.",
                 f"  {_err}",
                 "  the base satisfied the plan schema and the merged result does not, so the "
                 "change itself is what the schema refuses."],
            )
    for key in UNION_KEYS:
        if key not in out_order:
            continue
        want = [_item_id(i) for i in (base_doc.get(key) or [])]
        for item in prop_doc.get(key) or []:
            iid = _item_id(item)
            if iid not in want:
                want.append(iid)
        got = [_item_id(i) for i in (reloaded.get(key) or [])]
        if got != want:
            raise harness_merge.MergeRefusal(
                5,
                [
                    f"UNPARSEABLE: '{key}' does not reload as the merge that was computed — "
                    "REFUSING to write it.",
                    f"  expected ids: {want!r}",
                    f"  reloaded ids: {got!r}",
                ],
            )


def _item_indent(lines, item_ranges):
    """The leading-space width of a list item's own dash line, or None when there are none."""
    if not item_ranges:
        return None
    start, _end = item_ranges[0]
    line = lines[start]
    return len(line) - len(line.lstrip(" "))


def _reindent(item_lines, delta, iid, key):
    """Shift a whole item uniformly, so a proposal's indentation cannot corrupt the base.

    WHY THIS EXISTS, measured on 2026-08-31: FEAT-41's plan indents `decisions:` items two
    spaces. An operator-approved amendment was proposed as a standalone document with items at
    column 0 — valid YAML on its own, and the shape a human writes by hand. The splice appended
    that text verbatim, so a `- id:` landed at column 0 inside a two-space list, and a signed
    1541-line plan stopped loading. `apply` printed ADDED and exited 0.

    UNIFORM is the whole point: every line of the item moves by the same delta, so relative
    structure — nested mappings, block scalars, the `intent: |` body — is preserved exactly.
    Re-indenting per-line by any cleverer rule would rewrite the very text this tool exists to
    splice byte for byte.

    A dedent that would eat non-whitespace is a REFUSAL, never a silent truncation.
    """
    if delta == 0:
        return list(item_lines)
    out = []
    for line in item_lines:
        if not line.strip():
            out.append(line)
            continue
        if delta > 0:
            out.append(" " * delta + line)
            continue
        room = len(line) - len(line.lstrip(" "))
        if room < -delta:
            raise harness_merge.MergeRefusal(
                5,
                [
                    f"UNPARSEABLE: cannot re-indent id={iid!r} in '{key}' to the base's "
                    f"indentation — a line carries only {room} leading space(s) and the "
                    f"proposal is {-delta} deeper than the base.",
                ],
            )
        out.append(line[-delta:])
    return out


def _item_id(item):
    return item.get("id") if isinstance(item, dict) else None


def _key_head(lines, key_range, item_ranges):
    """The key's own line(s) up to the first item — e.g. the 'tasks:' line itself, plus any
    blank line before the first dash."""
    start, end = key_range
    first_item_start = item_ranges[0][0] if item_ranges else end
    return "".join(lines[start:first_item_start])


def apply_merge(base_bytes, proposal_text):
    """The whole algorithm. Returns (output_bytes, added_ids, preserved_ids, ignored_approval).
    Raises harness_merge.MergeRefusal(5|7|8) with nothing to write, per plan-merge.py's contract
    with harness_merge.locked_update: a raised MergeRefusal leaves the file untouched."""
    if base_bytes is None:
        # Step 3: a base that does not exist is an empty mapping; the proposal is written whole
        # UNLESS it carries an approval key. Read together with step 7b (D-04): the empty
        # mapping has no approval key at all, so a proposal's approval value always "differs"
        # from the base's absent one — the same structural refusal step 7b applies elsewhere,
        # here on the create path, so the tool never becomes capable of writing a signature to
        # a brand-new file.
        try:
            prop_doc = yaml.safe_load(proposal_text)
        except yaml.YAMLError as exc:
            raise harness_merge.MergeRefusal(
                5, [f"UNPARSEABLE: proposal failed to parse: {exc}"]
            )
        prop_doc = prop_doc if isinstance(prop_doc, dict) else {}
        if APPROVAL_REFUSAL and "approval" in prop_doc:
            raise harness_merge.MergeRefusal(
                8,
                [
                    "REFUSED: proposal carries an approval mapping and the base does not exist "
                    "(treated as an empty mapping with no approval key).",
                    "  base approval: <absent>",
                    f"  proposal approval: {prop_doc.get('approval')!r}",
                    "  the signer is the main session; plan-merge.py never writes approval.",
                ],
            )
        return proposal_text.encode("utf-8"), [], [], False

    base_text = base_bytes.decode("utf-8")
    try:
        base_doc = yaml.safe_load(base_text)
    except yaml.YAMLError as exc:
        raise harness_merge.MergeRefusal(5, [f"UNPARSEABLE: base failed to parse: {exc}"])
    try:
        prop_doc = yaml.safe_load(proposal_text)
    except yaml.YAMLError as exc:
        raise harness_merge.MergeRefusal(5, [f"UNPARSEABLE: proposal failed to parse: {exc}"])
    base_doc = base_doc if isinstance(base_doc, dict) else {}
    prop_doc = prop_doc if isinstance(prop_doc, dict) else {}

    if not UNION_MERGE:
        # Step 5, off: today's last-writer-wins, verbatim.
        return proposal_text.encode("utf-8"), [], [], False

    base_lines, base_order, base_ranges, base_preamble = _index_top_keys(base_text)
    prop_lines, prop_order, prop_ranges, _prop_preamble = _index_top_keys(proposal_text)

    base_has_approval = "approval" in base_doc
    prop_has_approval = "approval" in prop_doc
    base_approval = base_doc.get("approval")
    prop_approval = prop_doc.get("approval")

    # Step 7b: THE STRUCTURAL REFUSAL. Compares PARSED values, never text.
    if (
        APPROVAL_REFUSAL
        and base_has_approval
        and prop_has_approval
        and prop_approval != base_approval
    ):
        raise harness_merge.MergeRefusal(
            8,
            [
                "REFUSED: proposal's approval mapping differs from the base's.",
                f"  base approval: {base_approval!r}",
                f"  proposal approval: {prop_approval!r}",
                "  the signer is the main session; plan-merge.py never writes approval.",
            ],
        )
    ignored_approval = base_has_approval and prop_has_approval

    out_order = list(base_order)
    for key in prop_order:
        if key not in out_order:
            out_order.append(key)

    out_chunks = ["".join(base_preamble)]
    added_ids, preserved_ids = [], []

    for key in out_order:
        if key == "approval":
            # Step 7: the base's line range, byte for byte, always. If the base has no
            # approval block at all, this tool still never writes one — there is nothing to
            # carry forward, and the proposal's is ignored the same as everywhere else.
            if base_has_approval:
                s, e = base_ranges["approval"]
                out_chunks.append("".join(base_lines[s:e]))
            continue

        if key in UNION_KEYS:
            base_list = base_doc.get(key) or []
            prop_list = prop_doc.get(key) or []
            base_item_ranges = (
                _index_list_items(base_lines, base_ranges[key]) if key in base_ranges else []
            )
            prop_item_ranges = (
                _index_list_items(prop_lines, prop_ranges[key]) if key in prop_ranges else []
            )
            if len(base_item_ranges) != len(base_list) or len(prop_item_ranges) != len(
                prop_list
            ):
                raise harness_merge.MergeRefusal(
                    5,
                    [
                        f"UNPARSEABLE: could not align text ranges with parsed items for "
                        f"'{key}' — the block's formatting is not one dash per item."
                    ],
                )

            if key in base_ranges:
                out_chunks.append(_key_head(base_lines, base_ranges[key], base_item_ranges))
            elif key in prop_ranges:
                out_chunks.append(_key_head(prop_lines, prop_ranges[key], prop_item_ranges))
            else:
                continue

            base_by_id = {}
            for (s, e), item in zip(base_item_ranges, base_list):
                base_by_id[_item_id(item)] = (s, e, item)
            prop_by_id = {}
            prop_id_order = []
            for (s, e), item in zip(prop_item_ranges, prop_list):
                iid = _item_id(item)
                prop_by_id[iid] = (s, e, item)
                prop_id_order.append(iid)

            for iid, (s, e, item) in base_by_id.items():
                out_chunks.append("".join(base_lines[s:e]))
                if iid in prop_by_id:
                    _, _, pitem = prop_by_id[iid]
                    if pitem == item:
                        preserved_ids.append(iid)
                    else:
                        raise harness_merge.MergeRefusal(
                            7,
                            [
                                f"CONFLICT: id={iid!r} in '{key}' carries two different values.",
                                f"  base: {item!r}",
                                f"  proposal: {pitem!r}",
                            ],
                        )
            # THE ADDITION IS RE-INDENTED TO THE BASE'S LIST, never appended verbatim. When
            # the base has no items of its own there is nothing to match, and the key head came
            # from the proposal too, so its own indentation is already consistent.
            base_indent = _item_indent(base_lines, base_item_ranges)
            prop_indent = _item_indent(prop_lines, prop_item_ranges)
            for iid in prop_id_order:
                if iid not in base_by_id:
                    s, e, _item = prop_by_id[iid]
                    item_lines = prop_lines[s:e]
                    if base_indent is not None and prop_indent is not None:
                        item_lines = _reindent(
                            item_lines, base_indent - prop_indent, iid, key
                        )
                    out_chunks.append("".join(item_lines))
                    added_ids.append(iid)
            continue

        # Step 8: every other top-level key.
        in_base = key in base_ranges
        in_prop = key in prop_ranges
        if in_base and in_prop:
            bval, pval = base_doc.get(key), prop_doc.get(key)
            if bval != pval:
                raise harness_merge.MergeRefusal(
                    7,
                    [
                        f"CONFLICT: top-level key '{key}' carries two different values.",
                        f"  base: {bval!r}",
                        f"  proposal: {pval!r}",
                    ],
                )
            s, e = base_ranges[key]
            out_chunks.append("".join(base_lines[s:e]))
        elif in_base:
            s, e = base_ranges[key]
            out_chunks.append("".join(base_lines[s:e]))
        elif in_prop:
            s, e = prop_ranges[key]
            out_chunks.append("".join(prop_lines[s:e]))

    spliced_bytes = "".join(out_chunks).encode("utf-8")

    if PRESERVE_BASE_BYTES:
        # STEP 9: THE RESULT IS PARSED BEFORE IT IS WRITTEN, and this guard is general.
        # Steps 5-8 parse the BASE and the PROPOSAL; nothing parsed the OUTPUT, so a splice
        # defect could — and on 2026-08-31 did — write a signed plan that PyYAML cannot load
        # while printing ADDED and exiting 0. A tool whose whole promise is "the base's bytes
        # survive" must not be able to hand back bytes that are not a plan.
        #
        # It also checks the MERGE, not merely the syntax: every id the caller is about to be
        # told was added or preserved must actually be present in the reloaded document. A
        # splice that lands text in the wrong block can still parse.
        _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids)
        return spliced_bytes, added_ids, preserved_ids, ignored_approval

    # PRESERVE_BASE_BYTES off: what a naive implementation does — render the whole merged
    # document through yaml.safe_dump instead of splicing. Comments and quoting do not survive
    # this path; that is exactly the property the red proof grades.
    merged_doc = dict(base_doc)
    for key in UNION_KEYS:
        if key not in out_order:
            continue
        base_list = base_doc.get(key) or []
        merged_list = list(base_list)
        seen = {_item_id(i) for i in base_list}
        for item in prop_doc.get(key) or []:
            iid = _item_id(item)
            if iid not in seen:
                merged_list.append(item)
                seen.add(iid)
        if merged_list:
            merged_doc[key] = merged_list
    for key in prop_doc:
        if key in UNION_KEYS or key == "approval":
            continue
        if key not in merged_doc:
            merged_doc[key] = prop_doc[key]
    if base_has_approval:
        merged_doc["approval"] = base_approval
    dumped = yaml.safe_dump(merged_doc, sort_keys=False, allow_unicode=True).encode("utf-8")
    return dumped, added_ids, preserved_ids, ignored_approval


def cmd_apply(args):
    resolved = _resolve_plan(args.file)

    if args.proposal == "-":
        proposal_text = sys.stdin.read()
    else:
        with open(args.proposal, encoding="utf-8") as f:
            proposal_text = f.read()

    result = {}

    def transform(base_bytes):
        out_bytes, added, preserved, ignored_approval = apply_merge(base_bytes, proposal_text)
        result["added"] = added
        result["preserved"] = preserved
        result["ignored_approval"] = ignored_approval
        return out_bytes

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    for eid in result.get("added", []):
        print(f"ADDED {eid}")
    for eid in result.get("preserved", []):
        print(f"PRESERVED {eid}")
    if result.get("ignored_approval"):
        print("IGNORED-APPROVAL: proposal's approval block was not written; base's kept")
    print(f"APPLIED {resolved}")
    sys.exit(0)


TASK_ID_RE = re.compile(r"^(\s*)-\s+id:\s*(\S+)\s*$")
STATUS_LINE_RE = re.compile(r"^(\s*)status:\s*(.*)$")
FEATURE_LINE_RE = re.compile(r"^feature:\s*\S")


def _task_status_line(lines, task_id):
    """(index, indent) of `task_id`'s own status line, or (None, task_ids_present).

    Scans from the task's `- id:` line to the next item at the same indent, so a `status:` key
    nested deeper inside that task — a verify block's own prose, say — cannot be mistaken for
    the task's status. Returns the ids actually present when the id is absent, because a caller
    who mistyped one needs to see the real list, not just a refusal.

    SCOPED TO THE `tasks:` KEY. `- id:` also matches every entry under `decisions:`, and listing
    D-01..D-12 in the exit-3 message for a `--task` mistake invites the operator to retry with a
    decision id — which would then fail for the unrelated reason that decisions carry no status.
    A refusal that suggests a wrong next step is worse than a terse one.
    """
    _lines, _order, ranges, _pre = _index_top_keys("".join(lines))
    if "tasks" not in ranges:
        return None, []
    lo, hi = ranges["tasks"]
    ids_present = []
    start = None
    indent = ""
    for i in range(lo, hi):
        line = lines[i]
        m = TASK_ID_RE.match(line)
        if m:
            ids_present.append(m.group(2))
            if m.group(2) == task_id and start is None:
                start, indent = i, m.group(1)
            elif start is not None and m.group(1) == indent:
                break
    if start is None:
        return None, ids_present
    for j in range(start, len(lines)):
        m2 = TASK_ID_RE.match(lines[j])
        if m2 and j != start and m2.group(1) == indent:
            break
        ms = STATUS_LINE_RE.match(lines[j])
        if ms and len(ms.group(1)) > len(indent):
            return j, ms.group(1)
    return None, ids_present


def cmd_set_task_station(args):
    resolved = _resolve_plan(args.file)
    legal = _legal_stations(resolved)
    if args.station not in legal:
        _refuse_illegal_station(args.station, legal)

    missing = {}

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        lines = text.splitlines(keepends=True)
        idx, info = _task_status_line(lines, args.task)
        if idx is None:
            missing["ids"] = info
            return base_bytes
        newline = "\n" if lines[idx].endswith("\n") else ""
        lines[idx] = f"{info}status: {args.station}{newline}"
        return "".join(lines).encode("utf-8")

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    if "ids" in missing:
        present = ", ".join(missing["ids"]) or "(none)"
        print(f"plan-merge: {args.task} is not in {resolved} — it carries: {present}",
              file=sys.stderr)
        sys.exit(3)
    print(f"STATION {args.task} -> {args.station}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def _replace_top_level_status(lines, station):
    """Rewrite an existing column-0 `status:` line in place. True when one was found.

    The indent group must be EMPTY: every task carries its own `status:` and an indented match
    would rewrite the first task's station instead of the feature's.
    """
    for i, line in enumerate(lines):
        m = STATUS_LINE_RE.match(line)
        if m and m.group(1) == "":
            newline = "\n" if line.endswith("\n") else ""
            lines[i] = f"status: {station}{newline}"
            return True
    return False


def _insert_status_after_feature(lines, station):
    """Insert a `status:` line immediately after the top-level `feature:` key. True when done."""
    for i, line in enumerate(lines):
        if FEATURE_LINE_RE.match(line):
            lines.insert(i + 1, f"status: {station}\n")
            return True
    return False


def _splice_top_level_status(lines, station):
    """Set plan.yaml's top-level `status`, returning the new bytes, or None if there is nowhere.

    None means the document carries no top-level `feature:` key to anchor to, which the caller
    turns into a refusal — this function never raises, so the lock plumbing and the text edit
    stay separable. Extracted from `cmd_set_feature_station.transform` (FEAT-41 F-05), which
    interleaved two splice strategies with the refusal at grade 3.

    REPLACE the existing top-level status, or INSERT immediately after `feature:` so the file
    keeps a stable key order. Appending at the end would work and would also make every
    plan.yaml's key order depend on the order the verbs happened to run in.
    """
    if (_replace_top_level_status(lines, station)
            or _insert_status_after_feature(lines, station)):
        return "".join(lines).encode("utf-8")
    return None


def cmd_set_feature_station(args):
    resolved = _resolve_plan(args.file)
    legal = _legal_stations(resolved)
    if args.station not in legal:
        _refuse_illegal_station(args.station, legal)

    def transform(base_bytes):
        lines = base_bytes.decode("utf-8").splitlines(keepends=True)
        spliced = _splice_top_level_status(lines, args.station)
        if spliced is None:
            raise harness_merge.MergeRefusal(
                5,
                [f"plan-merge: {resolved} carries no top-level feature: key to anchor status to"],
            )
        return spliced

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    print(f"STATION {resolved} -> {args.station}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def cmd_sign_approval(args):
    """THE ONLY WAY THE APPROVAL MAPPING IS EVER WRITTEN (D-04, FEAT-41 T-03).

    Every other verb leaves the base's approval bytes byte-identical and `apply` still exits 8
    on a proposal carrying a different one. That prohibition and this verb are the same rule seen
    from two sides: approval is written HERE, deliberately, by the main session, and nowhere
    else by accident."""
    # #1103: a structural identity check INSIDE this verb, not only plan-sign-gate.py's hook.
    # That hook must PARSE untrusted shell text to predict whether a command will reach here,
    # and four shell forms have evaded that prediction across three review cycles (FEAT-41
    # F-03, H-02, C2-03, MF-1) while still literally invoking this verb. This check needs no
    # prediction: it reads the caller's own real identity at the moment this code actually runs.
    #
    # HARNESS_AGENT_TYPE is injected onto a governed subagent's Bash environment by the OMP
    # host itself (harness-hooks.ts's `tool_call` handler), from the same `agent_type` the hook
    # payload already carries — never from anything this command's own argv or text supplies,
    # and never set by this process. AN ABSENT VARIABLE IS THE MAIN SESSION, the identical
    # exemption plan-sign-gate.py's own hook already uses for the identical reason ("AN ABSENT
    # OR EMPTY agent_type IS THE MAIN SESSION"), and the one convention this whole codebase
    # applies without exception (dispatch-guard.sh, bash-write-guard.sh, check-domain.sh,
    # validate-digest.py). Treating absence as a refusal here would refuse the main session's
    # own legitimate signature — a stricter check that is wrong, not merely untested.
    #
    # RESIDUAL, STATED RATHER THAN HIDDEN: a caller sophisticated enough to scrub its own
    # environment before invoking this command (`env -u HARNESS_AGENT_TYPE ...`) still defeats
    # this, the same way plan-sign-gate.py's own docstring already concedes for itself — "a
    # guardrail against a signature written out of over-eagerness, NOT a security boundary."
    # This closes the four DEMONSTRATED shell-syntax leaks and needs no new case when a fifth
    # surfaces; it does not claim to close deliberate sabotage of its own identity signal.
    _signing_agent = os.environ.get("HARNESS_AGENT_TYPE") or ""
    if _signing_agent:
        for line in (
            f"REFUSED: {_signing_agent} may not sign an approval — only the main session may "
            "(REQ-05/DEC-120).",
            "This is enforced from inside cmd_sign_approval itself, not only by the calling "
            "hook, so no shell form of this call can reach a write.",
        ):
            print(line, file=sys.stderr)
        sys.exit(10)
    resolved = _resolve_plan(args.file)

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        lines = text.splitlines(keepends=True)
        start = None
        for i, line in enumerate(lines):
            if re.match(r"^approval:\s*$", line):
                start = i
                break
        if start is None:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {resolved} carries no approval: mapping to sign"]
            )
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].strip() and not lines[j].startswith((" ", "\t")):
                end = j
                break
        fields = {"status": "approved", "approved_by": args.by, "date": args.date}
        written = set()
        out = []
        for line in lines[start + 1:end]:
            m = re.match(r"^(\s+)(status|approved_by|date):\s*(.*)$", line)
            if m and m.group(2) not in written:
                out.append(_field_lines(m.group(1), m.group(2), fields[m.group(2)]))
                written.add(m.group(2))
            else:
                out.append(line)
        for key in ("status", "approved_by", "date"):
            if key not in written:
                out.insert(0, _field_lines("  ", key, fields[key]))
        spliced = "".join(lines[:start + 1] + out + lines[end:]).encode("utf-8")
        _verify_signature(spliced, resolved, fields)
        return spliced

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    print(f"SIGNED {resolved} by {args.by} on {args.date}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


# ---------------------------------------------------------------------------
# BUG-1128 — `amend`, the route that did not exist.
#
# FEAT-41 T-09 denies every Edit/Write to a plan.yaml for every author, and `apply`
# is ADD-ONLY (exit 7 on a changed value). Correct separately; together they left a
# signed plan uncorrectable by anyone, and FEAT-46 accumulated eight staged-but-
# unappliable amendment blocks. This is the same shape BUG-1080 fixed one layer up:
# a rule shipped without reconciling what it makes impossible.
#
# IT IS A COMPARE-AND-SWAP, NOT A WRITE. `--show` prints the field block and its
# sha256; a replace must name that hash. The lock alone cannot help here: a caller
# that read the field, thought, and then wrote would clobber a concurrent edit while
# holding the lock perfectly. The hash is what makes the read part of the promise.
#
# IT REACHES `decisions:`. FEAT-46's worst overclaims are D-05 and D-14, so a
# task-scoped verb would leave exactly the blocks that motivated it unreachable.
# `approval:` is NOT reachable: it is the main session's alone (DEC-120) and
# `sign-approval` is its only writer.
AMENDABLE_KEYS = ("tasks", "decisions")
ITEM_ID_RE = re.compile(r"^(\s*)-\s+id:\s*(\S+)\s*$")
SIBLING_KEY_RE = re.compile(r"^(\s*)([A-Za-z_][\w-]*):")


def _item_range(lines, key, iid):
    """(start, end, indent) of the `- id: iid` item under top-level `key`.

    Returns (None, None, ids_present) when absent, so the refusal can name what IS there.
    The id list is SCOPED TO `key` — listing decision ids for a `--key tasks` miss would
    invite a retry that fails for an unrelated reason, the precedent _task_status_line set.
    """
    _l, _order, ranges, _pre = _index_top_keys("".join(lines))
    if key not in ranges:
        return None, None, []
    lo, hi = ranges[key]
    ids_present, start, indent = [], None, ""
    for i in range(lo, hi):
        m = ITEM_ID_RE.match(lines[i])
        if not m:
            continue
        ids_present.append(m.group(2))
        if m.group(2) == iid and start is None:
            start, indent = i, m.group(1)
        elif start is not None and len(m.group(1)) <= len(indent):
            return start, i, indent
    if start is None:
        return None, None, ids_present
    return start, hi, indent


BLOCK_HEAD_RE = re.compile(r"^(\s*)([A-Za-z_][\w-]*):\s*([|>][+-]?\d*)\s*$")


def _block_scalar_end(lines, head, end):
    """First index after the block-scalar body opened at `head`.

    A block scalar's body is every following line indented deeper than its key, plus blank
    lines. NOTHING inside it is YAML: it is opaque text. Skipping it is what stops a prose
    line that happens to read `verify:` from being mistaken for a key (BUG-1128 panel V1).
    """
    key_indent = len(BLOCK_HEAD_RE.match(lines[head]).group(1))
    j = head + 1
    while j < end:
        stripped = lines[j].strip()
        if stripped and (len(lines[j]) - len(lines[j].lstrip())) <= key_indent:
            break
        j += 1
    return j


def _trim_tail(lines, first, last, comments_are_document):
    """Pull `last` back past trailing lines that belong to the DOCUMENT, not the field.

    BUG-1128 panel N1, reproduced independently by all four reviewers. The tail scan stopped
    only at the next item or the next sibling key; a `# NOTE` line and a blank line match
    NEITHER, so both were swept into the replaced range and DELETED by the splice, at exit 0
    under a clean AMENDED receipt.

    `_verify_amend` cannot catch that and never could: the amended field's own value is exactly
    what was asked for. Only the boundary was wrong, and a value check cannot see a boundary.

    `comments_are_document` IS NOT A CONVENIENCE. Inside a `|` body a `#` line is CONTENT — a
    shell or Python comment in a verify script — and trimming it silently truncated the value.
    The first cut of this fix did exactly that, found by loading a block whose last line was a
    comment and comparing against `yaml.safe_load`. So comments are document structure for a
    plain scalar, where a continuation cannot begin with `#`, and content for a block scalar.
    """
    while last - 1 > first:
        stripped = lines[last - 1].strip()
        if stripped == "":
            last -= 1
            continue
        if comments_are_document and stripped.startswith("#"):
            last -= 1
            continue
        break
    return last


def _dedent_value(block, indent, field):
    """The field's VALUE as `--value-file` expects it, derived from raw lines only.

    BUG-1128 panel N3. Two shapes, and the inverse of `_render_field` in both:

    A block scalar's value is its body with the emission indent removed, and it keeps a
    trailing newline because `|` does. A plain scalar's value is what follows `field: `, with
    continuation lines joined at one space, which is how YAML folds them.

    No parsing: `--show` must keep working on a plan whose YAML is broken, since repairing one
    is what the verb is for.
    """
    if not block:
        return ""
    if BLOCK_HEAD_RE.match(block[0]):
        body_indent = len(indent) + 2
        out = [ln[body_indent:] if len(ln) > body_indent else ln.lstrip(" ")
               for ln in block[1:]]
        return "".join(out)
    head = block[0].split(":", 1)[1].strip()
    rest = [ln.strip() for ln in block[1:] if ln.strip()]
    return " ".join([head] + rest) + "\n"


def _find_field_line(lines, start, end, item_indent, field):
    """(index, indent) of the item's own `field:` line, or (None, "").

    BLOCK-SCALAR AWARE (BUG-1128 panel V1, three readers). The first cut matched
    `^\\s*field:` over physical lines, so `--field verify` bound to a prose line inside an
    `intent: |` body and the replace corrupted `intent` while reporting `AMENDED ... verify` at
    exit 0. The compare-and-swap could not help: both hashes are taken over whatever the
    locator returns, so they agree perfectly on the wrong block.
    """
    i = start
    while i < end:
        m = SIBLING_KEY_RE.match(lines[i])
        if m and m.group(2) == field and len(m.group(1)) > len(item_indent):
            return i, m.group(1)
        head = BLOCK_HEAD_RE.match(lines[i])
        if head and len(head.group(1)) > len(item_indent):
            i = _block_scalar_end(lines, i, end)   # opaque text, never scanned for keys
            continue
        i += 1
    return None, ""


def _plain_scalar_end(lines, first, end, indent):
    """First index after a plain scalar's continuation lines."""
    for j in range(first + 1, end):
        if ITEM_ID_RE.match(lines[j]):
            return j
        m = SIBLING_KEY_RE.match(lines[j])
        if m and len(m.group(1)) <= len(indent):
            return j
    return end


def _field_block(lines, start, end, item_indent, field):
    """(first, last_exclusive, indent) of `field:` inside one item, or None.

    The block runs from the `field:` line through its continuation lines — a plain multi-line
    scalar or a `|` body is one unit — and stops short of trailing comments and blank lines,
    which belong to the document rather than the field (panel N1).
    """
    first, indent = _find_field_line(lines, start, end, item_indent, field)
    if first is None:
        return None
    is_block = bool(BLOCK_HEAD_RE.match(lines[first]))
    if is_block:
        last = _block_scalar_end(lines, first, end)
    else:
        last = _plain_scalar_end(lines, first, end, indent)
    # Comments are DOCUMENT structure for a plain scalar, whose continuation cannot begin with
    # `#`, and CONTENT for a block scalar, whose body routinely carries shell and Python
    # comments. Trimming them from a block silently truncated the value.
    return first, _trim_tail(lines, first, last, not is_block), indent


def _render_field(indent, field, value_text, original):
    """Emit the replacement, PRESERVING THE ORIGINAL FIELD'S FORM.

    Two lessons, both paid for:

    `_field_lines` is the one renderer for a plain value — a local quoting rule re-derives
    only part of what PyYAML knows, and the first cut's rule would have written `title: yes`
    reloading as boolean True.

    BUT `yaml.safe_dump` NEVER EMITS `|` (BUG-1128 panel V2). Routing a literal block through
    it changes the emitted form and drops the trailing newline a `|` body carries, so an
    IDENTITY replace of a `verify: |` field altered what `safe_load` returned. SPEC.md:1813
    makes that literal form a byte-exact contract. So when the original was a block scalar its
    header is REUSED VERBATIM and the body is emitted as given, which is both form-preserving
    and escape-free.
    """
    head = BLOCK_HEAD_RE.match(original[0]) if original else None
    if head:
        body_indent = f"{indent}  "
        body = value_text[:-1] if value_text.endswith("\n") else value_text
        out = [original[0]]
        out += [f"{body_indent}{ln}\n" if ln.strip() else "\n"
                for ln in body.split("\n")]
        return ["".join(out)]
    return [_field_lines(indent, field, value_text.strip("\n"))]


def _die(code, *lines):
    """Print a refusal to stderr and exit. Collapses the print/exit pairs that made
    `cmd_amend` an ABC outlier without changing a single message."""
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(code)


def _amend_locate(args, resolved, lines):
    """(first, last, indent) for the field named by `args`, or a refusal.

    Both refusals name what IS present, because a caller who mistyped needs the real list
    rather than a bare no. The id list is scoped to `--key`, the precedent
    `_task_status_line` set: offering decision ids for a `--key tasks` miss invites a retry
    that fails for an unrelated reason.
    """
    start, end, info = _item_range(lines, args.key, args.id)
    if start is None:
        _die(3, f"plan-merge: {args.id} is not under {args.key}: in {resolved} — it carries: "
                f"{', '.join(info) or '(none)'}")
    located = _field_block(lines, start, end, info, args.field)
    if located is None:
        _die(4, f"plan-merge: {args.id} carries no {args.field}: field. amend REPLACES; adding "
                f"a field is apply's job, and a verb that silently grows a plan is how it "
                f"acquires a key nobody reviewed.")
    return located


def _require_locked_hash(block_lines, expected, iid, field):
    """Refuse unless the block under the lock still hashes to what the caller named.

    THE CHECK THAT IS ACTUALLY LOAD-BEARING. The pre-lock check gives the caller a fast,
    precise refusal; this one is the guarantee, because only here are the bytes known not to be
    changing underneath. A caller that read a field, thought about it, and then wrote would
    otherwise clobber a concurrent edit while holding the lock perfectly.

    EXTRACTED SO IT CAN BE PINNED (panel F2). It survived being mutated out at 0 of 244 FAIL
    for four consecutive cycles, because nothing could reach it: reproducing the race
    end-to-end needs two processes interleaved inside one flock. As a named function it is
    unit-testable, which is the same remedy `_verify_amend` got for the same reason.
    """
    if hashlib.sha256("".join(block_lines).encode("utf-8")).hexdigest() != expected:
        raise harness_merge.MergeRefusal(
            6, [f"plan-merge: {iid}.{field} changed between the read and the lock."])


def _expected_value(rendered, indent, field):
    """What YAML will load from the lines we are about to splice in.

    ASK YAML, DO NOT REIMPLEMENT IT (panel F1), in this direction too. The previous `want` was
    hand-derived — `value_text` for a block header and `value_text.strip()` otherwise — correct
    for `|` and WRONG for `|-`, `|+` and `>`, which strip, keep and fold respectively.

    THE PROBE KEEPS THE ORIGINAL INDENTATION, and that is the whole subtlety. The first cut
    dedented the rendered field to column zero before parsing, which CHANGES THE ANSWER: a
    quoted multi-line scalar folds its newline to a space at column zero and preserves it at
    indent four. Measured, not reasoned about. So the field is parsed inside a synthetic item
    at exactly the nesting it will occupy.

    It is independent of the splice on purpose. Deriving `want` from the spliced document would
    make `_verify_amend` compare that document against itself and pass unconditionally.
    """
    item_indent = indent[:-2] if len(indent) >= 2 else ""
    probe = f"_p:\n{item_indent}- id: _x\n" + "".join(rendered)
    try:
        doc = yaml.safe_load(probe)
    except yaml.YAMLError:
        return None
    items = (doc or {}).get("_p")
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        return None
    return items[0].get(field)


# `None` cannot mean both "the document will not parse" and "the field is null" — conflating
# them made a null field fall through to the line-based reader and print as an empty string
# (panel F1, code-reviewer). A sentinel keeps the two answers separable.
_UNPARSEABLE = object()


def _parsed_value(raw, key, iid, field):
    """The field's value as YAML loads it, or None when the document will not parse.

    ASK YAML, DO NOT REIMPLEMENT IT (panel F1). The line-based reader diverged from the parser
    on four legal shapes at once: `|` clips to one trailing newline, `|-` strips it, `|+` keeps
    every one, and `>` FOLDS newlines into spaces. All four produced the same `--show` output
    and four different real values, so feeding that output back through the tool's own
    documented workflow silently rewrote the field.

    This is the third time in this feature that hand-rolling what PyYAML already knows was the
    defect: first a quoting rule, then form preservation, now value extraction.
    """
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError:
        return _UNPARSEABLE
    for item in (doc or {}).get(key) or []:
        if isinstance(item, dict) and item.get("id") == iid:
            return item.get(field)
    return _UNPARSEABLE


def _amend_show(lines, located, field, actual, raw, key, iid):
    """Print the field's VALUE and its hash, and exit.

    THE VALUE, NOT THE BLOCK (panel N3): `--value-file` takes the bare value, and printing the
    block with its `field:` key line meant feeding the output back wrote the key line INTO the
    value at exit 0. The identity check cannot catch that, because the corrupted value is
    byte-for-byte what the caller asked for.

    THE PARSER IS THE AUTHORITY (panel F1). The line-based path survives only as the fallback
    for a document that will not parse — which is the case this verb exists to repair — and it
    says so on stderr rather than pretending to be exact.
    """
    first, last, indent = located
    value = _parsed_value(raw, key, iid, field)
    if value is _UNPARSEABLE:
        sys.stderr.write("plan-merge: this plan does not parse, so the value below is derived "
                         "from raw lines and may not match what YAML would load. It is shown to "
                         "help you repair the document, not to be fed back verbatim.\n")
        sys.stdout.write(_dedent_value(lines[first:last], indent, field))
    elif not isinstance(value, str):
        _die(4, f"plan-merge: {iid}.{field} is a {type(value).__name__}, not text. amend "
                f"replaces TEXT scalars; a list or mapping field would need its structure "
                f"rewritten, which is apply's job.")
    else:
        sys.stdout.write(value if value.endswith("\n") else value + "\n")
    print(f"sha256: {actual}")
    sys.exit(0)


def _amend_preconditions(args, actual):
    """Refuse a replace that is missing its expectation, or naming a stale one."""
    if not args.expect_sha256 or not args.value_file:
        _die(2, "plan-merge: a replace needs BOTH --expect-sha256 and --value-file. Omitting "
                "the hash would make this a force-write, which is the hand-edit T-09 denies "
                "wearing a tool's name. Run --show first.")
    if args.expect_sha256 != actual:
        _die(6, f"plan-merge: --expect-sha256 does not match {args.id}.{args.field} — the field "
                f"changed since you read it. expected {args.expect_sha256} actual sha256: "
                f"{actual}. Re-run --show and re-derive your replacement.")


def cmd_amend(args):
    import hashlib

    if args.key not in AMENDABLE_KEYS:
        _die(2, f"plan-merge: --key {args.key} is not amendable — expected one of: "
                f"{', '.join(AMENDABLE_KEYS)}. `approval:` is the main session's alone "
                f"(DEC-120) and sign-approval is its only writer.")

    resolved = _resolve_plan(args.file)
    with open(resolved, "rb") as fh:
        raw = fh.read().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    located = _amend_locate(args, resolved, lines)
    first, last, indent = located
    actual = hashlib.sha256("".join(lines[first:last]).encode("utf-8")).hexdigest()

    if args.show:
        _amend_show(lines, located, args.field, actual, raw, args.key, args.id)
    _amend_preconditions(args, actual)
    with open(args.value_file, encoding="utf-8") as fh:
        value_text = fh.read()

    def transform(base_bytes):
        # THE BASE IS PARSED FIRST (panel V4, and its own de-vacuumed test). It used to be
        # parsed last, outside a try, so a broken plan either crashed with a traceback or was
        # reported as "a splice defect: the base parsed" — which was false. Repairing a plan
        # nobody else may edit is this verb's whole purpose, so an unreadable base must refuse
        # cleanly and say which document is at fault.
        raw = base_bytes.decode("utf-8")
        try:
            base_doc = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise harness_merge.MergeRefusal(
                8, [f"plan-merge: the plan on disk does not parse, so amend cannot tell whether "
                    f"its own splice made things worse — {exc}"])
        cur = raw.splitlines(keepends=True)
        s2, e2, i2 = _item_range(cur, args.key, args.id)
        if s2 is None:
            raise harness_merge.MergeRefusal(
                3, [f"plan-merge: {args.id} vanished from {args.key}: under the lock."])
        loc2 = _field_block(cur, s2, e2, i2, args.field)
        if loc2 is None:
            raise harness_merge.MergeRefusal(
                4, [f"plan-merge: {args.id}.{args.field} vanished under the lock."])
        f2, l2, ind2 = loc2
        _require_locked_hash(cur[f2:l2], args.expect_sha256, args.id, args.field)
        rendered = _render_field(ind2, args.field, value_text, cur[f2:l2])
        spliced = "".join(cur[:f2] + rendered + cur[l2:])
        # THE CHECK THAT ACTUALLY BINDS (panel V3). The hash proves the block replaced is the
        # block that was read; it cannot see that the splice landed in the wrong FIELD, nor that
        # the value was re-formed on the way in, because both hashes are taken over whatever the
        # locator returned. This compares the reloaded VALUE against what was asked for — the
        # discipline `_verify_signature` already held for signing, and `amend` did not inherit.
        #
        # A `|` body KEEPS its trailing newline on reload, so the expected value is the file's
        # bytes verbatim; a plain scalar carries none. Getting that backwards made the identity
        # check refuse a CORRECT write, found by replacing a real `verify: |` with itself.
        want = _expected_value(rendered, ind2, args.field)
        reloaded = _verify_amend(spliced.encode("utf-8"), args.key, args.id, args.field, want)
        # DO NO HARM: hold the splice to the plan schema only when the BASE satisfied it. A plan
        # mid-authoring legitimately does not, and refusing to amend it would make this verb
        # useless exactly where it is needed most.
        if _schema_error(base_doc) is None:
            err = _schema_error(reloaded)
            if err:
                raise harness_merge.MergeRefusal(
                    8, [f"plan-merge: the amended plan would not be legal — {err}"])
        return spliced.encode("utf-8")

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    print(f"AMENDED {args.key}:{args.id}.{args.field}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


# EVERY VERB IS A ROW, NOT A PARAGRAPH (FEAT-41 F-05). `main` regressed from grade 4 to 3 on ABC
# alone — cyclomatic 2, cognitive 1, ABC 23.8 — when T-03 turned one verb into five and each one
# added four more registration calls to the same body. There was no logic to simplify: the verb
# set is DATA, and it was written as control flow.
#
# EVERY ARGUMENT OF EVERY VERB IS `required=True`, which is what makes one loop honest rather
# than a lossy compression of five paragraphs. If a verb ever needs an optional argument, this
# table is the wrong shape for it and it gets its own registration — do not add a `required`
# column and keep pretending the rows are uniform.
_FILE = ("--file", "path to the plan.yaml")
_STATION = ("--station", "one of the six stations, or abandoned")
_PROPOSAL = ("--proposal", "path to the proposed plan.yaml, or - for stdin")

# ADD-ONLY IS A PROPERTY OF THE FIRST TWO VERBS, NOT OF THE TOOL (FEAT-41 T-03). The lock and
# the splice are what fix #628 and they apply to every verb; never deleting a task is a separate
# promise that `apply` and its alias alone make, which is why they share `cmd_apply` verbatim.
VERBS = (
    ("apply", "merge a proposal into a plan.yaml — adds, never deletes",
     (_FILE, _PROPOSAL), cmd_apply),
    ("add-tasks", "alias of apply, for callers that only add tasks — identical code path",
     (_FILE, _PROPOSAL), cmd_apply),
    ("set-task-station", "set ONE task's status, by splicing its one line",
     (_FILE, ("--task", "the task id, T-NN"), _STATION), cmd_set_task_station),
    ("set-feature-station", "set or insert the top-level status key",
     (_FILE, _STATION), cmd_set_feature_station),
    ("sign-approval", "the ONLY route that writes the approval mapping",
     (_FILE, ("--by", "the signer's name"), ("--date", "YYYY-MM-DD")), cmd_sign_approval),
)


def _register_amend(sub):
    """ITS OWN REGISTRATION, BY THE VERBS TABLE'S OWN INSTRUCTION (BUG-1128).

    That table says: if a verb ever needs an optional argument, the table is the wrong
    shape for it and it gets its own registration — do not add a `required` column and
    keep pretending the rows are uniform. `amend` has three optional arguments, because
    `--show` legitimately takes neither a hash nor a value. So it registers here rather
    than corrupting the uniformity that makes that loop honest.
    """
    p = sub.add_parser("amend", help="replace ONE field of ONE named task or decision, "
                                     "compare-and-swap on its sha256")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--key", required=True,
                   help=f"which list the id lives in: {' | '.join(AMENDABLE_KEYS)}")
    p.add_argument("--id", required=True, help="the item id, T-NN or D-NN")
    p.add_argument("--field", required=True, help="the field to replace, e.g. verify, because")
    p.add_argument("--show", action="store_true",
                   help="print the current field block and its sha256, and write nothing")
    p.add_argument("--expect-sha256", default=None,
                   help="the sha256 --show reported; a replace is refused without it")
    p.add_argument("--value-file", default=None,
                   help="file holding the replacement value; may be multi-line")
    p.set_defaults(func=cmd_amend)


def main():
    parser = argparse.ArgumentParser(prog="plan-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, helptext, arguments, func in VERBS:
        p = sub.add_parser(name, help=helptext)
        for flag, arghelp in arguments:
            p.add_argument(flag, required=True, help=arghelp)
        p.set_defaults(func=func)
    _register_amend(sub)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
