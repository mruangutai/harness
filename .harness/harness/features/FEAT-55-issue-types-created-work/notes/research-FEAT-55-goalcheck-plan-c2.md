# Goal-check c2 — does FEAT-55's REPAIRED plan deliver the operator's stated intent?

**YES — every `## Settled` clause, both out-of-scope items and all five creation routes have an owning
task or decision, and no gating finding stands.** All eleven prior findings (F-01..F-09, N-01, N-02)
are CLOSED in the plan text itself, verified by reading `plan.yaml`, not by trusting the repair notes.
Three findings open, highest severity **med**: the one property the repairs added — absent provenance
is never typed — is pinned by no automated gate, because REQ-10 carries **no success criterion at all**.

Graded against `.harness/notes/grilling-issue-types-2026-09-04.md`, not the BRIEF. Anchors are
working-tree line numbers in `plan.yaml` at sha256 `4e70d074…` (untracked; the sha is the baseline).

## Prior findings — closed, each cited to the plan text

| F | Status | Plan text that closes it |
|---|---|---|
| F-01 high | **CLOSED** | Adoption recorded positively in the same receipt act as the number: T-04 §7 `:544-553`, T-08 §8 `:865-870`. Both backfills exclude `"adopted"` forever (`:535-536`, `:874-875`) and `source_issues` (`:536`, `:874`). Fixtures T-03 H `:406-408`, **H2** `:409-415`, T-07 **F** `:754-762`. |
| F-02 med | **CLOSED** | T-10 `verify` `:930-940` resolves `github.repo` from `.harness/harness.json`, requires exactly one verdict line naming it (`:933-934`), fails on a create mention (`:935`), and adds a `PATH`-stripped leg that must SKIP with exit 0 (`:936-938`). |
| F-03 med→high | **CLOSED** | The pinned 511-char row covers capability + declared names, the issue-level identifier reads named as existing practice, and the probe's type read-back. Re-derived from the **loaded** document here: T-11 §3 and T-12 §1 byte-identical, sha256 `7f065a7a5225`. T-12 `verify` machine-compares the two copies. |
| F-04 med | **CLOSED** | Zero-create diagnostics asserted on all three commands: T-03 D `:385-389`, T-05 D `:604-608` (exactly one `issueTypes` argv, zero diagnostic lines in available mode) and F `:617-623`, T-07 G `:763-768`. T-06 §2 `:649-654` no longer overclaims. |
| F-05 med | **CLOSED via D-18** | D-18 + rewritten D-02; `"feature": "Task"` in T-02's table; fixtures carry a `feature`-change_type task and expect `IT_task` on both sub-issue routes (T-03 A, T-07 A). Override key `feature` stays legal (T-01 assertion 5). |
| F-06 low | **CLOSED** | T-01 `verify` `:158-161` greps all fifteen values plus `UnknownWorkNature`. |
| F-07 low | **CLOSED** | Receipt gated on `state == "available"`: T-06 §5 `:669-676`, skipped-item line only there (§6). Behavioural halves: T-05 C (no receipt file in compat mode) and F `:617-623` (compat rerun makes three MORE creates). |
| F-08 low | **CLOSED via D-19** | Read-only default + `CAPABILITY PRESENT` verdict T-10 §5 `:967-971`; `--create-in` must equal the configured repo; T-09 forbids the flag in the registered `cmd`. |
| F-09 low | **CLOSED** | Compatibility controls inside the gates: T-04 `verify` `:442`, T-06 `verify` `:636`, T-08 `verify` (`test-factory-decompose.py`, `test-factory-gh.py`). |
| N-01 high | **CLOSED** | Key-presence reading is now **prohibited** where it was mandated: T-04 §6 `:509-541`, T-08 §8 `:848-879`, both enumerating four readings with `ABSENT → never typed, on no route` (`:514-515`, `:853`). D-20 `:124-132` and amended D-10 `:84`. Fixtures T-03 **J** `:418-430`, T-07 **H** `:769-780`. |
| N-02 low | **CLOSED** | The backfill set is inside `missing_types`: T-04 §4 `:479-483`, T-08 §6 `:832-835` — "a backfill whose type name the repository does not declare is refused by exactly this check and by no other". |

## Coverage re-derived from the intent artifact

| Intent unit | Owner | Verdict |
|---|---|---|
| Settled 1 — overrides required; defaults Bug/Feature/Task | D-01, D-03, D-04, D-12, D-18; T-02, T-01 1–6, T-04 §2/§4, T-06 §3, T-08 §4/§6 | met |
| Settled 2 — feature/factory parents default `Feature`, same override key | D-18, D-12 (`parent`); `type_for_parent`; T-03 A/E, T-07 A/D | met |
| Settled 3 — unavailable → labels exact, one diagnostic per invocation | D-15; T-04 §3 `:470-472`/§5 `:495-499`, T-06 §2/§4/§5, T-08 §5 `:822-826`/§7; T-03 C/D/I, T-05 C/F, T-07 C/G | met |
| Settled 4 — active → no competing `bug`/`chore` | T-04 §5, T-06 §4 `:666-667`, T-08 §7; T-03 B, T-05 B, T-07 B | met |
| Settled 5 — create-then-type-fail → rerun classifies, never deletes/duplicates | D-10, D-13, D-20; T-04 §6, T-06 §5, T-08 §8; T-03 G, T-05 E, T-07 E | met |
| Out of scope (a) — never change adopted/source issues | positive provenance (D-20) + `"adopted"` marker on both routes; `source_issues` excluded twice | honoured in plan text, **ungated — N-03** |
| Out of scope (b) — never bootstrap Issue Types | no task writes a type definition; `refusal_text` only names the repair; probe creates an *issue* under opt-in only | honoured |
| Routes: feature parent · task sub-issue · backlog · factory parent · factory task | T-04/T-03 · T-04/T-03 · T-06/T-05 · T-08/T-07 · T-08/T-07 | 5/5 owned |

No internal contradiction found between the 20 decisions: D-10 was the only one carrying the
overturned ordering and is amended (`:84`); D-13 scopes the backlog receipt to a net-new file with no
legacy population, and D-20 `:127` scopes itself to `feature.json`/`factory.yaml`, so the two do not
collide. Every rewritten `intent:` still matches its `verify:` — T-03/T-05/T-07 remain RED-checks,
T-04/T-06/T-08 run the new file plus the compatibility control. Mechanical evidence: `yaml.safe_load`
loads (12 tasks, 20 decisions, `status: plan`, `approval: {status: pending}`, no `panel:`), every
`traces:` entry is inside REQ-01..REQ-11, and `check-plan-routes.py <plan>` → `0 violation(s)`, exit 0
(T-12's DEC-174 line is the expected carve-out output).

## Findings

**N-03 · med · the out-of-scope guarantee is pinned by no gate, and REQ-10 has no SC.** The repairs'
central safety property — absent or `"adopted"` provenance is never typed — lives only in task prose
(`:514-515`, `:535-539`, `:853`, `:874-877`). T-03's and T-07's `verify:` require only `ast.parse` plus
a non-zero exit, which *any* failing assertion satisfies, so a test file omitting case **J**/**H2**/**F**
greens every gate; T-04/T-06/T-08 then run that file and go green too. And REQ-10 is traced by tasks but
graded by **no success criterion**: no SC in `BRIEF.md` names an adopted parent, `source_issues` or
provenance (grepped — REQ-10 appears once, at `BRIEF.md:58`). Consequence: the one thing the operator
put out of scope can ship with nothing red. Cheap plan-time repair, the F-06 precedent: add per-case
greps to T-03 and T-07 `verify:` (e.g. the string `adopted` and a legacy-receipt case marker), and at
signature give REQ-10 an SC with `evidence: integration`.

**N-04 · low · T-05 case E's assertion admits the failure state it exists to exclude.** Case E `:614`
asserts the first run "left typed false **or absent**", while T-06 §5 `:669-676` mandates number and
`typed: false` written in one act — absent is therefore unreachable, and the disjunction also passes
when *no receipt entry was written at all*, which is exactly what makes the rerun duplicate. The
consequence is caught by a sibling assertion in the same case (zero `issue create` argv on the rerun),
hence low. Repair: assert `typed` is exactly `false`.

**N-05 · info · the backlog route spells the pre-apply state `false`, the other two spell it
`"created"`** (`:671` vs `:511`, `:850`). Dispositioned as the c2 repair's advisory: **not a safety
finding.** `backlog-issues.json` is net-new and keyed by the item string, so absence means "not created
yet" with no legacy population to misread, and D-20 does not quantify over it. One vocabulary would be
tidier; nothing rests on it.

**N-06 · info · issues created in compatibility mode carry no provenance, so they are never typed if
the repository later enables Issue Types.** T-04 §6 `:540-541` keeps the receipt byte-identical in
compat mode, which clause 3 requires; D-20 then reads those entries as unknown provenance. No intent
clause asks for retro-typing (the goal is issues Harness *creates* get the type), so this is an accepted
consequence, not a gap — recorded so nobody discovers it as a surprise after a repository is enabled.

**Carried forward — the c2 repair's Q1: NOT A FINDING.** D-20 accepts that a genuinely Harness-created
issue recorded before this ships is never typed by any rerun. Judged on the intent artifact, not
deferred: Settled clause 5 conditions on "creation succeeds but **required type assignment fails**", and
a pre-ship issue never had a required assignment to fail, so the clause does not reach that population.
Out-of-scope item (a) does reach it, and for absent provenance the two cases are indistinguishable — so
the fail-safe direction is the only one that honours the operator's own boundary. A retro-typing pass
would need a human-supplied provenance list and is separate, opt-in work.

## Byte-unchanged verification

`sha256sum` on both files, before any read and again after writing this note:

- `plan.yaml` — `4e70d07440d2682af77651f8dca36a1d092f7fa2f1ae9f8dad70a30530c93481` at both points.
- `BRIEF.md` — `e1d4e9195ff24fda780ff9d8ca7a5527c25ec183e7826f516ff23e144c8f56be` at both points.

`approval.status` is `pending`, the feature `status` is `plan`, and `panel:` is still absent — read out
of the loaded document, not assumed.

## Open questions for the operator

- **Q1 (non-blocking, N-03):** REQ-10 has no success criterion. Add one at signature
  (`verify: automated  evidence: integration`, carried by T-03 H2/J and T-07 F/H), or accept REQ-10 as
  graded by inspection of the diff alone?
