# Security review — FEAT-01 c1 (`a606d7a..9b07cfc`)

**PASS. One real defect, `low`: the digest gate fails open on a crash an ordinary confused agent can
trigger.** Everything else in the classic checklist is genuinely absent here, and the parser held up
under measurement rather than assumption.

## Scope

**In scope, narrowly.** No auth, no secrets, no SQL, no network, no rendered output. But
`validate-digest.py --hook` is registered as a `SubagentStop` hook in every project that deploys the
harness (`templates/settings.snippet.json`), so it executes on every harness subagent's stop and
parses **LLM-generated text the agent controls**. That is untrusted input crossing into a gate. The
hook registration itself predates this range (only the `_comment` line changed), and
`inject-expertise.sh` / `check-domain.sh` are untouched in range — out of scope.

## Finding 1 — `low` — enum fields crash the validator, which then silently passes the return

`validate-digest.py`, in `validate()` at `if val not in allowed:`. `allowed` is a `set`; `val` comes
from `parse_scalar`, which returns a **list** for any `[...]` value. `list in set` raises
`TypeError: unhashable type: 'list'`. Uncaught — `hook_mode()` wraps only `json.load`, not
`validate()`.

Reproduced against `9b07cfc` with a digest containing `severity_max: [low, med]`: traceback,
**exit 1**.

Exit 1 is a *non-blocking* hook error and execution proceeds — this repo established that
empirically, not by recall: `DECISIONS.md` DEC-100 ("Only `exit 2` blocks. Any other non-zero exit
is a non-blocking error and the write proceeds"), and `check-domain.sh:13-14` carries the same
verified comment. Educated guess on one step: DEC-100 probed `PreToolUse`; the same convention
applies to `SubagentStop` per the standard hook exit-code contract, and DEC-122 quotes
`exit 2 … prevents the subagent from stopping`. So the direction is **fail-open, not wedge** — the
subagent stops normally and its unvalidated digest ships.

**Who, and what they get.** Not an attacker — an agent making plausible drift. The `set`-valued
fields are `severity_max`, `feasibility`, `surface`, `recommend`, `risk`, `suite`, `contract`,
`change_type`. `severity_max:` sits one line from `must_fix: []` in every normative template, and
`[]` is the *mandated* way to say nothing (DEC-121), so `severity_max: [high]` is the single most
likely wrong thing to write. Writing it takes the entire gate offline **for that return only, with
no signal** — the orchestrator sees a clean stop. That is exactly the fail-open-and-silent class
DEC-97 / DEC-110 / DEC-121 exist to hunt, now inside the hunter.

`test-validate-digest.py` has no list-valued-enum case (it covers the scalar drift `severity_max:
medium` at line 141, never a list) — the gate's own suite does not reach its crash path.

Direction of fix (not applied): guard the membership test on `isinstance(val, str)`, and wrap
`validate()` in `hook_mode()` in a `try/except` that reports the exception on stderr and returns 0,
which is the fail-open-loudly behaviour the docstring already claims and does not currently have.

## Checked and cleared — with evidence, not assertion

| Area | Result |
|---|---|
| **ReDoS** | **Absent, measured.** Every pattern is `\s*`/`[a-z0-9_-]*` against a disjoint next literal — no nested quantifier, no overlapping alternation. 400 KB of pure whitespace through `--hook`: 0.03 s. |
| **Algorithmic DoS** | `parse_digest`'s inner block-list scan is O(n²) in empty-valued keys: 20 000 keys → 0.44 s. A self-authored multi-MB message would be needed to matter, and the "attacker" is the agent stalling its own stop. Not a finding. |
| **Path traversal / arbitrary read** | None. `hook_mode` reads **only** `last_assistant_message` from the payload — no transcript path, no filename, no `open()` on anything payload-derived. CLI mode's `open(sys.argv[2])` is operator argv, not a trust boundary. |
| **Injection / deserialization** | None. Grepped both new files: no `eval`, `exec`, `os.system`, `Popen`, `shell=True`, `pickle`, `yaml`, `__import__`, no network. `json.load` on stdin is safe. The test file's `subprocess.run` takes a list, no shell. |
| **Data exposure** | Rejection stderr echoes digest values (`{field}={val!r}`; member entries truncated to 60 chars). On `exit 2` that stderr returns to the **same** subagent that authored the text — no boundary crossed, no third-party data, no PII, no credentials. Not a disclosure path. |
| **Secrets** | None in range. The only `token`/`auth` hits are prose examples in SKILL.md/test fixtures. |
| **Agent scoping (EoP)** | `startswith("harness-")` plus `norm(agent) not in SCHEMAS` → pass through. A non-harness or unknown agent is never governed. Correct. |
| **`stop_hook_active`** | Honoured — no infinite-block loop. |

## Open questions

- Q1 (non-blocking): should the `SubagentStop` exit-1 semantics be probed and recorded as a DEC, the
  way DEC-100 recorded `PreToolUse`? The fail-open direction of Finding 1 rests on generalising it.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| Agent-authored digest text → hook parser | T (gate bypass) | **No** — Finding 1 |
| Agent-authored digest text → hook parser | D (ReDoS / algorithmic) | Yes — measured linear; quadratic path bounded and self-inflicted |
| Hook JSON payload → file access | I (arbitrary read) | Yes — no payload-derived path |
| Hook stderr → agent context | I (disclosure) | Yes — returns to the authoring agent only |
| `agent_type` → schema dispatch | E (governing foreign agents) | Yes — prefix + schema-presence pass-throughs |
