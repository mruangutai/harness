# STATE

## Current

- feature: FEAT-12-end-copy-distribution
- run: .harness/features/FEAT-12-end-copy-distribution/runs/t12-product/state.yaml
- squad: product
- status: awaiting-user

Three of the five team-lane tasks are done and committed: T-07 deleted `deploy.sh` (`e987c6d`),
T-10 neutralised every deploy reference in the six bin modules (`9e49ba7`), and T-12 rewrote the
distribution story across README.md, SPEC.md, BUILD.md and `.harness/README.md` (`ff75afb`). Full
unit suite green at each: exit 0, 85 PASS, 0 FAIL, re-run by me rather than relayed.

**The build stops here and goes up, because nine of the fourteen tasks are lane-locked to layer 0
and I am layer 1.** T-06, T-08 and T-11 return exit 2 from `check-domain.sh` for
`harness-orchestrator` — I probed each path. T-01 to T-05 and T-09 sit outside the project
directory where both guards pass me through, so those are locked by the signed plan under DEC-179,
not by a hook. The nine work orders, with every `verify:` verbatim, are in
`notes/segments-layer0-2026-08-10.md`.

T-14 and T-13 could not run and are not late. Measured at `ff75afb`: T-14's first verify clause
returns six hits, four of them inside T-08's and T-11's files. The plan's `depends_on` for T-14
names T-11 but omits T-08, and T-08 does block it.

One send-back this session, so the cycle count is five of ten. Product-lead sent documentor back
for writing into README.md a claim its own research had just disproved — that `factory_config.py`
is the fleet declaration's only reader. It is not: `check-state.sh` reads that file directly.

## Open Questions

- Q1 (BLOCKING, for the operator, before segment A is staged): the ship dispatch says to STOP if
  any of kaya's uncommitted entries sit under `.claude/skills/harness*` or `.claude/commands/harness*`.
  BRIEF.md's settled rulings record that 34 tracked files under exactly those paths carry local
  modifications he signed off on discarding. Read literally the stop fires on the signed-for work
  and T-02 can never run; read as intended it means entries beyond those 34. The cost of guessing
  is a permanent discard on another repository's `master`, so it is his call, not an agent's.
- Q2 (non-blocking, a HARNESS DEFECT, filed nowhere yet): `bash-write-guard.sh` passes
  `rm -f <out-of-domain-path>` at exit 0 while blocking `rm <same-path>` and `rm -rf <same-dir>` at
  exit 2. `trailing_files` treats `-f` as sed's script-file flag and skips the next token, so the
  target list comes back empty and no deny fires. Measured for `harness-orchestrator`, `harness-pm`
  and `harness-documentor`. The most common deletion idiom is the one that gets through, and the
  file is a DEC-174 carve-out so only the main session can fix it.
- Q3 (non-blocking, for T-13's author): `git grep -E` does not honour `\b`.
  `git grep -cE '\bdeploy' -- docs/harness/BUILD.md` matches nothing where `git grep -c 'deploy'`
  returns 5 and `-P` returns 5. T-13's case 4 asks for a word boundary on `DEC-12`; in Python `re`
  that is fine, through `git grep -E` it would pass vacuously.
- Q4 (non-blocking, unowned): `docs/harness/SPEC.md:419-421` illustrates the fleet-config claim with
  three scripts and omits `factory_claim.py`. Incomplete, not false. No scheduled task owns it.
- Q5 (non-blocking, for the record): `gh-sync.py open` CREATED parent issue #223 rather than
  adopting #203, which `feature.yaml`'s `effort:` names. `parent_origin: created`, so a ship close
  would close #223 and leave #203 open.
