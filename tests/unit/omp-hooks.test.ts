import { describe, expect, test } from "bun:test";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  DEFAULT_CONTEXT_WARN_TOKENS,
  DEFAULT_PLAN_PHASE_WARN_MINUTES,
  contextAdvisoryText,
  detectHarnessAgent,
  featureJsonPath,
  gatePath,
  extractEditPaths,
  normalizeYieldInput,
  normalizeTaskDispatches,
  readContextAnchor,
  registerHarnessHooks,
  resolveContextWarnTokens,
  resolvePlanPhaseWarnMinutes,
  resolveSessionFile,
  spendAdvisoryFor,
  spendAdvisoryText,
  yieldContractText,
} from "../../.omp/extensions/harness-hooks.ts";

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

  test("keeps the current top-level yield envelope unchanged", () => {
    const input = { data: { VERDICT: "PASS" } };
    expect(normalizeYieldInput(input, "ignored")).toEqual(input);
  });

  // #1676: the five "yield with null data" exits. The digest was complete in the assistant
  // text; the envelope named `data` and carried nothing under it, and the repair keyed on the
  // key rather than the value, so the host settled a finished run as failed.
  test("repairs a yield whose data or error key is present but hollow", () => {
    const repaired = { result: { data: { content: "VERDICT: PASS" } } };
    for (const envelope of [{ data: null }, { data: "" }, { data: {} }, { data: [] },
                            { error: null }, { data: null, error: "  " }]) {
      expect(normalizeYieldInput({ result: envelope }, "VERDICT: PASS")).toEqual(repaired);
    }
  });

  test("keeps a real error envelope, and leaves a hollow one alone with nothing to repair from", () => {
    const failed = { result: { error: "tool crashed" } };
    expect(normalizeYieldInput(failed, "VERDICT: PASS")).toEqual(failed);
    const hollow = { result: { data: null } };
    expect(normalizeYieldInput(hollow, "   ")).toEqual(hollow);
  });
});

// B-1 (FEAT-42 review panel). runPolicy chose the gate executable with `join(cwd, BIN,
// script)` against a caller-supplied ctx.cwd, so the binary enforcing a policy was selected
// by the party the policy governs — six gates, eleven call sites, no coverage at all. These
// cases assert the path is a function of THIS MODULE's location and of nothing else.
describe("gatePath", () => {
  test("resolves under the repository that ships this extension", () => {
    const p = gatePath("check-domain.py");
    expect(p.endsWith("/.agents/skills/harness/bin/check-domain.py")).toBe(true);
    expect(existsSync(p)).toBe(true);
  });

  test("is byte-identical whatever the process working directory is", () => {
    const before = process.cwd();
    const first = gatePath("check-domain.py");
    try {
      process.chdir(tmpdir());
      expect(gatePath("check-domain.py")).toBe(first);
    } finally {
      process.chdir(before);
    }
  });

  // THE PAIRED HALF. Without it the two cases above are satisfied by a gatePath that
  // returns a constant: this one proves the script name still reaches the result.
  test("the script name still selects the file", () => {
    expect(gatePath("bash-write-guard.py")).not.toBe(gatePath("check-domain.py"));
    expect(gatePath("bash-write-guard.py").endsWith("bash-write-guard.py")).toBe(true);
  });
});

describe("OMP task lifecycle adapter", () => {
  function fixture() {
    const handlers = new Map<string, Function>();
    const calls: Array<{ script: string; args: string[]; payload: Record<string, unknown> }> = [];
    const active = new Set(["agent-a", "agent-b"]);
    let claim = 0;
    const lineageClaims = new Map<string, {
      agent: string;
      feature: string;
      agentId?: string;
      parentAgentId?: string;
    }>();
    lineageClaims.set("fixture-parent", {
      agent: "harness-eng-lead",
      feature: "FEAT-43-long-run",
      agentId: "LeadOne",
      parentAgentId: "OrchestratorOne",
    });
    const option = (args: string[], name: string) => {
      const index = args.indexOf(name);
      return index >= 0 ? args[index + 1] : undefined;
    };
    const lifecycle: Function[] = [];
    const pi = {
      on(name: string, handler: Function) {
        handlers.set(name, handler);
      },
      events: {
        on(channel: string, handler: Function) {
          if (channel === "task:subagent:lifecycle") lifecycle.push(handler);
          return () => {};
        },
      },
    };
    const settle = (data: Record<string, unknown>) => lifecycle.forEach((handler) => handler(data));
    const runner = (
      _cwd: string,
      script: string,
      args: string[],
      payload: Record<string, unknown>,
    ) => {
      calls.push({ script, args, payload });
      if (script === "inject-expertise.py") return {
        blocked: false,
        stdout: JSON.stringify({
          hookSpecificOutput: {
            hookEventName: "SubagentStart",
            additionalContext: "injected expertise",
          },
        }),
      };
      if (script === "dispatch-guard.py") {
        const task = (payload.tool_input as Record<string, unknown>).task;
        if (task === "deny") return { blocked: true, reason: "denied", stdout: "" };
        // The guard's FAIL-OPEN shape: exit 0, nothing on stdout. Seven branches of
        // dispatch-guard.py return exactly this (:34, :38, :72, :112, :138, :145, :187).
        // Absent from this fixture, no test could execute the pass-through path and F1
        // was invisible to a green suite.
        if (task === "passthrough") return { blocked: false, stdout: "" };
        claim += 1;
        const claimId = `claim-${claim}`;
        const dispatchedAgent = String((payload.tool_input as Record<string, unknown>).agent);
        lineageClaims.set(claimId, {
          agent: dispatchedAgent,
          feature: "FEAT-43-long-run",
        });
        return {
          blocked: false,
          stdout: JSON.stringify({
            harness_claim: {
              root: "/repo",
              feature: "FEAT-43-long-run",
              agent: dispatchedAgent,
              claim_id: claimId,
            },
          }),
        };
      }
      if (script === "inflight_registry.py" && args[0] === "attach") {
        const claimId = option(args, "--claim-id");
        const claimRecord = claimId ? lineageClaims.get(claimId) : undefined;
        if (!claimRecord) {
          return { blocked: true, reason: "runtime lineage attach refused", stdout: "" };
        }
        const agentId = option(args, "--agent-id");
        const parentAgentId = option(args, "--parent-agent-id");
        if ((agentId && claimRecord.agentId && claimRecord.agentId !== agentId)
          || (parentAgentId && claimRecord.parentAgentId
            && claimRecord.parentAgentId !== parentAgentId)) {
          return { blocked: true, reason: "runtime lineage attach refused", stdout: "" };
        }
        if (agentId) claimRecord.agentId = agentId;
        if (parentAgentId) claimRecord.parentAgentId = parentAgentId;
        return { blocked: false, stdout: "" };
      }
      // T-01's run-start over this fixture's claim map: reuse the exact id (refusing another
      // parent's), bind the parent's unique unbound receipt, or create.
      if (script === "inflight_registry.py" && args[0] === "run-start") {
        const agent = option(args, "--agent");
        const feature = option(args, "--feature");
        const agentId = option(args, "--agent-id");
        const parentAgentId = option(args, "--parent-agent-id");
        const mine = [...lineageClaims.values()].filter((claimRecord) =>
          claimRecord.agent === agent && claimRecord.feature === feature);
        const exact = mine.find((claimRecord) => claimRecord.agentId === agentId);
        const answer = (value: Record<string, unknown>) => ({
          blocked: value.ok !== true, stdout: JSON.stringify(value),
        });
        if (exact && exact.parentAgentId && exact.parentAgentId !== parentAgentId) {
          return answer({ ok: false, cause: "lineage", retryable: false,
            message: `run ${agentId} is already claimed under a different parent` });
        }
        if (exact) return answer({ ok: true, outcome: "reused" });
        const receipts = mine.filter((claimRecord) =>
          !claimRecord.agentId && claimRecord.parentAgentId === parentAgentId);
        if (receipts.length === 1) {
          receipts[0].agentId = agentId;
          return answer({ ok: true, outcome: "bound" });
        }
        lineageClaims.set(`run-${agentId}`, {
          agent: String(agent), feature: String(feature), agentId, parentAgentId,
        });
        return answer({ ok: true, outcome: "created" });
      }
      if (script === "inflight_registry.py" && args[0] === "release-run") {
        const agentId = option(args, "--agent-id");
        const found = [...lineageClaims.values()].filter((claimRecord) =>
          claimRecord.agentId === agentId);
        if (found.length !== 1) {
          return { blocked: true, stdout: JSON.stringify({ ok: false, cause: "not-found", retryable: false,
            message: `no live claim is bound to run ${agentId}` }) };
        }
        active.delete(String(agentId));
        return { blocked: false, stdout: JSON.stringify({ ok: true, feature: found[0].feature, root: "/repo" }) };
      }
      if (script === "inflight_registry.py" && args[0] === "find-run") {
        const agentId = option(args, "--agent-id");
        const found = [...lineageClaims.values()].filter((claimRecord) =>
          claimRecord.agentId === agentId);
        return found.length === 1
          ? { blocked: false, stdout: JSON.stringify({ ok: true, feature: found[0].feature, root: "/repo" }) }
          : { blocked: true, stdout: JSON.stringify({ ok: false, cause: "not-found", retryable: false,
            message: `no live claim is bound to run ${agentId}` }) };
      }
      if (script === "inflight_registry.py" && args[0] === "authorize") {
        const agent = option(args, "--agent");
        const feature = option(args, "--feature");
        const agentId = option(args, "--agent-id");
        const parentAgentId = option(args, "--parent-agent-id");
        if (agentId === "AuthorizeError") {
          return { blocked: false, reason: "authorization gate crashed", stdout: "" };
        }
        const candidates = [...lineageClaims.values()].filter((claimRecord) =>
          claimRecord.agent === agent
          && claimRecord.feature === feature
          && claimRecord.parentAgentId === parentAgentId
          && (!claimRecord.agentId || claimRecord.agentId === agentId));
        const exact = candidates.filter((claimRecord) => claimRecord.agentId === agentId);
        const selected = exact.length === 1
          ? exact[0]
          : exact.length === 0 && candidates.length === 1
            ? candidates[0]
            : undefined;
        if (!selected || !agentId) {
          return { blocked: true, reason: "runtime lineage not authorized", stdout: "" };
        }
        selected.agentId = agentId;
        return { blocked: false, stdout: "" };
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
      if (script === "plan-sign-gate.py") {
        const command = ((payload.tool_input as Record<string, unknown> | undefined)?.command as string) || "";
        if (command.includes("sign-approval")) {
          return { blocked: true, reason: "plan-sign-gate: refused", stdout: "" };
        }
        return { blocked: false, stdout: "" };
      }
      return { blocked: false, stdout: "" };
    };
    registerHarnessHooks(pi, runner);
    return { handlers, calls, runner, settle };
  }

  async function start(
    handlers: Map<string, Function>,
    ctx: Record<string, unknown> = {
      cwd: "/repo",
      agentId: "LeadOne",
      parentAgentId: "OrchestratorOne",
      sessionManager: { getSessionId: () => "parent-session" },
    },
    agent = "harness-eng-lead",
  ) {
    await handlers.get("before_agent_start")?.({
      prompt: "Complete assignment thoroughly:\n\nHARNESS-FEATURE: FEAT-43-long-run\nassignment",
      systemPrompt: [`HARNESS_AGENT_ID: ${agent}`],
    }, ctx);
    await handlers.get("message_end")?.({
      message: {
        role: "user",
        content: [{ type: "text", text: "HARNESS-FEATURE: FEAT-43-long-run\nassignment" }],
      },
    }, ctx);
  }

  test("injects context through the native Python hook", async () => {
    const { handlers, calls } = fixture();
    const ctx = {
      cwd: "/repo",
      agentId: "LeadOne",
      parentAgentId: "OrchestratorOne",
      sessionManager: { getSessionId: () => "parent-session" },
    };
    const result = await handlers.get("before_agent_start")?.({
      prompt: "HARNESS-FEATURE: FEAT-43-long-run\nlead it",
      systemPrompt: ["HARNESS_AGENT_ID: harness-eng-lead"],
    }, ctx);
    expect(calls.some((call) => call.script === "inject-expertise.py")).toBe(true);
    expect(result?.message?.content).toBe("injected expertise");
  });

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

  test("refuses task dispatch when OMP exposes no runtime identity", async () => {
    const { handlers, calls } = fixture();
    const unsupportedCtx = {
      cwd: "/repo",
      sessionManager: { getSessionId: () => "main-session" },
    };
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, unsupportedCtx);
    const result = await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-orchestrator",
      input: {
        agent: "harness-orchestrator",
        name: "OrchestratorOne",
        task: "HARNESS-FEATURE: FEAT-43-long-run\nrun the feature",
      },
    }, unsupportedCtx);
    expect(result?.block).toBe(true);
    expect(result?.reason).toContain("runtime lineage capability");
    expect(calls.some((call) => call.script === "dispatch-guard.py")).toBe(false);
  });

  test("refuses governed mutation when OMP omits the parent runtime identity", async () => {
    const { handlers, calls } = fixture();
    const partialCtx = {
      cwd: "/repo",
      agentId: "OrchestratorOne",
      sessionManager: { getSessionId: () => "orchestrator-session" },
    };
    await start(handlers, partialCtx, "harness-orchestrator");
    const result = await handlers.get("tool_call")?.({
      toolName: "write",
      toolCallId: "call-write",
      input: { path: "/repo/.harness/state.json", content: "{}" },
    }, partialCtx);
    expect(result?.block).toBe(true);
    expect(result?.reason).toContain("runtime lineage capability");
    expect(calls.some((call) =>
      call.script === "inflight_registry.py" && call.args[0] === "authorize")).toBe(false);
  });

  test("claims and authorizes the Main-to-orchestrator runtime edge", async () => {
    const { handlers, calls, runner } = fixture();
    const mainCtx = {
      cwd: "/repo",
      agentId: "Main",
      sessionManager: { getSessionId: () => "main-session" },
    };
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx);
    const dispatched = await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-orchestrator",
      input: {
        agent: "harness-orchestrator",
        name: "OrchestratorOne",
        task: "HARNESS-FEATURE: FEAT-43-long-run\nrun the feature",
      },
    }, mainCtx);
    expect(dispatched).toBeUndefined();
    const dispatchCall = calls.find((call) => call.script === "dispatch-guard.py");
    expect(dispatchCall?.payload.agent_type).toBe("Main");
    expect(dispatchCall?.payload.harness_agent_id).toBe("Main");
    const parentAttach = calls.find((call) =>
      call.script === "inflight_registry.py"
      && call.args[0] === "attach"
      && call.args.includes("Main"));
    expect(parentAttach).toBeDefined();
    expect(parentAttach?.args).not.toContain("--agent-id");

    const childHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { childHandlers.set(name, handler); },
      events: { on: () => () => {} },
    }, runner);
    const childCtx = {
      cwd: "/repo",
      agentId: "OrchestratorOne",
      parentAgentId: "Main",
      sessionManager: { getSessionId: () => "orchestrator-session" },
    };
    await start(childHandlers, childCtx, "harness-orchestrator");
    expect(await childHandlers.get("tool_call")?.({
      toolName: "write",
      toolCallId: "call-write",
      input: { path: "/repo/.harness/state.json", content: "{}" },
    }, childCtx)).toBeUndefined();
    expect(calls.some((call) =>
      call.script === "inflight_registry.py"
      && call.args[0] === "authorize"
      && call.args.includes("OrchestratorOne")
      && call.args.includes("Main"))).toBe(true);
  });

  test("a named child binds at run start and inherits write and Bash policy", async () => {
    const { handlers, calls, runner } = fixture();
    const parentCtx = {
      cwd: "/repo",
      agentId: "LeadOne",
      parentAgentId: "OrchestratorOne",
      sessionManager: { getSessionId: () => "lead-session" },
    };
    await start(handlers, parentCtx);
    const dispatched = await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-child",
      input: {
        agent: "harness-backend-dev",
        name: "BackendOne",
        task: "HARNESS-FEATURE: FEAT-43-long-run\nimplement it",
      },
    }, parentCtx);
    expect(dispatched).toBeUndefined();
    const parentAttach = calls.find((call) =>
      call.script === "inflight_registry.py"
      && call.args[0] === "attach"
      && call.args.includes("--parent-agent-id"));
    expect(parentAttach?.args).toContain("LeadOne");
    expect(parentAttach?.args).not.toContain("BackendOne");

    const childHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { childHandlers.set(name, handler); },
      events: { on: () => () => {} },
    }, runner);
    const childCtx = {
      cwd: "/repo",
      agentId: "BackendOne",
      parentAgentId: "LeadOne",
      sessionManager: { getSessionId: () => "child-session" },
    };
    await start(childHandlers, childCtx, "harness-backend-dev");

    const beforeWrite = calls.length;
    const writeResult = await childHandlers.get("tool_call")?.({
      toolName: "write",
      toolCallId: "call-write",
      input: { path: "/repo/src/service.ts", content: "export {};" },
    }, childCtx);
    expect(writeResult).toBeUndefined();
    const writeScripts = calls.slice(beforeWrite).map((call) => call.script);
    expect(writeScripts.indexOf("inflight_registry.py")).toBeGreaterThanOrEqual(0);
    expect(writeScripts.indexOf("inflight_registry.py"))
      .toBeLessThan(writeScripts.indexOf("check-domain.py"));
    const domainCall = calls.slice(beforeWrite).find((call) =>
      call.script === "check-domain.py");
    expect(domainCall?.payload.harness_agent_id).toBe("BackendOne");
    expect(domainCall?.payload.harness_parent_agent_id).toBe("LeadOne");

    const bashResult = await childHandlers.get("tool_call")?.({
      toolName: "bash",
      toolCallId: "call-bash",
      input: { command: "printf ok", env: { EXISTING: "kept" } },
    }, childCtx);
    expect(bashResult?.input?.env).toEqual({
      EXISTING: "kept",
      HARNESS_AGENT_TYPE: "harness-backend-dev",
    });
    const bashGuard = calls.findLast((call) => call.script === "bash-write-guard.py");
    expect(bashGuard?.payload.harness_agent_id).toBe("BackendOne");
    expect(bashGuard?.payload.harness_parent_agent_id).toBe("LeadOne");
    const authorizations = calls.filter((call) =>
      call.script === "inflight_registry.py"
      && call.args[0] === "authorize"
      && call.args.includes("BackendOne")
      && call.args.includes("LeadOne"));
    expect(authorizations).toHaveLength(2);
  });

  test("blocks a sibling lineage and isolates a nested child's edit claim", async () => {
    const { handlers, runner } = fixture();
    const parentCtx = {
      cwd: "/repo",
      agentId: "LeadOne",
      parentAgentId: "OrchestratorOne",
      sessionManager: { getSessionId: () => "lead-session" },
    };
    await start(handlers, parentCtx);
    await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-child",
      input: {
        agent: "harness-backend-dev",
        name: "BackendOne",
        task: "HARNESS-FEATURE: FEAT-43-long-run\nimplement it",
      },
    }, parentCtx);

    const childHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { childHandlers.set(name, handler); },
      events: { on: () => () => {} },
    }, runner);
    const childCtx = {
      cwd: "/repo",
      agentId: "BackendOne",
      parentAgentId: "LeadOne",
      sessionManager: { getSessionId: () => "child-session" },
    };
    await start(childHandlers, childCtx, "harness-backend-dev");
    await childHandlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-grandchild",
      input: {
        agent: "harness-data-engineer",
        name: "DataOne",
        task: "HARNESS-FEATURE: FEAT-43-long-run\nchange the schema",
      },
    }, childCtx);

    const goodHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { goodHandlers.set(name, handler); },
      events: { on: () => () => {} },
    }, runner);
    const goodCtx = {
      cwd: "/repo",
      agentId: "DataOne",
      parentAgentId: "BackendOne",
      sessionManager: { getSessionId: () => "grandchild-session" },
    };
    await start(goodHandlers, goodCtx, "harness-data-engineer");
    expect(await goodHandlers.get("tool_call")?.({
      toolName: "edit",
      toolCallId: "call-edit-good",
      input: { input: "[schema.sql#A1B2]\nPUT 1.=1:\n+select 1;" },
    }, goodCtx)).toBeUndefined();

    const siblingHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { siblingHandlers.set(name, handler); },
      events: { on: () => () => {} },
    }, runner);
    const siblingCtx = {
      cwd: "/repo",
      agentId: "DataOne",
      parentAgentId: "LeadOne",
      sessionManager: { getSessionId: () => "sibling-session" },
    };
    await start(siblingHandlers, siblingCtx, "harness-data-engineer");
    const blocked = await siblingHandlers.get("tool_call")?.({
      toolName: "edit",
      toolCallId: "call-edit-blocked",
      input: { input: "[schema.sql#A1B2]\nPUT 1.=1:\n+select 2;" },
    }, siblingCtx);
    expect(blocked?.block).toBe(true);
    expect(blocked?.reason).toContain("already claimed under a different parent");
  });

  test("fails closed when runtime lineage authorization cannot run", async () => {
    const { runner } = fixture();
    const childHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { childHandlers.set(name, handler); },
      events: { on: () => () => {} },
    }, runner);
    const childCtx = {
      cwd: "/repo",
      agentId: "AuthorizeError",
      parentAgentId: "LeadOne",
      sessionManager: { getSessionId: () => "child-session" },
    };
    await start(childHandlers, childCtx, "harness-backend-dev");
    expect(await childHandlers.get("tool_call")?.({
      toolName: "write",
      toolCallId: "call-write-error",
      input: { path: "src/x.ts", content: "unsafe" },
    }, childCtx)).toEqual({ block: true, reason: "authorization gate crashed" });
  });

  test("blocks an empty structured yield instead of taking the hook's empty-message pass-through", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    await handlers.get("task:subagent:lifecycle")?.({
      status: "idle", agentId: "agent-a", jobId: "job-a",
    }, ctx);
    await handlers.get("task:subagent:lifecycle")?.({
      status: "idle", agentId: "agent-b", jobId: "job-b",
    }, ctx);

    const result = await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: {} },
    }, ctx);
    expect(result?.block).toBe(true);
    expect(result?.reason).toContain("VERDICT");
    expect(calls.filter((call) => call.script === "validate-digest.py")).toHaveLength(0);
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
    expect(scripts.indexOf("gh-close-gate.py")).toBeGreaterThan(-1);
    expect(scripts.indexOf("gh-close-gate.py")).toBeLessThan(scripts.indexOf("branch-create-gate.py"));
    expect(scripts.indexOf("branch-create-gate.py")).toBeLessThan(scripts.indexOf("bash-write-guard.py"));
    expect(scripts.indexOf("merge-gate.py")).toBeGreaterThan(scripts.indexOf("bash-write-guard.py"));
    expect(scripts.indexOf("merge-gate.py")).toBeGreaterThan(scripts.indexOf("plan-sign-gate.py"));

  });

  // BUG-1132: plan-sign-gate.py (REQ-05/DEC-120 — only the main session signs an approval) is
  // wired into `.claude/settings.json` for native Claude Code but was never added to this bash
  // gate list, so a `plan-merge.py sign-approval` Bash call under OMP reached NEITHER a deny
  // NOR even an invocation of the script. This asserts both: the gate runs on every bash call,
  // and its `blocked` decision is honoured rather than swallowed.
  test("BUG-1132: plan-sign-gate.py runs on a Bash call and its refusal blocks the tool call", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const result = await handlers.get("tool_call")?.({
      toolName: "bash",
      input: { command: "python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file p.yaml --by x --date 2026-09-01" },
    }, { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } });
    expect(calls.some((call) => call.script === "plan-sign-gate.py")).toBe(true);
    expect(result).toEqual({ block: true, reason: "plan-sign-gate: refused" });
  });

  // NEGATIVE CONTROL: an ordinary Bash call with no `sign-approval` in it must still run the
  // gate (proving the wiring is unconditional, not scoped by a prior positive result) and must
  // NOT be blocked by it.
  test("BUG-1132 negative control: plan-sign-gate.py runs but does not block an ordinary Bash call",
       async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const result = await handlers.get("tool_call")?.({
      toolName: "bash",
      input: { command: "git status --porcelain" },
    }, { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } });
    expect(calls.some((call) => call.script === "plan-sign-gate.py")).toBe(true);
    // Not blocked. #1103 also merges HARNESS_AGENT_TYPE into every allowed bash call's env
    // (asserted on its own below), so this no longer stays `undefined` — it now carries a
    // revised input, and the thing this negative control must still prove is `block` absent.
    expect(result?.block).toBeUndefined();
  });

  // #1103: cmd_sign_approval now checks its own caller's identity rather than relying solely
  // on plan-sign-gate.py's text-parsing denylist (BUG-1132's own commit). That check reads
  // HARNESS_AGENT_TYPE from its own process environment — this proves the OMP host is the one
  // actually setting it, from the SAME `currentAgent` the hook payload already carries, and
  // that it MERGES into any env the caller's own command already specified rather than
  // clobbering it.
  test("#1103: a governed agent's bash call carries HARNESS_AGENT_TYPE, merged with its own env",
       async () => {
    const { handlers } = fixture();
    await start(handlers);
    const result = await handlers.get("tool_call")?.({
      toolName: "bash",
      input: { command: "echo hi", env: { EXISTING: "kept" } },
    }, { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } });
    expect(result?.input?.env).toEqual({
      EXISTING: "kept",
      HARNESS_AGENT_TYPE: "harness-eng-lead",
    });
  });

  // NEGATIVE CONTROL: a refused command must not ALSO carry a revised input — `firstBlock`'s
  // `reason` and `revisedInput` are mutually exclusive branches in the real handler, and a
  // block that also returned an input would be an inconsistent instruction to the caller.
  test("#1103 negative control: a refused sign-approval call carries no revised input",
       async () => {
    const { handlers } = fixture();
    await start(handlers);
    const result = await handlers.get("tool_call")?.({
      toolName: "bash",
      input: { command: "python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file p.yaml --by x --date 2026-09-01" },
    }, { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } });
    expect(result).toEqual({ block: true, reason: "plan-sign-gate: refused" });
    expect(result?.input).toBeUndefined();
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
      toolName: "yield", input: { data: { content: "VERDICT: PASS" } },
    }, ctx)).toBeUndefined();
  });

  // #1677: the operator's pin rides in the assignment message — the one text the reviewer
  // does not author — and reaches validate-digest.py as harness_review_pin. A pin in a
  // later user turn is not a source.
  test("forwards the assignment's HARNESS-REVIEW-PIN to the digest validator", async () => {
    const { handlers, calls } = fixture();
    const ctx = {
      cwd: "/repo", agentId: "Lead.Child", parentAgentId: "Lead",
      sessionManager: { getSessionId: () => "parent-session" },
    };
    await handlers.get("before_agent_start")?.({
      prompt: "HARNESS-FEATURE: FEAT-43-long-run\nreview it",
      systemPrompt: ["HARNESS_AGENT_ID: harness-code-reviewer"],
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text",
        text: "HARNESS-FEATURE: FEAT-43-long-run\nHARNESS-REVIEW-PIN: ab0c9987\nreview it" }] },
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text", text: "HARNESS-REVIEW-PIN: deadbeef" }] },
    }, ctx);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: { data: { content: "VERDICT: PASS" } } },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(validation?.payload.harness_review_pin).toBe("ab0c9987");
    expect(validation?.payload.harness_feature).toBe("FEAT-43-long-run");
  });

  test("forwards no pin when the assignment carries none", async () => {
    const { handlers, calls } = fixture();
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    await start(handlers);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: { data: { content: "VERDICT: PASS" } } },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(validation?.payload.harness_review_pin).toBeUndefined();
  });

  // #1855: the mission rides the same road as the pin — the assignment message, scanned
  // once — and reaches validate-digest.py as harness_mission so a distill reader's
  // gate fields are pinned to their did-nothing spelling rather than fabricated.
  test("forwards the assignment's HARNESS-MISSION to the digest validator", async () => {
    const { handlers, calls } = fixture();
    const ctx = {
      cwd: "/repo", agentId: "Lead.Child", parentAgentId: "Lead",
      sessionManager: { getSessionId: () => "parent-session" },
    };
    await handlers.get("before_agent_start")?.({
      prompt: "HARNESS-FEATURE: FEAT-61-consolidation\ndistill your log",
      systemPrompt: ["HARNESS_AGENT_ID: harness-qa"],
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text",
        text: "HARNESS-FEATURE: FEAT-61-consolidation\nHARNESS-MISSION: distill\ndistill your log" }] },
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text", text: "HARNESS-MISSION: build" }] },
    }, ctx);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: { data: { content: "VERDICT: PASS" } } },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(validation?.payload.harness_mission).toBe("distill");
    expect(validation?.payload.harness_review_pin).toBeUndefined();
  });

  test("forwards no mission when the assignment carries none", async () => {
    const { handlers, calls } = fixture();
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    await start(handlers);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { result: { data: { content: "VERDICT: PASS" } } },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(validation?.payload.harness_mission).toBeUndefined();
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
  // postDomain hands an `edit` result to check-domain.py --post via
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
      .filter((call) => call.script === "check-domain.py" && call.args.includes("--post"))
      .map((call) => (call.payload as any).tool_input.file_path);

  test("a hashline edit reaches check-domain.py --post carrying the edited path", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    // The exact file and tag shape of the 2026-08-30 corruption.
    const path = ".harness/harness/features/FEAT-44-omp-context-advisory/feature.json";
    await handlers.get("tool_result")?.(
      editResult(`[${path}#5314]\nPUT 11.=11:\n+  "id": "2026-08-29-01-product",`),
      editCtx,
    );
    const post = calls.filter((call) =>
      call.script === "check-domain.py" && call.args.includes("--post"));
    expect(post.length).toBe(1);
    expect((post[0].payload as any).tool_input).toEqual({ file_path: path });
    // Named `Edit`, not `edit`: check-domain.py matches the Claude-shaped name.
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
  test("a hashline edit is gated BEFORE it lands - check-domain.py with no --post", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const path = ".harness/harness/features/FEAT-44-omp-context-advisory/feature.json";
    const blocked = await handlers.get("tool_call")?.(
      editResult(`[${path}#5314]\nPUT 11.=11:\n+  "id": "x",`), editCtx);
    const pre = calls.filter((call) =>
      call.script === "check-domain.py" && !call.args.includes("--post"));
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
      .filter((call) => call.script === "check-domain.py" && !call.args.includes("--post"))
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
    expect(calls.filter((call) => call.script === "check-domain.py")).toEqual([]);
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
    const pi = {
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: { on: () => () => {} },
    };
    const runner = (_cwd: string, script: string) => {
      if (script === "check-domain.py" && opts.blockReason) {
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

// ---------------------------------------------------------------------------
// FEAT-59 SC-19 — the SPEND advisory on the orchestrator's wake.
//
// The same wake path as the context advisory, the same voice, the same promise:
// it ADVISES and never refuses. The figure is what `feature-record.py spend`
// measures from feature.json — these cases spawn the REAL script through the
// fake runner, so the JSON contract between the two halves is what is tested,
// not a stub of it. Only `inflight_registry.py feature-root` is faked, to point
// the hook at a temp checkout.
// ---------------------------------------------------------------------------

describe("spendAdvisoryFor", () => {
  const spend = (minutes: number, phase: "plan" | "build", rework = 0) =>
    ({ runs: 3, wall_clock_minutes: minutes, tokens: null, phase, rework_minutes: rework, rework_rounds: 0 });

  test("plan phase compares against plan_phase_warn_minutes, strictly greater", () => {
    expect(spendAdvisoryFor(spend(91, "plan"), undefined, 90)).toContain("budgets.plan_phase_warn_minutes = 90");
    expect(spendAdvisoryFor(spend(90, "plan"), undefined, 90)).toBeUndefined();
    expect(spendAdvisoryFor(spend(91, "plan"), 10, 90)).toContain("plan phase");
  });

  test("build phase compares the REWORK WINDOW against the ruling, never the whole feature", () => {
    // 100 whole-feature minutes (plan + build) with 0 rework: under a 60-minute ruling,
    // silent — the ruling is a budget for rework, and none has happened.
    expect(spendAdvisoryFor(spend(100, "build", 0), 60, 90)).toBeUndefined();
    // 61 rework minutes: the line names the window's figure, not the whole.
    const line = spendAdvisoryFor(spend(161, "build", 61), 60, 90);
    expect(line).toContain("rework.wall_clock_minutes = 60");
    expect(line).toContain("build phase");
    expect(line).toContain("61 wall-clock minutes");
    expect(line).toContain("1.02x");
    expect(spendAdvisoryFor(spend(160, "build", 60), 60, 90)).toBeUndefined();
    // No ruling recorded: nothing to measure against, so nothing is said.
    expect(spendAdvisoryFor(spend(500, "build", 400), undefined, 90)).toBeUndefined();
  });

  test("names the measured tokens when a run carried one", () => {
    expect(spendAdvisoryText(135, 48213, "plan", "budgets.plan_phase_warn_minutes", 90))
      .toContain("48213 tokens");
    expect(spendAdvisoryText(135, null, "plan", "budgets.plan_phase_warn_minutes", 90))
      .not.toContain("tokens");
    expect(spendAdvisoryText(135, null, "plan", "budgets.plan_phase_warn_minutes", 90))
      .toContain("ADVISES and never refuses (DEC-198)");
  });
});

describe("resolvePlanPhaseWarnMinutes", () => {
  function rootWith(budgets: Record<string, unknown> | undefined) {
    const root = mkdtempSync(join(tmpdir(), "feat59-cfg-"));
    mkdirSync(join(root, ".harness"));
    writeFileSync(join(root, ".harness", "harness.json"),
      JSON.stringify(budgets === undefined ? {} : { budgets }));
    return root;
  }

  test("reads the configured value", () => {
    expect(resolvePlanPhaseWarnMinutes(rootWith({ plan_phase_warn_minutes: 30 }))).toBe(30);
  });

  test("falls back to the declared default when the key is absent", () => {
    expect(resolvePlanPhaseWarnMinutes(rootWith({}))).toBe(DEFAULT_PLAN_PHASE_WARN_MINUTES);
    expect(resolvePlanPhaseWarnMinutes(rootWith(undefined))).toBe(DEFAULT_PLAN_PHASE_WARN_MINUTES);
    expect(resolvePlanPhaseWarnMinutes("/nonexistent")).toBe(DEFAULT_PLAN_PHASE_WARN_MINUTES);
  });

  test("the shipped configuration carries the default", () => {
    // 90 in both harness.json files; the hook resolves from gateRoot(), so the
    // wake tests below rely on this figure being the one on disk.
    expect(resolvePlanPhaseWarnMinutes(join(import.meta.dir, "..", ".."))).toBe(90);
  });
});

describe("featureJsonPath", () => {
  test("finds the repo-tier layout and the flat layout, and nothing when absent", () => {
    const root = mkdtempSync(join(tmpdir(), "feat59-layout-"));
    expect(featureJsonPath(root, "FEAT-99-x")).toBeUndefined();
    mkdirSync(join(root, ".harness", "harness", "features", "FEAT-99-x"), { recursive: true });
    expect(featureJsonPath(root, "FEAT-99-x")).toBeUndefined();
    writeFileSync(join(root, ".harness", "harness", "features", "FEAT-99-x", "feature.json"), "{}");
    expect(featureJsonPath(root, "FEAT-99-x"))
      .toBe(join(root, ".harness", "harness", "features", "FEAT-99-x", "feature.json"));
    const flat = mkdtempSync(join(tmpdir(), "feat59-flat-"));
    mkdirSync(join(flat, ".harness", "features", "FEAT-99-x"), { recursive: true });
    writeFileSync(join(flat, ".harness", "features", "FEAT-99-x", "feature.json"), "{}");
    expect(featureJsonPath(flat, "FEAT-99-x"))
      .toBe(join(flat, ".harness", "features", "FEAT-99-x", "feature.json"));
  });
});

describe("spend advisory injection", () => {
  const FEATURE = "FEAT-99-spend";

  function runsSpanning(minutes: number, id = "r1") {
    const start = new Date("2026-09-11T10:00:00Z");
    const end = new Date(start.getTime() + minutes * 60_000);
    const iso = (d: Date) => d.toISOString().replace(/\.\d{3}Z$/, "+00:00");
    return [{ id, squad: "product", verdict: "PASS", agent: "harness-product-lead",
      started_at: iso(start), ended_at: iso(end), tokens: 48213 }];
  }

  function checkout(doc: Record<string, unknown> | undefined) {
    const root = mkdtempSync(join(tmpdir(), "feat59-wake-"));
    const dir = join(root, ".harness", "harness", "features", FEATURE);
    mkdirSync(dir, { recursive: true });
    if (doc) {
      writeFileSync(join(dir, "feature.json"), JSON.stringify({
        feature_id: FEATURE, branch: "none", pr: null, review_sha: "none",
        cycles_used: 0, max_total_cycles: 10, ...doc,
      }, null, 2) + "\n");
    }
    return root;
  }

  function wakeFixture(root: string) {
    const handlers = new Map<string, Function>();
    const pi = {
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: { on: () => () => {} },
    };
    const calls: Array<{ script: string; args: string[] }> = [];
    const runner = (_cwd: string, script: string, args: string[]) => {
      calls.push({ script, args });
      if (script === "inflight_registry.py" && args[0] === "feature-root") {
        return { blocked: false, stdout: `${root}\n` };
      }
      if (script === "feature-record.py") {
        // THE REAL SCRIPT, through the real gate path: the parse of its stdout
        // is the contract under test.
        const proc = spawnSync("python3", [gatePath(script), ...args], { encoding: "utf8" });
        return { blocked: false, stdout: proc.stdout || "", reason: proc.stderr || undefined };
      }
      return { blocked: false, stdout: "" };
    };
    registerHarnessHooks(pi, runner);
    const ctx = {
      cwd: root,
      sessionManager: { getSessionId: () => "own-session", getSessionFile: () => ANCHORED_FIXTURE },
    };
    return { handlers, ctx, calls };
  }

  async function asOrchestratorOn(handlers: Map<string, Function>, ctx: unknown) {
    await handlers.get("before_agent_start")?.({
      systemPrompt: ["HARNESS_AGENT_ID: harness-orchestrator", `HARNESS-FEATURE: ${FEATURE}`],
    }, ctx);
  }

  const wake = () => ({ toolName: "task", toolCallId: "call-1", input: {},
    content: [{ type: "text", text: "lead digest" }] });

  // Narrows the handler's return at the boundary once; every read below is checked.
  function patched(result: unknown): { texts: string[]; hasIsError: boolean } {
    if (!result || typeof result !== "object" || !("content" in result) || !Array.isArray(result.content)) {
      throw new Error(`expected a patched tool result, got ${JSON.stringify(result)}`);
    }
    const texts = result.content.map((part: unknown) =>
      part && typeof part === "object" && "text" in part && typeof part.text === "string" ? part.text : "");
    return { texts, hasIsError: "isError" in result };
  }

  test("over the plan budget: one SPEND line naming spend, budget and phase; isError absent", async () => {
    const { handlers, ctx } = wakeFixture(checkout({ runs: runsSpanning(135) }));
    await asOrchestratorOn(handlers, ctx);
    const result = await handlers.get("tool_result")?.(wake(), ctx);
    const line = patched(result).texts.at(-1) ?? "";
    expect(line.startsWith("SPEND: ")).toBe(true);
    expect(line).toContain("135 wall-clock minutes");
    expect(line).toContain("48213 tokens");
    expect(line).toContain("plan phase");
    expect(line).toContain("budgets.plan_phase_warn_minutes = 90");
    expect(line).toContain("1.50x");
    expect(line).toContain("ADVISES and never refuses (DEC-198)");
    expect(patched(result).hasIsError).toBe(false);
    // Exactly ONE advisory line was appended to the one content part.
    expect(patched(result).texts.length).toBe(2);
  });

  test("under the plan budget: nothing is appended", async () => {
    const { handlers, ctx, calls } = wakeFixture(checkout({ runs: runsSpanning(30) }));
    await asOrchestratorOn(handlers, ctx);
    expect(await handlers.get("tool_result")?.(wake(), ctx)).toBeUndefined();
    // The measurement WAS taken — silence is a judgement on the figure, not a skipped read.
    expect(calls.some((call) => call.script === "feature-record.py" && call.args[0] === "spend")).toBe(true);
  });

  test("after build entry: the rework ruling is the budget, measured over the rework window", async () => {
    // 135 minutes of runs, all of them plan/build — no validate-* run yet, so the
    // rework window is empty and a 60-minute ruling is not exceeded. Silence.
    const quiet = wakeFixture(checkout({
      runs: runsSpanning(135),
      github: { build_entry: "opened" },
      rework: { rounds: 2, wall_clock_minutes: 60, decision: "ruling-1" },
    }));
    await asOrchestratorOn(quiet.handlers, quiet.ctx);
    expect(await quiet.handlers.get("tool_result")?.(wake(), quiet.ctx)).toBeUndefined();
    // The same 135 minutes inside a validate run IS rework, and the ruling is exceeded. The id
    // is the corpus's date-prefixed run-dir shape: a bare `validate-validator` would pass
    // against the `startswith` window that never opened on any real ledger.
    const { handlers, ctx } = wakeFixture(checkout({
      runs: runsSpanning(135, "2026-09-11-05-validate-validator"),
      github: { build_entry: "opened" },
      rework: { rounds: 2, wall_clock_minutes: 60, decision: "ruling-1" },
    }));
    await asOrchestratorOn(handlers, ctx);
    const line = patched(await handlers.get("tool_result")?.(wake(), ctx)).texts.at(-1) ?? "";
    expect(line).toContain("build phase");
    expect(line).toContain("rework.wall_clock_minutes = 60");
    expect(line).toContain("135 wall-clock minutes");
  });
  test("after build entry with no rework ruling: nothing, even far past the plan budget", async () => {
    const { handlers, ctx } = wakeFixture(checkout({
      runs: runsSpanning(500), github: { build_entry: "opened" },
    }));
    await asOrchestratorOn(handlers, ctx);
    expect(await handlers.get("tool_result")?.(wake(), ctx)).toBeUndefined();
  });

  test("missing feature.json: nothing is appended and spend is never asked", async () => {
    const { handlers, ctx, calls } = wakeFixture(checkout(undefined));
    await asOrchestratorOn(handlers, ctx);
    expect(await handlers.get("tool_result")?.(wake(), ctx)).toBeUndefined();
    expect(calls.some((call) => call.script === "feature-record.py")).toBe(false);
  });

  test("a lead on the same feature is not advised", async () => {
    const { handlers, ctx, calls } = wakeFixture(checkout({ runs: runsSpanning(135) }));
    await handlers.get("before_agent_start")?.({
      systemPrompt: ["HARNESS_AGENT_ID: harness-eng-lead", `HARNESS-FEATURE: ${FEATURE}`],
    }, ctx);
    expect(await handlers.get("tool_result")?.(wake(), ctx)).toBeUndefined();
    expect(calls.some((call) => call.script === "feature-record.py")).toBe(false);
  });
});

// BUG-1724 (DEC-227): the HOST stamps the figure it measured onto the open run, on the
// same wake that reads spend, so the orchestrator never transcribes it. Measured on
// BUG-285-canonical-reader: 19/19 task results carried `details.results[i].tokens`,
// 0/26 `run-end` calls passed it. The real feature-record.py runs through the gate path,
// so what is asserted is the file on disk, not a recorded argv.
describe("host-stamped tokens", () => {
  const FEATURE = "FEAT-99-stamp";

  function openRun(id = "r1") {
    return [{ id, squad: "eng", verdict: "PENDING", agent: "harness-eng-lead",
      started_at: "2026-09-11T10:00:00+00:00" }];
  }

  function checkout(runs: unknown[]) {
    const root = mkdtempSync(join(tmpdir(), "bug1724-"));
    const dir = join(root, ".harness", "harness", "features", FEATURE);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "feature.json"), JSON.stringify({
      feature_id: FEATURE, branch: "none", pr: null, review_sha: "none",
      cycles_used: 0, max_total_cycles: 10, runs,
    }, null, 2) + "\n");
    return { root, featureJson: join(dir, "feature.json") };
  }

  function fixture(root: string) {
    const handlers = new Map<string, Function>();
    const pi = {
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: { on: () => () => {} },
    };
    const calls: Array<{ script: string; args: string[] }> = [];
    const runner = (_cwd: string, script: string, args: string[]) => {
      calls.push({ script, args });
      if (script === "inflight_registry.py" && args[0] === "feature-root") {
        return { blocked: false, stdout: `${root}\n` };
      }
      if (script === "feature-record.py") {
        const proc = spawnSync("python3", [gatePath(script), ...args], { encoding: "utf8" });
        return { blocked: false, stdout: proc.stdout || "", reason: proc.stderr || undefined };
      }
      return { blocked: false, stdout: "" };
    };
    registerHarnessHooks(pi, runner);
    const ctx = {
      cwd: root,
      sessionManager: { getSessionId: () => "own-session", getSessionFile: () => ANCHORED_FIXTURE },
    };
    return { handlers, ctx, calls };
  }

  async function asOrchestratorOn(handlers: Map<string, Function>, ctx: unknown) {
    await handlers.get("before_agent_start")?.({
      systemPrompt: ["HARNESS_AGENT_ID: harness-orchestrator", `HARNESS-FEATURE: ${FEATURE}`],
    }, ctx);
  }

  const wakeWith = (details: unknown) => ({ toolName: "task", toolCallId: "call-1", input: {},
    details, content: [{ type: "text", text: "lead digest" }] });

  const tokensOf = (featureJson: string, index = 0) =>
    JSON.parse(readFileSync(featureJson, "utf8")).runs[index].tokens;

  test("sums every result's integer tokens and stamps the open run BEFORE spend is read", async () => {
    const { root, featureJson } = checkout(openRun());
    const { handlers, ctx, calls } = fixture(root);
    await asOrchestratorOn(handlers, ctx);
    await handlers.get("tool_result")?.(wakeWith({
      results: [{ index: 0, exitCode: 0, tokens: 135888 }, { index: 1, exitCode: 0, tokens: 68447 }],
    }), ctx);
    expect(tokensOf(featureJson)).toBe(204335);
    const verbs = calls.filter((c) => c.script === "feature-record.py").map((c) => c.args[0]);
    expect(verbs.indexOf("stamp-tokens")).toBeGreaterThanOrEqual(0);
    expect(verbs.indexOf("stamp-tokens")).toBeLessThan(verbs.indexOf("spend"));
    expect(verbs.filter((v) => v === "stamp-tokens").length).toBe(1);
  });

  test("no result carries a figure: nothing is stamped and the run stays unmeasured (DEC-210)", async () => {
    const { root, featureJson } = checkout(openRun());
    const { handlers, ctx, calls } = fixture(root);
    await asOrchestratorOn(handlers, ctx);
    await handlers.get("tool_result")?.(wakeWith({ results: [{ index: 0, exitCode: 0 }] }), ctx);
    expect(JSON.parse(readFileSync(featureJson, "utf8")).runs[0]).not.toHaveProperty("tokens");
    expect(calls.some((c) => c.script === "feature-record.py" && c.args[0] === "stamp-tokens")).toBe(false);
    // A bare run-end then records null: the host reported nothing, and nothing was invented.
    spawnSync("python3", [gatePath("feature-record.py"), "run-end", "--file", featureJson,
      "--id", "r1", "--verdict", "PASS", "--cycles-used", "0"], { encoding: "utf8" });
    expect(tokensOf(featureJson)).toBeNull();
  });

  test("a non-integer or negative figure is not a figure", async () => {
    const { root, featureJson } = checkout(openRun());
    const { handlers, ctx } = fixture(root);
    await asOrchestratorOn(handlers, ctx);
    await handlers.get("tool_result")?.(wakeWith({
      results: [{ index: 0, tokens: "135888" }, { index: 1, tokens: -5 }, { index: 2, tokens: 12.5 }],
    }), ctx);
    expect(JSON.parse(readFileSync(featureJson, "utf8")).runs[0]).not.toHaveProperty("tokens");
  });

  test("a refused stamp (two open runs) never costs the wake: the advisory path still runs", async () => {
    const { root, featureJson } = checkout([...openRun("r1"), ...openRun("r2")]);
    const { handlers, ctx, calls } = fixture(root);
    await asOrchestratorOn(handlers, ctx);
    const result = await handlers.get("tool_result")?.(wakeWith({ results: [{ index: 0, tokens: 7 }] }), ctx);
    expect(JSON.parse(readFileSync(featureJson, "utf8")).runs.every((r: any) => !("tokens" in r))).toBe(true);
    expect(calls.some((c) => c.script === "feature-record.py" && c.args[0] === "spend")).toBe(true);
    expect(result === undefined || !("isError" in result)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// BUG-1898 T-02 — a governed run claims at run start, keyed by its runtime id.
//
// Every case drives the REAL inflight_registry.py against a fresh temp registry and
// asserts the rows it leaves and the verdict each tool call gets. Only dispatch-guard.py
// is emulated (it needs a whole checkout): a governed dispatch records the receipt the
// real guard records, through the registry's own claim_with_receipt; `passthrough` is its
// DEC-100 crash shape — exit 0, no receipt. validate-digest.py passes (T-03 owns it).
// ---------------------------------------------------------------------------
describe("BUG-1898 run-start claims on the real registry", () => {
  const FEATURE = "BUG-98-run-start";
  const REGISTRY_BIN = join(gatePath("inflight_registry.py"), "..");
  type Call = { script: string; args: string[]; payload: Record<string, unknown> };
  type Row = Record<string, unknown>;

  function python(args: string[], cwd: string) {
    const proc = spawnSync("python3", args, { cwd, encoding: "utf8" });
    const stderr = (proc.stderr || "").trim();
    if (proc.status === 2) return { blocked: true, reason: stderr, stdout: proc.stdout || "" };
    return proc.status === 0
      ? { blocked: false, stdout: proc.stdout || "" }
      : { blocked: false, reason: stderr || `exit ${proc.status}`, stdout: proc.stdout || "" };
  }

  const RECEIPT = [
    "import json, sys",
    `sys.path.insert(0, ${JSON.stringify(REGISTRY_BIN)})`,
    "import inflight_registry as reg",
    "root, agent, dispatcher, feature, pid = sys.argv[1:]",
    "entry = reg.claim_with_receipt(root, agent, dispatcher, root, feature=feature,",
    "                               supervisor_pid=int(pid))",
    "print(json.dumps({'harness_claim': {'root': root, 'feature': feature, 'agent': agent,",
    "                                    'claim_id': entry['claim_id']}}))",
  ].join("\n");

  function world(root = mkdtempSync(join(tmpdir(), "bug1898-"))) {
    const calls: Call[] = [];
    const runner = (cwd: string, script: string, args: string[], payload: Record<string, unknown>) => {
      calls.push({ script, args, payload });
      if (script === "inflight_registry.py") {
        return python([gatePath("inflight_registry.py"), ...args], cwd);
      }
      if (script === "dispatch-guard.py") {
        const input = payload.tool_input as Record<string, unknown>;
        const agent = String(input.agent);
        if (input.task === "passthrough" || !agent.startsWith("harness-")) {
          return { blocked: false, stdout: "" };
        }
        return python(["-c", RECEIPT, root, agent, String(payload.agent_type), FEATURE,
          String(process.pid)], cwd);
      }
      return { blocked: false, stdout: "" };
    };
    return { root, calls, runner };
  }

  function session(runner: Function) {
    const handlers = new Map<string, Function>();
    const bus = new Map<string, Function[]>();
    registerHarnessHooks({
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: {
        on(channel: string, handler: Function) {
          bus.set(channel, [...(bus.get(channel) || []), handler]);
          return () => {};
        },
        emit(channel: string, data: unknown) { (bus.get(channel) || []).forEach((h) => h(data)); },
      },
    }, runner as any);
    const emit = async (channel: string, data: unknown) => {
      for (const handler of bus.get(channel) || []) await handler(data);
    };
    return { handlers, emit };
  }

  function ctxFor(root: string, agentId: string, parentAgentId?: string) {
    return {
      cwd: root,
      agentId,
      ...(parentAgentId ? { parentAgentId } : {}),
      sessionManager: { getSessionId: () => `session-${agentId}` },
    };
  }

  async function begin(
    s: ReturnType<typeof session>, ctx: Record<string, unknown>, agent: string, prompt: string,
  ) {
    return s.handlers.get("before_agent_start")?.({
      prompt, systemPrompt: [`HARNESS_AGENT_ID: ${agent}`],
    }, ctx);
  }

  function rows(root: string): Row[] {
    const path = join(root, ".harness", ".inflight-claims.json");
    if (!existsSync(path)) return [];
    return (JSON.parse(readFileSync(path, "utf8")).claims || []) as Row[];
  }

  function seed(root: string, claims: Row[]) {
    mkdirSync(join(root, ".harness"), { recursive: true });
    writeFileSync(join(root, ".harness", ".inflight-claims.json"), JSON.stringify({
      schema_version: 2,
      claims: claims.map((claim, index) => ({
        claim_id: `seed-${index}`, started_at: Date.now() / 1000, cwd: root,
        dispatcher: "harness-eng-lead", runtime: "omp", supervisor_pid: process.pid,
        feature: FEATURE, ...claim,
      })),
    }));
  }

  const ASSIGN = `HARNESS-FEATURE: ${FEATURE}\nbuild the thing`;
  const write = (path = "src/x.ts") => ({
    toolName: "write", toolCallId: `w-${path}`, input: { path, content: "x" },
  });
  const blockedDigest = "VERDICT: BLOCKED\nDIGEST: cannot claim this run\nARTIFACT: none";

  async function lead(w: ReturnType<typeof world>) {
    const s = session(w.runner);
    const ctx = ctxFor(w.root, "Lead", "Orch");
    seed(w.root, [{ agent: "harness-eng-lead", agent_id: "Lead", parent_agent_id: "Orch",
      claim_id: "lead-claim" }]);
    await begin(s, ctx, "harness-eng-lead", ASSIGN);
    return { s, ctx };
  }

  const governed = (root: string) => rows(root).filter((row) => row.claim_id !== "lead-claim");

  test("a first run binds its parent's receipt to its exact id before its first write", async () => {
    const w = world();
    const parent = await lead(w);
    expect(await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "t1",
      input: { agent: "harness-backend-dev", name: "Dev", task: ASSIGN },
    }, parent.ctx)).toBeUndefined();
    expect(governed(w.root).map((row) => row.agent_id)).toEqual([undefined]);

    const child = session(w.runner);
    const childCtx = ctxFor(w.root, "Lead.Dev", "Lead");
    await begin(child, childCtx, "harness-backend-dev", ASSIGN);
    expect(governed(w.root).map((row) => [row.agent_id, row.parent_agent_id]))
      .toEqual([["Lead.Dev", "Lead"]]);
    expect(await child.handlers.get("tool_call")?.(write(), childCtx)).toBeUndefined();
  });

  // An IRC wake runs agent.prompt() directly: OMP emits agent_start for it, never
  // before_agent_start (agent-session.ts #wakeForIrc). The live probe's S2 caught the
  // run-start-only reclaim leaving the woken run's first write with no claim.
  test("a settled agent woken by message reclaims the same exact id", async () => {
    const w = world();
    const parent = await lead(w);
    const child = session(w.runner);
    const childCtx = ctxFor(w.root, "Lead.Dev", "Lead");
    await begin(child, childCtx, "harness-backend-dev", ASSIGN);
    await child.handlers.get("agent_start")?.({ type: "agent_start" }, childCtx);
    await child.handlers.get("agent_end")?.({ messages: [] }, childCtx);
    await parent.s.emit("task:subagent:lifecycle", {
      id: "Lead.Dev", agent: "harness-backend-dev", status: "completed", index: 0,
    });
    expect(governed(w.root)).toEqual([]);

    await child.handlers.get("agent_start")?.({ type: "agent_start" }, childCtx);
    expect(governed(w.root).map((row) => row.agent_id)).toEqual(["Lead.Dev"]);
    expect(await child.handlers.get("tool_call")?.(write(), childCtx)).toBeUndefined();
  });

  test("a woken run's writes are held until its wake has reclaimed", async () => {
    const w = world();
    const child = session(w.runner);
    const childCtx = ctxFor(w.root, "Lead.Dev", "Lead");
    seed(w.root, [{ agent: "harness-backend-dev", parent_agent_id: "Lead", claim_id: "r" }]);
    await begin(child, childCtx, "harness-backend-dev", ASSIGN);
    await child.handlers.get("agent_end")?.({ messages: [] }, childCtx);
    const held = await child.handlers.get("tool_call")?.(write(), childCtx) as
      { block?: boolean } | undefined;
    expect(held?.block).toBe(true);
  });

  test("a markerless revival recovers its feature from its one exact live claim", async () => {
    const w = world();
    seed(w.root, [{ agent: "harness-qa", agent_id: "Lead.Qa", parent_agent_id: "Lead" }]);
    const revived = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Qa", "Lead");
    await begin(revived, ctx, "harness-qa", "continue where you left off");
    expect(await revived.handlers.get("tool_call")?.(write(), ctx)).toBeUndefined();
    await revived.handlers.get("tool_call")?.({
      toolName: "yield", input: { data: { content: "VERDICT: PASS" } },
    }, ctx);
    const validation = w.calls.find((call) => call.script === "validate-digest.py");
    expect(validation?.payload.harness_feature).toBe(FEATURE);
    expect(rows(w.root).map((row) => row.agent_id)).toEqual(["Lead.Qa"]);
  });

  async function expectHeld(
    s: ReturnType<typeof session>, ctx: Record<string, unknown>, cause: RegExp,
  ) {
    for (const call of [
      write(),
      { toolName: "read", input: { path: "src/x.ts" } },
      { toolName: "bash", input: { command: "true" } },
      { toolName: "task", toolCallId: "t", input: { agent: "scout", task: "look" } },
      { toolName: "yield", input: { data: { content: "VERDICT: PASS\nDIGEST: done" } } },
    ]) {
      const verdict = await s.handlers.get("tool_call")?.(call, ctx);
      expect(verdict?.block).toBe(true);
      expect(verdict?.reason).toMatch(cause);
    }
    expect(await s.handlers.get("tool_call")?.({
      toolName: "yield", input: { data: { content: blockedDigest } },
    }, ctx)).toBeUndefined();
  }

  test("a markerless revival with no exact claim is held: only a BLOCKED yield passes", async () => {
    const w = world();
    seed(w.root, [{ agent: "harness-qa", agent_id: "Lead.Other", parent_agent_id: "Lead" }]);
    const s = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Qa", "Lead");
    const injected = await begin(s, ctx, "harness-qa", "continue");
    expect(String(injected?.message?.content)).toMatch(/not-found/);
    await expectHeld(s, ctx, /not-found/);
    expect(rows(w.root).map((row) => row.agent_id)).toEqual(["Lead.Other"]);
  });

  test("a markerless revival bound in two registries is held as ambiguous", async () => {
    const w = world();
    const linked = mkdtempSync(join(tmpdir(), "bug1898-wt-"));
    mkdirSync(join(w.root, ".git", "worktrees", "BUG-98"), { recursive: true });
    writeFileSync(join(w.root, ".git", "worktrees", "BUG-98", "gitdir"), join(linked, ".git"));
    seed(w.root, [{ agent: "harness-qa", agent_id: "Lead.Qa", parent_agent_id: "Lead" }]);
    seed(linked, [{ agent: "harness-qa", agent_id: "Lead.Qa", parent_agent_id: "Lead" }]);
    const s = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Qa", "Lead");
    await begin(s, ctx, "harness-qa", "continue");
    await expectHeld(s, ctx, /ambiguous/);
  });

  test("an unreadable registry holds the run, non-retryable, and is left as found", async () => {
    const w = world();
    mkdirSync(join(w.root, ".harness"), { recursive: true });
    writeFileSync(join(w.root, ".harness", ".inflight-claims.json"), "{not json");
    const s = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Qa", "Lead");
    await begin(s, ctx, "harness-qa", ASSIGN);
    await expectHeld(s, ctx, /unreadable[\s\S]*cannot succeed/);
    expect(readFileSync(join(w.root, ".harness", ".inflight-claims.json"), "utf8"))
      .toBe("{not json");
  });

  test("a second live pm is held, naming the holder and that a retry can succeed", async () => {
    const w = world();
    seed(w.root, [{ agent: "harness-pm", agent_id: "Lead.Pm", parent_agent_id: "Lead" }]);
    const s = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Pm-2", "Lead");
    await begin(s, ctx, "harness-pm", ASSIGN);
    await expectHeld(s, ctx, /Lead\.Pm[\s\S]*retry can succeed/);
    expect(rows(w.root).map((row) => row.agent_id)).toEqual(["Lead.Pm"]);
  });

  test("a DEC-100 receiptless dispatch still claims the child's exact id at run start", async () => {
    const w = world();
    const parent = await lead(w);
    expect(await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "t1",
      input: { agent: "harness-backend-dev", name: "Dev", task: "passthrough" },
    }, parent.ctx)).toBeUndefined();
    expect(governed(w.root)).toEqual([]);
    const child = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Dev", "Lead");
    await begin(child, ctx, "harness-backend-dev", ASSIGN);
    expect(governed(w.root).map((row) => row.agent_id)).toEqual(["Lead.Dev"]);
    expect(await child.handlers.get("tool_call")?.(write(), ctx)).toBeUndefined();
  });

  test("a mixed, reordered batch never cross-attaches and leaves zero governed rows", async () => {
    const w = world();
    const parent = await lead(w);
    const input = {
      context: "shared",
      tasks: [
        { agent: "scout", name: "Look", task: "survey" },
        { agent: "harness-backend-dev", name: "Scope", task: ASSIGN },
        { agent: "harness-backend-dev", name: "Scope", task: ASSIGN },
        { agent: "harness-qa", name: "Check", task: ASSIGN },
      ],
    };
    expect(await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "batch", input,
    }, parent.ctx)).toBeUndefined();
    expect(governed(w.root).every((row) => row.agent_id === undefined)).toBe(true);

    // Children start in reverse order and write before any result is delivered.
    const started: Array<[string, string]> = [
      ["Lead.Check", "harness-qa"], ["Lead.Scope-2", "harness-backend-dev"],
      ["Lead.Scope", "harness-backend-dev"],
    ];
    for (const [id, agent] of started) {
      const child = session(w.runner);
      const ctx = ctxFor(w.root, id, "Lead");
      await begin(child, ctx, agent, ASSIGN);
      expect(await child.handlers.get("tool_call")?.(write(`src/${id}.ts`), ctx)).toBeUndefined();
    }
    const bound = governed(w.root).filter((row) => row.agent_id)
      .map((row) => [row.agent_id, row.agent]).sort();
    expect(bound).toEqual([
      ["Lead.Check", "harness-qa"],
      ["Lead.Scope", "harness-backend-dev"],
      ["Lead.Scope-2", "harness-backend-dev"],
    ]);

    await parent.s.handlers.get("tool_result")?.({
      toolName: "task", toolCallId: "batch", input, content: [],
      details: { results: [
        { index: 3, id: "Lead.Check", exitCode: 0 },
        { index: 0, id: "Lead.Look", exitCode: 0 },
        { index: 2, id: "Lead.Scope-2", exitCode: 0 },
        { index: 1, id: "Lead.Scope", exitCode: 0 },
      ] },
    }, parent.ctx);
    expect(governed(w.root)).toEqual([]);
    expect(rows(w.root).map((row) => row.claim_id)).toEqual(["lead-claim"]);
  });

  test("a governed child that never starts has its receipt released at settlement", async () => {
    const w = world();
    const parent = await lead(w);
    const input = {
      context: "shared",
      tasks: [
        { agent: "harness-qa", name: "Check", task: ASSIGN },
        { agent: "harness-data-engineer", name: "Data", task: ASSIGN },
      ],
    };
    await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "pair", input,
    }, parent.ctx);
    const child = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Check", "Lead");
    await begin(child, ctx, "harness-qa", ASSIGN);
    await parent.s.handlers.get("tool_result")?.({
      toolName: "task", toolCallId: "pair", input, content: [],
      details: { results: [
        { index: 1, id: "Lead.Data", exitCode: 1 },
        { index: 0, id: "Lead.Check", exitCode: 0 },
      ] },
    }, parent.ctx);
    expect(governed(w.root)).toEqual([]);
  });

  test("background children are released by their own settlement on pi.events", async () => {
    const w = world();
    const parent = await lead(w);
    const input = {
      context: "shared",
      tasks: [
        { agent: "harness-qa", name: "Check", task: ASSIGN },
        { agent: "harness-backend-dev", name: "Dev", task: ASSIGN },
      ],
    };
    await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "bg", input,
    }, parent.ctx);
    await parent.s.handlers.get("tool_result")?.({
      toolName: "task", toolCallId: "bg", input, content: [],
      details: { progress: [
        { index: 0, id: "Lead.Check", status: "running" },
        { index: 1, id: "Lead.Dev", status: "pending" },
      ] },
    }, parent.ctx);
    const check = session(w.runner);
    await begin(check, ctxFor(w.root, "Lead.Check", "Lead"), "harness-qa", ASSIGN);
    const dev = session(w.runner);
    await begin(dev, ctxFor(w.root, "Lead.Dev", "Lead"), "harness-backend-dev", ASSIGN);
    expect(governed(w.root).map((row) => row.agent_id).sort()).toEqual(["Lead.Check", "Lead.Dev"]);

    await parent.s.emit("task:subagent:lifecycle", {
      id: "Lead.Dev", agent: "harness-backend-dev", status: "failed",
      parentToolCallId: "bg", index: 1,
    });
    expect(governed(w.root).map((row) => row.agent_id)).toEqual(["Lead.Check"]);
    await parent.s.emit("task:subagent:lifecycle", {
      id: "Lead.Check", agent: "harness-qa", status: "completed",
      parentToolCallId: "bg", index: 0,
    });
    expect(governed(w.root)).toEqual([]);
  });

  test("a governed run with no runtime parent id is held, never authorized", async () => {
    const w = world();
    const s = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Dev");
    await begin(s, ctx, "harness-backend-dev", ASSIGN);
    const verdict = await s.handlers.get("tool_call")?.(write(), ctx);
    expect(verdict?.block).toBe(true);
    expect(verdict?.reason).toContain("runtime lineage capability");
    expect(rows(w.root)).toEqual([]);
  });
});
