#!/usr/bin/env python3
"""One-shot and review-time census tools for FEAT-47."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
KIND_DIRS = (ROOT / "tests/unit", ROOT / "tests/integration")
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

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("verdict-lines"); p.add_argument("--baseline",required=True); p.add_argument("--deleted",action="append",default=[]); p.add_argument("--strict",action="store_true"); p.set_defaults(fn=verdict)
    p=sp.add_parser("migration"); p.add_argument("--base",required=True); p.add_argument("--floor",type=int,required=True); p.add_argument("--deleted",action="append",default=[]); p.set_defaults(fn=migration)
    p=sp.add_parser("residue"); p.add_argument("--ref"); p.set_defaults(fn=residue)
    p=sp.add_parser("children"); p.set_defaults(fn=children)
    a=ap.parse_args(); return a.fn(a)
if __name__=="__main__": raise SystemExit(main())
