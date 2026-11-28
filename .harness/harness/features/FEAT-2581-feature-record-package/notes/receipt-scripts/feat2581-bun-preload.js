// FEAT-2581 T-03: passed to `bun test --preload`. Marks every process bun spawns as the bun class
// for the recorder, carries the recorder's environment into children given an explicit env, and
// names node mkdtempSync directories with a counter under the same fixed root the Python recorder
// uses, so fixture paths are the same bytes on both sides. It changes nothing a test asserts on.
const fs = require("node:fs");
const path = require("node:path");
const childProcess = require("node:child_process");

const ROOT = "/tmp/feat2581-fixtures";
process.env.FEAT2581_BUN = "1";
const carried = Object.keys(process.env).filter((key) => key.startsWith("FEAT2581_"));

function withRecorder(env) {
  if (!env || typeof env !== "object") return env;
  const out = { ...env };
  for (const key of carried) if (!(key in out)) out[key] = process.env[key];
  const recorder = process.env.FEAT2581_RECORDER;
  const paths = (out.PYTHONPATH || "").split(path.delimiter).filter(Boolean);
  if (recorder && !paths.includes(recorder)) out.PYTHONPATH = [recorder, ...paths].join(path.delimiter);
  return out;
}

let counter = 0;
const originalMkdtempSync = fs.mkdtempSync;
fs.mkdtempSync = function mkdtempSync(prefix, options) {
  fs.mkdirSync(path.join(ROOT, "bun"), { recursive: true });
  for (;;) {
    counter += 1;
    const dir = path.join(ROOT, "bun", `${path.basename(String(prefix))}${String(counter).padStart(5, "0")}`);
    try {
      fs.mkdirSync(dir, { mode: 0o700 });
      return dir;
    } catch (error) {
      if (error && error.code === "EEXIST") continue;
      return originalMkdtempSync.call(fs, prefix, options);
    }
  }
};
// Bun's spawn functions default to the environment the process started with, not to the
// process.env this preload changed, so every call gets an explicit env: the caller's own env
// when it passed one, else process.env, each with the recorder's keys added.
const plain = (arg) => arg && typeof arg === "object" && !Array.isArray(arg) && typeof arg !== "function";

function carryEnv(args, canAppend) {
  const index = args.findIndex(plain);
  if (index >= 0) {
    const out = [...args];
    out[index] = { ...args[index], env: withRecorder(args[index].env || process.env) };
    return out;
  }
  return canAppend(args) ? [...args, { env: withRecorder(process.env) }] : args;
}

for (const name of ["spawn", "spawnSync", "execFile", "execFileSync", "exec", "execSync"]) {
  const original = childProcess[name];
  childProcess[name] = function (...args) {
    return original.apply(this, carryEnv(args, (a) => !a.some((x) => typeof x === "function")));
  };
}

for (const name of ["spawn", "spawnSync"]) {
  const original = Bun[name];
  Bun[name] = function (...args) {
    return original.apply(this, carryEnv(args, () => true));
  };
}
