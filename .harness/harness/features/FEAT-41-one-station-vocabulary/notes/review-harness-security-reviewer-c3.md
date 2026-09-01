# FEAT-41 cycle-3 security review — review_sha 5dc77108

BOTH STAGES RAN. Stage 1 (spec compliance, REQ-05/SC-06/SC-07) FAILS: two confirmed working
evasions falsify REQ-05's core claim and SC-07's literal wording. Stage 2 (code quality / STRIDE)
adds a third HIGH (fail-open crash) and a T-19-exemption elevation path. Tree left clean —
confirmed `git status --short` empty, HEAD unchanged at `a725472` (0 diff from `5dc77108` for
every file reviewed except `feature.json`'s `review_sha` bump), no scratch files left under the
worktree or `/tmp`. All mutation testing ran against synthetic plan.yaml files under system `/tmp`
(via Python `tempfile`, self-cleaned in-process) or ephemeral process substitution — never against
a tracked path.

## MUST-FIX (high)

**H-1. `$(...)`/backtick command substitution forges `sign-approval` end to end — C2-03's fix
covers only the braced-`${...}` syntax, not "any unquoted expansion that resolves to whitespace."**
`plan-sign-gate.py:126` (`BRACED_EXPANSION = re.compile(r'"?\$\{[^{}]*\}"?')`) neutralises only
`${...}`. Command substitution word-splits identically when unquoted and is untouched.
Payload: `python3 plan-merge.py$(printf " ")sign-approval --file plan.yaml`.
- Gate (`plan-sign-gate.py:150 denies()`, piped the real pinned-sha script): **exit 0**, no stderr.
- Real bash (`bash -c` with a stub `python3` printing argv): splits into
  `ARG1=[plan-merge.py] ARG2=[sign-approval] ARG3=[--file] ARG4=[plan.yaml]` — a genuine, working
  two-token call. Backtick form (`` plan-merge.py`printf " "`sign-approval ``) reproduces
  identically, gate exit 0.
- Impact confirmed by direct execution of `cmd_sign_approval` (`plan-merge.py:824`) against a
  synthetic plan.yaml: it has **zero internal caller-identity check** — any invocation succeeds
  and writes `approval: {status: approved, approved_by: <argv>, date: <argv>}`. Nothing else in
  the codebase gates this verb. `plan-sign-gate.py` is not a defense-in-depth layer here — the
  contract says so explicitly in its own docstring — but that means this bypass gives the
  agent a real, persisted, forged, "approved" signature, full stop.
- This directly falsifies **REQ-05** ("cannot write the approval signature at all; only the main
  session can record a signature") and **SC-07** ("`sign-approval` is refused when the hook
  payload carries an `agent_type`") — a case exists where `agent_type` is present and
  `sign-approval` is not refused. Per this diff's own DEC-100/C2-03 framing, the intended
  invariant was "an expansion could be whitespace, so adjacency must assume it is" — that rule was
  applied to one syntax (`${...}`) and not the mechanism it names.

**H-2. A NUL byte in `tool_input.file_path` crashes check-domain.sh's entire PreToolUse body —
exit 1, which the script's own header states is non-blocking (DEC-100) — disabling every
invariant it enforces for that call, not only the plan-route denial.**
Reproduced with the real script (`bash .claude/skills/harness/bin/check-domain.sh` fed the payload
on stdin, `agent_type: backend-dev`, `tool_name: Write`):
```
file_path = "bin/foo\u0000bar"                    -> exit 1, ValueError: lstat: embedded null character in path
file_path = "CLAUDE\u0000.md"                      -> exit 1, same
file_path = ".../plan\u0000...plan.yaml", Edit tool -> exit 1, same
```
Traceback: `_plan_route` (`check-domain.sh:1539`) → `_resolved_rel` (`:1490`) →
`os.path.realpath` → `ValueError`, uncaught anywhere in the 1791-line body. `check-domain.sh:12-13`
states outright: "VERIFIED (DEC-100): exit 2 blocks the tool call... Only exit 2 blocks — exit 1 is
a NON-blocking error and the write proceeds." By the file's own documented contract this is a
fail-open crash reachable by **any** NUL byte anywhere in a Write/Edit `file_path`, not merely one
shaped like `plan.yaml` — every budget check (CLAUDE.md 80 lines, STATE.md 120, feature.json 300),
every domain grant, and the plan-route denial are simultaneously disabled for that one call.
Rated high rather than critical because I could not verify from this repo whether the platform's
actual Write/Edit tool implementation (outside this repo) accepts or rejects a NUL-containing
`file_path` before ever reaching this hook — CPython and Node's `fs` both reject embedded NULs
outright, so the write itself may separately fail regardless. What is fully confirmed and
independent of that uncertainty: the enforcement layer is not crash-safe, and an adversarial agent
that can shape any field of `tool_input` has a demonstrated, trivial way to make it disappear.

**H-3. The T-19 task-less exemption plus `plan-merge.py apply`'s open-to-every-agent, unvalidated
create-new-file path let an agent put a feature on the board with an active station and zero
approval trail, invisible to every check-state.sh invariant.**
`apply` (`plan-merge.py:412`, "step 3") writes a nonexistent `--file` target **whole** from the
proposal, refusing only if the proposal itself carries an `approval:` key — it never calls
`_legal_stations`/`_refuse_illegal_station`, so the station value it writes is not validated
against the vocabulary at all (only `set-task-station`/`set-feature-station` validate). `apply` is
not gated by `plan-sign-gate.py` (which refuses `sign-approval` alone) or by `check-domain.sh`
(scoped to the `Write|Edit` tool matcher only — Bash-invoked `plan-merge.py` never reaches it).
Reproduced end to end against a scratch checkout:
```
proposal = "feature: FEAT-ROGUE-x\nstatus: build\ntasks: []\n"
python3 plan-merge.py apply --file .../FEAT-ROGUE-x/plan.yaml --proposal -
-> rc 0, file created verbatim, status: build, no approval: block, no BRIEF.md anywhere
```
Traced `check-state.sh`'s invariants against this shape (read, not independently executed — the
script resolves its root from its own installed location via `harness_boundary`, so it cannot be
pointed at an isolated scratch tree without touching the live repo):
- `briefs` (`check-state.sh:122`) is built only from *existing* `BRIEF.md` globs — a feature with
  none is simply absent from the dict, so the INV-1/2 "not approved" check (`:176-179`, iterating
  `briefs.items()`) never sees it.
- `plan_docs[feat]["tasks"]` is `[]` → the T-19 exemption (`:200`, `if not doc["tasks"]: continue`)
  skips the approval-block check and the STATE.md-task-id check both.
- INV-26 (`:1725`, board-vs-plan reconciliation) only compares an *existing* board card's station
  against the plan; a feature never mirrored to a board card is not examined.
- INV-34 (`:1091`) checks the opposite direction (a feature directory with *no* plan.yaml).
No invariant in the file cross-references "a `plan.yaml` exists, declares a working station, and
no `BRIEF.md` was ever written." This is the dispatch's item-3(b) scenario, and it is real: the
T-19 ruling ("every feature has a plan.yaml, so a station is always recordable") was scoped to
legitimate task-less scaffolding, but the write route that produces that shape is open to every
agent with Bash, with no station validation and no cross-check for a missing goal-of-record.

## Med (written reason for not-high)

**M-1. `check-domain.sh:1549`'s `_tool in ("Write", "Edit", "NotebookEdit")` is an allow-list of
known write-capable tool names, not a deny-list of anything writable — a tool this harness later
grants (or a platform-added tool name) that reaches the filesystem and is omitted from the tuple
silently reopens the plan-route denial for it.** Checked every agent definition under
`.claude/agents/*.md`: none currently declares `MultiEdit`; `NotebookEdit` is included defensively
but is likewise ungranted today. Not reachable at `5dc77108` under the current sixteen agent
grants — hence med, not high — but it is exactly the allow-list-inversion shape the dispatch named,
and the fix (deny on any tool carrying `file_path`/`notebook_path` rather than naming three) is
one line away from converting this into a real gap the day an agent config adds one.

## Low / info (measured, not exploitable — negative results are the finding)

**L-1. `_plan_route`'s "fails closed" claim (`check-domain.sh:1543-1548`, and the C2-02 commit
message) is empirically dead code, but the hole it describes is closed by a different mechanism it
does not name.** `os.path.realpath` (non-strict, what `_resolved_rel` calls) never raises `OSError`
for a symlink loop, a self-referential symlink, or a broken symlink on this platform — confirmed
directly:
```
loop a->b->a:        realpath(a) = <original path>, no exception
self-loop c->c:       realpath(c) = <original path>, no exception
broken symlink:        realpath(d) = <unresolved target path>, no exception
40-hop non-cyclic chain to a real file: realpath resolves it correctly (no cap — the C2-02(c) fix works)
```
So the `except OSError: return None` branch that the comment calls "the correction that matters
most" never fires for the cases it names. What actually closes the hole: `open()` for writing
through a genuine loop raises `ELOOP` at the OS level (confirmed: `open(a, 'w')` → `OSError ELOOP`),
and the same 40-hop chain that `realpath` resolves fine fails `ELOOP` on `open()` because macOS
enforces `SYMLOOP_MAX` independent of Python's own cycle-detecting walk. A genuine dangling
symlink pointing directly at a plan.yaml-shaped path *is* caught (realpath resolves it, no
exception, `RE_PLAN_YAML` matches the resolved target) — separately confirmed `open()` on a
dangling symlink **creates** the target through POSIX semantics, so that path is not itself a gap.
Net: the specific `resolved is None` fail-closed branch is unreachable in practice, but no live
hole follows from it — the kernel's own `ELOOP` enforcement (not this script) is what actually
fails closed. Reported at info because a future port to a filesystem/kernel without hard
`SYMLOOP_MAX` (or any stat-only, non-open-based consumer of `_plan_route`) would lose that
protection silently, and the code's self-description would still claim otherwise.

**Negative results — plan-sign-gate.py, tested end to end against the pinned script:**
| form | gate exit |
|---|---|
| `${IFS:0:1}` | 2 (denied) |
| `${IFS-x}` | 2 |
| `${IFS//x/}` | 2 |
| `${!var}` indirection | 2 |
| backslash-newline continuation | 2 |
| `eval "plan-merge.py sign-approval ..."` | 2 |
| `sh <<EOF ... EOF` heredoc | 2 |
| `--` / `-- --` separator forms | 2 |
| shell function shadowing `plan-merge.py` | 2 |
| `$'\x20'`/`$'\t'` ANSI-C quoting | 0 at the gate, **but not a real bypass** — confirmed via `bash -c` that adjacent ANSI-C-quoted text concatenates into ONE argv word (`"plan-merge.py sign-approval"`, embedded space, not two tokens), so `python3 <that>` fails to find the file. False positive at the gate level, non-exploitable. |
| `IFS=@; set -- plan-merge.py@sign-approval; python3 "$@"` | 0 at the gate initially reported, **also not real** — `set --`'s literal argument is never IFS-split (confirmed via isolated `bash -c`); an artifact of testing inside this session's own wrapper shell rather than genuine bash produced a false split on first pass, corrected against `bash -c` ground truth. |
| `echo <base64> \| base64 -d \| sh`, `xargs`, `sh -c` with an assembled verb, alias shadowing | 0 (real, working evasions) — but these are the **disclosed** class: the gate's own docstring names "a binary produced only by shell expansion... is invisible here... NOT a security boundary." Not reported as new findings. |

Only H-1 (command/backtick substitution) is a working evasion outside the disclosed class, and it
lands in the same "expansion could be whitespace" mechanism C2-03 claimed to close.

**--by/--date YAML injection (dispatch item 5) — all attempts refused correctly.** Ran
`cmd_sign_approval` (`plan-merge.py:824`) directly against synthetic plan.yaml with adversarial
`--by` values: embedded `\ntasks:\n  - id: T-99`, a value that closes `approval:` and opens
`tasks:`, a block scalar opening a new top-level key, an anchor/alias pair, `!!python/object/...`,
a flow-mapping, and a value literally spelling another key. Every one round-tripped through
`_field_lines`'s `yaml.safe_dump` (`:245`) as a correctly quoted scalar and was accepted verbatim
by `_verify_signature`'s identity comparison (`:271`, `got.get(key) != want`) — none altered
`plan.yaml`'s structure. F-02's fix generalizes correctly beyond `--date`.

**Case-insensitivity (dispatch item 2) — already closed.** `RE_PLAN_YAML` (`check-domain.sh:1046`)
is compiled with `_I = re.IGNORECASE`; `PLAN.YAML` matches the same as `plan.yaml`. Not a gap.

## Stage 1 — REQ-05/SC-06/SC-07, literal compliance at `5dc77108`

- **REQ-05 "An agent cannot write it with an editor tool"**: true for the ordinary case; **false**
  under H-2's crash (uncertain full exploit chain, honestly caveated above).
- **REQ-05 "cannot write the approval signature at all; only the main session can record a
  signature"**: **FALSE**, per H-1, executed and confirmed.
- **SC-06** (shell write of an illegal station reported by the post-Bash sweep): assessed by
  reading only, not independently executed this cycle — no contradicting evidence found, and it is
  a different mechanism (post-hoc sweep) than anything I mutation-tested. The BRIEF's own
  disclosure (a *legal*-value shell write is unattributable) is accurate as far as tested and is
  not understated by anything found here.
- **SC-07** ("`sign-approval` is refused when the hook payload carries an `agent_type`"):
  **FALSE as written** — H-1 is exactly the counterexample: `agent_type` present, `sign-approval`
  reached and executed.

## Threat model (STRIDE, agent as adversary)

| boundary | STRIDE | mitigated |
|---|---|---|
| `plan.yaml` `approval:` block, written only by `sign-approval` | Spoofing (forged signature) | false — H-1 |
| `check-domain.sh` PreToolUse enforcement of all budget/domain/route rules | Tampering (crash to fail-open) | false — H-2 |
| feature station / board visibility requiring a signed BRIEF | Elevation (agent-authored, unsigned "approved" work) | false — H-3 |
| `plan.yaml` write route restricted to `plan-merge.py`'s five verbs | Tampering (off-route write via link/hardlink/case) | true — C2-02 hardlink+dir-chain fix holds; case-insensitivity already covered |
| YAML structure of the signed block, via `--by`/`--date` | Tampering (structural injection) | true — F-02 generalizes correctly |

Convergence note for the panel: H-1 and H-3 are independent routes to the same asset (an
unaccountable "approved-looking" state in `plan.yaml`) — H-1 forges the literal signature, H-3
sidesteps the need for one entirely by exploiting the task-less exemption. Both should gate
shipping; neither substitutes for the other's fix.
