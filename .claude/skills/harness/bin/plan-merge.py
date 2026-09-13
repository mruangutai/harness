#!/usr/bin/env python3
"""plan-merge.py — the second plan writer: it adds tasks, replaces the fields a proposal names
on a task that already exists, and deletes one only when it is named and a reason is given
(FEAT-32 T-03, D-01..D-04, DEC-182, DEC-120; FEAT-59 SC-05/SC-07/SC-08).

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
    plan-merge.py record-panel      --file <plan.yaml> --digest <lead digest.md> --cycle N [--last-run <run-dir>]
    plan-merge.py set-lanes         --file <plan.yaml> --value-file <lanes.yaml>
    plan-merge.py check             --file <plan.yaml> --root <checkout root>
    plan-merge.py sign-approval     --file <plan.yaml> --by <name> --date <YYYY-MM-DD> [--overrule PF-ID:<reason>]... [--rework rounds=N,minutes=M --decision <path>]
    plan-merge.py delete-items      --file <plan.yaml> --task T-NN [--task T-NN]... [--decision D-NN]... --reason "<text>"

FEAT-59 (measured on FEAT-54's 23 pre-build runs, BRIEF ## Problem) retired four write
mechanics of this tool's own: `apply` refused any changed field on an existing id (exit 7), so
every plan revision cost one `amend --show`/`--expect-sha256` round trip per field — now the
proposal's fields REPLACE the base's, field by field, logged per field (except a task's
`status`: the station is `set-task-station`'s, and a proposal's value for an existing task is
IGNORED and said so, never laid over the base's); `lanes:` had no write route — `set-lanes`;
`set-panel` re-rendered every finding through the dumper so a diff could
not tell a carried finding from a changed one — both panel verbs now keep the bytes of any
finding whose id and content are unchanged; and pm spent whole runs transcribing a lead digest
into `panel:` — `record-panel` reads the digest itself. `check` resolves every `files:` anchor,
every `execution_agent` route and every `traces:` id before a plan is signed (SC-07), and a
line-number anchor `path:NN` is refused at write (plan_anchors.py). Any verb that changes the
task set or a task field on an APPROVED plan resets approval to `pending` with `reset_at` and
`reset_reason: <verb> <ids>` — `sign-approval` stays the only writer of `approved`.

CONTROLLED VERBS, ONE WRITE ROUTE (FEAT-41 T-03). Every mutating verb goes through
harness_merge.locked_update and a text splice, and require_destination (exit 9) guards every
path. NEVER-DELETE IS A PROPERTY OF `apply` AND ITS ALIAS, NOT OF THE TOOL: the lock and the
splice are what fix #628 and they hold for every mutating verb, while never deleting a task is a
promise those two verbs alone make — and `delete-items` is the verb that promise left missing.
With `apply` unable to remove, `amend` able to replace ONE field of ONE existing item, and
FEAT-41 T-09's shape gate (#1045) denying every editor and shell write of a plan.yaml to every
author, an operator-ruled scope REMOVAL had no route at all: that is a missing verb, not a
missing permission. So `delete-items` removes WHOLE items from `tasks:` and `decisions:`, by id,
with a reason — never by predicate, never one field, never `approval:`, and never silently. An id
that is not in the plan, an id given twice, a SURVIVING task's `depends_on` still naming a task
that would go (issue #201's own defect), a result that fails the plan schema or does not reload
as the deletion that was computed: each is a loud non-zero refusal naming the concrete value, and
each leaves the file byte-identical. The reason is NEVER written into the plan — it exists so
the refusals can name why one was asked for, and so a caller cannot delete by reflex.

`set-task-station` and `set-feature-station` validate the station against the vocabulary
factory_config declares — MANDATED_STATIONS plus TERMINAL_MARKER, imported, never respelled —
resolved through the harness.json of the checkout the target plan.yaml belongs to. The check runs
BEFORE the lock is taken, so a refused value never opens the file.

`approval:` has three controlled write paths: `apply` seeds a brand-new plan with the
unsigned `status: pending` mapping, `sign-approval` is the only path that can transition it
to approved or append an attributed risk acceptance to `approval.rulings`, and the task-changing
verbs (`apply`, `add-tasks`, `amend --key tasks`, `delete-items --task`) RESET an approved plan
to pending — never the other way. Every other verb operating on an existing plan leaves its
approval bytes byte for byte. The main session — nobody else — signs approval through this tool
rather than by hand. A proposal that carries an approval mapping which PARSES differently from
the base's is a REFUSAL (exit 8), not a silent drop: `apply` must be INCAPABLE of writing a
signature (step 7) and must also NOTICE a caller that tried to sneak one past it (step 7b) —
two different jobs, so two different guards.

The creation exception is deliberately narrower than signing: a proposal cannot choose the pending
mapping's contents, and the tool emits only its fixed status. Without this bootstrap, a newly
created plan cannot later be signed because `sign-approval` correctly refuses to invent a missing
mapping.

Exit codes are the interface:
    0  applied — stdout lists ADDED/PRESERVED ids and REPLACED fields, an IGNORED line per
       proposal `status` on an existing task, an APPROVAL-RESET line when a signed plan was
       voided (verified on reload, never merely reported), an IGNORED-APPROVAL line if the
       proposal carried an approval block, and a final APPLIED line. For `check`: every anchor,
       route and trace resolved
    1  `check` only: at least one anchor, route or trace did not resolve — one FAIL line each
    2  a command line is unusable: `delete-items` with no --task and no --decision, the same id
       twice, or an empty --reason; `sign-approval --rework` without --decision, malformed, or
       with no sibling feature.json; `check --root` without a manifest; or a `files:` entry in
       the line-number form `path:NN`, named (argparse's code, and `amend`'s missing-hash precedent)
    3  an id named by --task or --decision is absent from the plan, or the plan file itself is
       (the message names the ids present, scoped to the list the id was asked for)
    4  the value given to --station is not a legal station (the message lists the legal ones),
       or a requested deletion is not legal: a SURVIVING task's `depends_on` names a task being
       deleted, named pair by pair
    5  a side (base, proposal, panel value, lanes value, lead digest) failed to parse or failed
       its shape check, or a splice does not reload as the edit that was computed — for a
       deletion, that includes a survivor whose own fields moved
    6  the lock could not be acquired within the retry budget (harness_merge)
    7  the same top-level key carries two different loaded values (items no longer conflict:
       a proposal's fields replace the base's)
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
import json
import os
import re
import sys
from datetime import datetime, timezone

import yaml

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN_DIR)
import factory_config  # noqa: E402  (local import, after sys.path fix-up)
import feature_json_write  # noqa: E402
import gh_board  # noqa: E402
import harness_boundary  # noqa: E402
import harness_yaml  # noqa: E402
import harness_merge  # noqa: E402
import panel_findings  # noqa: E402
import plan_anchors  # noqa: E402

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



def _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids, replaced=()):
    """Refuse rather than return a splice that does not reload as the merge it reported.

    `replaced` is [(key, iid, base_item, changes)] for every existing item the proposal
    changed, `changes` being the (iid, field, old, new) rows the receipt will print. Each item
    must reload as the BASE item with exactly those fields at their new values — the fields the
    proposal omitted intact, a proposal `status` NOT laid over (review F7) — because a field
    splice one line long or one line short still parses (the `_verify_amend` lesson)."""
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
    _verify_replaced(reloaded, replaced)
    return reloaded


def _verify_replaced(reloaded, replaced):
    """Each replaced item must reload as the BASE item with the REPORTED changes laid over it."""
    for key, iid, base_item, changes in replaced:
        want_item = dict(base_item)
        want_item.update({field: new for _iid, field, _old, new in changes})
        got_item = _sole_item(reloaded, key, iid)
        if got_item != want_item:
            raise harness_merge.MergeRefusal(
                5,
                [f"UNPARSEABLE: id={iid!r} in '{key}' does not reload as the base item with the "
                 "proposal's fields replaced — REFUSING to write it.",
                 f"  expected: {want_item!r}",
                 f"  reloaded: {got_item!r}"],
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


def _anchor_faults(doc):
    """`  <task id> files: <message>` for every `files:` entry plan_anchors refuses, in order."""
    tasks = (doc.get("tasks") or []) if isinstance(doc, dict) else []
    return [f"  {task.get('id') or '<no id>'} files: {message}"
            for task in tasks if isinstance(task, dict)
            for message in plan_anchors.refusals(task.get("files"))]


def _refuse_illegal_anchors(doc, where):
    """MergeRefusal(2) naming every `files:` entry in `doc`'s tasks that plan_anchors refuses.

    C4: a line-number anchor `path:NN` is refused at WRITE, so it cannot enter a signed plan;
    `check` then only has to resolve the forms that can survive `main` moving. Every offending
    entry is named, with its task, in one refusal — a caller fixing them one at a time is the
    round trip this feature exists to remove."""
    faults = _anchor_faults(doc)
    if faults:
        raise harness_merge.MergeRefusal(
            2, [f"REFUSED: {where} carries a files: entry this tool will not write."] + faults
               + ["  legal forms: path, path#symbol, {path: <p>, quote: <q>} (plan_anchors.py)."])


def _field_indent(lines, dash_indent):
    """The indent an item's own fields sit at: the first sibling key after the dash line, or
    the dash indent plus two when the item carries nothing beyond its dash line."""
    for line in lines[1:]:
        m = SIBLING_KEY_RE.match(line)
        if m and len(m.group(1)) > len(dash_indent):
            return m.group(1)
    return dash_indent + "  "


def _proposal_field_lines(prop_lines, ps, pe, prop_dash, field, value, indent, iid, key):
    """The proposal's OWN lines for `field`, re-indented to the base item — or, when the field
    sits on the proposal's dash line and cannot be located as a block, the value rendered.

    Copying the author's bytes keeps a `verify: |` block a block and a hand-written list a
    list; rendering is the fallback, never the default, for the reason `_render_field` gives."""
    located = _field_block(prop_lines, ps, pe, prop_dash, field)
    if located is not None:
        first, last, prop_indent = located
        return _reindent(prop_lines[first:last], len(indent) - len(prop_indent), iid, key)
    if isinstance(value, (list, dict)):
        return _structured_field_lines(indent, field, value)
    return [_field_lines(indent, field, value)]


def _splice_field(lines, dash_indent, field, rendered):
    """`lines` (one item) with `field` replaced by `rendered`, or `rendered` added after the
    item's last own line — before any trailing blank or comment — when the item lacks it."""
    located = _field_block(lines, 0, len(lines), dash_indent, field)
    if located is None:
        own_end = _item_delete_end(lines, 0, len(lines), dash_indent)
        at = _last_nonblank(lines, 0, own_end)
        return lines[:at] + rendered + lines[at:]
    first, last, _indent = located
    return lines[:first] + rendered + lines[last:]


# A PROPOSAL'S `status` ON AN EXISTING ITEM IS IGNORED, NEVER LAID OVER THE BASE'S (review F7).
# The station is set-task-station's and gh-sync's during build; a pm proposal re-applied after
# build entry (to add T-05, say) still carries the `pending` it was drafted with, and laying
# that over `building` rolled the station back — and, counted as a task change, voided the
# signature mid-build. `id` is the item's identity and is never a field to replace.
STATION_FIELD = "status"


def _replace_fields(base_lines, s, e, item, prop_lines, ps, pe, pitem, iid, key):
    """The base item's lines with every field the proposal names replaced or added, plus
    [(iid, field, old, new)] per change and the same tuple per IGNORED `status`. Fields the
    proposal omits are untouched bytes.

    THIS IS WHAT RETIRES apply's EXIT 7 (FEAT-59 SC-08). A changed value is a splice of that
    field's lines only — the same one-block replace `amend` does, without the hash handshake,
    because `apply` is the plan author's own verb and the lock already serialises writers."""
    lines = list(base_lines[s:e])
    dash_indent = DASH_RE.match(lines[0]).group(1)
    prop_dash = DASH_RE.match(prop_lines[ps]).group(1)
    indent = _field_indent(lines, dash_indent)
    differing = [(field, value) for field, value in pitem.items()
                 if field != "id" and (field not in item or item[field] != value)]
    changed = [(field, value) for field, value in differing if field != STATION_FIELD]
    ignored = [(field, value) for field, value in differing if field == STATION_FIELD]
    for field, value in changed:
        rendered = _proposal_field_lines(prop_lines, ps, pe, prop_dash, field, value, indent,
                                         iid, key)
        lines = _splice_field(lines, dash_indent, field, rendered)

    def rows(pairs):
        return [(iid, field, item.get(field, _ABSENT), value) for field, value in pairs]

    return lines, rows(changed), rows(ignored)


# A field the base item does not carry, for the REPLACED receipt. Distinct from None, which is
# a legal YAML value a field can hold.
_ABSENT = object()


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _approval_status(doc):
    approval = doc.get("approval") if isinstance(doc, dict) else None
    return approval.get("status") if isinstance(approval, dict) else None


RESET_FIELDS = ("reset_at", "reset_reason")
_RESET_LINE_RE = re.compile(r"^  (reset_at|reset_reason):")


def _reset_approval_lines(lines, verb, ids):
    """`lines` with approval.status rewritten to pending and reset_at/reset_reason recorded.

    C4 / SC-08: a signature is a statement about ONE task set. Any verb that changes that set
    or a task's field on an approved plan voids it — downward only; `sign-approval` is the only
    writer of `approved`. The signer and date are kept so the operator can see what was voided
    and by which verb; a prior reset record is replaced, not stacked. The caller has already
    established that the parsed approval.status is `approved`, so the status key is found BY
    NAME at the mapping's own indent, never by a regex on its value: `status: "approved"` and a
    four-space body parsed as approved just the same (review F3). A shape with no status line
    to rewrite is returned unchanged, and `_verify_reset` refuses it."""
    start, end = _approval_span(lines)
    if start is None:
        return lines
    body = lines[start + 1:end]
    keyed, indent = _sub_key_lines(body, 0, len(body))
    status_at = next((i for key, i in keyed if key == "status"), None)
    if status_at is None:
        return lines
    stale = {i for key, i in keyed if key in RESET_FIELDS}
    reason = f"{verb} {', '.join(str(i) for i in ids)}"
    record = [_field_lines(indent, "status", "pending"),
              _field_lines(indent, "reset_at", _now_iso()),
              _field_lines(indent, "reset_reason", reason)]
    out = []
    for index, line in enumerate(body):
        if index == status_at:
            out.extend(record)
        elif index not in stale:
            out.append(line)
    return lines[:start + 1] + out + lines[end:]


def _verify_reset(text, verb):
    """Refuse rather than write a task change under a signature the splice could not void.

    `_verify_signature`'s rule from the other direction, same exit 5: the RELOADED value is
    what check-state.sh and the operator read, so it — not the splice's own report — decides
    whether APPROVAL-RESET is true. Proven before this check (review F3): a flow-style approval
    printed the receipt, exited 0 and reloaded as approved."""
    got = _approval_status(_reload_or_refuse(text.encode("utf-8")))
    if got != "pending":
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: {verb} changes a task on an approved plan, but approval.status would "
                "not reload as pending — REFUSING to write it.",
                f"  reloads as: {got!r}",
                "  the splice could not void the signature (approval is not a block mapping "
                "with its own status line), so the change is refused rather than written "
                "under a standing signature (SC-08)."])


def _maybe_reset_approval(text, base_doc, verb, task_ids):
    """(text, reset) — the text with approval reset when the base was approved and `task_ids`
    names at least one changed task; `reset` says whether it happened, for the receipt. A
    claimed reset is verified on reload or refused: the receipt is never ahead of the file."""
    if not task_ids or _approval_status(base_doc) != "approved":
        return text, False
    lines = text.splitlines(keepends=True)
    reset_text = "".join(_reset_approval_lines(lines, verb, task_ids))
    _verify_reset(reset_text, verb)
    return reset_text, True


class MergeResult:
    """What `apply_merge` computed, for the receipt `cmd_apply` prints.

    added / preserved: item ids. replaced: (iid, field, old, new) per replaced field, `old`
    being _ABSENT for a field the base item did not carry. ignored: the same tuple per
    proposal `status` that was NOT written (review F7). reset: approval was voided."""

    def __init__(self, out_bytes, added, preserved, ignored_approval, replaced=(), reset=False,
                 ignored=()):
        self.out_bytes = out_bytes
        self.added = added
        self.preserved = preserved
        self.ignored_approval = ignored_approval
        self.replaced = list(replaced)
        self.reset = reset
        self.ignored = list(ignored)


def apply_merge(base_bytes, proposal_text, verb="apply"):
    """The whole algorithm. Returns a MergeResult. Raises harness_merge.MergeRefusal(2|5|7|8)
    with nothing to write, per plan-merge.py's contract with harness_merge.locked_update: a
    raised MergeRefusal leaves the file untouched. `verb` is the command-line name, recorded
    in approval.reset_reason when this merge voids a signature."""
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
        _refuse_illegal_anchors(prop_doc, "the proposal")
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
                return MergeResult("".join(lines).encode("utf-8"), [], [], False)
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
    _refuse_illegal_anchors(prop_doc, "the proposal")

    if not UNION_MERGE:
        # Step 5, off: today's last-writer-wins, verbatim.
        return MergeResult(proposal_text.encode("utf-8"), [], [], False)

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
    added_ids, preserved_ids, replaced, changed_tasks, ignored = [], [], [], [], []

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
                if iid not in prop_by_id:
                    out_chunks.append("".join(base_lines[s:e]))
                    continue
                ps, pe, pitem = prop_by_id[iid]
                if pitem == item:
                    out_chunks.append("".join(base_lines[s:e]))
                    preserved_ids.append(iid)
                    continue
                # THE PROPOSAL'S FIELDS REPLACE THE BASE'S, FIELD BY FIELD (FEAT-59 SC-08).
                # This was exit 7 CONFLICT, and it cost FEAT-54 an amend round trip per field.
                # A `status` that differs is IGNORED, not a change: an item whose only
                # difference is its station is neither replaced nor a reason to void approval.
                item_lines, changes, ignored_here = _replace_fields(
                    base_lines, s, e, item, prop_lines, ps, pe, pitem, iid, key)
                out_chunks.append("".join(item_lines))
                ignored.extend(ignored_here)
                if not changes:
                    continue
                replaced.append((key, iid, item, changes))
                if key == "tasks":
                    changed_tasks.append(iid)
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
                    if key == "tasks":
                        changed_tasks.append(iid)
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

    spliced_text, reset = _maybe_reset_approval("".join(out_chunks), base_doc, verb, changed_tasks)
    spliced_bytes = spliced_text.encode("utf-8")
    changes = [change for _key, _iid, _item, item_changes in replaced for change in item_changes]

    if PRESERVE_BASE_BYTES:
        # STEP 9: THE RESULT IS PARSED BEFORE IT IS WRITTEN, and this guard is general.
        # Steps 5-8 parse the BASE and the PROPOSAL; nothing parsed the OUTPUT, so a splice
        # defect could — and on 2026-08-31 did — write a signed plan that PyYAML cannot load
        # while printing ADDED and exiting 0. A tool whose whole promise is "the base's bytes
        # survive" must not be able to hand back bytes that are not a plan.
        #
        # It also checks the MERGE, not merely the syntax: every id the caller is about to be
        # told was added or preserved must actually be present in the reloaded document, and
        # every replaced item must reload as base-with-the-reported-changes. A splice that
        # lands text in the wrong block can still parse.
        _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids, replaced)
        return MergeResult(spliced_bytes, added_ids, preserved_ids, ignored_approval,
                           changes, reset, ignored)

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
    return MergeResult(dumped, added_ids, preserved_ids, ignored_approval, changes, reset, ignored)


def cmd_apply(args):
    resolved = _resolve_plan(args.file)

    if args.proposal == "-":
        proposal_text = sys.stdin.read()
    else:
        with open(args.proposal, encoding="utf-8") as f:
            proposal_text = f.read()

    result = {}

    def transform(base_bytes):
        merged = apply_merge(base_bytes, proposal_text, args.cmd)
        result["merged"] = merged
        return merged.out_bytes

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    _print_apply_receipt(result["merged"])
    print(f"APPLIED {resolved}")
    sys.exit(0)


APPROVAL_RESET_LINE = ("APPROVAL-RESET: the plan was approved and its task set or a task field "
                       "changed; approval.status is pending until the main session signs again")


def _print_apply_receipt(merged):
    for eid in merged.added:
        print(f"ADDED {eid}")
    for eid in merged.preserved:
        print(f"PRESERVED {eid}")
    for iid, field, old, new in merged.replaced:
        was = "<absent>" if old is _ABSENT else repr(old)
        print(f"REPLACED {iid}.{field}: {was} -> {new!r}")
    for iid, field, old, new in merged.ignored:
        keeps = "none" if old is _ABSENT else repr(old)
        print(f"IGNORED {iid}.{field}: proposal's {new!r} was not written; the station is "
              f"set-task-station's (base keeps {keeps})")
    if merged.reset:
        print(APPROVAL_RESET_LINE)
    if merged.ignored_approval:
        print("IGNORED-APPROVAL: proposal's approval block was not written; base's kept")


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


# ---------------------------------------------------------------------------
# `panel:` and `lanes:` — the top-level mappings pm and the orchestrator write (FEAT-59 SC-05,
# SC-08).
#
# TWO PANEL VERBS, ONE SPLICE. `set-panel` takes a whole mapping from a value file; `record-panel`
# derives one from the validator lead's digest. Both land through `_panel_spliced`, which keeps
# the bytes of every finding whose id AND parsed content are unchanged and renders only what
# changed — the property set-task-station has for a status line, applied to a list item.
# Measured on FEAT-54: `set-panel` re-rendered all nine findings on every call, so a review
# diff of a one-finding change touched forty lines and could not show which finding was new.
#
# FINDING IDENTITY IS panel_findings.finding_id, imported. The validator lead never assigns a
# PF- id (it holds no Bash); pm used to run the helper by hand and transcribe. record-panel
# computes it from the digest's reader and summary, once, in the one place check-state.sh's
# INV-32 and approval.rulings agree on.
FINDING_KINDS = ("substance", "form", "proportionality")
READER_STATUSES = ("ran", "skipped")
LANES = ("team", "main-session-direct")


def _load_mapping_value(path, what):
    try:
        value = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: cannot load {what} value from {path}: {exc}"])
    if not isinstance(value, dict):
        raise harness_merge.MergeRefusal(5, [f"plan-merge: {what} value must be a mapping"])
    return value


def _require_shape(value, required, what):
    """Refuse a mapping missing a required key or carrying the wrong type for one.

    `required` is {key: type}; `cycle` is additionally refused as a bool, which isinstance
    would otherwise accept as an int."""
    missing = [key for key in required if key not in value]
    if missing:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {what} value is missing required key(s): {', '.join(missing)}"])
    wrong = [key for key, expected in required.items() if not _is_typed(value[key], expected)]
    if wrong:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {what} value has invalid type for: {', '.join(wrong)}"])


def _is_typed(value, expected):
    if expected is int and isinstance(value, bool):
        return False
    return isinstance(value, expected)


def _named_mapping(entry, key, where):
    """Refuse unless `entry` is a mapping whose `key` is a non-empty string."""
    if not isinstance(entry, dict) or not str(entry.get(key, "")).strip():
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} must be a mapping carrying {key}:"])


def _validate_reader(reader, where):
    _named_mapping(reader, "reader", where)
    status = reader.get("status")
    if status not in READER_STATUSES:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} status {status!r} is not one of "
                f"{', '.join(READER_STATUSES)}"])
    absent = [k for k in ("persona", "reason") if not str(reader.get(k) or "").strip()]
    if status == "skipped" and absent:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} is skipped without {' and '.join(absent)} — an unrunnable "
                "reader and a clean reader are opposite facts, and the record must say which."])


def _validate_readers(readers, what):
    for index, reader in enumerate(readers):
        _validate_reader(reader, f"{what} readers[{index}]")


def _validate_finding_kind(finding, where):
    kind = finding.get("kind")
    if kind not in FINDING_KINDS:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} kind {kind!r} is not one of {', '.join(FINDING_KINDS)} — "
                "a finding without a kind cannot say whether it re-gates (FEAT-59 SC-06, C2)."])


def _validate_panel(panel, what):
    """The shape both panel verbs hold a mapping to before the lock is taken."""
    _require_shape(panel, {"last_run": str, "cycle": int, "readers": list, "findings": list},
                   what)
    _validate_readers(panel["readers"], what)
    for index, finding in enumerate(panel["findings"]):
        where = f"{what} findings[{index}]"
        _named_mapping(finding, "id", where)
        _validate_finding_kind(finding, where)
    return panel


def _validate_lanes(lanes, what):
    _require_shape(lanes, {"resolved_at": str, "rows": list}, what)
    for index, row in enumerate(lanes["rows"]):
        where = f"{what} rows[{index}]"
        _named_mapping(row, "surface", where)
        if row.get("lane") not in LANES:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {where} lane {row.get('lane')!r} is not one of {', '.join(LANES)}"])
    return lanes


def _sub_key_lines(lines, lo, hi):
    """[(key, line index)] for every key line at the first indented key indent in lines[lo:hi],
    plus that indent (or None when there is no indented key)."""
    matches = [(i, SIBLING_KEY_RE.match(lines[i])) for i in range(lo, hi)]
    keyed = [(i, m) for i, m in matches if m and m.group(1)]
    if not keyed:
        return [], None
    indent = keyed[0][1].group(1)
    return [(m.group(2), i) for i, m in keyed if m.group(1) == indent], indent


def _index_sub_keys(lines, lo, hi):
    """[(key, start, end, indent)] for the direct sub-keys of a mapping whose body is
    lines[lo:hi]: every key line at the FIRST indent found, each running to the next."""
    found, indent = _sub_key_lines(lines, lo, hi)
    ends = [start for _key, start in found[1:]] + [hi]
    return [(key, start, end, indent) for (key, start), end in zip(found, ends)]


def _render_items(items, dash_indent):
    dumped = yaml.safe_dump(items, sort_keys=False, allow_unicode=True, width=10 ** 9)
    return [dash_indent + ln if ln.strip() else ln for ln in dumped.splitlines(keepends=True)]


def _findings_by_id(lines, item_ranges, base_findings, dash_indent):
    """{id: (start, own_end, end, parsed)} for the base's findings, or a refusal on a duplicate
    id. `end` is the full dash-to-dash range `_index_list_items` gives; `own_end` is where the
    finding's own bytes stop and its trailing comment lines begin."""
    by_id = {}
    for (s, e), item in zip(item_ranges, base_findings):
        fid = str(_item_id(item))
        if fid in by_id:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: panel.findings carries {fid} twice; a duplicate id cannot be "
                    "carried unambiguously."])
        by_id[fid] = (s, _item_delete_end(lines, s, e, dash_indent), e, item)
    return by_id


def _finding_lines(finding, base_by_id, lines, dash_indent):
    """One finding's lines, carried THROUGH ITS FULL RANGE (review F10): its own base bytes
    when id and parsed value are unchanged, a render otherwise — and in both cases the comment
    lines that followed it in the base, so a note stays with the finding it followed instead of
    migrating under whichever finding is appended next, or being dropped between two."""
    carried = base_by_id.get(str(_item_id(finding)))
    if carried is None:
        return _render_items([finding], dash_indent)
    s, own_end, e, parsed = carried
    if parsed == finding:
        return lines[s:e]
    return _render_items([finding], dash_indent) + lines[own_end:e]


def _findings_lines(lines, start, end, indent, base_findings, findings):
    """The `findings:` sub-block with every unchanged finding's bytes kept.

    A finding is carried byte for byte when its id is in the base and its parsed value equals
    the base's; anything else is rendered. Falls back to rendering the whole sub-block when the
    base's items cannot be aligned one dash per item, or when either side is the empty list —
    `findings: []` has no dash to splice under."""
    item_ranges = _index_list_items(lines, (start + 1, end))
    if not findings or not base_findings or len(item_ranges) != len(base_findings):
        return _structured_field_lines(indent, "findings", findings)
    dash_indent = DASH_RE.match(lines[item_ranges[0][0]]).group(1)
    base_by_id = _findings_by_id(lines, item_ranges, base_findings, dash_indent)
    out = [lines[start]]
    for finding in findings:
        out.extend(_finding_lines(finding, base_by_id, lines, dash_indent))
    return out


def _panel_sub_block(lines, key, located, indent, base_panel, panel):
    """One sub-key of the rebuilt panel: base bytes when unchanged, an item-wise splice for
    `findings`, a render otherwise. `located` is (start, end, indent) or None when absent."""
    if located is not None and base_panel.get(key) == panel[key]:
        return lines[located[0]:located[1]]
    if key == "findings" and located is not None:
        return _findings_lines(lines, located[0], located[1], indent,
                               base_panel.get(key) or [], panel[key])
    return _structured_field_lines(indent, key, panel[key])


def _panel_block(lines, start, own_end, base_panel, panel):
    """The rebuilt `panel:` block — its own head line, then each sub-key in base order with
    the new keys after, each carried or rendered by `_panel_sub_block`."""
    sub = _index_sub_keys(lines, start + 1, own_end)
    by_key = {key: (s, e, indent) for key, s, e, indent in sub}
    indent = sub[0][3] if sub else "  "
    order = [key for key, _s, _e, _i in sub if key in panel]
    order += [key for key in panel if key not in by_key]
    out = [lines[start]]
    for key in order:
        out.extend(_panel_sub_block(lines, key, by_key.get(key), indent, base_panel, panel))
    return out


def _panel_own_end(lines, start, end):
    """Where the `panel:` block's own bytes stop, inside its top-key range.

    Trailing blank lines and comments at the block's sub-key indent or shallower are the
    document's: they are re-emitted after the rebuilt block, so a wholesale render cannot eat
    them. A DEEPER trailing comment — the template's own `# resolved_by: T-NN` note under the
    last finding — is inside the last sub-key and stays with it (review F10); cutting it off
    here is what re-emitted it under whichever finding was appended next."""
    _keys, indent = _sub_key_lines(lines, start + 1, end)
    width = len(indent or "")
    index = end
    while index > start + 1:
        line = lines[index - 1]
        body = line.lstrip()
        if body and not (body.startswith("#") and len(line) - len(body) <= width):
            break
        index -= 1
    return index


def _panel_spliced(base_text, panel):
    """The plan's text with `panel:` replaced by `panel`, byte-preserving where nothing changed.

    Sub-keys whose parsed value is unchanged keep their bytes; `findings` is spliced item by
    item; everything else is rendered at the block's own indent. An absent `panel:` is inserted
    before `tasks:`, where the template has it."""
    lines, _order, ranges, _preamble = _index_top_keys(base_text)
    if "panel" not in ranges:
        replacement = yaml.safe_dump({"panel": panel}, sort_keys=False).splitlines(keepends=True)
        return _insert_top_mapping(lines, ranges, replacement, ("lanes", "decisions", "tasks"))
    base_panel = _load_base_doc(base_text).get("panel")
    start, end = ranges["panel"]
    own_end = _panel_own_end(lines, start, end)
    block = _panel_block(lines, start, own_end,
                         base_panel if isinstance(base_panel, dict) else {}, panel)
    return "".join(lines[:start] + block + lines[own_end:])


def _load_base_doc(text):
    """The plan on disk as a mapping, or a refusal that names the plan as the side at fault."""
    try:
        doc = harness_yaml.load_str(text, "<base plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the plan on disk does not parse, so nothing can be spliced into "
                f"it — {exc}"])
    return doc if isinstance(doc, dict) else {}


def _insert_top_mapping(lines, ranges, replacement, before):
    """Insert a rendered top-level block before the EARLIEST key of `before` that exists, or at
    the end of the document, so key order follows the template rather than the verb order."""
    starts = [ranges[key][0] for key in before if key in ranges]
    if not starts:
        return "".join(lines + replacement)
    at = min(starts)
    return "".join(lines[:at] + replacement + lines[at:])


def _write_top_mapping(resolved, key, value, splice):
    """Run `splice(base_text) -> new_text` under the lock and refuse unless `key` reloads as
    `value`. The shared tail of set-panel, record-panel and set-lanes."""
    def transform(base_bytes):
        spliced = splice(base_bytes.decode("utf-8")).encode("utf-8")
        reloaded = _reload_or_refuse(spliced)
        if reloaded.get(key) != value:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {key} does not reload as the value supplied"])
        return spliced

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def cmd_set_panel(args):
    resolved = _resolve_plan(args.file)
    try:
        panel = _validate_panel(_load_mapping_value(args.value_file, "panel"), "panel")
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    _write_top_mapping(resolved, "panel", panel, lambda text: _panel_spliced(text, panel))
    print(f"PANEL cycle {panel['cycle']} -> {resolved}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def cmd_set_lanes(args):
    """`lanes:` gets the write route it never had (FEAT-59 SC-08). Same shape as set-panel:
    validate before the lock, replace the whole top-level mapping, refuse unless it reloads."""
    resolved = _resolve_plan(args.file)
    try:
        lanes = _validate_lanes(_load_mapping_value(args.value_file, "lanes"), "lanes")
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    replacement = yaml.safe_dump({"lanes": lanes}, sort_keys=False).splitlines(keepends=True)

    def splice(text):
        lines, _order, ranges, _preamble = _index_top_keys(text)
        if "lanes" in ranges:
            start, end = ranges["lanes"]
            return "".join(lines[:start] + replacement + lines[end:])
        return _insert_top_mapping(lines, ranges, replacement, ("decisions", "tasks"))

    _write_top_mapping(resolved, "lanes", lanes, splice)
    print(f"LANES {len(lanes['rows'])} row(s) resolved at {lanes['resolved_at']} -> {resolved}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


FENCED_BLOCK_RE = re.compile(r"^[ \t]*```[^\n]*\n(.*?)^[ \t]*```", re.M | re.S)


def _fenced_blocks(text):
    """The bodies of every ``` fenced block in `text`, in order; an unclosed fence is dropped."""
    return [m.group(1) for m in FENCED_BLOCK_RE.finditer(text)]


def _digest_mapping(block, path):
    """The DIGEST mapping in one candidate block, or None when it is not a lead return."""
    try:
        doc = harness_yaml.load_str(block, path)
    except harness_yaml.YamlParseError:
        return None
    digest = doc.get("DIGEST") if isinstance(doc, dict) else None
    return digest if isinstance(digest, dict) else None


def _lead_digest(path):
    """The DIGEST mapping of a validator-lead return on disk, or a refusal.

    The return contract (harness-handoff, DEC-172) is one fenced yaml block — VERDICT, DIGEST,
    artifact — with prose allowed around it. The LAST fenced block carrying a DIGEST mapping
    wins, the rule validate-digest.py applies to echoed templates; a file with no fence is read
    whole as a last resort so a bare return still records."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise harness_merge.MergeRefusal(5, [f"plan-merge: cannot read digest {path}: {exc}"])
    for block in reversed(_fenced_blocks(text) or [text]):
        digest = _digest_mapping(block, path)
        if digest is not None:
            return digest
    raise harness_merge.MergeRefusal(
        5, [f"plan-merge: {path} carries no fenced yaml block with a DIGEST: mapping — the "
            "validator lead's return is what record-panel transcribes, and nothing else."])


def _digest_finding(finding, where):
    """One panel finding from one digest entry: content-hash id, closed key set, ALWAYS open.

    Every entry needs kind (C2), severity, reader and summary: identity is reader + summary,
    and a finding without a severity or a kind cannot gate. `why` and any other free key the
    lead wrote are NOT carried — panel.findings is the closed shape the template declares.
    The digest's `disposition` is not carried either (review F8 / SEC-04): a new finding
    arrives open whatever the lead wrote, because resolution is set-panel's and the operator's
    ruling's to record, and a finding landing pre-resolved would sign a plan past INV-32 with
    no ruling at all. A digest entry for a finding already in the base is matched by id only;
    the base's value, disposition included, wins."""
    if not isinstance(finding, dict):
        raise harness_merge.MergeRefusal(5, [f"plan-merge: {where} is not a mapping"])
    absent = [k for k in ("severity", "reader", "summary") if not str(finding.get(k) or "").strip()]
    if absent:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} is missing {', '.join(absent)} — reader and summary are "
                "the finding's identity, severity is what gates."])
    _validate_finding_kind(finding, where)
    reader, summary = str(finding["reader"]), str(finding["summary"])
    return {"id": panel_findings.finding_id(reader, summary), "severity": str(finding["severity"]),
            "reader": reader, "kind": finding["kind"], "summary": summary,
            "disposition": "open"}


def _digest_findings(digest, what):
    return [_digest_finding(finding, f"{what} findings[{index}]")
            for index, finding in enumerate(digest.get("findings") or [])]


def _digest_readers(digest, what):
    readers = digest.get("readers")
    if not isinstance(readers, list):
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {what} carries no readers: list — every reader must appear, ran "
                "or skipped, or a reader that never ran looks clean."])
    _validate_readers(readers, what)
    return readers


def _base_findings(base_text):
    """The base plan's parsed panel.findings mappings, [] when there is no panel yet."""
    base_panel = _load_base_doc(base_text).get("panel") if base_text else None
    findings = base_panel.get("findings") if isinstance(base_panel, dict) else None
    return [f for f in (findings or []) if isinstance(f, dict)]


def _recorded_panel(base_text, digest, cycle, last_run):
    """The panel mapping record-panel writes: the digest's readers, its findings UNIONED with
    the base's — a finding already present keeps its own parsed value (and so, through
    `_panel_spliced`, its own bytes and disposition); a new one is appended open.
    Returns (panel, carried ids, added ids)."""
    what = "lead digest"
    readers = _digest_readers(digest, what)
    findings = _base_findings(base_text)
    present = {str(_item_id(f)) for f in findings}
    incoming = _digest_findings(digest, what)
    carried = [f["id"] for f in incoming if f["id"] in present]
    added = _first_by_id([f for f in incoming if f["id"] not in present])
    findings.extend(added)
    panel = {"last_run": last_run, "cycle": cycle, "readers": readers, "findings": findings}
    return _validate_panel(panel, what), carried, [f["id"] for f in added]


def _first_by_id(findings):
    """`findings` with every repeat of an id dropped — the lead de-duplicates on normalized
    summary plus reader, which is exactly this id, so a repeat is the same finding twice."""
    seen, out = set(), []
    for finding in findings:
        if finding["id"] not in seen:
            seen.add(finding["id"])
            out.append(finding)
    return out


def cmd_record_panel(args):
    """Write `panel:` FROM the validator lead's digest (FEAT-59 SC-05).

    Before this verb, pm read the lead digest, ran panel_findings.py once per finding, built a
    value file in /tmp and called set-panel — a whole run whose only work was to copy one file
    into another (FEAT-54 c0 and c3, BUG-285 three of nineteen runs). The digest is parsed
    BEFORE the lock, so a malformed one refuses without opening the plan; the base's own
    findings are carried under the lock, so a concurrent set-panel cannot be lost."""
    resolved = _resolve_plan(args.file)
    last_run = args.last_run or os.path.basename(os.path.dirname(os.path.abspath(args.digest)))
    try:
        digest = _lead_digest(args.digest)
        # Shape faults in the digest refuse here, on an empty base, before any lock is taken.
        _recorded_panel("", digest, args.cycle, last_run)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    result = {}

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        panel, carried, added = _recorded_panel(text, digest, args.cycle, last_run)
        spliced = _panel_spliced(text, panel).encode("utf-8")
        reloaded = _reload_or_refuse(spliced)
        if reloaded.get("panel") != panel:
            raise harness_merge.MergeRefusal(
                5, ["plan-merge: panel does not reload as the value recorded"])
        result.update(carried=carried, added=added)
        return spliced

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    for fid in result["carried"]:
        print(f"CARRIED {fid}")
    for fid in result["added"]:
        print(f"ADDED {fid}")
    print(f"PANEL cycle {args.cycle} from {args.digest} -> {resolved}")
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
    """The approval body with status/approved_by/date rewritten and any auto-reset record
    dropped: a fresh signature supersedes `reset_at`/`reset_reason` (C4), and leaving them
    would make a signed plan read as voided."""
    written = set()
    output = []
    for line in body:
        if _RESET_LINE_RE.match(line):
            continue
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
    ruling, feature_json = _rework_ruling(args, resolved)
    # THE RULING IS RECORDED BEFORE THE SIGNATURE (review F4). feature_json_write can still
    # refuse past the existence check — invalid JSON, a schema regression, a lock timeout —
    # and a signed plan with no ruling is the half-state SC-15 exists to prevent. The other
    # order fails safe: a ruling without a signature is harmless, and the plan is re-signed.
    if ruling is not None:
        _record_rework(feature_json, ruling)
        print(f"REWORK rounds={ruling['rounds']} minutes={ruling['wall_clock_minutes']} "
              f"decision={ruling['decision']} -> {feature_json}")

    def transform(base_bytes):
        return _signed_approval_bytes(base_bytes, resolved, args)

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        lines = list(refusal.lines)
        if ruling is not None:
            lines.append(f"  the rework ruling was already recorded in {feature_json}; a ruling "
                         "without a signature is harmless — re-run sign-approval to sign.")
        _die(refusal.code, *lines)
    print(f"SIGNED {resolved} by {args.by} on {args.date}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


REWORK_RE = re.compile(r"^rounds=(\d+),minutes=(\d+)$")


def _parse_rework(rework, decision):
    """{rounds, wall_clock_minutes, decision} from the two flags, or an exit-2 refusal."""
    if rework is None or decision is None:
        _die(2, "plan-merge: --rework and --decision go together — the ruling is the bounds AND "
                "the record of who set them (SC-15).")
    m = REWORK_RE.match(rework.strip())
    if not m:
        _die(2, f"plan-merge: --rework {rework!r} is not rounds=N,minutes=M with non-negative "
                "integers.")
    if not decision.strip():
        _die(2, "plan-merge: --decision must name the ruling's record, not be empty.")
    return {"rounds": int(m.group(1)), "wall_clock_minutes": int(m.group(2)),
            "decision": decision.strip()}


def _rework_ruling(args, resolved):
    """(ruling, feature_json_path) from --rework/--decision, or (None, None) when neither was
    given. Both or neither; `rounds=N,minutes=M` with non-negative integers; the sibling
    feature.json must EXIST; and --decision must be an existing FILE under the feature
    directory (review F6 parity — the one rule feature-record.py's raise-cycles/set-rework
    apply, reused rather than restated). All refused here, before anything is written, because
    a signature with no auditable ruling is exactly the half-state SC-15 exists to prevent."""
    rework, decision = getattr(args, "rework", None), getattr(args, "decision", None)
    if rework is None and decision is None:
        return None, None
    ruling = _parse_rework(rework, decision)
    feature_json = os.path.join(os.path.dirname(resolved), "feature.json")
    if not os.path.isfile(feature_json):
        _die(2, f"plan-merge: {feature_json} does not exist, so the rework ruling has nowhere "
                "to go — REFUSING to sign. Create the feature's feature.json first.")
    try:
        _feature_record_module()._require_decision_file(feature_json, ruling["decision"],
                                                       "sign-approval --rework")
    except harness_merge.MergeRefusal as refusal:
        _die(2, *refusal.lines)
    return ruling, feature_json


def _feature_record_module():
    """feature-record.py as a module: the hyphen keeps it out of `import`, like check-plan-routes."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "feature_record", os.path.join(BIN_DIR, "feature-record.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _record_rework(feature_json, ruling):
    """Set `rework` on the sibling feature.json through the one locked, schema-checked writer
    (feature_json_write, C1). A refusal there propagates its own code."""
    def transform(base):
        doc = feature_json_write.parse_doc(base, feature_json)
        if doc is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE,
                [f"REFUSED: {feature_json} vanished between the existence check and the write."])
        doc["rework"] = ruling
        return json.dumps(doc, indent=2) + "\n"

    try:
        feature_json_write.write_feature_json(feature_json, transform)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)


# ---------------------------------------------------------------------------
# BUG-1128 — `amend`, the route that did not exist.
#
# FEAT-41 T-09 denies every Edit/Write to a plan.yaml for every author, and `apply`
# was ADD-ONLY (exit 7 on a changed value — FEAT-59 SC-08 has since made a proposal's
# fields replace the base's; `amend` remains the hash-checked route for a single field
# on a plan another writer may be touching). Correct separately; together they left a
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


def _amended_text(cur, first, last, rendered, want, args, base_doc, result):
    """The plan text with the field spliced in, the C4 guards applied.

    A `files:` replacement is held to plan_anchors' grammar — a line-number anchor is refused
    here as it is in `apply`. A TASK field is part of the signed contract, so amending one on
    an approved plan voids the signature; a decision's field is not the task set and leaves it
    standing. `result` learns whether that happened, for the receipt."""
    if args.field == "files":
        _refuse_illegal_anchors({"tasks": [{"id": args.id, "files": want}]},
                                f"the replacement for {args.id}.files")
    spliced = "".join(cur[:first] + rendered + cur[last:])
    task_ids = [args.id] if args.key == "tasks" else []
    spliced, result["reset"] = _maybe_reset_approval(spliced, base_doc, "amend", task_ids)
    return spliced


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
    result = {}

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
        spliced = _amended_text(cur, f2, l2, rendered, want, args, base_doc, result)
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
    if result.get("reset"):
        print(APPROVAL_RESET_LINE)
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


def _deleted_bytes(base_bytes, requested, receipt=None):
    """The plan's bytes with every requested item's lines removed, or a refusal.

    THE WHOLE EDIT AS A FUNCTION OF BYTES, `_signed_approval_bytes`'s shape: the verb's lock
    plumbing stays three lines and this stays reachable from a unit test, which is the remedy
    `_require_locked_hash` and `_verify_amend` both got for the same reason. `receipt`, when
    given, is a dict that learns whether the approval was reset (C4).
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
    spliced = _reset_after_deletion(_splice_out(lines, ranges), base_doc, requested, receipt)
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


def _reset_after_deletion(spliced, base_doc, requested, receipt):
    """DELETING A TASK CHANGES THE TASK SET (C4): an approved plan is reset to pending. A
    decision's removal is not the task set and leaves the signature standing."""
    doomed_tasks = [iid for key, iid in requested if key == "tasks"]
    text, reset = _maybe_reset_approval(spliced.decode("utf-8"), base_doc, "delete-items",
                                        doomed_tasks)
    if receipt is not None:
        receipt["reset"] = reset
    return text.encode("utf-8")


def cmd_delete_items(args):
    """Delete whole tasks and decisions by id, under the same lock every other verb takes."""
    resolved = _resolve_plan(args.file)
    try:
        requested = _requested_deletions(args)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)

    receipt = {}

    def transform(base_bytes):
        if base_bytes is None:
            raise harness_merge.MergeRefusal(
                3, [f"plan-merge: {resolved} does not exist, so there is nothing to delete."])
        return _deleted_bytes(base_bytes, requested, receipt)

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
    if receipt.get("reset"):
        print(APPROVAL_RESET_LINE)
    print(f"APPLIED {resolved}")
    sys.exit(0)


# ---------------------------------------------------------------------------
# `check` — resolve every anchor, route and trace before a plan is signed (FEAT-59 SC-07).
#
# FEAT-54's first build dispatch BLOCKED on five plan paths that four goal-check cycles and
# three panel cycles had read and none had resolved: "the first build dispatch found it in one
# member spawn". Readers were asked to find by reading what a script can find by running. This
# verb is that script. It WRITES NOTHING; exit 0 means every `files:` anchor resolves under
# --root, every team task's `execution_agent` is granted its files by the SAME resolver the
# build hook consults (check-plan-routes.resolve_agents -> check-domain.sh --resolve), and
# every `traces:` id is present in the sibling BRIEF.md. Exit 1 lists each failure on its own
# FAIL line; exit 2 means the check could not run at all (no manifest under --root).


def _check_plan_routes_module():
    """check-plan-routes.py as a module: the hyphen keeps it out of `import`, and its resolver
    is the ONE route resolver (DEC-179) — re-implementing it here would be a second copy of the
    rule check-domain.sh applies at build time, which is the drift SC-07 exists to close."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_plan_routes", os.path.join(BIN_DIR, "check-plan-routes.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _trace_in_brief(trace, brief_text):
    return re.search(rf"(?<![\w-]){re.escape(str(trace))}(?![\w-])", brief_text) is not None


class _Routes:
    """The route resolver bound to one --root, answering once per path.

    check-domain.sh is a subprocess per question, so the answer for a path is cached across
    the tasks that name it. Which checkout answers is check-plan-routes' choice, not ours: it
    runs the check-domain that lives under the resolution manifest's own root, so a worktree
    is answered by its owner (the DEVIATION rule), and no environment is set here — the
    retired env chain is refused by test-no-distribution case 6."""

    def __init__(self, root):
        self.root = root
        self.cpr = _check_plan_routes_module()
        try:
            self.manifest_root, self.deviation = self.cpr.resolution_manifest(root)
        except ValueError as exc:
            _die(2, f"plan-merge: {exc}")
        self._granted = {}

    def granted(self, path):
        if path not in self._granted:
            self._granted[path] = self.cpr.resolve_agents(path, self.root, self.manifest_root)
        return self._granted[path]


def _literal_paths(task):
    """The bare, non-glob path of every files: entry — what the route question is about."""
    paths = (plan_anchors.path_of(entry) for entry in task.get("files") or [])
    return [p for p in paths if isinstance(p, str) and not plan_anchors.is_glob(p)]


def _route_faults(task, tid, routes):
    """FAIL lines for a team task whose execution_agent is not granted every literal path."""
    if task.get("execution_mode") != "team":
        return []
    agent = task.get("execution_agent")
    if not isinstance(agent, str) or not agent.strip():
        return [f"FAIL {tid} execution_agent: missing, and execution_mode is team — the lane "
                "row is the authority, so name the agent it grants"]
    return [f"FAIL {tid} execution_agent: {agent} is not granted {path} "
            f"(granted: {', '.join(routes.granted(path)) or 'NOBODY'})"
            for path in _literal_paths(task) if agent not in routes.granted(path)]


def _trace_faults(task, tid, brief_text):
    if brief_text is None:
        return []
    return [f"FAIL {tid} traces: {trace} is not in the sibling BRIEF.md"
            for trace in task.get("traces") or [] if not _trace_in_brief(trace, brief_text)]


def _check_task(task, root, brief_text, routes):
    """(failures, anchors_resolved) for one task."""
    tid = str(task.get("id") or "<no id>")
    faults = [plan_anchors.resolve(entry, root) for entry in task.get("files") or []]
    failures = [f"FAIL {tid} files: {fault}" for fault in faults if fault is not None]
    failures += _route_faults(task, tid, routes)
    failures += _trace_faults(task, tid, brief_text)
    return failures, faults.count(None)


def _check_tasks(doc, resolved_plan):
    tasks = doc.get("tasks") if isinstance(doc, dict) else None
    if not isinstance(tasks, list):
        _die(5, f"plan-merge: {resolved_plan} carries no tasks: list to check")
    return tasks


def _check_inputs(args):
    """(resolved plan path, root, tasks) — or the exit-2/exit-5 refusal that says why not."""
    resolved_plan = _resolve_plan(args.file)
    root = os.path.abspath(args.root)
    if not os.path.isfile(os.path.join(root, harness_boundary.MARKER)):
        _die(2, f"plan-merge: {root} carries no {harness_boundary.MARKER}, so no route can be "
                "resolved against it — --root must be a harness checkout.")
    try:
        doc = harness_yaml.load_file(resolved_plan)
    except harness_yaml.YamlParseError as exc:
        _die(5, f"plan-merge: {resolved_plan} does not load: {exc}")
    return resolved_plan, root, _check_tasks(doc, resolved_plan)


def _brief_text(resolved_plan):
    """(text or None, failure line or None) for the sibling BRIEF.md. Absent is a failure: the
    traces cannot be checked, and an uncheckable trace must not read as a resolved one."""
    brief = os.path.join(os.path.dirname(resolved_plan), "BRIEF.md")
    if not os.path.isfile(brief):
        return None, f"FAIL BRIEF.md: {brief} is absent, so no traces: id can be checked"
    with open(brief, encoding="utf-8") as fh:
        return fh.read(), None


def _check_all(tasks, root, brief_text, routes):
    """(failures, anchors resolved) across every task, printing an OK line per clean task."""
    failures, total = [], 0
    for task in tasks:
        if not isinstance(task, dict):
            failures.append(f"FAIL tasks: {task!r} is not a mapping")
            continue
        task_failures, count = _check_task(task, root, brief_text, routes)
        total += count
        failures += task_failures
        if not task_failures:
            print(f"OK {task.get('id')} {count} anchor(s) resolved")
    return failures, total


def cmd_check(args):
    resolved_plan, root, tasks = _check_inputs(args)
    routes = _Routes(root)
    brief_text, brief_fault = _brief_text(resolved_plan)
    preface = [f"FAIL {routes.deviation}"] if routes.deviation else []
    preface += [brief_fault] if brief_fault else []
    task_failures, total = _check_all(tasks, root, brief_text, routes)
    failures = preface + task_failures
    for line in failures:
        print(line)
    print(f"CHECK {resolved_plan} against {root}: {len(tasks)} task(s), {total} anchor(s) "
          f"resolved, {len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


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

# NEVER-DELETE IS A PROPERTY OF THE FIRST TWO VERBS, NOT OF THE TOOL (FEAT-41 T-03). The lock
# and the splice are what fix #628 and they apply to every verb; never deleting a task is a
# separate promise that `apply` and its alias alone make, which is why they share `cmd_apply`
# verbatim. `delete-items` is what that distinction was always for: it deletes, by id and with
# a reason, through the same lock and the same splice, and it registers itself below rather
# than here because its id flags repeat.
VERBS = (
    ("apply", "merge a proposal into a plan.yaml — adds items, replaces the fields a proposal "
              "names on an existing id, never deletes",
     (_FILE, _PROPOSAL), cmd_apply),
    ("add-tasks", "alias of apply, for callers that only add tasks — identical code path",
     (_FILE, _PROPOSAL), cmd_apply),
    ("set-task-station", "set ONE task's status, by splicing its one line",
     (_FILE, ("--task", "the task id, T-NN"), _STATION), cmd_set_task_station),
    ("set-feature-station", "set or insert the top-level status key",
     (_FILE, _STATION), cmd_set_feature_station),
    ("set-panel", "replace the top-level panel mapping with a validated value, keeping the "
                  "bytes of every unchanged finding",
     (_FILE, ("--value-file", "YAML file holding the replacement panel mapping")), cmd_set_panel),
    ("set-lanes", "replace the top-level lanes mapping with a validated value",
     (_FILE, ("--value-file", "YAML file holding the replacement lanes mapping")), cmd_set_lanes),
    ("check", "resolve every files: anchor, execution_agent route and traces: id; writes nothing",
     (_FILE, ("--root", "the checkout root anchors and routes resolve against")), cmd_check),
)


def _register_record_panel(sub):
    """ITS OWN REGISTRATION: `--last-run` is optional (it defaults to the digest's run
    directory) and `--cycle` is typed, neither of which the uniform table can express."""
    p = sub.add_parser("record-panel",
                       help="write the panel mapping FROM the validator lead's digest, carrying "
                            "every finding already present byte for byte")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--digest", required=True,
                   help="the validator lead's digest.md — its fenced DIGEST block is parsed")
    p.add_argument("--cycle", required=True, type=int, help="the panel cycle being recorded")
    p.add_argument("--last-run", default=None,
                   help="the run directory name to record; defaults to the digest's parent dir")
    p.set_defaults(func=cmd_record_panel)


def _register_sign_approval(sub):
    p = sub.add_parser("sign-approval", help="the ONLY route that writes the approval mapping")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--by", required=True, help="the signer's name")
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument(
        "--overrule", action="append", default=[], metavar="FINDING-ID:REASON",
        help="accept a current panel finding's risk; repeat for multiple findings",
    )
    p.add_argument("--rework", default=None, metavar="rounds=N,minutes=M",
                   help="the operator's ONE rework ruling (SC-15), recorded on the sibling "
                        "feature.json as `rework`; needs --decision")
    p.add_argument("--decision", default=None, metavar="PATH",
                   help="where the rework ruling is recorded (feature.json rework.decision)")
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
    _register_record_panel(sub)
    _register_sign_approval(sub)
    _register_amend(sub)
    _register_delete_items(sub)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
