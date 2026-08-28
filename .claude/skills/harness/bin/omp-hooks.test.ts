import { describe, expect, test } from "bun:test";
import { existsSync } from "node:fs";
import { tmpdir } from "node:os";
import {
  detectHarnessAgent,
  gatePath,
  extractEditPaths,
  normalizeYieldInput,
  normalizeTaskDispatches,
  registerHarnessHooks,
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
});
