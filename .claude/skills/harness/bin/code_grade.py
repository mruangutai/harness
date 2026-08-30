#!/usr/bin/env python3
"""Pure source grading using ABC, cyclomatic, and a Sonar-style approximation."""
from __future__ import annotations

import ast
import hashlib
import subprocess
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from math import sqrt


@dataclass(frozen=True)
class FunctionGrade:
    qualname: str
    lineno: int
    cyclomatic: int
    cognitive: int
    abc_a: int
    abc_b: int
    abc_c: int
    abc: float
    grade: int
    driver: str
    path: str



def _band(value, limits):
    for grade, limit in limits:
        if value <= limit:
            return grade
    return 1


def _grade(cyclomatic, cognitive, abc):
    metrics = (
        ("cyclomatic", _band(cyclomatic, ((5, 4), (4, 8), (3, 10), (2, 20)))),
        ("cognitive", _band(cognitive, ((5, 3), (4, 9), (3, 15), (2, 30)))),
        ("abc", _band(abc, ((5, 8), (4, 20), (3, 26), (2, 45)))),
    )
    grade = min(value for _, value in metrics)
    return grade, "+".join(name for name, value in metrics if value == grade)


def _round_abc(a, b, c):
    value = Decimal(str(sqrt(a * a + b * b + c * c)))
    return float(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def _is_wildcard(case):
    return isinstance(case.pattern, ast.MatchAs) and case.pattern.name is None


class _Counter(ast.NodeVisitor):
    def __init__(self, qualname):
        self.qualname = qualname
        self.cyclomatic = 1
        self.cognitive = 0
        self.a = 0
        self.b = 0
        self.c = 0
        self.depth = 0

    def _decision(self, cognitive=True, nested=True):
        self.cyclomatic += 1
        self.c += 1
        if cognitive:
            self.cognitive += 1 + self.depth
        if nested:
            self.depth += 1

    def _visit_block(self, statements):
        for statement in statements:
            self.visit(statement)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.a += 1

    def visit_Call(self, node):
        self.b += 1
        self.generic_visit(node)

    def visit_Assign(self, node):
        self._visit_block(node.targets)
        self.visit(node.value)

    def visit_AnnAssign(self, node):
        self.visit(node.target)
        if node.value is not None:
            self.visit(node.value)

    def visit_AugAssign(self, node):
        self.visit(node.target)
        self.visit(node.value)

    def visit_NamedExpr(self, node):
        self.visit(node.target)
        self.visit(node.value)

    def visit_Import(self, node):
        self.a += len(node.names)

    def visit_ImportFrom(self, node):
        self.a += len(node.names)

    def visit_FunctionDef(self, node):
        self.a += 1

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.a += 1

    def visit_For(self, node):
        self._decision()
        self.visit(node.target)
        self.visit(node.iter)
        self._visit_block(node.body)
        self._visit_block(node.orelse)
        self.depth -= 1

    visit_AsyncFor = visit_For

    def visit_While(self, node):
        self._decision()
        self.visit(node.test)
        self._visit_block(node.body)
        self._visit_block(node.orelse)
        self.depth -= 1

    def visit_If(self, node):
        is_elif = isinstance(node.parent, ast.If) and node in node.parent.orelse
        self._decision(cognitive=not is_elif, nested=not is_elif)
        self.visit(node.test)
        self._visit_block(node.body)
        if node.orelse and not is_elif:
            self.cognitive += 1
        self._visit_block(node.orelse)
        if not is_elif:
            self.depth -= 1

    def visit_IfExp(self, node):
        self.c += 1
        self.cognitive += 1 + self.depth
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)

    def visit_With(self, node):
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars is not None:
                self.visit(item.optional_vars)
        self.depth += 1
        self._visit_block(node.body)
        self.depth -= 1

    visit_AsyncWith = visit_With

    def visit_Try(self, node):
        self._visit_block(node.body)
        for handler in node.handlers:
            self._decision()
            self.a += int(handler.name is not None)
            if handler.type is not None:
                self.visit(handler.type)
            self._visit_block(handler.body)
            self.depth -= 1
        if node.finalbody:
            self.cognitive += 1
            self._visit_block(node.finalbody)
        self._visit_block(node.orelse)

    def visit_Assert(self, node):
        self.cyclomatic += 1
        self.c += 1
        self.visit(node.test)
        if node.msg is not None:
            self.visit(node.msg)

    def visit_BoolOp(self, node):
        self.cyclomatic += len(node.values) - 1
        self.c += len(node.values) - 1
        self.cognitive += 1 + self.depth
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.c += len(node.ops)
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        self.c += int(isinstance(node.op, ast.Not))
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self._visit_comprehension(node)

    visit_SetComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp
    visit_DictComp = visit_ListComp

    def _visit_comprehension(self, node):
        for generator in node.generators:
            self.cyclomatic += 1
            self.visit(generator.target)
            self.visit(generator.iter)
            for condition in generator.ifs:
                self.cyclomatic += 1
                self.c += 1
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
        self.visit(node.elt if not isinstance(node, ast.DictComp) else node.value)

    def visit_Match(self, node):
        self.visit(node.subject)
        for case in node.cases:
            self.c += 1
            if not _is_wildcard(case):
                self.cyclomatic += 1
            self._visit_block(case.body)


def _attach_parents(tree):
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent


def _child_qualname(child, prefix):
    if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return None
    return f"{prefix}.{child.name}" if prefix else child.name


def _records(tree, path):
    records = []

    def collect(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            qualname = _child_qualname(child, prefix)
            if qualname is None:
                continue
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                records.append(_record(child, qualname, path))
            collect(child, qualname)

    collect(tree)
    return records


def _record(node, qualname, path):
    counter = _Counter(qualname)
    for decorator in node.decorator_list:
        counter.b += int(isinstance(decorator, ast.Name))
    counter._visit_block(node.body)
    if _calls_self(node, qualname):
        counter.cognitive += 1
    abc = _round_abc(counter.a, counter.b, counter.c)
    grade, driver = _grade(counter.cyclomatic, counter.cognitive, abc)
    return FunctionGrade(qualname, node.lineno, counter.cyclomatic, counter.cognitive,
                         counter.a, counter.b, counter.c, abc, grade, driver, path)


def _calls_self(node, qualname):
    return any(isinstance(child, ast.Call) and _call_name(child.func) == qualname.split(".")[-1]
               for child in ast.walk(node) if child is not node)


def _call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def grade_source(source_text, path):
    """Return source-ordered FunctionGrade records for Python source_text and path."""
    tree = ast.parse(source_text)
    _attach_parents(tree)
    return _records(tree, path)




def commit_oid(repo_root, revision):
    if not isinstance(revision, str) or revision.startswith("-"):
        raise ValueError(f"invalid Git commit revision: {revision}")
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", "--end-of-options",
         f"{revision}^{{commit}}"],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"invalid Git commit revision: {revision}")
    return result.stdout.strip()


def _git_output(repo_root, *args):
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def _git_show(repo_root, ref, path):
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{path}"],
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return result.stdout
    if "exists on disk, but not in" in result.stderr:
        return None
    raise RuntimeError(result.stderr.strip())


def _next_paths(status, fields):
    if status.startswith("R"):
        return next(fields), next(fields)
    return None, next(fields)


def _changed_python_files(repo_root, base_ref, head_ref):
    changed = []
    output = _git_output(repo_root, "diff", "--find-renames", "--name-status", "-z",
                         base_ref, head_ref)
    fields = iter(output.split("\0"))
    for status in fields:
        if not status:
            continue
        old_path, path = _next_paths(status, fields)
        if not status.startswith("D") and path.endswith(".py"):
            changed.append((path, old_path))
    return changed


def _qualname(prefix, name):
    return f"{prefix}.{name}" if prefix else name


def _strip_docstring(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(
            body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        return body[1:]
    return body


def _hash_body(node):
    source = "\n".join(ast.unparse(statement) for statement in _strip_docstring(node.body))
    return hashlib.sha256(source.encode()).hexdigest()


def _body_hashes(source_text):
    hashes = {}

    def collect(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualname = _qualname(prefix, child.name)
                hashes[qualname] = _hash_body(child)
                collect(child, qualname)
            elif isinstance(child, ast.ClassDef):
                collect(child, _qualname(prefix, child.name))

    collect(ast.parse(source_text))
    return hashes


def _pre_images(source_text):
    records = grade_source(source_text, "")
    by_name = {record.qualname: record for record in records}
    by_hash = {}
    for qualname, body_hash in _body_hashes(source_text).items():
        by_hash.setdefault(body_hash, []).append(by_name[qualname])
    return by_name, by_hash


def _resolve_base_source(repo_root, base_oid, path, old_path):
    base_source = _git_show(repo_root, base_oid, path)
    if base_source is None and old_path is not None:
        base_source = _git_show(repo_root, base_oid, old_path)
    return base_source


def _resolve_pre_image(record, before_names, before_hashes, head_hashes):
    before = before_names.get(record.qualname)
    if before is not None:
        return before
    matches = before_hashes.get(head_hashes[record.qualname], [])
    return matches[0] if matches else None


def _gate_file_records(repo_root, base_oid, head_oid, path, old_path):
    head_source = _git_show(repo_root, head_oid, path)
    base_source = _resolve_base_source(repo_root, base_oid, path, old_path)
    before_names, before_hashes = _pre_images(base_source) if base_source else ({}, {})
    head_hashes = _body_hashes(head_source)
    gated = []
    informational = []
    for record in grade_source(head_source, path):
        before = _resolve_pre_image(record, before_names, before_hashes, head_hashes)
        if before is None or record.grade < before.grade:
            gated.append(record)
        else:
            informational.append(record)
    return gated, informational


def gated_set(repo_root, base_ref, head_ref):
    """Return changed functions requiring a gate and changed informational functions."""
    gated = []
    informational = []
    base_oid = commit_oid(repo_root, base_ref)
    head_oid = commit_oid(repo_root, head_ref)
    for path, old_path in _changed_python_files(repo_root, base_oid, head_oid):
        file_gated, file_informational = _gate_file_records(
            repo_root, base_oid, head_oid, path, old_path)
        gated.extend(file_gated)
        informational.extend(file_informational)
    return gated, informational
