# Pilot SC-4 — Base defect rate and cost per incident

> **Instrument:** `kaya-ai` git history, mined 2026-07-26.
> **Window:** 2026-07-04 → 2026-07-25 (21 days, 470 commits).
> **Purpose:** supply the number that BUILD.md § Pilot's SC-4 weighs against SC-1's measured cost. The
> reviewers assumed a ~20% defect rate and marked their own dollar figures ±2×; this replaces the
> assumption with data.

---

## Method

`kaya-ai` merges two ways — 44 merge commits and 109 squash-merged first-parent commits — so both had to
be counted or the denominator would be half-right.

| Quantity | Definition | Count |
|---|---|---|
| **Feature units shipped** | `feat` squash-PRs on master (22) + `feat/*` merge-commit PRs (21) | **43** |
| **Escaped-defect units** | `fix` PRs landed on master, 18 of 19 citing a filed issue | **19** |
| Reverts | — | **0** |
| `fix/*` or `hotfix/*` branches | — | **0** |

An escaped defect here means: **it got its own PR after the feature merged, and in 18 of 19 cases it was
filed as an issue first.** That is a defect that survived the development loop, was noticed later, and
cost a separate cycle to repair. It is exactly the class the harness's gates exist to prevent.

---

## Result 1 — the base rate is 44%, not 20%

```
19 escaped-defect PRs ÷ 43 feature units  =  0.44 defects per feature
```

**More than double the reviewers' assumption.** This cuts *toward* gating, not away from it: the CTO
review's economic case against the org rested on a 20% rate, and at 44% the expected loss from shipping
ungated is roughly twice what that analysis assumed.

Cadence over the window: **2.0 features/day and 0.9 escaped defects/day.**

## Result 2 — cost per incident

| | PRs | Lines | Avg per PR |
|---|---|---|---|
| Features | 22 (squash) | +21,473 / −818 | **+976** |
| Escaped-defect fixes | 19 | +2,109 / −236 | **+111** |

**Remediation consumed ~9.8% of feature line volume.** Fixes averaged 111 added lines across 2–4 files —
small in code but each carrying diagnosis, reproduction, a regression test, review and a merge. Call it
1–3 hours each; that is an estimate, not a measurement, and it is the weakest number here.

At ~0.9 incidents/day that is roughly **1–2.7 hours/day of rework**, or 15–25% of a working day.

---

## Result 3 — which gate would have caught what

The decision-relevant analysis. Each of the 19 classified by the gate most likely to have caught it.

| Gate | Defects | Examples |
|---|:---:|---|
| **Code review** | **9** | `_apply_property` mutating `proposed_label` (#135); `dangling category_ref` **failing open** (#92); missing confidence guard (#139); citation not validated (#140); no fallback for garbage OCR (#142); PDF effect race on destroyed doc (#60) |
| **UAT / hand-test** | **5** | skeleton→content layout jump; focus lost when a row's status flips (#84); mapping picker ignores de-select on re-click (#91); `clearable={false}` not gating toggle-off (#104); inconsistent category label (#96) |
| **Security review** | **1** | **CSV formula injection in the Stessa export (#283)** |
| **AI eval** | **1** | refute agent not told which amount to cite — a prompt defect (#245) |
| **Architecture review** | **1** | correction harvest coupled to the export blocker gate (#150) |
| **Spec / BRIEF gap** | **1** | property-resolution strategy never specified (#149) — the largest fix at 315 lines |
| **Test maintenance** | **1** | `Decimal`/`float` TypeError in a test (#175) |

### What this implies for the org question

| Coverage | Defects | Share |
|---|:---:|---|
| Addressable by **the four artifacts** (review + UAT + BRIEF) | **15** | **79%** |
| Needing **org-specific gates** (security reviewer, architecture review, eval) | **3** | 16% |
| Neither | 1 | 5% |

**The four artifacts address roughly four-fifths of the observed defects.** The 15-agent org's marginal
contribution over them is about 3 defects in 21 days — and per the reviewers' estimates it costs 4–10×
more per feature to obtain.

Two of those three are worth noting individually, because they are the org's strongest evidence:

- **The CSV injection (#283) is a genuine security defect in an export path** — precisely what a
  self-scoping security reviewer is for, and the kind of thing a general code review misses because it
  is not a *correctness* bug.
- **The prompt defect (#245) is unreachable by every gate in either arm.** `kaya-ai` has eval helpers but
  no eval harness, so SPEC §9.1's declared gap is real here and neither the artifacts nor the org
  currently close it.

---

## Honest limits

Stated because the temptation is to read this as more conclusive than it is.

1. **"Which gate would have caught it" is my inference, not evidence.** Real-world code review catches
   perhaps 30–60% of the defects it *could* catch, so the 9-defect code-review column should be read as
   an upper bound. Applying a 50% catch rate to the addressable 15 gives ~7–8 defects actually prevented.
2. **Cost per incident is estimated.** Line counts are measured; the 1–3 hour figure is not.
3. **21 days is a short window on a young, fast-moving repo**, where defect rates are naturally high.
   A more mature codebase would likely show a lower rate — so 44% is probably an upper bound for
   `kaya-ai`'s own future, let alone other projects.
4. **One of the 19 (#175) is test maintenance, not an escaped product defect.** Removing it gives 18/43 =
   42%; the conclusion does not move.
5. **The window contains no production incidents** — no reverts, no hotfix branches. Every defect was
   caught by the operator or a filed issue, not by a customer. That is a meaningfully *cheaper* class of
   defect than the "found in production" scenario the reviewers priced.

Point 5 is the one that cuts hardest against the org: the cost model assumed a rework *day* per escaped
defect. The data shows ~111 lines and no production exposure — an hour or three, not a day.

---

## Bearing on the decision

| SC | Finding |
|---|---|
| **SC-4** | Base rate **0.44 defects/feature**; ~111 lines and 1–3h per incident; ~10% of feature line volume spent on rework; **zero production incidents** |
| **Implication for SC-1** | The org must justify itself against ~1–2.7h/day of rework, of which the four artifacts plausibly prevent 50–79%. Its marginal value is ~3 defects in 21 days — the security finding, the architecture coupling, and one prompt defect it cannot currently catch either |

**This does not settle the question, and it was not supposed to.** It replaces a guessed 20% with a
measured 44%, replaces "a rework day" with "111 lines and no production exposure," and shows the
artifacts capture most of the addressable value. SC-1's measured cost is still required — but the bar the
org has to clear is now a real number rather than an assumption.
