import { beforeAll, describe, expect, test } from "bun:test";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, statSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  DIGEST_PERSONAS,
  DIGEST_PERSONA_ALIASES,
  DigestSchemaBundleError,
  canonicalDigestPersona,
  loadDigestSchemaBundle,
} from "../../.omp/extensions/digest-schema.ts";
import {
  DEFAULT_CONTEXT_WARN_TOKENS,
  DEFAULT_PLAN_PHASE_WARN_MINUTES,
  contextAdvisoryText,
  detectHarnessAgent,
  featureJsonPath,
  gatePath,
  gateRoot,
  extractEditPaths,
  normalizeTaskDispatches,
  readContextAnchor,
  registerHarnessHooks,
  resolveContextWarnTokens,
  resolvePlanPhaseWarnMinutes,
  resolveSessionFile,
  spendAdvisoryFor,
  spendAdvisoryText,
  type PolicyPayload,
} from "../../.omp/extensions/harness-hooks.ts";
// FEAT-2274's classification seams, read off the module so each case fails on its own.
import * as hooks from "../../.omp/extensions/harness-hooks.ts";

// BUG-2390: a policy payload is the gate's object for every script except member-ops, whose
// payload is its ops LIST. A read that expects a gate's object asserts it, loudly.
function objectPayload(payload: PolicyPayload): Record<string, unknown> {
  if (Array.isArray(payload)) throw new Error(`expected an object policy payload, got ${JSON.stringify(payload)}`);
  return payload;
}
// The same assertion for a recorded call that may be absent: an absent call reads undefined.
function payloadOf(call: { payload: PolicyPayload } | undefined): Record<string, unknown> | undefined {
  return call ? objectPayload(call.payload) : undefined;
}

function ompContext(cwd: string, id: string, parentId?: string, sessionId = `session-${id}`) {
  return {
    cwd,
    agent: {
      kind: parentId ? "sub" : "main",
      id,
      name: id === "Main" ? "main" : "task",
      depth: parentId ? 1 : 0,
      ...(parentId ? { parentId } : {}),
    },
    sessionManager: { getSessionId: () => sessionId },
  };
}

// FEAT-2225: a credential-free stand-in for OMP's injected `pi.zod`. Every builder returns a
// plain descriptor (descriptions dropped), so a test can assert a registered schema exactly.
// Descriptor keys never reuse a method name: the methods are non-enumerable own properties.
type FakeSchema = Record<string, unknown>;
function fakeSchema(node: FakeSchema): FakeSchema {
  return Object.defineProperties({ ...node }, {
    optional: { value: () => fakeSchema({ ...node, isOptional: true }) },
    strict: { value: () => fakeSchema({ ...node, closed: true }) },
    min: { value: (bound: number) => fakeSchema({ ...node, minLength: bound }) },
    regex: { value: (expression: RegExp) => fakeSchema({ ...node, pattern: expression.source }) },
    describe: { value: () => fakeSchema(node) },
  });
}
const fakeZod = {
  string: () => fakeSchema({ type: "string" }),
  enum: (values: string[]) => fakeSchema({ enum: values }),
  literal: (value: unknown) => fakeSchema({ const: value }),
  array: (items: FakeSchema) => fakeSchema({ type: "array", items }),
  union: (anyOf: FakeSchema[]) => fakeSchema({ anyOf }),
  object: (shape: Record<string, FakeSchema>) => fakeSchema({ type: "object", shape }),
};
// The ExtensionAPI surface every mocked host now carries beside `on` and `events`.
const toolApi = (tools: Map<string, any> = new Map()) => ({
  zod: fakeZod,
  registerTool(tool: { name: string }) { tools.set(tool.name, tool); },
});

// FEAT-1928: a yield's `data` IS the digest object; the validator receives it unmodified.
const PASS_DIGEST = { VERDICT: "PASS", DIGEST: { headline: "done" }, artifact: "none" };
const RETURN_THE_OBJECT = "return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}})";
// The canonical schema directory the hook loads from: the gate tree this extension ships in.
const DIGEST_SCHEMA_DIR = gatePath("digest-schemas");
// FEAT-2225: one member-ops receipt line as T-01's core prints it; the host returns it verbatim.
const MEMBER_OPS_RECEIPT = JSON.stringify({
  batch: "b".repeat(64),
  counts: {
    before: { Gotchas: 0, Open: 0, Outcomes: 0, Patterns: 0 },
    after: { Gotchas: 0, Open: 0, Outcomes: 0, Patterns: 1 },
  },
  outcomes: [{ op: "add", section: "Patterns", target: "P-1" }],
  receipt: ".harness/harness/features/FEAT-90-long-run/notes/expertise-receipt-x.json",
});

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
  // BUG-1016: `featureRoot` answers `inflight_registry.py feature-root`. The default is the
  // real CLI's no-worktree answer, the --root it was given, so no other case is rewritten.
  type PolicyAnswer = { blocked: boolean; reason?: string; unavailable?: string; stdout: string };
  function fixture(options: {
    featureRoot?: (args: string[]) => PolicyAnswer;
    memberOps?: (args: string[], payload: PolicyPayload) => PolicyAnswer;
    mergeGate?: (payload: Record<string, unknown>) => PolicyAnswer;
    distillAuthority?: (payload: Record<string, unknown>) => PolicyAnswer;
    // FEAT-2274: a gate's own answer, ahead of every default below; undefined falls through.
    gate?: (script: string, args: string[], payload: PolicyPayload) => PolicyAnswer | undefined;
  } = {}) {
    const tools = new Map<string, any>();
    const handlers = new Map<string, Function>();
    const calls: Array<{ script: string; args: string[]; payload: PolicyPayload; cwd: string }> = [];
    const active = new Set(["agent-a", "agent-b"]);
    let claim = 0;
    const lineageClaims = new Map<string, {
      agent: string;
      feature: string;
      agentId?: string;
      parentAgentId?: string;
      repository?: string;
    }>();
    lineageClaims.set("fixture-parent", {
      agent: "harness-eng-lead",
      feature: "FEAT-90-long-run",
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
      ...toolApi(tools),
    };
    const settle = (data: Record<string, unknown>) => Promise.all(lifecycle.map((handler) => handler(data)));
    // FEAT-2337: a policy runner answers with a Promise, as runPolicy does.
    const runner = async (
      cwd: string,
      script: string,
      args: string[],
      payload: PolicyPayload,
    ) => {
      calls.push({ script, args, payload, cwd });
      const own = options.gate?.(script, args, payload);
      if (own) return own;
      if (script === "inflight_registry.py" && args[0] === "feature-root") {
        return options.featureRoot?.(args) ?? { blocked: false, stdout: `${option(args, "--root")}\n` };
      }
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
        const task = (objectPayload(payload).tool_input as Record<string, unknown>).task;
        if (task === "deny") return { blocked: true, reason: "denied", stdout: "" };
        // The guard's FAIL-OPEN shape: exit 0, nothing on stdout. Seven branches of
        // dispatch-guard.py return exactly this (:34, :38, :72, :112, :138, :145, :187).
        // Absent from this fixture, no test could execute the pass-through path and F1
        // was invisible to a green suite.
        if (task === "passthrough") return { blocked: false, stdout: "" };
        claim += 1;
        const claimId = `claim-${claim}`;
        const dispatchedAgent = String((objectPayload(payload).tool_input as Record<string, unknown>).agent);
        const repository = String(task).includes("HARNESS-REPOSITORY: acme/product-a")
          ? "product-a" : undefined;
        lineageClaims.set(claimId, {
          agent: dispatchedAgent,
          feature: "FEAT-90-long-run",
          repository,
        });
        return {
          blocked: false,
          stdout: JSON.stringify({
            harness_claim: {
              root: "/repo",
              feature: "FEAT-90-long-run",
              agent: dispatchedAgent,
              claim_id: claimId,
              ...(repository ? { repository } : {}),
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
        const repository = option(args, "--repository");
        if ((agentId && claimRecord.agentId && claimRecord.agentId !== agentId)
          || (parentAgentId && claimRecord.parentAgentId
            && claimRecord.parentAgentId !== parentAgentId)
          || claimRecord.repository !== repository) {
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
        const repository = option(args, "--repository");
        if (agentId === "AuthorizeError") {
          return { blocked: false, reason: "authorization gate crashed", stdout: "" };
        }
        const candidates = [...lineageClaims.values()].filter((claimRecord) =>
          claimRecord.agent === agent
          && claimRecord.feature === feature
          && claimRecord.repository === repository
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
      if (script === "validate-digest.py" && args[0] === "--distill-authority") {
        return options.distillAuthority?.(objectPayload(payload)) ?? { blocked: false, stdout: '{"authorized": true}\n' };
      }
      if (script === "validate-digest.py") {
        return active.size
          ? { blocked: true, reason: "children live", stdout: "" }
          : { blocked: false, stdout: "" };
      }
      if (script === "plan-sign-gate.py") {
        const command = ((objectPayload(payload).tool_input as Record<string, unknown> | undefined)?.command as string) || "";
        if (command.includes("sign-approval")) {
          return { blocked: true, reason: "plan-sign-gate: refused", stdout: "" };
        }
        return { blocked: false, stdout: "" };
      }
      if (script === "expertise-merge.py") {
        return options.memberOps?.(args, payload) ?? { blocked: false, stdout: `${MEMBER_OPS_RECEIPT}\n` };
      }
      if (script === "merge-gate.py" && options.mergeGate) return options.mergeGate(objectPayload(payload));
      return { blocked: false, stdout: "" };
    };
    registerHarnessHooks(pi, runner);
    return { handlers, calls, runner, settle, tools };
  }

  async function start(
    handlers: Map<string, Function>,
    ctx: Record<string, unknown> = ompContext(
      "/repo", "LeadOne", "OrchestratorOne", "parent-session",
    ),
    agent = "harness-eng-lead",
  ) {
    await handlers.get("before_agent_start")?.({
      prompt: "Complete assignment thoroughly:\n\nHARNESS-FEATURE: FEAT-90-long-run\nassignment",
      systemPrompt: [`HARNESS_AGENT_ID: ${agent}`],
    }, ctx);
    await handlers.get("message_end")?.({
      message: {
        role: "user",
        content: [{ type: "text", text: "HARNESS-FEATURE: FEAT-90-long-run\nassignment" }],
      },
    }, ctx);
  }

  test("injects context through the native Python hook", async () => {
    const { handlers, calls } = fixture();
    const ctx = ompContext("/repo", "LeadOne", "OrchestratorOne", "parent-session");
    const result = await handlers.get("before_agent_start")?.({
      prompt: "HARNESS-FEATURE: FEAT-90-long-run\nlead it",
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
        task: "HARNESS-FEATURE: FEAT-90-long-run\nrun the feature",
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
      agent: {
        kind: "sub",
        id: "OrchestratorOne",
        name: "orchestrator",
        depth: 1,
      },
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
    const mainCtx = ompContext("/repo", "Main", undefined, "main-session");
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx);
    const dispatched = await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-orchestrator",
      input: {
        agent: "harness-orchestrator",
        name: "OrchestratorOne",
        task: "HARNESS-FEATURE: FEAT-90-long-run\nrun the feature",
      },
    }, mainCtx);
    expect(dispatched?.block).toBeUndefined();
    const dispatchCall = calls.find((call) => call.script === "dispatch-guard.py");
    expect(payloadOf(dispatchCall)?.agent_type).toBe("Main");
    expect(payloadOf(dispatchCall)?.harness_agent_id).toBe("Main");
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
      ...toolApi(),
    }, runner);
    const childCtx = ompContext("/repo", "OrchestratorOne", "Main", "orchestrator-session");
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
    const parentCtx = ompContext("/repo", "LeadOne", "OrchestratorOne", "lead-session");
    await start(handlers, parentCtx);
    const dispatched = await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-child",
      input: {
        agent: "harness-backend-dev",
        name: "BackendOne",
        task: "HARNESS-FEATURE: FEAT-90-long-run\nimplement it",
      },
    }, parentCtx);
    expect(dispatched?.block).toBeUndefined();
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
      ...toolApi(),
    }, runner);
    const childCtx = ompContext("/repo", "BackendOne", "LeadOne", "child-session");
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
    expect(payloadOf(domainCall)?.harness_agent_id).toBe("BackendOne");
    expect(payloadOf(domainCall)?.harness_parent_agent_id).toBe("LeadOne");
    expect(payloadOf(domainCall)?.harness_feature).toBe("FEAT-90-long-run");

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
    expect(payloadOf(bashGuard)?.harness_feature).toBe("FEAT-90-long-run");
    expect(payloadOf(bashGuard)?.harness_agent_id).toBe("BackendOne");
    expect(payloadOf(bashGuard)?.harness_parent_agent_id).toBe("LeadOne");
    const authorizations = calls.filter((call) =>
      call.script === "inflight_registry.py"
      && call.args[0] === "authorize"
      && call.args.includes("BackendOne")
      && call.args.includes("LeadOne"));
    expect(authorizations).toHaveLength(2);
  });

  test("blocks a sibling lineage and isolates a nested child's edit claim", async () => {
    const { handlers, runner } = fixture();
    const parentCtx = ompContext("/repo", "LeadOne", "OrchestratorOne", "lead-session");
    await start(handlers, parentCtx);
    await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-child",
      input: {
        agent: "harness-backend-dev",
        name: "BackendOne",
        task: "HARNESS-FEATURE: FEAT-90-long-run\nimplement it",
      },
    }, parentCtx);

    const childHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { childHandlers.set(name, handler); },
      events: { on: () => () => {} },
      ...toolApi(),
    }, runner);
    const childCtx = ompContext("/repo", "BackendOne", "LeadOne", "child-session");
    await start(childHandlers, childCtx, "harness-backend-dev");
    await childHandlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-grandchild",
      input: {
        agent: "harness-data-engineer",
        name: "DataOne",
        task: "HARNESS-FEATURE: FEAT-90-long-run\nchange the schema",
      },
    }, childCtx);

    const goodHandlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { goodHandlers.set(name, handler); },
      events: { on: () => () => {} },
      ...toolApi(),
    }, runner);
    const goodCtx = ompContext("/repo", "DataOne", "BackendOne", "grandchild-session");
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
      ...toolApi(),
    }, runner);
    const siblingCtx = ompContext("/repo", "DataOne", "LeadOne", "sibling-session");
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
      ...toolApi(),
    }, runner);
    const childCtx = ompContext("/repo", "AuthorizeError", "LeadOne", "child-session");
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
    expect(result?.reason).toContain(RETURN_THE_OBJECT);
    expect(calls.filter((call) => call.script === "validate-digest.py")).toHaveLength(0);
  });

  test("blocks a whole batch and rolls back earlier claims", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    expect(calls.some((call) =>
      call.script === "inflight_registry.py"
      && call.args[0] === "reconcile"
      && call.args.includes("FEAT-90-long-run")
    )).toBe(true);

    const result = await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-refused",
      input: {
        context: "shared",
        tasks: [
          { agent: "harness-backend-dev", task: "HARNESS-FEATURE: FEAT-90-long-run\nallow" },
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
    const ctx = ompContext("/repo", "LeadOne", "OrchestratorOne", "parent-session");
    const input = {
      context: "shared",
      tasks: [
        { agent: "harness-backend-dev", task: "HARNESS-FEATURE: FEAT-90-long-run\none" },
        { agent: "harness-dev-ops", task: "HARNESS-FEATURE: FEAT-90-long-run\ntwo" },
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
    )).toHaveLength(2);
    expect(await handlers.get("tool_call")?.({
      toolName: "yield", input: { data: PASS_DIGEST },
    }, ctx)).toBeUndefined();
  });

  // #1677: the operator's pin rides in the assignment message — the one text the reviewer
  // does not author — and reaches validate-digest.py as harness_review_pin. A pin in a
  // later user turn is not a source.
  test("forwards the assignment's HARNESS-REVIEW-PIN to the digest validator", async () => {
    const { handlers, calls } = fixture();
    const ctx = ompContext("/repo", "Lead.Child", "Lead", "parent-session");
    await handlers.get("before_agent_start")?.({
      prompt: "HARNESS-FEATURE: FEAT-90-long-run\nreview it",
      systemPrompt: ["HARNESS_AGENT_ID: harness-code-reviewer"],
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text",
        text: "HARNESS-FEATURE: FEAT-90-long-run\nHARNESS-REVIEW-PIN: ab0c9987\nreview it" }] },
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text", text: "HARNESS-REVIEW-PIN: deadbeef" }] },
    }, ctx);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { data: PASS_DIGEST },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(payloadOf(validation)?.harness_review_pin).toBe("ab0c9987");
    expect(payloadOf(validation)?.harness_feature).toBe("FEAT-90-long-run");
  });

  test("forwards no pin when the assignment carries none", async () => {
    const { handlers, calls } = fixture();
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    await start(handlers);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { data: PASS_DIGEST },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(payloadOf(validation)?.harness_review_pin).toBeUndefined();
  });

  // #1855: the mission rides the same road as the pin — the assignment message, scanned
  // once — and reaches validate-digest.py as harness_mission so a distill reader's
  // gate fields are pinned to their did-nothing spelling rather than fabricated.
  test("forwards the assignment's HARNESS-MISSION to the digest validator", async () => {
    const { handlers, calls } = fixture();
    const ctx = ompContext("/repo", "Lead.Child", "Lead", "parent-session");
    await handlers.get("before_agent_start")?.({
      prompt: "HARNESS-FEATURE: FEAT-92-consolidation\ndistill your log",
      systemPrompt: ["HARNESS_AGENT_ID: harness-qa"],
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text",
        text: "HARNESS-FEATURE: FEAT-92-consolidation\nHARNESS-MISSION: distill\ndistill your log" }] },
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text", text: "HARNESS-MISSION: build" }] },
    }, ctx);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { data: PASS_DIGEST },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(payloadOf(validation)?.harness_mission).toBe("distill");
    expect(payloadOf(validation)?.harness_review_pin).toBeUndefined();
  });

  test("forwards no mission when the assignment carries none", async () => {
    const { handlers, calls } = fixture();
    const ctx = { cwd: "/repo", sessionManager: { getSessionId: () => "parent-session" } };
    await start(handlers);
    await handlers.get("tool_call")?.({
      toolName: "yield", input: { data: PASS_DIGEST },
    }, ctx);
    const validation = calls.find((call) => call.script === "validate-digest.py");
    expect(payloadOf(validation)?.harness_mission).toBeUndefined();
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
    expect((await handlers.get("tool_call")?.({
      toolName: "task",
      toolCallId: "call-mixed",
      input: {
        context: "shared",
        tasks: [
          { agent: "harness-backend-dev", task: "HARNESS-FEATURE: FEAT-90-long-run\nallow" },
          { agent: "scout", task: "passthrough" },
        ],
      },
    }, ctx))?.block).toBeUndefined();
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

  const postPaths = (calls: Array<{ script: string; args: string[]; payload: PolicyPayload }>) =>
    calls
      .filter((call) => call.script === "check-domain.py" && call.args.includes("--post"))
      .map((call) => (call.payload as any).tool_input.file_path);

  test("a hashline edit reaches check-domain.py --post carrying the edited path", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    // The exact file and tag shape of the 2026-08-30 corruption.
    const path = ".harness/harness/features/FEAT-91-context-advisory-fixture/feature.json";
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

  // -------------------------------------------------------------------------
  // BUG-2003: an internal URI is not a checkout file. `agent://` and exactly
  // `xd://report_issue` skip the file-domain gate; every other `scheme://` target is
  // refused by name, never resolved and never shown to check-domain.py — on write and
  // edit, pre and post. Real files keep today's gate, even beside an allowed URI.
  // -------------------------------------------------------------------------
  const FORBIDDEN = "/repo/forbidden.ts";
  const ALLOWED_URIS = ["agent://LeadTwo", "xd://report_issue"];
  const REFUSED_URIS = [
    "xd://ast_edit", "xd://lsp", "xd://recall", "xd://reflect", "xd://report_issue/extra",
    "conflict://1", "local://sample.md", "vault://_/sample.md", "ssh://host/sample.md",
    "novel-scheme://x",
  ];
  const uriEdit = (...targets: string[]) =>
    targets.map((target) => `[${target}#1A2B]\nPUT 1:\n+x`).join("\n");

  // One governed lead session over the fixture runner, with check-domain.py refusing `forbidden`.
  // BUG-1016's cases pass a feature-root answer; everything else takes the no-worktree default.
  async function governedUriHooks(options: {
    featureRoot?: (args: string[]) => PolicyAnswer;
    forbidden?: string;
  } = {}) {
    const forbidden = options.forbidden ?? FORBIDDEN;
    const { calls, runner } = fixture({ featureRoot: options.featureRoot });
    const handlers = new Map<string, Function>();
    registerHarnessHooks({
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: { on: () => () => {} },
      ...toolApi(),
    }, async (cwd, script, args, payload) => {
      const result = await runner(cwd, script, args, payload);
      const target = (objectPayload(payload).tool_input as Record<string, unknown> | undefined)?.file_path;
      return script === "check-domain.py" && target === forbidden
        ? { blocked: true, reason: `${forbidden} is outside your domain`, stdout: "" }
        : result;
    });
    const ctx = ompContext("/repo", "LeadOne", "OrchestratorOne", "parent-session");
    await start(handlers, ctx);
    const lookups = () => calls.filter((call) =>
      call.script === "inflight_registry.py" && call.args[0] === "feature-root");
    const domainTargets = (from: number) => calls.slice(from)
      .filter((call) => call.script === "check-domain.py")
      .map((call) => (objectPayload(call.payload).tool_input as Record<string, unknown>).file_path);
    const pre = (toolName: string, input: Record<string, unknown>) =>
      handlers.get("tool_call")?.({ toolName, toolCallId: "call-uri", input }, ctx);
    const post = (toolName: string, input: Record<string, unknown>) =>
      handlers.get("tool_result")?.({
        toolName, toolCallId: "call-uri", input, content: [{ type: "text", text: "ok" }],
      }, ctx);
    return { hooks: handlers, ctx, calls, lookups, domainTargets, pre, post };
  }

  const routes = (target: string): Array<[string, Record<string, unknown>]> => [
    ["write", { path: target, content: "x" }],
    ["edit", { input: uriEdit(target) }],
  ];

  test("agent:// and xd://report_issue skip the domain gate on both routes and stages", async () => {
    const hooks = await governedUriHooks();
    for (const target of ALLOWED_URIS) {
      for (const [toolName, input] of routes(target)) {
        const from = hooks.calls.length;
        expect(await hooks.pre(toolName, input)).toBeUndefined();
        expect(await hooks.post(toolName, input)).toBeUndefined();
        expect(hooks.domainTargets(from)).toEqual([]);
      }
    }
  });

  test("every other scheme is refused by name and never reaches check-domain.py", async () => {
    const hooks = await governedUriHooks();
    for (const target of REFUSED_URIS) {
      for (const [toolName, input] of routes(target)) {
        const from = hooks.calls.length;
        const blocked = await hooks.pre(toolName, input) as { block: boolean; reason: string };
        expect(blocked?.block).toBe(true);
        expect(blocked.reason).toContain(target);
        const result = await hooks.post(toolName, input) as
          { isError: boolean; content: Array<{ text: string }> };
        expect(result?.isError).toBe(true);
        expect(result.content.some((part) => part.text.includes(target))).toBe(true);
        expect(hooks.domainTargets(from)).toEqual([]);
      }
    }
  });

  test("an edit MV destination is judged by the same scheme rule", async () => {
    const hooks = await governedUriHooks();
    const from = hooks.calls.length;
    const blocked = await hooks.pre("edit", { input: "[/repo/src/a.ts#1A2B]\nMV local://moved.md" }) as
      { block: boolean; reason: string };
    expect(blocked?.block).toBe(true);
    expect(blocked.reason).toContain("local://moved.md");
    expect(hooks.domainTargets(from)).not.toContain("local://moved.md");
  });

  test("an allowed URI never exempts a sibling file or a refused URI in the same edit", async () => {
    const hooks = await governedUriHooks();
    let from = hooks.calls.length;
    const mixedFile = { input: uriEdit("agent://LeadTwo", FORBIDDEN) };
    const blocked = await hooks.pre("edit", mixedFile) as { block: boolean; reason: string };
    expect(blocked?.block).toBe(true);
    expect(blocked.reason).toBe(`${FORBIDDEN} is outside your domain`);
    const result = await hooks.post("edit", mixedFile) as
      { isError: boolean; content: Array<{ text: string }> };
    expect(result?.isError).toBe(true);
    expect(result.content.map((part) => part.text)).toEqual([
      "ok", `Harness post-write check: ${FORBIDDEN} is outside your domain`,
    ]);
    const gate = hooks.calls.slice(from).filter((call) => call.script === "check-domain.py");
    expect(gate.map((call) => [call.args, objectPayload(call.payload).tool_name, objectPayload(call.payload).tool_input]))
      .toEqual([
        [[], "Edit", { file_path: FORBIDDEN }],
        [["--post"], "Edit", { file_path: FORBIDDEN }],
      ]);

    from = hooks.calls.length;
    const mixedUri = await hooks.pre("edit", { input: uriEdit("agent://LeadTwo", "conflict://1") }) as
      { block: boolean; reason: string };
    expect(mixedUri?.block).toBe(true);
    expect(mixedUri.reason).toContain("conflict://1");
    expect(hooks.domainTargets(from)).toEqual([]);
  });

  test("an ordinary file keeps its exact domain-gate payloads", async () => {
    const hooks = await governedUriHooks();
    const from = hooks.calls.length;
    expect(await hooks.pre("write", { path: "/repo/src/a.ts", content: "x" })).toBeUndefined();
    await hooks.post("write", { path: "/repo/src/a.ts", content: "x" });
    const gate = hooks.calls.slice(from).filter((call) => call.script === "check-domain.py");
    expect(gate.map((call) => call.args)).toEqual([[], ["--post"]]);
    expect(gate.map((call) => objectPayload(call.payload).tool_input)).toEqual([
      { file_path: "/repo/src/a.ts", content: "x" },
      { file_path: "/repo/src/a.ts", content: "x" },
    ]);
  });

  test("a governed out-of-domain file write keeps its exact gate payload and refusal", async () => {
    const hooks = await governedUriHooks();
    const from = hooks.calls.length;
    const input = { path: FORBIDDEN, content: "x" };
    expect(await hooks.pre("write", input))
      .toEqual({ block: true, reason: `${FORBIDDEN} is outside your domain` });
    const result = await hooks.post("write", input) as
      { isError: boolean; content: Array<{ text: string }> };
    expect(result?.isError).toBe(true);
    expect(result.content.map((part) => part.text)).toEqual([
      "ok", `Harness post-write check: ${FORBIDDEN} is outside your domain`,
    ]);
    const gate = hooks.calls.slice(from).filter((call) => call.script === "check-domain.py");
    expect(gate.map((call) => [call.args, objectPayload(call.payload).tool_name, objectPayload(call.payload).tool_input]))
      .toEqual([
        [[], "Write", { file_path: FORBIDDEN, content: "x" }],
        [["--post"], "Write", { file_path: FORBIDDEN, content: "x" }],
      ]);
    expect(objectPayload(gate[0].payload).harness_feature).toBe("FEAT-90-long-run");
  });

  test("the main session's writes and edits are untouched, URIs included", async () => {
    const { handlers, calls } = fixture();
    const mainCtx = ompContext("/repo", "Main", undefined, "main-session");
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx);
    const from = calls.length;
    for (const target of ["conflict://1", "/repo/src/a.ts"]) {
      for (const [toolName, input] of [
        ["write", { path: target, content: "x" }],
        ["edit", { input: `[${target}#1A2B]\nPUT 1:\n+x` }],
      ] as Array<[string, Record<string, unknown>]>) {
        const event = { toolName, toolCallId: "call-main", input, content: [{ type: "text", text: "ok" }] };
        expect(await handlers.get("tool_call")?.(event, mainCtx)).toBeUndefined();
        expect(await handlers.get("tool_result")?.(event, mainCtx)).toBeUndefined();
      }
    }
    // The whole runner-call set, not only check-domain.py: the main session's write and
    // edit callbacks invoke no policy script at all, so no other gate can start judging
    // its URIs or files unnoticed (#2009).
    expect(calls.slice(from)).toEqual([]);
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
    const path = ".harness/harness/features/FEAT-91-context-advisory-fixture/feature.json";
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

  // -------------------------------------------------------------------------
  // BUG-1016: OMP starts a subagent in its parent's cwd, the main checkout, so a governed
  // agent's relative file-tool path read and wrote main's copy instead of its feature
  // worktree's. The hook roots every relative path, and an omitted search path, in the
  // worktree that `inflight_registry.py feature-root` names for the run's own feature.
  // Absolute, `~` and `scheme://` targets are never touched. Expected paths are literals.
  // -------------------------------------------------------------------------
  const WT = "/wt/FEAT-90-long-run";
  const featureRootArgs = ["feature-root", "--feature", "FEAT-90-long-run", "--root", "/repo"];
  const worktreeAnswer = (): PolicyAnswer => ({ blocked: false, stdout: `${WT}\n` });

  const rootedHooks = (featureRoot: (args: string[]) => PolicyAnswer = worktreeAnswer) =>
    governedUriHooks({ featureRoot, forbidden: `${WT}/forbidden.ts` });

  test("BUG-1016: a relative path on every path tool is rooted in the worktree, other fields kept", async () => {
    const { pre } = await rootedHooks();
    const cases: Array<[string, Record<string, unknown>, Record<string, unknown>]> = [
      ["read", { path: "src/a.ts", i: "Reading" }, { path: `${WT}/src/a.ts`, i: "Reading" }],
      ["grep", { pattern: "x", path: "src", case: false }, { pattern: "x", path: `${WT}/src`, case: false }],
      ["glob", { path: "src/**/*.ts", limit: 5 }, { path: `${WT}/src/**/*.ts`, limit: 5 }],
      ["write", { path: "notes/a.md", content: "x" }, { path: `${WT}/notes/a.md`, content: "x" }],
      ["ast_grep", { pat: "f($A)", path: "lib" }, { pat: "f($A)", path: `${WT}/lib` }],
      ["ast_edit", { ops: [{ pat: "a", out: "b" }], paths: ["src/a.ts", "/abs/b.ts", "~/c.ts", "agent://d"] },
        { ops: [{ pat: "a", out: "b" }], paths: [`${WT}/src/a.ts`, "/abs/b.ts", "~/c.ts", "agent://d"] }],
    ];
    for (const [toolName, input, expected] of cases) {
      const original = structuredClone(input);
      expect(await pre(toolName, input)).toEqual({ input: expected });
      expect(input).toEqual(original);
    }
  });

  test("BUG-1016: each list entry is judged alone; absolute, ~ and URI entries stay byte-for-byte", async () => {
    const { pre } = await rootedHooks();
    const list = "src; /abs/x; ~/h; agent://LeadTwo; xd://report_issue; lib/*.ts";
    const rooted = `${WT}/src; /abs/x; ~/h; agent://LeadTwo; xd://report_issue; ${WT}/lib/*.ts`;
    for (const toolName of ["read", "grep", "glob", "ast_grep"]) {
      expect(await pre(toolName, { path: list })).toEqual({ input: { path: rooted } });
    }
  });

  test("BUG-1016: a quoted target is rooted inside its quotes, even one made of quotes (R2)", async () => {
    const { pre } = await rootedHooks();
    const cases: Array<[string, string]> = [
      ['"""', `"${WT}/""`],
      ['""""', `"${WT}/"""`],
      ['"a b.ts"', `"${WT}/a b.ts"`],
      [' "x" ', ` "${WT}/x" `],
    ];
    for (const [path, rooted] of cases) {
      expect(await pre("read", { path })).toEqual({ input: { path: rooted } });
    }
    // A quoted ~, absolute or scheme target is still an explicit destination.
    for (const path of ['"~/notes.md"', '"/abs/a.ts"', '"agent://LeadTwo"']) {
      expect(await pre("read", { path })).toBeUndefined();
    }
  });

  test("#2026: a governed Bash post sweep names the run's feature", async () => {
    const { post, calls } = await rootedHooks();
    const at = calls.length;
    await post("bash", { command: "ls" });
    const sweep = calls.slice(at).find((call) => call.script === "check-domain.py");
    expect(sweep?.payload).toMatchObject({ tool_name: "Bash", harness_feature: "FEAT-90-long-run" });
    expect(sweep?.args).toEqual(["--post"]);
  });

  test("#2027: a quoted ~, absolute or scheme target is explicit on every path tool", async () => {
    const { pre, lookups } = await rootedHooks();
    for (const toolName of ["read", "grep", "glob", "write", "ast_grep"]) {
      for (const path of ['"~/notes.md"', '"/abs/a.ts"', '"agent://LeadTwo"', ' "~/x" ']) {
        expect([toolName, path, await pre(toolName, { path })]).toEqual([toolName, path, undefined]);
      }
    }
    expect(await pre("ast_edit", { paths: ['"~/a.ts"', '"/abs/b.ts"'] })).toBeUndefined();
    expect(lookups()).toEqual([]);
  });

  // FEAT-1559 (SC-02): a sparse worktree holds only its own feature, so another feature is read
  // at the owner root by ordinary absolute path. That read must reach the tool exactly as
  // written — selector, quotes and list entries included — with no feature-root lookup, while
  // a relative read still roots in the run's own worktree.
  test("FEAT-1559: an absolute main-corpus read is untouched and looks nothing up; a relative one is rooted", async () => {
    const { pre, lookups } = await rootedHooks();
    const landed = "/repo/.harness/kaya/features/FEAT-93-kaya-app";
    for (const toolName of ["read", "grep", "glob"]) {
      for (const path of [
        `${landed}/BRIEF.md:1-20`,
        `"${landed}/notes/plan.md:raw"`,
        `${landed}/BRIEF.md:1-20; /repo/.harness/harness/features/FEAT-2-beta/notes/research.md`,
      ]) {
        const input = { path, i: "Reading a landed feature" };
        const original = structuredClone(input);
        expect([toolName, path, await pre(toolName, input)]).toEqual([toolName, path, undefined]);
        expect(input).toEqual(original);
      }
    }
    expect(lookups()).toEqual([]);

    const own = ".harness/harness/features/FEAT-90-long-run/BRIEF.md:1-20";
    expect(await pre("read", { path: own })).toEqual({ input: { path: `${WT}/${own}` } });
    expect(lookups().map((call) => call.args)).toEqual([featureRootArgs]);
  });

  test("#2027: a quote-only edit section or MV destination is rooted inside its quotes", async () => {
    const { pre, domainTargets, calls } = await rootedHooks();
    const at = calls.length;
    expect(await pre("edit", { input: '["""#1A2B]\nPUT 1:\n+x\nMV """"' }))
      .toEqual({ input: { input: `["${WT}/""#1A2B]\nPUT 1:\n+x\nMV "${WT}/"""` } });
    expect(domainTargets(at)).toEqual([`${WT}/"`, `${WT}/""`]);
  });

  test("#2028: ast_edit is a mutation: authorized, and every paths entry is domain-gated pre and post", async () => {
    const { pre, post, calls, domainTargets } = await rootedHooks();
    let at = calls.length;
    expect(await pre("ast_edit", { ops: [{ pat: "a", out: "b" }], paths: ["src", "/abs/lib/**/*.ts"] }))
      .toEqual({ input: { ops: [{ pat: "a", out: "b" }], paths: [`${WT}/src`, "/abs/lib/**/*.ts"] } });
    const fromAt = calls.slice(at);
    expect(fromAt.some((call) => call.script === "inflight_registry.py" && call.args[0] === "authorize")).toBe(true);
    expect(domainTargets(at)).toEqual([`${WT}/src`, "/abs/lib/**/*.ts"]);
    expect(fromAt.filter((call) => call.script === "check-domain.py").map((call) => objectPayload(call.payload).tool_name))
      .toEqual(["Edit", "Edit"]);

    expect(await pre("ast_edit", { ops: [], paths: ["src; forbidden.ts"] }))
      .toEqual({ block: true, reason: `${WT}/forbidden.ts is outside your domain` });
    const refused = await pre("ast_edit", { ops: [], paths: ["src", "local://d.md"] });
    expect(refused.block).toBe(true);
    expect(refused.reason).toContain("local://d.md");

    at = calls.length;
    for (const input of [{ ops: [], paths: ["forbidden.ts"] }, { ops: [], paths: [`${WT}/forbidden.ts`] }]) {
      expect((await post("ast_edit", input)).isError).toBe(true);
    }
    expect(domainTargets(at)).toEqual([`${WT}/forbidden.ts`, `${WT}/forbidden.ts`]);
    expect(calls.slice(at).every((call) => call.script !== "check-domain.py" || call.args.includes("--post")))
      .toBe(true);
  });

  test("#2028: an unauthorized run's ast_edit is refused before any gate or rewrite", async () => {
    const { handlers, calls } = fixture({ featureRoot: worktreeAnswer });
    const ctx = ompContext("/repo", "AuthorizeError", "OrchestratorOne", "parent-session");
    await start(handlers, ctx);
    const at = calls.length;
    const result = await handlers.get("tool_call")?.({
      toolName: "ast_edit", toolCallId: "c", input: { ops: [], paths: ["src"] },
    }, ctx);
    expect(result).toEqual({ block: true, reason: "authorization gate crashed" });
    expect(calls.slice(at).map((call) => call.script)).toEqual(["inflight_registry.py"]);
  });

  test("BUG-1016: dot, parent, glob, selector, archive and SQLite text is preserved after the root", async () => {
    const { pre } = await rootedHooks();
    for (const path of [
      "./x.ts", "../sibling/y.ts", "src/**/*.ts", "src/a.ts:50-100", "src/a.ts:raw:2-4",
      "img/logo.png:img", "dist/app.zip:member/path.txt", "data.db:runs?where=ok=1",
    ]) {
      expect(await pre("read", { path })).toEqual({ input: { path: `${WT}/${path}` } });
    }
  });

  test("BUG-1016: an omitted or null search path becomes the worktree root; required paths are never invented", async () => {
    const { pre, lookups } = await rootedHooks();
    for (const toolName of ["grep", "glob", "ast_grep"]) {
      expect(await pre(toolName, { pattern: "x" })).toEqual({ input: { pattern: "x", path: WT } });
      expect(await pre(toolName, { pattern: "x", path: null })).toEqual({ input: { pattern: "x", path: WT } });
    }
    const before = lookups().length;
    expect(await pre("read", { i: "x" })).toBeUndefined();
    expect(await pre("ast_edit", { ops: [] })).toBeUndefined();
    expect(lookups().length).toBe(before);
  });

  test("BUG-1016: blank strings and blank list entries are kept verbatim and need no lookup", async () => {
    const { pre, lookups } = await rootedHooks();
    for (const toolName of ["read", "grep", "glob", "write", "ast_grep"]) {
      for (const path of ["", "   ", ";", " ; "]) {
        expect(await pre(toolName, { path })).toBeUndefined();
      }
    }
    expect(await pre("ast_edit", { paths: ["", "  "] })).toBeUndefined();
    expect(lookups()).toEqual([]);
    expect(await pre("grep", { path: "src;; ;" })).toEqual({ input: { path: `${WT}/src;; ;` } });
    expect(await pre("ast_edit", { paths: ["", "src"] })).toEqual({ input: { paths: ["", `${WT}/src`] } });
  });

  test("BUG-1016: absolute, ~, URI and main-session or Bash calls are untouched and look nothing up", async () => {
    const { pre, lookups } = await rootedHooks();
    for (const path of ["/abs/a.ts", "~/a.ts", "agent://LeadTwo", "xd://report_issue", "local://a.md"]) {
      expect(await pre("read", { path })).toBeUndefined();
    }
    expect(await pre("bash", { command: "cat src/a.ts" }))
      .toEqual({ input: { command: "cat src/a.ts", env: { HARNESS_AGENT_TYPE: "harness-eng-lead" } } });
    expect(lookups()).toEqual([]);

    const main = fixture({ featureRoot: worktreeAnswer });
    const mainCtx = ompContext("/repo", "Main", undefined, "main-session");
    await main.handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx);
    for (const [toolName, input] of [["read", { path: "src/a.ts" }], ["grep", { pattern: "x" }]] as const) {
      expect(await main.handlers.get("tool_call")?.({ toolName, toolCallId: "m", input }, mainCtx)).toBeUndefined();
    }
    expect(main.calls.filter((call) => call.args[0] === "feature-root")).toEqual([]);
  });

  test("BUG-1016: edit sections and MV destinations are rooted; hashes, rows and line endings are not", async () => {
    const { pre, domainTargets, calls } = await rootedHooks();
    const patch = [
      "[src/a.ts#1A2B]", "PUT 1:", "+[looks/like.ts#3C4D]", "+MV not/a/move.ts",
      "[/abs/b.ts#5E6F]", "MV renamed/b.ts\r",
      "[docs/c.md#7A8B]", "MV \"with space/c d.md\"",
      "[local://d.md#9C0D]", "MV /abs/e.md",
    ].join("\n");
    const expected = [
      `[${WT}/src/a.ts#1A2B]`, "PUT 1:", "+[looks/like.ts#3C4D]", "+MV not/a/move.ts",
      "[/abs/b.ts#5E6F]", `MV ${WT}/renamed/b.ts\r`,
      `[${WT}/docs/c.md#7A8B]`, `MV "${WT}/with space/c d.md"`,
      "[local://d.md#9C0D]", "MV /abs/e.md",
    ].join("\n");
    const result = await pre("edit", { input: patch });
    // local:// is refused by name (BUG-2003) only AFTER the rewrite: the rewrite itself is
    // judged on an edit without it.
    expect(result.block).toBe(true);
    expect(result.reason).toContain("local://d.md");
    const clean = patch.replace("[local://d.md#9C0D]\n", "");
    const cleanExpected = expected.replace("[local://d.md#9C0D]\n", "");
    const at = calls.length;
    expect(await pre("edit", { input: clean })).toEqual({ input: { input: cleanExpected } });
    expect(domainTargets(at)).toEqual(extractEditPaths(cleanExpected));
    expect(domainTargets(at)).toEqual([
      `${WT}/src/a.ts`, "/abs/b.ts", `${WT}/docs/c.md`, `${WT}/renamed/b.ts`,
      `${WT}/with space/c d.md`, "/abs/e.md",
    ]);
    // Idempotent: the revised edit needs nothing more, and is never rooted twice.
    expect(await pre("edit", { input: cleanExpected })).toBeUndefined();
  });

  test("BUG-1016: the resolver is asked once per call with the run's own feature, and cached for the run", async () => {
    const { pre, lookups, hooks, ctx } = await rootedHooks();
    await pre("grep", { path: "a; b; c" });
    await pre("read", { path: "d" });
    expect(lookups().map((call) => [call.cwd, call.args])).toEqual([["/repo", featureRootArgs]]);
    // A new run resolves again.
    await hooks.get("agent_end")?.({ messages: [] }, ctx);
    await start(hooks, ctx);
    await pre("read", { path: "e" });
    expect(lookups().length).toBe(2);
    // A run start drops it too, even with no agent_end before it.
    await start(hooks, ctx);
    await pre("read", { path: "f" });
    expect(lookups().length).toBe(3);
  });

  test("BUG-1016: no worktree for the feature means no rewrite, cached or not", async () => {
    const { pre, lookups } = await rootedHooks(() => ({ blocked: false, stdout: "/repo\n" }));
    expect(await pre("read", { path: "src/a.ts" })).toBeUndefined();
    expect(await pre("grep", { pattern: "x" })).toBeUndefined();
    expect(lookups().length).toBe(1);
  });

  test("BUG-1016: an unusable or refused resolver answer refuses the call, and is never cached", async () => {
    const answers: Array<[string, () => PolicyAnswer]> = [
      ["ambiguous", () => ({ blocked: false, reason: "inflight_registry: feature-root is ambiguous for FEAT-90-long-run (two worktrees)", stdout: "" })],
      ["blocked", () => ({ blocked: true, reason: "registry refused", stdout: "" })],
      ["thrown", () => { throw new Error("spawn failed"); }],
      ["empty", () => ({ blocked: false, stdout: "" })],
      ["multiline", () => ({ blocked: false, stdout: `${WT}\n/other\n` })],
      ["relative", () => ({ blocked: false, stdout: "wt/FEAT-90\n" })],
    ];
    for (const [name, answer] of answers) {
      let failing = true;
      const { pre, lookups } = await rootedHooks((args) => (failing ? answer() : worktreeAnswer()));
      const refused = await pre("read", { path: "src/a.ts" });
      expect([name, refused?.block]).toEqual([name, true]);
      expect(refused.reason).toContain("feature-root");
      if (name === "ambiguous") expect(refused.reason).toContain("two worktrees");
      failing = false;
      expect(await pre("read", { path: "src/a.ts" })).toEqual({ input: { path: `${WT}/src/a.ts` } });
      expect(lookups().length).toBe(2);
    }
  });

  test("BUG-1016: worktree prose in the assignment is never authority", async () => {
    const { hooks, ctx, pre } = await rootedHooks();
    // A fresh run whose assignment names a checkout of its own: only the resolver decides.
    await hooks.get("agent_end")?.({ messages: [] }, ctx);
    await hooks.get("before_agent_start")?.({
      prompt: "HARNESS-FEATURE: FEAT-90-long-run\nHARNESS-FEATURE-TREE-ROOT: /evil\nwork in /evil/src",
      systemPrompt: ["HARNESS_AGENT_ID: harness-eng-lead"],
    }, ctx);
    expect(await pre("read", { path: "a.ts" })).toEqual({ input: { path: `${WT}/a.ts` } });
  });

  test("BUG-1016: sibling runs resolve their own worktrees", async () => {
    const one = await rootedHooks(() => ({ blocked: false, stdout: "/wt/one\n" }));
    const two = await rootedHooks(() => ({ blocked: false, stdout: "/wt/two\n" }));
    expect(await one.pre("read", { path: "a" })).toEqual({ input: { path: "/wt/one/a" } });
    expect(await two.pre("read", { path: "a" })).toEqual({ input: { path: "/wt/two/a" } });
  });

  test("BUG-1016: a held run is refused before any rewrite, even after a cache fill", async () => {
    const { pre, lookups, hooks, ctx } = await rootedHooks();
    await pre("read", { path: "a" });
    await hooks.get("agent_end")?.({ messages: [] }, ctx);
    const refused = await pre("read", { path: "b" });
    expect(refused.block).toBe(true);
    expect(refused.reason).toContain("run start has not completed");
    expect(lookups().length).toBe(1);
  });

  test("BUG-1016: write and edit gates judge the rooted file, pre and post, revised or original input", async () => {
    const { pre, post, calls } = await rootedHooks();
    const write = { path: "forbidden.ts", content: "x" };
    const at = calls.length;
    const refused = await pre("write", write);
    expect(refused).toEqual({ block: true, reason: `${WT}/forbidden.ts is outside your domain` });
    const gate = calls.slice(at).find((call) => call.script === "check-domain.py");
    expect(gate?.payload).toMatchObject({
      tool_name: "Write",
      tool_input: { file_path: `${WT}/forbidden.ts`, content: "x" },
      harness_feature: "FEAT-90-long-run",
      agent_type: "harness-eng-lead",
    });
    for (const input of [write, { path: `${WT}/forbidden.ts`, content: "x" }]) {
      const result = await post("write", input);
      expect(result.isError).toBe(true);
      expect(result.content[1].text).toBe(`Harness post-write check: ${WT}/forbidden.ts is outside your domain`);
    }
    for (const input of [{ input: "[forbidden.ts#1A2B]\nPUT 1:\n+x" }, { input: `[${WT}/forbidden.ts#1A2B]\nPUT 1:\n+x` }]) {
      expect((await post("edit", input)).isError).toBe(true);
    }
    expect((await pre("edit", { input: "[forbidden.ts#1A2B]\nPUT 1:\n+x" })).block).toBe(true);
  });

  test("BUG-1016: BUG-2003's URI rule holds beside a rooted sibling, MV included", async () => {
    const { pre, post, calls, domainTargets } = await rootedHooks();
    let at = calls.length;
    expect(await pre("edit", { input: "[agent://LeadTwo#1A2B]\nPUT 1:\n+x\n[ok.ts#1A2B]\nPUT 1:\n+y" }))
      .toEqual({ input: { input: `[agent://LeadTwo#1A2B]\nPUT 1:\n+x\n[${WT}/ok.ts#1A2B]\nPUT 1:\n+y` } });
    expect(domainTargets(at)).toEqual([`${WT}/ok.ts`]);
    at = calls.length;
    const refused = await pre("edit", { input: "[ok.ts#1A2B]\nMV conflict://1" });
    expect(refused.block).toBe(true);
    expect(refused.reason).toContain("conflict://1");
    expect(domainTargets(at)).toEqual([`${WT}/ok.ts`]);
    expect(await pre("edit", { input: "[agent://LeadTwo#1A2B]\nPUT 1:\n+x\n[forbidden.ts#1A2B]\nPUT 1:\n+y" }))
      .toEqual({ block: true, reason: `${WT}/forbidden.ts is outside your domain` });
    expect(await post("write", { path: "xd://report_issue", content: "x" })).toBeUndefined();
  });

  test("BUG-1016: a successful rewrite is silent", async () => {
    const { post } = await rootedHooks();
    expect(await post("write", { path: "notes/a.md", content: "x" })).toBeUndefined();
    expect(await post("edit", { input: "[notes/a.md#1A2B]\nPUT 1:\n+x" })).toBeUndefined();
  });

  // --- FEAT-1928: the hook is the one schema authority for a harness dispatch, and a yield's
  // `data` object is the digest the validator receives.
  const leadCtx = () => ompContext("/repo", "LeadOne", "OrchestratorOne", "parent-session");
  const mainCtx = () => ompContext("/repo", "Main", undefined, "main-session");
  const guardCalls = (calls: Array<{ script: string }>) =>
    calls.filter((call) => call.script === "dispatch-guard.py");
  const digestCalls = <Call extends { script: string }>(calls: Call[]) =>
    calls.filter((call) => call.script === "validate-digest.py");
  const ASSIGNMENT = "HARNESS-FEATURE: FEAT-90-long-run\nbuild it";

  test("refuses outputSchema or schemaMode at the top level and in any item, naming it, the main session included", async () => {
    for (const dispatcher of ["lead", "main"]) {
      const { handlers, calls } = fixture();
      const ctx = dispatcher === "main" ? mainCtx() : leadCtx();
      if (dispatcher === "main") {
        await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, ctx);
      } else {
        await start(handlers, ctx);
      }
      const flat = await handlers.get("tool_call")?.({
        toolName: "task", toolCallId: "flat",
        input: { agent: "harness-backend-dev", task: ASSIGNMENT, outputSchema: { type: "object" } },
      }, ctx);
      expect(flat?.block).toBe(true);
      expect(flat?.reason).toContain("never carry outputSchema:");
      const batch = await handlers.get("tool_call")?.({
        toolName: "task", toolCallId: "batch",
        input: {
          context: "shared",
          schemaMode: "strict",
          tasks: [
            { agent: "harness-backend-dev", task: ASSIGNMENT },
            { agent: "scout", task: "look", schemaMode: "permissive" },
          ],
        },
      }, ctx);
      expect(batch?.block).toBe(true);
      expect(batch?.reason).toContain("never carry schemaMode, tasks[1].schemaMode:");
      expect(guardCalls(calls)).toEqual([]);
    }
  });

  test("injects every one of the 16 personas' own strict bundle, leaving other targets and fields alone", async () => {
    const { handlers, calls } = fixture();
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
    const scout = { agent: "scout", name: "Look", task: "look" };
    const tasks = [
      ...DIGEST_PERSONAS.map((agent) => ({ agent, task: ASSIGNMENT, tools: ["read"] })),
      scout,
    ];
    const result = await handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "all", input: { context: "shared", tasks },
    }, mainCtx());
    expect(result?.block).toBeUndefined();
    const revised = result?.input as { context: string; tasks: Array<Record<string, unknown>> };
    expect(revised.context).toBe("shared");
    expect(revised.tasks).toHaveLength(17);
    DIGEST_PERSONAS.forEach((persona, index) => {
      const bundle = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, persona);
      expect(revised.tasks[index]).toEqual({ ...tasks[index], outputSchema: bundle, schemaMode: "strict" });
    });
    expect(revised.tasks[16]).toBe(scout);
    // BUG-2305: a successful dispatch carries no note telling the dispatcher about the fields.
    expect(result).not.toHaveProperty("additionalContext");
    // The governed preflight still judges every harness target of the accepted call.
    expect(guardCalls(calls)).toHaveLength(17);
  });

  test("injects into a flat governed dispatch and keeps its other fields", async () => {
    const { handlers } = fixture();
    await start(handlers);
    const input = { agent: "harness-qa", name: "Check", task: ASSIGNMENT, context: "ctx" };
    const result = await handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "flat", input,
    }, leadCtx());
    expect(result).toEqual({
      input: { ...input, outputSchema: loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-qa"), schemaMode: "strict" },
    });
  });

  // BUG-2305: OMP persists the revised call, so a dispatcher may send the injected pair back.
  // Keys reversed at every depth, so only structural equality — not JSON text — accepts it.
  const reordered = (value: unknown): unknown => Array.isArray(value)
    ? value.map(reordered)
    : value && typeof value === "object"
      ? Object.fromEntries(Object.entries(value as Record<string, unknown>).reverse()
        .map(([key, item]) => [key, reordered(item)]))
      : value;
  const mainFixture = async () => {
    const f = fixture();
    await f.handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
    return f;
  };
  const dispatch = async (handlers: Map<string, any>, input: Record<string, unknown>) =>
    await handlers.get("tool_call")?.({ toolName: "task", toolCallId: "copy", input }, mainCtx()) as
      Record<string, any> | undefined;

  test("BUG-2305: every persona's injected bundle, copied back strict, is accepted flat and per item", async () => {
    for (const persona of DIGEST_PERSONAS) {
      const { handlers, calls } = await mainFixture();
      const first = await dispatch(handlers, { agent: persona, name: "One", task: ASSIGNMENT });
      const injected = first?.input.outputSchema;
      const bundle = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, persona);
      expect(injected).toEqual(bundle);
      for (const copy of [structuredClone(injected), reordered(structuredClone(injected))]) {
        expect(copy).not.toBe(injected);
        const flatInput = { agent: persona, name: "Two", task: ASSIGNMENT, outputSchema: copy, schemaMode: "strict" };
        const flat = await dispatch(handlers, flatInput);
        expect({ persona, block: flat?.block, reason: flat?.reason }).toEqual({ persona, block: undefined, reason: undefined });
        expect(flat).toEqual({ input: { ...flatInput, outputSchema: bundle, schemaMode: "strict" } });
        expect(flat?.input.outputSchema).not.toBe(copy);
        const item = { agent: persona, name: "Three", task: ASSIGNMENT, outputSchema: copy, schemaMode: "strict" };
        const batch = await dispatch(handlers, { context: "shared", tasks: [item] });
        expect({ persona, block: batch?.block, reason: batch?.reason }).toEqual({ persona, block: undefined, reason: undefined });
        expect(batch).toEqual({ input: { context: "shared", tasks: [{ ...item, outputSchema: bundle, schemaMode: "strict" }] } });
        expect(batch?.input.tasks[0].outputSchema).not.toBe(copy);
      }
      expect(guardCalls(calls)).toHaveLength(5);
    }
  });

  test("BUG-2305: a batch accepts copies at any position beside plain and non-harness items", async () => {
    const { handlers, calls } = await mainFixture();
    const qa = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-qa");
    const pm = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-pm");
    const tasks = [
      { agent: "harness-qa", task: ASSIGNMENT, outputSchema: reordered(structuredClone(qa)), schemaMode: "strict" },
      { agent: "harness-backend-dev", task: ASSIGNMENT },
      { agent: "scout", task: "look" },
      { agent: "harness-pm", task: ASSIGNMENT, schemaMode: "strict", outputSchema: structuredClone(pm) },
    ];
    const result = await dispatch(handlers, { context: "shared", tasks });
    expect(result?.block).toBeUndefined();
    expect(result?.input.tasks).toEqual([
      { ...tasks[0], outputSchema: qa, schemaMode: "strict" },
      { ...tasks[1], outputSchema: loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-backend-dev"), schemaMode: "strict" },
      tasks[2],
      { ...tasks[3], outputSchema: pm, schemaMode: "strict" },
    ]);
    expect(result).not.toHaveProperty("additionalContext");
    expect(guardCalls(calls)).toHaveLength(4);
  });

  test("BUG-2305: every other schema control is refused flat and per item, naming field and location", async () => {
    const qa = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-qa");
    const changed = { ...structuredClone(qa), additionalProperties: true };
    const target = (controls: Record<string, unknown>, agent = "harness-qa") =>
      ({ agent, name: "Check", task: agent.startsWith("harness-") ? ASSIGNMENT : "look", ...controls });
    const cases: Array<[string, Record<string, unknown>, string, string?]> = [
      ["changed schema, strict", { outputSchema: changed, schemaMode: "strict" }, "outputSchema"],
      ["wrong persona's bundle", { outputSchema: loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-pm"), schemaMode: "strict" }, "outputSchema"],
      ["exact, permissive", { outputSchema: structuredClone(qa), schemaMode: "permissive" }, "schemaMode"],
      ["exact, null mode", { outputSchema: structuredClone(qa), schemaMode: null }, "schemaMode"],
      ["exact, boolean mode", { outputSchema: structuredClone(qa), schemaMode: true }, "schemaMode"],
      ["exact, number mode", { outputSchema: structuredClone(qa), schemaMode: 1 }, "schemaMode"],
      ["exact, object mode", { outputSchema: structuredClone(qa), schemaMode: { mode: "strict" } }, "schemaMode"],
      ["schema without mode", { outputSchema: structuredClone(qa) }, "outputSchema"],
      ["mode without schema", { schemaMode: "strict" }, "schemaMode"],
      ["non-harness schema", { outputSchema: structuredClone(qa) }, "outputSchema", "scout"],
      ["non-harness mode", { schemaMode: "strict" }, "schemaMode", "scout"],
      ["non-harness pair", { outputSchema: structuredClone(qa), schemaMode: "strict" }, "outputSchema", "scout"],
    ];
    for (const [label, controls, field, agent] of cases) {
      const { handlers, calls } = await mainFixture();
      const flat = await dispatch(handlers, target(controls, agent));
      expect({ label, block: flat?.block }).toEqual({ label, block: true });
      expect(flat?.reason).toMatch(new RegExp(`never carry (\\S+, )*${field}[,:]`));
      const batch = await dispatch(handlers, { context: "shared", tasks: [target(controls, agent)] });
      expect({ label, block: batch?.block }).toEqual({ label, block: true });
      expect(batch?.reason).toContain(`tasks[0].${field}`);
      expect(guardCalls(calls)).toEqual([]);
    }
  });

  test("BUG-2305: batch top-level controls stay refused even as an exact copy, one or both", async () => {
    const qa = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-qa");
    for (const controls of [
      { outputSchema: structuredClone(qa) }, { schemaMode: "strict" },
      { outputSchema: structuredClone(qa), schemaMode: "strict" },
    ]) {
      const { handlers, calls } = await mainFixture();
      const result = await dispatch(handlers, {
        context: "shared", ...controls, tasks: [{ agent: "harness-qa", task: ASSIGNMENT }],
      });
      expect(result?.block).toBe(true);
      for (const field of Object.keys(controls)) expect(result?.reason).toMatch(new RegExp(`never carry (\\S+, )*${field}[,:]`));
      expect(guardCalls(calls)).toEqual([]);
    }
  });

  test("BUG-2305: an accepted copy never masks a later invalid item", async () => {
    const { handlers, calls } = await mainFixture();
    const qa = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-qa");
    const result = await dispatch(handlers, {
      context: "shared",
      tasks: [
        { agent: "harness-qa", task: ASSIGNMENT, outputSchema: structuredClone(qa), schemaMode: "strict" },
        { agent: "harness-pm", task: ASSIGNMENT },
        { agent: "harness-qa", task: ASSIGNMENT, outputSchema: structuredClone(qa), schemaMode: "permissive" },
      ],
    });
    expect(result?.block).toBe(true);
    expect(result?.reason).toContain("never carry tasks[2].outputSchema, tasks[2].schemaMode:");
    expect(result?.reason).not.toContain("tasks[0]");
    expect(guardCalls(calls)).toEqual([]);
  });

  test("BUG-2305: a copied pair for a persona whose bundle cannot load is refused before any claim", async () => {
    const { handlers, calls } = await mainFixture();
    const result = await dispatch(handlers, {
      agent: "harness-nobody", task: ASSIGNMENT, outputSchema: { type: "object" }, schemaMode: "strict",
    });
    expect(result?.block).toBe(true);
    expect(guardCalls(calls)).toEqual([]);
  });

  test("no injection note when nothing was injected", async () => {
    const { handlers } = fixture();
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
    for (const input of [
      { agent: "scout", name: "Look", task: "look" },
      { context: "shared", tasks: [{ agent: "scout", name: "Look", task: "look" }] },
    ]) {
      const result = await handlers.get("tool_call")?.({
        toolName: "task", toolCallId: "plain", input,
      }, mainCtx()) as Record<string, unknown> | undefined;
      expect(result?.block).toBeUndefined();
      expect(result?.additionalContext).toBeUndefined();
    }
  });

  test("refuses a harness dispatch whose schema cannot load, before any claim, with no loose fallback", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const result = await handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "nobody",
      input: {
        context: "shared",
        tasks: [
          { agent: "harness-backend-dev", task: ASSIGNMENT },
          { agent: "harness-nobody", task: ASSIGNMENT },
        ],
      },
    }, leadCtx());
    expect(result).toEqual({
      block: true,
      reason: expect.stringContaining('unknown persona "harness-nobody"'),
    });
    expect(guardCalls(calls)).toEqual([]);
  });

  test("hands the yield's data to validate-digest.py unmodified as digest_object", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const data = {
      VERDICT: "FAIL",
      DIGEST: { headline: "x", findings: [{ kind: "form", note: "a: b" }], empty: {} },
      artifact: "notes/x.md",
    };
    await handlers.get("tool_call")?.({ toolName: "yield", input: { data } }, leadCtx());
    const [validation] = digestCalls(calls);
    expect(objectPayload(validation.payload).digest_object).toEqual(data);
    expect(validation.payload).not.toHaveProperty("last_assistant_message");
  });

  test("blocks a yield whose data is not one object, even with a digest in the last assistant message", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    const digestText = "VERDICT: PASS\nDIGEST:\n  headline: x\nartifact: none\n";
    await handlers.get("message_end")?.({
      message: { role: "assistant", content: [{ type: "text", text: digestText }] },
    }, leadCtx());
    for (const input of [
      { data: digestText }, { data: null }, { data: [PASS_DIGEST] }, {},
      { result: { data: PASS_DIGEST } }, { error: "gave up" },
    ]) {
      expect(await handlers.get("tool_call")?.({ toolName: "yield", input }, leadCtx())).toEqual({
        block: true, reason: expect.stringContaining(RETURN_THE_OBJECT),
      });
    }
    expect(digestCalls(calls)).toEqual([]);
  });

  // BUG-2171: some models serialize the yield's object as a JSON string. OMP's own yield tool
  // parses such a string losslessly, but the hook ran first and refused it, so a complete
  // return could exhaust its retries. A string that parses to one plain object is that object.
  test("BUG-2171 string-serialized PASS digest is validated as the object it encodes", async () => {
    const yieldOnce = async (data: unknown) => {
      const { handlers, calls } = fixture();
      await start(handlers);
      const verdict = await handlers.get("tool_call")?.({ toolName: "yield", input: { data } }, leadCtx());
      return { verdict, validations: digestCalls(calls) };
    };
    const asObject = await yieldOnce(PASS_DIGEST);
    const asString = await yieldOnce(JSON.stringify(PASS_DIGEST));
    expect(asString.validations).toHaveLength(1);
    expect(objectPayload(asString.validations[0].payload).digest_object).toEqual(PASS_DIGEST);
    expect(asString.verdict).toEqual(asObject.verdict);
  });

  test("BUG-2171 a string that does not parse to one plain object is still refused", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    for (const data of ["{not json", "null", "[1]", JSON.stringify("PASS"), JSON.stringify([PASS_DIGEST])]) {
      expect(await handlers.get("tool_call")?.({ toolName: "yield", input: { data } }, leadCtx())).toEqual({
        block: true, reason: expect.stringContaining(RETURN_THE_OBJECT),
      });
    }
    expect(digestCalls(calls)).toEqual([]);
  });

  test("agent_end validates nothing: the yield is the one digest gate", async () => {
    const { handlers, calls } = fixture();
    await start(handlers);
    await handlers.get("agent_end")?.({
      messages: [{ role: "assistant", content: "VERDICT: PASS\nDIGEST:\n  headline: x\n" }],
    }, leadCtx());
    expect(digestCalls(calls)).toEqual([]);
  });

  // -------------------------------------------------------------------------
  // FEAT-2225 T-04: expertise_apply, each persona's host-bound Expertise pen, and the merge
  // gate on Main's own Bash merges.
  // -------------------------------------------------------------------------
  const OP_TEXT = { type: "string", minLength: 1 };
  const OP_SECTION = { enum: ["Patterns", "Gotchas", "Outcomes", "Open"] };
  const APPLY_SCHEMA = {
    type: "object",
    closed: true,
    shape: {
      tier: { enum: ["craft", "repository"] },
      repository: { type: "string", pattern: "^[a-z0-9][a-z0-9-]*$", isOptional: true },
      ops: {
        type: "array",
        items: {
          anyOf: [
            {
              type: "object",
              closed: true,
              shape: { op: { enum: ["add", "replace"] }, target: OP_TEXT, section: OP_SECTION, entry: OP_TEXT, why: OP_TEXT },
            },
            {
              type: "object",
              closed: true,
              shape: { op: { const: "drop" }, target: OP_TEXT, section: OP_SECTION, why: OP_TEXT },
            },
          ],
        },
      },
      supersedes: { type: "array", items: { type: "string", pattern: "^[0-9a-f]{64}$" }, isOptional: true },
    },
  };
  const ADD = { op: "add", target: "P-1", section: "Patterns", entry: "a lesson", why: "seen twice" };
  const BATCH = "a".repeat(64);
  const IDENTITY = (root: string) => [
    "--root", root, "--feature", "FEAT-90-long-run", "--persona", "harness-eng-lead",
    "--runtime-id", "LeadOne", "--parent-id", "OrchestratorOne",
  ];

  // A feature tree on disk with the craft tier and one declared repository tier; with `main`,
  // a git checkout whose origin/HEAD names a main commit.
  function featureTree(main = false): string {
    const root = realpathSync(mkdtempSync(join(tmpdir(), "f2225-tree-")));
    mkdirSync(join(root, ".harness", "expertise"), { recursive: true });
    mkdirSync(join(root, ".harness", "harness", "expertise"), { recursive: true });
    if (!main) return root;
    const git = (...args: string[]) => spawnSync("git", args, { cwd: root, encoding: "utf8" });
    git("init", "-q");
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base");
    git("update-ref", "refs/remotes/origin/main", "HEAD");
    git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main");
    return root;
  }

  async function startDistill(
    handlers: Map<string, Function>,
    ctx: Record<string, unknown> = leadCtx(),
    agent = "harness-eng-lead",
    mission = "distill",
  ) {
    const assignment = `HARNESS-FEATURE: FEAT-90-long-run\nHARNESS-MISSION: ${mission}\ndistill your lessons`;
    await handlers.get("before_agent_start")?.({
      prompt: `Complete assignment thoroughly:\n\n${assignment}`,
      systemPrompt: [`HARNESS_AGENT_ID: ${agent}`],
    }, ctx);
    await handlers.get("message_end")?.({
      message: { role: "user", content: [{ type: "text", text: assignment }] },
    }, ctx);
  }

  function applyHooks(root: string, options: Parameters<typeof fixture>[0] = {}) {
    const hooks = fixture({ featureRoot: () => ({ blocked: false, stdout: `${root}\n` }), ...options });
    const apply = (params: Record<string, unknown>, ctx: Record<string, unknown> = leadCtx(), id = "call-apply") =>
      hooks.tools.get("expertise_apply").execute(id, params, undefined, undefined, ctx);
    const coreCalls = () => hooks.calls.filter((call) => call.script === "expertise-merge.py");
    return { ...hooks, apply, coreCalls };
  }

  test("FEAT-2225: registers expertise_apply with the exact closed argument schema", () => {
    const { tools } = fixture();
    const tool = tools.get("expertise_apply");
    expect(tool?.name).toBe("expertise_apply");
    expect(typeof tool.execute).toBe("function");
    expect(JSON.parse(JSON.stringify(tool.parameters))).toEqual(APPLY_SCHEMA);
  });

  test("FEAT-2225: persona, feature, run id, root, destination, base and state arguments are refused before the core runs", async () => {
    const { handlers, apply, coreCalls } = applyHooks(featureTree());
    await startDistill(handlers);
    for (const key of ["persona", "feature", "runtime_id", "parent_id", "root", "destination", "base", "state"]) {
      await expect(apply({ tier: "craft", ops: [ADD], [key]: "spoofed" })).rejects.toThrow(`argument "${key}"`);
    }
    await expect(apply({ tier: "global", ops: [ADD] })).rejects.toThrow("tier");
    await expect(apply({ tier: "craft", ops: "not a list" })).rejects.toThrow("ops");
    await expect(apply({ tier: "craft", ops: [ADD], supersedes: ["../batch"] })).rejects.toThrow("supersedes");
    expect(coreCalls()).toEqual([]);
  });

  test("FEAT-2225: an unidentified, non-distill, held, unready, unplaced or unauthorized caller is refused", async () => {
    const root = featureTree();
    const refusals: Array<[string, () => Promise<any>, Record<string, unknown>, string]> = [
      ["main", async () => {
        const hooks = applyHooks(root);
        await hooks.handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
        return hooks;
      }, mainCtx(), "governed Harness persona"],
      ["build mission", async () => {
        const hooks = applyHooks(root);
        await startDistill(hooks.handlers, leadCtx(), "harness-eng-lead", "build");
        return hooks;
      }, leadCtx(), "HARNESS-MISSION: distill"],
      ["no mission", async () => {
        const hooks = applyHooks(root);
        await start(hooks.handlers);
        return hooks;
      }, leadCtx(), "HARNESS-MISSION: distill"],
      ["held", async () => {
        const hooks = applyHooks(root);
        await startDistill(hooks.handlers, ompContext("/repo", "LeadOne", "OtherParent", "s"));
        return hooks;
      }, ompContext("/repo", "LeadOne", "OtherParent", "s"), "already claimed under a different parent"],
      ["unready", async () => {
        const hooks = applyHooks(root);
        await startDistill(hooks.handlers);
        await hooks.handlers.get("agent_end")?.({ messages: [] }, leadCtx());
        return hooks;
      }, leadCtx(), "run start has not completed"],
      ["unplaced", async () => {
        const hooks = applyHooks(root, { featureRoot: () => ({ blocked: true, reason: "registry refused", stdout: "" }) });
        await startDistill(hooks.handlers);
        return hooks;
      }, leadCtx(), "feature-root refused"],
      ["unauthorized", async () => {
        const hooks = applyHooks(root);
        await startDistill(hooks.handlers, ompContext("/repo", "AuthorizeError", "LeadOne", "c"), "harness-backend-dev");
        return hooks;
      }, ompContext("/repo", "AuthorizeError", "LeadOne", "c"), "authorization gate crashed"],
    ];
    for (const [name, make, ctx, why] of refusals) {
      const hooks = await make();
      const error = await hooks.apply({ tier: "craft", ops: [ADD] }, ctx).then(() => undefined, (e: Error) => e.message);
      expect([name, error]).toEqual([name, expect.stringContaining(why)]);
      expect([name, hooks.coreCalls()]).toEqual([name, []]);
    }
  });

  test("FEAT-2225: the custom mutator takes the existing claim authorization and held-run refusal in tool_call", async () => {
    const root = featureTree();
    const { handlers, calls } = applyHooks(root);
    await startDistill(handlers);
    const at = calls.length;
    const call = { toolName: "expertise_apply", toolCallId: "call-apply", input: { tier: "craft", ops: [ADD] } };
    expect(await handlers.get("tool_call")?.(call, leadCtx())).toBeUndefined();
    expect(calls.slice(at).map((c) => [c.script, c.args[0]])).toContainEqual(["inflight_registry.py", "authorize"]);
    const crashed = applyHooks(root);
    const crashCtx = ompContext("/repo", "AuthorizeError", "LeadOne", "c");
    await startDistill(crashed.handlers, crashCtx, "harness-backend-dev");
    expect(await crashed.handlers.get("tool_call")?.(call, crashCtx))
      .toEqual({ block: true, reason: "authorization gate crashed" });
    await handlers.get("agent_end")?.({ messages: [] }, leadCtx());
    const held = await handlers.get("tool_call")?.(call, leadCtx());
    expect(held?.block).toBe(true);
    expect(held?.reason).toContain("run start has not completed");
  });

  test("FEAT-2225: craft and repository destinations run member-ops with host-derived identity and return its receipt verbatim", async () => {
    const root = featureTree();
    const { handlers, apply, coreCalls, calls } = applyHooks(root);
    await startDistill(handlers);
    const craft = await apply({ tier: "craft", ops: [ADD] });
    expect(craft.content).toEqual([{ type: "text", text: MEMBER_OPS_RECEIPT }]);
    expect(craft.details).toEqual(JSON.parse(MEMBER_OPS_RECEIPT));
    await apply({ tier: "repository", repository: "harness", ops: [ADD] }, leadCtx(), "call-repo");
    expect(coreCalls().map((call) => call.args)).toEqual([
      ["member-ops", ...IDENTITY(root), "--tier", "craft", "--ops", "-"],
      ["member-ops", ...IDENTITY(root), "--tier", "repository", "--repository", "harness", "--ops", "-"],
    ]);
    // member-ops receives its ops LIST as the stdin document, typed as the list it is.
    expect(coreCalls().map((call) => call.payload)).toEqual([[ADD], [ADD]]);
    // BUG-2390: the runner contract accepts that list. A narrow gate that failed on a list
    // payload has no command to guard, so its failure refuses nothing.
    const failed: hooks.PolicyProcess = { status: 1, signal: null, stdout: "", stderr: "boom", timedOut: false };
    expect(hooks.classifyPolicyRun("merge-gate.py", coreCalls()[0].payload, failed).blocked).toBe(false);
    expect(coreCalls().map((call) => call.cwd)).toEqual([root, root]);
    // The post-write check judges the destination the host resolved, never a caller path.
    const at = calls.length;
    expect(await handlers.get("tool_result")?.({
      toolName: "expertise_apply", toolCallId: "call-repo", content: [],
      input: { tier: "repository", repository: "harness", ops: [ADD], destination: "/evil.md" },
    }, leadCtx())).toBeUndefined();
    expect(calls.slice(at).filter((call) => call.script === "check-domain.py").map((call) =>
      [call.args, objectPayload(call.payload).tool_name, (objectPayload(call.payload).tool_input as Record<string, unknown>).file_path]))
      .toEqual([[["--post"], "Edit", `${root}/.harness/harness/expertise/harness-eng-lead.md`]]);
  });

  test("FEAT-2225: a repository segment with separators, traversal, an undeclared name or a symlink is refused before the core runs", async () => {
    const root = featureTree();
    const outside = realpathSync(mkdtempSync(join(tmpdir(), "f2225-outside-")));
    mkdirSync(join(outside, "expertise"));
    symlinkSync(outside, join(root, ".harness", "linked"));
    const { handlers, apply, coreCalls } = applyHooks(root);
    await startDistill(handlers);
    for (const repository of ["../harness", "harness/expertise", "..", ".", "", "/abs", "Harness", "expertise", "undeclared", "linked"]) {
      const error = await apply({ tier: "repository", repository, ops: [ADD] }).then(() => undefined, (e: Error) => e.message);
      expect([repository, error]).toEqual([repository, expect.stringContaining("repository")]);
    }
    await expect(apply({ tier: "repository", ops: [ADD] })).rejects.toThrow("repository");
    await expect(apply({ tier: "craft", repository: "harness", ops: [ADD] })).rejects.toThrow("repository");
    symlinkSync(join(outside, "x.md"), join(root, ".harness", "expertise", "harness-eng-lead.md"));
    await expect(apply({ tier: "craft", ops: [ADD] })).rejects.toThrow("symlink");
    expect(coreCalls()).toEqual([]);
  });

  test("FEAT-2225: any nonzero member-ops exit, or a missing receipt, is a tool failure carrying the core's words", async () => {
    const root = featureTree();
    const answers: Array<[PolicyAnswer, string]> = [
      [{ blocked: false, reason: "expertise-merge.py exited 14", stdout: "CANDIDATE REFUSED check-expertise failed\n" }, "CANDIDATE REFUSED"],
      [{ blocked: false, reason: "expertise-merge.py exited 9", stdout: "REFUSED destination\n" }, "exited 9"],
      [{ blocked: true, reason: "denied by core", stdout: "" }, "denied by core"],
      [{ blocked: false, stdout: "no receipt here\n" }, "no receipt"],
    ];
    for (const [answer, words] of answers) {
      const { handlers, apply, calls } = applyHooks(root, { memberOps: () => answer });
      await startDistill(handlers);
      await expect(apply({ tier: "craft", ops: [ADD] })).rejects.toThrow(words);
      // A failed application leaves no destination for the post-write check to judge.
      const at = calls.length;
      await handlers.get("tool_result")?.({
        toolName: "expertise_apply", toolCallId: "call-apply", content: [], isError: true, input: {},
      }, leadCtx());
      expect(calls.slice(at).filter((call) => call.script === "check-domain.py")).toEqual([]);
    }
  });

  // F1 (validate c1): the HARNESS-MISSION marker alone never authorizes an application. The
  // registered lineage does, answered by validate-digest.py --distill-authority for this exact run.
  test("FEAT-2225 F1: a distill marker under a non-distill registered run is refused and member-ops never runs", async () => {
    const root = featureTree();
    const refusals: PolicyAnswer[] = [
      { blocked: true, reason: "harness-eng-lead's registered run 'build-engineering' is not a feature-close distill run", stdout: "" },
      { blocked: false, reason: "validate-digest.py exited 1", stdout: "" },
      { blocked: false, stdout: '{"authorized": false}\n' },
      { blocked: false, stdout: "" },
    ];
    for (const answer of refusals) {
      const asked: Array<Record<string, unknown>> = [];
      const { handlers, apply, coreCalls, calls } = applyHooks(root, {
        distillAuthority: (payload) => { asked.push(payload); return answer; },
      });
      await startDistill(handlers);
      const error = await apply({ tier: "craft", ops: [ADD] }).then(() => undefined, (e: Error) => e.message);
      expect([answer, error]).toEqual([answer, expect.stringContaining("expertise_apply refused")]);
      if (answer.reason) expect(error).toContain(answer.reason);
      expect(coreCalls()).toEqual([]);
      expect(asked).toEqual([{
        agent_type: "harness-eng-lead", harness_feature: "FEAT-90-long-run", harness_agent_id: "LeadOne",
        harness_parent_agent_id: "OrchestratorOne", cwd: root,
      }]);
      expect(calls.find((call) => call.args[0] === "--distill-authority")?.cwd).toBe(root);
    }
  });

  test("FEAT-2225: supersedes carries exact batch ids and the host-resolved main base, never a caller base", async () => {
    const root = featureTree(true);
    const main = spawnSync("git", ["rev-parse", "refs/remotes/origin/HEAD"], { cwd: root, encoding: "utf8" }).stdout.trim();
    const { handlers, apply, coreCalls } = applyHooks(root);
    await startDistill(handlers);
    await apply({ tier: "craft", ops: [ADD], supersedes: [BATCH] });
    expect(coreCalls().map((call) => call.args)).toEqual([
      ["member-ops", ...IDENTITY(root), "--tier", "craft", "--ops", "-", "--supersedes", BATCH, "--base", main],
    ]);
    const bare = applyHooks(featureTree());
    await startDistill(bare.handlers);
    await expect(bare.apply({ tier: "craft", ops: [], supersedes: [BATCH] })).rejects.toThrow("origin/HEAD");
    expect(bare.coreCalls()).toEqual([]);
  });

  test("FEAT-2225: Main's Bash git merge and gh pr merge reach merge-gate before the non-governed return", async () => {
    const seen: Array<Record<string, unknown>> = [];
    const { handlers, calls } = fixture({
      mergeGate: (payload) => {
        seen.push(payload);
        return { blocked: true, reason: "merge-gate: run merge-gate.py merge-distill --root R --feature F --pr 42", stdout: "" };
      },
    });
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
    const commands = ["gh pr merge 42 --squash", "git merge feat/x", "bash -c 'git -C /x merge feat/y'"];
    for (const command of commands) {
      expect(await handlers.get("tool_call")?.({ toolName: "bash", toolCallId: "m", input: { command } }, mainCtx()))
        .toEqual({ block: true, reason: expect.stringContaining("merge-distill") });
    }
    expect(seen.map((payload) => [payload.agent_type, payload.harness_agent_id, payload.tool_name,
      (payload.tool_input as Record<string, unknown>).command])).toEqual(
      commands.map((command) => ["Main", "Main", "Bash", command]),
    );
    // Every other Main call stays ungoverned: no merge gate, no domain or shell guard.
    const at = calls.length;
    expect(await handlers.get("tool_call")?.({ toolName: "bash", input: { command: "git status" } }, mainCtx())).toBeUndefined();
    expect(await handlers.get("tool_call")?.({ toolName: "write", input: { path: "/repo/x", content: "x" } }, mainCtx())).toBeUndefined();
    expect(calls.slice(at)).toEqual([]);
    // A merge the gate passes runs as asked.
    const open = fixture();
    await open.handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
    expect(await open.handlers.get("tool_call")?.({ toolName: "bash", input: { command: "gh pr merge 7" } }, mainCtx())).toBeUndefined();
    expect(open.calls.map((call) => call.script)).toContain("merge-gate.py");
  });

  // FEAT-2337 (DEC-100): Main's merge path reads merge-gate's failure through the same narrow
  // classification. The `\bmerge\b` pre-screen still only spares a spawn; whether a gate that
  // could not answer refuses is merge_ref's call, so an abort, a search or an echo stays allowed.
  test("FEAT-2337: Main's merge is refused when merge-gate times out; a command it does not guard is not", async () => {
    const timedOut: hooks.PolicyProcess = { status: null, signal: "SIGKILL", stdout: "", stderr: "", timedOut: true };
    const seen: unknown[] = [];
    const { handlers } = fixture({
      mergeGate: (payload) => {
        seen.push((payload.tool_input as Record<string, unknown>).command);
        return hooks.classifyPolicyRun("merge-gate.py", payload, timedOut);
      },
    });
    await handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
    const call = async (command: string) =>
      handlers.get("tool_call")?.({ toolName: "bash", toolCallId: "m", input: { command } }, mainCtx());
    const guarded = ["git merge feat/x", "gh pr merge 42 --squash", "bash -c 'git -C /x merge feat/y'"];
    const unguarded = ["git merge --abort", "echo merge", "rg merge src/"];
    for (const command of guarded) {
      expect(await call(command)).toEqual({
        block: true,
        reason: expect.stringMatching(/^merge-gate: BLOCKED — the gate could not run \(exceeded its 30-second budget/),
      });
    }
    for (const command of unguarded) expect(await call(command)).toBeUndefined();
    expect(seen).toEqual([...guarded, ...unguarded]);
  });

  // -------------------------------------------------------------------------
  // FEAT-2274 (D-01, SC-01, SC-07, SC-09): a broad gate that could not run is not a pass.
  // The call proceeds, and the handler says so in passive additionalContext, phase-tagged
  // so omp's identical-string dedup cannot fold a pre notice into a post one.
  // -------------------------------------------------------------------------
  const notice = (gate: string, phase: string, reason = "crashed (RuntimeError: boom)") =>
    `Harness: ${gate} (${phase}) could not run; nothing was checked. ${reason}`;
  const unavailableAt = (scripts: string[], extra: { featureRoot?: (args: string[]) => PolicyAnswer } = {}) => fixture({
    ...extra,
    gate: (script) => scripts.includes(script)
      ? { blocked: false, unavailable: "crashed (RuntimeError: boom)", stdout: "" }
      : undefined,
  });
  const fileCall = (toolName: string, input: Record<string, unknown>) => ({
    toolName, toolCallId: "call-unavailable", input, content: [{ type: "text", text: "ok" }],
  });

  test("FEAT-2274: an unavailable check-domain lets the write proceed and says so, pre and post", async () => {
    const { handlers } = unavailableAt(["check-domain.py"]);
    await start(handlers);
    const event = fileCall("write", { path: "/repo/src/a.ts", content: "x" });
    const pre = await handlers.get("tool_call")?.(event, leadCtx());
    expect(pre).toEqual({ additionalContext: notice("check-domain", "pre") });
    expect(pre.additionalContext).toContain("nothing was checked");
    const post = await handlers.get("tool_result")?.(event, leadCtx());
    // Passive context only: the tool's own content stays the host's, and no isError key at all.
    expect(post).toEqual({ additionalContext: notice("check-domain", "post") });
    expect("isError" in post).toBe(false);
    expect(post.additionalContext).not.toBe(pre.additionalContext);
  });

  test("FEAT-2274: every unavailable invocation is reported again; nothing is cached for the session", async () => {
    const { handlers } = unavailableAt(["check-domain.py"]);
    await start(handlers);
    const event = fileCall("write", { path: "/repo/src/a.ts", content: "x" });
    for (let attempt = 0; attempt < 3; attempt += 1) {
      expect(await handlers.get("tool_call")?.(event, leadCtx()))
        .toEqual({ additionalContext: notice("check-domain", "pre") });
      expect(await handlers.get("tool_result")?.(event, leadCtx()))
        .toEqual({ additionalContext: notice("check-domain", "post") });
    }
  });

  test("FEAT-2274: several unavailable invocations on one call each keep their notice", async () => {
    const { handlers } = unavailableAt(["check-domain.py"]);
    await start(handlers);
    const event = fileCall("edit", { input: "[a/one.ts#A1B2]\nPUT 1:\n+x\n[b/two.ts#C3D4]\nPUT 1:\n+y" });
    expect(await handlers.get("tool_call")?.(event, leadCtx())).toEqual({
      additionalContext: [notice("check-domain", "pre"), notice("check-domain", "pre")].join("\n"),
    });
    expect(await handlers.get("tool_result")?.(event, leadCtx())).toEqual({
      additionalContext: [notice("check-domain", "post"), notice("check-domain", "post")].join("\n"),
    });
  });

  test("FEAT-2274: an explicit deny stays a refusal and a normal pass stays silent beside an unavailable gate", async () => {
    const { handlers } = fixture({
      gate: (script, _args, payload) => {
        if (script !== "check-domain.py") return undefined;
        const target = (objectPayload(payload).tool_input as Record<string, unknown>).file_path;
        if (target === "a/denied.ts") return { blocked: true, reason: "a/denied.ts is outside your domain", stdout: "" };
        if (target === "b/crashed.ts") return { blocked: false, unavailable: "crashed (RuntimeError: boom)", stdout: "" };
        return undefined;
      },
    });
    await start(handlers);
    const denied = fileCall("edit", { input: "[a/denied.ts#A1B2]\nPUT 1:\n+x\n[b/crashed.ts#C3D4]\nPUT 1:\n+y" });
    // Pre: omp 19.1.0 drops additionalContext from a blocking tool_call result and hands the
    // model only `reason`, so the sibling's notice rides in the reason, after the denial.
    expect(await handlers.get("tool_call")?.(denied, leadCtx())).toEqual({
      block: true,
      reason: ["a/denied.ts is outside your domain", notice("check-domain", "pre")].join("\n"),
    });
    // Post: the refusal is still an error, and the sibling's notice rides beside it.
    expect(await handlers.get("tool_result")?.(denied, leadCtx())).toEqual({
      content: [{ type: "text", text: "ok" }, { type: "text", text: "Harness post-write check: a/denied.ts is outside your domain" }],
      isError: true,
      additionalContext: notice("check-domain", "post"),
    });
    const clean = fileCall("write", { path: "c/fine.ts", content: "x" });
    expect(await handlers.get("tool_call")?.(clean, leadCtx())).toBeUndefined();
    expect(await handlers.get("tool_result")?.(clean, leadCtx())).toBeUndefined();
  });

  test("FEAT-2274: an ast_edit post notice leaves the tool's own content to the host, never an error", async () => {
    const { handlers } = unavailableAt(["check-domain.py"]);
    await start(handlers);
    const written = await handlers.get("tool_result")?.(
      { ...fileCall("ast_edit", { paths: ["src/a.ts"] }), content: [{ type: "text", text: "patched" }] }, leadCtx());
    expect(written).toEqual({ additionalContext: notice("check-domain", "post") });
  });

  test("FEAT-2274: an unavailable bash-write-guard keeps the HARNESS_AGENT_TYPE env revision beside its notice", async () => {
    const { handlers } = unavailableAt(["bash-write-guard.py"]);
    await start(handlers);
    const input = { command: "echo hi", env: { EXISTING: "kept" } };
    expect(await handlers.get("tool_call")?.({ toolName: "bash", input }, leadCtx())).toEqual({
      input: { ...input, env: { EXISTING: "kept", HARNESS_AGENT_TYPE: "harness-eng-lead" } },
      additionalContext: notice("bash-write-guard", "pre"),
    });
  });

  test("FEAT-2274: a governed Bash post sweep that could not run is reported as post", async () => {
    const { handlers } = unavailableAt(["check-domain.py"]);
    await start(handlers);
    const result = await handlers.get("tool_result")?.(fileCall("bash", { command: "echo hi" }), leadCtx());
    expect(result).toEqual({ additionalContext: notice("check-domain", "post") });
  });

  test("FEAT-2274: BUG-1016 rooting keeps its revised input beside the notice", async () => {
    const WT = "/worktrees/FEAT-90-long-run";
    const { handlers } = unavailableAt(["check-domain.py"], {
      featureRoot: () => ({ blocked: false, stdout: `${WT}\n` }),
    });
    await start(handlers);
    expect(await handlers.get("tool_call")?.(fileCall("write", { path: "notes/a.md", content: "x" }), leadCtx()))
      .toEqual({
        input: { path: `${WT}/notes/a.md`, content: "x" },
        additionalContext: notice("check-domain", "pre"),
      });
  });

  test("FEAT-2274: an unavailable dispatch-guard keeps the schema injection, one notice per target", async () => {
    const begins: Array<[Record<string, unknown>, (h: Map<string, Function>) => Promise<unknown>]> = [
      [leadCtx(), (h) => start(h)],
      [mainCtx(), async (h) => h.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx())],
    ];
    for (const [ctx, begin] of begins) {
      const { handlers, calls } = unavailableAt(["dispatch-guard.py"]);
      await begin(handlers);
      const tasks = [
        { agent: "harness-backend-dev", task: ASSIGNMENT },
        { agent: "harness-qa", task: ASSIGNMENT },
      ];
      const result = await handlers.get("tool_call")?.({
        toolName: "task", toolCallId: "unavailable-guard", input: { context: "shared", tasks },
      }, ctx);
      expect(result).toEqual({
        input: {
          context: "shared",
          tasks: tasks.map((item) => ({
            ...item, outputSchema: loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, item.agent), schemaMode: "strict",
          })),
        },
        additionalContext: [notice("dispatch-guard", "dispatch"), notice("dispatch-guard", "dispatch")].join("\n"),
      });
      expect(guardCalls(calls)).toHaveLength(2);
    }
  });

  test("FEAT-2274: an unavailable digest validator lets the yield through and says so; a refusal still blocks", async () => {
    const { handlers } = unavailableAt(["validate-digest.py"]);
    await start(handlers);
    expect(await handlers.get("tool_call")?.({ toolName: "yield", input: { data: PASS_DIGEST } }, leadCtx()))
      .toEqual({ additionalContext: notice("validate-digest", "yield") });
    // SC-09: the contract refusal for a missing digest object is not reclassified.
    expect(await handlers.get("tool_call")?.({ toolName: "yield", input: { data: "not an object" } }, leadCtx()))
      .toEqual({ block: true, reason: expect.stringContaining(RETURN_THE_OBJECT) });
    const refused = fixture();
    await start(refused.handlers);
    expect(await refused.handlers.get("tool_call")?.({ toolName: "yield", input: { data: PASS_DIGEST } }, leadCtx()))
      .toEqual({ block: true, reason: "children live" });
  });

  // -------------------------------------------------------------------------
  // FEAT-2274 (C4, SC-03): a governed persona is spawned through `task` and nothing else,
  // whoever the caller is. Which targets a caller may spawn is native policy, not this hook's.
  // -------------------------------------------------------------------------
  test("FEAT-2274: before_subagent_spawn refuses a harness target outside task, for Main and governed parents alike", async () => {
    const spawn = (h: Map<string, Function>, event: Record<string, unknown>) =>
      h.get("before_subagent_spawn")?.({ patterns: [], ...event }, leadCtx());
    const unstarted = fixture();
    const main = fixture();
    await main.handlers.get("before_agent_start")?.({ systemPrompt: ["project"] }, mainCtx());
    const governed = fixture();
    await start(governed.handlers);
    for (const { handlers } of [unstarted, main, governed]) {
      const refused = await spawn(handlers, { agent: "harness-backend-dev", invocationKind: "eval" });
      expect(refused).toEqual({ block: true, reason: expect.stringContaining("task tool") });
      expect(refused.reason).toContain("harness-backend-dev");
      expect(await spawn(handlers, { agent: "harness-pm", invocationKind: "workpool" }))
        .toEqual({ block: true, reason: expect.stringContaining("task tool") });
      expect(await spawn(handlers, { agent: "harness-pm" }))
        .toEqual({ block: true, reason: expect.stringContaining("task tool") });
      expect(await spawn(handlers, { agent: "harness-backend-dev", invocationKind: "task" })).toBeUndefined();
      expect(await spawn(handlers, { agent: "scout", invocationKind: "eval" })).toBeUndefined();
      expect(await spawn(handlers, { agent: "task", invocationKind: "eval" })).toBeUndefined();
    }
  });
});

// FEAT-2274 (C3): how one gate process's end is read. Broad gates report their own failure as
// `unavailable` and never block for it; narrow gates refuse only a command they guard; every
// other runPolicy caller (registry, feature record, digest destination) keeps its posture.
describe("classifyPolicyRun", () => {
  const BROAD = ["check-domain.py", "bash-write-guard.py", "dispatch-guard.py", "validate-digest.py"];
  const sh = (script: string) => spawnSync("/bin/sh", ["-c", script], { encoding: "utf8" });
  const bash = (command: string) => ({ tool_name: "Bash", tool_input: { command } });
  const classify = hooks.classifyPolicyRun;
  // Real process ends, not hand-written shapes: a crash exit, a kill, and a missing executable.
  const crashes: Array<[string, hooks.PolicyProcess]> = [
    ["exit 1", sh("echo 'Traceback: boom' >&2; exit 1")],
    ["exit 3", sh("exit 3")],
    ["signal", sh("kill -9 $$")],
    ["spawn error", spawnSync("/nonexistent/harness/bin/gate.py", [], { encoding: "utf8" })],
    ["thrown", { status: null, signal: null, stdout: "", stderr: "", error: new Error("spawnSync threw") }],
  ];

  test("the crash fixtures are the process ends they claim to be", () => {
    expect(crashes[0][1].status).toBe(1);
    expect(crashes[2][1].status).toBeNull();
    expect(crashes[2][1].signal).toBe("SIGKILL");
    expect((crashes[3][1].error as NodeJS.ErrnoException).code).toBe("ENOENT");
  });

  test("a declared unavailable line is unavailable, naming the gate, and not a block", () => {
    for (const script of BROAD) {
      const gate = script.slice(0, -3);
      const stdout = `${JSON.stringify({ decision: "unavailable", gate, reason: "RuntimeError: boom" })}\n`;
      const result = classify(script, {}, { status: 0, signal: null, stdout, stderr: "trace" });
      expect(result.blocked).toBe(false);
      expect(result.unavailable).toContain(gate);
      expect(result.unavailable).toContain("RuntimeError: boom");
      expect(result.reason).toBeUndefined();
    }
  });

  test("a broad gate's structured deny and exit 2 stay refusals; a normal pass carries no notice", () => {
    const deny = JSON.stringify({ hookSpecificOutput: { permissionDecision: "deny", permissionDecisionReason: "no" } });
    for (const script of BROAD) {
      expect(classify(script, {}, { status: 0, signal: null, stdout: deny, stderr: "" }))
        .toEqual({ blocked: true, reason: "no", stdout: deny });
      expect(classify(script, {}, { status: 2, signal: null, stdout: "", stderr: "refused\n" }))
        .toEqual({ blocked: true, reason: "refused", stdout: "" });
      expect(classify(script, {}, { status: 0, signal: null, stdout: "", stderr: "" }))
        .toEqual({ blocked: false, stdout: "" });
    }
  });

  test("a broad gate that crashed, was killed, or never started is unavailable, never a block", () => {
    for (const script of BROAD) {
      for (const [label, proc] of crashes) {
        const result = classify(script, {}, proc);
        expect({ label, blocked: result.blocked }).toEqual({ label, blocked: false });
        expect(result.unavailable).toContain(script.slice(0, -3));
        expect(result.reason).toBeUndefined();
      }
    }
    expect(classify("check-domain.py", {}, crashes[0][1]).unavailable).toContain("Traceback: boom");
    expect(classify("check-domain.py", {}, crashes[2][1]).unavailable).toContain("SIGKILL");
    expect(classify("check-domain.py", {}, crashes[3][1]).unavailable).toContain("ENOENT");
  });

  test("a narrow gate that could not run refuses a command it guards and allows any other silently", () => {
    const guarded: Record<string, string> = {
      "gh-close-gate.py": "gh issue close 728 --repo x/y",
      "branch-create-gate.py": "git checkout -b FEAT-9999-runtime-probe",
      "plan-sign-gate.py": "python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file p.yaml",
      // FEAT-2337 (DEC-100): merge-gate.py is a narrow gate.
      "merge-gate.py": "git merge feat/x",
    };
    for (const [script, command] of Object.entries(guarded)) {
      const gate = script.slice(0, -3);
      for (const [label, proc] of crashes) {
        const refused = classify(script, bash(command), proc);
        expect({ label, blocked: refused.blocked }).toEqual({ label, blocked: true });
        expect(refused.reason).toStartWith(`${gate}: BLOCKED — the gate could not run (`);
        expect(refused.reason).toEndWith("); the command it guards is refused rather than left unchecked.");
        expect(refused.unavailable).toBeUndefined();
        for (const unrelated of ["echo hi", "git status"]) {
          expect(classify(script, bash(unrelated), proc)).toEqual({ blocked: false, stdout: proc.stdout ?? "" });
        }
      }
      // A narrow gate that ran keeps its own answer either way.
      expect(classify(script, bash(command), { status: 0, signal: null, stdout: "", stderr: "" }))
        .toEqual({ blocked: false, stdout: "" });
      expect(classify(script, bash("echo hi"), { status: 2, signal: null, stdout: "", stderr: "no" }))
        .toEqual({ blocked: true, reason: "no", stdout: "" });
    }
  });

  test("every other script keeps its non-blocking error contract and still throws a spawn error", () => {
    for (const script of ["inflight_registry.py", "feature-record.py", "digest_destination.py"]) {
      expect(classify(script, {}, crashes[0][1]))
        .toEqual({ blocked: false, reason: "Traceback: boom", stdout: "" });
      expect(classify(script, {}, { status: 3, signal: null, stdout: "", stderr: "" }))
        .toEqual({ blocked: false, reason: `${script} exited 3`, stdout: "" });
      expect(() => classify(script, {}, crashes[3][1])).toThrow("ENOENT");
      // An unavailable line means nothing outside the four broad gates.
      const stdout = JSON.stringify({ decision: "unavailable", gate: "x", reason: "y" });
      expect(classify(script, {}, { status: 0, signal: null, stdout, stderr: "" })).toEqual({ blocked: false, stdout });
    }
  });
});

// FEAT-2274 (C2/C3): the extension's own reading of a narrow gate's protected commands, used
// only when the gate process itself could not run. It mirrors each Python gate's matcher at
// 1e0b014: gh-close-gate `denies`, branch-create-gate `_branch_name`, plan-sign-gate `denies`.
describe("narrowGateApplies", () => {
  const TOOL = "python3 .claude/skills/harness/bin/plan-merge.py";
  const RECORD = "python3 .claude/skills/harness/bin/feature-record.py";
  const SPELLINGS: Record<string, Array<[string, boolean]>> = {
    "gh-close-gate.py": [
      ["gh issue close 728 --repo x/y", true],
      ["cd /tmp && gh issue close 728", true],
      ["FOO=1 gh issue close 728", true],
      ["echo hi | gh issue close 728", true],
      ["true; gh issue close 728", true],
      ['gh "issue" close 5', true],
      ["gh 'issue' 'close' 5", true],
      ["/opt/homebrew/bin/gh issue close 5", true],
      ["/usr/bin/env gh issue close 5", true],
      ["\\gh issue close 5", true],
      ['eval "gh issue close 5"', true],
      ["bash -c 'gh issue close 5'", true],
      ['sh -c "gh issue close 5"', true],
      ["x=$(gh issue close 5)", true],
      ["$(echo gh) issue close 5", true],
      ["gh api -X PATCH repos/o/r/issues/9 -f state=closed", true],
      ["gh api -f state=closed -X PATCH repos/o/r/issues/9", true],
      ["gh api repos/o/r/issues/9 -X PATCH -f state=closed", true],
      ['gh api -X PATCH repos/o/r/issues/5 -f state="closed"', true],
      ["gh api --method PATCH repos/o/r/issues/5 --input -", true],
      ['gh api graphql -f query="mutation{closeIssue(input:{issueId:\\"x\\"}){clientMutationId}}"', true],
      ['gh issue close "5', true],
      ["echo it's here; gh issue close 5", true],
      ["echo 'gh issue close is refused here'", true],
      ["gh issue close 1 && python3 .claude/skills/harness/bin/gh-sync.py ship d", true],
      ["gh pr close 5", false],
      ["echo hi", false],
      ["git status", false],
      ["git branch -d x", false],
      ["gh issue view 728", false],
      ["gh issue list --repo o/r --state closed", false],
      ["python3 .claude/skills/harness/bin/gh-sync.py abandon d --reason-file r --yes", false],
      ["gh api repos/o/r/issues/9", false],
      ["gh issue close-milestone 5", false],
      ["gh api repos/o/r/issues/5 --jq .state", false],
      ["gh api -X GET repos/o/r/issues/5", false],
      ["git commit -m 'closes the loop'", false],
      ["gh issue edit 5 --add-label wontfix", false],
      ["echo it's fine", false],
      ['git commit -m "don\'t close the loop"', false],
      ["cat > /tmp/x.md <<'MD'\nthe module's contract\nMD\ngh issue comment 8 --repo o/r --body-file /tmp/x.md", false],
      ["G=gh; $G issue close 5", false],
    ],
    "branch-create-gate.py": [
      ["git checkout -b FEAT-9999-runtime-probe", true],
      ["git checkout -b feat/FEAT-99-nope", true],
      ["git checkout -B fix/123-typo", true],
      ["git checkout --track origin/x -b feat/x", true],
      ["git -C /repo checkout -b feat/x", true],
      ["git -c core.x=1 switch -c fix/1-y", true],
      ["git switch --create feat/z", true],
      ["git switch -c=feat/z", true],
      ["git worktree add -b feat/w ../w", true],
      ["git worktree add ../w -b feat/w", true],
      ["git branch feat/new", true],
      ["cd /x && git checkout -b feat/y", true],
      ["git status", false],
      ["echo hi", false],
      ["gh pr close 5", false],
      ["git branch -d x", false],
      ["git branch", false],
      ["git branch --list", false],
      ["git checkout main", false],
      ["git switch main", false],
      ["git worktree add ../w main", false],
      ["git checkout -- file-b", false],
    ],
    "plan-sign-gate.py": [
      [`${TOOL} sign-approval --file p.yaml`, true],
      ["/opt/homebrew/bin/python3 /abs/path/to/plan-merge.py sign-approval --file p", true],
      ['eval "python3 plan-merge.py sign-approval --file p.yaml"', true],
      ["bash -c 'python3 plan-merge.py sign-approval --file p.yaml'", true],
      ['python3 "plan-merge.py" sign-approval --file p.yaml', true],
      ["python3 plan-merge.py sign-approval --name \"O'Brien", true],
      [`${TOOL} -- sign-approval --file p.yaml`, true],
      [`echo it's fine; ${TOOL} -- sign-approval --file p.yaml`, true],
      [`${TOOL} \\\nsign-approval --file p.yaml`, true],
      [`echo it's fine; ${TOOL} \\\nsign-approval --file p.yaml`, true],
      [`${TOOL}\${IFS}sign-approval --file p.yaml`, true],
      [`${TOOL}"\${IFS}"sign-approval --file p.yaml`, true],
      [`${TOOL}$(printf " ")sign-approval --file p.yaml`, true],
      [`${TOOL}\`printf ' '\`sign-approval --file p.yaml`, true],
      [`${TOOL}$(echo "$(printf " ")")sign-approval --file p.yaml`, true],
      [`${TOOL} sign-approval --file p.yaml --by Someone --date $(date +%F)`, true],
      [`echo sign-approval | xargs -I{} ${TOOL} {} --file p.yaml`, true],
      [`echo sign-approval | xargs ${TOOL}`, true],
      [`xargs ${TOOL} < /tmp/verb.txt`, true],
      [`find . -name p.yaml -exec ${TOOL} sign-approval --file {} \\;`, true],
      [`${RECORD} raise-cycles --file f.json --to 30 --decision notes/raise.md`, true],
      [`${RECORD} set-rework --file f.json --rounds 4 --minutes 240 --decision plan.yaml`, true],
      [`echo it's fine; ${RECORD} -- raise-cycles --file f.json`, true],
      [`echo raise-cycles | xargs ${RECORD}`, true],
      ["git status", false],
      ["echo hi", false],
      ["gh pr close 5", false],
      ["grep -rn sign-approval .claude/skills/harness/bin/", false],
      [`${TOOL} set-task-station --file p --task T-01 --station build`, false],
      [`${TOOL} apply --file p.yaml --proposal q.yaml  # not a sign-approval call`, false],
      [`${TOOL} apply --file p.yaml \\\n--proposal q.yaml  # not a sign-approval call`, false],
      [`${TOOL}$IFSsign-approval --file p.yaml`, false],
      [`${TOOL} apply --file $(ls p.yaml) --proposal q.yaml  # not a sign-approval call`, false],
      ["echo sign-approval | xargs -I{} grep {} .claude/skills/harness/bin/", false],
      [`${RECORD} run-start --file f.json`, false],
      ["grep -rn raise-cycles .claude/skills/harness/", false],
      [`${RECORD} judgement --file f.json --reason 'no raise-cycles without the operator'`, false],
    ],
  };

  for (const [script, spellings] of Object.entries(SPELLINGS)) {
    test(`${script}: every protected spelling matches and every unrelated command does not`, () => {
      const mismatched = spellings
        .filter(([command, applies]) => hooks.narrowGateApplies(script, command) !== applies)
        .map(([command, applies]) => `${applies ? "missed" : "overmatched"}: ${JSON.stringify(command)}`);
      expect(mismatched).toEqual([]);
    });
  }

  test("a script that is not a narrow gate guards nothing", () => {
    expect(hooks.narrowGateApplies("check-domain.py", "gh issue close 5")).toBe(false);
    expect(hooks.narrowGateApplies("bash-write-guard.py", "git merge x")).toBe(false);
  });

  // FEAT-2337 (DEC-100): merge-gate.py's applicability is a port of its `merge_ref` at 352ceebe,
  // never mainMergeGate's `\bmerge\b` pre-screen, which also matches an abort, a search or an echo.
  const nest = (command: string, layers: number): string =>
    layers ? nest(`bash -c ${JSON.stringify(command)}`, layers - 1) : command;
  const MERGES: Array<[string, boolean]> = [
    ["git merge feat/x", true],
    ["git merge", true],
    ["git merge --squash feat/x", true],
    ["git merge -m 'not --abort' feat/x", true],
    ["git merge -X theirs feat/x", true],
    ["git merge feat/x --abort", true],
    ["git -C /repo merge feat/x", true],
    ["git -c core.pager=cat merge feat/x", true],
    ["git --work-tree /w --git-dir /w/.git merge feat/x", true],
    ["git --no-pager merge feat/x", true],
    ["git --abort merge feat/x", true],
    ["/usr/bin/git merge feat/x", true],
    ["\\git merge feat/x", true],
    ['git "merge" feat/x', true],
    ["cd /x && git merge feat/x", true],
    ["echo git merge feat/x", true],
    ["gh pr merge 12 --squash", true],
    ["gh pr merge --auto", true],
    ["/opt/homebrew/bin/gh pr merge 7", true],
    ["true; gh pr merge 7", true],
    ["bash -c 'git merge feat/x'", true],
    ['sh -c "gh pr merge 12 --squash"', true],
    ['eval "git merge feat/x"', true],
    ["grep -rn 'git merge' docs/", true],
    [nest("git merge feat/x", 3), true],
    ['git merge feat/x "unclosed', true],
    ["git merge --abort", false],
    ["git merge --continue", false],
    ["git merge --quit", false],
    ["git merge -s ours --abort", false],
    ["git -C /repo merge --abort", false],
    ["bash -c 'git merge --abort'", false],
    [nest("git merge feat/x", 4), false],
    ["echo merge", false],
    ['echo "merge', false],
    ["rg merge src/", false],
    ["git status", false],
    ["git log --grep merge", false],
    ["git mergetool", false],
    ["git merge-base main HEAD", false],
    ["git -C merge status", false],
    ["gh pr view 12", false],
    ["gh merge pr 12", false],
    ["gh pr list --search merge", false],
    ["python3 .claude/skills/harness/bin/merge-gate.py merge-distill --root R --feature F --pr 7", false],
  ];
  test("FEAT-2337: merge-gate.py guards merge_ref's merges, not every command that says merge", () => {
    const mismatched = MERGES
      .filter(([command, applies]) => hooks.narrowGateApplies("merge-gate.py", command) !== applies)
      .map(([command, applies]) => `${applies ? "missed" : "overmatched"}: ${JSON.stringify(command)}`);
    expect(mismatched).toEqual([]);
  });
});

// FEAT-1928: the in-process provider adapter over bin/digest-schemas/.
describe("loadDigestSchemaBundle", () => {
  const STRUCTURAL = new Set(["type", "properties", "required", "additionalProperties", "items", "enum", "anyOf"]);
  const TYPES = new Set(["object", "array", "string", "integer", "number", "boolean", "null"]);

  // Every keyword anywhere in a bundle must be structural, `additionalProperties` only ever
  // false, every type one of the seven, and every enum non-empty; a `$ref` is off the whitelist
  // like any other. The OpenAI strict rules the bundle itself must meet ride the same walk:
  // every array declares `items`, and every property, element and anyOf alternative declares
  // a type, an enum or an anyOf (so `items: {}` and `items: true` are violations).
  function offWhitelist(node: unknown, at: string): string[] {
    if (!node || typeof node !== "object" || Array.isArray(node)) return [`${at}: not a schema`];
    const schema = node as Record<string, unknown>;
    const types = schema.type === undefined ? [] : Array.isArray(schema.type) ? schema.type : [schema.type];
    const own = types.includes("array") && !("items" in schema) ? [`${at}: array without items`] : [];
    const typedChild = (child: unknown, where: string): string[] => {
      const shaped = !!child && typeof child === "object" && !Array.isArray(child)
        && ["type", "enum", "anyOf"].some((keyword) => keyword in child);
      return [...(shaped ? [] : [`${where}: untyped`]), ...offWhitelist(child, where)];
    };
    return [...own, ...Object.entries(schema).flatMap(([keyword, value]) => {
      const where = `${at}/${keyword}`;
      if (!STRUCTURAL.has(keyword)) return [where];
      if (keyword === "additionalProperties") return value === false ? [] : [where];
      if (keyword === "type") {
        return (Array.isArray(value) ? value : [value]).every((name) => TYPES.has(name as string)) ? [] : [where];
      }
      if (keyword === "enum") return Array.isArray(value) && value.length ? [] : [where];
      if (keyword === "properties") {
        return Object.entries(value as Record<string, unknown>)
          .flatMap(([name, child]) => typedChild(child, `${where}/${name}`));
      }
      if (keyword === "items") return typedChild(value, where);
      if (keyword === "anyOf") return (value as unknown[]).flatMap((branch, index) => typedChild(branch, `${where}/${index}`));
      return [];
    })];
  }

  function schemaDir(files: Record<string, unknown>): string {
    const dir = mkdtempSync(join(tmpdir(), "feat1928-schemas-"));
    for (const [name, content] of Object.entries(files)) {
      writeFileSync(join(dir, name), typeof content === "string" ? content : JSON.stringify(content));
    }
    return dir;
  }

  const load = (files: Record<string, unknown>) => () => loadDigestSchemaBundle(schemaDir(files), "harness-qa");

  test("loads all 16 personas as ref-free bundles over the structural whitelist only", () => {
    expect(DIGEST_PERSONAS).toHaveLength(16);
    expect(DIGEST_PERSONAS.flatMap((persona) =>
      offWhitelist(loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, persona), persona))).toEqual([]);
    for (const persona of DIGEST_PERSONAS) {
      expect(loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, persona).type).toBe("object");
    }
  });

  test("a repeat load, an alias and another path to the same directory give the same contract", () => {
    const bundle = loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-backend-dev");
    expect(loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "harness-backend-dev")).toEqual(bundle);
    expect(loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, "main-session")).toEqual(bundle);
    expect(loadDigestSchemaBundle(join(DIGEST_SCHEMA_DIR, "..", "digest-schemas"), "backend-dev")).toEqual(bundle);
  });

  // #2328: a long-running process must inject the contract on disk now, not the one it first read.
  test("a schema file changed on disk is reflected by the next load", () => {
    const entry = (required: string[]) => ({ type: "object", additionalProperties: false, required,
      properties: Object.fromEntries(required.map((name) => [name, { type: "string" }])) });
    const persona = { type: "object", additionalProperties: false, required: ["x"],
      properties: { x: { $ref: "common.json#/$defs/entry" } } };
    const projected = (required: string[]) => ({ ...persona, properties: { x: entry(required) } });
    const dir = schemaDir({ "harness-qa.json": persona, "common.json": { $defs: { entry: entry(["op"]) } } });
    expect(loadDigestSchemaBundle(dir, "harness-qa")).toEqual(projected(["op"]));
    writeFileSync(join(dir, "common.json"), JSON.stringify({ $defs: { entry: entry(["op", "persona"]) } }));
    expect(loadDigestSchemaBundle(dir, "harness-qa")).toEqual(projected(["op", "persona"]));
  });

  test("canonicalises personas with digest_schema.py's own table", () => {
    const bin = join(DIGEST_SCHEMA_DIR, "..");
    const proc = spawnSync("python3", ["-c", [
      "import json, sys",
      `sys.path.insert(0, ${JSON.stringify(bin)})`,
      "import digest_schema",
      "print(json.dumps({'personas': list(digest_schema.PERSONAS), 'aliases': digest_schema.ALIASES}))",
    ].join("\n")], { encoding: "utf8" });
    expect(proc.stderr).toBe("");
    expect(JSON.parse(proc.stdout)).toEqual({ personas: [...DIGEST_PERSONAS], aliases: { ...DIGEST_PERSONA_ALIASES } });
    expect(canonicalDigestPersona("qa")).toBe("harness-qa");
    expect(canonicalDigestPersona("lead")).toBe("harness-eng-lead");
    expect(() => canonicalDigestPersona("harness-nobody")).toThrow(DigestSchemaBundleError);
  });

  test("names the file and pointer of malformed JSON, an unresolved or missing reference, and an unsupported keyword", () => {
    expect(load({ "harness-qa.json": "{not json" }))
      .toThrow(/^digest schema harness-qa\.json#: malformed JSON/);
    expect(load({
      "harness-qa.json": { type: "object", properties: { x: { $ref: "common.json#/$defs/missing" } } },
      "common.json": { $defs: {} },
    })).toThrow('digest schema harness-qa.json#/properties/x: unresolved reference "common.json#/$defs/missing"');
    expect(load({ "harness-qa.json": { type: "object", properties: { x: { $ref: "absent.json#/x" } } } }))
      .toThrow(/^digest schema harness-qa\.json#\/properties\/x: cannot read .*absent\.json \(ENOENT\)/);
    expect(load({
      "harness-qa.json": { type: "object", properties: { x: { type: "string", oneOf: [{ type: "string" }] } } },
    })).toThrow('digest schema harness-qa.json#/properties/x/oneOf: unsupported keyword "oneOf"');
    expect(load({ "harness-qa.json": { type: "object", additionalProperties: true } }))
      .toThrow("unsupported additionalProperties true");
    expect(load({ "harness-qa.json": { type: "object", properties: { x: { $ref: "https://example.com/s.json#/a" } } } }))
      .toThrow(/unsupported reference/);
    // OpenAI strict rejects the whole yield tool on one array without items ("array schema
    // missing items", measured live on Codex), so the file is refused before it can ship.
    expect(load({ "harness-qa.json": { type: "object", properties: { x: { type: "array" } } } }))
      .toThrow("digest schema harness-qa.json#/properties/x: array schema without items");
    expect(load({
      "harness-qa.json": { type: "object", properties: { x: { $ref: "common.json#/$defs/list" } } },
      "common.json": { $defs: { list: { type: ["string", "array"] } } },
    })).toThrow("digest schema common.json#/$defs/list: array schema without items");
    expect(load({ "harness-qa.json": { type: "object", properties: { x: { type: "array", items: {} } } } }))
      .toThrow("digest schema harness-qa.json#/properties/x/items: array items admits any value");
    expect(load({ "harness-qa.json": { type: "object", properties: { x: { type: "array", items: true } } } }))
      .toThrow("digest schema harness-qa.json#/properties/x/items: array items must be a typed schema, got true");
    expect(load({ "harness-qa.json": { type: "object", properties: { x: { pattern: "\\S" } } } }))
      .toThrow("digest schema harness-qa.json#/properties/x: a property admits any value");
  });

  test("refuses a reference cycle and a reference that escapes the schema directory", () => {
    expect(load({
      "harness-qa.json": { type: "object", properties: { x: { $ref: "common.json#/$defs/a" } } },
      "common.json": { $defs: { a: { $ref: "#/$defs/b" }, b: { $ref: "#/$defs/a" } } },
    })).toThrow(/reference cycle/);
    const outside = mkdtempSync(join(tmpdir(), "feat1928-outside-"));
    writeFileSync(join(outside, "shared.json"), JSON.stringify({ $defs: { a: { type: "string" } } }));
    const dir = schemaDir({
      "harness-qa.json": { type: "object", properties: { x: { $ref: `../${outside.split("/").pop()}/shared.json#/$defs/a` } } },
    });
    expect(() => loadDigestSchemaBundle(dir, "harness-qa")).toThrow(/escapes the schema directory/);
    const linked = schemaDir({
      "harness-qa.json": { type: "object", properties: { x: { $ref: "common.json#/$defs/a" } } },
    });
    symlinkSync(join(outside, "shared.json"), join(linked, "common.json"));
    expect(() => loadDigestSchemaBundle(linked, "harness-qa")).toThrow(/escapes the schema directory/);
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
    const failed = { kind: "failed" as const, accessor: "sessionManager.getSessionFile" };
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

// Builder-generated valid configs (tests/harness_config_support.build_config, checked in and
// drift-checked by test-harness-config-fixtures.py), so Bun never needs Python or jsonschema.
const BUDGET_CONFIGS = JSON.parse(
  readFileSync(join(import.meta.dir, "..", "fixtures", "harness-config-budgets.json"), "utf8"));

/** `config` minus `drop`: one budgets key, or "budgets" for the whole block. */
function without(config: Record<string, any>, drop?: string) {
  if (drop === "budgets") delete config.budgets;
  else if (drop) delete config.budgets[drop];
  return config;
}

/** A root whose harness.json is the generated `name` config, with `drop` deleted from it. */
function budgetRoot(name: "default" | "context_150000" | "plan_30", drop?: string) {
  const root = mkdtempSync(join(tmpdir(), "budget-cfg-"));
  mkdirSync(join(root, ".harness"));
  writeFileSync(join(root, ".harness", "harness.json"),
    JSON.stringify(without(structuredClone(BUDGET_CONFIGS[name]), drop)));
  return root;
}

describe("resolveContextWarnTokens", () => {
  test("reads the configured budget", () => {
    // 150000 differs from the default, so a mutation back to a hardcoded 200000 reddens.
    expect(resolveContextWarnTokens(budgetRoot("context_150000"))).toBe(150000);
  });

  test("falls back to the declared default when the key is absent", () => {
    expect(resolveContextWarnTokens(budgetRoot("default", "orchestrator_context_warn_tokens")))
      .toBe(DEFAULT_CONTEXT_WARN_TOKENS);
    expect(resolveContextWarnTokens(budgetRoot("default", "budgets"))).toBe(DEFAULT_CONTEXT_WARN_TOKENS);
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
      ...toolApi(),
    };
    const runner = async (_cwd: string, script: string) => {
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
  test("reads the configured value", () => {
    expect(resolvePlanPhaseWarnMinutes(budgetRoot("plan_30"))).toBe(30);
  });

  test("falls back to the declared default when the key is absent", () => {
    expect(resolvePlanPhaseWarnMinutes(budgetRoot("default", "plan_phase_warn_minutes")))
      .toBe(DEFAULT_PLAN_PHASE_WARN_MINUTES);
    expect(resolvePlanPhaseWarnMinutes(budgetRoot("default", "budgets"))).toBe(DEFAULT_PLAN_PHASE_WARN_MINUTES);
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
      ...toolApi(),
    };
    const calls: Array<{ script: string; args: string[] }> = [];
    const runner = async (_cwd: string, script: string, args: string[]) => {
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
// BUG-285: 19/19 task results carried `details.results[i].tokens`,
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
      ...toolApi(),
    };
    const calls: Array<{ script: string; args: string[] }> = [];
    const runner = async (_cwd: string, script: string, args: string[]) => {
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
    // Closing without a host measurement preserves null, with an explicit evidenced count.
    const digest = join(root, ".harness", "harness", "features", FEATURE, "lead.json");
    writeFileSync(digest, JSON.stringify({
      VERDICT: "PASS", DIGEST: { cycles_used: 0 }, artifact: "lead.json",
    }));
    const closed = spawnSync("python3", [gatePath("feature-record.py"), "run-end", "--file", featureJson,
      "--id", "r1", "--verdict", "PASS", "--cycles-used", "0", "--digest", digest], { encoding: "utf8" });
    expect(closed.status).toBe(0);
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
  type Call = { script: string; args: string[]; payload: PolicyPayload };
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
    const runner = async (cwd: string, script: string, args: string[], payload: PolicyPayload) => {
      calls.push({ script, args, payload });
      if (script === "inflight_registry.py") {
        return python([gatePath("inflight_registry.py"), ...args], cwd);
      }
      if (script === "dispatch-guard.py") {
        const input = objectPayload(payload).tool_input as Record<string, unknown>;
        const agent = String(input.agent);
        if (input.task === "passthrough" || !agent.startsWith("harness-")) {
          return { blocked: false, stdout: "" };
        }
        return python(["-c", RECEIPT, root, agent, String(objectPayload(payload).agent_type), FEATURE,
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
      ...toolApi(),
    }, runner as any);
    const emit = async (channel: string, data: unknown) => {
      for (const handler of bus.get(channel) || []) await handler(data);
    };
    return { handlers, emit };
  }

  function ctxFor(root: string, agentId: string, parentAgentId?: string) {
    return ompContext(root, agentId, parentAgentId);
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
  const blockedDigest = { VERDICT: "BLOCKED", DIGEST: { headline: "cannot claim this run" }, artifact: "none" };

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
    expect((await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "t1",
      input: { agent: "harness-backend-dev", name: "Dev", task: ASSIGN },
    }, parent.ctx))?.block).toBeUndefined();
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

  // FEAT-1928: schema refusal and schema loading finish before dispatch-guard.py runs, so a
  // schema-refused dispatch leaves the real registry exactly as it found it.
  test("a schema-refused dispatch records no claim", async () => {
    const w = world();
    const parent = await lead(w);
    for (const input of [
      { agent: "harness-qa", name: "Check", task: ASSIGN, outputSchema: { type: "object" } },
      { context: "shared", tasks: [{ agent: "harness-qa", name: "Check", task: ASSIGN, schemaMode: "permissive" }] },
      { agent: "harness-nobody", name: "Nobody", task: ASSIGN },
    ]) {
      const verdict = await parent.s.handlers.get("tool_call")?.({
        toolName: "task", toolCallId: "refused", input,
      }, parent.ctx);
      expect(verdict?.block).toBe(true);
    }
    expect(w.calls.filter((call) => call.script === "dispatch-guard.py")).toEqual([]);
    expect(governed(w.root)).toEqual([]);
  });

  // #1908: a parked agent is revived cold — OMP builds a NEW session from its session file,
  // so the extension runs in a fresh instance, and the hub's message reaches it through
  // agent.prompt(): agent_start fires, before_agent_start never does. The only record of who
  // the run is lives in the session file's session_init entry (system prompt + assignment).
  function revivedCtx(root: string, id: string, parentId: string, agent: string | null, task: string) {
    const systemPrompt = agent ? `persona\nHARNESS_AGENT_ID: ${agent}` : "plain system prompt";
    const base = ctxFor(root, id, parentId) as Record<string, any>;
    return {
      ...base,
      sessionManager: {
        ...base.sessionManager,
        getEntries: () => [
          { type: "session_init", id: "i", parentId: null, timestamp: "", systemPrompt, task, tools: [] },
          { type: "message", id: "m", parentId: "i", timestamp: "", message: { role: "user", content: task } },
        ],
      },
    };
  }

  test("a cold-revived governed agent recovers its identity and reclaims before writing (#1908)", async () => {
    const w = world();
    const revived = session(w.runner);
    const ctx = revivedCtx(w.root, "Lead.Dev", "Lead", "harness-backend-dev", ASSIGN);
    await revived.handlers.get("agent_start")?.({ type: "agent_start" }, ctx);
    expect(governed(w.root).map((row) => [row.agent, row.agent_id, row.parent_agent_id]))
      .toEqual([["harness-backend-dev", "Lead.Dev", "Lead"]]);
    expect(await revived.handlers.get("tool_call")?.(write(), ctx)).toBeUndefined();
    const dispatched = await revived.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "t-revived",
      input: { agent: "harness-qa", name: "Qa", task: ASSIGN },
    }, ctx) as { reason?: string } | undefined;
    expect(dispatched?.reason ?? "").not.toContain("runtime lineage capability");
  });

  test("a cold-revived governed agent that cannot reclaim is held, never ungoverned (#1908)", async () => {
    const w = world();
    const revived = session(w.runner);
    const ctx = revivedCtx(w.root, "Lead.Dev", "Lead", "harness-backend-dev", "continue");
    await revived.handlers.get("agent_start")?.({ type: "agent_start" }, ctx);
    const held = await revived.handlers.get("tool_call")?.(write(), ctx) as
      { block?: boolean } | undefined;
    expect(held?.block).toBe(true);
  });

  test("a cold-revived ungoverned agent keeps its runtime lineage for task (#1908)", async () => {
    const w = world();
    const revived = session(w.runner);
    const ctx = revivedCtx(w.root, "Main.Scout", "Main", null, "look around");
    await revived.handlers.get("agent_start")?.({ type: "agent_start" }, ctx);
    const dispatched = await revived.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "t-scout", input: { agent: "scout", task: "x" },
    }, ctx) as { reason?: string } | undefined;
    expect(dispatched?.reason ?? "").not.toContain("runtime lineage capability");
    expect(governed(w.root)).toEqual([]);
  });

  test("a markerless revival recovers its feature from its one exact live claim", async () => {
    const w = world();
    seed(w.root, [{ agent: "harness-qa", agent_id: "Lead.Qa", parent_agent_id: "Lead" }]);
    const revived = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Qa", "Lead");
    await begin(revived, ctx, "harness-qa", "continue where you left off");
    expect(await revived.handlers.get("tool_call")?.(write(), ctx)).toBeUndefined();
    await revived.handlers.get("tool_call")?.({
      toolName: "yield", input: { data: PASS_DIGEST },
    }, ctx);
    const validation = w.calls.find((call) => call.script === "validate-digest.py");
    expect(payloadOf(validation)?.harness_feature).toBe(FEATURE);
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
      { toolName: "yield", input: { data: PASS_DIGEST } },
    ]) {
      const verdict = await s.handlers.get("tool_call")?.(call, ctx);
      expect(verdict?.block).toBe(true);
      expect(verdict?.reason).toMatch(cause);
    }
    expect(await s.handlers.get("tool_call")?.({
      toolName: "yield", input: { data: blockedDigest },
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

  test("BUG-2171 a held run refuses a string PASS digest and validates a string BLOCKED one", async () => {
    const w = world();
    mkdirSync(join(w.root, ".harness"), { recursive: true });
    writeFileSync(join(w.root, ".harness", ".inflight-claims.json"), "{not json");
    const s = session(w.runner);
    const ctx = ctxFor(w.root, "Lead.Qa", "Lead");
    await begin(s, ctx, "harness-qa", ASSIGN);
    const pass = await s.handlers.get("tool_call")?.({
      toolName: "yield", input: { data: JSON.stringify(PASS_DIGEST) },
    }, ctx);
    expect(pass?.block).toBe(true);
    expect(pass?.reason).toMatch(/may yield only a BLOCKED digest/);
    expect(w.calls.filter((call) => call.script === "validate-digest.py")).toEqual([]);
    expect(await s.handlers.get("tool_call")?.({
      toolName: "yield", input: { data: JSON.stringify(blockedDigest) },
    }, ctx)).toBeUndefined();
    const validations = w.calls.filter((call) => call.script === "validate-digest.py");
    expect(validations.map((call) => objectPayload(call.payload).digest_object)).toEqual([blockedDigest]);
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
    expect((await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "t1",
      input: { agent: "harness-backend-dev", name: "Dev", task: "passthrough" },
    }, parent.ctx))?.block).toBeUndefined();
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
    expect((await parent.s.handlers.get("tool_call")?.({
      toolName: "task", toolCallId: "batch", input,
    }, parent.ctx))?.block).toBeUndefined();
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

// ---------------------------------------------------------------------------
// FEAT-2225 F3 (validate c1): the host tool driven through the REAL policyRunner — the module's
// own runPolicy, no runner injected — into the real inflight_registry, validate-digest
// --distill-authority and expertise-merge.py member-ops, with every receipt then checked by the
// real verify-receipt. Nothing is canned: the lineage is real claims made by each session's own
// run start plus feature.json distill runs.
//
// ISOLATED COPY: every gate resolves its root from its own location (root_from_script) and the
// marker there, never from cwd. So each temporary checkout carries the marker AND its own copy
// of the harness bin, the `.agents/skills` discovery symlink and the hook extension; the test
// imports that copied module, and its gates then judge the temporary checkout and nothing else.
// The five capability-class representatives each create, add, replace and drop on both tiers.
// ---------------------------------------------------------------------------
describe("FEAT-2225 expertise_apply through the real policyRunner into the real core", () => {
  const FEATURE = "FEAT-9003-host-core";
  const FEATURE_REL = `.harness/harness/features/${FEATURE}`;
  const SOURCE = realpathSync(gateRoot());
  const SQUADS: Record<string, string> = {
    "harness-product-lead": "product", "harness-eng-lead": "engineering", "harness-validator-lead": "validator",
  };
  const DISTILL_RUNS = {
    "harness-product-lead": "distill-product", "harness-eng-lead": "distill-engineering",
    "harness-validator-lead": "distill-validator",
  };
  type Register = typeof registerHarnessHooks;
  type Tree = { root: string; register: Register };
  type Session = { tools: Map<string, any>; ctx: Record<string, unknown>; persona: string; id: string; parent: string };

  const op = (verb: string, section: string, target: string, entry?: string) =>
    ({ op: verb, target, section, why: "seen in two runs", ...(entry ? { entry } : {}) });
  const ADDS = [op("add", "Patterns", "P-01", "WHEN x DO y"), op("add", "Gotchas", "G-01", "WHEN w DO watch")];
  const CHANGES = [op("replace", "Patterns", "P-01", "WHEN x DO z"), op("drop", "Gotchas", "G-01")];

  // The gate tree a checkout needs to be its own root: the bin, its discovery symlink and the
  // extension, copied from this checkout; returns the copied module's registerHarnessHooks.
  async function isolate(root: string): Promise<Register> {
    cpSync(join(SOURCE, ".claude/skills/harness/bin"), join(root, ".claude/skills/harness/bin"), { recursive: true });
    mkdirSync(join(root, ".agents"), { recursive: true });
    symlinkSync("../.claude/skills", join(root, ".agents/skills"));
    for (const name of ["harness-hooks.ts", "digest-schema.ts"]) {
      cpSync(join(SOURCE, ".omp/extensions", name), join(root, ".omp/extensions", name));
    }
    // Runtime-selected: the module under test is the copy inside this temporary checkout.
    return (await import(join(root, ".omp/extensions/harness-hooks.ts"))).registerHarnessHooks;
  }

  // A committed feature checkout: the root marker with each lead's run grant, one open
  // registered run per lead named by `runs`, the craft and harness tiers, and no Expertise yet.
  async function tree(runs: Record<string, string>): Promise<Tree> {
    const root = realpathSync(mkdtempSync(join(tmpdir(), "f2225-host-core-")));
    const put = (rel: string, body: string) => {
      mkdirSync(join(root, rel, ".."), { recursive: true });
      writeFileSync(join(root, rel), body);
    };
    // JSON is YAML: the manifest needs no YAML writer here.
    put(".harness/team-config.yaml", JSON.stringify({
      leads: Object.entries(SQUADS).map(([name, squad]) => ({
        name, squad, domain: [{ path: `.harness/*/features/*/runs/*-${squad}/**`, upsert: true }, { path: ".", read: true }],
      })),
    }));
    put(`${FEATURE_REL}/feature.json`, JSON.stringify({
      feature_id: FEATURE,
      runs: Object.entries(runs).map(([agent, id]) => ({
        id, squad: SQUADS[agent], agent, verdict: "PENDING", started_at: "2026-11-21T00:00:00+00:00",
      })),
    }));
    put(`${FEATURE_REL}/notes/README`, "notes\n");
    put(".harness/expertise/README", "craft tier\n");
    put(".harness/harness/expertise/README", "repository tier\n");
    put(".gitignore", "*.lock\n.harness/.inflight-claims.json\n.claude/\n.agents/\n.omp/\n");
    const register = await isolate(root);
    const git = (...args: string[]) => spawnSync("git", ["-c", "user.name=t", "-c", "user.email=t@t",
      "-c", "commit.gpgsign=false", ...args], { cwd: root, encoding: "utf8", timeout: 30_000 });
    git("init", "-q", "-b", "main");
    git("add", "-A");
    git("commit", "-q", "-m", "base");
    return { root, register };
  }

  // One governed session over the copied real hooks: its own run start makes its real claim.
  async function session(t: Tree, persona: string, id: string, parent: string): Promise<Session> {
    const tools = new Map<string, any>();
    const handlers = new Map<string, Function>();
    t.register({
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: { on: () => () => {} },
      ...toolApi(tools),
    });
    const ctx = ompContext(t.root, id, parent);
    const assignment = `HARNESS-FEATURE: ${FEATURE}\nHARNESS-MISSION: distill\ndistill your lessons`;
    const started = await handlers.get("before_agent_start")?.({
      prompt: assignment, systemPrompt: [`HARNESS_AGENT_ID: ${persona}`],
    }, ctx);
    expect([persona, started?.message?.customType]).not.toEqual([persona, "harness-run-refused"]);
    await handlers.get("message_end")?.({ message: { role: "user", content: [{ type: "text", text: assignment }] } }, ctx);
    return { tools, ctx, persona, id, parent };
  }

  const apply = (s: Session, call: string, params: Record<string, unknown>) =>
    s.tools.get("expertise_apply").execute(call, params, undefined, undefined, s.ctx);

  function verify(root: string, s: Session, persona: string, repository?: string) {
    const claimed = [...ADDS, ...CHANGES].map((item) => ({ ...item, persona }));
    return spawnSync("python3", [join(root, ".agents/skills/harness/bin/expertise-merge.py"), "verify-receipt",
      "--root", root, "--feature", FEATURE,
      "--persona", persona, "--runtime-id", s.id, "--parent-id", s.parent,
      "--tier", repository ? "repository" : "craft", ...(repository ? ["--repository", repository] : []),
      "--claimed", "-"], { input: JSON.stringify(claimed), encoding: "utf8", timeout: 30_000 });
  }

  const receiptPath = (root: string, id: string) =>
    join(root, FEATURE_REL, "notes", `expertise-receipt-${createHash("sha256").update(id).digest("hex")}.json`);

  let main: Tree;
  let root = "";
  const sessions = new Map<string, Session>();
  beforeAll(async () => {
    main = await tree(DISTILL_RUNS);
    root = main.root;
    // Parents first: a member's authority is its dispatching lead's LIVE registered distill run.
    const lineage: Array<[string, string, string]> = [
      ["harness-orchestrator", "Orch", "Main"],
      ["harness-product-lead", "Orch.Product", "Orch"],
      ["harness-eng-lead", "Orch.Eng", "Orch"],
      ["harness-validator-lead", "Orch.Val", "Orch"],
      ["harness-backend-dev", "Orch.Eng.Dev", "Orch.Eng"],
      ["harness-dev-ops", "Orch.Eng.Ops", "Orch.Eng"],
      ["harness-code-reviewer", "Orch.Val.Code", "Orch.Val"],
    ];
    for (const [persona, id, parent] of lineage) sessions.set(persona, await session(main, persona, id, parent));
  }, 60_000);

  const REPRESENTATIVES = [
    "harness-product-lead", "harness-code-reviewer", "harness-dev-ops", "harness-orchestrator", "harness-backend-dev",
  ];
  for (const persona of REPRESENTATIVES) {
    test(`${persona}: creates, adds, replaces and drops on craft and repository; each receipt verifies`, async () => {
      const s = sessions.get(persona)!;
      for (const [tier, repository, rel] of [
        ["craft", undefined, `.harness/expertise/${persona}.md`],
        ["repository", "harness", `.harness/harness/expertise/${persona}.md`],
      ] as Array<[string, string | undefined, string]>) {
        const params = (ops: unknown[]) => ({ tier, ...(repository ? { repository } : {}), ops });
        const first = await apply(s, `${s.id}-${tier}-1`, params(ADDS));
        const second = await apply(s, `${s.id}-${tier}-2`, params(CHANGES));
        expect(JSON.parse(first.content[0].text)).toEqual(first.details);
        expect([tier, first.details.destination, first.details.counts.before, first.details.counts.after]).toEqual(
          [tier, rel, { Gotchas: 0, Open: 0, Outcomes: 0, Patterns: 0 }, { Gotchas: 1, Open: 0, Outcomes: 0, Patterns: 1 }]);
        expect([tier, second.details.counts.after]).toEqual([tier, { Gotchas: 0, Open: 0, Outcomes: 0, Patterns: 1 }]);
        const written = readFileSync(join(root, rel), "utf8");
        expect([tier, written.includes("WHEN x DO z"), written.includes("WHEN x DO y"), written.includes("WHEN w DO watch")])
          .toEqual([tier, true, false, false]);
        const verified = verify(root, s, persona, repository);
        expect([tier, verified.status, verified.stdout + verified.stderr]).toEqual([tier, 0, expect.any(String)]);
      }
      expect(existsSync(receiptPath(root, s.id))).toBe(true);
    }, 60_000);
  }

  test("a receipt does not vouch for another persona", () => {
    const forged = verify(root, sessions.get("harness-backend-dev")!, "harness-qa");
    expect(forged.status).not.toBe(0);
  }, 30_000);

  // F1 on real lineage: the distill marker rides the dispatch, but the eng-lead's registered
  // run is an ordinary build run, so neither the lead nor its member may apply.
  test("F1: a distill marker under a non-distill registered run applies nothing", async () => {
    const build = await tree({ "harness-eng-lead": "build-engineering" });
    await session(build, "harness-orchestrator", "Orch", "Main");
    const lead = await session(build, "harness-eng-lead", "Orch.Eng", "Orch");
    const member = await session(build, "harness-backend-dev", "Orch.Eng.Dev", "Orch.Eng");
    for (const s of [lead, member]) {
      const error = await apply(s, `${s.id}-refused`, { tier: "craft", ops: ADDS }).then(() => undefined, (e: Error) => e.message);
      expect([s.persona, error]).toEqual([s.persona, expect.stringContaining("expertise_apply refused: distill-authority: REFUSED")]);
      expect([s.persona, existsSync(join(build.root, `.harness/expertise/${s.persona}.md`))]).toEqual([s.persona, false]);
      expect([s.persona, existsSync(receiptPath(build.root, s.id))]).toEqual([s.persona, false]);
    }
  }, 60_000);
});

// FEAT-2337 (D-01, DEC-100): every Python policy call is awaited and bounded, and a Bash call's five
// gates run at once. Real-process cases import a COPY of the extension whose gate tree holds only
// planted scripts; a shortened budget is written into that copy's source, never passed as an option.
describe("FEAT-2337 async bounded policy runtime", () => {
  type Answer = { blocked: boolean; reason?: string; unavailable?: string; stdout: string };
  // A planned answer, `after` microtask turns late: completion order without a wall clock.
  type Gate = { answer?: Answer; sequence?: Answer[]; reject?: string; after: number };
  type Outcome = Partial<Answer> & { threw?: string };
  const EXTENSIONS = join(import.meta.dir, "..", "..", ".omp", "extensions");
  const BASH_GATES = ["gh-close-gate.py", "branch-create-gate.py", "bash-write-guard.py", "plan-sign-gate.py", "merge-gate.py"];
  const PASS: Answer = { blocked: false, stdout: "" };
  const STARTED: Answer = { blocked: false, stdout: '{"ok": true}\n' };
  const EXPERTISE: Answer = {
    blocked: false, stdout: JSON.stringify({ hookSpecificOutput: { additionalContext: "injected expertise" } }),
  };
  const python = (...lines: string[]) => ["#!/usr/bin/env python3", ...lines, ""].join("\n");
  const notice = (gate: string, why: string) => `Harness: ${gate} (pre) could not run; nothing was checked. ${why}`;
  const failed = (gate: string) => `Harness: ${gate} (pre) failed before answering, so the call is refused: transport down`;
  const refuse = (reason: string): Answer => ({ blocked: true, reason, stdout: "" });
  const unavailable = (why: string): Answer => ({ blocked: false, unavailable: why, stdout: "" });
  const ASSIGNMENT = {
    prompt: "HARNESS-FEATURE: FEAT-90-long-run\nassignment",
    systemPrompt: ["HARNESS_AGENT_ID: harness-backend-dev"],
  };
  const TASK = (task: string) => ({ agent: "harness-qa", task: `HARNESS-FEATURE: FEAT-90-long-run\n${task}` });
  const RECEIPT: Answer = {
    blocked: false,
    stdout: JSON.stringify({ harness_claim: { root: "/repo", feature: "FEAT-90-long-run", agent: "harness-qa", claim_id: "c1" } }),
  };

  async function copiedRuntime(scripts: Record<string, string>, timeoutMs?: number) {
    const root = realpathSync(mkdtempSync(join(tmpdir(), "feat2337-")));
    const extensions = join(root, ".omp", "extensions");
    cpSync(EXTENSIONS, extensions, { recursive: true });
    const source = join(extensions, "harness-hooks.ts");
    const original = readFileSync(source, "utf8");
    const clocked = timeoutMs === undefined ? original
      : original.replace(/^export const POLICY_TIMEOUT_MS = [0-9_]+;$/m, `export const POLICY_TIMEOUT_MS = ${timeoutMs};`);
    expect(timeoutMs === undefined || clocked !== original).toBe(true);
    writeFileSync(source, clocked);
    const bin = join(root, ".agents", "skills", "harness", "bin");
    mkdirSync(bin, { recursive: true });
    for (const [name, body] of Object.entries(scripts)) writeFileSync(join(bin, name), body, { mode: 0o755 });
    // Dynamic by necessity: the module under test is the per-case copy, chosen at run time.
    return { root, bin, hooks: await import(source) };
  }

  // A process that ignores graceful termination and leaves a grandchild holding its pipes.
  const HANG = python(
    "import os, signal, subprocess, sys, time",
    "signal.signal(signal.SIGTERM, signal.SIG_IGN)",
    "kid = subprocess.Popen(['sleep', '8'])",
    "open(os.path.abspath(__file__) + '.pids', 'w').write(f'{os.getpid()} {kid.pid}')",
    "print('partial', flush=True)",
    "time.sleep(8)",
  );

  const alive = (pid: number) => {
    try { process.kill(pid, 0); return true; } catch { return false; }
  };
  // Real processes die on the OS's schedule, not a fake clock: poll briefly for the kill to land.
  async function survivors(pidFile: string) {
    const pids = readFileSync(pidFile, "utf8").trim().split(" ").map(Number);
    for (let wait = 0; wait < 50 && pids.some(alive); wait += 1) await Bun.sleep(20);
    return pids.filter(alive);
  }

  test("FEAT-2337: one named 30-second budget, and no synchronous Python policy spawn", () => {
    const source = readFileSync(join(EXTENSIONS, "harness-hooks.ts"), "utf8");
    expect(hooks.POLICY_TIMEOUT_MS).toBe(30_000);
    expect(source.match(/POLICY_TIMEOUT_MS = /g)).toHaveLength(1);
    expect(source.match(/spawnSync\("[^"]*"/g) ?? []).toEqual(['spawnSync("git"']);
  });

  // The heartbeat is a real interval on purpose: what is under test is that the real event loop
  // keeps turning while a real child runs, which no fake clock can witness.
  test("FEAT-2337: the event loop keeps running while a policy child is pending", async () => {
    const { root, hooks: copy } = await copiedRuntime({
      "check-domain.py": python("import sys, time", "sys.stdin.read()", "time.sleep(0.5)"),
    });
    let ticks = 0;
    const beat = setInterval(() => { ticks += 1; }, 5);
    const pending = copy.runPolicy(root, "check-domain.py", [], {});
    const ticksAtReturn = ticks;
    const result = await pending;
    clearInterval(beat);
    expect([ticksAtReturn, ticks >= 20, result]).toEqual([0, true, { blocked: false, stdout: "" }]);
  }, 10_000);

  // Each row: label, script, Bash command, and the DEC-100 outcome a timed-out process must take.
  const TIMEOUTS: Array<[string, string, string, (result: Answer) => boolean]> = [
    ["a broad gate is visibly unavailable", "bash-write-guard.py", "echo hi",
      (result) => !result.blocked && /budget/.test(result.unavailable ?? "")],
    ["a matching narrow command is refused", "gh-close-gate.py", "gh issue close 7 --repo x/y",
      (result) => result.blocked && /budget/.test(result.reason ?? "")],
    ["an unrelated narrow command is allowed silently", "gh-close-gate.py", "git status",
      (result) => !result.blocked && result.unavailable === undefined && result.reason === undefined],
    // merge-gate.py is a narrow gate: its timeout refuses only the merge it guards.
    ["a guarded merge is refused", "merge-gate.py", "git merge feat/x",
      (result) => result.blocked && /^merge-gate: BLOCKED/.test(result.reason ?? "") && /budget/.test(result.reason ?? "")],
    ["unrelated Bash is allowed silently past merge-gate", "merge-gate.py", "echo merge",
      (result) => !result.blocked && result.unavailable === undefined && result.reason === undefined],
    ["a helper keeps its non-blocking reason", "inflight_registry.py", "",
      (result) => !result.blocked && /budget/.test(result.reason ?? "")],
  ];
  test.each(TIMEOUTS)("FEAT-2337: past the budget %s, killed with no survivor", async (_label, script, command, holds) => {
    const { root, bin, hooks: copy } = await copiedRuntime({ [script]: HANG }, 400);
    const started = performance.now();
    const result = await copy.runPolicy(root, script, [], { tool_input: { command } });
    const elapsed = performance.now() - started;
    expect([holds(result), elapsed < 3_000, await survivors(join(bin, `${script}.pids`))])
      .toEqual([true, true, []]);
  }, 15_000);

  // A fixture-local clock: every timer the runner arms with the copy's budget must be cleared by
  // the one settlement, whichever of error, exit, close or the deadline arrives first.
  async function armedBudgets(budget: number, run: () => Promise<Outcome>) {
    const realSet = globalThis.setTimeout;
    const realClear = globalThis.clearTimeout;
    const armed: unknown[] = [];
    const cleared = new Set<unknown>();
    globalThis.setTimeout = ((handler: () => void, ms?: number, ...rest: unknown[]) => {
      const id = realSet(handler, ms, ...rest);
      if (ms === budget) armed.push(id);
      return id;
    }) as typeof setTimeout;
    globalThis.clearTimeout = ((id: Parameters<typeof clearTimeout>[0]) => {
      cleared.add(id);
      realClear(id);
    }) as typeof clearTimeout;
    try {
      const outcome = await run().then((value) => value, (error: Error): Outcome => ({ threw: error.message }));
      return { outcome, armed: armed.length, uncleared: armed.filter((id) => !cleared.has(id)).length };
    } finally {
      globalThis.setTimeout = realSet;
      globalThis.clearTimeout = realClear;
    }
  }

  const SETTLEMENTS: Array<[string, Record<string, string>, string, (outcome: Outcome) => boolean]> = [
    ["a clean exit", { "check-domain.py": python("print('{}')") }, "check-domain.py",
      (outcome) => outcome.blocked === false && outcome.unavailable === undefined],
    ["a spawn error followed by close", {}, "check-domain.py",
      (outcome) => /could not be started/.test(outcome.unavailable ?? "")],
    ["a death by signal", { "check-domain.py": python("import os, signal", "os.kill(os.getpid(), signal.SIGKILL)") },
      "check-domain.py", (outcome) => /terminated by SIGKILL/.test(outcome.unavailable ?? "")],
    ["a deadline before close", { "check-domain.py": HANG }, "check-domain.py",
      (outcome) => /budget/.test(outcome.unavailable ?? "")],
    ["a helper spawn error", {}, "feature-record.py", (outcome) => typeof outcome.threw === "string"],
  ];
  test.each(SETTLEMENTS)("FEAT-2337: %s settles once and clears its timer", async (_label, scripts, script, holds) => {
    const budget = 600;
    const { root, hooks: copy } = await copiedRuntime(scripts, budget);
    const seen = await armedBudgets(budget, () => copy.runPolicy(root, script, [], {}));
    expect([holds(seen.outcome), seen.armed, seen.uncleared]).toEqual([true, 1, 0]);
  }, 15_000);

  // An injected-runner session. Gate scripts answer through `gates`; registry steps (by verb) and
  // other helpers through `helpers`, defaulting to an immediate pass. `events` records each call's
  // start and end, so a test can read what happened before the hook answered.
  function host(gates: Record<string, Gate>, helpers: Record<string, Gate> = {}) {
    const events: string[] = [];
    const handlers = new Map<string, Function>();
    const lifecycle: Function[] = [];
    const answer = async (name: string, plan: Gate | undefined, fallback: Answer) => {
      events.push(`start ${name}`);
      for (let turn = 0; turn < (plan?.after ?? 0); turn += 1) await Promise.resolve();
      events.push(`end ${name}`);
      if (plan?.reject) throw new Error(plan.reject);
      return plan?.sequence?.shift() ?? plan?.answer ?? fallback;
    };
    const runner = (_cwd: string, script: string, args: string[]) => {
      const name = script === "inflight_registry.py" ? args[0] : script;
      if (BASH_GATES.includes(script)) return answer(name, gates[script], PASS);
      return answer(name, helpers[name], name === "run-start" ? STARTED : PASS);
    };
    registerHarnessHooks({
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: { on(_channel: string, handler: Function) { lifecycle.push(handler); return () => {}; } },
      ...toolApi(),
    }, runner);
    const ctx = ompContext("/repo", "Lead.Dev", "Lead");
    const begin = () => handlers.get("before_agent_start")?.(ASSIGNMENT, ctx);
    const call = (toolName: string, input: Record<string, unknown>) =>
      handlers.get("tool_call")?.({ toolName, toolCallId: `call-${toolName}`, input }, ctx);
    const settle = (data: Record<string, unknown>) => Promise.all(lifecycle.map((handler) => handler(data)));
    return { events, begin, call, settle };
  }

  // Later declared gates finish first, so completion order is the reverse of declared order.
  const reversed = (answers: Record<string, Answer | string>) => Object.fromEntries(BASH_GATES.map((script, index) => {
    const given = answers[script];
    const after = (BASH_GATES.length - index) * 15;
    return [script, typeof given === "string" ? { reject: given, after } : { answer: given, after }];
  }));
  const ENV = { command: "ls -la", env: { HARNESS_AGENT_TYPE: "harness-backend-dev" } };

  const COMPOSITIONS: Array<[string, Record<string, Answer | string>, unknown]> = [
    ["the first declared refusal wins whatever finishes first",
      { "gh-close-gate.py": refuse("gh-close refused"), "plan-sign-gate.py": refuse("plan-sign refused") },
      { block: true, reason: "gh-close refused" }],
    ["every unavailable notice rides beside the refusal, in declared order",
      { "branch-create-gate.py": unavailable("bcg broke"), "bash-write-guard.py": unavailable("bwg broke"),
        "merge-gate.py": refuse("merge refused") },
      { block: true, reason: ["merge refused", notice("branch-create-gate", "bcg broke"),
        notice("bash-write-guard", "bwg broke")].join("\n") }],
    ["unavailable notices without a refusal stay passive context",
      { "branch-create-gate.py": unavailable("bcg broke"), "bash-write-guard.py": unavailable("bwg broke") },
      { input: ENV, additionalContext: [notice("branch-create-gate", "bcg broke"),
        notice("bash-write-guard", "bwg broke")].join("\n") }],
    ["a rejected gate hides neither the refusal nor a sibling's notice",
      { "gh-close-gate.py": refuse("gh-close refused"), "bash-write-guard.py": unavailable("bwg broke"),
        "plan-sign-gate.py": "transport down" },
      { block: true, reason: ["gh-close refused", failed("plan-sign-gate"), notice("bash-write-guard", "bwg broke")].join("\n") }],
    ["a rejection alone still refuses and keeps the notices",
      { "bash-write-guard.py": unavailable("bwg broke"), "merge-gate.py": "transport down" },
      { block: true, reason: [failed("merge-gate"), notice("bash-write-guard", "bwg broke")].join("\n") }],
    ["an unrelated command still runs every gate", {}, { input: ENV }],
  ];
  test.each(COMPOSITIONS)("FEAT-2337: Bash gates, %s", async (_label, answers, expected) => {
    const session = host(reversed(answers));
    await session.begin();
    const result = await session.call("bash", { command: "ls -la" });
    const gateEvents = session.events.filter((event) => BASH_GATES.some((gate) => event.endsWith(gate)));
    expect(result).toEqual(expected);
    expect(gateEvents).toEqual([
      ...BASH_GATES.map((gate) => `start ${gate}`),
      ...BASH_GATES.map((gate) => `end ${gate}`).reverse(),
    ]);
  });

  // Real processes: each planted gate waits (at most 2 s) until all five have started.
  const BARRIER = python(
    "import os, sys, time",
    "sys.stdin.read()",
    "here = os.path.dirname(os.path.abspath(__file__))",
    "open(os.path.abspath(__file__) + '.started', 'w').close()",
    `gates = ${JSON.stringify(BASH_GATES)}`,
    "until = time.monotonic() + 2",
    "seen = lambda: all(os.path.exists(os.path.join(here, g + '.started')) for g in gates)",
    "while not seen() and time.monotonic() < until: time.sleep(0.01)",
    "open(os.path.abspath(__file__) + '.met', 'w').write('met' if seen() else 'alone')",
  );
  test("FEAT-2337: all five real gate processes start before any is allowed to finish", async () => {
    const { root, bin, hooks: copy } = await copiedRuntime({
      ...Object.fromEntries(BASH_GATES.map((gate) => [gate, BARRIER])),
      "inflight_registry.py": python("print('{\"ok\": true}')"),
      "inject-expertise.py": python("pass"),
    });
    const handlers = new Map<string, Function>();
    copy.registerHarnessHooks({
      on(name: string, handler: Function) { handlers.set(name, handler); },
      events: { on: () => () => {} },
      ...toolApi(),
    });
    const ctx = ompContext(root, "Lead.Dev", "Lead");
    await handlers.get("before_agent_start")?.(ASSIGNMENT, ctx);
    const result = await handlers.get("tool_call")?.({ toolName: "bash", toolCallId: "b", input: { command: "ls -la" } }, ctx);
    expect(result?.block).toBeUndefined();
    expect(BASH_GATES.map((gate) => readFileSync(join(bin, `${gate}.met`), "utf8"))).toEqual(BASH_GATES.map(() => "met"));
  }, 20_000);

  // A helper that answers late must not be read before it answers: each row delays one helper,
  // and expertise injection is late in every row.
  const DELAYED: Array<[string, Record<string, Gate>, (session: ReturnType<typeof host>) => Promise<unknown>, unknown]> = [
    ["an authorization refusal is not an early allow", { authorize: { answer: refuse("lineage refused"), after: 20 } },
      async (session) => { await session.begin(); return session.call("write", { path: "/repo/src/x.ts", content: "x" }); },
      { block: true, reason: "lineage refused" }],
    ["a yield refusal is not an early pass", { "validate-digest.py": { answer: refuse("children live"), after: 20 } },
      async (session) => { await session.begin(); return session.call("yield", { data: PASS_DIGEST }); },
      { block: true, reason: "children live" }],
    ["an expertise answer is still injected", {},
      async (session) => (await session.begin())?.message?.content,
      "injected expertise"],
  ];
  test.each(DELAYED)("FEAT-2337: delayed helper, %s", async (_label, helpers, act, expected) => {
    const session = host({}, { ...helpers, "inject-expertise.py": { answer: EXPERTISE, after: 20 } });
    expect(await act(session)).toEqual(expected);
  });

  test("FEAT-2337: a run is held until its delayed run-start answers, then ready", async () => {
    const session = host({}, { "run-start": { answer: STARTED, after: 30 } });
    const opening = session.begin();
    const early = await session.call("write", { path: "/repo/src/x.ts", content: "x" });
    await opening;
    const late = await session.call("write", { path: "/repo/src/x.ts", content: "x" });
    expect([early?.block, String(early?.reason).includes("has not completed"), late]).toEqual([true, true, undefined]);
    expect(session.events.indexOf("end run-start")).toBeLessThan(session.events.indexOf("start reconcile"));
  });

  test("FEAT-2337: a refused batch answers only after its earlier claim is released", async () => {
    const session = host({}, {
      "dispatch-guard.py": { sequence: [RECEIPT, refuse("second refused")], after: 5 },
      release: { answer: PASS, after: 20 },
    });
    await session.begin();
    const answered = await session.call("task", { tasks: [TASK("a"), TASK("b")] });
    session.events.push("answered");
    expect(answered).toEqual({ block: true, reason: "second refused" });
    expect(session.events.slice(-3)).toEqual(["start release", "end release", "answered"]);
  });

  test("FEAT-2337: a lifecycle settlement resolves only after release-run and the call's receipt release", async () => {
    const session = host({}, {
      "dispatch-guard.py": { answer: RECEIPT, after: 5 },
      "release-run": { answer: PASS, after: 20 },
      release: { answer: PASS, after: 20 },
    });
    await session.begin();
    expect((await session.call("task", TASK("a")))?.block).toBeUndefined();
    await session.settle({ id: "Lead.Dev.Qa", status: "completed", parentToolCallId: "call-task" });
    session.events.push("settled");
    expect(session.events.slice(-5)).toEqual(["start release-run", "end release-run", "start release", "end release", "settled"]);
  });
});
