#!/usr/bin/env python3
"""BUG-1898 SC-07: the live OMP merge gate for the inflight-claim lifecycle.

This is a manual, credentialed probe. It is not a CI check and must never be registered as one.
It starts the real pinned `omp` in RPC mode, with THIS linked feature worktree as cwd so the
Harness hook it loads is the one under test. It drives Main through five scenarios and records
the session, result-row and agent ids it observes; it never predicts names.

  S1  Main dispatches harness-orchestrator in the background, and its real lifecycle
      settlement leaves no row.
  S2  The settled orchestrator is woken by hub send and writes under a claim bound to its
      exact runtime id. The hook authorizes that write only against such a claim. Nobody
      binds by hand.
  S3  A background batch mixes a scout with two orchestrators, one of which dispatches a
      nested scout. It must show a repeated name's suffix id and a lineage id. Rows are
      matched by real ids: no governed row ever carries a non-governed id or another
      persona's id, and every governed child settles.
  S4  One real suite run leaves a separately seeded, unrelated live claim byte-identical.
  S5  Every governed child settled, and the feature registry is empty at the end.

A skipped or unobserved scenario is a FAIL, never a pass. Cleanup releases only the sentinel
claim this probe seeded and deletes only the wake marker it asked for.

`--dry-run` checks the prerequisites and prints the planned command, cwd and scenarios. It
starts nothing and is never a receipt. Live mode appends its receipt to
notes/live-omp-probe.md.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import queue
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FEATURE = "BUG-1898-inflight-claim-lifecycle"
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
REGISTRY = ROOT / ".harness" / ".inflight-claims.json"
NOTES = ROOT / ".harness" / "harness" / "features" / FEATURE / "notes"
RECEIPT = NOTES / "live-omp-probe.md"
WAKE_MARKER = NOTES / "probe-wake-marker.txt"
SUITE = ("python3", "tests/integration/test-validate-digest.py")
DEFAULT_MODEL = "anthropic/claude-sonnet-5"
SENTINEL_FEATURE = "BUG-1898-probe-sentinel"
SENTINEL_ID = "Probe.Sentinel"
SETTLED = ("completed", "failed", "aborted")
SCENARIOS = (
    ("S1-orchestrator-background",
     "Main dispatches harness-orchestrator in background; its lifecycle settlement leaves no row"),
    ("S2-wake-reclaim",
     "the settled orchestrator, woken by hub send, writes under a claim bound to its exact id"),
    ("S3-mixed-batch",
     "scout + two orchestrators (one nesting a scout) settle by real ids, no cross-attachment"),
    ("S4-suite-preservation",
     "one real suite run leaves a separately seeded unrelated live claim intact"),
    ("S5-settled-empty", "every governed child settled and the feature registry is empty"),
)
DIGEST = """VERDICT: PASS
DIGEST:
  headline: BUG-1898 live probe child settled
  feature: {feature}
  status: in_progress
  runs: []
  cycles_used: 0
  briefing: none
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/harness/features/{feature}/feature.json""".format(feature=FEATURE)
CHILD_PREAMBLE = (
    "HARNESS-FEATURE: {feature}\nHARNESS-FEATURE-TREE-ROOT: {root}\n"
    "This is a scripted Harness live probe (BUG-1898), not feature work. Read nothing, change "
    "nothing and dispatch nothing unless the steps below say so."
).format(feature=FEATURE, root=ROOT)

sys.path.insert(0, str(BIN))
import harness_boundary  # noqa: E402  (the root resolver every gate uses)
import inflight_registry  # noqa: E402  (the registry under test, from this worktree)

RESULTS: list[tuple[str, bool, object]] = []


def check(name: str, ok: bool, detail: object = "") -> bool:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} - {name}" + ("" if ok else f" ({detail!r})"))
    return bool(ok)


# ---------------------------------------------------------------------------------------
# Prerequisites: shared by --dry-run and live mode
# ---------------------------------------------------------------------------------------

def pinned_commit() -> str:
    return json.loads((ROOT / ".omp" / "runtime-pin.json").read_text())["commit"]


def omp_runtime(omp: str) -> tuple[Path | None, str]:
    """The checkout the `omp` launcher runs from, and its HEAD commit."""
    here = Path(omp).resolve().parent
    for candidate in (here, *here.parents):
        if (candidate / ".git").exists():
            head = subprocess.run(["git", "-C", str(candidate), "rev-parse", "HEAD"],
                                  capture_output=True, text=True)
            return candidate, head.stdout.strip()
    return None, ""


def has_credentials(model: str) -> bool:
    """Is there a usable credential for `model`'s provider? Only a row count is read; no
    secret value leaves the store."""
    provider = model.split("/", 1)[0]
    if os.environ.get(provider.upper().replace("-", "_") + "_API_KEY"):
        return True
    store = Path.home() / ".omp" / "agent" / "agent.db"
    if not store.is_file():
        return False
    try:
        with sqlite3.connect(f"file:{store}?mode=ro", uri=True) as db:
            (count,) = db.execute(
                "SELECT count(*) FROM auth_credentials WHERE provider = ? "
                "AND disabled_cause IS NULL", (provider,)).fetchone()
    except sqlite3.Error:
        return False
    return count > 0


def registry_rows(root: Path = ROOT) -> list[dict]:
    path = root / ".harness" / ".inflight-claims.json"
    if not path.exists():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("claims", []))


def check_runtime(omp: str | None) -> None:
    check("omp is on PATH", omp is not None, omp)
    runtime, head = omp_runtime(omp) if omp else (None, "")
    check("omp runs the pinned Harness runtime", head == pinned_commit(),
          {"runtime": str(runtime), "head": head, "pin": pinned_commit()})


def owner_checkout() -> Path | None:
    """The checkout this linked worktree belongs to (`.git` is a `gitdir:` pointer file)."""
    pointer = (ROOT / ".git").read_text().strip() if (ROOT / ".git").is_file() else ""
    return Path(pointer[len("gitdir: "):]).parents[2] if pointer.startswith("gitdir: ") else None


def check_checkout() -> None:
    check("cwd is this feature worktree", Path.cwd().resolve() == ROOT.resolve(),
          {"cwd": str(Path.cwd()), "worktree": str(ROOT)})
    owner = owner_checkout()
    placed = inflight_registry.feature_root(str(owner), FEATURE) if owner else ""
    check("feature_root places the feature in this linked worktree",
          os.path.realpath(placed) == os.path.realpath(ROOT),
          {"owner": str(owner), "feature_root": placed})


def check_no_substitution() -> None:
    resolved = harness_boundary.resolve_root(str(BIN), strict=False)
    check("no fixture substitution: the gates resolve their root to this worktree",
          os.path.realpath(resolved) == os.path.realpath(ROOT), resolved)
    check("no fixture substitution: VALIDATE_DIGEST_BIN is unset",
          "VALIDATE_DIGEST_BIN" not in os.environ, os.environ.get("VALIDATE_DIGEST_BIN"))
    check("the hook under test is this worktree's",
          (ROOT / ".omp" / "extensions" / "harness-hooks.ts").is_file(), str(ROOT / ".omp"))


def preflight(model: str) -> bool:
    omp = shutil.which("omp")
    check_runtime(omp)
    check_checkout()
    check_no_substitution()
    check("credentials exist for " + model.split("/", 1)[0], has_credentials(model), model)
    check("the feature registry holds no rows (cutover done, nothing live)",
          registry_rows() == [], registry_rows())
    return all(ok for _name, ok, _detail in RESULTS)


def live_command(model: str) -> list[str]:
    return [shutil.which("omp") or "omp", "--mode", "rpc", "--model", model, "--cwd", str(ROOT)]


def dry_run(model: str) -> int:
    ready = preflight(model)
    print("\nDRY RUN: nothing was started and no scenario ran. This is not a receipt.")
    print("planned command: " + " ".join(live_command(model)))
    print("planned cwd:     " + str(ROOT))
    print("planned suite:   " + " ".join(SUITE))
    for scenario, summary in SCENARIOS:
        print(f"  {scenario}: {summary}")
    print(f"prerequisites: {'READY' if ready else 'NOT READY'}")
    return 0 if ready else 1


# ---------------------------------------------------------------------------------------
# The RPC session
# ---------------------------------------------------------------------------------------

class Session:
    """One `omp --mode rpc` process: JSON frames out, chunked frames reassembled in."""

    def __init__(self, command: list[str], log: Path):
        self.proc = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=log.open("w"), text=True)
        self.frames: queue.Queue = queue.Queue()
        self.lifecycle: list[dict] = []
        self.samples: list[tuple[float, list[dict]]] = []
        self._chunks: dict[str, dict[int, str]] = {}
        self._next = 0
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self) -> None:
        for line in self.proc.stdout:
            try:
                frame = json.loads(line)
            except json.JSONDecodeError:
                continue
            frame = self._reassemble(frame)
            if frame is not None:
                self.frames.put(frame)

    def _reassemble(self, frame: dict) -> dict | None:
        if frame.get("type") != "rpc_chunk":
            return frame
        parts = self._chunks.setdefault(frame["chunkId"], {})
        parts[frame["index"]] = frame["data"]
        if len(parts) < frame["count"]:
            return None
        del self._chunks[frame["chunkId"]]
        raw = b"".join(base64.b64decode(parts[i]) for i in range(frame["count"]))
        return json.loads(raw)

    def send(self, command: dict) -> str:
        self._next += 1
        command = {"id": f"probe-{self._next}", **command}
        self.proc.stdin.write(json.dumps(command) + "\n")
        self.proc.stdin.flush()
        return command["id"]

    def pump(self, until, timeout: float) -> dict | None:
        """Consume frames until `until(frame)` is true or `timeout` passes. Lifecycle frames
        are kept, and the registry is sampled on every step for the receipt."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            frame = self._next_frame()
            if frame is not None and until(frame):
                return frame
        return None

    def _next_frame(self) -> dict | None:
        self.samples.append((time.time(), registry_rows()))
        try:
            frame = self.frames.get(timeout=0.25)
        except queue.Empty:
            return None
        if frame.get("type") == "subagent_lifecycle":
            self.lifecycle.append(frame.get("payload") or {})
        return frame

    def request(self, command: dict, timeout: float = 60) -> dict | None:
        sent = self.send(command)
        return self.pump(lambda f: f.get("type") == "response" and f.get("id") == sent, timeout)

    def prompt(self, message: str, timeout: float) -> bool:
        self.request({"type": "prompt", "message": message})
        return self.pump(lambda f: f.get("type") == "agent_end", timeout) is not None

    def settled(self, agent_id: str, timeout: float) -> dict | None:
        done = self._settlement(agent_id)
        if done:
            return done
        found = self.pump(lambda f: f.get("type") == "subagent_lifecycle"
                          and (f.get("payload") or {}).get("id") == agent_id
                          and (f.get("payload") or {}).get("status") in SETTLED, timeout)
        return (found or {}).get("payload")

    def _settlement(self, agent_id: str) -> dict | None:
        return next((p for p in reversed(self.lifecycle)
                     if p.get("id") == agent_id and p.get("status") in SETTLED), None)

    def started(self, agent: str, since: int) -> list[str]:
        return [p["id"] for p in self.lifecycle[since:]
                if p.get("agent") == agent and p.get("status") == "started" and p.get("id")]

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.proc.kill()


# ---------------------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------------------

def child_task(steps: str) -> str:
    return f"{CHILD_PREAMBLE}\n{steps}\nThen yield exactly this digest as your result:\n{DIGEST}"


def governed_rows(agent_ids) -> list[dict]:
    return [row for row in registry_rows() if row.get("agent_id") in set(agent_ids)]


def s1_background_orchestrator(s: Session, timeout: float) -> str | None:
    mark = len(s.lifecycle)
    s.prompt("Use the task tool exactly once, as a BACKGROUND (non-blocking) spawn: agent "
             "harness-orchestrator, name Scope, task:\n" + child_task("There are no steps.")
             + "\nDo not wait for it. Reply with exactly PROBE_S1_SENT.", timeout)
    ids = s.started("harness-orchestrator", mark) or [None]
    orch = ids[0]
    settled = s.settled(orch, timeout) if orch else None
    check("S1: a background orchestrator started under a real runtime id", orch is not None,
          s.lifecycle[mark:])
    check("S1: its settlement arrived on the lifecycle bus", settled is not None, orch)
    check("S1: its settled run leaves no row", not governed_rows([orch]), registry_rows())
    return orch


def wake_settlement(s: Session, orch: str, mark: int, timeout: float) -> dict | None:
    """A settlement of `orch` AFTER the wake began: the S1 one does not count."""
    def woken_settled(_frame: dict) -> bool:
        return any(p.get("id") == orch and p.get("status") in SETTLED
                   for p in s.lifecycle[mark:])
    return s.pump(woken_settled, timeout) or next(
        (p for p in s.lifecycle[mark:] if p.get("id") == orch and p.get("status") in SETTLED),
        None)


def sampled_owner(s: Session, orch: str) -> list[float]:
    return [ts for ts, rows in s.samples
            if any(r.get("agent_id") == orch and r.get("feature") == FEATURE for r in rows)]


def s2_wake_reclaim(s: Session, orch: str | None, timeout: float) -> None:
    if not check("S2: has a settled orchestrator to wake", orch is not None, orch):
        return
    mark = len(s.lifecycle)
    wake = child_task(f"Use the write tool to create {WAKE_MARKER} containing exactly: "
                      f"woken {orch}")
    s.prompt(f"Use the hub tool once: op send, to {orch}, message:\n{wake}\nThen use hub "
             f"wait from {orch} and reply with exactly PROBE_S2_DONE.", timeout)
    settled = wake_settlement(s, orch, mark, timeout)
    owned = sampled_owner(s, orch)
    text = WAKE_MARKER.read_text().strip() if WAKE_MARKER.exists() else None
    check("S2: the woken run's write landed (the hook authorizes only an exact-id claim)",
          text == f"woken {orch}", text)
    check("S2: a row bound to the exact woken id was sampled during the wake",
          bool(owned), "no sample caught the live claim")
    check("S2: the wake settled on the lifecycle bus", settled is not None, s.lifecycle[mark:])
    check("S2: and leaves no row", not governed_rows([orch]), registry_rows())


def s3_mixed_batch(s: Session, timeout: float) -> list[str]:
    mark = len(s.lifecycle)
    nested = child_task("Use the task tool exactly once (blocking): agent scout, name Scope, "
                        "task: Reply with the single word ok.")
    plain = child_task("There are no steps.")
    s.prompt("Use the task tool exactly once, as a BACKGROUND (non-blocking) batch of three "
             "tasks with shared context 'BUG-1898 probe batch':\n"
             "1. agent scout, name Scope, task: Reply with the single word ok.\n"
             f"2. agent harness-orchestrator, name Nest, task:\n{nested}\n"
             f"3. agent harness-orchestrator, name Plain, task:\n{plain}\n"
             "Then wait for all three with hub wait and reply with exactly PROBE_S3_DONE.",
             timeout)
    governed = s.started("harness-orchestrator", mark)
    for agent_id in governed:
        s.settled(agent_id, timeout)
    check_batch_ids(s, governed, batch_plain_ids(s, mark))
    return governed


def batch_plain_ids(s: Session, mark: int) -> list[str]:
    return [p["id"] for p in s.lifecycle[mark:]
            if p.get("id") and p.get("agent") != "harness-orchestrator"]


def observed_ids(s: Session, governed: list[str], plain_ids: list[str]) -> list[str]:
    """Every id OMP reported: lifecycle frames plus its subagent registry (nested included)."""
    listed = (s.request({"type": "get_subagents"}) or {}).get("data") or {}
    return sorted({str(a.get("id")) for a in listed.get("subagents", [])}
                  | set(governed) | set(plain_ids))


def crossed_rows(s: Session, governed: list[str], plain_ids: list[str]) -> list[dict]:
    """Rows, over every sample, bound to a non-governed id or to another persona's id."""
    def crossed(row: dict) -> bool:
        agent_id = row.get("agent_id")
        return agent_id in plain_ids or (
            agent_id in governed and row.get("agent") != "harness-orchestrator")
    return [row for _ts, rows in s.samples for row in rows if crossed(row)]


def check_batch_ids(s: Session, governed: list[str], plain_ids: list[str]) -> None:
    every = observed_ids(s, governed, plain_ids)
    stray = crossed_rows(s, governed, plain_ids)
    settled = [s._settlement(i) for i in governed]
    check("S3: two governed orchestrators started under real ids", len(governed) == 2, governed)
    check("S3: a repeated name produced a suffix id (Name-2)",
          any(i.rsplit("-", 1)[-1].isdigit() for i in every if "-" in i), every)
    check("S3: a nested child produced a lineage id (Lead.Scope)",
          any("." in i for i in every), every)
    check("S3: no row ever carried a non-governed id or crossed personas", not stray, stray[:3])
    check("S3: every governed child settled", all(settled), settled)
    check("S3: and none leaves a row", not governed_rows(governed), registry_rows())


def seed_sentinel() -> dict:
    entry = inflight_registry.claim_with_receipt(
        str(ROOT), "harness-qa", "probe-sentinel", str(ROOT), feature=SENTINEL_FEATURE,
        supervisor_pid=os.getpid())
    inflight_registry.attach_runtime_identity(
        str(ROOT), "harness-qa", SENTINEL_FEATURE, agent_id=SENTINEL_ID,
        claim_id=entry["claim_id"], parent_agent_id="Probe")
    return next(r for r in registry_rows() if r.get("claim_id") == entry["claim_id"])


def s4_suite_preservation(sentinel: dict) -> dict:
    before = registry_rows()
    run = subprocess.run(list(SUITE), cwd=ROOT, capture_output=True, text=True, timeout=1800)
    after = registry_rows()
    tail = (run.stdout + run.stderr).strip().splitlines()[-3:]
    check("S4: the real suite run passed", run.returncode == 0, tail)
    check("S4: the seeded unrelated claim is byte-identical after the suite",
          [r for r in after if r.get("claim_id") == sentinel["claim_id"]] == [sentinel], after)
    check("S4: and the suite changed no other row", after == before, {"before": before,
                                                                      "after": after})
    return {"returncode": run.returncode, "tail": tail}


def s5_settled_empty(orch: str | None, governed: list[str], sentinel: dict) -> None:
    inflight_registry.release(str(ROOT), feature=SENTINEL_FEATURE,
                              claim_id=sentinel["claim_id"])
    if WAKE_MARKER.exists():
        WAKE_MARKER.unlink()
    check("S5: every governed child observed", orch is not None and len(governed) == 2,
          [orch, *governed])
    check("S5: the feature registry is empty at probe end", registry_rows() == [],
          registry_rows())


# ---------------------------------------------------------------------------------------
# Live mode and the receipt
# ---------------------------------------------------------------------------------------

def run_scenarios(session: Session, evidence: dict, timeout: float) -> None:
    session.request({"type": "set_subagent_subscription", "level": "progress"})
    state = (session.request({"type": "get_state"}) or {}).get("data") or {}
    evidence["session"] = {key: state.get(key) for key in ("sessionId", "sessionFile")}
    orch = s1_background_orchestrator(session, timeout)
    s2_wake_reclaim(session, orch, timeout)
    governed = s3_mixed_batch(session, timeout)
    sentinel = seed_sentinel()
    evidence["sentinel"] = sentinel
    evidence["suite"] = s4_suite_preservation(sentinel)
    s5_settled_empty(orch, governed, sentinel)
    evidence["ids"] = {"S1/S2 orchestrator": orch, "S3 governed": governed,
                       "lifecycle": session.lifecycle}


def run_live(args) -> tuple[dict, Session | None]:
    evidence: dict = {"before": registry_rows()}
    log = Path(os.environ.get("TMPDIR", "/tmp")) / f"bug1898-probe-{os.getpid()}.log"
    session = Session(live_command(args.model), log)
    evidence["stderr_log"] = str(log)
    try:
        if check("the RPC session became ready",
                 session.pump(lambda f: f.get("type") == "ready", 60) is not None, str(log)):
            run_scenarios(session, evidence, args.timeout)
    finally:
        session.close()
        evidence["after"] = registry_rows()
    return evidence, session


def check_lines() -> list[str]:
    return [f"- {'PASS' if ok else 'FAIL'}: {name}" + ("" if ok else f" (`{detail!r}`)")
            for name, ok, detail in RESULTS]


def receipt_header(args, evidence: dict, failed: list[str]) -> list[str]:
    omp = shutil.which("omp")
    runtime, head = omp_runtime(omp) if omp else (None, "")
    return [
        f"\n## Live run {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"- Verdict: **{'FAIL' if failed else 'PASS'}** "
        f"({len(RESULTS) - len(failed)}/{len(RESULTS)} checks)",
        f"- Command: `{' '.join(live_command(args.model))}`",
        f"- cwd: `{ROOT}`",
        f"- OMP: `{omp}` → runtime `{runtime}` @ `{head}` (pin `{pinned_commit()}`)",
        f"- Session: `{json.dumps(evidence.get('session'))}`",
        f"- Scenarios: {', '.join(s for s, _ in SCENARIOS)}",
        f"- Suite: `{' '.join(SUITE)}` → `{json.dumps(evidence.get('suite'))}`",
    ]


def write_receipt(args, evidence: dict) -> None:
    failed = [name for name, ok, _ in RESULTS if not ok]
    snapshot = {k: evidence.get(k) for k in ("ids", "sentinel", "before", "after")}
    lines = [
        *receipt_header(args, evidence, failed),
        "",
        "Checks:",
        *check_lines(),
        "",
        "Observed ids and registry snapshots:",
        "```json",
        json.dumps(snapshot, indent=2, default=str),
        "```",
    ]
    with RECEIPT.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"receipt appended to {RECEIPT}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="check prerequisites and print the plan; start nothing")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=float, default=900,
                        help="seconds allowed per scenario step")
    args = parser.parse_args()
    if args.dry_run:
        return dry_run(args.model)
    if not preflight(args.model):
        print("live probe REFUSED: prerequisites are not met; nothing was started.")
        return 1
    evidence, _session = run_live(args)
    write_receipt(args, evidence)
    failed = [name for name, ok, _ in RESULTS if not ok]
    print(f"{'FAIL' if failed else 'PASS'} - {len(RESULTS) - len(failed)}/{len(RESULTS)} "
          "checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
