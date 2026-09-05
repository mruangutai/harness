#!/usr/bin/env python3
"""One-shot and review-time census tools for FEAT-47."""
import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
KIND_DIRS = (ROOT / "tests/unit", ROOT / "tests/integration")
sys.path.insert(0, str(ROOT / ".claude/skills/harness/bin"))
from suite_layout import (  # noqa: E402
    AGNOSTIC_NAME_PATTERNS,
    DOCUMENTED_EXCEPTIONS,
    RESTRICTED_NAME_PATTERNS,
    SOURCE_EXTENSIONS,
    is_test_shaped,
)
RESIDUE_TOKENS = ("UNIT_SCRIPTS", "INTEGRATION_SCRIPTS", "check-kinds")
# Exactly three historical line exemptions, on purpose.
RESIDUE_EXEMPTIONS = (
    (".harness/harness/docs/DECISIONS.md", "Eight of twelve"),
    ("tests/manual/probe-omp-session-accessor.py", "It was first registered in"),
    ("tests/manual/suite-census.py", "RESIDUE_TOKENS"),
)

def tests():
    return sorted(p for d in KIND_DIRS for p in d.glob("test-*.py"))

def baseline(path):
    text=Path(path).read_text(); blocks=re.findall(r"```(?:text)?\n(.*?)\n```",text,re.S)
    rows={}
    for block in blocks:
        for line in block.splitlines():
            m=re.fullmatch(r"(test-.*\.py)\s+(\d+)",line.strip())
            if m: rows[m.group(1)]=int(m.group(2))
    return rows

def verdict(args):
    expected=baseline(args.baseline); deleted=set(args.deleted); bad=0; seen=set()
    for p in tests():
        r=subprocess.run([sys.executable,str(p)],cwd=ROOT,text=True,capture_output=True)
        count=0
        for line in (r.stdout+r.stderr).splitlines():
            fields=line.split()
            token=fields[0].rstrip(":") if fields else ""
            if token in {"ok","PASS","FAIL"} or line.startswith("not ok"): count+=1
        seen.add(p.name); exp=expected.get(p.name)
        print(f"{p.name} expected={exp if exp is not None else 'new'} actual={count} exit={r.returncode}")
        if r.returncode or (exp is not None and exp != count): bad+=1
    for name in sorted(set(expected)-seen-deleted): print(f"missing baseline file: {name}"); bad+=1
    return 1 if bad and args.strict else 0

def migration(args):
    names=subprocess.run(["git","ls-tree","-r","--name-only",args.base,".claude/skills/harness/bin/"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.splitlines()
    base={Path(x).name for x in names if re.fullmatch(r"test-.*\.py",Path(x).name)}
    print(f"base test count: {len(base)}")
    at_ref=subprocess.run(["git","ls-tree","-r","--name-only",args.base,"tests/unit","tests/integration"],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    if not base and "test-" in at_ref: print("base is after the migration; one-shot check cannot answer",file=sys.stderr); return 2
    if len(base)<args.floor: print(f"base floor {args.floor} not met",file=sys.stderr); return 1
    deleted=set(args.deleted); bad=0
    for name in sorted(base):
        hits=[d/name for d in KIND_DIRS if (d/name).exists()]
        if name in deleted and not hits: continue
        if len(hits)!=1: print(f"{name}: expected exactly one destination, got {hits}"); bad+=1
    return 1 if bad else 0


def _vocabulary_paths(ref):
    """Sorted (path, basename, agnostic, restricted) tuples matching either vocabulary tuple."""
    names = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref], cwd=ROOT, text=True,
        capture_output=True, check=True,
    ).stdout.splitlines()
    selected = []
    for path in names:
        basename = os.path.basename(path)
        agnostic = any(fnmatch.fnmatch(basename, p) for p in AGNOSTIC_NAME_PATTERNS)
        restricted = any(fnmatch.fnmatch(basename, p) for p in RESTRICTED_NAME_PATTERNS)
        if agnostic or restricted:
            selected.append((path, basename, agnostic, restricted))
    return sorted(selected, key=lambda entry: entry[0])


def _disposition(path, basename, agnostic, restricted, exception_paths):
    if path.startswith("tests/"):
        return "in-tests-tree"
    if path in exception_paths:
        return "documented-exception"
    if restricted and not agnostic and not is_test_shaped(path):
        return "out-of-vocabulary"
    return "violation"


def _measure(ref):
    exception_paths = {entry[0] for entry in DOCUMENTED_EXCEPTIONS}
    rows = []
    for path, basename, agnostic, restricted in _vocabulary_paths(ref):
        rows.append((path, _disposition(path, basename, agnostic, restricted, exception_paths)))
    return rows


def _read_note_rows(path):
    """Parse an --against note's single fenced block into a row set.

    Prints the exact refusal message and returns None for zero or 2+ blocks."""
    blocks = re.findall(r"```(?:text)?\n(.*?)\n```", Path(path).read_text(), re.S)
    if not blocks:
        print(f"note carries no fenced block: {path}", file=sys.stderr)
        return None
    if len(blocks) > 1:
        print(f"note carries {len(blocks)} fenced blocks, expected exactly 1: {path}", file=sys.stderr)
        return None
    rows = set()
    for line in blocks[0].splitlines():
        line = line.strip()
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) == 2:
            rows.add((fields[0], fields[1]))
    return rows


def _print_measurement(rows):
    for path, disposition in rows:
        print(f"{path}\t{disposition}")
    total = len(rows)
    outside = sum(1 for _, disposition in rows if disposition != "in-tests-tree")
    violations = sum(1 for _, disposition in rows if disposition == "violation")
    print(f"TOTAL {total} OUTSIDE {outside} VIOLATIONS {violations}")
    return violations


def _print_diff(rows, against):
    note_rows = _read_note_rows(against)
    if note_rows is None:
        return 2
    measured = set(rows)
    missing = sorted(measured - note_rows)
    extra = sorted(note_rows - measured)
    for path, disposition in missing:
        print(f"MISSING {path}\t{disposition}")
    for path, disposition in extra:
        print(f"EXTRA {path}\t{disposition}")
    return 1 if missing or extra else 0


def tree_audit(args):
    rows = _measure(args.ref)
    violations = _print_measurement(rows)
    if args.against:
        diff_status = _print_diff(rows, args.against)
        if diff_status == 2:
            return 2
        return 1 if diff_status or violations else 0
    return 1 if violations else 0

def residue(args):
    if any("/expertise/" in f"/{p}/" for p,_ in RESIDUE_EXEMPTIONS): print("expertise exemption refused"); return 1
    if args.ref:
        paths=subprocess.run(["git","ls-tree","-r","--name-only",args.ref],cwd=ROOT,text=True,capture_output=True,check=True).stdout.splitlines()
        read=lambda p: subprocess.run(["git","show",f"{args.ref}:{p}"],cwd=ROOT,text=True,capture_output=True).stdout
        source=f"ref {args.ref}"
    else:
        paths=subprocess.run(["git","ls-files","--cached","--others","--exclude-standard"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.splitlines(); read=lambda p:(ROOT/p).read_text(errors="replace") if (ROOT/p).is_file() else ""; source="working tree"
    print(f"reading {source}"); matches=[]; positive=0
    for path in paths:
        text=read(path)
        for n,line in enumerate(text.splitlines(),1):
            if any(t in line for t in RESIDUE_TOKENS):
                if path.startswith((".harness/notes/",".harness/harness/features/",".harness/logs/")): positive+=1; continue
                matches.append((path,n,line))
    if not positive: print("positive control empty"); return 1
    bad=0
    for path,n,line in matches:
        covered=any(path==p and frag in line for p,frag in RESIDUE_EXEMPTIONS)
        print(f"{'covered' if covered else 'LIVE'} {path}:{n}:{line}")
        bad += not covered
    for p,frag in RESIDUE_EXEMPTIONS:
        if not any(path==p and frag in line for path,_,line in matches): print(f"stale exemption: {p} {frag}"); bad+=1
    return 1 if bad else 0

def children(args):
    instrument = r'''
import json, os, runpy, shlex, subprocess, sys
seen = []
original_popen = subprocess.Popen.__init__
original_system = os.system
original_fork = getattr(os, "fork", None)
original_spawn = getattr(os, "posix_spawn", None)
def head(argv):
    if isinstance(argv, str):
        parts = shlex.split(argv)
        return parts[0] if parts else "<empty>"
    try:
        return str(argv[0])
    except (IndexError, TypeError):
        return "<empty>"
def popen(self, argv, *a, **kw):
    seen.append(head(argv))
    return original_popen(self, argv, *a, **kw)
def system(command):
    seen.append(head(command))
    return original_system(command)
def fork():
    seen.append("fork")
    return original_fork()
def spawn(path, argv, env, *a, **kw):
    seen.append(str(path))
    return original_spawn(path, argv, env, *a, **kw)
subprocess.Popen.__init__ = popen
os.system = system
if original_fork is not None:
    os.fork = fork
if original_spawn is not None:
    os.posix_spawn = spawn
try:
    runpy.run_path(sys.argv[1], run_name="__main__")
except SystemExit:
    pass
except BaseException as exc:
    seen.append("<test-error:" + type(exc).__name__ + ">")
finally:
    print("__CHILD_CENSUS__" + json.dumps(seen))
'''
    for path in tests():
        result = subprocess.run(
            [sys.executable, "-c", instrument, str(path)], cwd=ROOT,
            text=True, capture_output=True)
        marker = next(
            (line.removeprefix("__CHILD_CENSUS__")
             for line in reversed(result.stdout.splitlines())
             if line.startswith("__CHILD_CENSUS__")),
            None)
        names = json.loads(marker) if marker is not None else ["<instrument-failed>"]
        rendered = " ".join(names) if names else "-"
        print(f"{path.name} children={len(names)} names={rendered}")
    return 0

def add_verdict_parser(subparsers):
    parser = subparsers.add_parser("verdict-lines")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--deleted", action="append", default=[])
    parser.add_argument("--strict", action="store_true")
    parser.set_defaults(fn=verdict)


def add_migration_parser(subparsers):
    parser = subparsers.add_parser("migration")
    parser.add_argument("--base", required=True)
    parser.add_argument("--floor", type=int, required=True)
    parser.add_argument("--deleted", action="append", default=[])
    parser.set_defaults(fn=migration)


def add_residue_parser(subparsers):
    parser = subparsers.add_parser("residue")
    parser.add_argument("--ref")
    parser.set_defaults(fn=residue)


def add_children_parser(subparsers):
    parser = subparsers.add_parser("children")
    parser.set_defaults(fn=children)


def add_tree_audit_parser(subparsers):
    parser = subparsers.add_parser("tree-audit")
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--against")
    parser.set_defaults(fn=tree_audit)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    add_verdict_parser(subparsers)
    add_migration_parser(subparsers)
    add_residue_parser(subparsers)
    add_children_parser(subparsers)
    add_tree_audit_parser(subparsers)
    args = parser.parse_args()
    return args.fn(args)
if __name__=="__main__": raise SystemExit(main())
