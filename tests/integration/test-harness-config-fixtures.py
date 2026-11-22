#!/usr/bin/env python3
"""FEAT-2297 D-06: fixture census — every valid harness.json producer reaches the one builder.

    test-harness-config-fixtures.py [source ...]

With no arguments the population is every tracked test source (`git ls-files tests`, .py and
.ts), derived here and never from a plan's file list; arguments bound the files examined. The
bypass negative controls always run.

A PRODUCER is any site that puts harness.json content somewhere a reader will find it: a raw write
to a path naming harness.json (open/write, json.dump, write_text — directly, through a variable,
or through a helper function that raw-writes its parameter), a `".../harness.json": content`
mapping entry, a remote `product_configs=` payload, and in TypeScript an inline writeFileSync of
harness.json. A producer REACHES THE BUILDER when its written value is, or resolves through names
and module constants (imported ones included) to, a build_config/write_config result — so a
valid-base-plus-corruption case passes because its base was built. Anything else is a bypass
unless CLASSIFIED below with evidence. Site ids follow the canonical reader audit's convention:
`file::symbol::kind#n`.
"""
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from harness_config_support import build_config  # noqa: E402

HELPERS = {"build_config", "write_config"}
HELPER_MODULE = "tests/harness_config_support.py"
BUDGET_FIXTURE = "tests/fixtures/harness-config-budgets.json"
TS_SOURCE = "tests/unit/omp-hooks.test.ts"
# Not producers of a valid config, though the scan cannot tell: id -> evidence.
CLASSIFIED = {
    "tests/unit/test-artifact-accessors.py::JsonContracts.test_nonfinite_json_constants_are_rejected::raw-write#1":
        "non-config: NaN/Infinity text that tests the strict decoder, not a config; the signed inventory "
        "keeps tests/unit/test-artifact-accessors.py:56-62 UNAFFECTED as the one centralized decode contract",
}


def budget_configs():
    return {"default": build_config(),
            "context_150000": build_config({"budgets": {"orchestrator_context_warn_tokens": 150000}}),
            "plan_30": build_config({"budgets": {"plan_phase_warn_minutes": 30}})}


def budget_expectation():
    """The checked-in entries: each builder config cut to the version and budgets that TypeScript
    reads. Every other key is a schema default, so the cut loads back to the identical config."""
    return {key: {"schema_version": config["schema_version"], "budgets": config["budgets"]}
            for key, config in budget_configs().items()}


def _names_config(text):
    return isinstance(text, str) and text.endswith("harness.json")


class _Module:
    """One Python source: its scopes' assignments, imports and the writers it defines."""

    def __init__(self, relative, source):
        self.relative, self.tree = relative, ast.parse(source, filename=relative)
        self.parents = {child: node for node in ast.walk(self.tree) for child in ast.iter_child_nodes(node)}
        self.imports = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for item in node.names:
                    self.imports[item.asname or item.name] = (node.module, item.name)

    def scope_of(self, node):
        while node in self.parents:
            node = self.parents[node]
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return node
        return self.tree

    def symbol(self, node):
        names = []
        while node in self.parents:
            node = self.parents[node]
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(node.name)
        return ".".join(reversed(names)) or "<module>"

    def assigned(self, name, scope):
        """Values bound to `name` in `scope`, falling back to the module's own top level."""
        for where in (scope, self.tree) if scope is not self.tree else (self.tree,):
            values = [node.value for node in ast.walk(where) if isinstance(node, (ast.Assign, ast.AnnAssign))
                      and node.value is not None and self.scope_of(node) is where
                      and any(isinstance(t, ast.Name) and t.id == name
                              for t in (node.targets if isinstance(node, ast.Assign) else [node.target]))]
            if values:
                return values
        return []


def _into(call, handle):
    """True when `call` is `handle.write(...)` or `json.dump(value, handle)`."""
    if call.func.attr == "write":
        target = call.func.value
    else:
        target = call.args[1] if call.func.attr == "dump" and len(call.args) > 1 else None
    return isinstance(target, ast.Name) and target.id == handle


def _handle_write(block, handle):
    """The value a `with open(...) as handle` block writes or dumps into `handle`, or None."""
    for node in ast.walk(block):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.args and _into(node, handle):
            return node.args[0]
    return None


class Census:
    def __init__(self, sources):
        self.modules, self.ts, self.findings = {}, {}, []
        for relative, text in sources.items():
            if relative.endswith(".ts"):
                self.ts[relative] = text
                continue
            try:
                self.modules[relative] = _Module(relative, text)
            except SyntaxError as error:
                self.findings.append(f"{relative}: cannot be parsed, so its producers are unknown ({error})")
        self.by_name = {Path(r).stem: m for r, m in self.modules.items()}
        self.writers = {}
        for module in self.modules.values():
            for path, value, node in self._raw_writes(module):
                self._record_writer(module, path, value, node)

    def _record_writer(self, module, path, value, node):
        """(module, function) -> (path index, path parameter, content index, content parameter,
        own value) for a function that raw-writes to a path parameter. A write of an expression
        over a parameter is checked at each call site's argument; a write of anything else is the
        helper's own value, checked in the helper's own module."""
        scope = module.scope_of(node)
        params = [a.arg for a in scope.args.args] if hasattr(scope, "args") else []
        at = next((n.id for n in ast.walk(path) if isinstance(n, ast.Name) and n.id in params), None) if path else None
        if at is None:
            return
        content = [n.id for n in ast.walk(value) if isinstance(n, ast.Name)
                   and n.id in params and n.id != at] if value is not None else []
        self.writers[(module.relative, scope.name)] = (
            (params.index(at), at, params.index(content[0]), content[0], None)
            if content else (params.index(at), at, None, None, (module, value)))

    def _writer(self, module, func):
        """The writer a call reaches: defined here, imported by name, or called as `module.helper`."""
        if isinstance(func, ast.Name):
            origin = module.imports.get(func.id)
            other = origin and self.by_name.get(origin[0].rsplit(".", 1)[-1])
            return self.writers.get((module.relative, func.id)) or (
                other and self.writers.get((other.relative, origin[1])))
        other = isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and self.by_name.get(func.value.id)
        return other and self.writers.get((other.relative, func.attr))

    # --- what a site writes, and where -------------------------------------------------------
    def _raw_writes(self, module):
        """(path expression, value expression or None, node) for every raw file write."""
        for node in ast.walk(module.tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in ("write_text", "write_bytes") and node.args:
                yield func.value, node.args[0], node
            elif isinstance(func, ast.Name) and func.id == "open" and self._writable(node):
                yield node.args[0] if node.args else None, self._written_through(module, node), node

    @staticmethod
    def _writable(call):
        mode = call.args[1] if len(call.args) > 1 else next(
            (k.value for k in call.keywords if k.arg == "mode"), None)
        return isinstance(mode, ast.Constant) and isinstance(mode.value, str) and set(mode.value) & set("wa")

    @staticmethod
    def _written_through(module, call):
        parent = module.parents.get(call)
        if isinstance(parent, ast.Attribute) and parent.attr == "write":
            return module.parents[parent].args[0]
        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute) and parent.func.attr == "dump":
            return parent.args[0]
        if isinstance(parent, ast.withitem) and isinstance(parent.optional_vars, ast.Name):
            return _handle_write(module.parents[parent], parent.optional_vars.id)
        return None

    # --- name resolution -----------------------------------------------------------------------
    def _resolve(self, module, node, test, seen=None):
        """True when `test` holds for `node` or for anything it resolves to through names."""
        seen = seen if seen is not None else set()
        for sub in ast.walk(node):
            if test(sub):
                return True
            if isinstance(sub, ast.Name) and (module.relative, sub.id) not in seen:
                seen.add((module.relative, sub.id))
                if any(self._resolve(owner, value, test, seen) for owner, value in self._values_of(module, sub)):
                    return True
        return False

    def _values_of(self, module, name):
        """(module, expression) for every value `name` is assigned here or in the module it is imported from."""
        yield from ((module, value) for value in module.assigned(name.id, module.scope_of(name)))
        origin = module.imports.get(name.id)
        other = origin and self.by_name.get(origin[0].rsplit(".", 1)[-1])
        if other:
            yield from ((other, value) for value in other.assigned(origin[1], other.tree))

    def _mentions_config(self, module, node):
        return node is not None and self._resolve(
            module, node, lambda n: isinstance(n, ast.Constant) and _names_config(n.value))

    def _reaches(self, module, node):
        def helper_call(n):
            if not isinstance(n, ast.Call):
                return False
            name = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", None)
            return name in HELPERS
        return node is not None and self._resolve(module, node, helper_call)

    # --- producers -----------------------------------------------------------------------------
    def producers(self, module):
        """(kind, node, value) for every harness.json producer in `module`."""
        if module.relative == HELPER_MODULE:
            return
        for path, value, node in self._raw_writes(module):
            if self._mentions_config(module, path):
                yield "raw-write", node, value
        for node in ast.walk(module.tree):
            if isinstance(node, ast.Dict):
                yield from self._mapping_entries(node)
            elif isinstance(node, ast.Call):
                yield from self._remote_payloads(node)
                yield from self._indirect_writes(module, node)

    @staticmethod
    def _mapping_entries(node):
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and _names_config(key.value):
                yield "mapping-entry", node, value

    @staticmethod
    def _remote_payloads(node):
        for keyword in (k for k in node.keywords if k.arg == "product_configs"):
            payloads = keyword.value.values if isinstance(keyword.value, ast.Dict) else [keyword.value]
            yield from (("remote-payload", node, value) for value in payloads)

    def _indirect_writes(self, module, node):
        writer = self._writer(module, node.func)
        if not writer:
            return
        path_at, path_name, value_at, value_name, own = writer
        args = {**dict(enumerate(node.args)), **{k.arg: k.value for k in node.keywords}}
        if self._mentions_config(module, args.get(path_at, args.get(path_name))):
            yield "indirect-write", node, own or (module, args.get(value_at, args.get(value_name)))

    def run(self):
        for relative in sorted(self.modules):
            module, ordinals = self.modules[relative], {}
            for kind, node, value in self.producers(module):
                source, value = value if isinstance(value, tuple) else (module, value)
                key = (module.symbol(node), kind)
                ordinals[key] = ordinals.get(key, 0) + 1
                site = f"{relative}::{key[0]}::{kind}#{ordinals[key]}"
                if not self._reaches(source, value) and site not in CLASSIFIED:
                    self.findings.append(f"{site} (line {node.lineno}): a harness.json producer that "
                                         "does not reach build_config/write_config")
        for relative, text in sorted(self.ts.items()):
            self.findings += _ts_findings(relative, text)
        return self.findings


def _ts_findings(relative, text):
    fixtures = set(re.findall(r"(?:const|let)\s+(\w+)\s*=[^;]*harness-config-budgets\.json", text))
    return [f"{relative}::writeFileSync#{number}: an inline TypeScript harness.json that is not read "
            "from the checked-in budget fixture"
            for number, call in enumerate(_ts_calls(text, "writeFileSync"), 1)
            if "harness.json" in call and not any(re.search(rf"\b{name}\b", call) for name in fixtures)]


def _ts_calls(text, name):
    """The full argument text of every `name(` call, by bracket balance."""
    for match in re.finditer(rf"\b{name}\(", text):
        depth, at = 1, match.end()
        while depth and at < len(text):
            depth += {"(": 1, ")": -1}.get(text[at], 0)
            at += 1
        yield text[match.end():at - 1]


def budget_fixture_findings(text):
    try:
        actual = json.loads(text)
    except ValueError as error:
        return [f"{BUDGET_FIXTURE}: not JSON ({error})"]
    expected = budget_expectation()
    findings = [f"{BUDGET_FIXTURE}: `{key}` does not load to the builder's config"
                for key, config in budget_configs().items() if build_config(expected[key]) != config]
    return findings + [f"{BUDGET_FIXTURE}: `{key}` is missing or stale against build_config" for key in expected
                       if actual.get(key) != expected[key]] + [
            f"{BUDGET_FIXTURE}: `{key}` is not a generated entry" for key in actual if key not in expected]


def population(arguments):
    if arguments:
        return [os.path.relpath(os.path.abspath(a), ROOT) for a in arguments]
    listed = subprocess.run(["git", "ls-files", "tests"], cwd=ROOT, capture_output=True, text=True, check=True)
    return sorted(p for p in listed.stdout.split() if p.endswith((".py", ".ts")) or p == BUDGET_FIXTURE)


def census(paths):
    sources = {p: (ROOT / p).read_text(encoding="utf-8") for p in paths if p != BUDGET_FIXTURE}
    findings = Census(sources).run()
    if TS_SOURCE in paths or BUDGET_FIXTURE in paths:
        fixture = ROOT / BUDGET_FIXTURE
        findings += (budget_fixture_findings(fixture.read_text(encoding="utf-8")) if fixture.is_file()
                     else [f"{BUDGET_FIXTURE}: missing — the TypeScript budget configs must be generated"])
    return findings


# --- negative controls: each must be reported -------------------------------------------------
BYPASSES = {
    "new inline bypass": ("tests/unit/test-new.py", """
import os
def test(tmp):
    with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
        f.write('{"schema_version": 3}')
"""),
    "inherited make_fixture writes its raw parameter": ("tests/integration/check_state_support.py", """
import os
def make_fixture(tmp, harness_json, parent_line):
    with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
        f.write(harness_json)
"""),
    "inherited constant written by a caller": ("tests/integration/test-caller.py", """
from check_state_support import HARNESS_JSON_SYNC_OFF
def test(path):
    with open(path + "/.harness/harness.json", "w") as f:
        f.write(HARNESS_JSON_SYNC_OFF)
""", ("tests/integration/check_state_support.py", 'HARNESS_JSON_SYNC_OFF = """{"github": {"sync": false}}"""\n')),
    "inherited _owner_files mapping entry": ("tests/integration/f58_sparse_fixture.py", """
def _owner_files():
    return {"README.md": "owner\\n", ".harness/harness.json": "{}\\n"}
"""),
    "inherited stage json.dump": ("tests/integration/gh_sync_support.py", """
import json, os
def stage(tmp, sync=True):
    g = {"sync": sync, "board": None}
    json.dump({"github": g}, open(os.path.join(tmp, ".harness", "harness.json"), "w"))
"""),
    "inherited stage_fleet remote payload": ("tests/integration/gh_sync_support.py", """
def stage_fleet(tmp):
    product = {"github": {"sync": True, "repo": "product/app"}}
    install_gh(tmp, "script", product_configs={"product/app@release": product})
"""),
    "helper that raw-writes its parameter": ("tests/integration/test-indirect.py", """
from pathlib import Path
def put(path, text):
    Path(path).write_text(text)
def test(tmp):
    put(tmp + "/.harness/harness.json", "{}")
"""),
    "helper that raw-writes an expression of its parameter": ("tests/integration/test-ifexp.py", """
import json
def write(path, content):
    with open(path, "w") as stream:
        stream.write(content if isinstance(content, str) else json.dumps(content))
def test(tmp):
    write(tmp + "/.harness/harness.json", {"github": {"sync": True}})
"""),
    "helper that raw-writes its own literal to its path parameter": ("tests/integration/test-own.py", """
import json
def write_review_config(config, review):
    with open(config, "w") as f:
        json.dump({"gates": {"review": review}}, f)
def test(tmp):
    write_review_config(tmp + "/.harness/harness.json", "strict")
"""),
    "inline TypeScript config": ("tests/unit/new.test.ts",
                                 'writeFileSync(join(dir, "harness.json"), JSON.stringify({ budgets }));\n'),
}
ROUTED = ("tests/integration/test-routed.py", """
import json, os
from harness_config_support import build_config, write_config
def test(tmp):
    write_config(os.path.join(tmp, ".harness", "harness.json"), {"github": {"sync": False}})
    broken = build_config()
    broken["gates"]["review"] = "strict"
    with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
        f.write(json.dumps(broken))
def seed(path):
    with open(path, "w") as f:
        f.write(json.dumps(build_config()))
def test_seed(tmp):
    seed(os.path.join(tmp, ".harness", "harness.json"))
""")


def negative_control_failures():
    failures = []
    for name, (relative, source, *extra) in BYPASSES.items():
        if not Census({relative: source, **dict(extra)}).run():
            failures.append(f"negative control not detected: {name}")
    if Census({ROUTED[0]: ROUTED[1]}).run():
        failures.append("a builder-routed write (with valid-base corruption) was reported as a bypass")
    drifted = budget_expectation()
    drifted["plan_30"]["budgets"]["plan_phase_warn_minutes"] = 31
    if not budget_fixture_findings(json.dumps(drifted)) or budget_fixture_findings(json.dumps(budget_expectation())):
        failures.append("the budget fixture comparison does not separate a drift mutant from the generated mapping")
    return failures


def main(arguments):
    failures = negative_control_failures() + census(population(arguments))
    for failure in failures:
        print(f"FAIL  {failure}")
    print(f"{len(failures)} finding(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
