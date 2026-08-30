import { describe, expect, test } from "bun:test";
import { existsSync, mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  DEFAULT_CONTEXT_WARN_TOKENS,
  contextAdvisoryText,
  detectHarnessAgent,
  gatePath,
  extractEditPaths,
  normalizeYieldInput,
  normalizeTaskDispatches,
  readContextAnchor,
  registerHarnessHooks,
  resolveContextWarnTokens,
  resolveSessionFile,
  yieldContractText,
} from "../../../../.omp/extensions/harness-hooks.ts";

describe("detectHarnessAgent", () => {
  test("finds the canonical machine-readable marker", () => {
    expect(detectHarnessAgent([
      "base system prompt",
      "HARNESS_AGENT_ID: harness-backend-dev\n\n# Harness: Backend Engineer",
      "project context",
    ])).toBe("harness-backend-dev");
  });

  test("returns undefined for the main session", () => {
    expect(detectHarnessAgent(["base", "project"])).toBeUndefined();
  });

  test("rejects conflicting markers", () => {
    expect(() => detectHarnessAgent([
      "HARNESS_AGENT_ID: harness-backend-dev",
      "HARNESS_AGENT_ID: harness-pm",
    ])).toThrow("conflicting Harness agent markers");
  });

  test("ignores unsafe agent names", () => {
    expect(detectHarnessAgent(["HARNESS_AGENT_ID: ../../etc/passwd"])).toBeUndefined();
  });
});

describe("extractEditPaths", () => {
  test("extracts one hash-anchored file", () => {
    expect(extractEditPaths(`*** Begin Patch\n[src/a.ts#A1B2]\nPUT 1.=1:\n+new\n*** End Patch\n`))
      .toEqual(["src/a.ts"]);
  });

  test("extracts and deduplicates multiple files", () => {
    expect(extractEditPaths(`*** Begin Patch\n[a.ts#A1B2]\nPUT 1.=1:\n+x\n[b.ts#C3D4]\nPUT 2.=2:\n+y\n[a.ts#A1B2]\nPUT 1.=1:\n+z\n*** End Patch\n`))
      .toEqual(["a.ts", "b.ts"]);
  });

  test("returns no paths for a non-patch input", () => {
    expect(extractEditPaths("not a patch")).toEqual([]);
  });
});

describe("yieldContractText", () => {
  test("unwraps text content", () => {
    expect(yieldContractText({ data: { content: "VERDICT: PASS" } })).toBe("VERDICT: PASS");
  });

  test("renders a structured digest for the validator", () => {
    const rendered = yieldContractText({
      data: {
        VERDICT: "PASS",
        DIGEST: {
          headline: "No changes.",
          files_touched: [],
          open_questions: [],
        },
        artifact: "none",
      },
    });
    expect(rendered).toContain("VERDICT: PASS");
    expect(rendered).toContain("DIGEST:");
    expect(rendered).toContain("  files_touched: []");
    expect(rendered).toContain("artifact: none");
  });

  test("uses the last assistant message for an omitted yield payload", () => {
    expect(yieldContractText({}, "VERDICT: PASS")).toBe("VERDICT: PASS");
  });

  test("rewrites an empty yield to explicit last-turn data", () => {
    expect(normalizeYieldInput({ result: {} }, "VERDICT: PASS")).toEqual({
      result: { data: { content: "VERDICT: PASS" } },
    });
  });

  test("keeps explicit yield data unchanged", () => {
    const input = { result: { data: { VERDICT: "PASS" } } };
    expect(normalizeYieldInput(input, "ignored")).toEqual(input);
  });
});

// B-1 (FEAT-42 review panel). runPolicy chose the gate executable with `join(cwd, BIN,
// script)` against a caller-supplied ctx.cwd, so the binary enforcing a policy was selected
// by the party the policy governs — six gates, eleven call sites, no coverage at all. These
// cases assert the path is a function of THIS MODULE's location and of nothing else.
describe("gatePath", () => {
  test("resolves under the repository that ships this extension", () => {
    const p = gatePath("check-domain.sh");
    expect(p.endsWith("/.agents/skills/harness/bin/check-domain.sh")).toBe(true);
    expect(existsSync(p)).toBe(true);
  });

  test("is byte-identical whatever the process working directory is", () => {
    const before = process.cwd();
    const first = gatePath("check-domain.sh");
    try {
      process.chdir(tmpdir());
      expect(gatePath("check-domain.sh")).toBe(first);
    } finally {
      process.chdir(before);
    }
  });

  // THE PAIRED HALF. Without it the two cases above are satisfied by a gatePath that
  // returns a constant: this one proves the script name still reaches the result.
  test("the script name still selects the file", () => {
    expect(gatePath("bash-write-guard.sh")).not.toBe(gatePath("check-domain.sh"));
    expect(gatePath("bash-write-guard.sh").endsWith("bash-write-guard.sh")).toBe(true);
  });
});

describe("OMP task lifecycle adapter", () => {
  function fixture() {
    const handlers = new Map<string, Function>();
    const calls: Array<{ script: string; args: string[]; payload: Record<string, unknown> }> = [];
    const active = new Set(["agent-a", "agent-b"]);
    let claim = 0;
    const pi = {
      on(name: string, handler: Function) {
        handlers.set(name, handler);
      },
    };
    const runner = (
      _cwd: string,
      script: string,
      args: string[],
      payload: Record<string, unknown>,
    ) => {
      calls.push({ script, args, payload });
      if (script === "inject-expertise.sh") return { blocked: false, stdout: "" };
      if (script === "dispatch-guard.sh") {
        const task = (payload.tool_input as Record<string, unknown>).task;
        if (task === "deny") return { blocked: true, reason: "denied", stdout: "" };
        // The guard's FAIL-OPEN shape: exit 0, nothing on stdout. Seven branches of
        // dispatch-guard.sh return exactly this (:34, :38, :72, :112, :138, :145, :187).
        // Absent from this fixture, no test could execute the pass-through path and F1
        // was invisible to a green suite.
        if (task === "passthrough") return { blocked: false, stdout: "" };
        claim += 1;
        return {
          blocked: false,
          stdout: JSON.stringify({
            harness_claim: {
              root: "/repo",
              feature: "FEAT-43-long-run",
              agent: (payload.tool_input as Record<string, unknown>).agent,
              claim_id: `claim-${claim}`,
            },
          }),
        };
      }
      if (script === "inflight_registry.py" && args[0] === "release") {
        const agentIndex = args.indexOf("--agent-id");
        if (agentIndex >= 0) active.delete(args[agentIndex + 1]);
        const claimIndex = args.indexOf("--claim-id");
        if (claimIndex >= 0 && args[claimIndex + 1] === "claim-1") active.delete("agent-a");
        if (claimIndex >= 0 && args[claimIndex + 1] === "claim-2") active.delete("agent-b");
        return { blocked: false, stdout: "" };
      }
      if (script === "validate-digest.py") {
        return active.size
          ? { blocked: true, reason: "children live", stdout: "" }
          : { blocked: false, stdout: "" };
      }
      return { blocked: false, stdout: "" };
    };
    registerHarnessHooks(pi, runner);
    return { handlers, calls };
  }

  async function start(handlers: Map<string, Function>) {
    const ctx = {
      cwd: "/repo",
      sessionManager: { getSessionId: () => "parent-session" },
    };
    await handlers.get("before_agent_start")?.({
      systemPrompt: ["HARNESS_AGENT_ID: harness-eng-lead"],
    }, ctx);
    await handlers.get("message_end")?.({
      message: {
        role: "user",
        content: [{ type: "text", text: "HARNESS-FEATURE: FEAT-43-long-run\nassignment" }],
      },
    }, ctx);
  }

  test("normalizes batch and flat task calls", () => {
    expect(normalizeTaskDispatches({
      context: "shared",
      tasks: [{ agent: "harness-backend-dev", task: "a" }, { agent: "harness-dev-ops", task: "b" }],
    })).toEqual([
      { agent: "harness-backend-dev", task: "a" },
      { agent: "harness-dev-ops", task: "b" },
    ]);
    expect(normalizeTaskDispatches({ agent: "harness-pm", task: "plan" }))
      .toEqual([{ agent: "harness-pm", task: "plan" }]);
  });

  test("blocks a whole batch and rolls back earlier claims", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    expect(calls.some((call) =>
      call.script === "inflight_registry.py"
      && call.args[0] === "reconcile"
      && call.args.includes("FEAT-43-long-run")
    )).toBe(true);

    const result = await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-refused",
      input: {
        context: "shared",
        tasks: [
          { agent: "harness-backend-dev", task: "HARNESS-FEATURE: FEAT-43-long-run\nallow" },
          { agent: "harness-dev-ops", task: "deny" },
        ],
      },
    }, { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } });
    expect(result).toEqual({ block: true, reason: "denied" });
    expect(calls.some((call) =>
      call.script === "inflight_registry.py"
      && call.args.includes("--claim-id")
      && call.args.includes("claim-1")
    )).toBe(true);
  });
  test("runs the GitHub close gate before other Bash guards", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    await handlers.get("tool_call")?.({
      toolName: "bash",
      input: { command: "gh issue close 12" },
    }, { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } });
    const scripts = calls.map((call) => call.script);
    expect(scripts.indexOf("gh-close-gate.sh")).toBeGreaterThan(-1);
    expect(scripts.indexOf("gh-close-gate.sh")).toBeLessThan(scripts.indexOf("branch-create-gate.sh"));
    expect(scripts.indexOf("branch-create-gate.sh")).toBeLessThan(scripts.indexOf("bash-write-guard.sh"));
  });

  test("releases settled blocking results before the parent resumes", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    const input = {
      context: "shared",
      tasks: [
        { agent: "harness-backend-dev", task: "HARNESS-FEATURE: FEAT-43-long-run\none" },
        { agent: "harness-dev-ops", task: "HARNESS-FEATURE: FEAT-43-long-run\ntwo" },
      ],
    };
    await handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "call-blocking", input,
    }, ctx);
    await handlers.get("tool_result")?.({
      toolName: "task",
      toolCallId: "call-blocking",
      input,
      details: {
        results: [
          { index: 0, id: "agent-a", exitCode: 0 },
          { index: 1, id: "agent-b", exitCode: 0 },
        ],
      },
      content: [],
    }, ctx);
    expect(calls.filter((call) =>
      call.script === "inflight_registry.py" && call.args[0] === "attach"
    )).toHaveLength(0);
    expect(await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: { data: { content: "VERDICT: PASS" } } },
    }, ctx)).toBeUndefined();
  });

  test("attaches task identities and releases each terminal child", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    const input = {
      context: "shared",
      tasks: [
        { agent: "harness-backend-dev", task: "HARNESS-FEATURE: FEAT-43-long-run\none" },
        { agent: "harness-dev-ops", task: "HARNESS-FEATURE: FEAT-43-long-run\ntwo" },
      ],
    };
    expect(await handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "call-ok", input,
    }, ctx)).toBeUndefined();
    await handlers.get("tool_result")?.({
      toolName: "task",
      toolCallId: "call-ok",
      input,
      details: {
        progress: [
          { index: 0, id: "agent-a", jobId: "job-a" },
          { index: 1, id: "agent-b", jobId: "job-b" },
        ],
      },
      content: [],
    }, ctx);
    expect(calls.filter((call) =>
      call.script === "inflight_registry.py" && call.args[0] === "attach"
    )).toHaveLength(2);

    await handlers.get("task:subagent:lifecycle")?.({
      status: "idle", agentId: "agent-a", jobId: "job-a",
    }, ctx);
    expect(await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: { data: { content: "VERDICT: PASS" } } },
    }, ctx)).toEqual({ block: true, reason: "children live" });

    await handlers.get("task:subagent:lifecycle")?.({
      status: "idle", agentId: "agent-b", jobId: "job-b",
    }, ctx);
    expect(await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: { data: { content: "VERDICT: PASS" } } },
    }, ctx)).toBeUndefined();
  });

  // --- F1. DEC-100: only exit 2 blocks. Fails on the pre-fix adapter, which read an
  // absent receipt as a refusal and inverted every fail-open branch into a hard block.
  test("a guard pass-through with no claim receipt allows the dispatch", async () => {
    const { handlers } = fixture();
    await start(handlers);
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    expect(await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-passthrough",
      input: { agent: "scout", task: "passthrough" },
    }, ctx)).toBeUndefined();
  });

  test("a claimless dispatch in a batch does not roll back its siblings' claims", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    expect(await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-mixed",
      input: {
        context: "shared",
        tasks: [
          { agent: "harness-backend-dev", task: "HARNESS-FEATURE: FEAT-43-long-run\nallow" },
          { agent: "scout", task: "passthrough" },
        ],
      },
    }, ctx)).toBeUndefined();
    expect(calls.filter((call) =>
      call.script === "inflight_registry.py" && call.args[0] === "release"
    )).toHaveLength(0);
  });

  // --- F2. DEC-204 captures the assignment message, once, as `user`. Both cases below
  // THROW on the pre-fix adapter, from inside an async pi.on handler.
  test("a tool result echoing another feature's marker cannot re-key the session", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    const reconciled = (call: { script: string; args: string[] }) =>
      call.script === "inflight_registry.py" && call.args[0] === "reconcile";
    const before = calls.filter(reconciled).length;
    await handlers.get("message_end")?.({
      message: {
        role: "toolResult",
        content: [{ type: "text", text: "HARNESS-FEATURE: FEAT-99-other-feature\nnotes" }],
      },
    }, ctx);
    expect(calls.filter(reconciled).length).toBe(before);
  });

  test("a later user message cannot re-key the captured feature", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    const reconciled = (call: { script: string; args: string[] }) =>
      call.script === "inflight_registry.py" && call.args[0] === "reconcile";
    const before = calls.filter(reconciled).length;
    await handlers.get("message_update")?.({
      message: {
        role: "user",
        content: [{ type: "text", text: "HARNESS-FEATURE: FEAT-99-other-feature\nlater" }],
      },
    }, ctx);
    expect(calls.filter(reconciled).length).toBe(before);
  });

  // -------------------------------------------------------------------------
  // THE EDIT ROUTE. Added 2026-08-30, after a line-anchored edit corrupted a
  // feature.json that gh-sync.py had rewritten between the read and the write,
  // and nothing refused it.
  //
  // postDomain hands an `edit` result to check-domain.sh --post via
  // extractEditPaths(...).map(...). An empty array yields ZERO runner calls and
  // no diagnostic of any kind, because no process is ever spawned. Until these
  // cases the suite drove `task` eight times and `edit` NOT ONCE: a regression
  // that emptied that array would have kept the suite green while silently
  // disabling the shape gate on every file an agent edits.
  // -------------------------------------------------------------------------
  const editCtx = {
    cwd: "/repo",
    sessionManager: { getSessionId: () => "parent-session" },
  };

  const editResult = (patch: unknown) => ({
    toolName: "edit",
    toolCallId: "call-edit",
    input: { input: patch },
    content: [{ type: "text", text: "ok" }],
  });

  const postPaths = (calls: Array<{ script: string; args: string[]; payload: Record<string, unknown> }>) =>
    calls
      .filter((call) => call.script === "check-domain.sh" && call.args.includes("--post"))
      .map((call) => (call.payload as any).tool_input.file_path);

  test("a hashline edit reaches check-domain.sh --post carrying the edited path", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    // The exact file and tag shape of the 2026-08-30 corruption.
    const path = ".harness/harness/features/FEAT-44-omp-context-advisory/feature.json";
    await handlers.get("tool_result")?.(
      editResult(`[${path}#5314]\nPUT 11.=11:\n+  "id": "2026-08-29-01-product",`),
      editCtx,
    );
    const post = calls.filter((call) =>
      call.script === "check-domain.sh" && call.args.includes("--post"));
    expect(post.length).toBe(1);
    expect((post[0].payload as any).tool_input).toEqual({ file_path: path });
    // Named `Edit`, not `edit`: check-domain.sh matches the Claude-shaped name.
    expect((post[0].payload as any).tool_name).toBe("Edit");
  });

  test("every file of a multi-section edit is gated, not just the first", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    await handlers.get("tool_result")?.(
      editResult("[a/one.json#A1B2]\nPUT 1.=1:\n+x\n[b/two.yaml#00FF]\nPUT 2.=2:\n+y"),
      editCtx,
    );
    expect(postPaths(calls)).toEqual(["a/one.json", "b/two.yaml"]);
  });

  test("an MV destination is gated - a rename lands bytes at a new path", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    await handlers.get("tool_result")?.(
      editResult("[src/old.ts#BEEF]\nMV src/new.ts"),
      editCtx,
    );
    expect(postPaths(calls)).toEqual(["src/old.ts", "src/new.ts"]);
  });

  test("a non-string patch spawns no gate, and SAYS SO (S2)", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const result = await handlers.get("tool_result")?.(
      editResult({ sections: ["a/one.json"] }), editCtx);
    // extractEditPaths returns [] for any non-string input, so `.map()` spawns
    // nothing. The gate genuinely cannot run: no path was extracted, so there is
    // no file to check. What S2 fixes is that the absence is now ANNOUNCED rather
    // than being byte-identical to a gate that ran and passed.
    expect(postPaths(calls)).toEqual([]);
    const texts = ((result as any).content as Array<{ text: string }>).map((part) => part.text);
    expect(texts.some((t) => t.includes("neither the pre-write nor the post-write"))).toBe(true);
    // AND IT MUST NOT COST A GATE. No isError key at all, not merely a falsy one:
    // a notice that turned a normal result into an error would be worse than the
    // silence it replaces.
    expect("isError" in (result as any)).toBe(false);
  });

  test("a well-formed edit is gated and stays silent - no spurious S2 notice", async () => {
    const { handlers } = fixture();
    await start(handlers);
    const result = await handlers.get("tool_result")?.(
      editResult("[a/one.json#A1B2]\nPUT 1.=1:\n+x"), editCtx);
    // The gate ran, so there is nothing to announce. If this reddens, every edit
    // in every session just started carrying a notice.
    expect(result).toBeUndefined();
  });

  // -------------------------------------------------------------------------
  // THE PRE-DOMAIN EDIT ROUTE (M1, raised by the cycle-0 panel).
  //
  // preDomain carries the IDENTICAL silent-zero `.map()`, and it is the BLOCKING
  // gate: `reason = firstBlock(preDomain(...))` at :684. A zero extraction there
  // is strictly worse than on postDomain — the edit LANDS unchecked rather than
  // merely going unreported. Every case above filters on `--post`, so by
  // construction none of them touched this route: neutering it changed nothing.
  // -------------------------------------------------------------------------
  test("a hashline edit is gated BEFORE it lands - check-domain.sh with no --post", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const path = ".harness/harness/features/FEAT-44-omp-context-advisory/feature.json";
    const blocked = await handlers.get("tool_call")?.(
      editResult(`[${path}#5314]\nPUT 11.=11:\n+  "id": "x",`), editCtx);
    const pre = calls.filter((call) =>
      call.script === "check-domain.sh" && !call.args.includes("--post"));
    expect(pre.length).toBe(1);
    expect((pre[0].payload as any).tool_input).toEqual({ file_path: path });
    expect((pre[0].payload as any).tool_name).toBe("Edit");
    // The fixture's runner does not block, so a clean edit proceeds.
    expect(blocked).toBeUndefined();
  });

  test("every file of a multi-section edit is gated before it lands", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    await handlers.get("tool_call")?.(
      editResult("[a/one.json#A1B2]\nPUT 1.=1:\n+x\n[b/two.yaml#00FF]\nPUT 2.=2:\n+y"),
      editCtx);
    expect(calls
      .filter((call) => call.script === "check-domain.sh" && !call.args.includes("--post"))
      .map((call) => (call.payload as any).tool_input.file_path))
      .toEqual(["a/one.json", "b/two.yaml"]);
  });

  test("a non-string patch reaches no pre-write gate and does not block the edit", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const blocked = await handlers.get("tool_call")?.(
      editResult({ sections: ["a/one.json"] }), editCtx);
    // MEASURED, not assumed: the preventive gate spawns nothing and the edit is
    // allowed through. Blocking instead would be a fail-closed enforcement change
    // -- it would refuse every edit whose payload shape the extractor cannot read
    // -- so it is recorded as an open decision, not taken silently here. The S2
    // notice on the RESULT is what tells the operator both checks were skipped.
    expect(calls.filter((call) => call.script === "check-domain.sh")).toEqual([]);
    expect(blocked).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// FEAT-44 (issue #923) — the OMP-native orchestrator context advisory.
//
// Written BEFORE the implementation, per T-01. Every case below except the
// installed-OMP host-surface one imports exports that do not exist yet, so this
// suite MUST be red until T-02 and T-03 land. A green suite here means
// production code was written out of order.
// ---------------------------------------------------------------------------

const ANCHORED_FIXTURE = join(import.meta.dir, "omp-session-anchored.fixture.jsonl");
const ANCHORLESS_FIXTURE = join(import.meta.dir, "omp-session-anchorless.fixture.jsonl");

// The newest anchor in the anchored fixture. Deliberately distinct from 200000
// (the default), 150000 (the resolver test) and 223029 (the ratio test), so a
// hardcoded return cannot satisfy any of them. Provenance: notes/fixture-provenance.md.
const NEWEST_ANCHOR_TOKENS = 28614;

// Spelled literally on purpose. A test that reads CONTEXT_TOKENS_FIELD back from
// the module cannot detect the constant itself being wrong.
const TOKENS_FIELD = "message.contextSnapshot.promptTokens";

describe("readContextAnchor", () => {
  test("returns the newest anchor's promptTokens from a captured nested transcript", () => {
    expect(readContextAnchor(ANCHORED_FIXTURE)).toEqual({
      kind: "tokens",
      tokens: NEWEST_ANCHOR_TOKENS,
    });
  });

  test("widens past the initial window when the anchor sits far beyond it", () => {
    const dir = mkdtempSync(join(tmpdir(), "feat44-widen-"));
    const padded = join(dir, "padded.jsonl");
    const pad = JSON.stringify({ type: "custom", customType: "pad", pad: "x".repeat(200 * 1024) });
    writeFileSync(padded, readFileSync(ANCHORED_FIXTURE, "utf8") + pad + "\n");
    // Reddens if the scan window is pinned to a fixed 64 KiB instead of widening.
    expect(readContextAnchor(padded)).toEqual({ kind: "tokens", tokens: NEWEST_ANCHOR_TOKENS });
  });

  test("reports inert with the scanned size and the field it looked for", () => {
    const result = readContextAnchor(ANCHORLESS_FIXTURE) as {
      kind: string; scannedBytes: number; field: string;
    };
    expect(result.kind).toBe("inert");
    expect(result.scannedBytes).toBe(statSync(ANCHORLESS_FIXTURE).size);
    expect(result.field).toBe(TOKENS_FIELD);
  });

  test("returns none for an absent path and for no path at all", () => {
    expect(readContextAnchor(undefined)).toEqual({ kind: "none" });
    expect(readContextAnchor(join(tmpdir(), "feat44-does-not-exist.jsonl"))).toEqual({ kind: "none" });
  });
});

describe("resolveSessionFile", () => {
  // Telling "the accessor moved" apart from "no session yet" is the whole point:
  // folding them together is the silent-undefined shape issue #923 exists to fix.
  //
  // NOTE: the real host surface is NOT asserted here. It cannot be, from a unit
  // test — see test-omp-session-accessor.py, which drives the actual omp binary.
  // The .d.ts assertion this describe block replaced could not work: Bun.resolveSync
  // succeeds under `bun run` but not under `bun test`, and the three copies on a
  // developer machine disagree anyway (running binary 18.0.5, bun cache 18.0.10,
  // global node_modules 17.3.8), so it would have asserted a package that is not
  // the one executing these hooks.
  test("returns the path when the accessor yields one", () => {
    const ctx = { sessionManager: { getSessionFile: () => "/tmp/fixture/own.jsonl" } };
    expect(resolveSessionFile(ctx)).toEqual({ kind: "path", path: "/tmp/fixture/own.jsonl" });
  });

  test("distinguishes a moved accessor from a session that has none yet", () => {
    const failed = { kind: "failed", accessor: "sessionManager.getSessionFile" };
    // Threw, absent, and not-a-function are all "the API moved".
    expect(resolveSessionFile({
      sessionManager: { getSessionFile: () => { throw new Error("gone"); } },
    })).toEqual(failed);
    expect(resolveSessionFile({ sessionManager: {} })).toEqual(failed);
    expect(resolveSessionFile({})).toEqual(failed);
    // A clean call returning nothing usable is NOT a failure — it is no session yet.
    expect(resolveSessionFile({ sessionManager: { getSessionFile: () => "" } }))
      .toEqual({ kind: "absent" });
    expect(resolveSessionFile({ sessionManager: { getSessionFile: () => undefined } }))
      .toEqual({ kind: "absent" });
  });
});

describe("resolveContextWarnTokens", () => {
  function rootWith(budgets: Record<string, unknown> | undefined) {
    const root = mkdtempSync(join(tmpdir(), "feat44-cfg-"));
    const dir = join(root, ".harness");
    require("node:fs").mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "harness.json"), JSON.stringify(budgets ? { budgets } : {}));
    return root;
  }

  test("reads the configured budget", () => {
    // 150000 differs from the default, so a mutation back to a hardcoded 200000 reddens.
    expect(resolveContextWarnTokens(rootWith({ orchestrator_context_warn_tokens: 150000 }))).toBe(150000);
  });

  test("falls back to the declared default when the key is absent", () => {
    expect(resolveContextWarnTokens(rootWith(undefined))).toBe(DEFAULT_CONTEXT_WARN_TOKENS);
    expect(DEFAULT_CONTEXT_WARN_TOKENS).toBe(200000);
  });
});

describe("contextAdvisoryText", () => {
  // Two thresholds, so a hardcoded ratio string cannot pass both.
  test("computes the DEC-201 ratio against the default threshold", () => {
    expect(contextAdvisoryText(223029, 200000)).toContain("1.12x");
  });

  test("computes the DEC-201 ratio against a configured threshold", () => {
    expect(contextAdvisoryText(223029, 150000)).toContain("1.49x");
  });
});

describe("context advisory injection", () => {
  function advisoryFixture(opts: {
    sessionFile?: string | (() => string);
    blockReason?: string;
  } = {}) {
    const handlers = new Map<string, Function>();
    const pi = { on(name: string, handler: Function) { handlers.set(name, handler); } };
    const runner = (_cwd: string, script: string) => {
      if (script === "check-domain.sh" && opts.blockReason) {
        return { blocked: true, reason: opts.blockReason, stdout: "" };
      }
      return { blocked: false, stdout: "" };
    };
    registerHarnessHooks(pi, runner);
    const getSessionFile = typeof opts.sessionFile === "function"
      ? opts.sessionFile
      : () => opts.sessionFile ?? ANCHORED_FIXTURE;
    const ctx = {
      cwd: "/repo",
      sessionManager: { getSessionId: () => "own-session", getSessionFile },
    };
    return { handlers, ctx };
  }

  async function asAgent(handlers: Map<string, Function>, ctx: unknown, agentId?: string) {
    await handlers.get("before_agent_start")?.({
      systemPrompt: agentId ? [`HARNESS_AGENT_ID: ${agentId}`] : ["plain system prompt"],
    }, ctx);
  }

  const taskResult = (content: unknown[] = [{ type: "text", text: "lead digest" }]) =>
    ({ toolName: "task", toolCallId: "call-1", input: {}, content });

  // The committed fixture's newest anchor (28614) is far UNDER the repo's
  // configured 200000, which is what makes the under-threshold case real. The
  // handler resolves its threshold from gateRoot(), not from anything a test can
  // inject, so an over-threshold wake needs a transcript carrying a bigger
  // number. Built from the real captured records, with only the newest anchor's
  // value replaced — 223029 is the code-reviewer figure measured on PR #922 that
  // crossed the line with nothing surfacing it, and it yields the 1.12x asserted
  // in contextAdvisoryText.
  function transcriptWithAnchor(tokens: number): string {
    const records = readFileSync(ANCHORED_FIXTURE, "utf8").trimEnd().split("\n");
    for (let i = records.length - 1; i >= 0; i -= 1) {
      const record = JSON.parse(records[i]);
      if (record?.message?.contextSnapshot?.promptTokens === undefined) continue;
      record.message.contextSnapshot.promptTokens = tokens;
      records[i] = JSON.stringify(record);
      break;
    }
    const path = join(mkdtempSync(join(tmpdir(), "feat44-anchor-")), "anchor.jsonl");
    writeFileSync(path, records.join("\n") + "\n");
    return path;
  }
  const overThresholdTranscript = () => transcriptWithAnchor(223029);

  test("appends the advisory to the orchestrator's wake and leaves isError absent", async () => {
    const { handlers, ctx } = advisoryFixture({ sessionFile: overThresholdTranscript() });
    await asAgent(handlers, ctx, "harness-orchestrator");
    const result = await handlers.get("tool_result")?.(taskResult(), ctx);
    const content = (result as { content: Array<{ text: string }> }).content;
    expect(content[content.length - 1].text).toContain("CONTEXT");
    // Asserted as key ABSENCE, not falsiness: an unblocked wake must not invent isError.
    expect("isError" in (result as object)).toBe(false);
  });

  test("stays silent when tokens EQUAL the threshold, killing the >= mutant", async () => {
    // Added on the cycle-1 panel's F-2. The under-threshold case below uses the
    // committed fixture's 28614, and BOTH `28614 > 200000` and `28614 >= 200000`
    // are false — so it cannot distinguish `>` from `>=`, and SC-10's claim to
    // kill that mutant was untrue as tested. Only the exact boundary separates
    // them. 200000 is DEFAULT_CONTEXT_WARN_TOKENS and the value this repo's
    // harness.json carries, which is what gateRoot() resolves to here.
    const { handlers, ctx } = advisoryFixture({
      sessionFile: transcriptWithAnchor(DEFAULT_CONTEXT_WARN_TOKENS),
    });
    await asAgent(handlers, ctx, "harness-orchestrator");
    expect(await handlers.get("tool_result")?.(taskResult(), ctx)).toBeUndefined();
  });

  test("does not advise a lead", async () => {
    const { handlers, ctx } = advisoryFixture();
    await asAgent(handlers, ctx, "harness-product-lead");
    expect(await handlers.get("tool_result")?.(taskResult(), ctx)).toBeUndefined();
  });

  test("does not advise the main session", async () => {
    const { handlers, ctx } = advisoryFixture();
    await asAgent(handlers, ctx, undefined);
    expect(await handlers.get("tool_result")?.(taskResult(), ctx)).toBeUndefined();
  });

  test("does not advise on a tool result that is not the orchestrator's wake", async () => {
    const { handlers, ctx } = advisoryFixture();
    await asAgent(handlers, ctx, "harness-orchestrator");
    const notAWake = { toolName: "read", toolCallId: "call-2", input: {}, content: [] };
    expect(await handlers.get("tool_result")?.(notAWake, ctx)).toBeUndefined();
  });

  // SUBSTITUTED, and the deviation is deliberate — see the T-01 completion note.
  // The plan specified: orchestrator, over threshold, WITH a post-domain block
  // reason, asserting the result keeps isError:true and carries BOTH lines.
  // That state is unreachable: postDomain returns [] for every toolName that is
  // not write/edit/bash (harness-hooks.ts:272), while the advisory fires only on
  // toolName "task". A block reason and the advisory cannot co-occur.
  // This guards the same seam from the reachable side: a blocked bash result
  // from the orchestrator keeps isError true and must NOT gain an advisory line.
  test("a blocked non-wake result keeps isError and gains no advisory", async () => {
    const { handlers, ctx } = advisoryFixture({ blockReason: "outside your domain" });
    await asAgent(handlers, ctx, "harness-orchestrator");
    const write = {
      toolName: "write", toolCallId: "call-3",
      input: { path: "/repo/x.ts", content: "x" },
      content: [{ type: "text", text: "wrote" }],
    };
    const result = await handlers.get("tool_result")?.(write, ctx) as
      { content: Array<{ text: string }>; isError: boolean };
    expect(result.isError).toBe(true);
    expect(result.content.some((part) => part.text.includes("post-write check"))).toBe(true);
    expect(result.content.some((part) => part.text.includes("CONTEXT"))).toBe(false);
  });

  test("emits the inert notice once, naming the field, and does not repeat or re-read", async () => {
    const { handlers, ctx } = advisoryFixture({ sessionFile: ANCHORLESS_FIXTURE });
    await asAgent(handlers, ctx, "harness-orchestrator");
    const first = await handlers.get("tool_result")?.(taskResult(), ctx) as
      { content: Array<{ text: string }> };
    const notice = first.content[first.content.length - 1].text;
    expect(notice).toContain(TOKENS_FIELD);
    // The once-per-session cap makes the absence of a second notice observable.
    expect(await handlers.get("tool_result")?.(taskResult(), ctx)).toBeUndefined();
  });

  test("reports an accessor failure once, naming the accessor", async () => {
    // The branch that would otherwise collapse into the silent no-figure path —
    // which is precisely the failure shape issue #923 exists to fix.
    const { handlers, ctx } = advisoryFixture({
      sessionFile: () => { throw new Error("getSessionFile is not a function"); },
    });
    await asAgent(handlers, ctx, "harness-orchestrator");
    const first = await handlers.get("tool_result")?.(taskResult(), ctx) as
      { content: Array<{ text: string }> };
    expect(first.content[first.content.length - 1].text).toContain("sessionManager.getSessionFile");
    expect(await handlers.get("tool_result")?.(taskResult(), ctx)).toBeUndefined();
  });

  test("stays silent at or under the threshold and returns the content untouched", async () => {
    // REQ-01's no-extra-token promise. Without this, a >= written where > was
    // specified ships green. The fixture anchor (28614) is far under 200000.
    const { handlers, ctx } = advisoryFixture();
    await asAgent(handlers, ctx, "harness-orchestrator");
    const content = [{ type: "text", text: "lead digest" }];
    const result = await handlers.get("tool_result")?.(taskResult(content), ctx);
    expect(result).toBeUndefined();
    expect(content).toEqual([{ type: "text", text: "lead digest" }]);
  });
});
