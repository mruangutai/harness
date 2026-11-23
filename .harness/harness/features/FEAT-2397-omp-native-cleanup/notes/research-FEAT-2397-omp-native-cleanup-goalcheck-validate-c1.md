# FEAT-2397 goalcheck c1 — FAIL

All 23 decision dispositions now land; the c0 doctrine and changed-function defects close. **SC-04 remains partial on the exact executed-command receipt**, not on the implementation or per-target red/green results. No new scope ruling or suite rerun is requested.

Review: **9c38040397bb115583e71b13f1a7ca4bf2f10c2e**; comparison base: **522c94b2b79e5e2021cb670910772428c17914b0**; c0 pin: 53a89eb70251d1529dbffd8e50959c4590a032f7. Requirements, authority, source and committed build receipts were read with git show at the review pin. **F** means this feature directory; **N** means F/notes. Fresh panel evidence below is explicitly post-pin, never represented as committed evidence. PM ran only immutable source/receipt comparisons, not suites, builds, lint, formatting or live-host probes.

## Perspectives and coverage

- **operator — partial:** SC-03/06/08 met; SC-04 partial. Native model authority, every-yield validation and current instructions agree; the required exact transient-check command is still not in its committed receipt.
- **code maintainer — pass:** SC-01/02/05/09/12 met. Context/boundary regressions, retained ABI/history/data, exhaustive changed-function bars and evidence preservation are supported.
- **orchestrator — pass:** SC-07/10/11 met. Advisory behavior and authorized real-host numeric child observation are supported; PM does not author human acceptance.

All 12 criteria trace to shipped files through pinned plan tasks: T-01→01/02/03/06/07/09/12; T-02/T-03→04/05/09/12; T-04→10/11/12; T-05→08/09/12; T-06→10/12. No perspective or SC is orphaned.

| SC | Outcome / method | Evidence and limits |
|---|---|---|
| SC-01 | met / automated | tests/integration/test-inject-expertise.py:276,320,346,359,432; N/t01-red-green.md A–C and raw red-A/B/C/green-inject-expertise receipts: complete context bytes, newline/cap tiers, checker CLI/PID/error/no-op/bootstrap cases. QA c0 integration95/95; these subjects are unchanged to c1. |
| SC-02 | met / automated | tests/unit/omp-hooks.test.ts:4560,4576,4593,4606; N/t01-red-green.md D and raw red-D/green-D: one decode, carried context, hidden once-only delivery, retries, malformed/envelope rejection. QA c0 bun247/0; fresh c1 unit manifest records test-omp-hooks.py exit0 at this pin. |
| SC-03 | met / automated | test-dispatch-guard.py:92,105,133; test-validate-digest.py:693,1167,1258,4208; test-check-domain-grant.py:397–410; native-gate runtime. N/t01-red-green.md E/H/I/J/K and QA c0 integration95/95. Raw red-H:409/412/426 fail invalid truthy yield, valid correction settlement and held-child refusal;411/428 are preserved claim-retention behavior, not missing fail-first evidence. Subjects unchanged to c1. |
| SC-04 | partial / inspection | Pinned N/c1-evidence/t02-transient-522c94b2.txt:1–22 gives16 failed targets plus positive guidance-count row, exit1; t02-transient-f5c89121.txt gives17 OK rows and exit0. All eight T-02-owned file blobs match f5c8912152c23e03904299af4c9e2cd8800ff536→pin. Diff preserves HARNESS and script/cwd fallback rules. However neither c1 receipt contains the executed CHECK command; N/T-02-red-green.md:3 still points only to plan tasks[1].verify and a /tmp script. The signed criterion explicitly requires the receipt to include the exact check. T-02/Main owns packaging, not source repair. |
| SC-05 | met / automated | test-harness-yaml.py:504; test-gen-decisions-index.py:753,786; test-validate-feature-json.py:433,458,470. Pinned T-02-red-green.md:342–368 and QA c0 green root-negative suites preserve explicit old-env nonredirect assertions; no fabricated new fail-first obligation for unchanged behavior. |
| SC-06 | met / automated | test-check-omp-port.py:55–85 reads through the OMP config accessor; .omp/config.yml:18–22 pins the string off; missing/on/eval mutants fail. N/t01-red-green.md G and red-G/green-G give31/35→35/35; QA c0 integration green, subjects unchanged. |
| SC-07 | met / automated | omp-hooks.test.ts:3008,3068 onward; harness-hooks.ts:1140,1957 onward. N/t01-red-green.md L:37 baseline failures, with semantic handler failures distinct from signature-absent helper rows. Native finite tokens, equality/default/custom thresholds, repeat/retry/exclusion/result/postDomain witnesses; QA c0 bun247/0 and fresh c1 unit file exit0. |
| SC-08 | met / inspection | All23 owning rows below; DECISIONS-INDEX.md affected tails20–29 words with durable successors; SPEC.md:808–815 correctly assigns model refusal to native off; DECISIONS.md:7117–7119 uses tool_input.task. harness.md:137–143 obeys settled asynchronous Main edge; constraints.md:30–34 carries stronger-model open_questions route. Native floor/session estimates in DEC-198/201; org.html:223–227. Code reviewer c1:10 independently concurs. |
| SC-09 | met / inspection | Code reviewer c1:11 and pinned base diff: frozen prior/context fixtures, Expertise data/writers, BUILD and DEC-108/109 unchanged; copied dispatch/inject bootstraps identical; six bin comment-module executable ASTs identical (docstrings excluded explicitly, not called byte-identical). Live harness_yaml.py:789–798 systemMessage; DECISIONS.md:7933–7943 retains internal request/tool/policy-decision ABI and authored .claude trees. Model helper/call and JSONL reader removed without shim; c0 doctrine residuals repaired. |
| SC-10 | met / uat — recorded authorized Main observation | Pinned N/research-omp1910-observation.md:11–20,25–48,59–69,81–90: launcher /Users/molchairuangutai/.bun/bin/omp, omp19.1.0, real command,7/7,empty stderr,exit0; nested child8wcr tokens6827/window500000/percent1.3654, distinct flat main3z54 tokens13653/window1000000/percent1.3653. Signoff:36–38 authorizes Main. Observed tree59c3becfd751ea2f2419ba82c4f832367b36be33 is not relabelled c1: probe81a28131c1e233c415aacdf6162faa9583344236 and companion8c3e9153faf876d97e3ef4c0c25f6c03a54c1e6d exactly match this pin. Receipt records issue2194 CLOSED/closedAt2026-11-23T05:42:04Z and closure-comment URL. No live host/issue rerun. |
| SC-11 | met / automated | test-session-accessor-probe.py:82,98,133,144,185,193; N/t04-red-green.md/raw per-function baseline and10 semantic mutants. Identity independent of usageDefined, numerical validation independent of path, defined-usage child reaches remaining checks;82 green checks and QA c0 unit green. Fresh c1 unit receipt covers this file. |
| SC-12 | met / inspection | Pinned focused receipts, N/t05-verify-literal.txt cumulative gates/typecheck, N/c1-evidence actual-base T02/grade/corpus/unit executions, and committed c0 runs/QA manifests exist at pin. Canonical93/93 is a narrower selector, not proof of all changed functions: code reviewer c1:18–58 independently grades171 changed bodies (8 production>=4,163 tests>=3), including both validate-digest functions and repaired T03 functions. See provenance distinctions below; green obligation is not inferred from red clone runs. |

## Decision dispositions — exact pinned owning clauses

Each row is the unique plan decisions_affected row identified by DEC/disposition/clause/successor/reason; there are no duplicate DEC rows. Every evidence cell means **9c38040397bb115583e71b13f1a7ca4bf2f10c2e:.harness/harness/docs/DECISIONS.md:<lines>**, not a mutable-tree read. All rows use inspection. Any partial/not_met row would route to DECISIONS-owning **T-05**; none remains.

| DEC / disposition | Outcome | Owning-clause landing |
|---|---|---|
| DEC-11 / amend | met |153–170: native capability/policy split and extension registration replace settings wiring.|
| DEC-59 / amend | met |647–658: body prose is not parsed; deleted Skills section stays historical.|
| DEC-63 / amend | met |705–720: autoloadSkills/full-content/no-obedience contract; old host evidence bounded.|
| DEC-64 / amend | met |724–729: before_agent_start, retained request label, context-only response.|
| DEC-81 / amend | met |972–984: historical interpolation/20–200; live stdin/exit2 adapter and native32. Not struck.|
| DEC-101 / amend | met |1477–1497,1511–1513: native delivery and bounded original settings/zero-dependency measurements.|
| DEC-110 / amend | met |1761–1789: historical settings deployment replaced with native identity-keyed gate; cwd-independent root retained.|
| DEC-111 / strike | met |1803–1813: numbered strike names DEC-233; live DEC-202 provisioning citation repointed6342–6345. BUILD948 remains authorized history.|
| DEC-112 / amend | met |1819–1822,1842–1855: removed settings merger historical; surviving tools/onboarding retained.|
| DEC-127 / amend | met |2724–2743: old repro bounded, every yield validates with no retry bypass.|
| DEC-144 / amend | met |3334–3342: unconditional native gate replaces fifth-settings prerequisite.|
| DEC-151 / amend | met |3543–3555: native Bash gate/internal ABI; caller-bound Expertise policy retained.|
| DEC-155 / amend | met |3657–3673: stronger-model open_questions route, native off binds Main; both former refusals deleted.|
| DEC-156 / amend | met |3692–3717: complete model bullet replaced; digest/checkpoint rules retained.|
| DEC-173 / amend | met |4454–4460,4471–4475: historical forced retry; bypass closed, honest gate reporting retained.|
| DEC-198 / amend | met |5910–5919,5936–5958: native finite session estimate, existing resolver/default/strict threshold/advisory.|
| DEC-199 / amend | met |6012–6041: native claim lifecycle, both stop-sequence paragraphs say every yield, no once-only bound; core/locking retained.|
| DEC-201 / amend | met |6190–6226: native replacement, retired JSONL limitation, upstream10098/v18.0.11/floor; source versus host evidence separated. Original no-wait/measurements/bands retained.|
| DEC-208 / amend | met |6868–6874: bypass deleted; append-only/checkout-binding rules retained.|
| DEC-214 / amend | met |7074–7079,7117–7119,7126–7134: native injection, corrected task request spelling, in-process four-file checker/unknown states, both anchors retained. c0 partial closes.|
| DEC-218 / amend | met |7239–7275: residues/non-OMP TTL/quarantine removed history; exact OMP lineage/unreadable-registry policy retained. Not struck.|
| DEC-222 / amend | met |7421–7447: native provisioning/command door replaces settings/adapter rationale; two-skill seam retained. Not struck.|
| DEC-233 / amend | met |7910–7919,7925–7943: actual runtime/default/alias/bypass deletions; retained internal ABI/authored directories.|

The13 keep rows are not disposition-graded: DEC-65/123/126/145/174/188/202/205/219/234/237/253/256. DEC-202's required citation repoint is a strike consequence, not a policy change. DEC-204 is byte-identical to base; Q2 resolves the signed blocking word as drafting error, not authority to amend DEC-204.

## Provenance, prior findings and gate limits

- **Doctrine finding closes (substance/med, T-05):** directly inspected all23 tails, corrected SPEC/DEC214 and async Main command. N/t05-doctrine.md's dated correction explicitly preserves and retracts the prior false completion claim; the old bytes are not silently rewritten as if true.
- **Complexity finding closes (substance/med, T-03):** code reviewer c1 independently reproduces c0 changed-body155 and measures c1 body171. Canonical code_grade.py:416–429 selects new/no-preimage or grade-worsened records, excluding unchanged/improved grades; its93 is binding for DEC-209, while signed SC12's all-new/changed bars require the exhaustive171 selector. The78 omitted functions are individually listed/graded, including validate-digest hook_mode4/_pass_through4. All14 files represented in committed grade93 JSON have identical b9a8c3ad→pin blobs; no Python/runtime/workflow/test/doctrine source changed over that interval. Receipt transfer is not a claim of re-execution.
- **Clone reds remain red:** independently normalized and compared all FAIL/(fail) lines from pinned unit-522c94b2-clone-cleanenv.txt and unit-b9a8c3ad-clone-cleanenv.txt, removing durations only: identical17 rows with duplicates, no base-only/head-only row. Both include factory-config assertion21/FLEET_PATH, five FEAT2225 real-core claim refusals and BUG1290 5a/b/c (including mutation output). Equality establishes baseline equivalence for those observations, not environmental causation, green CI, or67/67. N/c1-evidence/README.md:27 is explicitly an inference, not acceptance evidence. The delegated green obligation is retained.
- **Tracked runs:** both c0 production manifests and all16 required run files are present in git ls-tree at the pin. c0 unit manifest is67 completed/exit1 at53a89eb7, integration95/exit0. Their two changed unit and two changed integration subjects prevent relabelling those complete runs as c1. Fresh c1 manifest-unit.json at F/runs/r-20261122-5-validate-validator/qa records this exact pin and individual file exit0; it is post-pin QA evidence, not a committed c1 receipt.
- **INV26 timing:** pinned N/c1-evidence/check-state-b9a8c3ad.txt records34 tracked features/exit0. Pinned README ends with a promise of the pin execution; its current lines32–37 are a later append recording pin9c380403/34/exit0. This is explicitly fresh execution evidence under settled Q3, never git-show evidence at the pin. Original T05 positive31-record success and c0 positive34-record failure remain historical facts. No PM rerun or fabricated committed evidence.
- **Settled scope honored:** workflow exemption/three bin comments and removal of the stale once-only floor with detector controls follow Q1; async Main wording follows Q2; fresh corpus timing follows Q3. Known team-config owner-manifest DEVIATION (GC03/#2387) is not newly escalated or silently called a passing execution.

## Remaining action / open questions

**SC-04 evidence packaging — form / med (T-02/Main):** commit the exact executed CHECK text/invocation beside the already committed actual-base/per-target outputs, preserving their execution refs and exits. The existing pinned plan contains the candidate command; a path to that candidate is not the receipt's record of which bytes actually executed. This is the surviving c0 evidence gap, not a source defect or new product/scope question. The lead routes a same-run packaging correction; no source re-gate or suite rerun is requested.

Open questions: none. No source, plan, BRIEF, approval or lead-run record authored by PM.
