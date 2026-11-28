"""FEAT-2581 T-03 one-side measurement. Usage:
    feat2581-ledger-driver.py <side> <checkout> <baseline-sha> <out.jsonl.gz>

Runs, in <checkout> and once each: the gate calibration, every baseline test file directly under
tests/unit and tests/integration (test-*.py / test_*.py at <baseline-sha>, test-feature-json-merge.py
excepted) one at a time with the recorder on PYTHONPATH, tests/unit/omp-hooks.test.ts under bun
with the preload and the junit reporter, the replay, and the canonical-reader audit. Writes every
record raw (before any root replacement) as gzip (mtime 0) JSON Lines to <out.jsonl.gz>.
Exits non-zero without writing when the recorder reported a stream it could not capture."""
import base64
import glob
import gzip
import json
import os
import re
import shutil
import subprocess
import sys

side, checkout, baseline, out = sys.argv[1], os.path.realpath(sys.argv[2]), sys.argv[3], sys.argv[4]
HERE = os.path.dirname(os.path.abspath(__file__))
RECORDER = os.path.join(HERE, "recorder")
PRELOAD = os.path.join(HERE, "feat2581-bun-preload.js")
LEDGER = "/tmp/feat2581-ledger/" + side
FIXTURES = "/tmp/feat2581-fixtures"
OMP = "tests/unit/omp-hooks.test.ts"
SKIP = "tests/integration/test-feature-json-merge.py"
CALIBRATION = b"feat2581 raw\r\nline\rend\xe2\x80\x94\n"


def b64(data):
    return base64.b64encode(data).decode("ascii")


def argv_bytes(argv):
    return b"\0".join(os.fsencode(a) for a in argv)


def base_env():
    env = {k: v for k, v in os.environ.items()
           if k not in ("HARNESS_AGENT_TYPE", "CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR", "PYTHONPATH")
           and not k.startswith("FEAT2581_")}
    env.update(FEAT2581_LEDGER=LEDGER, FEAT2581_CHECKOUT=checkout, FEAT2581_RECORDER=RECORDER,
               PYTHONPATH=RECORDER, TMPDIR=FIXTURES, TMP=FIXTURES, TEMP=FIXTURES)
    return env


def run_files():
    names = subprocess.run(["git", "-C", checkout, "ls-tree", "-r", "--name-only", baseline,
                            "tests/unit", "tests/integration"], check=True, capture_output=True,
                           text=True).stdout.split()
    files = sorted(n for n in names if re.fullmatch(r"tests/(unit|integration)/test[-_][^/]*\.py", n) and n != SKIP)
    return files + [OMP]


def calibration(env):
    script = os.path.join(FIXTURES, "calibration", "check-state.py")
    os.makedirs(os.path.dirname(script), exist_ok=True)
    with open(script, "w", encoding="utf-8") as handle:
        handle.write("import sys\nsys.stdout.buffer.write(%r)\n" % CALIBRATION)
    probe = "import subprocess,sys\nsubprocess.run([sys.executable, %r], capture_output=True, text=True)\n" % script
    subprocess.run([sys.executable, "-c", probe], check=True, cwd=checkout,
                   env=dict(env, FEAT2581_TESTFILE="calibration", FEAT2581_TESTINDEX="000"))


def suite(env, index, rel):
    test_env = dict(env, FEAT2581_TESTFILE=rel, FEAT2581_TESTINDEX="%03d" % index, FEAT2581_TOP="1")
    junit = os.path.join(LEDGER, "omp-hooks.junit.xml")
    if rel == OMP:
        argv = ["bun", "test", "--preload", PRELOAD, "--reporter=junit", "--reporter-outfile=" + junit, rel]
    else:
        argv = [sys.executable, rel]
    proc = subprocess.run(argv, cwd=checkout, env=test_env, capture_output=True, stdin=subprocess.DEVNULL)
    if rel == OMP:
        with open(junit, "rb") as handle:
            cases = handle.read()
    else:
        path = os.path.join(LEDGER, "cases", "".join(c if c.isalnum() or c in "-_." else "_" for c in rel) + ".txt")
        cases = open(path, "rb").read() if os.path.exists(path) else b""
    print("%s %s exit %d" % (side, rel, proc.returncode), flush=True)
    return {"id": "suite#" + rel, "kind": "suite", "streams": {
        "argv": b64(argv_bytes(argv)), "cwd": b64(os.fsencode(checkout)),
        "exit": b64(str(proc.returncode).encode()), "stdout": b64(proc.stdout), "stderr": b64(proc.stderr),
        "cases": b64(cases)}}


def audit():
    env = {k: v for k, v in os.environ.items() if k not in ("HARNESS_AGENT_TYPE", "CLAUDE_PROJECT_DIR", "PYTHONPATH")}
    proc = subprocess.run([os.path.join(checkout, ".agents/skills/harness/bin/check-plan-routes.py"),
                           "--canonical-reader-audit"], cwd=checkout, env=env, capture_output=True)
    return {"id": "audit", "kind": "audit", "streams": {
        "exit": b64(str(proc.returncode).encode()), "stdout": b64(proc.stdout), "stderr": b64(proc.stderr)}}


def replay():
    path = os.path.join(LEDGER, "replay.json")
    subprocess.run([sys.executable, os.path.join(HERE, "feat2581-replay.py"), checkout, RECORDER, path], check=True)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main():
    for d in (LEDGER, FIXTURES, "/tmp/feat2581-replay-ledger"):
        shutil.rmtree(d, ignore_errors=True)
    os.makedirs(LEDGER)
    os.makedirs(FIXTURES)
    env = base_env()
    calibration(env)
    records = [suite(env, i, rel) for i, rel in enumerate(run_files(), 1)]
    records += replay()
    records.append(audit())
    for path in sorted(glob.glob(os.path.join(LEDGER, "rec", "*.json"))):
        with open(path, encoding="utf-8") as handle:
            records.append(json.load(handle))
    errors = sorted(glob.glob(os.path.join(LEDGER, "errors", "*.txt")))
    if errors:
        sys.exit("recorder could not capture a required stream: %s" % [open(e).read().strip() for e in errors])
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        sys.exit("duplicate record ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:10])
    records.sort(key=lambda r: (r["kind"], r["id"]))
    body = "".join(json.dumps(r, sort_keys=True) + "\n" for r in records).encode("utf-8")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=handle, mtime=0) as gz:
            gz.write(body)
    print("%s: %d record(s) -> %s" % (side, len(records), out))


main()
