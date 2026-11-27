# Distill — harness-pm — FEAT-2452-gh-one-transport

**BLUF:** 2 batches applied (craft 6 ops, repository 1 op). Counts stay at cap: craft P 15→15, G 15→15, O 10→10; repository (harness) P 13→13, G 15→15, O 1→1. Nothing was added to a full section without displacing something. This was a distill run: I reviewed no diff, ran no suite and made no git writes.

## Batches
- craft: `13417dc3373273b5f2828cff4075f719934d2a7381ff1ac643179691fdb1e91e` → `.harness/expertise/harness-pm.md`
- repository harness: `066c48114965bceb7285e0e9dab7092a31395f726eefe6cfbb8c4d066c274916` → `.harness/harness/expertise/harness-pm.md`
- receipt (both batches): `.harness/harness/features/FEAT-2452-gh-one-transport/notes/expertise-receipt-fd6ae0e7a80f05243080602934c00a1d5fc25004ac71207359c0a37e44f69c62.json`

## Dispositions (observations by log line)
| Source | Disposition |
|---|---|
| obs L3 — removing an override pin lets old code fall back to the gh binary on PATH; needs an offline PATH sentinel | Rejected. It is one case of craft G-20 (isolating the inherited environment). The "baseline pass is not discriminating" half is already covered by O-07 and O-13. |
| obs L4 — a kept DEC's present-tense implementation sentence is falsified by a settled deletion | Applied: craft **replace P-16**. The old P-16 covered signed plan prose; it now also covers each kept decision's whole entry, at plan time. |
| obs L5 — gh label create already-exists output has no 422 | Rejected. This is a fact about one external CLI (recipe-like), and it will rot. |
| obs L6 + L8 — the 50-line machine-field cap; amend does not enforce it; derive file lists from plan.yaml | Applied: repository **replace G-03**. I confirmed `MACHINE_LINES_PER_TASK = 50` in check-plan-routes.py, which plan_merge/check.py also runs. |
| obs L7 — SC requires var-absent while the confinement strips by name; strip by prefix instead | Rejected. It is a single design instance with no reusable rule. |
| obs L9 — dispatch-named receipt path lies outside the pm domain; tee only works with a literal absolute path | Rejected as its own entry. The literal-path part is already repo G-02 and the grant check is already craft G-02. The "inside your write grant" clause went into the new G-21. |
| obs L10 — a red from a different failure point discharges the SC text but not the task's reading | Applied: craft **replace O-13**, which now adds "an earlier failure point reddens before the one the task names" to its list of reds that only look discriminating. The free-mutant half is already O-07. |
| obs L11 — git-archive pin export plus prior-commit copy reproduced the red; field-by-field cases | The first half is already O-07 and G-19. The second half went into LC-1 (P-18). |
| obs L12 — builder note superseded inside the same commit | Rejected. Grading code over notes is already implied by P-05 and P-17, and a new entry here would be weaker than every survivor. |
| LC-1 — per-field enumeration of an external payload's validity, plus identity binding of related objects | Applied: craft **add P-18**, which displaces **drop P-15** (byte-for-byte preservation criteria are narrow and rarely fire). It is kept separate from P-04, which is about per-item assertions over N items rather than fields of one payload class. |
| LC-2 — full writer stdout must go into a durable receipt before temp files vanish | Applied: craft **add G-21**, which displaces **drop G-04** (a runner ignoring a production-only flag, which is a narrow tooling trap). This is craft because it holds in any repo. |

## Open
None. No harness defects surfaced during the distill.
