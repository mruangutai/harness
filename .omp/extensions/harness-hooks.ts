import { spawnSync } from "node:child_process";
import { join } from "node:path";

const AGENT_MARKER = /^HARNESS_AGENT_ID: (harness-[a-z0-9-]+)$/gm;
const BIN = ".agents/skills/harness/bin";

type Dict = Record<string, unknown>;
type PolicyResult = { blocked: boolean; reason?: string; stdout: string };

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
  const proc = spawnSync(join(cwd, BIN, script), args, {
    cwd,
    env: { ...process.env, HARNESS_PROJECT_DIR: cwd },
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

function preDomain(cwd: string, agent: string, toolName: string, input: Dict): PolicyResult[] {
  const base = basePayload(agent, "PreToolUse", cwd);
  if (toolName === "write") {
    return [runPolicy(cwd, "check-domain.sh", [], {
      ...base,
      tool_name: "Write",
      tool_input: { file_path: input.path, content: input.content },
    })];
  }
  if (toolName === "edit") {
    return extractEditPaths(input.input).map((filePath) => runPolicy(cwd, "check-domain.sh", [], {
      ...base,
      tool_name: "Edit",
      tool_input: { file_path: filePath },
    }));
  }
  return [];
}

function postDomain(cwd: string, agent: string, toolName: string, input: Dict): PolicyResult[] {
  const base = basePayload(agent, "PostToolUse", cwd);
  if (toolName === "write") {
    return [runPolicy(cwd, "check-domain.sh", ["--post"], {
      ...base,
      tool_name: "Write",
      tool_input: { file_path: input.path, content: input.content },
    })];
  }
  if (toolName === "edit") {
    return extractEditPaths(input.input).map((filePath) => runPolicy(cwd, "check-domain.sh", ["--post"], {
      ...base,
      tool_name: "Edit",
      tool_input: { file_path: filePath },
    }));
  }
  if (toolName === "bash") {
    return [runPolicy(cwd, "check-domain.sh", ["--post"], {
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

function taskModelOverride(input: Dict): string | undefined {
  const tasks = Array.isArray(input.tasks) ? input.tasks : [];
  for (const task of tasks) {
    if (task && typeof task === "object" && "model" in task) {
      return `Harness dispatches select an agent, never a per-invocation model.`;
    }
  }
  return undefined;
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

export default function harnessHooks(pi: any): void {
  let currentAgent: string | undefined;
  let expertiseInjected = false;
  let lastAssistantMessage = "";

  pi.on("before_agent_start", async (event: Dict, ctx: any) => {
    const detected = detectHarnessAgent(event.systemPrompt);
    if (detected) currentAgent = detected;
    if (!currentAgent || expertiseInjected) return;

    const result = runPolicy(ctx.cwd, "inject-expertise.sh", [], {
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

  pi.on("message_update", async (event: Dict) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    const found = lastAssistantText([candidate]);
    if (found.trim()) lastAssistantMessage = found;
  });

  pi.on("message_end", async (event: Dict) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    const found = lastAssistantText([candidate]);
    if (found.trim()) lastAssistantMessage = found;
  });

  pi.on("tool_call", async (event: Dict, ctx: any) => {
    if (!currentAgent) return;
    const toolName = text(event.toolName);
    const input = (event.input && typeof event.input === "object" ? event.input : {}) as Dict;

    let revisedInput: Dict | undefined;
    let reason = firstBlock(preDomain(ctx.cwd, currentAgent, toolName, input));
    if (!reason && toolName === "bash") {
      const payload = {
        ...basePayload(currentAgent, "PreToolUse", ctx.cwd),
        tool_name: "Bash",
        tool_input: { command: input.command },
      };
      reason = firstBlock([
        runPolicy(ctx.cwd, "branch-create-gate.sh", [], payload),
        runPolicy(ctx.cwd, "bash-write-guard.sh", [], payload),
      ]);
    }
    if (!reason && toolName === "task") reason = taskModelOverride(input);
    if (!reason && toolName === "yield") {
      const normalized = normalizeYieldInput(input, lastAssistantMessage);
      const contract = yieldContractText(normalized.result, lastAssistantMessage);
      const result = runPolicy(ctx.cwd, "validate-digest.py", ["--hook"], {
        ...basePayload(currentAgent, "SubagentStop", ctx.cwd),
        stop_hook_active: false,
        last_assistant_message: contract,
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
    const reason = firstBlock(postDomain(ctx.cwd, currentAgent, toolName, input));
    if (!reason) return;
    const content = Array.isArray(event.content) ? event.content : [];
    return {
      content: [...content, { type: "text", text: `Harness post-write check: ${reason}` }],
      isError: true,
    };
  });

  pi.on("agent_end", async (event: Dict, ctx: any) => {
    if (!currentAgent) return;
    const finalText = lastAssistantText(event.messages);
    if (!finalText.trim()) return;
    // Notification-only backstop. Normal task agents are validated on `yield`.
    const result = runPolicy(ctx.cwd, "validate-digest.py", ["--hook"], {
      ...basePayload(currentAgent, "SubagentStop", ctx.cwd),
      stop_hook_active: true,
      last_assistant_message: finalText,
    });
    if (result.reason && result.blocked) ctx.ui?.notify?.(result.reason, "warning");
  });
}
