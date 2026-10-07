#!/usr/bin/env python3
"""FEAT-2081 SC-06: the structure audits' per-file AST index and its per-invocation session.

The index is one breadth-first, parent-aware traversal of a parsed tree; each fact list it
fills must be exactly what the replaced `ast.walk` scans returned, in the same order, and a
subtree question must answer exactly as `ast.walk(subject)` would. The session is built fresh
per public audit call: nothing it read survives into the next call or crosses to another root.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import ast
import importlib.util
import os
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_REL = os.path.join(".claude", "skills", "harness", "bin")
SCRIPT = os.environ.get("CHECK_PLAN_ROUTES_BIN") or os.path.join(ROOT, BIN_REL, "check-plan-routes.py")

SOURCE = '''
import subprocess
PROGRAM = "try:\\n    pass\\nexcept Exception:\\n    pass\\n"
PROSE = "try this, except when it rains"

def outer(ctx):
    def inner():
        return frozenset(("plan", "build"))
    subprocess.run(["git", "status"])
    return open(f"{ctx}/BRIEF.md" + "x.json")

class Ctx:
    async def method(self):
        try:
            ctx.spawn(["gh", "auth", "status"])
        except Exception:
            pass
        except:
            pass
'''

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name}{'' if cond else ' ' + detail}")
    if not cond:
        failures.append(name)


def cpr():
    spec = importlib.util.spec_from_file_location("_cpr_index_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _walk_parents(tree):
    return {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}


def case_index_facts_match_ast_walk(mod):
    tree = ast.parse(SOURCE)
    index = mod._SourceIndex(tree)
    walked = list(ast.walk(tree))
    check("index_nodes_are_ast_walk_order", index.nodes == walked)
    parents = _walk_parents(tree)
    check("index_parent_links_match", all(index.parent[n] is parents.get(n) for n in walked))
    expected = {
        "functions": [n for n in walked if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))],
        "calls": [n for n in walked if isinstance(n, ast.Call)],
        "handlers": [n for n in walked if isinstance(n, ast.ExceptHandler)],
        "tries": [n for n in walked if isinstance(n, ast.Try)],
        "literal_candidates": [n for n in walked if isinstance(n, mod._LITERAL_CANDIDATES)],
    }
    for kind, nodes in expected.items():
        check(f"index_{kind}_match_ast_walk", index.facts[kind] == nodes, f"{len(index.facts[kind])} vs {len(nodes)}")
    programs = [n.value for n in walked if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and "try" in n.value and "except" in n.value]
    check("index_program_texts_are_the_try_except_strings", index.program_texts == programs, repr(index.program_texts))


def case_subtree_queries_match_ast_walk(mod):
    tree = ast.parse(SOURCE)
    index = mod._SourceIndex(tree)
    subjects = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Call))]
    subjects += list(tree.body)
    for kind in (ast.Call, ast.Constant):
        same = all(list(index.within(s, kind)) == [n for n in ast.walk(s) if isinstance(n, kind)] for s in subjects)
        check(f"within_{kind.__name__}_equals_ast_walk_of_the_subject", same)
    outer = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    check("input_literals_skip_fstring_parts", mod._input_literals(index, outer) == {"x.json"},
          repr(mod._input_literals(index, outer)))
    check("observed_resources_read_the_spawned_argv", mod._observed_inputs(index, outer)[1] == {"git:status"})
    method = index.facts["functions"][-1]
    check("called_names_map_ctx_methods", mod._called_names(index, method) == ["Ctx.spawn"],
          repr(mod._called_names(index, method)))
    frozen = next(c for c in index.facts["calls"] if mod._callee_name(c) == "frozenset")
    check("call_symbol_is_the_innermost_function", mod._call_symbol(index, frozen) == "inner")


def case_embedded_programs_count_once(mod):
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "carrier.py")
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(SOURCE)
        check("broad_count_is_own_handlers_plus_embedded_program", mod._broad_catch_count(path) == 3,
              repr(mod._broad_catch_count(path)))
        session = mod._AuditSession(td)
        text = mod._SourceIndex(ast.parse(SOURCE)).program_texts[0]
        first = session.program(text)
        check("session_parses_an_embedded_program_once", first is not None and session.program(text) is first)
        check("prose_with_both_keywords_is_not_a_program", session.program("try this, except when it rains") is None)


def case_session_caches_once_and_keeps_errors(mod):
    with tempfile.TemporaryDirectory() as td:
        good, bad = os.path.join(td, "good.py"), os.path.join(td, "bad.py")
        for path, text in ((good, "x = 1\n"), (bad, "def (:\n")):
            with open(path, "w", encoding="utf-8") as stream:
                stream.write(text)
        session = mod._AuditSession(td)
        check("session_index_is_built_once_per_file", session.index(good, "good.py") is session.index(
            os.path.join(td, ".", "good.py"), "good.py"))
        errors = []
        for _ in range(2):
            try:
                session.index(bad, "bad.py")
            except SyntaxError as error:
                errors.append(error)
        check("session_reraises_the_same_parse_error_to_every_asker",
              len(errors) == 2 and errors[0] is errors[1] and "bad.py" in str(errors[0]), repr(errors))
        missing = os.path.join(td, "absent.py")
        try:
            session.text(missing)
            check("session_text_raises_for_an_absent_file", False)
        except OSError:
            check("session_text_raises_for_an_absent_file", True)


def _root_with_bin(td, text):
    bin_dir = os.path.join(td, BIN_REL)
    os.makedirs(bin_dir)
    with open(os.path.join(bin_dir, "probe.py"), "w", encoding="utf-8") as stream:
        stream.write(text)
    return td


_BROAD = "try:\n    pass\nexcept Exception:\n    pass\n"


def case_each_invocation_is_fresh(mod):
    with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two:
        _root_with_bin(one, "x = 1\n")
        _root_with_bin(two, _BROAD)
        check("clean_root_has_no_broad_catch_finding", mod.broad_catch_findings(one) == [])
        found = mod.broad_catch_findings(two)
        check("second_root_is_audited_from_its_own_sources", len(found) == 1 and "probe.py" in found[0], repr(found))
        check("first_root_is_still_clean_after_the_second", mod.broad_catch_findings(one) == [])
        with open(os.path.join(one, BIN_REL, "probe.py"), "w", encoding="utf-8") as stream:
            stream.write(_BROAD)
        check("an_edit_between_invocations_is_seen", len(mod.broad_catch_findings(one)) == 1)
    leaked = [name for name, value in vars(mod).items()
              if isinstance(value, (mod._AuditSession, mod._SourceIndex))]
    check("no_session_or_index_is_retained_at_module_scope", leaked == [], repr(leaked))


def main():
    mod = cpr()
    for case in (case_index_facts_match_ast_walk, case_subtree_queries_match_ast_walk,
                 case_embedded_programs_count_once, case_session_caches_once_and_keeps_errors,
                 case_each_invocation_is_fresh):
        case(mod)
    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
