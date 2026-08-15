# Operator's answers — FEAT-15-domain-product-base — 2026-08-10

Relayed by the main session. Sections marked **RULED** are the operator's words and are the
authority for the revision. The section marked **ORCHESTRATOR'S READING** is mine, pinned so pm
does not have to guess, and flagged upward for correction at signature.

## Q1 — RULED: OPTION (c). Add explicit control-plane entries. Do NOT change the inference grammar.

Prefix inference stands exactly as ruled in the grilling: `.harness/` and `.claude/` are
control-plane, everything else resolves against the product checkout. On top of that, harness's own
non-prefixed control-plane paths are named explicitly so the routes survive:

- `docs/harness/**`
- `docs/PRINCIPLES.md`
- `README.md`
- `.github/**`

**Option (b) — the `harness:` prefix marker — was DECLINED**, for the reason product-lead gave: it
changes the value grammar of every future manifest entry, which is the schema change ruling 1
existed to avoid.

**Option (a) — ship as written — was DECLINED.** Revoking documentor's route to the constitution and
SPEC, and dev-ops's route to `.github/**`, is not an acceptable cost.

### The accepted cost of (c) — carry it into the BRIEF, do not design it away

This is now **one more place to remember**. A future harness-owned path that starts with neither
`.harness/` nor `.claude/` must be added to this explicit list, or it silently becomes a product
path. **State it in the BRIEF as an accepted risk. Do NOT add machinery to detect it.**

This replaces — it does not remove — the accepted risk already carried from grilling ruling 1. The
risk is the same shape, narrowed: it now bites only paths outside both the two prefixes and these
four entries.

## ORCHESTRATOR'S READING — the four entries are DUAL-BASE, not control-plane-only

**pm must build to this reading, and the operator may correct it at signature (raised as Q7).**

Three of the four named paths — `docs/**`, `README.md`, `.github/**` — are **also** three of the 12
product-shaped globs. Read as *instead of* product, a product checkout's `README.md`, its `docs/`
and its `.github/**` would resolve to nobody, and dev-ops could no longer write a product's CI —
which re-creates the original defect for exactly the paths this ruling exists to protect.

The plain reading is **in addition to**: an entry named in the explicit list resolves against
**BOTH** bases. Every other non-prefixed glob stays product-only. Every `.harness/`- or
`.claude/`-prefixed glob stays control-plane-only.

**The corrected mirror-image assertion set** (this is a different set of assertions, not a
re-wording — the plan's SC must be re-cut, not restated):

| Glob | Matches inside harness | Matches inside a product checkout |
|---|---|---|
| `src/**`, `web/src/**`, `tests/**`, `evals/**`, `supabase/migrations/**`, `Dockerfile`, and the `src/**`-derived entries | **no** | yes |
| `.harness/**`, `.claude/**` | yes | **no** |
| `docs/harness/**`, `docs/PRINCIPLES.md`, `README.md`, `.github/**` | yes | yes |

## Q2 — MEASURED, NOT ASSERTED. It dissolves.

The operator required a measurement rather than a claim. Method: `check-plan-routes.py`'s own
parser and plan discovery, with **only** `resolve_agents` swapped for option (c)'s rule — an
in-harness path resolves normally iff it is control-plane under the revised rule (the two prefixes
plus the four entries above), and otherwise returns NOBODY.

**Result, measured on the working tree at `96d5d5c` (branch `chore/203-end-copy-distribution`),
across the 9 plans `check-plan-routes.py` discovers there:**

- `0 violation(s)` — unchanged from the unpatched baseline on the same tree.
- **ZERO paths lose their grant.** Every literal path in every task of every plan is either
  control-plane under the revised rule, or already resolved to NOBODY today.
- The four tasks that flipped under option (a) now resolve normally: FEAT-12 T-12 and T-14 and
  FEAT-14 T-09 and T-10 all report `granted to harness-documentor`.

**Three honest caveats on that measurement — the clean number must not carry more weight than it
earned.**

1. It models the RULE, not the implementation. The implementation is unbuilt and
   main-session-direct. The real `check-plan-routes.py` re-run is only possible after T-04 lands,
   and the plan must require it there.
2. It covers PLAN ROUTING, which is what the CI check reads. It does not exercise day-to-day agent
   writes. `docs/PRINCIPLES.md` and `.github/**` appear in no task's `files:` in any plan, so they
   contributed nothing to this number — they are in the list to protect live write routes, not plan
   rows.
3. **It is silent on the PRODUCT side.** The simulation only ever models in-harness resolution, so
   it cannot see the dual-base error described above. That error would land entirely on the product
   side, and only an SC can catch it.

## What exists in harness today — measured, and it validates the operator's list

Checked at `96d5d5c` for every product-shaped glob's root:

- **PRESENT:** `.github/`, `README.md`, `docs/` (and inside `docs/`, everything except
  `docs/PRINCIPLES.md` lives under `docs/harness/`).
- **ABSENT:** `src/`, `web/src/`, `tests/`, `evals/`, `supabase/migrations/`, `Dockerfile`.

Two consequences worth stating rather than rediscovering:

- **The operator's four-item list is complete against the present tree.** No fifth entry is needed
  today; in particular `Dockerfile` is product-shaped and granted to dev-ops but does not exist in
  harness, so it needs no control-plane twin. The accepted-risk sentence above is what covers it if
  one is ever added.
- **The grilling's phrasing "harness has its own `src/` and `docs/`" is loose.** `docs/` is real;
  `src/` is not. `check-domain.sh` matches path STRINGS, not existing files, which is why the probe
  `harness-documentor -> src/main.py` exits 2 against a directory that does not exist. The
  mechanism claim holds; the file-existence claim does not. pm should not repeat it as written.

## Unchanged and still binding

- Every task stays `execution_mode: main-session-direct`. No build squad. No task dispatches an
  agent at `check-domain.sh` — DEC-174.
- Ruling 2: a path under `workspace_root` for a repo not in `fleet.yaml` is REFUSED.
- Ruling 3: an unparseable `fleet.yaml` fails closed on every write.
- `/tmp` and anything outside both bases keep today's no-verdict behaviour.
- The mirror-image bug stays a success criterion, in the corrected three-row form above.
