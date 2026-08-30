import { spawnSync } from "node:child_process";
import { closeSync, openSync, readFileSync, readSync, statSync } from "node:fs";
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

// --- FEAT-44 (issue #923): the OMP-native orchestrator context advisory ------
//
// The orchestrator is a subagent, and `ctx.getContextUsage()` returns `undefined`
// in subagent sessions (upstream can1357/oh-my-pi#10097). So the figure is read
// off disk instead: omp persists every session, including subagents, as
// append-only JSONL, and each assistant record carries the number omp itself
// computed. That is the host's own value by the host's own definition, not an
// estimate.
//
// EVERY failure branch below yields NO figure rather than a wrong one.

export type ContextAnchor =
  | { kind: "tokens"; tokens: number }
  | { kind: "inert"; scannedBytes: number; field: string }
  | { kind: "none" };

// Named to match the resolver in the retired context-watch.py: DEC-198's
// amendment re-homes its citation to this constant.
export const DEFAULT_CONTEXT_WARN_TOKENS = 200000;

// The ONE home for this path. `readContextAnchor` walks it to read the value and
// hands it out on the inert arm; `contextInertText` prints only what it is given.
// So the notice can never name a field the parse did not look for.
export const CONTEXT_TOKENS_FIELD = "message.contextSnapshot.promptTokens";

const CONTEXT_TOKENS_SEGMENTS = CONTEXT_TOKENS_FIELD.split(".");
// Keyed prefilter. The key implies the substring, so a false negative is
// impossible; a false positive is caught by the parse and the type check below.
const CONTEXT_PREFILTER = "contextSnapshot";
const CONTEXT_INITIAL_WINDOW = 65536;
const SESSION_FILE_ACCESSOR = "sessionManager.getSessionFile";

function readTailBytes(path: string, size: number, length: number): string | undefined {
  const start = Math.max(0, size - length);
  const span = size - start;
  if (span <= 0) return "";
  const buffer = Buffer.allocUnsafe(span);
  let fd: number | undefined;
  try {
    fd = openSync(path, "r");
    readSync(fd, buffer, 0, span, start);
  } catch {
    return undefined;
  } finally {
    if (fd !== undefined) {
      try { closeSync(fd); } catch { /* nothing actionable */ }
    }
  }
  return buffer.toString("utf8");
}

function anchorFromFragment(fragment: string): number | undefined {
  if (!fragment.includes(CONTEXT_PREFILTER)) return undefined;
  let parsed: unknown;
  try {
    parsed = JSON.parse(fragment);
  } catch {
    return undefined;   // a torn or truncated line is skipped, never guessed at
  }
  let cursor: unknown = parsed;
  for (const segment of CONTEXT_TOKENS_SEGMENTS) {
    if (!cursor || typeof cursor !== "object") return undefined;
    cursor = (cursor as Record<string, unknown>)[segment];
  }
  return typeof cursor === "number" && Number.isFinite(cursor) ? cursor : undefined;
}

// Stateless by construction: the newest anchor is read fresh on every call. No
// byte offset, no accumulated delta, no dedupe — so truncation and rotation are
// non-issues. The once-per-session cap lives in the handler's closure, not here,
// which keeps this function pure and directly testable.
export function readContextAnchor(sessionFile: string | undefined): ContextAnchor {
  if (!sessionFile) return { kind: "none" };
  let size: number;
  try {
    size = statSync(sessionFile).size;
  } catch {
    return { kind: "none" };
  }
  // The window MUST adapt: measured anchor gaps run to 95 KiB on real
  // transcripts, driven by large tool-result lines, so a fixed 64 KiB read is a
  // latent miss rather than an optimisation.
  let window = CONTEXT_INITIAL_WINDOW;
  for (;;) {
    const whole = window >= size;
    const text = readTailBytes(sessionFile, size, whole ? size : window);
    if (text === undefined) return { kind: "none" };
    const fragments = text.split("\n");
    // A partial window's first fragment may be a torn line; the whole-file pass
    // has no such fragment.
    if (!whole) fragments.shift();
    for (let i = fragments.length - 1; i >= 0; i -= 1) {
      const tokens = anchorFromFragment(fragments[i]);
      if (tokens !== undefined) return { kind: "tokens", tokens };
    }
    if (whole) {
      return { kind: "inert", scannedBytes: size, field: CONTEXT_TOKENS_FIELD };
    }
    window *= 4;
  }
}

// Mirrors the miss-path set DEC-198 records: file missing, unreadable, not JSON,
// no budgets object, key absent, or value not a number (bools excluded, since
// typeof true is "boolean").
export function resolveContextWarnTokens(root: string): number {
  try {
    const raw = readFileSync(join(root, ".harness", "harness.json"), "utf8");
    const budgets = (JSON.parse(raw) as Record<string, unknown>).budgets;
    if (budgets && typeof budgets === "object") {
      const value = (budgets as Record<string, unknown>).orchestrator_context_warn_tokens;
      if (typeof value === "number" && Number.isFinite(value)) return value;
    }
  } catch { /* every miss path falls through to the declared default */ }
  return DEFAULT_CONTEXT_WARN_TOKENS;
}

export function contextAdvisoryText(tokens: number, threshold: number): string {
  const ratio = (tokens / threshold).toFixed(2);
  return `CONTEXT: this orchestrator session measures ${tokens} tokens against `
    + `budgets.orchestrator_context_warn_tokens = ${threshold} (${ratio}x). This ADVISES and `
    + `never refuses (DEC-198). Weigh it yourself, and if you hand off, hand off at a seam `
    + `rather than mid-phase (DEC-201).`;
}

export function contextInertText(scannedBytes: number, field: string): string {
  return `CONTEXT: no ${field} value was found in the ${scannedBytes} bytes scanned of this `
    + `session's transcript, so the context advisory is inert for this session. The host's `
    + `record shape may have changed (issue #923). This ADVISES and never refuses.`;
}

export type SessionFileResolution =
  | { kind: "path"; path: string }
  | { kind: "absent" }
  | { kind: "failed"; accessor: string };

// Its own export, not an inline try/catch, because the two failure classes must
// be told apart and the distinction must be unit-testable with a fake ctx.
// Folding "the accessor moved" into "no session yet" is exactly the silent-
// undefined shape issue #923 exists to fix, so it must not be rebuilt here.
export function resolveSessionFile(ctx: unknown): SessionFileResolution {
  const manager = ctx && typeof ctx === "object"
    ? (ctx as Record<string, unknown>).sessionManager
    : undefined;
  if (!manager || typeof manager !== "object") {
    return { kind: "failed", accessor: SESSION_FILE_ACCESSOR };
  }
  const accessor = (manager as Record<string, unknown>).getSessionFile;
  if (typeof accessor !== "function") {
    return { kind: "failed", accessor: SESSION_FILE_ACCESSOR };
  }
  let value: unknown;
  try {
    value = (accessor as () => unknown).call(manager);
  } catch {
    return { kind: "failed", accessor: SESSION_FILE_ACCESSOR };
  }
  return typeof value === "string" && value.length > 0
    ? { kind: "path", path: value }
    : { kind: "absent" };
}

export function contextAccessorFailureText(accessor: string): string {
  return `CONTEXT: ${accessor} did not resolve this session's transcript, so context cannot be `
    + `measured this session — the host's session-resolution API has moved (issue #923). This `
    + `ADVISES and never refuses.`;
}

export function registerHarnessHooks(pi: any, policyRunner: PolicyRunner = runPolicy): void {
  let currentAgent: string | undefined;
  let currentFeature: string | undefined;
  let expertiseInjected = false;
  let featureCaptured = false;
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
    featureCaptured = true;
    if (currentAgent && !claimsReconciled) {
      policyRunner(ctx.cwd, "inflight_registry.py", [
        "reconcile",
        "--feature", currentFeature,
        "--root", ctx.cwd,
      ], {});
      claimsReconciled = true;
    }
  };

  // DEC-204 captures the ASSIGNMENT message — it arrives ONCE, as `user`, before the
  // first tool call. Nothing after it is an identity source: not this agent's own
  // output, and above all not a tool result echoing another feature's stored dispatch
  // or notes, which is routine harness work rather than an attack. Unfiltered and
  // unbounded, both failure paths are live — an agent on feature A that reads feature
  // B's notes throws from inside an async pi.on handler, or, if the foreign marker
  // lands first, reconciles against the WRONG feature's claims.
  const captureFeatureFromMessage = (candidate: unknown, ctx: { cwd: string }): void => {
    if (featureCaptured) return;
    if (!candidate || typeof candidate !== "object") return;
    if ((candidate as Dict).role !== "user") return;
    setFeature(detectHarnessFeature([messageText(candidate)]), ctx);
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
    captureFeatureFromMessage(candidate, ctx);
    const found = lastAssistantText([candidate]);
    if (found.trim()) lastAssistantMessage = found;
  });

  pi.on("message_end", async (event: Dict, ctx: any) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    captureFeatureFromMessage(candidate, ctx);
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
          // DEC-100: ONLY exit 2 BLOCKS. dispatch-guard.sh exits 0 WITHOUT printing a
          // receipt on every pass-through branch it has — unreadable payload (:34), a
          // non-harness dispatcher (:38) or dispatched persona (:72), no checkout root
          // (:112), inflight_registry unavailable (:138), OMP runtime with no supervisor
          // pid (:145), and its own internal exception (:187, "passing through, the
          // dispatch is NOT blocked"). Reading an ABSENT receipt as a refusal inverted
          // all seven into a hard block: a transient guard fault would halt the very
          // multi-hour unattended run this feature exists to enable, and dispatching any
          // non-harness subagent (scout, sonic) was refused outright because the guard
          // deliberately records no claim for one. Whether a dispatch gets a claim is the
          // guard's decision; this caller only enforces the refusals the guard declares.
          const receipt = parseClaimReceipt(result.stdout);
          if (receipt) receipts.push(receipt);
          else debug(`dispatch-guard allowed ${dispatch.agent} with no claim recorded`);
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
