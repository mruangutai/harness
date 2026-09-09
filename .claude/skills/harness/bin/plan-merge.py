#!/usr/bin/env python3
"""plan-merge.py — the second plan writer: it adds tasks, and deletes one only when it is
named and a reason is given (FEAT-32 T-03, D-01..D-04, DEC-182, DEC-120).

Reproduces and fixes #628: two whole-file writes to the same plan.yaml, one after another,
silently lose whatever the first one added. This CLI never does a whole-file rewrite of an
existing plan.yaml. It SPLICES TEXT — never re-renders through a YAML dumper (D-03) — keyed on
each task/decision's `id`, under harness_merge.locked_update so the replace stays atomic and the
lock stays the one shared with every other write route in this feature.

    plan-merge.py apply             --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py add-tasks         --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py set-task-station  --file <plan.yaml> --task T-NN --station <name>
    plan-merge.py set-feature-station --file <plan.yaml> --station <name>
    plan-merge.py set-panel         --file <plan.yaml> --value-file <panel.yaml>
    plan-merge.py sign-approval     --file <plan.yaml> --by <name> --date <YYYY-MM-DD> [--overrule PF-ID:<reason>]...
    plan-merge.py delete-items      --file <plan.yaml> --task T-NN [--task T-NN]... [--decision D-NN]... --reason "<text>"

CONTROLLED VERBS, ONE WRITE ROUTE (FEAT-41 T-03). Every mutating verb goes through
harness_merge.locked_update and a text splice, and require_destination (exit 9) guards every
path. ADD-ONLY IS A PROPERTY OF `apply` AND ITS ALIAS, NOT OF THE TOOL: the lock and the splice
are what fix #628 and they hold for every mutating verb, while never deleting a task is a promise
those two verbs alone make — and `delete-items` is the verb that promise left missing. With
`apply` add-only, `amend` able to replace ONE field of ONE existing item, and FEAT-41 T-09's
shape gate (#1045) denying every editor and shell write of a plan.yaml to every author, an
operator-ruled scope REMOVAL had no route at all: that is a missing verb, not a missing
permission. So `delete-items` removes WHOLE items from `tasks:` and `decisions:`, by id, with a
reason — never by predicate, never one field, never `approval:`, and never silently. An id that
is not in the plan, an id given twice, a SURVIVING task's `depends_on` still naming a task that
would go (issue #201's own defect), a result that fails the plan schema or does not reload as
the deletion that was computed: each is a loud non-zero refusal naming the concrete value, and
each leaves the file byte-identical. The reason is NEVER written into the plan — it exists so
the refusals can name why one was asked for, and so a caller cannot delete by reflex.

`set-task-station` and `set-feature-station` validate the station against the vocabulary
factory_config declares — MANDATED_STATIONS plus TERMINAL_MARKER, imported, never respelled —
resolved through the harness.json of the checkout the target plan.yaml belongs to. The check runs
BEFORE the lock is taken, so a refused value never opens the file.

`approval:` has two controlled write paths: `apply` seeds a brand-new plan with the
unsigned `status: pending` mapping, and `sign-approval` is the only path that can transition it
to approved or append an attributed risk acceptance to `approval.rulings`. Every other verb
operating on an existing plan leaves its approval bytes byte for byte. The main session — nobody
else — signs approval through this tool rather than by hand. A proposal
that carries an approval mapping which PARSES differently from the base's is a REFUSAL (exit 8),
not a silent drop: `apply` must be INCAPABLE of writing a signature (step 7) and must also NOTICE
a caller that tried to sneak one past it (step 7b) — two different jobs, so two different guards.

The creation exception is deliberately narrower than signing: a proposal cannot choose the pending
mapping's contents, and the tool emits only its fixed status. Without this bootstrap, a newly
created plan cannot later be signed because `sign-approval` correctly refuses to invent a missing
mapping.

Exit codes are the interface:
    0  applied — stdout lists ADDED/PRESERVED ids, an IGNORED-APPROVAL line if the proposal
       carried an approval block, and a final APPLIED line
    2  `delete-items`'s own command line is unusable: no --task and no --decision, the same id
       twice, or an empty --reason (argparse's code, and `amend`'s missing-hash precedent)
    3  an id named by --task or --decision is absent from the plan, or the plan file itself is
       (the message names the ids present, scoped to the list the id was asked for)
    4  the value given to --station is not a legal station (the message lists the legal ones),
       or a requested deletion is not legal: a SURVIVING task's `depends_on` names a task being
       deleted, named pair by pair
    5  a side (base or proposal) failed to parse as YAML, or a splice does not reload as the
       edit that was computed — for a deletion, that includes a survivor whose own fields moved
    6  the lock could not be acquired within the retry budget (harness_merge)
    7  the same id, or the same top-level key, carries two different loaded values
    8  the proposal's approval mapping parses differently from the base's
    9  --file does not resolve to a plan.yaml this tool owns

python3 stdlib plus PyYAML (DEC-171 requires it here). Reads go through harness_yaml.py, same as
every other harness tool (issue #720): a duplicate mapping key refuses here exactly as it would
downstream, instead of merging clean and breaking the next reader. `import yaml` survives ONLY
for `yaml.safe_dump` — harness_yaml.py exposes no serializer, and this file never re-renders a
whole document through one regardless (see D-03 below); it splices bytes and re-parses its own
splice as a self-check.
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


def _panel_finding_ids(doc):
    panel = doc.get("panel") if isinstance(doc, dict) else None
    findings = panel.get("findings", []) if isinstance(panel, dict) else []
    return {
        str(item.get("id", "")).strip()
        for item in findings
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }


def _parse_overrule(spec, finding_ids):
    finding, separator, reason = spec.partition(":")
    finding, reason = finding.strip(), reason.strip()
    if not separator or not finding or not reason:
        raise harness_merge.MergeRefusal(
            4, ["plan-merge: --overrule must be FINDING-ID:non-empty reason"]
        )
    if finding not in finding_ids:
        present = ", ".join(sorted(finding_ids)) or "<none>"
        raise harness_merge.MergeRefusal(
            4, [f"plan-merge: --overrule finding {finding} is not in panel.findings",
                f"  current finding ids: {present}"],
        )
    return finding, reason


def _requested_overrules(specs, doc, who, date):
    """Validate `FINDING:REASON` arguments against the panel snapshot being signed."""
    invalid_attribution = (
        not str(who).strip()
        or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", str(date).strip())
    )
    if specs and invalid_attribution:
        raise harness_merge.MergeRefusal(
            4, ["plan-merge: --overrule requires a non-empty --by and YYYY-MM-DD --date"]
        )
    finding_ids = _panel_finding_ids(doc)
    parsed = [_parse_overrule(spec, finding_ids) for spec in specs]
    return [
        {"finding": finding, "who": who, "date": date, "reason": reason}
        for finding, reason in parsed
    ]


def _rulings_lines(indent, rulings):
    dumped = yaml.safe_dump(rulings, sort_keys=False, width=10 ** 9, allow_unicode=True)
    return [f"{indent}rulings:\n"] + [
        f"{indent}  {line}\n" for line in dumped.rstrip("\n").split("\n")
    ]


def _rulings_key(lines):
    for index, line in enumerate(lines):
        match = re.match(r"^(\s+)rulings:\s*(.*)$", line)
        if match:
            return index, match.group(1)
    return None, "  "


def _before_trailing_comments(lines, floor=0):
    index = len(lines)
    while index > floor and (
        not lines[index - 1].strip() or lines[index - 1].lstrip().startswith("#")
    ):
        index -= 1
    return index


def _next_approval_key(lines, start, indent):
    sibling = re.compile(rf"^{re.escape(indent)}[A-Za-z_][\w-]*:")
    return next((i for i in range(start, len(lines)) if sibling.match(lines[i])), len(lines))


def _splice_approval_rulings(lines, rulings):
    """Replace only approval.rulings, retaining sibling fields and trailing comments."""
    key_at, indent = _rulings_key(lines)
    if key_at is None:
        insert_at = _before_trailing_comments(lines)
        return lines[:insert_at] + _rulings_lines(indent, rulings) + lines[insert_at:]
    end = _next_approval_key(lines, key_at + 1, indent)
    content_end = _before_trailing_comments(lines[:end], key_at + 1)
    return (lines[:key_at] + _rulings_lines(indent, rulings)
            + lines[content_end:])


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
        reloaded = harness_yaml.load_str(spliced_bytes.decode("utf-8"), "<spliced signature>")
    except harness_yaml.YamlParseError as exc:
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
        return harness_yaml.load_str(spliced_bytes.decode("utf-8"), "<spliced plan>")
    except harness_yaml.YamlParseError as exc:
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
        reloaded = harness_yaml.load_str(spliced_bytes.decode("utf-8"), "<merged plan>")
    except harness_yaml.YamlParseError as exc:
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
        # A new plan needs an unsigned approval mapping before the main session can later sign it.
        # The proposal may not supply that mapping: accepting any caller-owned value would let
        # `apply` mint an approved plan, bypassing cmd_sign_approval's identity gate.
        try:
            prop_doc = harness_yaml.load_str(proposal_text, "<proposal>")
        except harness_yaml.YamlParseError as exc:
            raise harness_merge.MergeRefusal(
                5, [f"UNPARSEABLE: proposal failed to parse: {exc}"]
            )
        prop_doc = prop_doc if isinstance(prop_doc, dict) else {}
        if APPROVAL_REFUSAL and "approval" in prop_doc:
            raise harness_merge.MergeRefusal(
                8,
                [
                    "REFUSED: proposal carries an approval mapping and the base does not exist.",
                    "  base approval: <absent>",
                    f"  proposal approval: {prop_doc.get('approval')!r}",
                    "  apply seeds a fixed pending mapping; only the main session may approve it through sign-approval.",
                ],
            )
        lines = proposal_text.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if FEATURE_LINE_RE.match(line):
                lines[index + 1:index + 1] = ["approval:\n", "  status: pending\n"]
                return "".join(lines).encode("utf-8"), [], [], False
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: proposal carries no top-level feature: key to anchor approval."]
        )

    base_text = base_bytes.decode("utf-8")
    try:
        base_doc = harness_yaml.load_str(base_text, "<base plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(5, [f"UNPARSEABLE: base failed to parse: {exc}"])
    try:
        prop_doc = harness_yaml.load_str(proposal_text, "<proposal>")
    except harness_yaml.YamlParseError as exc:
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
def _load_panel_value(path):
    try:
        panel = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: cannot load panel value from {path}: {exc}"])
    required = {
        "last_run": str,
        "cycle": int,
        "readers": list,
        "findings": list,
    }
    if not isinstance(panel, dict):
        raise harness_merge.MergeRefusal(
            5, ["plan-merge: panel value must be a mapping"])
    missing = [key for key in required if key not in panel]
    if missing:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: panel value is missing required key(s): {', '.join(missing)}"])
    wrong = [
        key for key, expected in required.items()
        if not isinstance(panel[key], expected) or (key == "cycle" and isinstance(panel[key], bool))
    ]
    if wrong:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: panel value has invalid type for: {', '.join(wrong)}"])
    return panel


def cmd_set_panel(args):
    resolved = _resolve_plan(args.file)
    try:
        panel = _load_panel_value(args.value_file)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    replacement = yaml.safe_dump({"panel": panel}, sort_keys=False).splitlines(keepends=True)

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        lines, _order, ranges, _preamble = _index_top_keys(text)
        if "panel" in ranges:
            start, end = ranges["panel"]
            lines[start:end] = replacement
        elif "tasks" in ranges:
            start, _end = ranges["tasks"]
            lines[start:start] = replacement
        else:
            lines.extend(replacement)
        spliced = "".join(lines).encode("utf-8")
        reloaded = _reload_or_refuse(spliced)
        if reloaded.get("panel") != panel:
            raise harness_merge.MergeRefusal(
                5, ["plan-merge: panel does not reload as the value supplied"])
        return spliced

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    print(f"PANEL cycle {panel['cycle']} -> {resolved}")
    print(f"APPLIED {resolved}")
    sys.exit(0)




def _approval_fields(base_bytes, args):
    fields = {"status": "approved", "approved_by": args.by, "date": args.date}
    base_doc = _reload_or_refuse(base_bytes)
    requested = _requested_overrules(args.overrule, base_doc, args.by, args.date)
    if not requested:
        return fields
    approval = base_doc.get("approval") or {}
    existing = approval.get("rulings", [])
    if not isinstance(existing, list):
        raise harness_merge.MergeRefusal(
            5, ["plan-merge: approval.rulings is malformed; expected a list"]
        )
    fields["rulings"] = existing + requested
    return fields


def _approval_span(lines):
    start = next((i for i, line in enumerate(lines)
                  if re.match(r"^approval:\s*$", line)), None)
    if start is None:
        return None, None
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith((" ", "\t"))), len(lines))
    return start, end


def _new_approval_block(fields):
    block = ["approval:\n"]
    block.extend(_field_lines("  ", key, fields[key])
                 for key in ("status", "approved_by", "date"))
    if "rulings" in fields:
        block.extend(_rulings_lines("  ", fields["rulings"]))
    return block


def _replace_signature_fields(body, fields):
    written = set()
    output = []
    for line in body:
        match = re.match(r"^(  )(status|approved_by|date):\s*(.*)$", line)
        if not match or match.group(2) in written:
            output.append(line)
            continue
        output.append(_field_lines(match.group(1), match.group(2), fields[match.group(2)]))
        written.add(match.group(2))
    return output, written


def _updated_approval_body(body, fields):
    output, written = _replace_signature_fields(body, fields)
    missing = [key for key in ("status", "approved_by", "date") if key not in written]
    for key in missing:
        output.insert(0, _field_lines("  ", key, fields[key]))
    if "rulings" in fields:
        return _splice_approval_rulings(output, fields["rulings"])
    return output


def _signed_approval_bytes(base_bytes, resolved, args):
    lines = base_bytes.decode("utf-8").splitlines(keepends=True)
    fields = _approval_fields(base_bytes, args)
    start, end = _approval_span(lines)
    if start is None:
        insert_at = next(
            (i + 1 for i, line in enumerate(lines) if re.match(r"^feature:\s*", line)), None
        )
        if insert_at is None:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {resolved} carries no feature key before signing"]
            )
        lines[insert_at:insert_at] = _new_approval_block(fields)
    else:
        lines[start + 1:end] = _updated_approval_body(lines[start + 1:end], fields)
    spliced = "".join(lines).encode("utf-8")
    _verify_signature(spliced, resolved, fields)
    return spliced


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
        return _signed_approval_bytes(base_bytes, resolved, args)

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
        doc = harness_yaml.load_str(probe, "<rendered field probe>")
    except harness_yaml.YamlParseError:
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
        doc = harness_yaml.load_str(raw, "<base plan>")
    except harness_yaml.YamlParseError:
        return _UNPARSEABLE
    for item in (doc or {}).get(key) or []:
        if isinstance(item, dict) and item.get("id") == iid:
            return item.get(field)
    return _UNPARSEABLE


def _amend_show(lines, located, field, actual, raw, key, iid, yaml_value=False):
    """Print the field value and its hash, preserving structured values only by opt-in."""
    first, last, indent = located
    value = _parsed_value(raw, key, iid, field)
    if value is _UNPARSEABLE:
        sys.stderr.write("plan-merge: this plan does not parse, so the value below is derived "
                         "from raw lines and may not match what YAML would load. It is shown to "
                         "help you repair the document, not to be fed back verbatim.\n")
        sys.stdout.write(_dedent_value(lines[first:last], indent, field))
    elif isinstance(value, str):
        sys.stdout.write(value if value.endswith("\n") else value + "\n")
    elif yaml_value and isinstance(value, (list, dict)):
        sys.stdout.write(yaml.safe_dump(value, sort_keys=False))
    else:
        _die(4, f"plan-merge: {iid}.{field} is a {type(value).__name__}, not text. amend "
                f"replaces TEXT scalars unless --yaml-value explicitly selects a list or "
                f"mapping field.")
    print(f"sha256: {actual}")
    sys.exit(0)


def _structured_field_lines(indent, field, value):
    dumped = yaml.safe_dump({field: value}, sort_keys=False).splitlines(keepends=True)
    return [indent + line if line.strip() else line for line in dumped]


def _load_structured_value(path):
    try:
        value = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as exc:
        _die(5, f"plan-merge: cannot load structured value from {path}: {exc}")
    if not isinstance(value, (list, dict)):
        _die(5, "plan-merge: --yaml-value requires a YAML list or mapping")
    return value


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
        _amend_show(lines, located, args.field, actual, raw, args.key, args.id,
                    yaml_value=args.yaml_value)
    _amend_preconditions(args, actual)
    if args.yaml_value:
        want_value = _load_structured_value(args.value_file)
        value_text = None
    else:
        with open(args.value_file, encoding="utf-8") as fh:
            value_text = fh.read()
        want_value = None

    def transform(base_bytes):
        # THE BASE IS PARSED FIRST (panel V4, and its own de-vacuumed test). It used to be
        # parsed last, outside a try, so a broken plan either crashed with a traceback or was
        # reported as "a splice defect: the base parsed" — which was false. Repairing a plan
        # nobody else may edit is this verb's whole purpose, so an unreadable base must refuse
        # cleanly and say which document is at fault.
        raw = base_bytes.decode("utf-8")
        try:
            base_doc = harness_yaml.load_str(raw, "<base plan>")
        except harness_yaml.YamlParseError as exc:
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
        if args.yaml_value:
            current = _parsed_value(raw, args.key, args.id, args.field)
            if not isinstance(current, (list, dict)):
                raise harness_merge.MergeRefusal(
                    5, [f"plan-merge: {args.id}.{args.field} is not a list or mapping under "
                        "the lock; --yaml-value cannot change a scalar field's type."])
            rendered = _structured_field_lines(ind2, args.field, want_value)
            want = want_value
        else:
            rendered = _render_field(ind2, args.field, value_text, cur[f2:l2])
            want = _expected_value(rendered, ind2, args.field)
        spliced = "".join(cur[:f2] + rendered + cur[l2:])
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


# ---------------------------------------------------------------------------
# `delete-items` — the verb the add-only property left missing.
#
# `apply` is add-only by promise, `amend` replaces ONE field of ONE existing item, and FEAT-41
# T-09 (#1045) denies every editor and shell write of a plan.yaml to every author. Each is
# correct alone; together they left an operator-ruled SCOPE REMOVAL with no route at all — not
# a permission anybody could be granted, a verb nobody had written. This is the same shape
# BUG-1128 fixed for correcting a field, one step further: a rule shipped without reconciling
# what it makes impossible.
#
# IT IS THE SAME WRITER AS EVERY OTHER VERB. The lock, the byte-level splice, the
# reload-or-refuse and the do-no-harm schema check are what fix #628 and they are properties of
# the TOOL; add-only is a property of two verbs. So this one reuses all four rather than
# growing a second write path, and it never re-renders a line: it FILTERS lines, so every
# survivor is byte-identical and a review diff shows deletions only.
#
# WHAT IT DELIBERATELY CANNOT DO: delete by predicate (only ids, named one at a time), delete a
# field (that is `amend`), delete `approval:` (the main session's alone, DEC-120), or delete
# anything quietly — an unknown id, a repeated id, or a surviving `depends_on` edge naming the
# doomed task is a loud non-zero refusal, and a refused call writes nothing.
DELETABLE_KEYS = ("tasks", "decisions")


def _refuse_empty_request(requested, reason):
    """Refuse a call that names nothing to delete, or gives no reason for deleting it.

    `--reason` IS REQUIRED AND IS NEVER WRITTEN. It exists so a refusal can name why a deletion
    was asked for and so a caller cannot delete by reflex; an empty one defeats both, so it is
    refused rather than accepted as a formality.
    """
    if not requested:
        raise harness_merge.MergeRefusal(
            2, ["plan-merge: delete-items needs at least one --task or --decision.",
                "  A call that names nothing to delete is a write with no subject, and "
                "reporting success for it would teach the caller that a typo'd flag worked."])
    if not reason.strip():
        raise harness_merge.MergeRefusal(
            2, ["plan-merge: --reason must not be empty.",
                "  It is never written into the plan; it exists so a deletion cannot be made "
                "by reflex and so a refusal can name why one was asked for."])


def _refuse_repeated_id(requested):
    """Refuse an id given twice, NEVER a set union.

    Deleting one item twice cannot be what was meant, and de-duplicating it silently would
    swallow the far likelier explanation — that one of the other ids the caller typed is wrong.
    """
    seen = set()
    for _key, iid in requested:
        if iid in seen:
            raise harness_merge.MergeRefusal(
                2, [f"plan-merge: {iid} was named twice on the command line.",
                    "  Deleting one item twice cannot be what was meant, and accepting it "
                    "would hide a typo in one of the other ids."])
        seen.add(iid)


def _requested_deletions(args):
    """[(key, id)] in command-line order, or a MergeRefusal(2) naming the offending value.

    CHECKED BEFORE THE LOCK IS TAKEN, the discipline `_refuse_illegal_station` states in full:
    a refused command line must never open the file, so a typo cannot contend for the lock or
    leave a partial write behind.
    """
    requested = [("tasks", tid) for tid in args.task]
    requested += [("decisions", did) for did in args.decision]
    _refuse_empty_request(requested, args.reason)
    _refuse_repeated_id(requested)
    return requested


def _last_nonblank(lines, lo, hi):
    """1 + the index of the last non-blank line in [lo, hi), or `lo` when they are all blank."""
    for index in range(hi - 1, lo - 1, -1):
        if lines[index].strip():
            return index + 1
    return lo


def _item_delete_end(lines, start, end, indent):
    """Where an item's OWN bytes stop, inside the dash-to-dash range `_index_list_items` gives.

    THE RANGE `_index_list_items` RETURNS IS TOO WIDE TO DELETE. It runs each item to the NEXT
    dash line, and the last item to the end of the key's block, so whatever whitespace and
    comments sit between two items land inside the earlier one. Two different answers are owed,
    and both were measured on FEAT-57's own plan.yaml rather than reasoned about:

    AN ITEM OWNS THE BLANK LINES THAT FOLLOW IT. Deleting five consecutive blank-separated
    tasks while calling those blanks "the document's" left FIVE blank lines behind, four of
    them stranded at end of file, and turned a deletions-only diff into one carrying
    insertions. Whitespace after an item is its separator; a human deleting the item in an
    editor takes it, and taking it is what makes N deletions leave N-1 separators rather than
    N-1 empty lines.

    AN ITEM DOES NOT OWN A TRAILING COMMENT. A `#` line between two items is a note somebody
    wrote about the list, and BUG-1128 panel N1 is this same defect one level down: a `# NOTE`
    matched neither the next item nor the next sibling key, was swept into a replaced range,
    and was deleted at exit 0 under a clean receipt. So the delete stops at the FIRST trailing
    comment line, which keeps that comment and everything after it — including any blank lines
    the comment itself is separated by.

    INSIDE A `|` BODY A `#` LINE IS CONTENT — a shell or Python comment in a verify script —
    and must go WITH the item, or a fragment of the deleted task's own script is orphaned
    inside `tasks:`. So the scan walks block scalars with `_block_scalar_end` and floors the
    trailing-run search past their last non-blank line, which is the split `_trim_tail`'s
    `comments_are_document` argument makes, reused rather than re-derived.
    """
    floor, index = start + 1, start
    while index < end:
        head = BLOCK_HEAD_RE.match(lines[index])
        if head and len(head.group(1)) > len(indent):
            body_end = _block_scalar_end(lines, index, end)
            floor = max(floor, _last_nonblank(lines, index, body_end))
            index = body_end
            continue
        index += 1
    trailing = _before_trailing_comments(lines[:end], floor)
    comment = next((i for i in range(trailing, end)
                    if lines[i].lstrip().startswith("#")), None)
    return end if comment is None else comment


def _item_delete_ranges(lines, key_range, items, key):
    """[(start, end)] per parsed item of `key`, in text order, or a refusal.

    THE ALIGNMENT IS `apply_merge`'S OWN, AND SO IS ITS REFUSAL: one dash per item is what lets
    a text range and a parsed item be zipped, and a delete that mis-aligned them would remove
    the wrong item's bytes while reporting the id it was asked for.
    """
    item_ranges = _index_list_items(lines, key_range)
    if len(item_ranges) != len(items):
        raise harness_merge.MergeRefusal(
            5, [f"UNPARSEABLE: could not align text ranges with parsed items for '{key}' — "
                "the block's formatting is not one dash per item."])
    return [
        (start, _item_delete_end(lines, start, end, DASH_RE.match(lines[start]).group(1)))
        for start, end in item_ranges
    ]


def _locate_one(present, key, iid):
    """The index of `iid` in `present`, or the refusal that names the concrete miss.

    AN ABSENT ID IS NEVER A NO-OP (exit 3): a delete that reported success for an id it could
    not find would tell a caller who mistyped one that their scope removal had happened. The id
    list is SCOPED TO `key`, the precedent `_task_status_line` set — offering decision ids for a
    `--task` miss invites a retry that fails for an unrelated reason.

    A DUPLICATE ID IN THE PLAN IS ALSO A REFUSAL (exit 5), `_sole_item`'s rule verbatim: which
    of two items carrying one id was meant cannot be known, and binding to the first match
    silently is what the code-reviewer found in `amend`'s cycle 0.
    """
    hits = [index for index, pid in enumerate(present) if pid == iid]
    if not hits:
        raise harness_merge.MergeRefusal(
            3, [f"plan-merge: {iid} is not under {key}: in this plan, so there is nothing to "
                "delete — REFUSING, rather than reporting a deletion that did not happen.",
                f"  {key}: carries: {', '.join(str(p) for p in present) or '(none)'}"])
    if len(hits) != 1:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {iid} appears {len(hits)} time(s) under {key}:; exactly one is "
                "required. A duplicate id cannot be deleted unambiguously."])
    return hits[0]


def _deletion_ranges(lines, base_doc, requested):
    """The text ranges every requested id occupies, or the refusal that names the miss."""
    _l, _order, key_ranges, _pre = _index_top_keys("".join(lines))
    ranges = []
    for key in DELETABLE_KEYS:
        wanted = [iid for k, iid in requested if k == key]
        if not wanted:
            continue
        items = base_doc.get(key) if isinstance(base_doc.get(key), list) else []
        present = [_item_id(item) for item in items]
        item_ranges = (_item_delete_ranges(lines, key_ranges[key], items, key)
                       if key in key_ranges else [])
        ranges.extend(item_ranges[_locate_one(present, key, iid)] for iid in wanted)
    return ranges


def _task_edges(task, doomed):
    """`<tid> depends_on <entry>` for every doomed id this ONE task names, or [] for none.

    A DOOMED TASK CONTRIBUTES NOTHING. A task being deleted in the same call may name another
    being deleted in the same call — that is a scope removal, not a dangling edge, and counting
    it would make the verb unable to remove a dependent pair, which is the ordinary case.

    A `depends_on` THAT IS NOT A LIST IS NOT READ AS ONE, for `harness_yaml._depends_on_entries`'
    own measured reason: iterated as-is, a bare string walks CHARACTERS and reports phantom ids.
    Nothing can be proven dangling from a malformed field, so this reports none and leaves the
    shape complaint to the schema, which already owns it.
    """
    if not isinstance(task, dict) or _item_id(task) in doomed:
        return []
    entries = task.get("depends_on")
    if not isinstance(entries, list):
        return []
    tid = _item_id(task)
    return [f"{tid} depends_on {entry}" for entry in entries if str(entry) in doomed]


def _dangling_edges(base_doc, doomed):
    """Every edge the deletion would leave pointing at a task that is no longer there."""
    return [edge
            for task in (base_doc.get("tasks") or [])
            for edge in _task_edges(task, doomed)]


def _refuse_dangling_depends_on(base_doc, requested):
    """Refuse a deletion that would leave a SURVIVING task's `depends_on` naming a deleted one.

    ISSUE #201's OWN DEFECT, FROM THE OTHER SIDE. `harness_yaml._validate_plan_depends_on`
    refuses a plan whose edge names an absent task, so the do-no-harm schema check below would
    also catch this — but ONLY when the base was already schema-legal, and do-no-harm
    deliberately skips it for a plan mid-authoring, which is most plans a scope removal is run
    against. The schema is therefore not a substitute for this check: it is a second net with a
    hole exactly where a delete is most likely to be used. This check also names the EDGE,
    which the schema's own complaint cannot do, because it fires on the finished document
    rather than on the request.
    """
    doomed = {iid for key, iid in requested if key == "tasks"}
    dangling = _dangling_edges(base_doc, doomed) if doomed else []
    if not dangling:
        return
    raise harness_merge.MergeRefusal(
        4, ["REFUSED: this deletion would leave a dangling depends_on edge — REFUSING to "
            "write it.",
            f"  {', '.join(dangling)}",
            "  amend the surviving task's depends_on first, or delete that task in the "
            "same call. A plan whose edge names an absent task is issue #201's defect, and "
            "a delete verb that creates one is worse than no delete verb."])


def _splice_out(lines, ranges):
    """`lines` with every range removed, as bytes.

    IT FILTERS LINES AND RENDERS NONE, which is what makes every survivor byte-identical: a
    round trip through a YAML dumper would reformat the whole plan and destroy the review diff
    this tool exists to keep readable (D-03). Overlapping ranges cannot arise from distinct
    items, and a set makes one harmless rather than a double-deletion if one ever did.
    """
    dropped = set()
    for start, end in ranges:
        dropped.update(range(start, end))
    return "".join(line for index, line in enumerate(lines)
                   if index not in dropped).encode("utf-8")


def _survivors(base_doc, key, requested):
    doomed = {iid for k, iid in requested if k == key}
    return [item for item in (base_doc.get(key) or []) if _item_id(item) not in doomed]


def _verify_deletion(spliced_bytes, base_doc, requested):
    """Refuse rather than write a deletion that does not reload as the one that was asked for.

    IT COMPARES WHOLE PARSED ITEMS, NOT IDS, for the reason `_verify_amend` states: a boundary
    error leaves a document that parses perfectly. A range one line long takes the next item's
    `- id:` line and MERGES two items into one; a range one line short leaves an orphaned field
    on the neighbour. An id-only check sees neither — the first because the merged item still
    carries the survivor's id, the second because no id moved at all.

    BOTH LISTS ARE CHECKED even when only one was touched, because a mis-computed range in
    `tasks:` can only be proven not to have reached `decisions:` by looking.
    """
    reloaded = _reload_or_refuse(spliced_bytes)
    if not isinstance(reloaded, dict):
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the pruned plan is not a mapping — REFUSING to write it."])
    for key in DELETABLE_KEYS:
        want = _survivors(base_doc, key, requested)
        got = reloaded.get(key) or []
        if got == want:
            continue
        want_ids = [_item_id(item) for item in want]
        got_ids = [_item_id(item) for item in got]
        detail = (f"  expected ids: {want_ids!r}\n  reloaded ids: {got_ids!r}"
                  if want_ids != got_ids else
                  "  the ids match, so a SURVIVOR's own fields changed: that is a boundary "
                  "error, which a check on ids alone cannot see.")
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: '{key}' does not reload as the deletion that was computed — "
                "REFUSING to write it.", detail])
    return reloaded


def _deleted_bytes(base_bytes, requested):
    """The plan's bytes with every requested item's lines removed, or a refusal.

    THE WHOLE EDIT AS A FUNCTION OF BYTES, `_signed_approval_bytes`'s shape: the verb's lock
    plumbing stays three lines and this stays reachable from a unit test, which is the remedy
    `_require_locked_hash` and `_verify_amend` both got for the same reason.
    """
    raw = base_bytes.decode("utf-8")
    try:
        base_doc = harness_yaml.load_str(raw, "<base plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the plan on disk does not parse, so delete-items cannot tell "
                "which bytes belong to the items it was asked to remove.",
                f"  {exc}"])
    base_doc = base_doc if isinstance(base_doc, dict) else {}
    lines = raw.splitlines(keepends=True)
    ranges = _deletion_ranges(lines, base_doc, requested)
    _refuse_dangling_depends_on(base_doc, requested)
    spliced = _splice_out(lines, ranges)
    reloaded = _verify_deletion(spliced, base_doc, requested)
    # DO NO HARM, the rule `apply` and `amend` both hold to: the result is held to the plan
    # schema only when the BASE satisfied it. A plan mid-authoring legitimately does not, and
    # refusing to prune it would make this verb useless exactly where scope is still moving.
    if _schema_error(base_doc) is None:
        err = _schema_error(reloaded)
        if err is not None:
            raise harness_merge.MergeRefusal(
                5, ["ILLEGAL PLAN: this deletion would make a legal plan illegal — REFUSING "
                    "to write it.",
                    f"  {err}",
                    "  the base satisfied the plan schema and the pruned result does not, so "
                    "the deletion itself is what the schema refuses."])
    return spliced


def cmd_delete_items(args):
    """Delete whole tasks and decisions by id, under the same lock every other verb takes."""
    resolved = _resolve_plan(args.file)
    try:
        requested = _requested_deletions(args)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)

    def transform(base_bytes):
        if base_bytes is None:
            raise harness_merge.MergeRefusal(
                3, [f"plan-merge: {resolved} does not exist, so there is nothing to delete."])
        return _deleted_bytes(base_bytes, requested)

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    for key, iid in requested:
        print(f"DELETED {key}:{iid}")
    # THE REASON IS PRINTED, NEVER WRITTEN. The plan carries no record of it by design — the
    # operator's ruling lives in the feature's own notes — so the receipt is where it has to
    # appear for a run log to say why ten items went.
    print(f"DELETED-ITEMS {len(requested)} from {resolved} — reason: {args.reason}")
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
# `delete-items` is what that distinction was always for: it deletes, by id and with a reason,
# through the same lock and the same splice, and it registers itself below rather than here
# because its id flags repeat.
VERBS = (
    ("apply", "merge a proposal into a plan.yaml — adds, never deletes",
     (_FILE, _PROPOSAL), cmd_apply),
    ("add-tasks", "alias of apply, for callers that only add tasks — identical code path",
     (_FILE, _PROPOSAL), cmd_apply),
    ("set-task-station", "set ONE task's status, by splicing its one line",
     (_FILE, ("--task", "the task id, T-NN"), _STATION), cmd_set_task_station),
    ("set-feature-station", "set or insert the top-level status key",
     (_FILE, _STATION), cmd_set_feature_station),
    ("set-panel", "replace the top-level panel mapping with a validated value",
     (_FILE, ("--value-file", "YAML file holding the replacement panel mapping")), cmd_set_panel),
)


def _register_sign_approval(sub):
    p = sub.add_parser("sign-approval", help="the ONLY route that writes the approval mapping")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--by", required=True, help="the signer's name")
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument(
        "--overrule", action="append", default=[], metavar="FINDING-ID:REASON",
        help="accept a current panel finding's risk; repeat for multiple findings",
    )
    p.set_defaults(func=cmd_sign_approval)


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
    p.add_argument("--yaml-value", action="store_true",
                   help="read/write the value-file as a YAML list or mapping")
    p.set_defaults(func=cmd_amend)


def _register_delete_items(sub):
    """ITS OWN REGISTRATION, BY THE VERBS TABLE'S OWN INSTRUCTION.

    `--task` and `--decision` REPEAT, and neither is required on its own — one of the two is,
    which is a rule no `required=True` column can express. The table says so itself: a verb
    that needs an optional argument gets its own registration rather than a `required` column
    that makes the rows only look uniform. The one-of-two rule is enforced in
    `_requested_deletions`, before the lock, where it can say what was missing.
    """
    p = sub.add_parser("delete-items",
                       help="delete WHOLE tasks and/or decisions by id, with a stated reason")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--task", action="append", default=[], metavar="T-NN",
                   help="a task id to delete; repeat the flag for more")
    p.add_argument("--decision", action="append", default=[], metavar="D-NN",
                   help="a decision id to delete; repeat the flag for more")
    p.add_argument("--reason", required=True,
                   help="why these items are going; printed on the receipt, never written "
                        "into the plan")
    p.set_defaults(func=cmd_delete_items)


def main():
    parser = argparse.ArgumentParser(prog="plan-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, helptext, arguments, func in VERBS:
        p = sub.add_parser(name, help=helptext)
        for flag, arghelp in arguments:
            p.add_argument(flag, required=True, help=arghelp)
        p.set_defaults(func=func)
    _register_sign_approval(sub)
    _register_amend(sub)
    _register_delete_items(sub)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
