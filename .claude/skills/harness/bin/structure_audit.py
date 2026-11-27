"""structure_audit.py — the consolidation, checker-structure, posture and broad-catch audits.

Moved verbatim from check-plan-routes.py by FEAT-2489. `check-plan-routes.py
--consolidation-audit` and the in-process calls in
tests/integration/test-checker-structure-locks.py are its entry paths. It is a
gate-imported library under DEC-174's library clause, never imports the entry, and keeps
no module-scope session or index (SPEC Structure-audit guardrail).
"""
import ast
import collections
import os
import re
from canonical_reader_audit import _reader_source_paths


# ---------------------------------------------------------------------------------------------
# FEAT-61 T-05: THE TWO CONSOLIDATION LOCKS (D-08). Exactly two, by decision — not a generic
# duplicate detector and not a dead-symbol sweep. Each names the one reintroduction path the
# wave closed and would otherwise reopen silently:
#
#   1. A feature-station literal outside factory_config.py. The station table is the one place
#      a lifecycle bucket is spelled; a call site that writes `("plan", "ready", "building",
#      "review")` or `("done",) + TERMINAL_STATIONS` again is the seventh-station-in-nine-of-ten
#      defect this wave removed. BY BUCKET AND CONTEXT, NOT BY WORD. A literal collection is a
#      respelling when it is USED AS A PREDICATE — the target of an `in`/`not in` test, a
#      returned or assigned value — and its names all fall inside ONE lifecycle bucket
#      (ACTIVE_STATIONS or FINISHED_STATIONS), two or more of them. Subset, not equality
#      (validate c1, CR-01): a copied bucket that has ALREADY drifted — `("plan", "ready",
#      "building")` missing `review` — is the most realistic recurrence, and an exact-set check
#      waves it through. plan-merge.py's `_work_started` over {building, review, done} spans
#      both buckets and so matches neither (D-11); a `for` over station keys to derive column
#      names is iteration, not a predicate, and is not flagged. A single name is a station, not
#      a bucket. The `<literal> + <export>` concatenation is flagged wherever it appears.
#   2. A second `spec_from_file_location` under bin/. harness_boundary.load_repo_module owns
#      the registration and failure decisions; a fresh copy re-derives them from scratch.
#
# Tests are not scanned: a test loading its subject by path is that test's own business.
STATION_TABLE_REL = os.path.join(".claude", "skills", "harness", "bin", "factory_config.py")
# FEAT-64: the home symbol is the private body `_load_repo_module`. `load_repo_module` (the
# public entry every caller names) runs that body inside `_as_repo_module_failure`, the ONE
# broad catch the load and call boundaries share -- so the spec call moved one function
# inward while staying the sole one under bin/.
MODULE_LOADER_HOME = (
    os.path.join(".claude", "skills", "harness", "bin", "harness_boundary.py"),
    "_load_repo_module",
)
_STATION_EXPORTS = ("MANDATED_STATIONS", "TERMINAL_STATIONS", "ACTIVE_STATIONS",
                    "FINISHED_STATIONS")


def _unwrap_set_call(node):
    """`set(x)` / `frozenset(x)` → `x`; anything else unchanged."""
    is_set_call = (isinstance(node, ast.Call) and not node.keywords and len(node.args) == 1
                   and isinstance(node.func, ast.Name) and node.func.id in ("set", "frozenset"))
    return node.args[0] if is_set_call else node


def _string_literal_collection(node):
    """The set of strings in a literal tuple/list/set, or `set(...)`/`frozenset(...)` over
    one, or None when the node is anything else (including a collection with a non-string)."""
    node = _unwrap_set_call(node)
    if not isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return None
    if not all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts):
        return None
    return {e.value for e in node.elts}


def _names_station_export(node):
    return (isinstance(node, ast.Attribute) and node.attr in _STATION_EXPORTS) or (
        isinstance(node, ast.Name) and node.id in _STATION_EXPORTS)


def _lifecycle_buckets():
    import factory_config
    return {"ACTIVE_STATIONS": set(factory_config.ACTIVE_STATIONS),
            "FINISHED_STATIONS": set(factory_config.FINISHED_STATIONS)}


def _is_station_concatenation(node):
    """`<string literal> + <STATION export>` in either order — the `("done",) +
    TERMINAL_STATIONS` shape that used to stand in for FINISHED_STATIONS at six sites."""
    if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)):
        return False
    sides = (node.left, node.right)
    return (any(_string_literal_collection(s) for s in sides)
            and any(_names_station_export(s) for s in sides))


_PREDICATE_PARENTS = (ast.Compare, ast.Return, ast.Assign, ast.AnnAssign)
# The only node types `_respelled_bucket` can answer for: a literal collection, a set(...) /
# frozenset(...) call over one, or a `+` concatenation. Everything else is skipped unexamined.
_LITERAL_CANDIDATES = (ast.Tuple, ast.List, ast.Set, ast.Call, ast.BinOp)


def _respelled_bucket(node, parent, buckets):
    """Which table export a literal node respells, or None: a concatenation anywhere, or a
    literal collection of two or more names inside one bucket, used as a predicate."""
    if _is_station_concatenation(node):
        return "FINISHED_STATIONS by concatenation"
    values = _string_literal_collection(node)
    if not values or len(values) < 2 or not isinstance(parent, _PREDICATE_PARENTS):
        return None
    return next((name for name, bucket in buckets.items() if values <= bucket), None)


# FEAT-2081 SC-06: the fact lists one traversal fills, by node type. A node of several
# kinds (a set(...) Call is a call AND a literal candidate) lands in each.
_INDEX_KINDS = (
    ("functions", (ast.FunctionDef, ast.AsyncFunctionDef)),
    ("calls", (ast.Call,)),
    ("handlers", (ast.ExceptHandler,)),
    ("tries", (ast.Try,)),
    ("literal_candidates", _LITERAL_CANDIDATES),
    ("constants", (ast.Constant,)),
)


class _SourceIndex:
    """FEAT-2081 SC-06: ONE breadth-first, parent-aware traversal of one parsed tree, in
    `ast.walk`'s exact order, dispatching each node to every rule's fact list. Facts are
    references into the tree, never copies; every structure rule reads the index and none
    walks the tree again. Subtree questions (the calls or constants inside one function,
    statement or call) are answered from the parent links, in the order `ast.walk(subject)`
    would yield them -- the restriction of the tree's breadth-first order to the subtree."""

    def __init__(self, tree):
        self.tree, self.nodes, self.parent = tree, [tree], {tree: None}
        self.facts = {kind: [] for kind, _types in _INDEX_KINDS}
        self._members, self._lists_of_type = None, {}
        # `nodes` is its own FIFO queue: appending children while reading forward is
        # exactly ast.walk's breadth-first order.
        for node in self.nodes:
            for child in ast.iter_child_nodes(node):
                self.parent[child] = node
                self.nodes.append(child)
            for bucket in self._lists_for(type(node)):
                bucket.append(node)
        self.program_texts = [c.value for c in self.facts["constants"] if _may_be_program(c)]

    def _lists_for(self, node_type):
        """The fact lists a node of `node_type` belongs in, resolved once per type."""
        lists = self._lists_of_type.get(node_type)
        if lists is None:
            lists = self._lists_of_type[node_type] = [
                self.facts[kind] for kind, types in _INDEX_KINDS if issubclass(node_type, types)]
        return lists

    def within(self, subject, kind):
        """The `kind` (ast.Call or ast.Constant) nodes of `subject`'s subtree, itself
        included, in `ast.walk(subject)` order."""
        if self._members is None:
            self._members = self._subtree_members()
        return self._members.get((subject, kind), ())

    def _subtree_members(self):
        members = collections.defaultdict(list)
        for kind, nodes in ((ast.Call, self.facts["calls"]), (ast.Constant, self.facts["constants"])):
            for node in nodes:
                ancestor = node
                while ancestor is not None:
                    members[(ancestor, kind)].append(node)
                    ancestor = self.parent[ancestor]
        return members


_SOURCE_ERRORS = (OSError, SyntaxError, ValueError)


def _cached(store, key, build):
    """`store[key]`, built once; a source error is kept and re-raised to every asker, so
    each rule still answers it with its own except clause and its own message."""
    if key not in store:
        try:
            store[key] = build()
        except _SOURCE_ERRORS as error:
            store[key] = error
    value = store[key]
    if isinstance(value, BaseException):
        raise value
    return value


def _read_source(absolute):
    with open(absolute, encoding="utf-8") as source:
        return source.read()


class _AuditSession:
    """FEAT-2081 SC-06: one audit invocation's sources. Each physical file is read, parsed and
    indexed at most once however many rules share it -- the reader census, the
    checker-structure surface and the broad-catch census overlap on check-state.py and
    check_state/ -- and each embedded program likewise. Built fresh by every public entry and
    dropped with it: nothing outlives the invocation or crosses roots. Parses keep the
    root-relative filename every rule used before, so error text is unchanged."""

    def __init__(self, root):
        self.root, self._texts, self._indexes, self._programs = root, {}, {}, {}
        self._census = None

    def census(self):
        """The ordered reader-source census, walked once per invocation."""
        if self._census is None:
            self._census = _reader_source_paths(self.root)
        return self._census

    def text(self, absolute):
        return _cached(self._texts, os.path.normpath(absolute), lambda: _read_source(absolute))

    def index(self, absolute, relative):
        def build():
            return _SourceIndex(ast.parse(self.text(absolute), filename=relative))
        return _cached(self._indexes, os.path.normpath(absolute), build)

    def program(self, text):
        """The index of an embedded program, or None (see _parsed_program); once per text."""
        if text not in self._programs:
            self._programs[text] = _parsed_program(text)
        return self._programs[text]


def _literal_candidates(index):
    """The candidate nodes in `ast.walk` order, and each one's parent with
    `set(...)`/`frozenset(...)` wrappers looked through, so the inner tuple sees the
    Compare/Return the call sits in. Only candidates need a parent, and a wrapper is itself a
    candidate (a Call), so its own parent is always recorded before it is looked through."""
    candidates = index.facts["literal_candidates"]
    parents = {node: index.parent[node] for node in candidates if index.parent[node] is not None}
    for child, parent in list(parents.items()):
        if _unwrap_set_call(parent) is not parent:
            parents[child] = parents.get(parent)
    return candidates, parents


def _feature_station_literal_findings(index, relative, buckets):
    # Keyed by line so `frozenset(("plan", ...))` — a Call wrapping a Tuple — reports once.
    candidates, parents = _literal_candidates(index)
    findings = {}
    for node in candidates:
        respelled = _respelled_bucket(node, parents.get(node), buckets)
        if respelled is not None and node.lineno not in findings:
            findings[node.lineno] = (
                f"{relative}::{_call_symbol(index, node)}:{node.lineno} feature-station literal "
                f"respells factory_config.{respelled} — read the table's export or call "
                "is_active/is_finished (FEAT-61 D-08)")
    return [findings[line] for line in sorted(findings)]


def _callee_name(call):
    func = call.func
    return func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)


def _module_loader_findings(index, relative):
    home_file, home_symbol = MODULE_LOADER_HOME
    loaders = [
        (node, _call_symbol(index, node)) for node in index.facts["calls"]
        if _callee_name(node) == "spec_from_file_location"
    ]
    return [
        f"{relative}::{symbol}:{node.lineno} second spec_from_file_location under bin/ — "
        "load through harness_boundary.load_repo_module (FEAT-61 D-08)"
        for node, symbol in loaders
        if not (relative == home_file and symbol == home_symbol)
    ]


def _call_symbol(index, node):
    """The innermost function enclosing `node`, or `<module>`."""
    containers = [
        candidate for candidate in index.facts["functions"]
        if candidate.lineno <= node.lineno <= candidate.end_lineno
    ]
    if not containers:
        return "<module>"
    return min(containers, key=lambda c: c.end_lineno - c.lineno).name


# ---------------------------------------------------------------------------------------------
# FEAT-62 T-02: THE THREE CHECKER-STRUCTURE LOCKS, plus one invocation-posture scan that is
# deliberately NOT counted as a fourth structural rule. Each names the one way the
# decomposition of check-state.py could grow back:
#
#   1. MODULE BODY. After the trusted bootstrap (everything through `root = sys.argv[1]`), the
#      checker's module body holds imports, definitions, constants and tables, and the guarded
#      main call — never an invariant. A top-level `for`/`while`/`with`/`try` (other than an
#      import guard), an `if` that is not the main guard, or a statement that READS (open, read,
#      glob, subprocess, a canonical accessor) is a block escaping the table. In the same family:
#      a source the runner context parses ONCE (plan.yaml as a mapping; BRIEF.md, STATE.md and
#      PLAN.md as text) is not re-parsed inside an invariant body — `load_plan(...)` or a
#      `read(...)`/`open(...)` naming one of those files there is a second parse of a shared
#      source, which is the drift the context exists to remove.
#   2. READS. Every `Inv` row declares what its function opens (`path:`, `git:`, `gh:`), and
#      that declaration is what `--changed` joins on. A file name the function (or a helper it
#      calls) names in code, a `git` argv it spawns, or a `gh` binary it runs that the row does
#      not declare is a silent hole in selective execution — the run skips the row exactly when
#      that input changed. Message text (f-strings) is not an input and is not scanned.
#   3. AUTHORITY. Every row's `authority` resolves to a live `DEC-NNN` in DECISIONS-INDEX.md and
#      is not STRUCK. DEC-188 says a struck decision is removed from every gate; this is the
#      mechanism — striking a decision reddens every invariant that stood on it until each is
#      re-cited or retired. A decision amended in place under the same number is an accepted,
#      recorded limit.
#
#   POSTURE (not a structural rule): `--changed` is the edit-loop verb and never the gate.
#   No workflow under .github/workflows/ and no hook under .claude/skills/harness/hooks/ may
#   invoke check-state.py with it; CI, command entry and pre-commit run the full table.
BIN_REL = os.path.join(".claude", "skills", "harness", "bin")
CHECKER_REL = os.path.join(BIN_REL, "check-state.py")
# FEAT-69: the entry is a bootstrap over the check_state/ package; the locked surface is the
# entry PLUS every package file, parsed into ONE function table so a helper reached through an
# import (`from check_state.ctx import ...`) is walked exactly as a same-file helper was.
CHECKER_PACKAGE_REL = os.path.join(BIN_REL, "check_state")
CHECKER_TABLE_MODULE = "table"
# The settled ownership (FEAT-69 BRIEF, by declared reads): the module that must DEFINE each
# row's run function. A row absent here is a finding -- a new invariant names its family in
# the lock before it lands, which is the placement rule with teeth.
ROW_FAMILIES = {
    "plan": ("INV-35", "INV-3", "INV-4", "INV-5", "INV-34", "INV-32", "INV-44", "INV-51"),
    "feature_record": ("INV-1", "INV-2", "INV-6", "INV-7", "INV-8", "INV-12", "INV-18", "INV-22",
                       "INV-23", "INV-33", "INV-39", "INV-40", "INV-43", "INV-47"),
    "run_state": ("INV-15", "INV-16", "INV-36", "INV-46"),
    "seams": ("INV-17",),
    "brief": ("INV-38", "INV-41", "INV-49"),
    "worktrees": ("INV-25", "INV-27", "INV-29", "INV-31"),
    "board": ("INV-21", "INV-24", "INV-26", "INV-37"),
    "host": ("INV-19", "INV-42", "INV-45", "INV-48"),
    "corpus": ("INV-52",),
}
_FAMILY_OF_ROW = {row: family for family, rows in ROW_FAMILIES.items() for row in rows}
DECISIONS_INDEX_REL = os.path.join(".harness", "harness", "docs", "DECISIONS-INDEX.md")
_BOOTSTRAP_END_TARGET = "root"           # the first top-level `root = ...` closes the bootstrap
_READER_CALLEES = {"open", "read", "glob", "iglob", "run", "check_output", "Popen", "listdir",
                   "walk", "load_plan", "load_feature_json", "load_harness_json", "load_fleet",
                   "load_file", "load_repo_module"}
# The runner parses these ONCE into Ctx (plan_docs, record, cj); an invariant that calls the
# loader again has forked the source (FEAT-62 SC-03; feature/harness JSON added by FEAT-63 SC-05,
# which is what let sixteen re-parses sit under a green audit).
_SHARED_SOURCE_LOADERS = {"load_plan", "load_feature_json", "load_harness_json"}
_SHARED_SOURCE_TEXTS = ("BRIEF.md", "STATE.md", "PLAN.md")
_INVARIANT_FN = re.compile(r"^(?:inv_\d+|_inv\d+_\w+|collate_\w+|_collate\d+_\w+)$")
_INPUT_LITERAL = re.compile(r"^[\w.*-]+\.(?:yaml|yml|json|md|py)$")
_READ_KINDS = ("path:", "git:", "gh:")


def _checker_package_paths(root):
    """(absolute, relative) for every check_state/*.py in name order."""
    directory = os.path.join(root, CHECKER_PACKAGE_REL)
    if not os.path.isdir(directory):
        return []
    return [(os.path.join(directory, name), os.path.join(CHECKER_PACKAGE_REL, name))
            for name in sorted(os.listdir(directory)) if name.endswith(".py")]


def _checker_module_name(relative):
    """`check-state` for the entry, the stem for a package file."""
    return os.path.splitext(os.path.basename(relative))[0]


def _checker_trees(session):
    """[(relative, index)] for the entry then every package file, and the parse findings for
    those that did not parse. The entry failing to parse is the one finding that stands alone."""
    trees, findings = [], []
    try:
        trees.append((CHECKER_REL, session.index(os.path.join(session.root, CHECKER_REL), CHECKER_REL)))
    except (OSError, UnicodeDecodeError, SyntaxError) as error:
        return [], [f"{CHECKER_REL}::<module> source_parse: {error}"]
    sources = _checker_package_paths(session.root)
    for absolute, relative in sources:
        try:
            session.text(absolute)
        except (OSError, UnicodeDecodeError):
            findings.append(f"{relative}::<module> source_parse: unreadable")
            continue
        try:
            trees.append((relative, session.index(absolute, relative)))
        except (SyntaxError, ValueError) as error:
            findings.append(f"{relative}::<module> source_parse: {error}")
    return trees, findings


def _bootstrap_end(tree):
    """Line of the first top-level `root = ...`; everything after it is the locked body."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == _BOOTSTRAP_END_TARGET for t in node.targets):
            return node.lineno
    return 0


def _is_main_guard(node):
    test = node.test
    return (isinstance(node, ast.If) and isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name) and test.left.id == "__name__")


def _is_import_guard(node):
    """`try: import x except: x = None` — the one Try shape the body may carry."""
    body_ok = all(isinstance(s, (ast.Import, ast.ImportFrom)) for s in node.body)
    handlers_ok = all(all(isinstance(s, (ast.Assign, ast.Pass)) for s in h.body) for h in node.handlers)
    return isinstance(node, ast.Try) and body_ok and handlers_ok


def _reads_in(index, node):
    """Callee names in `node` that read the tree — the vocabulary in _READER_CALLEES."""
    return sorted({_callee_name(c) for c in index.within(node, ast.Call)
                   if _callee_name(c) in _READER_CALLEES})


_BLOCK_KINDS = (ast.For, ast.While, ast.With, ast.AsyncFor, ast.AsyncWith)


def _module_body_shape(node):
    """What is wrong with a top-level statement's SHAPE, or None: a block, a conditional that
    is not the main guard, a try that is not an import guard."""
    if isinstance(node, _BLOCK_KINDS):
        return f"{type(node).__name__.lower()} block at module scope"
    if isinstance(node, ast.If) and not _is_main_guard(node):
        return "conditional at module scope"
    if isinstance(node, ast.Try) and not _is_import_guard(node):
        return "try block at module scope"
    return None


def _module_body_finding(index, node, relative):
    what = _module_body_shape(node)
    if what is None and isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr)):
        reads = _reads_in(index, node)
        what = f"reads the tree at module scope ({', '.join(reads)})" if reads else None
    return f"{relative}::<module>:{node.lineno} {what}" if what else None


def _module_body_findings(index, relative):
    tree = index.tree
    after = _bootstrap_end(tree)
    findings = []
    for node in tree.body:
        if node.lineno <= after:
            continue
        finding = _module_body_finding(index, node, relative)
        if finding:
            findings.append(finding + " — an invariant lives in a function registered in INVARIANTS (FEAT-62 SC-03)")
    return findings


def _names_shared_text(index, call):
    return any(isinstance(c.value, str) and c.value in _SHARED_SOURCE_TEXTS
               for c in index.within(call, ast.Constant))


def _reparsing_calls(index, fn):
    """(callee, lineno) for every call in `fn` that parses a runner-shared source again."""
    return [(_callee_name(c), c.lineno) for c in index.within(fn, ast.Call)
            if _callee_name(c) in _SHARED_SOURCE_LOADERS
            or (_callee_name(c) in ("read", "open") and _names_shared_text(index, c))]


def _reparse_findings(index, relative):
    """A shared source parsed again inside an invariant body (module-body family)."""
    return [f"{relative}::{fn.name}:{lineno} re-parses a runner-shared source ({callee}) — read it "
            f"from ctx (FEAT-62 SC-03)"
            for fn in _invariant_functions(index.tree) for callee, lineno in _reparsing_calls(index, fn)]


def _invariant_functions(tree):
    return [n for n in tree.body if isinstance(n, ast.FunctionDef) and _INVARIANT_FN.match(n.name)]


def _module_functions(tree):
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        for m in cls.body:
            if isinstance(m, ast.FunctionDef):
                fns[f"{cls.name}.{m.name}"] = m
    return fns


def _package_import_module(node):
    """The `<module>` of a `from check_state.<module> import ...` statement, else None."""
    if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("check_state."):
        return node.module.split(".", 1)[1]
    return None


def _package_imports(tree):
    """{local name: (module, name)} for every `from check_state.<module> import ...` in `tree`."""
    imports = {}
    for node in tree.body:
        module = _package_import_module(node)
        if module is None:
            continue
        for alias in node.names:
            imports[alias.asname or alias.name] = (module, alias.name)
    return imports


class _PackageFunctions:
    """FEAT-69: one function table over the entry and every package file. Keys are
    `<module>.<function>` for module functions and `Ctx.<method>` for the context's methods
    (the one class); a bare callee resolves in its caller's module first, then through that
    module's `from check_state.<m> import` bindings -- never through an assignment alias."""

    def __init__(self, trees):
        self.fns, self.module_of, self.imports, self.index_of = {}, {}, {}, {}
        for relative, index in trees:
            module = _checker_module_name(relative)
            self.imports[module] = _package_imports(index.tree)
            for name, fn in _module_functions(index.tree).items():
                key = name if name.startswith("Ctx.") else f"{module}.{name}"
                self.fns[key] = fn
                self.module_of[key] = module
                self.index_of[key] = index

    def resolve(self, module, callee):
        """The table key `callee` names when called from `module`, or None."""
        if callee.startswith("Ctx."):
            return callee if callee in self.fns else None
        if f"{module}.{callee}" in self.fns:
            return f"{module}.{callee}"
        bound = self.imports.get(module, {}).get(callee)
        if bound and f"{bound[0]}.{bound[1]}" in self.fns:
            return f"{bound[0]}.{bound[1]}"
        return None


def _is_string_assign(node):
    return (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str))


def _string_constants(tree):
    """Top-level `NAME = "..."` bindings — the `_FEATURE_JSON`-style read aliases."""
    return {t.id: node.value.value
            for node in tree.body if _is_string_assign(node)
            for t in node.targets if isinstance(t, ast.Name)}


def _inv_rows(index):
    """(name, run function name, reads tuple, authority, lineno) for every Inv(...) in the table."""
    aliases = _string_constants(index.tree)
    rows = []
    for call in index.facts["calls"]:
        if not (isinstance(call.func, ast.Name) and call.func.id == "Inv"):
            continue
        name, run, _scope, reads, _contract, authority = call.args
        declared = tuple(aliases.get(e.id) if isinstance(e, ast.Name) else e.value for e in reads.elts)
        rows.append((name.value, run.id, declared, authority.value, call.lineno))
    return rows


def _reachable(key, table, seen=None):
    """`key` and every check-state function it calls, transitively (module functions by name
    in the caller's module or through its package imports, Ctx methods through
    `ctx.<method>(...)`), across every file of the package (FEAT-69)."""
    seen = set() if seen is None else seen
    if key in seen or key not in table.fns:
        return seen
    seen.add(key)
    for callee in _called_names(table.index_of[key], table.fns[key]):
        _reachable(table.resolve(table.module_of[key], callee), table, seen)
    return seen


def _called_names(index, fn):
    """Names `fn` calls that could be check-state functions: bare names, and `ctx.<m>` as
    `Ctx.<m>`."""
    names = []
    for call in index.within(fn, ast.Call):
        f = call.func
        if isinstance(f, ast.Name):
            names.append(f.id)
        elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "ctx":
            names.append(f"Ctx.{f.attr}")
    return names


# `spawn` is Ctx.spawn, the checker's one process boundary (FEAT-63 T-01): every git/gh read
# now arrives through it, so the lock reads its argv exactly as it read subprocess.run's.
_SPAWN_CALLEES = ("run", "check_output", "Popen", "spawn")
# The one GitHub read check-state.py makes through a module rather than an argv: gh_board's
# board query. Declared on the row as "gh:board".
_BOARD_READ_CALLEE = "board_stations_for"


def _argv_tokens(call):
    """The constant string tokens of a `subprocess.run([...])`-shaped argv, in order; a
    `"literal" % x` token contributes its literal, anything else contributes None so position
    is kept. Empty when the call is not a spawn."""
    if _callee_name(call) not in _SPAWN_CALLEES or not call.args:
        return []
    argv = call.args[0]
    if not isinstance(argv, (ast.List, ast.Tuple)):
        return []
    return [_token_text(e) for e in argv.elts]


def _token_text(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        node = node.left
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and "gh" in node.id.lower():
        return "gh"
    return None


def _git_resource(tokens):
    """`git:<subcommand>` for a git argv; `worktree list` reads as `git:worktree-list`.
    `-C <dir>` is skipped; the first token that is not an option is the subcommand."""
    rest = tokens[1:]
    while rest and rest[0] == "-C":
        rest = rest[2:]
    words = [w for w in rest if w is not None and not w.startswith("-")]
    if not words:
        return "git:"
    return "git:" + ("-".join(words[:2]) if words[0] == "worktree" else words[0])


def _gh_resource(tokens):
    """`gh:<resource>`: the subcommand (`gh auth status` -> gh:auth), or for `gh api` the last
    path segment of the endpoint before its query (`repos/x/milestones?...` -> gh:milestones)."""
    words = [w for w in tokens[1:] if w is not None and not w.startswith("-")]
    if not words:
        return "gh:"
    if words[0] != "api" or len(words) < 2:
        return "gh:" + words[0]
    return "gh:" + words[1].split("?", 1)[0].rstrip("/").rsplit("/", 1)[-1]


def _spawn_resource(call):
    """The `git:<op>` / `gh:<resource>` a call reads, or None: an argv spawn headed by git or a
    gh binary, or the board module's query."""
    if _callee_name(call) == _BOARD_READ_CALLEE:
        return "gh:board"
    tokens = _argv_tokens(call)
    if tokens and tokens[0] == "git":
        return _git_resource(tokens)
    if tokens and tokens[0] == "gh":
        return _gh_resource(tokens)
    return None


def _input_literals(index, fn):
    """File-name string literals in `fn`, skipping the constant parts of every f-string — its
    message text, not an input."""
    return {n.value for n in index.within(fn, ast.Constant)
            if isinstance(n.value, str) and not isinstance(index.parent[n], ast.JoinedStr)
            and _INPUT_LITERAL.match(n.value)}


def _observed_inputs(index, fn):
    """File-name literals (outside f-strings) and git/gh resources read in one function body."""
    resources = {_spawn_resource(n) for n in index.within(fn, ast.Call)} - {None}
    return _input_literals(index, fn), resources


def _declared_covers(literal, declared):
    return any(d.startswith("path:") and (d.endswith("/" + literal) or d == "path:" + literal
                                          or os.path.basename(d[5:]) == literal)
               for d in declared)


def _row_inputs(run_key, table):
    """Every literal and git/gh resource the row's function and its helpers observe."""
    literals, resources = set(), set()
    for key in sorted(_reachable(run_key, table)):
        if key.startswith("Ctx.__init__"):
            continue
        lits, res = _observed_inputs(table.index_of[key], table.fns[key])
        literals |= lits
        resources |= res
    return literals, resources


def _row_family_finding(row, run_key, table, relative):
    """FEAT-69: the row's run function is DEFINED in the family module its reads name
    (ROW_FAMILIES); an import alias, an assignment alias or a function in another module
    is a finding, and a row no family claims is one too."""
    name, run, _declared, _authority, lineno = row
    family = _FAMILY_OF_ROW.get(name)
    if family is None:
        return (f"{relative}::INVARIANTS:{lineno} {name} belongs to no family in ROW_FAMILIES — name the "
                f"module its reads place it in before it lands (FEAT-69 SC-03)")
    if run_key is None:
        return (f"{relative}::INVARIANTS:{lineno} {name} runs {run!r}, which is not a function defined in "
                f"the package — an alias is not a definition (FEAT-69 SC-03)")
    if table.module_of[run_key] != family:
        return (f"{relative}::INVARIANTS:{lineno} {name} runs {run_key}, defined in check_state/"
                f"{table.module_of[run_key]}.py, but its reads place it in check_state/{family}.py "
                f"(FEAT-69 SC-03)")
    return None


def _row_observed_findings(row, run_key, table, relative):
    """The reads the row's function and its helpers observe but the row does not declare."""
    name, run, declared, _authority, lineno = row
    literals, resources = _row_inputs(run_key, table)
    findings = [f"{relative}::{run}:{lineno} {name} opens {literal!r} but its row declares no path: read "
                f"covering it (FEAT-62 SC-04)"
                for literal in sorted(literals) if not _declared_covers(literal, declared)]
    findings += [f"{relative}::{run}:{lineno} {name} reads {resource} but its row declares no {resource} "
                 f"read (FEAT-62 SC-04)" for resource in sorted(resources) if resource not in declared]
    return findings


def _row_reads_findings(row, table, relative):
    name, run, declared, _authority, lineno = row
    findings = [f"{relative}::INVARIANTS:{lineno} {name} declares {d!r}, which is not path:/git:/gh: "
                f"(FEAT-62 SC-04)" for d in declared if not d.startswith(_READ_KINDS)][:1]
    run_key = table.resolve(CHECKER_TABLE_MODULE, run)
    family = _row_family_finding(row, run_key, table, relative)
    if family:
        findings.append(family)
    if run_key is not None:
        findings += _row_observed_findings(row, run_key, table, relative)
    return findings


def _table_tree(trees):
    """The (relative, index) of the package's table module, or None when it is absent."""
    return next(((rel, index) for rel, index in trees
                 if _checker_module_name(rel) == CHECKER_TABLE_MODULE), None)


def _reads_findings(trees):
    table = _PackageFunctions(trees)
    located = _table_tree(trees)
    if located is None:
        return [f"{CHECKER_PACKAGE_REL}/{CHECKER_TABLE_MODULE}.py is absent — the table is the one place a "
                f"row is declared (FEAT-69 SC-03)"]
    relative, index = located
    return [f for row in _inv_rows(index) for f in _row_reads_findings(row, table, relative)]


def _decisions_index(root):
    """{DEC-NNN: struck?} from the index; None when the index cannot be read."""
    path = os.path.join(root, DECISIONS_INDEX_REL)
    try:
        with open(path, encoding="utf-8") as source:
            lines = source.read().splitlines()
    except OSError:
        return None
    entries = {}
    for line in lines:
        m = re.match(r"^- (DEC-\d+) @\S+ \[[^\]]*\] refs:[^:]*:: (.*)$", line)
        if m:
            entries[m.group(1)] = m.group(2).lstrip().startswith("STRUCK")
    return entries


def _authority_findings(trees, root):
    index = _decisions_index(root)
    findings = []
    located = _table_tree(trees)
    if located is None:
        return []                       # _reads_findings already names the absent table
    relative, tree = located
    if index is None:
        return [f"{relative}::INVARIANTS authority audit CANNOT RUN: {DECISIONS_INDEX_REL} is unreadable "
                f"(FEAT-62 SC-05)"]
    for name, _run, _reads, authority, lineno in _inv_rows(tree):
        if authority not in index:
            findings.append(f"{relative}::INVARIANTS:{lineno} {name} cites {authority}, which does not resolve in "
                            f"{DECISIONS_INDEX_REL} — cite the governing decision (FEAT-62 SC-05)")
        elif index[authority]:
            findings.append(f"{relative}::INVARIANTS:{lineno} {name} cites {authority}, which is STRUCK — a struck "
                            f"decision is removed from every gate (DEC-188); re-cite or retire the invariant "
                            f"(FEAT-62 SC-05)")
    return findings


_POSTURE_DIRS = (os.path.join(".github", "workflows"), os.path.join(".claude", "skills", "harness", "hooks"))


def _posture_lines(path):
    """Line numbers in `path` that invoke check-state.py with --changed, or an OSError."""
    try:
        with open(path, encoding="utf-8", errors="replace") as source:
            return [n for n, line in enumerate(source, 1)
                    if "check-state.py" in line and "--changed" in line]
    except OSError as error:
        return error


def _posture_file_findings(rel_dir, name, path):
    lines = _posture_lines(path)
    if isinstance(lines, OSError):
        return [f"{os.path.join(rel_dir, name)} posture scan cannot read it: {lines}"]
    return [f"{os.path.join(rel_dir, name)}:{n} invokes check-state.py --changed — the gate runs the full "
            f"table; --changed is the edit-loop verb only (FEAT-62 SC-06)" for n in lines]


def _posture_files(root):
    for rel_dir in _POSTURE_DIRS:
        directory = os.path.join(root, rel_dir)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                yield rel_dir, name, path


def _posture_findings(root):
    """A workflow or hook that invokes check-state.py with --changed."""
    return [f for rel_dir, name, path in _posture_files(root)
            for f in _posture_file_findings(rel_dir, name, path)]


# --- FEAT-63 T-03 (SC-04, D-03): ONE AST census of broad catches -- handlers typed exactly
# `Exception`, or bare `except:` -- over every Python script under bin/. check-state.py's
# ceiling is zero. Every other script is frozen at the count observed when this lock landed
# (950b2f04 for the legacy set; harness_boundary.py at its post-T-02 count, RepoModuleError's
# load and call boundaries included). Above its own ceiling is one finding naming the file and
# both counts; below is fine (wave 4 burns the allowlist down); allowance never moves between
# files; a script absent from the list has a zero ceiling. Counted from the AST, never from
# source text or comments -- a text grep of this tree once reported 121 where the AST says 118.
#
# FEAT-64 (SC-04): every lib and tool of wave 4 is now ABSENT from the table -- zero by the
# default -- and harness_boundary.py holds at exactly two: `_as_repo_module_failure` (the load
# and call boundary) and `hook_guard` (the hook own-failure idiom, wired by FEAT-65).
#
# FEAT-65 (SC-04): the eleven hooks are gone from the table too. The budget is the two designed
# catches and nothing else; a broad catch anywhere else under bin/ is a finding by default.
BROAD_CATCH_CEILINGS = {
    "harness_boundary.py": 2,
}


def _is_broad_catch(handler):
    return handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id == "Exception")


def _parsed_program(text):
    """The index of `text` as a Python module when it is one and carries a try statement,
    else None. One level only: an embedded program's own strings are not programs."""
    try:
        inner = _SourceIndex(ast.parse(text))
    except (SyntaxError, ValueError):
        return None
    return inner if inner.facts["tries"] else None


def _may_be_program(node):
    """A string constant that could hold a try statement — which cannot be written without both
    keywords, so a string lacking either is never parsed."""
    return (isinstance(node, ast.Constant) and isinstance(node.value, str)
            and "except" in node.value and "try" in node.value)


def _broad_count(index):
    return sum(1 for handler in index.facts["handlers"] if _is_broad_catch(handler))


def _broad_catch_count(path, session=None, relative=None):
    """Broad catches in one script by AST — its own handlers plus those of any executable Python
    it embeds as a string (`python3 -I -c`, `python3 -`), whose handlers are as real as its own
    (FEAT-65 c1, CR-01) — or None when it does not parse (its own finding). Prose and
    docstrings that pass `_may_be_program` still do not parse into a try and add nothing."""
    session = session or _AuditSession(os.path.dirname(path))
    try:
        index = session.index(path, relative or path)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None
    programs = [program for program in map(session.program, index.program_texts) if program is not None]
    return _broad_count(index) + sum(map(_broad_count, programs))


def _broad_catch_finding(rel, name, count):
    ceiling = BROAD_CATCH_CEILINGS.get(name, 0)
    if count is None:
        return f"{rel} broad-catch census cannot parse it (FEAT-63 SC-04)"
    if count <= ceiling:
        return None
    return (f"{rel} carries {count} broad catch(es) (`except Exception` or bare `except:`) against "
            f"ceiling {ceiling} — narrow the new one to the boundary's real error class "
            f"(FEAT-63 SC-04)")


def _census_names(root, census):
    bin_dir = os.path.join(root, BIN_REL)
    return [(absolute, os.path.relpath(absolute, bin_dir), relative) for absolute, relative in census]


def broad_catch_census_paths(root):
    """Every Python file the census scans, as (absolute, bin-relative name), in
    _reader_source_paths' walk order -- bin/*.py and every package beneath it (FEAT-69: the
    check_state/ files are ceiling-0 like the entry they came from; a ceiling is keyed by the
    bin-relative name, so a package file can never borrow a sibling's allowance)."""
    return [(absolute, name) for absolute, name, _rel in _census_names(root, _reader_source_paths(root))]


def _broad_catch_findings(session):
    findings = []
    for absolute, name, relative in _census_names(session.root, session.census()):
        count = _broad_catch_count(absolute, session, relative)
        finding = _broad_catch_finding(os.path.join(BIN_REL, name), name, count)
        if finding:
            findings.append(finding)
    return findings


def broad_catch_findings(root):
    """The census over every bin/ script and every check_state/ package file, in name order."""
    return _broad_catch_findings(_AuditSession(root))


def _feat62_findings(session):
    trees, findings = _checker_trees(session)
    if not trees:
        return findings
    for relative, index in trees:
        findings.extend(_module_body_findings(index, relative))
        findings.extend(_reparse_findings(index, relative))
    findings.extend(_reads_findings(trees))
    findings.extend(_authority_findings(trees, session.root))
    findings.extend(_posture_findings(session.root))
    findings.extend(_broad_catch_findings(session))
    return findings


def feat62_findings(root):
    """The three checker-structure rule families over check-state.py and every check_state/
    package file (FEAT-69), then the posture scan and the broad-catch census."""
    return _feat62_findings(_AuditSession(root))


def consolidation_findings(root):
    """Every FEAT-61 lock violation under bin/, as printable lines; empty on a clean tree.
    FEAT-2081: the FEAT-62 rules and the broad-catch census share this call's session, so a
    file every rule audits is still read, parsed and traversed once."""
    buckets = _lifecycle_buckets()
    session = _AuditSession(root)
    findings = []
    for absolute, relative in session.census():
        try:
            index = session.index(absolute, relative)
        except (OSError, UnicodeDecodeError, SyntaxError) as error:
            findings.append(f"{relative}::<module> source_parse: {error}")
            continue
        if relative != STATION_TABLE_REL:
            findings.extend(_feature_station_literal_findings(index, relative, buckets))
        # The loader lock matches the callee by NAME, so a source that never spells it cannot
        # produce a finding; skipping it there changes cost, not the answer.
        if "spec_from_file_location" in session.text(absolute):
            findings.extend(_module_loader_findings(index, relative))
    findings.extend(_feat62_findings(session))
    return findings


def _run_consolidation_audit(root):
    findings = consolidation_findings(root)
    for finding in findings:
        print(f"CONSOLIDATION {finding}")
    print(f"{len(findings)} consolidation finding(s) under bin/")
    return 1 if findings else 0
