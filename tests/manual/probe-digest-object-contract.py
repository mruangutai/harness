#!/usr/bin/env python3
"""FEAT-1928 T-02 (SC-04, SC-05): the live OMP probe for the digest object contract.

This is a manual, credentialed probe. It is not a CI check and must never be registered as one.
It starts one fresh, disposable `omp --mode rpc` process with THIS linked feature worktree as
cwd, so the Harness hook OMP loads is the one under test, and drives Main through one
governed dispatch:

  1. Main dispatches harness-documentor once, with no outputSchema and no schemaMode. The
     hook must inject the persona's strict bundle: the settled job reports a `caller` schema
     in `strict` mode, and the child's system prompt carries the persona's own fields.
  2. The child yields `{"data": null}` first. That call must come back as a tool error the
     child can retry, and the transcript names which component refused it (the Harness hook
     or OMP's YieldTool).
  3. The child then yields the valid object. The SAME job completes: one child session, one
     job id, lifecycle `completed`, exit 0, structured output `valid` and equal to the object.

The probe writes the digest's artifact itself, under a temporary `runs/<slug>-product/` dir it
deletes afterwards (a documentor cannot write run dirs). Every RPC frame it keeps, and the
child session OMP returns over `get_subagent_messages`, is sanitized into
notes/live-digest-object-probe.transcript.jsonl. The receipt, notes/live-digest-object-probe.md,
is derived from that file alone.

`--dry-run` checks the prerequisites and prints the plan. It starts nothing and writes nothing:
it is never a receipt. `--verify` (or `--verify-receipt PATH`) re-derives every receipt field
from the recorded transcript, checks its sha256 and the pinned OMP commit, and refuses a
dry-run, failed or hand-edited receipt.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import queue
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FEATURE = "FEAT-1928-digest-object-contract"
FEATURE_REL = f".harness/harness/features/{FEATURE}"
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
NOTES = ROOT / FEATURE_REL / "notes"
RECEIPT = NOTES / "live-digest-object-probe.md"
TRANSCRIPT = NOTES / "live-digest-object-probe.transcript.jsonl"
PERSONA = "harness-documentor"
PROBE_ID = "digest-object-contract-live"
PROVIDERS = {"anthropic": "anthropic/claude-sonnet-5", "openai": "openai-codex/gpt-5.6-terra"}
# The two components that can refuse a null yield, by the text each one writes.
HOOK_REJECTION = "Harness agents must return the digest as an object"
OMP_REJECTIONS = ("yield must contain either", "does not match schema",
                  "requires structured output matching the declared schema")
UNDER_TEST = (
    ".omp/extensions/harness-hooks.ts",
    ".omp/extensions/digest-schema.ts",
    ".claude/skills/harness/bin/validate-digest.py",
    ".claude/skills/harness/bin/digest_schema.py",
    ".claude/skills/harness/bin/digest-schemas/harness-documentor.json",
    ".claude/skills/harness/bin/digest-schemas/common.json",
    "tests/manual/probe-digest-object-contract.py",
)
# Only fields the documentor schema has and no other persona's does prove the bundle is its own.
PERSONA_FIELDS = ('"docs_updated"', '"stale_found"')
SCHEMA_CONTROLS = ("outputSchema", "schemaMode")
DROPPED_FRAMES = {"message_start", "message_update", "tool_execution_update", "subagent_progress"}
DROPPED_KEYS = {"thinkingSignature", "thoughtSignature", "textSignature", "signature",
                "encrypted_content", "encryptedContent"}
SECRETS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
)
HOME = str(Path.home())

sys.path.insert(0, str(BIN))
import harness_boundary  # noqa: E402  (the root resolver every gate uses)
import inflight_registry  # noqa: E402  (this worktree's claim registry)

RESULTS: list[tuple[str, bool, object]] = []


def check(name: str, ok: bool, detail: object = "") -> bool:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} - {name}" + ("" if ok else f" ({detail!r})"))
    return bool(ok)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


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


def has_credentials(provider: str) -> bool:
    """Is there a usable credential for `provider`? Only a row count is read; no secret
    value leaves the store."""
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


def overlay(provider: str) -> Path:
    return ROOT / ".omp" / "providers" / f"{provider}.yml"


def persona_role_model(provider: str) -> str:
    """The concrete model the overlay maps the persona's capability alias to."""
    head = (ROOT / ".omp" / "agents" / f"{PERSONA}.md").read_text(encoding="utf-8").split("---", 2)[1]
    alias = str(yaml.safe_load(head)["model"]).lstrip("@")
    return str(yaml.safe_load(overlay(provider).read_text(encoding="utf-8"))["modelRoles"][alias])


def feature_rows() -> list[dict]:
    path = ROOT / inflight_registry.REGISTRY_REL
    if not path.exists():
        return []
    rows = json.loads(path.read_text(encoding="utf-8")).get("claims", [])
    return [row for row in rows if row.get("feature") == FEATURE]


def preflight(args) -> bool:
    omp = shutil.which("omp")
    check("omp is on PATH", omp is not None, omp)
    runtime, head = omp_runtime(omp) if omp else (None, "")
    check("omp runs the pinned Harness runtime", head == pinned_commit(),
          {"runtime": str(runtime), "head": head, "pin": pinned_commit()})
    check("cwd is this feature worktree", Path.cwd().resolve() == ROOT.resolve(),
          {"cwd": str(Path.cwd()), "worktree": str(ROOT)})
    owned = harness_boundary.worktree_owner(str(ROOT))
    owner = owned[1] if owned else None
    placed = inflight_registry.feature_root(owner, FEATURE) if owner else ""
    check("feature_root places the feature in this linked worktree",
          os.path.realpath(placed) == os.path.realpath(ROOT), {"owner": str(owner), "root": placed})
    check("no fixture substitution: the gates resolve their root to this worktree",
          os.path.realpath(harness_boundary.resolve_root(str(BIN), strict=False))
          == os.path.realpath(ROOT))
    check("no fixture substitution: VALIDATE_DIGEST_BIN is unset",
          "VALIDATE_DIGEST_BIN" not in os.environ, os.environ.get("VALIDATE_DIGEST_BIN"))
    check("the hook under test is this worktree's",
          all((ROOT / rel).is_file() for rel in UNDER_TEST[:2]), str(ROOT / ".omp"))
    check("the provider overlay exists", overlay(args.provider).is_file(), str(overlay(args.provider)))
    child_provider = persona_role_model(args.provider).split("/", 1)[0]
    for provider in dict.fromkeys((args.model.split("/", 1)[0], child_provider)):
        check(f"credentials exist for {provider}", has_credentials(provider), provider)
    check("the feature holds no live claim", feature_rows() == [], feature_rows())
    return all(ok for _name, ok, _detail in RESULTS)


def live_command(args) -> list[str]:
    return [shutil.which("omp") or "omp", "--config", str(overlay(args.provider)), "--mode", "rpc",
            "--model", args.model, "--cwd", str(ROOT)]


def sanitized_command(args) -> str:
    parts = ["omp", *live_command(args)[1:]]
    return " ".join(part.replace(str(ROOT), "<worktree>").replace(HOME, "~") for part in parts)


# ---------------------------------------------------------------------------------------
# The probe's own inputs
# ---------------------------------------------------------------------------------------

def run_slug(stamp: str) -> str:
    # `-product`: the documentor's squad run-dir form, so dispatch-guard's slug check passes.
    return f"probe-digest-object-{stamp}-product"


def valid_object(artifact_rel: str) -> dict:
    return {
        "VERDICT": "PASS",
        "DIGEST": {
            "headline": "FEAT-1928 live digest-object probe child settled",
            "open_questions": [], "files_touched": [], "expertise_update": [],
            "docs_updated": [], "gaps": [], "stale_found": [],
        },
        "artifact": artifact_rel,
    }


def child_task(expected: dict) -> str:
    return "\n".join((
        f"HARNESS-FEATURE: {FEATURE}",
        f"HARNESS-FEATURE-TREE-ROOT: {ROOT}",
        "This is a scripted Harness live probe (FEAT-1928 T-02), not documentation work. Read "
        "nothing, write nothing, run nothing and dispatch nothing. Exactly two tool calls:",
        'Step 1. Call yield with the raw tool-call arguments {"data":null}. The value of data '
        "is the bare JSON null token, unquoted. It is NOT the four-character string \"null\" and "
        "it is not an object; it deliberately violates the yield schema. There is no other key. "
        "It is refused with a tool error. That refusal is what this probe measures, so do not "
        "avoid it or repair it.",
        "Step 2. After that error, call yield again with exactly this object as data, "
        "yield({data: <object>}), and nothing else:",
        json.dumps(expected),
    ))


def main_prompt(expected: dict) -> str:
    return ("Use the task tool exactly once, as a blocking spawn with a single task: agent "
            f"{PERSONA}, and this task text verbatim (keep its first line first):\n"
            f"{child_task(expected)}\n"
            "Pass context \"FEAT-1928 live digest-object probe\" (an in-band refusal for a "
            "missing context strands the dispatch claim). Do not pass outputSchema, schemaMode, "
            "model or isolation. When it returns, reply with exactly PROBE_DONE.")


# ---------------------------------------------------------------------------------------
# The RPC session and the sanitized transcript
# ---------------------------------------------------------------------------------------

def sanitize(value):
    if isinstance(value, str):
        for secret in SECRETS:
            value = secret.sub("[redacted]", value)
        return value.replace(HOME, "~")
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        out = {key: sanitize(item) for key, item in value.items() if key not in DROPPED_KEYS}
        if out.get("type") == "credential_pin" and "hash" in out:
            out["hash"] = "[redacted]"
        return out
    return value


def kept(frame: dict) -> bool:
    if frame.get("type") in DROPPED_FRAMES:
        return False
    if frame.get("type") == "subagent_event":
        event = (frame.get("payload") or {}).get("event") or {}
        return event.get("type") not in DROPPED_FRAMES
    return True


class Session:
    """One disposable `omp --mode rpc` process: JSON frames out, chunked frames reassembled in,
    every kept frame recorded, sanitized, in arrival order."""

    def __init__(self, command: list[str], log: Path):
        self.proc = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=log.open("w"), text=True)
        self.frames: queue.Queue = queue.Queue()
        self.records: list[dict] = []
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
        return json.loads(b"".join(base64.b64decode(parts[i]) for i in range(frame["count"])))

    def _record(self, frame: dict) -> None:
        if not kept(frame):
            return
        if frame.get("type") == "response" and frame.get("command") == "get_subagent_messages":
            data = dict(frame.get("data") or {})
            data.pop("messages", None)  # the same messages again, parsed from `entries`
            frame = {**frame, "data": data}
        self.records.append({"seq": len(self.records), "at": utc_now(), "frame": sanitize(frame)})

    def send(self, command: dict) -> str:
        self._next += 1
        command = {"id": f"probe-{self._next}", **command}
        self.proc.stdin.write(json.dumps(command) + "\n")
        self.proc.stdin.flush()
        return command["id"]

    def pump(self, until, timeout: float) -> dict | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                frame = self.frames.get(timeout=0.25)
            except queue.Empty:
                if self.proc.poll() is not None and self.frames.empty():
                    return None
                continue
            self._record(frame)
            if until(frame):
                return frame
        return None

    def request(self, command: dict, timeout: float = 60) -> dict | None:
        sent = self.send(command)
        return self.pump(lambda f: f.get("type") == "response" and f.get("id") == sent, timeout)

    def close(self) -> int | None:
        if self.proc.poll() is None:
            try:
                self.proc.stdin.close()
                self.proc.wait(timeout=10)
            except (OSError, subprocess.TimeoutExpired):
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        return self.proc.wait()


# ---------------------------------------------------------------------------------------
# Evidence: derived from the transcript alone, identically in live and --verify mode
# ---------------------------------------------------------------------------------------

def _text(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(str(block.get("text", "")) for block in content or []
                     if isinstance(block, dict) and block.get("type") == "text")


def _dispatch_items(args: dict) -> list[dict]:
    tasks = args.get("tasks")
    return [item for item in tasks if isinstance(item, dict)] if isinstance(tasks, list) else [args]


SCHEMA_CONTROL_REFUSAL = "Harness dispatches never carry"


def _task_dispatch(frames: list[dict]) -> tuple[dict, dict, dict]:
    """Main's task call that dispatched a job (start, end), and a tally of every task call:
    how many there were and how many the hook refused for carrying a schema control."""
    ends = {f.get("toolCallId"): f for f in frames
            if f.get("type") == "tool_execution_end" and f.get("toolName") == "task"}
    starts = [f for f in frames if f.get("type") == "tool_execution_start" and f.get("toolName") == "task"]
    texts = [_text((ends.get(s.get("toolCallId")) or {}).get("result", {}).get("content")) for s in starts]
    tally = {"task_calls": len(starts),
             "schema_control_refusals": sum(SCHEMA_CONTROL_REFUSAL in text for text in texts)}
    dispatched = [s for s in starts if (((ends.get(s.get("toolCallId")) or {}).get("result") or {})
                                        .get("details") or {}).get("results")]
    if not dispatched:
        return {}, {}, tally
    return dispatched[0], ends[dispatched[0]["toolCallId"]], tally


def _yields(entries: list[dict]) -> list[dict]:
    """Every yield call in the child session, in order, with its tool result."""
    results = {}
    calls = []
    for entry in entries:
        message = entry.get("message") if entry.get("type") == "message" else None
        if not isinstance(message, dict):
            continue
        if message.get("role") == "toolResult":
            results[message.get("toolCallId")] = message
        elif message.get("role") == "assistant":
            calls += [block for block in message.get("content") or []
                      if isinstance(block, dict) and block.get("type") == "toolCall"
                      and block.get("name") == "yield"]
    out = []
    for call in calls:
        arguments = call.get("arguments") or {}
        result = results.get(call.get("id")) or {}
        out.append({
            "tool_call_id": call.get("id"),
            "arguments": arguments,
            "data_key_present": "data" in arguments,
            "is_error": bool(result.get("isError")),
            "result_text": _text(result.get("content")),
        })
    return out


def rejected_by(text: str) -> str:
    if HOOK_REJECTION in text:
        return "harness-hook (tool_call block, before OMP's YieldTool.execute)"
    if any(marker in text for marker in OMP_REJECTIONS):
        return "omp-yield-tool (YieldTool.execute)"
    return "unknown"


def canonical_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def injected_bundle_sha() -> str:
    """The sha256 of the bundle this worktree's own adapter builds for the persona — the
    exact object the hook injects (DIGEST_SCHEMA_DIR under the gate root)."""
    script = ("import {loadDigestSchemaBundle} from './.omp/extensions/digest-schema.ts';"
              f"console.log(JSON.stringify(loadDigestSchemaBundle('{BIN / 'digest-schemas'}', '{PERSONA}')))")
    run = subprocess.run(["bun", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True)
    return canonical_sha(json.loads(run.stdout))


def derive(records: list[dict]) -> dict:
    frames = [record["frame"] for record in records]
    state = next(((f.get("data") or {}) for f in frames if f.get("type") == "response"
                  and f.get("command") == "get_state" and f.get("success")), {})
    start, end, tally = _task_dispatch(frames)
    args = start.get("args") or {}
    results = ((end.get("result") or {}).get("details") or {}).get("results") or [{}]
    job = results[0] if isinstance(results[0], dict) else {}
    job_id = job.get("id")
    child = next(((f.get("data") or {}) for f in frames if f.get("type") == "response"
                  and f.get("command") == "get_subagent_messages" and f.get("success")), {})
    entries = child.get("entries") or []
    header = next((e for e in entries if e.get("type") == "session"), {})
    init = next((e for e in entries if e.get("type") == "session_init"), {})
    prompt = str(init.get("systemPrompt") or "")
    assistants = [e["message"] for e in entries if e.get("type") == "message"
                  and isinstance(e.get("message"), dict) and e["message"].get("role") == "assistant"]
    yields = _yields(entries)
    bus = [((f.get("payload") or {}).get("event") or {}) for f in frames
           if f.get("type") == "subagent_event" and (f.get("payload") or {}).get("id") == job_id]
    first = yields[0] if yields else {}
    structured = job.get("structuredOutput") or {}
    return {
        "ready_frame": any(f.get("type") == "ready" for f in frames),
        "main_session_id": state.get("sessionId"),
        "task_tool_call_id": start.get("toolCallId"),
        "task_calls": tally,
        # OMP bakes a tool_call hook's revision into the call itself, so these are the args
        # the task tool executed. The hook refuses a dispatcher-supplied outputSchema or
        # schemaMode outright, so a dispatched call that carries them carries the hook's.
        "dispatch": {
            "agents": [item.get("agent") for item in _dispatch_items(args)],
            "top_level_schema_controls": sorted(key for key in SCHEMA_CONTROLS if key in args),
            "executed_schema_modes": [item.get("schemaMode") for item in _dispatch_items(args)],
            "executed_output_schema_sha256": [canonical_sha(item["outputSchema"]) if "outputSchema" in item
                                              else None for item in _dispatch_items(args)],
            "task_first_line": str(next(iter(_dispatch_items(args)), {}).get("task", "")).split("\n")[0],
        },
        "job": {
            "id": job_id,
            "agent": job.get("agent"),
            "exit_code": job.get("exitCode"),
            "resolved_model": job.get("resolvedModel"),
            "structured_output": {key: structured.get(key)
                                  for key in ("source", "mode", "status", "data", "error")},
            "lifecycle": [p.get("status") for p in
                          ((f.get("payload") or {}) for f in frames if f.get("type") == "subagent_lifecycle")
                          if p.get("id") == job_id],
        },
        "child_session": {
            "session_id": header.get("id"),
            "session_file": child.get("sessionFile"),
            "agent": init.get("agent"),
            "providers_models": sorted({f"{m.get('provider')}/{m.get('model')}" for m in assistants}),
            "persona_schema_lines": [line.strip()[:200] for line in prompt.splitlines()
                                     if any(field in line for field in PERSONA_FIELDS)][:6],
        },
        "yields": yields,
        "null_rejection": {
            "text": first.get("result_text"),
            "rejected_by": rejected_by(str(first.get("result_text") or "")),
        },
        "bus_yield_results": [bool(event.get("isError")) for event in bus
                              if event.get("type") == "tool_execution_end" and event.get("toolName") == "yield"],
    }


def without_nulls(value):
    """`value` with every null-valued key dropped. A strict provider grammar (OpenAI's) makes
    each optional property nullable, so the model may send `<optional>: null`; OMP strips an
    optional null before the tool runs (ai/src/utils/validation.ts), and the structured-output
    check below shows the object OMP actually accepted."""
    if isinstance(value, dict):
        return {key: without_nulls(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [without_nulls(item) for item in value]
    return value


def evidence_checks(ev: dict, expected: dict, bundle_sha: str) -> list[tuple[str, bool, object]]:
    """The acceptance, as named predicates over derived evidence."""
    job, child, yields = ev["job"], ev["child_session"], ev["yields"]
    structured = job["structured_output"]
    first = yields[0] if yields else {}
    later = yields[1:]
    valid = [y for y in later if without_nulls(y["arguments"].get("data")) == expected]
    return [
        ("the RPC session became ready", ev["ready_frame"], ev["ready_frame"]),
        ("Main dispatched exactly one harness-documentor", ev["dispatch"]["agents"] == [PERSONA],
         ev["dispatch"]["agents"]),
        ("no task call was refused for a dispatcher-supplied schema control",
         ev["task_calls"]["schema_control_refusals"] == 0
         and ev["dispatch"]["top_level_schema_controls"] == [],
         {"tally": ev["task_calls"], "top_level": ev["dispatch"]["top_level_schema_controls"]}),
        ("the executed dispatch carried the hook's documentor bundle and schemaMode strict",
         ev["dispatch"]["executed_schema_modes"] == ["strict"]
         and ev["dispatch"]["executed_output_schema_sha256"] == [bundle_sha],
         {"bundle_sha256": bundle_sha, **ev["dispatch"]}),
        ("the dispatch declares this feature on its first line",
         ev["dispatch"]["task_first_line"] == f"HARNESS-FEATURE: {FEATURE}", ev["dispatch"]["task_first_line"]),
        ("OMP ran the job with a caller-supplied schema in strict mode (hook injection)",
         structured.get("source") == "caller" and structured.get("mode") == "strict", structured),
        ("the child's system prompt carries the documentor bundle's own fields",
         all(any(f in line for line in child["persona_schema_lines"]) for f in PERSONA_FIELDS),
         child["persona_schema_lines"]),
        ("the first yield carried data explicitly null",
         bool(first) and first["data_key_present"] and first["arguments"].get("data") is None, first),
        ("the null yield came back as a tool error", bool(first) and first["is_error"], first),
        ("a known component refused the null yield",
         ev["null_rejection"]["rejected_by"] != "unknown", ev["null_rejection"]),
        ("the child retried: a later yield in the same session carried the valid object",
         len(valid) == 1, [y["arguments"] for y in later]),
        ("that valid yield was accepted", bool(valid) and not valid[0]["is_error"]
         and "Result submitted" in valid[0]["result_text"], valid),
        ("no yield between the null and the valid one was accepted",
         bool(valid) and all(y["is_error"] for y in later[:later.index(valid[0])]), later),
        ("the live bus saw the same job reject then accept a yield",
         ev["bus_yield_results"][:1] == [True] and ev["bus_yield_results"][-1:] == [False],
         ev["bus_yield_results"]),
        ("the same job settled completed", bool(job["id"]) and job["lifecycle"][-1:] == ["completed"],
         {"id": job["id"], "lifecycle": job["lifecycle"]}),
        ("the child session is that job's", str(child["session_file"] or "").endswith(f"/{job['id']}.jsonl")
         and child["agent"] in (PERSONA, None) and bool(child["session_id"]), child),
        ("the job exited 0", job["exit_code"] == 0, job["exit_code"]),
        ("OMP validated the object: structured output valid and equal to it",
         structured.get("status") == "valid" and structured.get("data") == expected, structured),
    ]


# ---------------------------------------------------------------------------------------
# Live mode and the receipt
# ---------------------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def harness_identity() -> dict:
    git = lambda *a: subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout
    return {
        "head": git("rev-parse", "HEAD").strip(),
        "uncommitted_paths": len([line for line in git("status", "--porcelain").splitlines() if line]),
        "under_test_sha256": {rel: sha256_file(ROOT / rel) for rel in UNDER_TEST},
    }


def run_live(args, expected: dict, artifact: Path) -> dict:
    log = Path(os.environ.get("TMPDIR", "/tmp")) / f"feat1928-digest-probe-{os.getpid()}.log"
    # Identity is taken before the probe writes anything: its own receipt and transcript are
    # tracked files, and rewriting them must not read as an uncommitted change under test.
    meta = {"started_at": utc_now(), "stderr_log": str(log).replace(HOME, "~"),
            "injected_bundle_sha256": injected_bundle_sha(), "harness": harness_identity()}
    artifact.parent.mkdir(parents=True, exist_ok=False)
    artifact.write_text("# FEAT-1928 live digest-object probe artifact\n\nDeleted after the run.\n",
                        encoding="utf-8")
    session = Session(live_command(args), log)
    try:
        if session.pump(lambda f: f.get("type") == "ready", 90) is None:
            meta["failure"] = f"the RPC session never became ready; see {log}"
            return {**meta, "records": session.records, "omp_returncode": session.close()}
        session.request({"type": "set_subagent_subscription", "level": "events"})
        session.request({"type": "get_state"})
        session.send({"type": "prompt", "message": main_prompt(expected)})
        if session.pump(lambda f: f.get("type") == "agent_end", args.timeout) is None:
            meta["failure"] = f"Main's turn did not end within {args.timeout}s"
        job_id = derive(session.records)["job"]["id"]
        if job_id:
            session.request({"type": "get_subagent_messages", "subagentId": job_id})
    finally:
        returncode = session.close()
        shutil.rmtree(artifact.parent, ignore_errors=True)
    return {**meta, "records": session.records, "omp_returncode": returncode}


def write_transcript(records: list[dict]) -> str:
    TRANSCRIPT.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    return sha256_file(TRANSCRIPT)


def read_transcript(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_record(args, run: dict, expected: dict, transcript_sha: str) -> dict:
    omp = shutil.which("omp")
    runtime, head = omp_runtime(omp) if omp else (None, "")
    evidence = derive(read_transcript(TRANSCRIPT))
    checks = evidence_checks(evidence, expected, run["injected_bundle_sha256"])
    failed = [name for name, ok, _ in checks if not ok] + ([run["failure"]] if run.get("failure") else [])
    return {
        "probe": PROBE_ID,
        "mode": "live",
        "dry_run": False,
        "verdict": "FAIL" if failed else "PASS",
        "failed": failed,
        "started_at": run["started_at"],
        "finished_at": utc_now(),
        "command": sanitized_command(args),
        "cwd": "<worktree>",
        "omp": {"launcher": str(omp).replace(HOME, "~"), "runtime": str(runtime).replace(HOME, "~"),
                "sha": head, "pin": pinned_commit()},
        "harness": run["harness"],
        "provider": args.provider,
        "main_model": args.model,
        "child_model": evidence["job"]["resolved_model"],
        "persona": PERSONA,
        "ids": {"main_session": evidence["main_session_id"], "task_tool_call": evidence["task_tool_call_id"],
                "job": evidence["job"]["id"], "child_session": evidence["child_session"]["session_id"]},
        "valid_object": expected,
        "injected_bundle_sha256": run["injected_bundle_sha256"],
        "exit_status": {"job_exit_code": evidence["job"]["exit_code"],
                        "omp_process_returncode": run["omp_returncode"],
                        "probe_exit": 1 if failed else 0},
        "transcript": {"path": str(TRANSCRIPT.relative_to(ROOT)), "sha256": transcript_sha,
                       "records": len(read_transcript(TRANSCRIPT))},
        "evidence": evidence,
        "checks": [{"name": name, "ok": ok} for name, ok, _ in checks],
    }


def receipt_text(record: dict) -> str:
    ev = record["evidence"]
    yields = ev["yields"]
    lines = [
        "# FEAT-1928 live digest-object probe receipt",
        "",
        "Written by `tests/manual/probe-digest-object-contract.py` from a real, disposable OMP RPC "
        "process. Every field below is re-derived from the transcript by `--verify`; hand edits fail.",
        "",
        f"- Verdict: **{record['verdict']}** "
        f"({sum(c['ok'] for c in record['checks'])}/{len(record['checks'])} checks)",
        f"- Run: {record['started_at']} → {record['finished_at']}",
        f"- Command: `{record['command']}` (cwd `{record['cwd']}`)",
        f"- OMP: `{record['omp']['sha']}` (pin `{record['omp']['pin']}`)",
        f"- Harness: HEAD `{record['harness']['head']}` + {record['harness']['uncommitted_paths']} "
        "uncommitted paths; files under test are pinned by sha256 in the record",
        f"- Provider `{record['provider']}`: Main `{record['main_model']}`, "
        f"child `{record['child_model']}` ({', '.join(ev['child_session']['providers_models'])})",
        f"- Ids: main session `{record['ids']['main_session']}`, task call "
        f"`{record['ids']['task_tool_call']}`, job `{record['ids']['job']}`, child session "
        f"`{record['ids']['child_session']}`",
        f"- Injected schema: executed dispatch schemaMode {ev['dispatch']['executed_schema_modes']}, "
        f"outputSchema sha256 {ev['dispatch']['executed_output_schema_sha256']} (hook bundle "
        f"`{record['injected_bundle_sha256']}`); job structured output source "
        f"`{ev['job']['structured_output']['source']}`, mode `{ev['job']['structured_output']['mode']}`",
        f"- Null yield: `{json.dumps(yields[0]['arguments']) if yields else 'none'}` → tool error by "
        f"**{ev['null_rejection']['rejected_by']}**: {ev['null_rejection']['text']!r}",
        f"- Retry: {len(yields)} yields in child session `{record['ids']['child_session']}` of job "
        f"`{record['ids']['job']}`; results {['error' if y['is_error'] else y['result_text'] for y in yields]}",
        f"- Completion: lifecycle {ev['job']['lifecycle']}, job exit {record['exit_status']['job_exit_code']}, "
        f"structured output `{ev['job']['structured_output']['status']}`",
        f"- Transcript: `{record['transcript']['path']}` sha256 `{record['transcript']['sha256']}` "
        f"({record['transcript']['records']} records)",
        "",
        "Checks:",
        *[f"- {'PASS' if c['ok'] else 'FAIL'}: {c['name']}" for c in record["checks"]],
        *([f"- FAIL: {name}" for name in record["failed"] if name not in {c['name'] for c in record['checks']}]),
        "",
        "Record:",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------
# --verify: the receipt against its transcript
# ---------------------------------------------------------------------------------------

def load_record(receipt: Path) -> dict:
    blocks = re.findall(r"```json\n(.*?)\n```", receipt.read_text(encoding="utf-8"), re.S)
    if len(blocks) != 1:
        raise ValueError(f"expected exactly one ```json record block, found {len(blocks)}")
    return json.loads(blocks[0])


def verify(receipt: Path) -> int:
    try:
        record = load_record(receipt)
    except (OSError, ValueError) as exc:
        print(f"FAIL - receipt {receipt} is unreadable: {exc}")
        return 1
    transcript = ROOT / str((record.get("transcript") or {}).get("path", ""))
    if not check("the receipt records a live run, not a dry run",
                 record.get("probe") == PROBE_ID and record.get("mode") == "live"
                 and record.get("dry_run") is False, {k: record.get(k) for k in ("probe", "mode", "dry_run")}):
        return 1
    if not check("the transcript it names exists inside the feature notes",
                 transcript.resolve().parent == NOTES.resolve() and transcript.is_file(), str(transcript)):
        return 1
    check("the transcript's sha256 matches the receipt",
          sha256_file(transcript) == record["transcript"]["sha256"], record["transcript"]["sha256"])
    records = read_transcript(transcript)
    check("the transcript is an ordered frame record",
          [r.get("seq") for r in records] == list(range(len(records)))
          and all(isinstance(r.get("frame"), dict) for r in records)
          and len(records) == record["transcript"]["records"], len(records))
    evidence = derive(records)
    check("every evidence field re-derives from the transcript", evidence == record.get("evidence"),
          "evidence differs")
    for name, ok, detail in evidence_checks(evidence, record.get("valid_object"),
                                            record.get("injected_bundle_sha256")):
        check(name, ok, detail)
    check("the ids match the transcript", record.get("ids") == {
        "main_session": evidence["main_session_id"], "task_tool_call": evidence["task_tool_call_id"],
        "job": evidence["job"]["id"], "child_session": evidence["child_session"]["session_id"]},
        record.get("ids"))
    check("the child model is the one the job resolved",
          record.get("child_model") == evidence["job"]["resolved_model"], record.get("child_model"))
    check("OMP was the pinned runtime", record["omp"]["sha"] == record["omp"]["pin"] == pinned_commit(),
          record["omp"])
    head = str(record["harness"]["head"])
    check("the Harness HEAD is a commit in this repository", bool(re.fullmatch(r"[0-9a-f]{40}", head))
          and subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{head}^{{commit}}"],
                             capture_output=True).returncode == 0, head)
    check("the run was taken at a clean tree: no uncommitted paths",
          record["harness"].get("uncommitted_paths") == 0, record["harness"].get("uncommitted_paths"))
    committed = {rel: hashlib.sha256(subprocess.run(["git", "-C", str(ROOT), "show", f"{head}:{rel}"],
                                                    capture_output=True).stdout).hexdigest()
                 for rel in UNDER_TEST}
    check("every file under test is byte-identical to that commit's",
          committed == record["harness"].get("under_test_sha256"),
          {rel for rel in UNDER_TEST if committed[rel] != record["harness"]["under_test_sha256"].get(rel)})
    check("the recorded run passed and exited 0",
          record.get("verdict") == "PASS" and not record.get("failed")
          and record["exit_status"]["probe_exit"] == 0 and record["exit_status"]["job_exit_code"] == 0,
          {k: record.get(k) for k in ("verdict", "failed", "exit_status")})
    started, finished = (dt.datetime.fromisoformat(record[k]) for k in ("started_at", "finished_at"))
    stamps = [dt.datetime.fromisoformat(r["at"]) for r in records]
    check("the transcript frames fall inside the recorded run",
          bool(stamps) and started <= stamps[0] and stamps[-1] <= finished,
          (record["started_at"], record["finished_at"]))
    failed = [name for name, ok, _ in RESULTS if not ok]
    print(f"{'FAIL' if failed else 'PASS'} - receipt verification {len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="check prerequisites; start nothing")
    parser.add_argument("--verify", action="store_true", help=f"verify {RECEIPT.name}")
    parser.add_argument("--verify-receipt", type=Path, help="verify the receipt at this path")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="anthropic")
    parser.add_argument("--model", help="Main's model (default: the provider's standard model)")
    parser.add_argument("--timeout", type=float, default=900, help="seconds allowed for Main's turn")
    args = parser.parse_args()
    if args.verify or args.verify_receipt:
        return verify(args.verify_receipt or RECEIPT)
    args.model = args.model or PROVIDERS[args.provider]
    ready = preflight(args)
    if args.dry_run:
        print("\nDRY RUN: nothing was started or written. This is not a receipt.")
        print("planned command: " + sanitized_command(args))
        print(f"planned child:   {PERSONA} on {persona_role_model(args.provider)}")
        print(f"prerequisites: {'READY' if ready else 'NOT READY'}")
        return 0 if ready else 1
    if not ready:
        print("live probe REFUSED: prerequisites are not met; nothing was started.")
        return 1
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_rel = f"{FEATURE_REL}/runs/{run_slug(stamp)}/probe-artifact.md"
    expected = valid_object(artifact_rel)
    run = run_live(args, expected, ROOT / artifact_rel)
    record = build_record(args, run, expected, write_transcript(run["records"]))
    RECEIPT.write_text(receipt_text(record), encoding="utf-8")
    print(f"receipt written to {RECEIPT}")
    for name in record["failed"]:
        print(f"FAIL - {name}")
    print(f"{record['verdict']} - {sum(c['ok'] for c in record['checks'])}/{len(record['checks'])} checks")
    return record["exit_status"]["probe_exit"]


if __name__ == "__main__":
    sys.exit(main())
