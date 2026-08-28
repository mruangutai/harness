import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const AGENT_MARKER = /^HARNESS_AGENT_ID: (harness-[a-z0-9-]+)$/gm;
const FEATURE_MARKER = /^HARNESS-FEATURE: ((?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+)$/gm;
const BIN = ".agents/skills/harness/bin";

// THE GATE DIRECTORY IS DERIVED FROM THIS FILE, NOT FROM ANY CALLER (FEAT-42, panel B-1).
// This module ships at <root>/.omp/extensions/harness-hooks.ts, so <root> is two levels up.
// What stood here was `join(cwd, BIN, script)` against a caller-supplied ctx.cwd: the
// executable that enforces a policy was CHOSEN by the party the policy governs. Issue #556,
// which this feature closes, was the same defect one level down — a harness_boundary.py in
// an agent's working directory became the module a gate imported, taking check-domain.sh
// from `exit 2 BLOCKED` to `exit 0 enforcement OFF`. That substituted an imported module.
// This substituted the whole gate, across six gates and eleven call sites.
//
// `cwd` is still passed to the child, deliberately — a gate must judge the tree the agent is
// working in. What must not come from the caller is WHICH BINARY judges it.
export function gateRoot(): string {
  return join(fileURLToPath(new URL(".", import.meta.url)), "..", "..");
}

// Exported so the executable path can be asserted without spawning anything. runPolicy is
// not exported and had no coverage at all, which is how B-1 survived four review passes.
export function gatePath(script: string): string {
  return join(gateRoot(), BIN, script);
}

type Dict = Record<string, unknown>;
type PolicyResult = { blocked: boolean; reason?: string; stdout: string };
type PolicyRunner = (
  cwd: string,
  script: string,
  args: string[],
  payload: Dict,
) => PolicyResult;

function debug(message: string): void {
  if (process.env.HARNESS_HOOK_DEBUG === "1") console.error(`[harness-hooks] ${message}`);
}

export function detectHarnessAgent(systemPrompt: unknown): string | undefined {
  if (!Array.isArray(systemPrompt)) return undefined;
  const names = new Set<string>();
  for (const layer of systemPrompt) {
    if (typeof layer !== "string") continue;
    for (const match of layer.matchAll(AGENT_MARKER)) names.add(match[1]);
  }
  if (names.size > 1) {
    throw new Error(`conflicting Harness agent markers: ${[...names].sort().join(", ")}`);
  }
  return names.values().next().value;
}

export function detectHarnessFeature(systemPrompt: unknown): string | undefined {
  if (!Array.isArray(systemPrompt)) return undefined;
  const features = new Set<string>();
  for (const layer of systemPrompt) {
    if (typeof layer !== "string") continue;
    for (const match of layer.matchAll(FEATURE_MARKER)) features.add(match[1]);
  }
  if (features.size > 1) {
    throw new Error(`conflicting Harness feature markers: ${[...features].sort().join(", ")}`);
  }
  return features.values().next().value;
}

export function extractEditPaths(input: unknown): string[] {
  if (typeof input !== "string") return [];
  const paths: string[] = [];
  const seen = new Set<string>();
  const add = (raw: string): void => {
    const path = raw.trim().replace(/^"(.*)"$/, "$1");
    if (path && !seen.has(path)) {
      seen.add(path);
      paths.push(path);
    }
  };
  for (const match of input.matchAll(/^\[([^#\r\n]+)#[0-9A-F]{4}\]$/gm)) add(match[1]);
  for (const match of input.matchAll(/^MV (.+)$/gm)) add(match[1]);
  return paths;
}

function text(value: unknown): string {
  if (typeof value === "string") return value;
  if (value === undefined) return "";
  return JSON.stringify(value);
}

function yamlScalar(value: unknown): string {
  if (value === null) return "null";
  if (typeof value === "boolean" || typeof value === "number") return String(value);
  const valueText = text(value);
  return /^[A-Za-z0-9_.\/ -]+$/.test(valueText) && !/^(true|false|null)$/i.test(valueText)
    ? valueText
    : JSON.stringify(valueText);
}

function yamlLines(value: Dict, indent = 0): string[] {
  const pad = " ".repeat(indent);
  const lines: string[] = [];
  for (const [key, item] of Object.entries(value)) {
    if (Array.isArray(item)) {
      if (item.length === 0) {
        lines.push(`${pad}${key}: []`);
      } else if (item.every((entry) => entry === null || typeof entry !== "object")) {
        lines.push(`${pad}${key}: [${item.map(yamlScalar).join(", ")}]`);
      } else {
        lines.push(`${pad}${key}:`);
        for (const entry of item) {
          if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
            lines.push(`${pad}  - ${yamlScalar(entry)}`);
            continue;
          }
          const nested = yamlLines(entry as Dict, indent + 4);
          if (nested.length === 0) {
            lines.push(`${pad}  - {}`);
          } else {
            lines.push(`${pad}  - ${nested[0].trimStart()}`);
            lines.push(...nested.slice(1));
          }
        }
      }
    } else if (item && typeof item === "object") {
      lines.push(`${pad}${key}:`);
      lines.push(...yamlLines(item as Dict, indent + 2));
    } else {
      lines.push(`${pad}${key}: ${yamlScalar(item)}`);
    }
  }
  return lines;
}

export function yieldContractText(result: unknown, fallback = ""): string {
  if (typeof result === "string") return result || fallback;
  if (!result || typeof result !== "object" || Array.isArray(result)) return text(result) || fallback;
  const wrapper = result as Dict;
  if (Object.keys(wrapper).length === 0) return fallback;
  const data = wrapper.data;
  if (data && typeof data === "object" && !Array.isArray(data)) {
    const content = (data as Dict).content;
    if (typeof content === "string") return content || fallback;
    const rendered = yamlLines(data as Dict).join("\n");
    return rendered ? `${rendered}\n` : fallback;
  }
  if (typeof wrapper.content === "string") return wrapper.content || fallback;
  return text(result) || fallback;
}

export function normalizeYieldInput(input: Dict, fallback: string): Dict {
  const result = input.result;
  if (result && typeof result === "object" && !Array.isArray(result)) {
    const envelope = result as Dict;
    if ("data" in envelope || "error" in envelope) return input;
  }
  if (!fallback.trim()) return input;
  return { ...input, result: { data: { content: fallback } } };
}

function parseDecision(stdout: string): string | undefined {
  for (const line of stdout.split("\n")) {
    if (!line.trim().startsWith("{")) continue;
    try {
      const data = JSON.parse(line) as Dict;
      const hook = data.hookSpecificOutput as Dict | undefined;
      if (hook?.permissionDecision === "deny") {
        return text(hook.permissionDecisionReason) || "Harness policy denied the operation.";
      }
      if (data.decision === "block") return text(data.reason) || "Harness policy denied the operation.";
    } catch {
      // Non-JSON diagnostic output is handled by the script exit code.
    }
  }
  return undefined;
}

function runPolicy(
  cwd: string,
  script: string,
  args: string[],
  payload: Dict,
): PolicyResult {
  const proc = spawnSync(gatePath(script), args, {
    cwd,
    // The child inherits the host environment and NOTHING IS ADDED to it (FEAT-42 T-20).
    // A root override used to be injected here, set to the host process working directory.
    // Every script this helper invokes now derives its own root from its own file location,
    // so handing it one is redundant — and worse: a feature worktree carries the harness
    // marker, so a wrong-but-plausible cwd probes VALID and is honoured in preference to the
    // script's own derivation. That is the fail-open this feature closes, reopened from
    // outside the directory the invariant scans. Once a parent sets it every descendant
    // inherits it, which is how one bad value reaches a whole process tree.
    env: { ...process.env },
    input: JSON.stringify(payload),
    encoding: "utf8",
  });
  const stdout = proc.stdout || "";
  const stderr = (proc.stderr || "").trim();
  const structuredReason = parseDecision(stdout);
  if (structuredReason) return { blocked: true, reason: structuredReason, stdout };
  if (proc.status === 2) {
    return { blocked: true, reason: stderr || `${script} denied the operation.`, stdout };
  }
  if (proc.error) throw proc.error;
  if (proc.status !== 0) {
    // Preserve each existing policy script's non-blocking error contract. Safety-
    // critical internal failures are converted to exit 2 inside those scripts.
    return { blocked: false, reason: stderr || `${script} exited ${proc.status}`, stdout };
  }
  return { blocked: false, stdout };
}

function basePayload(agent: string, eventName: string, cwd: string): Dict {
  return { agent_type: agent, hook_event_name: eventName, cwd };
}

function preDomain(
  cwd: string,
  agent: string,
  toolName: string,
  input: Dict,
  runner: PolicyRunner,
): PolicyResult[] {
  const base = basePayload(agent, "PreToolUse", cwd);
  if (toolName === "write") {
    return [runner(cwd, "check-domain.sh", [], {
      ...base,
      tool_name: "Write",
      tool_input: { file_path: input.path, content: input.content },
    })];
  }
  if (toolName === "edit") {
    return extractEditPaths(input.input).map((filePath) => runner(cwd, "check-domain.sh", [], {
      ...base,
      tool_name: "Edit",
      tool_input: { file_path: filePath },
    }));
  }
  return [];
}

function postDomain(
  cwd: string,
  agent: string,
  toolName: string,
  input: Dict,
  runner: PolicyRunner,
): PolicyResult[] {
  const base = basePayload(agent, "PostToolUse", cwd);
  if (toolName === "write") {
    return [runner(cwd, "check-domain.sh", ["--post"], {
      ...base,
      tool_name: "Write",
      tool_input: { file_path: input.path, content: input.content },
    })];
  }
  if (toolName === "edit") {
    return extractEditPaths(input.input).map((filePath) => runner(cwd, "check-domain.sh", ["--post"], {
      ...base,
      tool_name: "Edit",
      tool_input: { file_path: filePath },
    }));
  }
  if (toolName === "bash") {
    return [runner(cwd, "check-domain.sh", ["--post"], {
      ...base,
      tool_name: "Bash",
      tool_input: { command: input.command },
    })];
  }
  return [];
}

function firstBlock(results: PolicyResult[]): string | undefined {
  return results.find((result) => result.blocked)?.reason;
}

type TaskDispatch = { agent: string; task: string; model?: unknown };
type ClaimReceipt = { root: string; feature: string; agent: string; claimId: string };

export function normalizeTaskDispatches(input: Dict): TaskDispatch[] {
  if (Array.isArray(input.tasks)) {
    return input.tasks.flatMap((item) => {
      if (!item || typeof item !== "object") return [];
      const value = item as Dict;
      const agent = text(value.agent);
      const task = text(value.task);
      return agent && task ? [{ agent, task, ...("model" in value ? { model: value.model } : {}) }] : [];
    });
  }
  const agent = text(input.agent);
  const task = text(input.task);
  return agent && task ? [{ agent, task, ...("model" in input ? { model: input.model } : {}) }] : [];
}

function taskModelOverride(input: Dict): string | undefined {
  if ("model" in input) return "Harness dispatches select an agent, never a per-invocation model.";
  return normalizeTaskDispatches(input).some((item) => "model" in item)
    ? "Harness dispatches select an agent, never a per-invocation model."
    : undefined;
}

function parseClaimReceipt(stdout: string): ClaimReceipt | undefined {
  for (const line of stdout.split("\n")) {
    if (!line.trim().startsWith("{")) continue;
    try {
      const parsed = JSON.parse(line) as Dict;
      const raw = parsed.harness_claim as Dict | undefined;
      if (!raw) continue;
      const root = text(raw.root);
      const feature = text(raw.feature);
      const agent = text(raw.agent);
      const claimId = text(raw.claim_id);
      if (root && feature && agent && claimId) return { root, feature, agent, claimId };
    } catch {
      continue;
    }
  }
  return undefined;
}

function sessionId(ctx: any): string | undefined {
  try {
    const value = ctx.sessionManager?.getSessionId?.();
    return typeof value === "string" && value ? value : undefined;
  } catch {
    return undefined;
  }
}

type TaskIdentity = { index: number; agentId?: string; jobId?: string; settled: boolean };

function taskIdentities(details: unknown): TaskIdentity[] {
  if (!details || typeof details !== "object") return [];
  const value = details as Dict;
  const identities = new Map<number, TaskIdentity>();
  const add = (row: unknown, fallbackIndex: number, settledBySource: boolean): void => {
    if (!row || typeof row !== "object") return;
    const item = row as Dict;
    const rawIndex = item.index;
    const index = typeof rawIndex === "number" ? rawIndex : fallbackIndex;
    const agentId = text(item.agentId || item.id || item.outputId) || undefined;
    const jobId = text(item.jobId || item.job_id) || undefined;
    const status = text(item.status || item.state);
    const settled = settledBySource
      || typeof item.exitCode === "number"
      || ["idle", "parked", "aborted", "failed", "completed", "exited"].includes(status);
    const prior = identities.get(index);
    identities.set(index, {
      index,
      agentId: agentId || prior?.agentId,
      jobId: jobId || prior?.jobId,
      settled: settled || prior?.settled || false,
    });
  };
  (Array.isArray(value.progress) ? value.progress : []).forEach(
    (row, index) => add(row, index, false),
  );
  (Array.isArray(value.results) ? value.results : []).forEach(
    (row, index) => add(row, index, true),
  );
  return [...identities.values()].sort((a, b) => a.index - b.index);
}

function releaseClaim(
  runner: PolicyRunner,
  cwd: string,
  receipt: ClaimReceipt,
): void {
  runner(cwd, "inflight_registry.py", [
    "release",
    "--claim-id", receipt.claimId,
    "--feature", receipt.feature,
    "--root", receipt.root,
  ], {});
}

function messageText(message: unknown): string {
  if (!message || typeof message !== "object") return "";
  const content = (message as Dict).content;
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content.map((part) => {
    if (typeof part === "string") return part;
    if (part && typeof part === "object" && "text" in part) return text((part as Dict).text);
    return "";
  }).join("");
}

function lastAssistantText(messages: unknown): string {
  if (!Array.isArray(messages)) return "";
  for (let i = messages.length - 1; i >= 0; i -= 1) {
    const message = messages[i] as Dict;
    if (message?.role !== "assistant") continue;
    const content = message.content;
    if (typeof content === "string") return content;
    if (Array.isArray(content)) {
      return content.map((part) => {
        if (typeof part === "string") return part;
        if (part && typeof part === "object" && "text" in part) return text((part as Dict).text);
        return "";
      }).join("");
    }
  }
  return "";
}

export function registerHarnessHooks(pi: any, policyRunner: PolicyRunner = runPolicy): void {
  let currentAgent: string | undefined;
  let currentFeature: string | undefined;
  let expertiseInjected = false;
  let claimsReconciled = false;
  let lastAssistantMessage = "";
  const pendingTaskCalls = new Map<string, ClaimReceipt[]>();
  const runtimeClaims = new Map<string, ClaimReceipt>();
  const setFeature = (feature: string | undefined, ctx: any): void => {
    if (!feature) return;
    if (currentFeature && currentFeature !== feature) {
      throw new Error(`conflicting Harness feature markers: ${currentFeature}, ${feature}`);
    }
    currentFeature = feature;
    if (currentAgent && !claimsReconciled) {
      policyRunner(ctx.cwd, "inflight_registry.py", [
        "reconcile",
        "--feature", currentFeature,
        "--root", ctx.cwd,
      ], {});
      claimsReconciled = true;
    }
  };

  pi.on("before_agent_start", async (event: Dict, ctx: any) => {
    const detected = detectHarnessAgent(event.systemPrompt);
    const detectedFeature = detectHarnessFeature(event.systemPrompt);
    if (detected) currentAgent = detected;
    setFeature(detectedFeature, ctx);
    if (!currentAgent || expertiseInjected) return;

    const result = policyRunner(ctx.cwd, "inject-expertise.sh", [], {
      ...basePayload(currentAgent, "SubagentStart", ctx.cwd),
    });
    if (result.blocked || !result.stdout.trim()) return;
    try {
      const data = JSON.parse(result.stdout) as Dict;
      const hook = data.hookSpecificOutput as Dict | undefined;
      const additionalContext = text(hook?.additionalContext);
      if (!additionalContext.trim()) return;
      expertiseInjected = true;
      return {
        message: {
          customType: "harness-expertise",
          content: additionalContext,
          display: false,
          details: { agent: currentAgent },
          attribution: "harness",
        },
      };
    } catch {
      throw new Error("inject-expertise.sh returned invalid JSON");
    }
  });

  pi.on("message_update", async (event: Dict, ctx: any) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    setFeature(detectHarnessFeature([messageText(candidate)]), ctx);
    const found = lastAssistantText([candidate]);
    if (found.trim()) lastAssistantMessage = found;
  });

  pi.on("message_end", async (event: Dict, ctx: any) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    setFeature(detectHarnessFeature([messageText(candidate)]), ctx);
    const found = lastAssistantText([candidate]);
    if (found.trim()) lastAssistantMessage = found;
  });

  pi.on("tool_call", async (event: Dict, ctx: any) => {
    if (!currentAgent) return;
    const toolName = text(event.toolName);
    const input = (event.input && typeof event.input === "object" ? event.input : {}) as Dict;

    let revisedInput: Dict | undefined;
    let reason = firstBlock(preDomain(ctx.cwd, currentAgent, toolName, input, policyRunner));
    if (!reason && toolName === "bash") {
      const payload = {
        ...basePayload(currentAgent, "PreToolUse", ctx.cwd),
        tool_name: "Bash",
        tool_input: { command: input.command },
      };
      reason = firstBlock([
        policyRunner(ctx.cwd, "gh-close-gate.sh", [], payload),
        policyRunner(ctx.cwd, "branch-create-gate.sh", [], payload),
        policyRunner(ctx.cwd, "bash-write-guard.sh", [], payload),
      ]);
    }
    if (!reason && toolName === "task") {
      reason = taskModelOverride(input);
      const receipts: ClaimReceipt[] = [];
      if (!reason) {
        for (const dispatch of normalizeTaskDispatches(input)) {
          const result = policyRunner(ctx.cwd, "dispatch-guard.sh", [], {
            ...basePayload(currentAgent, "PreToolUse", ctx.cwd),
            tool_name: "Task",
            tool_input: dispatch,
            session_id: sessionId(ctx),
            harness_runtime: "omp",
            supervisor_pid: process.pid,
          });
          if (result.blocked) {
            receipts.forEach((receipt) => releaseClaim(policyRunner, ctx.cwd, receipt));
            reason = result.reason || "Harness dispatch policy denied the task.";
            break;
          }
          const receipt = parseClaimReceipt(result.stdout);
          if (!receipt) {
            receipts.forEach((created) => releaseClaim(policyRunner, ctx.cwd, created));
            reason = "Harness dispatch policy returned no claim receipt; the task was not started.";
            break;
          }
          receipts.push(receipt);
        }
      }
      if (!reason && receipts.length) {
        pendingTaskCalls.set(text(event.toolCallId) || "task", receipts);
      }
    }
    if (!reason && toolName === "yield") {
      const normalized = normalizeYieldInput(input, lastAssistantMessage);
      const contract = yieldContractText(normalized.result, lastAssistantMessage);
      const result = policyRunner(ctx.cwd, "validate-digest.py", ["--hook"], {
        ...basePayload(currentAgent, "SubagentStop", ctx.cwd),
        stop_hook_active: false,
        last_assistant_message: contract,
        harness_runtime: "omp",
        harness_feature: currentFeature,
        harness_agent_id: text(ctx.agentId) || undefined,
      });
      debug(`yield agent=${currentAgent} value=${contract.slice(0, 500)}`);
      debug(`yield verdict blocked=${result.blocked} reason=${result.reason || "none"}`);
      reason = result.blocked ? result.reason : undefined;
      if (!reason && normalized !== input) revisedInput = normalized;
    }
    if (reason) return { block: true, reason };
    if (revisedInput) return { input: revisedInput };
  });

  pi.on("tool_result", async (event: Dict, ctx: any) => {
    if (!currentAgent) return;
    const toolName = text(event.toolName);
    const input = (event.input && typeof event.input === "object" ? event.input : {}) as Dict;
    if (toolName === "task") {
      const key = text(event.toolCallId) || "task";
      const receipts = pendingTaskCalls.get(key) || [];
      pendingTaskCalls.delete(key);
      if (event.isError) {
        receipts.forEach((receipt) => releaseClaim(policyRunner, ctx.cwd, receipt));
      } else {
        const identities = taskIdentities(event.details);
        receipts.forEach((receipt, index) => {
          const identity = identities.find((item) => item.index === index);
          if (identity?.settled) {
            releaseClaim(policyRunner, ctx.cwd, receipt);
            return;
          }
          if (!identity?.agentId && !identity?.jobId) {
            releaseClaim(policyRunner, ctx.cwd, receipt);
            return;
          }
          const args = [
            "attach",
            "--agent", receipt.agent,
            "--feature", receipt.feature,
            "--claim-id", receipt.claimId,
            "--root", receipt.root,
          ];
          if (identity.agentId) args.push("--agent-id", identity.agentId);
          if (identity.jobId) args.push("--job-id", identity.jobId);
          policyRunner(ctx.cwd, "inflight_registry.py", args, {});
          if (identity.agentId) runtimeClaims.set(`agent:${identity.agentId}`, receipt);
          if (identity.jobId) runtimeClaims.set(`job:${identity.jobId}`, receipt);
        });
      }
    }
    const reason = firstBlock(postDomain(ctx.cwd, currentAgent, toolName, input, policyRunner));
    if (!reason) return;
    const content = Array.isArray(event.content) ? event.content : [];
    return {
      content: [...content, { type: "text", text: `Harness post-write check: ${reason}` }],
      isError: true,
    };
  });

  pi.on("task:subagent:lifecycle", async (event: Dict, ctx: any) => {
    const status = text(event.status || event.state);
    if (!["idle", "parked", "aborted", "failed", "completed", "exited"].includes(status)) return;
    const agentId = text(event.agentId || event.id);
    const jobId = text(event.jobId || event.job_id);
    const receipt = runtimeClaims.get(`agent:${agentId}`) || runtimeClaims.get(`job:${jobId}`);
    if (receipt) {
      releaseClaim(policyRunner, ctx.cwd, receipt);
      if (agentId) runtimeClaims.delete(`agent:${agentId}`);
      if (jobId) runtimeClaims.delete(`job:${jobId}`);
      return;
    }
    const args = ["release", "--root", ctx.cwd];
    if (currentFeature) args.push("--feature", currentFeature);
    if (agentId) args.push("--agent-id", agentId);
    if (jobId) args.push("--job-id", jobId);
    if (agentId || jobId) policyRunner(ctx.cwd, "inflight_registry.py", args, {});
  });

  pi.on("agent_end", async (event: Dict, ctx: any) => {
    if (!currentAgent) return;
    const finalText = lastAssistantText(event.messages);
    if (!finalText.trim()) return;
    // Notification-only backstop. Normal task agents are validated on `yield`.
    const result = policyRunner(ctx.cwd, "validate-digest.py", ["--hook"], {
      ...basePayload(currentAgent, "SubagentStop", ctx.cwd),
      stop_hook_active: true,
      last_assistant_message: finalText,
      harness_runtime: "omp",
      harness_feature: currentFeature,
    });
    if (result.reason && result.blocked) ctx.ui?.notify?.(result.reason, "warning");
  });
}

export default function harnessHooks(pi: any): void {
  registerHarnessHooks(pi);
}
