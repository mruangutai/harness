# panel.readers — the goalcheck entry, transcribed

**Done. `panel.readers` now holds three entries; nothing else in plan.yaml changed in value.**
One deviation from the dispatch, forced and proven: the write went through `plan-merge.py
**set-panel**`, not `apply`. `apply` cannot express this change.

## Why not `apply`

`panel` is not a union key — `UNION_KEYS = ("tasks", "decisions")` (`plan-merge.py:104`). Every
other top-level key falls to step 8, which raises **exit 7 CONFLICT** when base and proposal
disagree (`plan-merge.py:764-774`). Probed both proposal shapes against a throwaway copy:

| case | result |
|---|---|
| `apply`, panel-only proposal | exit 7 CONFLICT, file untouched |
| `apply`, whole-document proposal | exit 7 CONFLICT, file untouched |
| `set-panel --value-file` | exit 0, exactly the one entry added |

`amend` is not a route either: `--key` accepts `tasks \| decisions` only. `set-panel` is the verb
the tool declares for this key (`plan-merge.py:15`, `cmd_set_panel:1040`), under the same
`locked_update` lock and the same `require_destination` guard. The constraint "plan.yaml's only
write route is plan-merge.py" is honoured; only the sub-verb differs. No Edit, no Write, no
redirect touched the file.

## What moved

Added, after the existing two (`plan.yaml:695-697`):

```
  - reader: goalcheck
    persona: harness-pm
    status: ran
```

Three keys, no fourth — matching the shape of the other two, and `status: ran` needs no `reason`
(only `skipped` does, `check-state.sh:548-553`).

**Everything before `panel:` is byte-identical** (compared as text, split on the `\npanel:\n`
boundary). Inside `panel`, all values reload equal — verified key by key: non-panel keys equal,
`panel` minus `readers` equal, `readers[:2]` unchanged. Findings, dismissed, transcription_rule,
last_run, cycle, severity_max: values untouched. `approval: {status: pending}`.

**Cosmetic caveat, unavoidable:** `cmd_set_panel` re-emits the panel block through
`yaml.safe_dump` at the default width, so long plain scalars in `findings`/`dismissed`/
`transcription_rule` are now line-wrapped. Byte positions moved; **no value did** — the verb
refuses unless the block reloads equal to the value supplied (`plan-merge.py:1063`). There is no
route that avoids this: `set-panel` is the only verb that owns the key.

## Evidence

Acceptance command, literal output:

```
['should-not-exist', 'scope', 'goalcheck']
4
```

Four PF ids, severities unchanged: `PF-4bd91290deaf98062943319ff3ea5641` high should-not-exist ·
`PF-d2cefa75a1931540efa60d3561f7df6b` med should-not-exist ·
`PF-4d84bb7e52beff3ee62eb98a7115ae9e` low scope · `PF-7469688fee994f7ec08ad85dea1d1f8b` low scope.
`dismissed` holds 2. No finding was added for the goal-check; its six were closed in
`planfix-c1-product` and dispositioned in `notes/research-FEAT-104-planfix-c1.md`. The run itself
is real: `feature.json` run `goalcheck-plan-product`, agent `harness-product-lead`, verdict FAIL.

## INV-32 is fixed but not yet exercised — read this before claiming it green

`check-state.sh` emits **no INV-32 line for FEAT-104 at all**, and that is not proof of a pass:
the whole INV-32 body is gated on an **approved** plan (`check-state.sh:438-487`). FEAT-104 is
`pending`, so it is skipped — which is also why its open `high` finding raises nothing today. The
invariant starts grading this feature the moment the operator signs.

Proved the branch discriminates by running the reader predicate (`check-state.sh:534-553`,
transcribed verbatim) against the real file and against a mutant with the entry removed:

- real file → no BAD lines
- mutant → `INV-32: ... reader goalcheck never ran or was not recorded`

## Open — not mine, not caused by this change

`check-plan-routes.py` on this plan **exits 1**. The single counted violation is the header line:
the worktree's `.harness/team-config.yaml` differs from the owner manifest, so routes resolve
against the owner's. Task-level output is all `OK`/`DEVIATION` (the expected DEC-174 carve-out
shape). Unrelated to `panel`, which this checker does not read — but it is red at signature time
and someone should own it.
