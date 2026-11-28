"""FEAT-2581 T-03 replay (SC-06). Usage: feat2581-replay.py <checkout> <recorder-dir> <out.json>

For every feature.json tracked in <checkout> (`.harness/<segment>/features/<feature>/feature.json`,
FEAT-2581's own excepted, git ls-files order), build one scratch tree at the fixed path
/tmp/feat2581-replay (cleared first) holding the record at its own relative path with the checkout's
.harness/harness.json, .harness/team-config.yaml and the sibling plan.yaml when tracked, then run the
nine steps against each record under the recorder's fixed clock. Writes one replay record per step
to <out.json>, streams base64: argv, exit, stdout, stderr, before and after (the record's bytes)."""
import base64
import json
import os
import re
import shutil
import subprocess
import sys

checkout, recorder, out = sys.argv[1], sys.argv[2], sys.argv[3]
OWN = ".harness/harness/features/FEAT-2581-feature-record-package/"
SCRATCH = "/tmp/feat2581-replay"
BIN = os.path.join(checkout, ".claude", "skills", "harness", "bin")
RECORD = os.path.join(BIN, "feature-record.py")
VALIDATE = os.path.join(BIN, "validate-feature-json.py")


def b64(data):
    return base64.b64encode(data).decode("ascii")


def tracked():
    names = subprocess.run(["git", "-C", checkout, "ls-files"], check=True, capture_output=True,
                           text=True).stdout.splitlines()
    return [n for n in names if re.fullmatch(r"\.harness/[^/]+/features/[^/]+/feature\.json", n)
            and not n.startswith(OWN)], set(names)


def copy_in(rel):
    dest = os.path.join(SCRATCH, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(os.path.join(checkout, rel), dest)


def steps(path):
    record = [sys.executable, RECORD]
    return [
        [sys.executable, VALIDATE, path],
        record + ["spend", "--file", path],
        record + ["propose-rework", "--file", path],
        record + ["run-start", "--file", path, "--id", "feat2581-replay", "--squad", "product",
                  "--agent", "harness-product-lead"],
        record + ["stamp-tokens", "--file", path, "--tokens", "1"],
        record + ["run-end", "--file", path, "--id", "feat2581-replay", "--verdict", "PASS",
                  "--cycles-used", "0"],
        record + ["judgement", "--file", path, "--by", "harness-orchestrator", "--kind", "continue",
                  "--decision", "replay", "--reason", "replay"],
        record + ["spend", "--file", path],
        [sys.executable, VALIDATE, path],
    ]


def read(path):
    with open(path, "rb") as handle:
        return handle.read()


def build_scratch(records, names):
    """Recreate SCRATCH mode 0700 and copy the records in. A tree this user cannot remove, or a
    symlink in its place, stops the replay instead of being reused."""
    if os.path.lexists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.mkdir(SCRATCH, 0o700)
    for rel in (".harness/harness.json", ".harness/team-config.yaml"):
        copy_in(rel)
    for rel in records:
        copy_in(rel)
        plan = os.path.join(os.path.dirname(rel), "plan.yaml")
        if plan in names:
            copy_in(plan)


def replay_step(rid, argv, path, env):
    before = read(path)
    proc = subprocess.run(argv, cwd=SCRATCH, env=env, capture_output=True, stdin=subprocess.DEVNULL)
    return {"id": rid, "kind": "replay", "streams": {
        "argv": b64(b"\0".join(os.fsencode(a) for a in argv)), "exit": b64(str(proc.returncode).encode()),
        "stdout": b64(proc.stdout), "stderr": b64(proc.stderr), "before": b64(before), "after": b64(read(path))}}


def main():
    records, names = tracked()
    build_scratch(records, names)
    env = {k: v for k, v in os.environ.items() if k not in ("HARNESS_AGENT_TYPE", "CLAUDE_PROJECT_DIR")}
    env.update(PYTHONPATH=recorder, FEAT2581_LEDGER="/tmp/feat2581-replay-ledger", FEAT2581_CLOCK_ONLY="1")
    result = []
    for index, rel in enumerate(records, 1):
        path = os.path.join(SCRATCH, rel)
        result += [replay_step("replay#%d:%s:%d" % (index, rel, step), argv, path, env)
                   for step, argv in enumerate(steps(path), 1)]
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(result, handle)
    print("replay: %d record(s), %d step(s)" % (len(records), len(result)))


main()
