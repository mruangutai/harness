import { spawnSync } from "node:child_process";
import { closeSync, existsSync, openSync, readdirSync, readFileSync, readSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const AGENT_MARKER = /^HARNESS_AGENT_ID: (harness-[a-z0-9-]+)$/gm;
const FEATURE_MARKER = /^HARNESS-FEATURE: ((?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+)$/gm;
// #1677: an operator-supplied review pin travels in the DISPATCH — the one text a reviewer
// does not author — and reaches validate-digest.py as `harness_review_pin`, the same way the
// feature marker reaches it as `harness_feature`. It stands in for feature.json's review_sha
// when that is unset (a frozen feature, a review dispatched outside the plan path) and must
// agree with it when both exist.
const REVIEW_PIN_MARKER = /^HARNESS-REVIEW-PIN: ([0-9a-f]{7,40})$/gm;
// #1855: the mission rides the same road. A distill dispatch (DEC-145) has no diff to grade
// and no suite to run; validate-digest.py pins the readers' gate fields to their did-nothing
// spelling on `harness_mission: distill` rather than teaching them to fabricate a pass.
const MISSION_MARKER = /^HARNESS-MISSION: ([a-z]+)$/gm;
const BIN = ".agents/skills/harness/bin";

// THE GATE DIRECTORY IS DERIVED FROM THIS FILE, NOT FROM ANY CALLER (FEAT-42, panel B-1).
// This module ships at <root>/.omp/extensions/harness-hooks.ts, so <root> is two levels up.
// What stood here was `join(cwd, BIN, script)` against a caller-supplied ctx.cwd: the
// executable that enforces a policy was CHOSEN by the party the policy governs. Issue #556,
// which this feature closes, was the same defect one level down — a harness_boundary.py in
// an agent's working directory became the module a gate imported, taking check-domain.py
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

// One marker per identity axis, each with exactly one value across every layer: two
// different values for the same axis is a conflict, never a choice.
function detectMarker(systemPrompt: unknown, marker: RegExp, what: string): string | undefined {
  if (!Array.isArray(systemPrompt)) return undefined;
  const found = new Set<string>();
  for (const layer of systemPrompt) {
    if (typeof layer !== "string") continue;
    for (const match of layer.matchAll(marker)) found.add(match[1]);
  }
  if (found.size > 1) {
    throw new Error(`conflicting Harness ${what} markers: ${[...found].sort().join(", ")}`);
  }
  return found.values().next().value;
}

// Exported: the test seam that pins the marker grammar.
export function detectHarnessAgent(systemPrompt: unknown): string | undefined {
  return detectMarker(systemPrompt, AGENT_MARKER, "agent");
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

// A yield envelope that names `data` or `error` but carries nothing under it (#1676). The
// host finalizer reads such a yield as "null data" and settles the job exit 1 — while the
// complete digest sits in the assistant text the model wrote just before yielding. The
// repair below used to key on the KEY being present (`"data" in envelope`), so `data: null`,
// `data: ""`, `data: {}` and `data: []` all passed through unrepaired: a well-formed return,
// verified on disk, recorded as a failed run. Measured five times across BUG-285 and BUG-380.
export function hollowYieldValue(value: unknown): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === "string") return !value.trim();
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value as Dict).length === 0;
  return false;
}

export function normalizeYieldInput(input: Dict, fallback: string): Dict {
  // Current OMP yields `{data|error}` directly; older hosts wrap that envelope in `result`.
  // Preserve either explicit form. Only synthesize legacy `result` data for an empty yield.
  if ("data" in input || "error" in input) return input;
  const result = input.result;
  if (result && typeof result === "object" && !Array.isArray(result)) {
    const envelope = result as Dict;
    if (!hollowYieldValue(envelope.data) || !hollowYieldValue(envelope.error)) return input;
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

function basePayload(agent: string, eventName: string, cwd: string, ctx?: any): Dict {
  const agentId = text(ctx?.agentId);
  const parentAgentId = text(ctx?.parentAgentId);
  return {
    agent_type: agent,
    hook_event_name: eventName,
    cwd,
    ...(agentId ? { harness_agent_id: agentId } : {}),
    ...(parentAgentId ? { harness_parent_agent_id: parentAgentId } : {}),
  };
}

function preDomain(
  cwd: string,
  agent: string,
  toolName: string,
  input: Dict,
  runner: PolicyRunner,
  ctx?: any,
): PolicyResult[] {
  const base = basePayload(agent, "PreToolUse", cwd, ctx);
  if (toolName === "write") {
    return [runner(cwd, "check-domain.py", [], {
      ...base,
      tool_name: "Write",
      tool_input: { file_path: input.path, content: input.content },
    })];
  }
  if (toolName === "edit") {
    return extractEditPaths(input.input).map((filePath) => runner(cwd, "check-domain.py", [], {
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
  ctx?: any,
): PolicyResult[] {
  const base = basePayload(agent, "PostToolUse", cwd, ctx);
  if (toolName === "write") {
    return [runner(cwd, "check-domain.py", ["--post"], {
      ...base,
      tool_name: "Write",
      tool_input: { file_path: input.path, content: input.content },
    })];
  }
  if (toolName === "edit") {
    return extractEditPaths(input.input).map((filePath) => runner(cwd, "check-domain.py", ["--post"], {
      ...base,
      tool_name: "Edit",
      tool_input: { file_path: filePath },
    }));
  }
  if (toolName === "bash") {
    return [runner(cwd, "check-domain.py", ["--post"], {
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

type TaskDispatch = { agent: string; task: string; name?: string; model?: unknown };
type ClaimReceipt = { root: string; feature: string; agent: string; claimId: string };

export function normalizeTaskDispatches(input: Dict): TaskDispatch[] {
  if (Array.isArray(input.tasks)) {
    return input.tasks.flatMap((item) => {
      if (!item || typeof item !== "object") return [];
      const value = item as Dict;
      const agent = text(value.agent);
      const task = text(value.task);
      const name = text(value.name);
      return agent && task ? [{
        agent,
        task,
        ...(name ? { name } : {}),
        ...("model" in value ? { model: value.model } : {}),
      }] : [];
    });
  }
  const agent = text(input.agent);
  const task = text(input.task);
  const name = text(input.name);
  return agent && task ? [{
    agent,
    task,
    ...(name ? { name } : {}),
    ...("model" in input ? { model: input.model } : {}),
  }] : [];
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

// BUG-1898: a task result names its children by their runtime ids, and that id is the only
// key a claim is ever released by. Row order is not dispatch order (a batch settles in any
// order and mixes governed with plain work), so nothing here is keyed by position.
const SETTLED_STATUSES = ["completed", "failed", "aborted"];

export function settledRunIds(details: unknown): string[] {
  if (!details || typeof details !== "object") return [];
  const value = details as Dict;
  const ids = new Set<string>();
  const add = (row: unknown, settledBySource: boolean): void => {
    if (!row || typeof row !== "object") return;
    const item = row as Dict;
    const id = text(item.id || item.agentId);
    const settled = settledBySource || SETTLED_STATUSES.includes(text(item.status));
    if (id && settled) ids.add(id);
  };
  (Array.isArray(value.progress) ? value.progress : []).forEach((row) => add(row, false));
  (Array.isArray(value.results) ? value.results : []).forEach((row) => add(row, true));
  return [...ids];
}

// A run-start or find-run answer (inflight_registry.py prints one JSON object). A step that
// printed none crashed; that is a refusal the run can retry, never a silent pass.
type RunAnswer = {
  ok: boolean;
  cause?: string;
  retryable?: boolean;
  message?: string;
  feature?: string;
  root?: string;
};

function parseRunAnswer(result: PolicyResult): RunAnswer {
  for (const line of result.stdout.split("\n").reverse()) {
    if (!line.trim().startsWith("{")) continue;
    try {
      const parsed = JSON.parse(line) as Dict;
      if (typeof parsed.ok === "boolean") return parsed as RunAnswer;
    } catch {
      continue;
    }
  }
  return {
    ok: false,
    cause: "claim-step-failed",
    retryable: true,
    message: result.reason || "inflight_registry.py printed no result",
  };
}

export function heldRunReason(refusal: RunAnswer): string {
  const retry = refusal.retryable
    ? "a retry can succeed once the cause clears"
    : "a retry cannot succeed until the operator acts";
  return `Harness run start refused: ${refusal.message} (cause: ${refusal.cause}; ${retry}). `
    + "Every tool is refused for this run; yield a BLOCKED digest that names this cause.";
}

const BLOCKED_VERDICT = /^VERDICT:\s*BLOCKED\b/m;
const MISSING_CAPABILITY = "Harness requires OMP's runtime lineage capability; install the "
  + "pinned Harness OMP build before dispatching agents or allowing governed mutations.";

// The assignment's feature: one HARNESS-FEATURE value across the prompt (DEC-204's grammar,
// now read where OMP delivers the assignment). Two different values are a conflict to refuse.
function promptFeature(prompt: unknown): { feature?: string; conflict?: string } {
  try {
    return { feature: detectMarker([text(prompt)], FEATURE_MARKER, "feature") };
  } catch (error) {
    return { conflict: (error as Error).message };
  }
}

// BUG-1724 (DEC-227): the tokens the host measured for one `task` call — the sum over
// every result carrying a non-negative integer `tokens`. `undefined` when none does, so
// the caller writes nothing rather than zero: null on the run means "unmeasured", and
// a host that reported nothing must leave it that way.
export function taskResultTokens(details: unknown): number | undefined {
  if (!details || typeof details !== "object") return undefined;
  const results = (details as Dict).results;
  if (!Array.isArray(results)) return undefined;
  let sum = 0;
  let measured = false;
  for (const row of results) {
    if (!row || typeof row !== "object") continue;
    const tokens = (row as Dict).tokens;
    if (typeof tokens === "number" && Number.isInteger(tokens) && tokens >= 0) {
      sum += tokens;
      measured = true;
    }
  }
  return measured ? sum : undefined;
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

// Release the one claim bound to runtime id `agentId`, in whichever registry holds it. A
// child that never governed (a scout, a sonic) holds none, and nothing is released for it.
function releaseRun(runner: PolicyRunner, cwd: string, agentId: string): void {
  const found = parseRunAnswer(runner(cwd, "inflight_registry.py", [
    "find-run", "--agent-id", agentId, "--root", cwd,
  ], {}));
  if (!found.ok || !found.feature || !found.root) return;
  runner(cwd, "inflight_registry.py", [
    "release",
    "--agent-id", agentId,
    "--feature", found.feature,
    "--root", found.root,
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
  let fd: number | undefined;
  try {
    // allocUnsafe and toString are INSIDE the guard on purpose. Both can throw on a
    // pathological span — over buffer.constants.MAX_LENGTH, or under memory pressure —
    // and an escaping throw here would propagate out of the advisory and skip the
    // postDomain check below it, turning an advisory failure into a SKIPPED GATE.
    const buffer = Buffer.allocUnsafe(span);
    fd = openSync(path, "r");
    readSync(fd, buffer, 0, span, start);
    return buffer.toString("utf8");
  } catch {
    return undefined;
  } finally {
    if (fd !== undefined) {
      try { closeSync(fd); } catch { /* nothing actionable */ }
    }
  }
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
function resolveBudgetNumber(root: string, key: string, fallback: number): number {
  try {
    const raw = readFileSync(join(root, ".harness", "harness.json"), "utf8");
    const budgets = (JSON.parse(raw) as Record<string, unknown>).budgets;
    if (budgets && typeof budgets === "object") {
      const value = (budgets as Record<string, unknown>)[key];
      if (typeof value === "number" && Number.isFinite(value)) return value;
    }
  } catch { /* every miss path falls through to the declared default */ }
  return fallback;
}

export function resolveContextWarnTokens(root: string): number {
  return resolveBudgetNumber(root, "orchestrator_context_warn_tokens", DEFAULT_CONTEXT_WARN_TOKENS);
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

// --- FEAT-59 SC-19: the SPEND advisory, on the same wake and in the same voice -----
//
// The figure is what `feature-record.py spend` MEASURES from feature.json's
// runs[].started_at/ended_at and tokens — never an estimate (SC-18). Before build
// entry the budget is budgets.plan_phase_warn_minutes against the whole feature so
// far; after it, the operator's own rework.wall_clock_minutes ruling against the
// REWORK WINDOW — `rework_minutes`, every run from the first validate-* onward —
// never against the whole, because the ruling is a budget for rework and the plan
// and build phases are not rework. With no ruling recorded nothing is said, because
// there is nothing to measure against. Strictly greater, like the context advisory:
// at or under the budget the wake costs zero extra tokens.

export const DEFAULT_PLAN_PHASE_WARN_MINUTES = 90;

export function resolvePlanPhaseWarnMinutes(root: string): number {
  return resolveBudgetNumber(root, "plan_phase_warn_minutes", DEFAULT_PLAN_PHASE_WARN_MINUTES);
}

export type SpendSummary = {
  runs: number;
  wall_clock_minutes: number;
  tokens: number | null;
  phase: "plan" | "build";
  rework_minutes: number;
  rework_rounds: number;
};

// The JSON `feature-record.py spend` prints, validated field by field: a stdout
// that does not carry exactly this shape yields no figure rather than a wrong one.
export function parseSpend(stdout: string): SpendSummary | undefined {
  let parsed: unknown;
  try {
    parsed = JSON.parse(stdout);
  } catch {
    return undefined;
  }
  if (!parsed || typeof parsed !== "object") return undefined;
  const record = parsed as Record<string, unknown>;
  const { runs, wall_clock_minutes: minutes, tokens, phase } = record;
  const rework = record.rework_minutes;
  const rounds = record.rework_rounds;
  if (typeof runs !== "number" || typeof minutes !== "number" || !Number.isFinite(minutes)) return undefined;
  if (typeof rework !== "number" || !Number.isFinite(rework)) return undefined;
  if (typeof rounds !== "number" || !Number.isFinite(rounds)) return undefined;
  if (tokens !== null && typeof tokens !== "number") return undefined;
  if (phase !== "plan" && phase !== "build") return undefined;
  return { runs, wall_clock_minutes: minutes, tokens, phase, rework_minutes: rework, rework_rounds: rounds };
}

// feature.json under either layout the checkout may use: `.harness/<repo>/features/`
// (repo-tier) or `.harness/features/` (flat). Undefined when neither holds one, which
// the caller reads as "nothing to measure yet" — the orchestrator instantiates the
// file on its first cycle.
export function featureJsonPath(root: string, feature: string): string | undefined {
  const harnessDir = join(root, ".harness");
  const candidates = [join(harnessDir, "features", feature, "feature.json")];
  try {
    for (const entry of readdirSync(harnessDir, { withFileTypes: true })) {
      if (entry.isDirectory()) candidates.push(join(harnessDir, entry.name, "features", feature, "feature.json"));
    }
  } catch {
    return undefined;
  }
  return candidates.find((candidate) => existsSync(candidate));
}

// The operator's rework ruling, or undefined when none is recorded (or the file is
// unreadable — both mean there is no build-phase budget to compare against).
export function readReworkMinutes(featureJson: string): number | undefined {
  try {
    const doc = JSON.parse(readFileSync(featureJson, "utf8")) as Record<string, unknown>;
    const rework = doc.rework;
    if (!rework || typeof rework !== "object") return undefined;
    const minutes = (rework as Record<string, unknown>).wall_clock_minutes;
    return typeof minutes === "number" && Number.isFinite(minutes) ? minutes : undefined;
  } catch {
    return undefined;
  }
}

export function spendAdvisoryText(
  minutes: number,
  tokens: number | null,
  phase: "plan" | "build",
  budgetKey: string,
  threshold: number,
): string {
  const ratio = (minutes / threshold).toFixed(2);
  const measured = tokens === null ? "" : ` and ${tokens} tokens`;
  return `SPEND: this feature measures ${minutes} wall-clock minutes${measured} in its ${phase} `
    + `phase against ${budgetKey} = ${threshold} (${ratio}x). This ADVISES and never refuses `
    + `(DEC-198). Weigh it yourself; whether you continue, downgrade or stop is a judgement to `
    + `record (SC-21), and a handoff belongs at a seam rather than mid-phase (DEC-201).`;
}

export function spendAdvisoryFor(
  spend: SpendSummary,
  reworkMinutes: number | undefined,
  planWarnMinutes: number,
): string | undefined {
  if (spend.phase === "plan") {
    return spend.wall_clock_minutes > planWarnMinutes
      ? spendAdvisoryText(spend.wall_clock_minutes, spend.tokens, "plan",
        "budgets.plan_phase_warn_minutes", planWarnMinutes)
      : undefined;
  }
  if (reworkMinutes === undefined) return undefined;
  return spend.rework_minutes > reworkMinutes
    ? spendAdvisoryText(spend.rework_minutes, spend.tokens, "build",
      "rework.wall_clock_minutes", reworkMinutes)
    : undefined;
}

export function registerHarnessHooks(pi: any, policyRunner: PolicyRunner = runPolicy): void {
  let currentAgent: string | undefined;
  let currentFeature: string | undefined;
  let expertiseInjected = false;
  let currentReviewPin: string | undefined;
  let currentMission: string | undefined;
  let dispatchCaptured = false;
  let claimsReconciled = false;
  let lastAssistantMessage = "";
  let runtimeAgentId = "";
  let runtimeParentAgentId = "";
  // BUG-1898: a governed run is unready until it holds a claim bound to its runtime id, and
  // held — every tool refused, only a BLOCKED yield allowed — when it cannot get one.
  let runGate: { state: "unready" | "ready" } | { state: "held"; reason: string } = {
    state: "unready",
  };
  // The lifecycle bus hands its listener no ctx; this is the checkout the session works in.
  let sessionCwd = process.cwd();
  // FEAT-44: once-per-session cap for BOTH notice classes (inert and accessor
  // failure). Setting it skips the whole advisory path on every later wake in
  // this session, the read included, so the full scan the widening ladder
  // degrades to is paid once per session rather than once per wake. Accepted
  // cost, disclosed in BRIEF.md: if the host recovers mid-session the advisory
  // does not return until the next session.
  let contextNoticeEmitted = false;
  // FEAT-59: the feature.json this session's spend is measured from, resolved once it
  // is found. Not cached while ABSENT — the orchestrator instantiates the file on its
  // first cycle, so an early miss must be retried on the next wake.
  let spendFeatureJson: string | undefined;
  // Dispatch receipts per task call. A receipt holds a governed slot across the spawn gap
  // and is released only once every child of its call has settled: by then a child that
  // started has bound it (and was released by its own id) or never touched it.
  const pendingTaskCalls = new Map<string, {
    receipts: ClaimReceipt[];
    total: number;
    settled: Set<string>;
  }>();
  const setFeature = (feature: string | undefined): void => {
    if (!feature) return;
    if (currentFeature && currentFeature !== feature) {
      throw new Error(`conflicting Harness feature markers: ${currentFeature}, ${feature}`);
    }
    currentFeature = feature;
  };

  // The pin and the mission have one source: the assignment message (DEC-204), scanned
  // once. A later user turn or a tool result echoing another dispatch is never either.
  const captureDispatchFromMessage = (candidate: unknown): void => {
    if (dispatchCaptured) return;
    if (!candidate || typeof candidate !== "object") return;
    if ((candidate as Dict).role !== "user") return;
    dispatchCaptured = true;
    const layers = [messageText(candidate)];
    const pin = detectMarker(layers, REVIEW_PIN_MARKER, "review pin");
    if (pin) currentReviewPin = pin;
    const mission = detectMarker(layers, MISSION_MARKER, "mission");
    if (mission) currentMission = mission;
  };

  // BUG-1898: where a governed run's feature comes from, in order — the feature this
  // session already runs (a wake), the assignment OMP delivers as the run's prompt (DEC-204:
  // identity is read from the assignment, never from later output), or, for a restart or
  // revival that carries no marker, the ONE live claim bound to this exact runtime id.
  // Never persona, dispatch name, cwd or session: a guess binds a run to a stranger.
  const resolveFeature = (ctx: { cwd: string }, prompt: unknown): RunAnswer => {
    if (currentFeature) return { ok: true };
    const assigned = promptFeature(prompt);
    if (assigned.conflict) {
      return { ok: false, cause: "feature-conflict", retryable: false, message: assigned.conflict };
    }
    setFeature(assigned.feature);
    if (currentFeature) return { ok: true };
    const found = parseRunAnswer(policyRunner(ctx.cwd, "inflight_registry.py", [
      "find-run", "--agent-id", runtimeAgentId, "--root", ctx.cwd,
    ], {}));
    if (found.ok) setFeature(found.feature);
    return found;
  };

  // The run-start claim (T-01's one locked step): reuse this id's claim, bind the unique
  // receipt its parent's dispatch left, or create one. A refusal holds the run.
  const startRun = (ctx: { cwd: string }, prompt: unknown): RunAnswer => {
    if (!runtimeAgentId || !runtimeParentAgentId) {
      return { ok: false, cause: "runtime-lineage", retryable: false, message: MISSING_CAPABILITY };
    }
    const feature = resolveFeature(ctx, prompt);
    if (!feature.ok) return feature;
    return parseRunAnswer(policyRunner(ctx.cwd, "inflight_registry.py", [
      "run-start",
      "--root", ctx.cwd,
      "--feature", String(currentFeature),
      "--agent", String(currentAgent),
      "--agent-id", runtimeAgentId,
      "--parent-agent-id", runtimeParentAgentId,
      "--supervisor-pid", String(process.pid),
    ], {}));
  };

  const heldReason = (): string =>
    runGate.state === "held"
      ? runGate.reason
      : "Harness run start has not completed; no tool runs before the run holds its claim.";

  // A child is released by its runtime id wherever its claim lives, and a call's receipts
  // once all of that call's children have settled.
  const settleRun = (callKey: string | undefined, agentId: string, cwd: string): void => {
    releaseRun(policyRunner, cwd, agentId);
    const pending = callKey ? pendingTaskCalls.get(callKey) : undefined;
    if (!pending) return;
    pending.settled.add(agentId);
    if (pending.settled.size < pending.total) return;
    pendingTaskCalls.delete(String(callKey));
    pending.receipts.forEach((receipt) => releaseClaim(policyRunner, cwd, receipt));
  };

  pi.on("before_agent_start", async (event: Dict, ctx: any) => {
    const detected = detectHarnessAgent(event.systemPrompt);
    const detectedFeature = detectMarker(event.systemPrompt, FEATURE_MARKER, "feature");
    const detectedPin = detectMarker(event.systemPrompt, REVIEW_PIN_MARKER, "review pin");
    const detectedMission = detectMarker(event.systemPrompt, MISSION_MARKER, "mission");
    runtimeAgentId = text(ctx.agentId);
    runtimeParentAgentId = text(ctx.parentAgentId);
    sessionCwd = text(ctx.cwd) || sessionCwd;
    if (detected) currentAgent = detected;
    if (detectedPin) currentReviewPin = detectedPin;
    if (detectedMission) currentMission = detectedMission;
    setFeature(detectedFeature);
    if (!currentAgent) return;
    runGate = { state: "unready" };
    const started = startRun(ctx, event.prompt);
    if (!started.ok) {
      runGate = { state: "held", reason: heldRunReason(started) };
      return {
        message: {
          customType: "harness-run-refused",
          content: runGate.reason,
          display: true,
          details: { agent: currentAgent, cause: started.cause, retryable: started.retryable },
          attribution: "harness",
        },
      };
    }
    runGate = { state: "ready" };
    // Only once the run holds its claim: reconcile's locked writer reads a corrupt registry
    // as empty and rewrites it, which would erase the very file a refusal leaves as found.
    if (!claimsReconciled) {
      policyRunner(ctx.cwd, "inflight_registry.py", [
        "reconcile",
        "--feature", String(currentFeature),
        "--root", ctx.cwd,
      ], {});
      claimsReconciled = true;
    }
    if (expertiseInjected) return;

    const result = policyRunner(ctx.cwd, "inject-expertise.py", [], {
      ...basePayload(currentAgent, "SubagentStart", ctx.cwd, ctx),
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
      throw new Error("inject-expertise.py returned invalid JSON");
    }
  });

  pi.on("message_update", async (event: Dict) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    captureDispatchFromMessage(candidate);
    const found = lastAssistantText([candidate]);
    if (found.trim()) lastAssistantMessage = found;
  });

  pi.on("message_end", async (event: Dict) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    captureDispatchFromMessage(candidate);
    const found = lastAssistantText([candidate]);
    if (found.trim()) lastAssistantMessage = found;
  });

  pi.on("tool_call", async (event: Dict, ctx: any) => {
    const toolName = text(event.toolName);
    const input = (event.input && typeof event.input === "object" ? event.input : {}) as Dict;
    const agentId = runtimeAgentId;
    const parentAgentId = runtimeParentAgentId;
    const runtimeCtx = { ...ctx, agentId, parentAgentId };
    const mutates = ["write", "edit", "bash"].includes(toolName);
    sessionCwd = text(ctx.cwd) || sessionCwd;
    if (toolName === "task" && !agentId) {
      return { block: true, reason: MISSING_CAPABILITY };
    }
    // BUG-1898: a governed run that holds no claim of its own runs nothing but a yield.
    if (currentAgent && runGate.state !== "ready" && toolName !== "yield") {
      return { block: true, reason: heldReason() };
    }
    const ompMainTask = !currentAgent
      && toolName === "task"
      && agentId === "Main"
      && !parentAgentId;
    if (!currentAgent && !ompMainTask) return;
    const policyAgent = currentAgent || "Main";
    let revisedInput: Dict | undefined;
    let reason: string | undefined;
    if (mutates) {
      if (!currentFeature) {
        reason = "Harness child mutation policy requires runtime child, parent, and feature identity.";
      } else {
        const authorization = policyRunner(ctx.cwd, "inflight_registry.py", [
          "authorize",
          "--agent", policyAgent,
          "--feature", currentFeature,
          "--agent-id", agentId,
          "--parent-agent-id", parentAgentId,
          "--root", ctx.cwd,
        ], {});
        if (authorization.blocked || authorization.reason) {
          reason = authorization.reason || "Harness runtime child lineage is not authorized.";
        }
      }
    }
    if (!reason) {
      reason = firstBlock(preDomain(
        ctx.cwd, policyAgent, toolName, input, policyRunner, runtimeCtx,
      ));
    }
    if (!reason && toolName === "bash") {
      const payload = {
        ...basePayload(policyAgent, "PreToolUse", ctx.cwd, runtimeCtx),
        tool_name: "Bash",
        tool_input: { command: input.command },
      };
      // BUG-1132: plan-sign-gate.py (REQ-05/DEC-120 — only the main session signs an approval)
      // was wired into `.claude/settings.json` for native Claude Code but never ported here, so
      // a `plan-merge.py sign-approval` Bash call under OMP reached no denylist at all — not
      // merely the evadable one #1103 documents. `cmd_sign_approval` itself has no identity
      // check (that is #1103's own scope), so this script was the ONLY thing standing between
      // an agent and forging a signature, and on this host it was never invoked.
      reason = firstBlock([
        policyRunner(ctx.cwd, "gh-close-gate.py", [], payload),
        policyRunner(ctx.cwd, "branch-create-gate.py", [], payload),
        policyRunner(ctx.cwd, "bash-write-guard.py", [], payload),
        policyRunner(ctx.cwd, "plan-sign-gate.py", [], payload),
        policyRunner(ctx.cwd, "merge-gate.py", [], payload),
      ]);
      // #1103: the identity signal cmd_sign_approval (plan-merge.py) now checks on its own,
      // rather than only the text-parsing denylist above. This is the SAME `currentAgent` the
      // payload just carried to every one of those four scripts — never derived from `command`,
      // never settable by the command itself. MERGED into any env the agent's own command
      // already specified, never replacing it: an agent's own `env` choices for its command are
      // its business; this is the one key it does not get to author.
      if (!reason) {
        const existingEnv = (input.env && typeof input.env === "object" ? input.env : {}) as Dict;
        revisedInput = { ...input, env: { ...existingEnv, HARNESS_AGENT_TYPE: policyAgent } };
      }
    }
    if (!reason && toolName === "task") {
      reason = ompMainTask ? undefined : taskModelOverride(input);
      const receipts: ClaimReceipt[] = [];
      if (!reason) {
        for (const dispatch of normalizeTaskDispatches(input)) {
          const result = policyRunner(ctx.cwd, "dispatch-guard.py", [], {
            ...basePayload(policyAgent, "PreToolUse", ctx.cwd, ctx),
            tool_name: "Task",
            tool_input: dispatch,
            harness_runtime: "omp",
            supervisor_pid: process.pid,
          });
          if (result.blocked) {
            receipts.forEach((receipt) => releaseClaim(policyRunner, ctx.cwd, receipt));
            reason = result.reason || "Harness dispatch policy denied the task.";
            break;
          }
          // DEC-100: ONLY exit 2 BLOCKS. dispatch-guard.py exits 0 WITHOUT printing a
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
          // BUG-1898: the receipt learns only its dispatching parent. Which run takes it is
          // decided when a child STARTS, by that child's own runtime id (T-01 run-start) —
          // never by a dispatch name, which is not the id OMP gives the child.
          const receipt = parseClaimReceipt(result.stdout);
          if (receipt) {
            receipts.push(receipt);
            const parentAgentId = text(ctx.agentId);
            if (parentAgentId) {
              const args = [
                "attach",
                "--agent", receipt.agent,
                "--feature", receipt.feature,
                "--claim-id", receipt.claimId,
                "--parent-agent-id", parentAgentId,
                "--root", receipt.root,
              ];
              const attached = policyRunner(
                ctx.cwd, "inflight_registry.py", args, {},
              );
              if (attached.blocked || attached.reason) {
                receipts.forEach((claimed) =>
                  releaseClaim(policyRunner, ctx.cwd, claimed));
                receipts.length = 0;
                reason = attached.reason || "Harness could not bind the child runtime lineage.";
                break;
              }
            }
          } else {
            debug(`dispatch-guard allowed ${dispatch.agent} with no claim recorded`);
          }
        }
      }
      if (!reason && receipts.length) {
        pendingTaskCalls.set(text(event.toolCallId) || "task", {
          receipts,
          total: normalizeTaskDispatches(input).length,
          settled: new Set(),
        });
      }
    }
    if (!reason && toolName === "yield") {
      const normalized = normalizeYieldInput(input, lastAssistantMessage);
      const payload = ("data" in normalized || "error" in normalized)
        ? normalized : normalized.result;
      const contract = yieldContractText(payload, lastAssistantMessage);
      // The two outcomes #1676 asks to tell apart. No fallback and no payload: nothing
      // was produced, and the block below says so. A payload repaired from the assistant
      // text: a digest WAS produced and the envelope dropped it — repaired here, named
      // under HARNESS_HOOK_DEBUG, so the host never sees the null-data yield at all.
      if (normalized !== input) {
        debug(`yield agent=${currentAgent} envelope carried no data; repaired from the last assistant message`);
      }
      if (!contract.trim()) {
        reason = "Harness agents must yield a VERDICT, DIGEST, and artifact; no digest was produced — neither the yield payload nor the last assistant message carries one.";
      } else if (currentAgent && runGate.state !== "ready" && !BLOCKED_VERDICT.test(contract)) {
        reason = `${heldReason()} This run may yield only a BLOCKED digest.`;
      } else {
        const result = policyRunner(ctx.cwd, "validate-digest.py", ["--hook"], {
          ...basePayload(policyAgent, "SubagentStop", ctx.cwd, runtimeCtx),
          stop_hook_active: false,
          last_assistant_message: contract,
          harness_feature: currentFeature,
          harness_review_pin: currentReviewPin,
          harness_mission: currentMission,
        });
        debug(`yield agent=${currentAgent} value=${contract.slice(0, 500)}`);
        debug(`yield verdict blocked=${result.blocked} reason=${result.reason || "none"}`);
        reason = result.blocked ? result.reason : undefined;
        if (!reason && normalized !== input) revisedInput = normalized;
      }
    }
    if (reason) return { block: true, reason };
    if (revisedInput) return { input: revisedInput };
  });

  pi.on("tool_result", async (event: Dict, ctx: any) => {
    const toolName = text(event.toolName);
    const ompMainTask = !currentAgent
      && toolName === "task"
      && text(ctx.agentId) === "Main"
      && !text(ctx.parentAgentId);
    if (!currentAgent && !ompMainTask) return;
    const policyAgent = currentAgent || "Main";
    const input = (event.input && typeof event.input === "object" ? event.input : {}) as Dict;
    if (toolName === "task") {
      const key = text(event.toolCallId) || "task";
      sessionCwd = text(ctx.cwd) || sessionCwd;
      if (event.isError) {
        // The call failed as a whole: no child of it ran, so its receipts are released.
        const pending = pendingTaskCalls.get(key);
        pendingTaskCalls.delete(key);
        pending?.receipts.forEach((receipt) => releaseClaim(policyRunner, ctx.cwd, receipt));
      } else {
        settledRunIds(event.details).forEach((agentId) => settleRun(key, agentId, ctx.cwd));
      }
    }
    // FEAT-44: computed BEFORE the early return below. That return fires whenever
    // there is no block reason, which is the common case for a task result, so an
    // advisory computed after it would never be emitted at all.
    const advisories: string[] = [];
    if (currentAgent === "harness-orchestrator" && toolName === "task" && !contextNoticeEmitted) {
      // THE ADVISORY MUST NEVER COST A GATE. This whole block sits above the postDomain
      // call, so anything escaping it would skip `check-domain.py --post` — an advisory
      // failure silently disabling an enforcement check. Every branch inside already
      // returns rather than throws, and readTailBytes now guards its allocation too, but
      // this catch is what makes "the advisory cannot break the gate" a property of the
      // structure rather than of every branch staying correct forever.
      try {
        // resolveSessionFile, not an inline try/catch: inside this gate a throw can
        // only mean the accessor moved, and collapsing that into "nothing to report"
        // is the silent-undefined shape issue #923 exists to fix. The sessionId
        // helper above is deliberately NOT the model here.
        const resolved = resolveSessionFile(ctx);
        if (resolved.kind === "failed") {
          advisories.push(contextAccessorFailureText(resolved.accessor));
          contextNoticeEmitted = true;
        } else if (resolved.kind === "path") {
          const anchor = readContextAnchor(resolved.path);
          if (anchor.kind === "inert") {
            // Both arguments come out of the result; no field name is written here,
            // so the notice can never name a field the parse did not look for.
            advisories.push(contextInertText(anchor.scannedBytes, anchor.field));
            contextNoticeEmitted = true;
          } else if (anchor.kind === "tokens") {
            const threshold = resolveContextWarnTokens(gateRoot());
            // Strictly greater: at or under the threshold nothing is added, which is
            // REQ-01's zero-extra-token promise on the healthy path.
            if (anchor.tokens > threshold) {
              advisories.push(contextAdvisoryText(anchor.tokens, threshold));
            }
          }
        }
        // kind "absent" is the legitimate no-session-yet case: no advisory, no notice.
      } catch {
        // no figure, and the gate below still runs
      }
    }
    // FEAT-59 SC-19: the SPEND advisory, on the same wake. Independent of the context
    // notice cap above — that cap is about a host record shape this path never reads.
    // The same non-blocking structure: one try around the whole measurement, so a
    // missing script, an unreadable file or a malformed stdout yields no line and the
    // gate below still runs. The figure comes from `feature-record.py spend`, which is
    // the ONE reader of runs[].started_at/ended_at/tokens; this hook parses its output
    // and never re-derives the sum.
    if (currentAgent === "harness-orchestrator" && toolName === "task" && currentFeature) {
      try {
        if (!spendFeatureJson) {
          // The same resolution the reconcile call makes: the checkout assigned to this
          // feature, which may be a worktree rather than ctx.cwd.
          const rooted = policyRunner(ctx.cwd, "inflight_registry.py", [
            "feature-root", "--feature", currentFeature, "--root", ctx.cwd,
          ], {});
          const featureRoot = rooted.stdout.trim().split("\n").pop() || "";
          if (featureRoot) spendFeatureJson = featureJsonPath(featureRoot, currentFeature);
        }
        if (spendFeatureJson) {
          // BUG-1724: stamp what the host measured onto the open run BEFORE spend reads
          // it, so the figure the orchestrator was asked to transcribe (and never did,
          // 0 of 26 times on BUG-285) is written by the host that computed it. A refusal
          // (no open run, two open runs) is stamp-tokens' own exit 2 and costs nothing
          // here: spend still runs and the gate below is untouched.
          const tokens = taskResultTokens(event.details);
          if (tokens !== undefined) {
            policyRunner(ctx.cwd, "feature-record.py", [
              "stamp-tokens", "--file", spendFeatureJson, "--tokens", String(tokens),
            ], {});
          }
          const measured = policyRunner(ctx.cwd, "feature-record.py", [
            "spend", "--file", spendFeatureJson,
          ], {});
          const spend = parseSpend(measured.stdout);
          if (spend) {
            const line = spendAdvisoryFor(
              spend, readReworkMinutes(spendFeatureJson), resolvePlanPhaseWarnMinutes(gateRoot()),
            );
            if (line) advisories.push(line);
          }
        }
      } catch {
        // no figure, and the gate below still runs
      }
    }
    // S2 (stale-anchor hazard, 2026-08-30) — MAKE THE ZERO-PATH CASE OBSERVABLE.
    // postDomain's edit branch maps over extractEditPaths, so an empty extraction
    // spawns no runner at all: no error, no stderr, no exit code. That is
    // byte-for-byte indistinguishable from a gate that ran and passed, and the
    // indistinguishability is the mechanism that made the feature.json corruption
    // silent. This does not restore the check — the path is unknown, so there is
    // nothing to check — it states the absence instead of hiding it.
    //
    // NON-BLOCKING BY CONSTRUCTION, not by care: it only ever appends to `advisories`,
    // and the composition below appends those with NO isError key. It cannot cost a
    // gate.
    if (toolName === "edit" && extractEditPaths(input.input).length === 0) {
      // NAMES BOTH GATES. preDomain's edit branch has the identical `.map()`, so a
      // zero extraction skips the PRE (blocking) check too — and that one is worse,
      // because it is preventive: the edit lands unchecked rather than merely
      // unreported. Measured 2026-08-30: preDomain returns no block and spawns no
      // check-domain.py at all. An earlier wording said only "post-write", which
      // understated the skip by exactly the gate that matters more.
      advisories.push("Harness: no target path could be extracted from this edit, so "
        + "neither the pre-write nor the post-write shape check ran on any file. "
        + "This is a notice, not a refusal.");
    }
    const reason = firstBlock(postDomain(
      ctx.cwd, policyAgent, toolName, input, policyRunner, ctx,
    ));
    const content = Array.isArray(event.content) ? event.content : [];
    const appended = advisories.map((advisoryText) => ({ type: "text", text: advisoryText }));
    if (!reason) {
      if (appended.length === 0) return;
      // No isError key AT ALL: a normal tool result must not become an error.
      return { content: [...content, ...appended] };
    }
    return {
      content: [...content, { type: "text", text: `Harness post-write check: ${reason}` }, ...appended],
      isError: true,
    };
  });

  // BUG-1898 defect D: OMP publishes a child's lifecycle on the session EventBus — the
  // `pi.events` an extension holds — for a first run and for every message-woken turn
  // alike. `pi.on` is the hook dispatcher and never carried it, so no child was ever
  // released here. A settled child is released by its own runtime id and nothing else.
  pi.events.on("task:subagent:lifecycle", (data: unknown) => {
    const event = (data && typeof data === "object" ? data : {}) as Dict;
    const agentId = text(event.id);
    if (!agentId || !SETTLED_STATUSES.includes(text(event.status))) return;
    settleRun(text(event.parentToolCallId) || undefined, agentId, sessionCwd);
  });

  pi.on("agent_end", async (event: Dict, ctx: any) => {
    if (!currentAgent) return;
    const finalText = lastAssistantText(event.messages);
    if (!finalText.trim()) return;
    // Notification-only backstop. Normal task agents are validated on `yield`.
    const result = policyRunner(ctx.cwd, "validate-digest.py", ["--hook"], {
      ...basePayload(currentAgent, "SubagentStop", ctx.cwd, ctx),
      stop_hook_active: true,
      last_assistant_message: finalText,
      harness_feature: currentFeature,
      harness_review_pin: currentReviewPin,
      harness_mission: currentMission,
    });
    if (result.reason && result.blocked) ctx.ui?.notify?.(result.reason, "warning");
  });
}

export default function harnessHooks(pi: any): void {
  registerHarnessHooks(pi);
}
