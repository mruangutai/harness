# Two YAML entry points for plan.yaml — judged `needs_signature`, severity BACKLOG

**Verdict: `needs_signature`.** The signed text permits a duplicate-key guard but does not force one,
and adding one moves acceptance. **Severity: backlog** — it fails closed and loudly.
**Carrier: a follow-up outside FEAT-32** for the code fix; inside FEAT-32 only two prose items,
both operator-signed. No task here is mine and I adopted none.

## The finding (carried, not re-derived)

`bin/plan-merge.py:37` imports `yaml` plainly per T-03's `intent:` (`plan.yaml:604-605`).
`bin/harness_yaml.py:199-218` rejects a repeated mapping key at any depth (`DuplicateKeyError`,
raised at `:181`). Measured by the tier above: stdlib `safe_load` accepts a duplicated `status:`
inside a task and keeps the last value; `harness_yaml.load_str` rejects it, with the
no-duplicate control accepted by both. So plan-merge can splice a duplicate-key proposal into a
real `plan.yaml` that every later reader — and both write hooks — then refuses.

## Job 1 ruling

### 1. `needs_signature`, and the reading I rejected

Principle applied, from `notes/research-FEAT-32-t15-verify.md:8-10`: a correction to signed text
needs no new signature **only when the signed artifact itself forces the one right answer.**

**Rejected reading:** *"a guard added alongside `import yaml` contradicts none of T-03's words, so it
is covered."* It is true that it contradicts none of them — and that is exactly why it fails the
test. **Permission is not compulsion.** T-03 step 3 (`plan.yaml:604-607`) names `yaml.safe_load` as
the parser and defines exit 5 as *"the parser's own message"*; a stricter loader adds a refusal class
the signed text never contemplated, and three questions follow that nothing in the artifact settles:
is a duplicate key exit 5 or a new code; is the **base** strict-parsed too (which would make the tool
refuse plans already on disk — a fail-closed regression on existing files); and does the divergence
get closed here or recorded as residue. Choosing among those is new content.

**Confirmed at source, and it is the crux:** DEC-171 am.1 (`DECISIONS.md:4550-4565`) is entirely about
**dependency availability** — no fallback, no line scanner, a missing PyYAML is an error not a quieter
mode. It says nothing about loader semantics. A rationale about availability **cannot** bear the
weight of forbidding a duplicate-key guard. That is what makes a fix legitimate to propose; it is not
what makes it already-signed.

Citation: the ONLY-try/except declaration is **D-12**, at `bin/harness_yaml.py:4` — a signed decision
of FEAT-05 (`FEAT-05-pyyaml-file-parsers/PLAN.md:229-234`, approved 2026-08-03). Not D-02.
**D-12 is not violated:** its literal claim is one `try/except`, and plan-merge adds none.

### 2. Severity — backlog, and the fail-closed argument stands

It needs an agent to emit malformed YAML; it then fails **closed and loudly** at the next reader, and
the approval block is untouched (D-04 keeps base bytes). Nothing is silently wrong. The real cost is
misattributed blame — the merge exits 0 and the *next* tool reports the corruption — plus a plan.yaml
recoverable only by hand-edit. Annoying, not dangerous. I could not beat the fail-closed argument, so
I do not call it a ship-blocker.

### 3. Carrier

Not T-03 reopened (done, and its signed step 3 would have to change). Not a new FEAT-32 task — that
is scope creep on a feature at T-06/T-10. **A follow-up issue outside FEAT-32.** Inside FEAT-32,
operator's call on two prose items only (see the request).

### 4. Success criteria

- **SC-11 (`BRIEF.md:321-327`) does NOT fail.** Its enumeration is *"each obtain their lock and
  perform their atomic replace by calling the shared core, and none of them contains a lock or
  replace primitive of its own."* A YAML loader is neither a lock nor a replace primitive. Reading
  its lead sentence *"There is one implementation"* as reaching every shared module in the tree would
  make it quantify over files no FEAT-32 task touches — the failure my own brief rules forbid.
  **But it passes while a reader would believe something false**: "one implementation" plus
  `harness_yaml.py:4-6` reads as one YAML entry point for `plan.yaml`, and there are two.
- **SC-13 (`BRIEF.md:334-340`) needs a seventh statement if the divergence ships unfixed** — the same
  shape as the lock file. It does not *fail* on its six today; widening it is a signed-text change,
  which is why it is in the request. `plan-merge.py:29-30` already states the divergence in code
  ("raised upward as a decision question, not resolved here"), so the residue exists — it is just not
  in SC-13's list.
- **A falsified statement in shipped code.** `bin/harness_yaml.py:4-6` asserts *"Every other module in
  this tree that needs YAML imports THIS module, never `yaml` directly."* Discriminating check I ran:
  every other direct `import yaml` under `bin/` is in a `test-*.py` file; `plan-merge.py:37` is the
  **only non-test module** that does it. So the sentence was true before T-03 and is false now. No SC
  covers it, and there is no propagation checker (CLAUDE.md, DEC-188) — nothing will catch it.
- No other SC turns on this. SC-14 / the 221 figure: untouched, per dispatch.

## Open questions

- Q1 (blocking the two prose items only): operator's call on the request's three items.
- Q2 (non-blocking): if the fix is ever built, does the strict loader apply to the **base** as well as
  the proposal? Strict-parsing the base can refuse a plan already on disk. That is the trade-off a
  signature is for.
