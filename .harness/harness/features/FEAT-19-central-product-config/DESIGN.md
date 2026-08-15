# DESIGN — FEAT-19 Central product config

**Scope: the operator-facing command surface only.** This feature has no graphical surface and
**no prototype is required** (the gate is at the end of this document). What is designed here is
what a human reads at a terminal when they ask which config answered — the one success payload and
the **seven** refusal lines — because this project already treats that text as a designed artifact,
with its grammar centralized in `factory_cli.body` and its stream/exit rules in `factory_cli`'s
module docstring.

Everything below is a **contract on code that does not exist yet**. No sentence here is a
measurement of `factory_product_config.py`; the measured statements are about the existing files
they cite.

## BLUF

SC-12 — "the operator can see, in one command's output, which config file answered" — is answered by
eight strings, not one. The plan pins the success payload; the branch the operator hits first is a
refusal, and **on a refusal there is no stdout at all**, so "which file was consulted" is carried
solely by the stderr line's `value` slot. Contracts 2 and 3 pin that slot, and slot 3, across all
seven refusals.

Five of the seven now hold as the plan writes them — T-01's re-authored `intent:` absorbed this
document's earlier corrections and cites it by name. **Two do not: row 6 (5b-ii, a product's config
file present but malformed or not a mapping) and row 7 (step 6, the harness's own
`.harness/harness.json` missing, unparseable or not a mapping) have no `what` string in the plan at
all.** Contract 3's last two rows supply both, and mark them as contract-supplied rather than
plan-quoted so a later reader can tell which slots came from where.

## Contract 1 — the success payload

`--which-config <path>` on success MUST emit exactly one stdout line through `factory_cli.payload`, a
JSON object with these three keys and no others:

| Key | Value | Why it is in the operator's view |
|---|---|---|
| `source` | `"product"` or `"harness"` | the one-word answer; readable without parsing a path |
| `config_path` | absolute path of the file that answered | **this is the SC-12 observable** |
| `product` | the fleet name `owner/repo`, or `null` when harness answered | disambiguates two products whose paths look alike |

`null` for `product` is required, not omission — an absent key is indistinguishable from a tool that
forgot to set it, which is the same failure mode the DIGEST contract exists to prevent elsewhere.
The parsed config body MUST NOT be printed: the question is which file answered, and a full matrix
dump buries the answer it was asked for.

## Contract 2 — the refusal branches are also the SC-12 surface

Every refusal exits 2 with **empty stdout** (`factory_cli.run`). So for all **seven** failing
branches, the "which config file" answer is the `value` slot of the stderr line, and nothing else.
The grammar is `factory: product-config: {what}: {value} — {next_step}`.

**`value` MUST be the path or repository name the operator can act on** — where the tool has already
computed a path, `value` is that path and not the session root. An operator told only where they
were standing has to re-derive what the tool already knew.

## Contract 3 — every refusal, and slot 3 is the next action, never the cause

`factory_cli.body`'s third slot is what the operator does next. Existing call sites hold to it
("install gh, or point FACTORY_GH at its path"; "check the board number"). The table is the complete
enumeration of the refusal surface — one row per `raise` in T-01's algorithm:

| # | Branch (T-01 step) | `value` | `next_step` | Verdict |
|---|---|---|---|---|
| 1 | 4b — fleet absent, session outside the harness root | session root | run from inside `<harness root>`, or declare a fleet at `<fleet_path>` | **holds** |
| 2 | 4b — fleet present but does not load | `fleet_path` | fix that file (original error chained in) | **holds** |
| 3 | 5a — inside neither root | session root | run from inside `<harness root>`, or from a registered checkout under `<workspace_root>` | **holds** |
| 4 | 5b-i — checkout registered nowhere | session root | add a repos entry to `<fleet_path>` | **holds** |
| 5 | 5b-ii — registered repo has no product config | the config path looked for | create it | **holds** |
| 6 | 5b-ii — product config malformed / not a mapping | the file path | repair the file to a JSON object | **`value`/`next_step` hold — `what` gap in plan, text supplied below** |
| 7 | 6 — the harness's own `harness.json` missing, unparseable or not a mapping | that file's path | **see below — the plan supplies no `what`** | **gap in plan — text supplied below** |

Rows 1–5 satisfy both slot rules as T-01's `intent:` writes them; nothing here overrides them. Rows 6
and 7 satisfy them on `value` and `next_step` as written, and are missing `what` entirely — the two
blocks below supply it. **Everything in those two blocks marked "contract-supplied" is written here,
not quoted from `plan.yaml`;** every other cell in the table is the plan's own text.

**Row 6, the required `what`.** The plan's 5b-ii malformed branch pins `value` (the file path) and
`next_step` (repair the file to a JSON object) and writes no `what` at all. It is supplied here:

- `what` — **"the product config does not parse to a JSON object"** (contract-supplied). It MUST NOT
  reuse row 5's "registered repository has no product config": on this branch the file **exists**,
  and telling the operator their config is absent sends them hunting for a missing file that is
  sitting at the very path in the `value` slot. "does not parse" states the file is there and the
  contents are the fault, and covers both causes the plan names — invalid JSON, and valid JSON that
  is not a mapping. It also must not read like row 7's harness-side text: the word *product* is what
  tells the operator whose file to open.
- `value` and `next_step` — as the plan writes them; nothing here overrides them.

**Row 7, the required text** (all three slots contract-supplied). The plan's step 6 says only "Missing, unparseable or not a mapping
raises ProductConfigError with value the file path and next_step the repair" — `value` and slot 3
gestured at, `what` unwritten. It owes all three:

- `what` — **"the harness's own config does not load"**. Not "config not found": this branch is
  reached only when the session already resolved to the *control plane*, and the operator must be
  told it is the harness's file at fault, not a product's. Rows 5 and 6 name a product's file in the
  same slot, and the two must not read alike.
- `value` — the absolute `<harness root>/.harness/harness.json` path. Same rule as rows 5 and 6.
- `next_step` — **"restore or repair `<path>` to a JSON object"**, one action covering all three
  causes. It must NOT say "create it" the way row 5 does: a harness checkout always ships this file,
  so its absence means a damaged checkout, not an unconfigured one, and "create it" would send the
  operator to hand-author the control plane instead of restoring it. This **sharpens** the plan's
  bare "the repair", which covers the unparseable cause but not the missing one.

This is the branch a harness developer hits when their own checkout is broken — the likeliest of the
seven to be hit while this very feature is being built, and one of the two the plan leaves without a
`what`.

## Contract 4 — `--which-config`, and the homonym it avoids

`check-domain.sh --resolve <path>` already exists and answers a **different** question with a
**different** output shape: which agent owns a path, in plain text, including the literal `NOBODY`
(`check-domain.sh` line-marked `if [ "${1:-}" = "--resolve" ]`; cases (c) and (d) in
`test-check-domain.py` assert the literal `NOBODY` and a non-empty stdout at exit 0).

The resolver's flag is therefore **`--which-config`, never `--resolve`** (D-07). The confusion this
avoids is live and not hypothetical: the BRIEF's D-01 prose already argues about a harness checkout
returning "NOBODY" versus "exit 2" in a paragraph about config resolution. **Documentation that
names either flag must name its tool with it** — never a bare `--resolve`, and never a bare
`--which-config`.

## Contract 5 — the path argument

`--which-config` takes a path. It MUST accept a relative path and resolve it as the module resolves
every other path (`os.path.realpath(os.path.abspath(...))`), so that `--which-config .` works from
inside the checkout under test. An operator standing in the product checkout typing `.` is the SC-12
gesture; requiring an absolute path makes the UAT step a paste rather than a look.

## The prototype gate

**`needs_prototype: false`.**

- The surface is one non-interactive command with one line of output. There is no screen, no
  control, and no multi-step flow a person operates — a prototype of it would *be* the tool, built
  early and outside the plan.
- The manifest declares no design-system `conventions:`, so there is nothing to build a
  high-fidelity prototype *on*; the applicable design system here is `factory_cli`'s grammar, which
  is what this document writes against.
- SC-12 already puts the real command in the operator's hands at UAT. The prototype gate exists so
  the operator judges the experience before it is built; for an eight-string surface, this contract
  is the thing to judge, and it is in front of them at the same signature.

Rejected: a mocked terminal-transcript prototype showing the eight outputs. It would restate this
document's tables as prose with a `$` in front of them, and could not be checked against the code.

## Open questions

- **Q1 — RESOLVED by D-07.** Asked whether to rename the resolver's flag off `--resolve` to end the
  homonym with `check-domain.sh --resolve`. The plan adopted `--which-config`; Contracts 4 and 5 are
  written against that name. No open question remains.
