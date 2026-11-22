import { type ChildProcess, spawn, spawnSync } from "node:child_process";
import { closeSync, existsSync, lstatSync, openSync, readdirSync, readFileSync, readSync, realpathSync, statSync, type Stats } from "node:fs";
import { isAbsolute, join } from "node:path";
import { fileURLToPath } from "node:url";
import { isDeepStrictEqual } from "node:util";
import { DigestSchemaBundleError, loadDigestSchemaBundle } from "./digest-schema.ts";

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
// `unavailable` (FEAT-2274, D-01): a broad gate could not run, so nothing was checked. It is
// never a block; the handler reports it as passive context naming the gate.
type PolicyResult = { blocked: boolean; reason?: string; unavailable?: string; stdout: string };
// FEAT-2337 (D-01): every policy answer is awaited. Nothing reads a gate's answer before it
// arrives, and the host's event loop keeps running while the process does.
type PolicyRunner = (
  cwd: string,
  script: string,
  args: string[],
  payload: Dict,
) => Promise<PolicyResult>;

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

// One matcher for an edit's targets, a section header `[path#HASH]` or an `MV dest` line, read
// by extraction (the domain gates) and by BUG-1016's rooting alike, so the two can never
// disagree on which lines name a file. Body rows start with `+` and never match.
const EDIT_TARGET = /^(?:\[([^#\r\n]+)#([0-9A-F]{4})\]|MV (.+))$/gm;

export function extractEditPaths(input: unknown): string[] {
  if (typeof input !== "string") return [];
  const sections: string[] = [];
  const moves: string[] = [];
  for (const match of input.matchAll(EDIT_TARGET)) {
    const path = (match[1] ?? match[3]).trim().replace(/^"(.*)"$/, "$1");
    if (path) (match[1] === undefined ? moves : sections).push(path);
  }
  return [...new Set([...sections, ...moves])];
}

function text(value: unknown): string {
  if (typeof value === "string") return value;
  if (value === undefined) return "";
  return JSON.stringify(value);
}

// A gate's machine-readable answer is one JSON object on one stdout line; every other line
// is diagnostic text. Each caller keeps only its own predicate over these objects.
function jsonLines(stdout: string): Dict[] {
  const objects: Dict[] = [];
  for (const line of stdout.split("\n")) {
    if (!line.trim().startsWith("{")) continue;
    try {
      objects.push(JSON.parse(line) as Dict);
    } catch {
      // Non-JSON diagnostic output is handled by the script exit code.
    }
  }
  return objects;
}

function parseDecision(stdout: string): string | undefined {
  for (const data of jsonLines(stdout)) {
    const hook = data.hookSpecificOutput as Dict | undefined;
    if (hook?.permissionDecision === "deny") {
      return text(hook.permissionDecisionReason) || "Harness policy denied the operation.";
    }
    if (data.decision === "block") return text(data.reason) || "Harness policy denied the operation.";
  }
  return undefined;
}

// --- FEAT-2274 (C2/C3): the extension's reading of the three narrow gates' commands ---------
//
// Consulted ONLY when a narrow gate's own process could not run, to decide whether the command
// was one it guards (refuse) or not (allow silently). Each matcher mirrors its Python gate's at
// 1e0b014 — gh-close-gate `denies`, branch-create-gate `_branch_name`, plan-sign-gate `denies` —
// and agreement is held by the shared spelling corpora, not by a shared dependency.

// Python's `shlex.shlex(line, posix=True, punctuation_chars=True)` with `whitespace_split`, the
// tokenizer both Python gates read a command with: quotes resolved, `#` comments dropped, runs of
// `();<>|&` split out and then discarded as operators. Undefined where shlex raises (an unclosed
// quote, a trailing escape), which sends the caller to its text fallback as the gate does.
const SHELL_WHITESPACE = " \t\r\n";
const SHELL_PUNCTUATION = "();<>|&";
const SHELL_OPERATORS = [";", "&", "&&", "|", "||", "(", ")", "<", ">", ">>", "\n"];

function shellWords(line: string): string[] | undefined {
  const words: string[] = [];
  let index = 0;
  let pushback = "";
  const read = (): string => {
    const char = pushback || (index < line.length ? line[index++] : "");
    pushback = "";
    return char;
  };
  const skipComment = (): void => {
    const end = line.indexOf("\n", index);
    index = end < 0 ? line.length : end + 1;
  };
  for (let atEnd = false; !atEnd;) {
    let state = " ";
    let token = "";
    let quoted = false;
    let escapedState = " ";
    for (;;) {
      const char = read();
      if (state === " ") {
        if (!char) { atEnd = true; break; }
        if (SHELL_WHITESPACE.includes(char)) continue;
        if (char === "#") skipComment();
        else if (char === "\\") { escapedState = "a"; state = char; }
        else if (SHELL_PUNCTUATION.includes(char)) { token = char; state = "c"; }
        else if (char === "'" || char === '"') state = char;
        else { token = char; state = "a"; }
      } else if (state === "'" || state === '"') {
        quoted = true;
        if (!char) return undefined;
        if (char === state) state = "a";
        else if (char === "\\" && state === '"') { escapedState = state; state = char; }
        else token += char;
      } else if (state === "\\") {
        if (!char) return undefined;
        // Inside double quotes only the quote and the escape itself may be escaped.
        if ((escapedState === "'" || escapedState === '"') && char !== "\\" && char !== escapedState) token += "\\";
        token += char;
        state = escapedState;
      } else {
        if (!char) { atEnd = true; break; }
        if (SHELL_WHITESPACE.includes(char)) { state = " "; break; }
        if (char === "#") { skipComment(); state = " "; break; }
        if (state === "c") {
          if (SHELL_PUNCTUATION.includes(char)) { token += char; continue; }
          pushback = char;
          state = " ";
          break;
        }
        if (char === "'" || char === '"') state = char;
        else if (char === "\\") { escapedState = "a"; state = char; }
        else if (SHELL_PUNCTUATION.includes(char)) { pushback = char; state = " "; break; }
        else token += char;
      }
    }
    if (!token && !quoted) break;
    words.push(token);
  }
  return words.filter((word) => !SHELL_OPERATORS.includes(word));
}

// The command a token names: `os.path.basename(tok.strip("\\'\"$()`"))`.
const commandName = (token: string): string =>
  token.replace(/^[\\'"$()`]+|[\\'"$()`]+$/g, "").split("/").pop() ?? "";

// Python's `str.split()` word count: a token that still reads as a command line is re-scanned.
const carriesCommandLine = (token: string): boolean =>
  token.split(/[\s\x1c-\x1f\x85]+/).filter(Boolean).length >= 3;

const NESTED_DEPTH = 3;

// gh-close-gate.py `denies`: `gh issue close`, or a `gh api` call that closes an issue.
const GH_ISSUE_PATH = /repos\/[^/\s]+\/[^/\s]+\/issues\/\p{Nd}+/u;
const GH_RAW_CLOSE = /(^|[;&|(]|\s)gh\s+issue\s+close(\s|$)/;
const GH_RAW_API = /(^|[;&|(]|\s)gh\s+api(\s|$)/;
const GH_RAW_STATE = /state=["']?closed/;
const GH_MUTATES = ["PATCH", "POST", "PUT", "DELETE"];

function ghApiCloses(rest: string[]): boolean {
  const joined = rest.join(" ");
  if (joined.includes("closeIssue")) return true;
  if (!GH_ISSUE_PATH.test(joined)) return false;
  if (joined.includes("state=closed")) return true;
  return rest.includes("--input") || rest.some((argument, index) =>
    (argument === "-X" || argument === "--method")
    && index + 1 < rest.length && GH_MUTATES.includes(rest[index + 1].toUpperCase()));
}

function ghCloses(line: string, depth = 0): boolean {
  const tokens = shellWords(line);
  if (!tokens) {
    return GH_RAW_CLOSE.test(line)
      || (GH_RAW_API.test(line) && GH_ISSUE_PATH.test(line) && GH_RAW_STATE.test(line));
  }
  const direct = tokens.some((token, index) => {
    if (commandName(token) !== "gh") return false;
    const rest = tokens.slice(index + 1);
    return (rest[0] === "issue" && rest[1] === "close") || (rest[0] === "api" && ghApiCloses(rest));
  });
  return direct || (depth < NESTED_DEPTH
    && tokens.some((token) => carriesCommandLine(token) && ghCloses(token, depth + 1)));
}

// branch-create-gate.py `_branch_name`: a detector per creation form, then its name extractor.
// Python's `.` never crosses a newline; `[^\n]` keeps that where JavaScript's `.` would differ.
const BRANCH_FORMS: Array<[RegExp, RegExp, number]> = [
  [/git( +-[cC] +[^ ]+)* +checkout +([^;&|]* )?-[bB]/, /[^\n]*checkout +([^;&|]* )?-[bB] *=?([^ ;&|]+)[^\n]*/, 2],
  [/git( +-[cC] +[^ ]+)* +switch +([^;&|]* )?(-[cC]|--create)/, /[^\n]*switch +([^;&|]* )?(-[cC]|--create) *=?([^ ;&|]+)[^\n]*/, 3],
  [/git +worktree +add +([^;&|]* )?-[bB]/, /[^\n]*worktree +add +([^;&|]* )?-[bB] *=?([^ ;&|]+)[^\n]*/, 2],
  [/git( +-[cC] +[^ ]+)* +branch +[^ -]/, /[^\n]*git( +-[cC] +[^ ]+)* +branch +([^ ;&|-][^ ;&|]*)[^\n]*/, 2],
];

function createsBranch(command: string): boolean {
  const form = BRANCH_FORMS.find(([detector]) => detector.test(command));
  return Boolean(form && form[1].exec(command)?.[form[2]]);
}

// plan-sign-gate.py `denies`: a main-session-only verb of a gated tool, or the tool reached
// through a wrapper whose argv the gate cannot read.
const SIGN_GATED: Record<string, string[]> = {
  "plan-merge.py": ["sign-approval"],
  "feature-record.py": ["raise-cycles", "set-rework"],
};
const SIGN_RAW = Object.entries(SIGN_GATED).map(([tool, verbs]) => {
  const escape = (value: string) => value.replace(/[.*+?^${}()|[\]\\-]/g, "\\$&");
  return new RegExp(`${escape(tool)}["'\\s]+(?:--["'\\s]+)*(${verbs.map(escape).join("|")})(\\s|$)`);
});
const SIGN_INDIRECT = ["xargs", "parallel"];
const SIGN_INTERPRETERS = ["python", "python3", "python2", "env", "nice", "time", "nohup", "stdbuf"];
const isSignTool = (token: string): boolean => Object.hasOwn(SIGN_GATED, commandName(token));

// `as_bash_reads_it`: rejoin continued lines, and treat every `$(...)`, backtick and braced
// expansion as the whitespace it may become. An unclosed `$(` consumes the rest of the line.
function asBashReadsIt(line: string): string {
  const joined = line.replace(/\\\r?\n/g, "");
  let out = "";
  for (let index = 0; index < joined.length;) {
    if (joined.startsWith("$(", index)) {
      out += " ";
      let depth = 0;
      let end = joined.length + 1;
      for (let scan = index + 1; scan < joined.length; scan += 1) {
        if (joined[scan] === "(") depth += 1;
        else if (joined[scan] === ")") depth -= 1;
        if (depth === 0) { end = scan + 1; break; }
      }
      index = end;
    } else if (joined[index] === "`") {
      out += " ";
      const end = joined.indexOf("`", index + 1);
      index = end < 0 ? joined.length : end + 1;
    } else {
      out += joined[index];
      index += 1;
    }
  }
  return out.replace(/"?\$\{[^{}]*\}"?/g, " ");
}

function signToolIndirectly(tokens: string[]): boolean {
  return tokens.some((token, index) => {
    if (commandName(token) === "find") {
      return tokens.slice(index + 1).some((flag, offset) =>
        (flag === "-exec" || flag === "-execdir")
        && tokens.slice(index + offset + 2, index + offset + 4).some(isSignTool));
    }
    if (!SIGN_INDIRECT.includes(commandName(token))) return false;
    let rest = tokens.slice(index + 1);
    while (rest.length && rest[0].startsWith("-")) rest = rest.slice(1);
    if (rest.length && SIGN_INTERPRETERS.includes(commandName(rest[0]))) rest = rest.slice(1);
    return rest.length > 0 && isSignTool(rest[0]);
  });
}

function signsAsMain(raw: string, depth = 0): boolean {
  const line = asBashReadsIt(raw);
  const tokens = shellWords(line);
  if (!tokens) return SIGN_RAW.some((pattern) => pattern.test(line));
  if (signToolIndirectly(tokens)) return true;
  const direct = tokens.some((token, index) => {
    if (!isSignTool(token)) return false;
    let at = index + 1;
    while (tokens[at] === "--") at += 1;
    return at < tokens.length && SIGN_GATED[commandName(token)].includes(tokens[at]);
  });
  return direct || (depth < NESTED_DEPTH
    && tokens.some((token) => carriesCommandLine(token) && signsAsMain(token, depth + 1)));
}

const NARROW_GATES: Record<string, (command: string) => boolean> = {
  "gh-close-gate.py": (command) => ghCloses(command),
  "branch-create-gate.py": createsBranch,
  "plan-sign-gate.py": (command) => signsAsMain(command),
};

// Whether `command` is one the narrow gate `script` guards. False for any other script.
export function narrowGateApplies(script: string, command: string): boolean {
  return Object.hasOwn(NARROW_GATES, script) && NARROW_GATES[script](command);
}

// The four gates whose own failure is reported rather than enforced (DEC-100, amended by D-01).
const BROAD_GATES = ["check-domain.py", "bash-write-guard.py", "dispatch-guard.py", "validate-digest.py"];

// How a gate process ended; `error` is a spawn failure, `timedOut` a kill at the budget.
export type PolicyProcess = {
  status: number | null;
  signal?: string | null;
  stdout?: string | null;
  stderr?: string | null;
  error?: Error;
  timedOut?: boolean;
};

function failureDetail(proc: PolicyProcess, stderr: string): string {
  if (proc.timedOut) return `exceeded its ${POLICY_TIMEOUT_MS / 1000}-second budget and was killed`;
  if (proc.error) return `could not be started: ${proc.error.message}`;
  if (proc.signal) return `was terminated by ${proc.signal}`;
  if (proc.status === null) return "ended with no exit status";
  const last = stderr.split("\n").map((line) => line.trim()).filter(Boolean).pop();
  return `exited ${proc.status}${last ? `: ${last}` : ""}`;
}

// One gate process's answer. A structured deny or exit 2 is a refusal from every script. Past
// that, a broad gate's declared or apparent failure (any other exit, a signal, no start) is
// `unavailable`; a narrow gate's failure refuses only a command it guards; every other script
// keeps its non-blocking error contract, and a spawn error still throws from it.
export function classifyPolicyRun(script: string, payload: Dict, proc: PolicyProcess): PolicyResult {
  const stdout = proc.stdout || "";
  const stderr = (proc.stderr || "").trim();
  const structuredReason = parseDecision(stdout);
  if (structuredReason) return { blocked: true, reason: structuredReason, stdout };
  if (proc.status === 2) {
    return { blocked: true, reason: stderr || `${script} denied the operation.`, stdout };
  }
  const gate = script.replace(/\.py$/, "");
  const failed = proc.error !== undefined || proc.status !== 0;
  if (BROAD_GATES.includes(script)) {
    const declared = jsonLines(stdout).find((line) => line.decision === "unavailable");
    if (declared) {
      const why = text(declared.reason) || "no reason given";
      return { blocked: false, unavailable: why.includes(gate) ? why : `${gate}: ${why}`, stdout };
    }
    return failed
      ? { blocked: false, unavailable: `${gate} ${failureDetail(proc, stderr)}`, stdout }
      : { blocked: false, stdout };
  }
  if (failed && Object.hasOwn(NARROW_GATES, script)) {
    const command = text(((payload as Dict | undefined)?.tool_input as Dict | undefined)?.command);
    if (!narrowGateApplies(script, command)) return { blocked: false, stdout };
    return {
      blocked: true,
      reason: `${gate}: BLOCKED — the gate could not run (${failureDetail(proc, stderr)}); `
        + "the command it guards is refused rather than left unchecked.",
      stdout,
    };
  }
  if (proc.error) throw proc.error;
  if (proc.timedOut) return { blocked: false, reason: `${script} ${failureDetail(proc, stderr)}`, stdout };
  if (proc.status !== 0) {
    // Preserve each existing policy script's non-blocking error contract. Safety-
    // critical internal failures are converted to exit 2 inside those scripts.
    return { blocked: false, reason: stderr || `${script} exited ${proc.status}`, stdout };
  }
  return { blocked: false, stdout };
}

// FEAT-2337 (D-01, DEC-100): the one budget a Python policy process gets, the same 30 seconds as
// validate-digest's HOOK_HANG_BUDGET_S. Not configurable: no harness.json key, no environment
// override. Past it the process and everything it started are killed and the answer is a
// timeout, which classifyPolicyRun reads like any other failure to run.
export const POLICY_TIMEOUT_MS = 30_000;

function killGroup(pid: number | undefined): void {
  if (pid === undefined) return;
  try {
    process.kill(-pid, "SIGKILL");
  } catch {
    // The group is already gone.
  }
}

// One policy process, settled exactly once by whichever comes first: a spawn error, the close of
// its pipes, or the budget. The child leads its own process group so that one SIGKILL reaches
// what it started too: a grandchild holding an inherited pipe would otherwise keep `close` from
// ever firing, and a child ignoring SIGTERM is not asked twice. The timer is cleared on every
// settlement.
function spawnPolicy(executable: string, args: string[], cwd: string, input: string | undefined): Promise<PolicyProcess> {
  const { promise, resolve } = Promise.withResolvers<PolicyProcess>();
  let stdout = "";
  let stderr = "";
  let settled = false;
  let timer: ReturnType<typeof setTimeout> | undefined;
  const settle = (proc: PolicyProcess): void => {
    if (settled) return;
    settled = true;
    clearTimeout(timer);
    resolve({ ...proc, stdout, stderr });
  };
  let child: ChildProcess;
  try {
    child = spawn(executable, args, {
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
      stdio: "pipe",
      detached: true,
    });
  } catch (error) {
    settle({ status: null, error: error instanceof Error ? error : new Error(String(error)) });
    return promise;
  }
  child.stdout?.setEncoding("utf8").on("data", (chunk: string) => { stdout += chunk; });
  child.stderr?.setEncoding("utf8").on("data", (chunk: string) => { stderr += chunk; });
  // A gate that exits without reading its input closes the pipe under the write.
  child.stdin?.on("error", () => {});
  child.on("error", (error) => settle({ status: null, error }));
  // Whatever the child left running would hold its pipes open past its own exit.
  child.on("exit", () => killGroup(child.pid));
  child.on("close", (status, signal) => settle({ status, signal }));
  timer = setTimeout(() => {
    killGroup(child.pid);
    child.stdout?.destroy();
    child.stderr?.destroy();
    settle({ status: null, signal: "SIGKILL", timedOut: true });
  }, POLICY_TIMEOUT_MS);
  child.stdin?.end(input);
  return promise;
}

export async function runPolicy(
  cwd: string,
  script: string,
  args: string[],
  payload: Dict,
): Promise<PolicyResult> {
  const proc = await spawnPolicy(gatePath(script), args, cwd, JSON.stringify(payload));
  return classifyPolicyRun(script, payload, proc);
}

type GatePhase = "pre" | "post" | "dispatch" | "yield";

// One notice per unavailable answer, tagged with its phase so omp's identical-context dedup
// never folds a pre notice into a post one.
function noteUnavailable(notices: string[], phase: GatePhase, script: string, result: PolicyResult): void {
  if (result.unavailable === undefined) return;
  notices.push(`Harness: ${script.replace(/\.py$/, "")} (${phase}) could not run; `
    + `nothing was checked. ${result.unavailable}`);
}

// The runner a handler hands its gates: every unavailable answer leaves one notice.
function reportingRunner(runner: PolicyRunner, phase: GatePhase, notices: string[]): PolicyRunner {
  return async (cwd, script, args, payload) => {
    const result = await runner(cwd, script, args, payload);
    noteUnavailable(notices, phase, script, result);
    return result;
  };
}

// FEAT-2337 (D-01): the five Bash gates, in the order their answers combine. Each stays its own
// process with its own applicability decision (DEC-234); no classifier skips one and no
// dispatcher merges them. All five are launched before any answer is read, then every outcome
// is read in this order whatever order they finished in: the first refusal leads, every gate
// that could not run leaves its notice, and a runner that failed outright refuses the call (as a
// thrown hook does) without hiding a sibling's refusal or notice.
const BASH_GATES = ["gh-close-gate.py", "branch-create-gate.py", "bash-write-guard.py", "plan-sign-gate.py", "merge-gate.py"];

async function bashGateRefusal(
  runner: PolicyRunner,
  cwd: string,
  payload: Dict,
  notices: string[],
): Promise<string | undefined> {
  const launch = async (script: string) => runner(cwd, script, [], payload);
  const outcomes = await Promise.allSettled(BASH_GATES.map(launch));
  const answers: PolicyResult[] = [];
  const failures: string[] = [];
  outcomes.forEach((outcome, index) => {
    const script = BASH_GATES[index];
    if (outcome.status === "fulfilled") {
      noteUnavailable(notices, "pre", script, outcome.value);
      answers.push(outcome.value);
      return;
    }
    const why = outcome.reason instanceof Error ? outcome.reason.message : String(outcome.reason);
    failures.push(`Harness: ${script.replace(/\.py$/, "")} (pre) failed before answering, so the call is refused: ${why}`);
  });
  const refusal = firstBlock(answers);
  return refusal || failures.length ? [refusal, ...failures].filter(Boolean).join("\n") : undefined;
}

function runtimeLineage(ctx?: any): { agentId: string; parentAgentId: string } {
  const agent = ctx?.agent && typeof ctx.agent === "object" ? ctx.agent as Dict : {};
  return {
    agentId: text(agent.id),
    parentAgentId: text(agent.parentId),
  };
}

function basePayload(agent: string, eventName: string, cwd: string, ctx?: any): Dict {
  const { agentId, parentAgentId } = runtimeLineage(ctx);
  return {
    agent_type: agent,
    hook_event_name: eventName,
    cwd,
    ...(agentId ? { harness_agent_id: agentId } : {}),
    ...(parentAgentId ? { harness_parent_agent_id: parentAgentId } : {}),
  };
}

// BUG-2003: an internal URI is not a checkout file, so check-domain.py never judges one.
// `agent://` (messaging) and exactly `xd://report_issue` (defect reports) pass. Every other
// scheme is refused by name, unknown ones included: some (`conflict://`, `local://`) write real
// files, and this adapter does not resolve URIs to paths. The main session never gets here.
const URI_SCHEME = /^([A-Za-z][A-Za-z0-9+.-]*):\/\//;

type DomainTarget = { kind: "file" } | { kind: "allowed" } | { kind: "refused"; reason: string };

function domainTarget(target: unknown): DomainTarget {
  const scheme = typeof target === "string" ? URI_SCHEME.exec(target)?.[1] : undefined;
  if (!scheme) return { kind: "file" };
  if (scheme === "agent" || target === "xd://report_issue") return { kind: "allowed" };
  const destination = scheme === "xd"
    ? `xd device "${String(target).slice("xd://".length)}"`
    : `${scheme}:// scheme`;
  return {
    kind: "refused",
    reason: `Harness refuses ${target}: the ${destination} is not a destination a governed `
      + "agent may write. Only agent:// and xd://report_issue are.",
  };
}

// The write path, every edit path (section sources and MV destinations) and every ast_edit
// `paths` entry pass through ONE decision, pre and post, so neither edit tool can become the way
// around a refused scheme and an allowed URI never exempts a sibling file in the same call.
// An ast_edit entry may be a directory or glob; it is judged as given, so one reaching outside
// the agent's domain is refused rather than expanded (#2028).
async function fileDomain(
  cwd: string,
  toolName: string,
  input: Dict,
  runner: PolicyRunner,
  args: string[],
  base: Dict,
): Promise<PolicyResult[]> {
  const targets: Array<[unknown, Dict]> = toolName === "write"
    ? [[input.path, { file_path: input.path, content: input.content }]]
    : toolName === "edit"
      ? extractEditPaths(input.input).map((filePath) => [filePath, { file_path: filePath }])
      : toolName === "ast_edit" && Array.isArray(input.paths)
        ? input.paths
          .flatMap((entry) => (typeof entry === "string" ? entry.split(";").map((part) => part.trim()) : [entry]))
          .filter((filePath) => filePath !== "")
          .map((filePath): [unknown, Dict] => [filePath, { file_path: filePath }])
        : [];
  const results: PolicyResult[] = [];
  for (const [target, toolInput] of targets) {
    const decision = domainTarget(target);
    if (decision.kind === "allowed") continue;
    results.push(decision.kind === "refused"
      ? { blocked: true, reason: decision.reason, stdout: "" }
      : await runner(cwd, "check-domain.py", args, {
        ...base,
        tool_name: toolName === "write" ? "Write" : "Edit",
        tool_input: toolInput,
      }));
  }
  return results;
}

function preDomain(
  cwd: string,
  agent: string,
  toolName: string,
  input: Dict,
  runner: PolicyRunner,
  ctx?: any,
  feature?: string,
): Promise<PolicyResult[]> {
  const base = {
    ...basePayload(agent, "PreToolUse", cwd, ctx),
    ...(feature ? { harness_feature: feature } : {}),
  };
  return fileDomain(cwd, toolName, input, runner, [], base);
}

async function postDomain(
  cwd: string,
  agent: string,
  toolName: string,
  input: Dict,
  runner: PolicyRunner,
  ctx?: any,
  feature?: string,
): Promise<PolicyResult[]> {
  const base = basePayload(agent, "PostToolUse", cwd, ctx);
  if (toolName !== "bash") return fileDomain(cwd, toolName, input, runner, ["--post"], base);
  // #2026: the Bash sweep narrows to the run's own feature's checkouts when it is named.
  return [await runner(cwd, "check-domain.py", ["--post"], {
    ...base,
    ...(feature ? { harness_feature: feature } : {}),
    tool_name: "Bash",
    tool_input: { command: input.command },
  })];
}

// BUG-1016: OMP starts a subagent in its parent's cwd, the main checkout, so a governed
// agent's relative path read and wrote main's copy rather than its feature worktree's. Each
// relative target is rooted in the worktree, lexically: no existence probe, no realpath, and
// selector text after the path (`:50-100`, an archive member, a SQLite query) is kept as is.
// Absolute, `~` and `scheme://` targets are explicit destinations and are never touched;
// blank ones are kept verbatim. Quoting and surrounding whitespace survive.
function rootTarget(raw: string, root: string): string {
  const trimmed = raw.trim();
  const quoted = /^"(.*)"$/.exec(trimmed);
  const target = quoted ? quoted[1] : trimmed;
  if (!target.trim() || isAbsolute(target) || target.startsWith("~") || URI_SCHEME.test(target)) {
    return raw;
  }
  // The target starts after the leading whitespace and, when quoted, the opening quote; never
  // searched for, since a target made of quotes would match the wrapper first.
  const at = raw.length - raw.trimStart().length + (quoted ? 1 : 0);
  return `${raw.slice(0, at)}${root}/${raw.slice(at)}`;
}

const rootPathList = (value: string, root: string): string =>
  value.split(";").map((entry) => rootTarget(entry, root)).join(";");

const PATH_TOOLS = ["read", "grep", "glob", "write", "ast_grep"];
// The tools whose omitted path means "search the cwd". read and write require a path, and
// ast_edit requires `paths`: none is invented for them.
const ROOT_DEFAULT_TOOLS = ["grep", "glob", "ast_grep"];

// The input the tool runs with once every relative target is rooted at `root`, or undefined
// when nothing changes. Never mutates `input`.
function rootedInput(toolName: string, input: Dict, root: string): Dict | undefined {
  if (toolName === "edit") {
    if (typeof input.input !== "string") return undefined;
    const patch = input.input.replace(EDIT_TARGET, (line: string, section?: string, hash?: string, move?: string) =>
      section !== undefined ? `[${rootTarget(section, root)}#${hash}]` : `MV ${rootTarget(String(move), root)}`);
    return patch === input.input ? undefined : { ...input, input: patch };
  }
  if (toolName === "ast_edit") {
    if (!Array.isArray(input.paths)) return undefined;
    const paths = input.paths.map((entry) => (typeof entry === "string" ? rootPathList(entry, root) : entry));
    return paths.every((entry, index) => entry === (input.paths as unknown[])[index])
      ? undefined : { ...input, paths };
  }
  if (!PATH_TOOLS.includes(toolName)) return undefined;
  if (input.path === undefined || input.path === null) {
    return ROOT_DEFAULT_TOOLS.includes(toolName) ? { ...input, path: root } : undefined;
  }
  if (typeof input.path !== "string") return undefined;
  const path = rootPathList(input.path, root);
  return path === input.path ? undefined : { ...input, path };
}

// Whether a call has anything to root, decided before any resolver runs: rooting at a
// placeholder changes the input exactly when rooting at the real worktree would.
const needsRoot = (toolName: string, input: Dict): boolean =>
  rootedInput(toolName, input, "/") !== undefined;

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

// FEAT-1928: the digest contract a harness child yields against is the hook's to supply, and
// only the hook's. Agent frontmatter cannot set schemaMode and OMP defaults to permissive, so a
// dispatcher-supplied schema or mode would replace or loosen that contract. Refused wherever
// it can appear, the main session included — the FEAT-65 collision came from the main session.
// BUG-2305: OMP persists the hook's revision as the call itself, so a dispatcher may send the
// injected pair back. A harness target carrying exactly its own bundle (key order aside) with
// schemaMode "strict" changes nothing and is accepted; withDigestSchemas re-injects it anyway.
const SCHEMA_CONTROLS = ["outputSchema", "schemaMode"];
const DIGEST_SCHEMA_DIR = join(gateRoot(), BIN, "digest-schemas");

function isInjectedCopy(target: Dict): boolean {
  const agent = text(target.agent);
  if (!agent.startsWith("harness-") || target.schemaMode !== "strict" || !Object.hasOwn(target, "outputSchema")) {
    return false;
  }
  try {
    return isDeepStrictEqual(target.outputSchema, loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, agent));
  } catch (error) {
    // An unloadable bundle has no copy; the controls are refused like any other.
    if (error instanceof DigestSchemaBundleError) return false;
    throw error;
  }
}

function schemaControlRefusal(input: Dict): string | undefined {
  const batch = Array.isArray(input.tasks);
  const found = batch || !isInjectedCopy(input)
    ? SCHEMA_CONTROLS.filter((key) => Object.hasOwn(input, key))
    : [];
  if (batch) {
    (input.tasks as unknown[]).forEach((item, index) => {
      if (!item || typeof item !== "object" || isInjectedCopy(item as Dict)) return;
      found.push(...SCHEMA_CONTROLS.filter((key) => Object.hasOwn(item, key))
        .map((key) => `tasks[${index}].${key}`));
    });
  }
  return found.length
    ? `Harness dispatches never carry ${found.join(", ")}: the hook injects each harness `
      + "persona's strict digest schema itself. Remove the field and dispatch again."
      + " Only an unchanged copy of a harness target's own bundle with schemaMode strict is accepted."
    : undefined;
}

// The revised task input with every harness target carrying its persona's strict bundle, or
// undefined when no target is a harness persona. Other targets and every other field — the
// batch shape, context, names, tools — are passed through as given. A bundle that cannot load
// throws DigestSchemaBundleError; there is no loose fallback.
function withDigestSchemas(input: Dict): Dict | undefined {
  const governed = (item: Dict): Dict => text(item.agent).startsWith("harness-")
    ? { ...item, outputSchema: loadDigestSchemaBundle(DIGEST_SCHEMA_DIR, text(item.agent)), schemaMode: "strict" }
    : item;
  if (Array.isArray(input.tasks)) {
    const given = input.tasks;
    const tasks = given.map((item) =>
      item && typeof item === "object" && !Array.isArray(item) ? governed(item as Dict) : item);
    return tasks.some((item, index) => item !== given[index]) ? { ...input, tasks } : undefined;
  }
  const flat = governed(input);
  return flat === input ? undefined : flat;
}

function parseClaimReceipt(stdout: string): ClaimReceipt | undefined {
  for (const parsed of jsonLines(stdout)) {
    const raw = parsed.harness_claim as Dict | undefined;
    if (!raw) continue;
    const root = text(raw.root);
    const feature = text(raw.feature);
    const agent = text(raw.agent);
    const claimId = text(raw.claim_id);
    if (root && feature && agent && claimId) return { root, feature, agent, claimId };
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

// A run-start, find-run or release-run answer (inflight_registry.py prints one JSON object).
// A step that printed none crashed; that is a refusal the run can retry, never a silent pass.
type RunAnswer = {
  ok: boolean;
  cause?: string;
  retryable?: boolean;
  message?: string;
  feature?: string;
  root?: string;
};
type DigestBinding = {
  root: string;
  feature: string;
  agent: string;
  agent_id: string;
  parent_agent_id: string;
  run_id: string;
  artifact: string;
};

function parseRunAnswer(result: PolicyResult): RunAnswer {
  const answer = jsonLines(result.stdout).reverse().find((parsed) => typeof parsed.ok === "boolean");
  if (answer) return answer as RunAnswer;
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

// FEAT-1928: the yield's `data` IS the digest. Anything but one object is refused here, before
// the validator runs, with the shape the agent must return instead.
const RETURN_THE_OBJECT = "Harness agents must return the digest as an object: "
  + "yield({data: {VERDICT, DIGEST, artifact}}) — a string, null, list or missing `data` is "
  + "not a digest.";
const MISSING_CAPABILITY = "Harness requires OMP's runtime lineage capability; install the "
  + "pinned Harness OMP build before dispatching agents or allowing governed mutations.";

// --- FEAT-2225 (DEC-253): expertise_apply, each persona's own Expertise pen ---------------
//
// The ONLY arguments are what the member judged: a tier, a literal repository segment, the ops
// and, for an original-member re-judgment, the exact batches it supersedes. Persona, feature,
// runtime ids, root, destination and main base are host-derived; naming one is refused.
const APPLY_ARGUMENTS = ["tier", "repository", "ops", "supersedes"];
// T-01's SEGMENT_RE and HEX64_RE, so the host refuses nothing the core would take and vice versa.
const REPOSITORY_SEGMENT = /^[a-z0-9][a-z0-9-]*$/;
const BATCH_ID = /^[0-9a-f]{64}$/;
const GIT_TIMEOUT_MS = 10_000;

function expertiseApplySchema(z: any): unknown {
  const textField = z.string().min(1);
  const section = z.enum(["Patterns", "Gotchas", "Outcomes", "Open"]);
  return z.object({
    tier: z.enum(["craft", "repository"])
      .describe("craft: your own .harness/expertise file; repository: your file under one declared repository"),
    repository: z.string().regex(REPOSITORY_SEGMENT).optional()
      .describe("tier=repository only: the literal declared segment, e.g. harness"),
    ops: z.array(z.union([
      z.object({ op: z.enum(["add", "replace"]), target: textField, section, entry: textField, why: textField }).strict(),
      z.object({ op: z.literal("drop"), target: textField, section, why: textField }).strict(),
    ])).describe("your judged ops; empty only to withdraw superseded batches"),
    supersedes: z.array(z.string().regex(BATCH_ID)).optional()
      .describe("exact batch ids of your own refused batches this re-judgment replaces"),
  }).strict();
}

function refuseApply(reason: string): never {
  throw new Error(`expertise_apply refused: ${reason}`);
}

// A second fence behind the host's own schema validation: a host that skipped it must still
// never forward a caller-named identity, root, destination or base.
function applyArgumentRefusal(params: Dict): string | undefined {
  const extra = Object.keys(params).find((key) => !APPLY_ARGUMENTS.includes(key));
  if (extra) {
    return `argument "${extra}" is not accepted; persona, feature, runtime ids, root, destination `
      + "and base are host-derived. Pass only tier, repository, ops and supersedes.";
  }
  if (!Array.isArray(params.ops)) return "ops must be a list of add, replace or drop ops.";
  const supersedes = params.supersedes ?? [];
  const exact = Array.isArray(supersedes)
    && supersedes.every((id) => typeof id === "string" && BATCH_ID.test(id));
  return exact ? undefined : "supersedes must list exact 64-hex batch ids.";
}

// The persona's own file, checkout-relative: never a free path.
function applyDestination(tier: unknown, repository: unknown, persona: string): { rel: string } | { reason: string } {
  if (tier === "craft") {
    return repository === undefined
      ? { rel: `.harness/expertise/${persona}.md` }
      : { reason: "tier craft takes no repository segment." };
  }
  if (tier !== "repository") return { reason: `tier must be craft or repository, not ${JSON.stringify(tier)}.` };
  if (typeof repository !== "string" || !REPOSITORY_SEGMENT.test(repository) || repository === "expertise") {
    return { reason: `repository must be one literal declared segment, not ${JSON.stringify(repository)}.` };
  }
  return { rel: `.harness/${repository}/expertise/${persona}.md` };
}

function lstatOrUndefined(path: string): Stats | undefined {
  try {
    return lstatSync(path);
  } catch {
    return undefined;
  }
}

// The containment recheck on the resolved root: a repository segment must be a real directory
// under .harness (declared), and no existing component of the destination may be a symlink —
// the same exact-path rule T-01's resolve_destination applies, checked before the core runs.
function placementRefusal(root: string, rel: string): string | undefined {
  const parts = rel.split("/");
  if (parts.length === 4 && !lstatOrUndefined(join(root, parts[0], parts[1]))?.isDirectory()) {
    return `repository segment "${parts[1]}" is not declared under ${root}/.harness.`;
  }
  for (let depth = 1; depth <= parts.length; depth += 1) {
    const path = join(root, ...parts.slice(0, depth));
    const stat = lstatOrUndefined(path);
    if (!stat) return undefined;
    if (stat.isSymbolicLink()) return `${path} is a symlink; the destination must stay inside ${root}.`;
  }
  return undefined;
}

// The current main a supersession reconstructs from: origin/HEAD's commit as the feature checkout
// records it — the default branch validate-digest.py also reads — never a caller-chosen base.
function mainBase(root: string): { base: string } | { reason: string } {
  const proc = spawnSync("git", ["rev-parse", "--verify", "--quiet", "refs/remotes/origin/HEAD^{commit}"], {
    cwd: root, encoding: "utf8", timeout: GIT_TIMEOUT_MS,
  });
  const base = (proc.stdout || "").trim();
  if (proc.status === 0 && /^[0-9a-f]{40,64}$/.test(base)) return { base };
  return {
    reason: `the current main base (origin/HEAD) could not be resolved in ${root}; Main must fetch `
      + "origin and set origin/HEAD before a re-judgment can supersede a batch.",
  };
}

// member-ops answers exit 0 with one JSON receipt line, returned verbatim. ANY other exit is a
// tool failure — not runPolicy's policy-only non-blocking convention — carrying the core's lines.
function memberOpsReceipt(result: PolicyResult): { line: string; receipt: Dict } {
  const lines = result.stdout.split("\n").map((line) => line.trim()).filter(Boolean);
  if (result.blocked || result.reason) {
    refuseApply(`expertise-merge.py member-ops failed (${result.reason || "refused"}): `
      + (lines.join(" | ") || "no output"));
  }
  const line = lines.at(-1) ?? "";
  const receipt = jsonLines(line)[0];
  if (!receipt) refuseApply(`expertise-merge.py member-ops exited 0 but printed no receipt: ${line || "no output"}`);
  return { line, receipt };
}

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

async function releaseClaim(
  runner: PolicyRunner,
  cwd: string,
  receipt: ClaimReceipt,
): Promise<void> {
  await runner(cwd, "inflight_registry.py", [
    "release",
    "--claim-id", receipt.claimId,
    "--feature", receipt.feature,
    "--root", receipt.root,
  ], {});
}

// Receipts are released one at a time, in the order they were taken, each awaited.
async function releaseClaims(runner: PolicyRunner, cwd: string, receipts: ClaimReceipt[]): Promise<void> {
  for (const receipt of receipts) await releaseClaim(runner, cwd, receipt);
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
  let digestBinding: DigestBinding | undefined;
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
  const resolveFeature = async (ctx: { cwd: string }, prompt: unknown): Promise<RunAnswer> => {
    if (currentFeature) return { ok: true };
    const assigned = promptFeature(prompt);
    if (assigned.conflict) {
      return { ok: false, cause: "feature-conflict", retryable: false, message: assigned.conflict };
    }
    if (assigned.feature) {
      setFeature(assigned.feature);
      return { ok: true };
    }
    const found = parseRunAnswer(await policyRunner(ctx.cwd, "inflight_registry.py", [
      "find-run", "--agent-id", runtimeAgentId, "--root", ctx.cwd,
    ], {}));
    if (found.ok) setFeature(found.feature);
    return found;
  };

  // The run-start claim (T-01's one locked step): reuse this id's claim, bind the unique
  // receipt its parent's dispatch left, or create one. A refusal holds the run.
  const startRun = async (ctx: { cwd: string }, prompt: unknown): Promise<RunAnswer> => {
    if (!runtimeAgentId || !runtimeParentAgentId) {
      return { ok: false, cause: "runtime-lineage", retryable: false, message: MISSING_CAPABILITY };
    }
    const feature = await resolveFeature(ctx, prompt);
    if (!feature.ok) return feature;
    return parseRunAnswer(await policyRunner(ctx.cwd, "inflight_registry.py", [
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

  // BUG-1016: the worktree this run's relative paths are rooted in, named by the ONE feature-root
  // resolver for the run's own feature, never by dispatch prose, tool input or the environment.
  // A validated answer is kept for the run (keyed by run id, feature and checkout, and dropped at
  // every run boundary); a refusal or an unusable answer is never kept and never guessed past.
  let featureRootCache: { key: string; root: string } | undefined;
  const featureRoot = async (cwd: string): Promise<{ root: string } | { reason: string }> => {
    const key = JSON.stringify([runtimeAgentId, currentFeature, cwd]);
    if (featureRootCache?.key === key) return { root: featureRootCache.root };
    const refused = (why: string) => ({
      reason: `Harness could not place this call in ${currentFeature}'s checkout: feature-root ${why}.`,
    });
    let answer: PolicyResult;
    try {
      answer = await policyRunner(cwd, "inflight_registry.py", [
        "feature-root", "--feature", String(currentFeature), "--root", cwd,
      ], {});
    } catch (error) {
      return refused(`could not run (${error instanceof Error ? error.message : String(error)})`);
    }
    if (answer.blocked || answer.reason) return refused(`refused: ${answer.reason || "no reason given"}`);
    const roots = answer.stdout.split("\n").map((line) => line.trim()).filter(Boolean);
    if (roots.length !== 1 || !isAbsolute(roots[0])) {
      return refused(`gave no single absolute root (${JSON.stringify(answer.stdout)})`);
    }
    featureRootCache = { key, root: roots[0] };
    return { root: roots[0] };
  };

  // A governed call's input rooted in its worktree: undefined when there is nothing to root or
  // the feature has no worktree (the resolver answers the checkout itself).
  const rootCall = async (cwd: string, toolName: string, input: Dict): Promise<{ input?: Dict; reason?: string }> => {
    if (!needsRoot(toolName, input)) return {};
    const resolved = await featureRoot(cwd);
    if ("reason" in resolved) return { reason: resolved.reason };
    return resolved.root === cwd ? {} : { input: rootedInput(toolName, input, resolved.root) };
  };

  // A child is released by its runtime id wherever its claim lives, and a call's receipts
  // once all of that call's children have settled.
  const settleRun = async (callKey: string | undefined, agentId: string, cwd: string): Promise<void> => {
    // One registry step finds the claim bound to this runtime id, wherever it lives, and
    // releases it by feature + id under that registry's lock. A child that never governed
    // (a scout, a sonic) holds none, and nothing is released for it.
    await policyRunner(cwd, "inflight_registry.py", ["release-run", "--agent-id", agentId, "--root", cwd], {});
    if (!callKey) return;
    const pending = pendingTaskCalls.get(callKey);
    if (!pending) return;
    pending.settled.add(agentId);
    if (pending.settled.size < pending.total) return;
    // Taken off the map before the first release is awaited, so a concurrent settlement of the
    // same call can never release these receipts twice.
    pendingTaskCalls.delete(callKey);
    await releaseClaims(policyRunner, cwd, pending.receipts);
  };

  // Open the run gate: claim this exact id, or hold the run with the refusal's reason. The gate
  // stays unready (every tool refused) until every answer it depends on has arrived, and a second
  // opening while one is in flight joins it rather than claiming again.
  let opening: Promise<RunAnswer> | undefined;
  const claimRun = async (ctx: { cwd: string }, prompt: unknown): Promise<RunAnswer> => {
    runGate = { state: "unready" };
    digestBinding = undefined;
    featureRootCache = undefined;
    const started = await startRun(ctx, prompt);
    try {
      if (started.ok && (currentAgent === "harness-eng-lead" || currentAgent === "harness-product-lead" || currentAgent === "harness-validator-lead")) {
        const result = await policyRunner(ctx.cwd, "digest_destination.py", [], {
          ...basePayload(String(currentAgent), "SubagentStart", ctx.cwd, {
            agent: { id: runtimeAgentId, parentId: runtimeParentAgentId },
          }),
          harness_feature: currentFeature,
        });
        const bound = jsonLines(result.stdout).reverse().find((answer) => answer.ok === true);
        if (!result.blocked && bound?.binding) digestBinding = bound.binding as DigestBinding;
      }
    } finally {
      runGate = started.ok ? { state: "ready" } : { state: "held", reason: heldRunReason(started) };
    }
    return started;
  };
  const openRun = (ctx: { cwd: string }, prompt: unknown): Promise<RunAnswer> => {
    opening ??= claimRun(ctx, prompt).finally(() => { opening = undefined; });
    return opening;
  };

  // Exact runtime lineage through the registry: the one claim authorization every governed
  // mutation passes, expertise_apply included.
  const authorizationRefusal = async (cwd: string, agent: string): Promise<string | undefined> => {
    const authorization = await policyRunner(cwd, "inflight_registry.py", [
      "authorize",
      "--agent", agent,
      "--feature", String(currentFeature),
      "--agent-id", runtimeAgentId,
      "--parent-agent-id", runtimeParentAgentId,
      "--root", cwd,
    ], {});
    return authorization.blocked || authorization.reason
      ? authorization.reason || "Harness runtime child lineage is not authorized."
      : undefined;
  };

  // FEAT-2225: the caller expertise_apply serves — a ready governed run under a trusted distill
  // assignment whose exact runtime lineage the registry authorizes. Nothing is read from arguments.
  const applyCallerRefusal = async (cwd: string): Promise<string | undefined> => {
    if (!currentAgent) {
      return "expertise_apply is only for a governed Harness persona; this session carries no Harness identity.";
    }
    if (runGate.state !== "ready") return heldReason();
    if (currentMission !== "distill") {
      return "expertise_apply runs only under a trusted distill assignment (HARNESS-MISSION: distill in the dispatch).";
    }
    if (!currentFeature || !runtimeAgentId || !runtimeParentAgentId) return MISSING_CAPABILITY;
    return authorizationRefusal(cwd, currentAgent);
  };

  // Where the persona's own file lands: the run's feature root from the one resolver, the file
  // from tier and segment, the containment recheck, and for a supersession the main base.
  const applyPlacement = async (cwd: string, params: Dict): Promise<{ root: string; rel: string; base?: string }> => {
    const destination = applyDestination(params.tier, params.repository, String(currentAgent));
    if ("reason" in destination) refuseApply(destination.reason);
    const resolved = await featureRoot(cwd);
    if ("reason" in resolved) refuseApply(resolved.reason);
    const root = realpathSync(resolved.root);
    const misplaced = placementRefusal(root, destination.rel);
    if (misplaced) refuseApply(misplaced);
    if (!(params.supersedes as unknown[] | undefined)?.length) return { root, rel: destination.rel };
    const main = mainBase(root);
    if ("reason" in main) refuseApply(main.reason);
    return { root, rel: destination.rel, base: main.base };
  };

  // Destinations expertise_apply landed, by tool call, for that call's post-write check.
  const appliedDestinations = new Map<string, string>();

  // F1: REGISTERED distill authority, never the HARNESS-MISSION marker alone. validate-digest.py
  // derives it from this exact run's live claim and its registered distill lineage (the lineage
  // it already checks for yields); only exit 0 with `{"authorized": true}` grants it.
  const distillAuthorityRefusal = async (root: string): Promise<string | undefined> => {
    const answer = await policyRunner(root, "validate-digest.py", ["--distill-authority"], {
      agent_type: currentAgent,
      harness_feature: currentFeature,
      harness_agent_id: runtimeAgentId,
      harness_parent_agent_id: runtimeParentAgentId,
      cwd: root,
    });
    const granted = !answer.blocked && !answer.reason
      && jsonLines(answer.stdout).some((line) => line.authorized === true);
    return granted ? undefined : answer.reason || answer.unavailable
      || "validate-digest.py --distill-authority granted no authority.";
  };

  const applyExpertise = async (toolCallId: string, params: Dict, cwd: string) => {
    const refusal = applyArgumentRefusal(params) ?? await applyCallerRefusal(cwd);
    if (refusal) refuseApply(refusal);
    const placed = await applyPlacement(cwd, params);
    const unauthorized = await distillAuthorityRefusal(placed.root);
    if (unauthorized) refuseApply(unauthorized);
    const supersedes = (params.supersedes as string[] | undefined) ?? [];
    const result = await policyRunner(placed.root, "expertise-merge.py", [
      "member-ops",
      "--root", placed.root,
      "--feature", String(currentFeature),
      "--persona", String(currentAgent),
      "--runtime-id", runtimeAgentId,
      "--parent-id", runtimeParentAgentId,
      "--tier", String(params.tier),
      ...(params.tier === "repository" ? ["--repository", String(params.repository)] : []),
      "--ops", "-",
      ...supersedes.flatMap((id) => ["--supersedes", id]),
      ...(placed.base ? ["--base", placed.base] : []),
      // The ops list is the stdin document (`--ops -`); runPolicy serializes any JSON value.
    ], params.ops as unknown as Dict);
    const { line, receipt } = memberOpsReceipt(result);
    appliedDestinations.set(toolCallId, join(placed.root, placed.rel));
    return { content: [{ type: "text", text: line }], details: receipt };
  };

  // Essential, not discoverable: a discoverable tool is reached through `write xd://…`, which the
  // governed URI rule refuses, and the tool_call gates must see this tool under its own name.
  pi.registerTool({
    name: "expertise_apply",
    label: "Expertise apply",
    description: "During a distill assignment, apply your own judged Expertise ops (add, replace, drop) "
      + "to your own craft or repository Expertise file in this feature's checkout. Persona, feature "
      + "and destination come from your run. Returns the core's receipt with before/after counts.",
    parameters: expertiseApplySchema(pi.zod),
    approval: "write",
    loadMode: "essential",
    async execute(toolCallId: string, params: unknown, _signal: unknown, _onUpdate: unknown, ctx: any) {
      const args = (params && typeof params === "object" && !Array.isArray(params) ? params : {}) as Dict;
      return applyExpertise(toolCallId, args, text(ctx?.cwd) || sessionCwd);
    },
  });

  // The post-write check on the file expertise_apply landed, as an Edit of that exact path: the
  // destination the host resolved for this call, never one the caller's input names.
  const appliedPost = async (cwd: string, agent: string, toolCallId: string, ctx: any, runner: PolicyRunner): Promise<PolicyResult[]> => {
    const destination = appliedDestinations.get(toolCallId);
    appliedDestinations.delete(toolCallId);
    if (!destination) return [];
    return [await runner(cwd, "check-domain.py", ["--post"], {
      ...basePayload(agent, "PostToolUse", cwd, ctx),
      tool_name: "Edit",
      tool_input: { file_path: destination },
    })];
  };

  // FEAT-2225: a non-governed Bash merge reaches merge-gate.py (a distill candidate must go through
  // merge-gate.py merge-distill) while every other Main call stays outside governed domains. The
  // word prefilter only spares a spawn; merge-gate.py parses the command itself.
  const mainMergeGate = async (cwd: string, command: string, ctx: any): Promise<{ block: true; reason: string } | undefined> => {
    if (!/\bmerge\b/.test(command)) return undefined;
    const result = await policyRunner(cwd, "merge-gate.py", [], {
      ...basePayload("Main", "PreToolUse", cwd, ctx),
      tool_name: "Bash",
      tool_input: { command },
    });
    return result.blocked ? { block: true, reason: result.reason || "merge-gate.py denied the merge." } : undefined;
  };

  // FEAT-2274 (C4): a Harness persona is spawned through `task` and nothing else — eval `agent()`
  // and workpool carry none of the task path's claim, schema or dispatch checks. Every caller,
  // Main included, and independent of this session's own identity. Which targets a caller may
  // spawn at all is native `spawns` policy, not this hook's.
  pi.on("before_subagent_spawn", async (event: Dict) => {
    const agent = text(event.agent);
    if (!agent.startsWith("harness-") || event.invocationKind === "task") return undefined;
    return {
      block: true,
      reason: `Harness refuses spawning ${agent} through ${text(event.invocationKind) || "an unnamed route"}: `
        + "a Harness persona is dispatched with the task tool only, which carries its claim, digest "
        + "schema and dispatch checks. Dispatch it with the task tool.",
    };
  });

  pi.on("before_agent_start", async (event: Dict, ctx: any) => {
    const detected = detectHarnessAgent(event.systemPrompt);
    const detectedFeature = detectMarker(event.systemPrompt, FEATURE_MARKER, "feature");
    const detectedPin = detectMarker(event.systemPrompt, REVIEW_PIN_MARKER, "review pin");
    const detectedMission = detectMarker(event.systemPrompt, MISSION_MARKER, "mission");
    ({ agentId: runtimeAgentId, parentAgentId: runtimeParentAgentId } = runtimeLineage(ctx));
    sessionCwd = text(ctx.cwd) || sessionCwd;
    if (detected) currentAgent = detected;
    if (detectedPin) currentReviewPin = detectedPin;
    if (detectedMission) currentMission = detectedMission;
    setFeature(detectedFeature);
    if (!currentAgent) return;
    const started = await openRun(ctx, event.prompt);
    if (runGate.state === "held") {
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
    // Only once the run holds its claim: reconcile's locked writer reads a corrupt registry
    // as empty and rewrites it, which would erase the very file a refusal leaves as found.
    if (!claimsReconciled) {
      await policyRunner(ctx.cwd, "inflight_registry.py", [
        "reconcile",
        "--feature", String(currentFeature),
        "--root", ctx.cwd,
      ], {});
      claimsReconciled = true;
    }
    if (expertiseInjected) return;

    const result = await policyRunner(ctx.cwd, "inject-expertise.py", [], {
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

  // #1908: a parked agent is revived COLD — OMP rebuilds its session from the session file, so
  // this extension is a fresh instance that never saw before_agent_start, and the hub's message
  // arrives through agent.prompt(), which emits agent_start only. Without this, the revived run
  // had no runtime lineage (every `task` refused) and no persona (every write ungoverned). Its
  // identity is read back from the one record OMP persisted at spawn: the session_init entry's
  // system prompt and assignment (DEC-204: identity comes from the assignment, nothing later).
  const adoptPersistedRun = (ctx: any): string | undefined => {
    ({ agentId: runtimeAgentId, parentAgentId: runtimeParentAgentId } = runtimeLineage(ctx));
    sessionCwd = text(ctx?.cwd) || sessionCwd;
    const entries = typeof ctx?.sessionManager?.getEntries === "function"
      ? ctx.sessionManager.getEntries() as unknown[]
      : [];
    const init = entries.find((entry) =>
      entry && typeof entry === "object" && (entry as Dict).type === "session_init") as Dict | undefined;
    if (!init) return undefined;
    const systemPrompt = [text(init.systemPrompt)];
    const detected = detectHarnessAgent(systemPrompt);
    if (detected) currentAgent = detected;
    const pin = detectMarker(systemPrompt, REVIEW_PIN_MARKER, "review pin");
    if (pin) currentReviewPin = pin;
    const mission = detectMarker(systemPrompt, MISSION_MARKER, "mission");
    if (mission) currentMission = mission;
    setFeature(detectMarker(systemPrompt, FEATURE_MARKER, "feature"));
    captureDispatchFromMessage({ role: "user", content: text(init.task) });
    return text(init.task);
  };

  // BUG-1898 (live probe S2): a hub-woken agent runs a new turn through agent.prompt(),
  // which emits agent_start but never before_agent_start. Its claim was released when it
  // settled, so the wake re-opens the gate here — the same exact-id claim step, with the
  // feature this session already runs. A first run arrives already ready and is untouched.
  pi.on("agent_start", async (_event: Dict, ctx: any) => {
    const assignment = runtimeAgentId ? "" : adoptPersistedRun(ctx);
    if (!currentAgent || runGate.state === "ready") return;
    await openRun({ cwd: text(ctx?.cwd) || sessionCwd }, assignment ?? "");
  });

  pi.on("message_update", async (event: Dict) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    captureDispatchFromMessage(candidate);
  });

  pi.on("message_end", async (event: Dict) => {
    const candidate = event.message && typeof event.message === "object"
      ? event.message
      : event;
    captureDispatchFromMessage(candidate);
  });

  pi.on("tool_call", async (event: Dict, ctx: any) => {
    const toolName = text(event.toolName);
    const input = (event.input && typeof event.input === "object" ? event.input : {}) as Dict;
    const agentId = runtimeAgentId;
    const parentAgentId = runtimeParentAgentId;
    const runtimeCtx = {
      ...ctx,
      agent: {
        ...(ctx.agent && typeof ctx.agent === "object" ? ctx.agent : {}),
        id: agentId,
        ...(parentAgentId ? { parentId: parentAgentId } : {}),
      },
    };
    const mutates = ["write", "edit", "ast_edit", "bash", "expertise_apply"].includes(toolName);
    sessionCwd = text(ctx.cwd) || sessionCwd;
    if (toolName === "task" && !agentId) {
      return { block: true, reason: MISSING_CAPABILITY };
    }
    // BUG-1898: a governed run that holds no claim of its own runs nothing but a yield.
    if (currentAgent && runGate.state !== "ready" && toolName !== "yield") {
      return { block: true, reason: heldReason() };
    }
    if (!currentAgent && toolName === "bash") return mainMergeGate(ctx.cwd, text(input.command), runtimeCtx);
    const ompMainTask = !currentAgent
      && toolName === "task"
      && agentId === "Main"
      && !parentAgentId;
    if (!currentAgent && !ompMainTask) return;
    const policyAgent = currentAgent || "Main";
    let revisedInput: Dict | undefined;
    let reason: string | undefined;
    // FEAT-2274: one notice per gate invocation that could not run, in the order the gates are
    // declared (FEAT-2337: the concurrent Bash gates too, whatever order they finished in).
    const notices: string[] = [];
    const preGate = reportingRunner(policyRunner, "pre", notices);
    if (mutates) {
      reason = currentFeature
        ? await authorizationRefusal(ctx.cwd, policyAgent)
        : "Harness child mutation policy requires runtime child, parent, and feature identity.";
    }
    // BUG-1016: after claim readiness and mutation authorization, before any domain gate, so
    // every gate judges the input the tool will actually run with.
    let effectiveInput = input;
    if (!reason && currentAgent) {
      const rooted = await rootCall(ctx.cwd, toolName, input);
      reason = rooted.reason;
      if (rooted.input) effectiveInput = revisedInput = rooted.input;
    }
    if (!reason) {
      reason = firstBlock(await preDomain(
        ctx.cwd, policyAgent, toolName, effectiveInput, preGate, runtimeCtx, currentFeature,
      ));
    }
    if (!reason && toolName === "bash") {
      const payload = {
        ...basePayload(policyAgent, "PreToolUse", ctx.cwd, runtimeCtx),
        ...(currentFeature ? { harness_feature: currentFeature } : {}),
        tool_name: "Bash",
        tool_input: { command: input.command },
      };
      // BUG-1132: plan-sign-gate.py (REQ-05/DEC-120 — only the main session signs an approval)
      // was wired into `.claude/settings.json` for native Claude Code but never ported here, so
      // a `plan-merge.py sign-approval` Bash call under OMP reached no denylist at all — not
      // merely the evadable one #1103 documents. `cmd_sign_approval` itself has no identity
      // check (that is #1103's own scope), so this script was the ONLY thing standing between
      // an agent and forging a signature, and on this host it was never invoked.
      reason = await bashGateRefusal(policyRunner, ctx.cwd, payload, notices);
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
      // FEAT-1928: schema controls are refused and every harness target's bundle is loaded
      // BEFORE dispatch-guard.py runs, so a schema-refused dispatch never records a claim.
      reason = schemaControlRefusal(input)
        ?? (ompMainTask ? undefined : taskModelOverride(input));
      if (!reason) {
        try {
          revisedInput = withDigestSchemas(input);
        } catch (error) {
          if (!(error instanceof DigestSchemaBundleError)) throw error;
          reason = `Harness dispatch refused: ${error.message} A harness agent is never `
            + "dispatched without its strict digest schema.";
        }
      }
      const receipts: ClaimReceipt[] = [];
      if (!reason) {
        for (const dispatch of normalizeTaskDispatches(input)) {
          const result = await reportingRunner(policyRunner, "dispatch", notices)(ctx.cwd, "dispatch-guard.py", [], {
            ...basePayload(policyAgent, "PreToolUse", ctx.cwd, ctx),
            tool_name: "Task",
            tool_input: dispatch,
            harness_runtime: "omp",
            supervisor_pid: process.pid,
          });
          if (result.blocked) {
            await releaseClaims(policyRunner, ctx.cwd, receipts);
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
            const parentAgentId = agentId;
            if (parentAgentId) {
              const args = [
                "attach",
                "--agent", receipt.agent,
                "--feature", receipt.feature,
                "--claim-id", receipt.claimId,
                "--parent-agent-id", parentAgentId,
                "--root", receipt.root,
              ];

              const attached = await policyRunner(
                ctx.cwd, "inflight_registry.py", args, {},
              );
              if (attached.blocked || attached.reason) {
                await releaseClaims(policyRunner, ctx.cwd, receipts);
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
      let digest: unknown = input.data;
      // OMP normalizes optional null data to absence before this hook; strict terminal yields
      // reject that natively before last-turn resolution and leave the same child retryable.
      if (digest == null && input.type === "result") return undefined;
      // BUG-2171: a model may send the object as JSON text, which OMP's own yield tool parses
      // losslessly; only a string encoding one plain object passes the check below.
      if (typeof digest === "string") {
        try { digest = JSON.parse(digest); } catch { digest = undefined; }
      }
      if (!digest || typeof digest !== "object" || Array.isArray(digest)) {
        reason = RETURN_THE_OBJECT;
      } else if (currentAgent && runGate.state !== "ready" && (digest as Dict).VERDICT !== "BLOCKED") {
        reason = `${heldReason()} This run may yield only a BLOCKED digest.`;
      } else {
        const result = await reportingRunner(policyRunner, "yield", notices)(ctx.cwd, "validate-digest.py", ["--hook"], {
          ...basePayload(policyAgent, "SubagentStop", ctx.cwd, runtimeCtx),
          stop_hook_active: false,
          digest_object: digest,
          harness_digest_binding: digestBinding,
          harness_feature: currentFeature,
          harness_review_pin: currentReviewPin,
          harness_mission: currentMission,
        });
        debug(`yield agent=${currentAgent} value=${JSON.stringify(digest).slice(0, 500)}`);
        debug(`yield verdict blocked=${result.blocked} reason=${result.reason || "none"}`);
        reason = result.blocked ? result.reason : undefined;
      }
    }
    // FEAT-2274 V3: omp 19.1.0 returns a blocking tool_call result's `reason` alone and drops
    // its additionalContext, so a sibling gate's could-not-run notice rides in the reason,
    // after the denial that blocked the call.
    if (reason) return { block: true, reason: [reason, ...notices].join("\n") };
    if (!revisedInput && !notices.length) return undefined;
    return {
      ...(revisedInput ? { input: revisedInput } : {}),
      ...(notices.length ? { additionalContext: notices.join("\n") } : {}),
    };
  });

  pi.on("tool_result", async (event: Dict, ctx: any) => {
    const toolName = text(event.toolName);
    const ompMainTask = !currentAgent
      && toolName === "task"
      && runtimeAgentId === "Main"
      && !runtimeParentAgentId;
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
        await releaseClaims(policyRunner, ctx.cwd, pending?.receipts ?? []);
      } else {
        for (const agentId of settledRunIds(event.details)) await settleRun(key, agentId, ctx.cwd);
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
          const rooted = await policyRunner(ctx.cwd, "inflight_registry.py", [
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
            await policyRunner(ctx.cwd, "feature-record.py", [
              "stamp-tokens", "--file", spendFeatureJson, "--tokens", String(tokens),
            ], {});
          }
          const measured = await policyRunner(ctx.cwd, "feature-record.py", [
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
    // BUG-1016: the host may hand back the original or the revised input; rooting is
    // idempotent, so the post gate judges the same files the pre gate did either way.
    const rooted = currentAgent && ["write", "edit", "ast_edit"].includes(toolName)
      ? await rootCall(ctx.cwd, toolName, input) : {};
    const notices: string[] = [];
    const postGate = reportingRunner(policyRunner, "post", notices);
    const reason = rooted.reason ?? firstBlock(toolName === "expertise_apply"
      ? await appliedPost(ctx.cwd, policyAgent, text(event.toolCallId), ctx, postGate)
      : await postDomain(ctx.cwd, policyAgent, toolName, rooted.input ?? input, postGate, ctx, currentFeature));
    const content = Array.isArray(event.content) ? event.content : [];
    const appended = advisories.map((advisoryText) => ({ type: "text", text: advisoryText }));
    // FEAT-2274: a post gate that could not run is passive context beside the result, never an
    // error and never a rewrite of the tool's own content.
    const context = notices.length ? { additionalContext: notices.join("\n") } : {};
    if (!reason) {
      if (appended.length === 0) return notices.length ? context : undefined;
      // No isError key AT ALL: a normal tool result must not become an error.
      return { content: [...content, ...appended], ...context };
    }
    return {
      content: [...content, { type: "text", text: `Harness post-write check: ${reason}` }, ...appended],
      isError: true,
      ...context,
    };
  });

  // BUG-1898 defect D: OMP publishes a child's lifecycle on the session EventBus — the
  // `pi.events` an extension holds — for a first run and for every message-woken turn
  // alike. `pi.on` is the hook dispatcher and never carried it, so no child was ever
  // released here. A settled child is released by its own runtime id and nothing else. The
  // bus awaits an async listener (and reports its failure), so the settlement is returned.
  pi.events.on("task:subagent:lifecycle", async (data: unknown) => {
    const event = (data && typeof data === "object" ? data : {}) as Dict;
    const agentId = text(event.id);
    if (!agentId || !SETTLED_STATUSES.includes(text(event.status))) return;
    await settleRun(text(event.parentToolCallId) || undefined, agentId, sessionCwd);
  });

  pi.on("agent_end", async () => {
    if (!currentAgent) return;
    // The turn is over and its claim released on yield; a later wake must claim again.
    runGate = { state: "unready" };
    featureRootCache = undefined;
  });
}

export default function harnessHooks(pi: any): void {
  registerHarnessHooks(pi);
}
