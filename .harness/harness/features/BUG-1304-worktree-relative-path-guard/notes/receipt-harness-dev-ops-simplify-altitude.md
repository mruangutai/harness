# SIMPLIFY / ALTITUDE — BUG-1304

## BLUF
Nothing in this diff sits at the wrong altitude — the vendored fixtures, the single-home claim-set
rule, and DEC-218's placement all check out; no recommendation clears the bar. **leave** on all counts.

## Fixture judgement (primary target)

The two large fixtures (`fixtures/prior-check-domain.sh.fixture` ~2115 lines,
`fixtures/prior-bash-write-guard.sh.fixture` ~859 lines) are consumed by simple
`shutil.copyfile(fixture_path, hook); os.chmod(hook, 0o755)` in
`test-check-domain.py:4408-4412` and `test-bash-write-guard.py:967-970` — a byte-identical
pre-change binary dropped into an isolated bin tree and executed directly, exactly as BRIEF SC-06
requires: every new refusal case shown non-refused (exit 0) against the pre-change guard, with the
ran-proof (no `enforcement OFF` / `was not enforced` / `passing through` on stderr) and a positive
control still refusing at the same frozen guard (BRIEF.md:148-160).

The env-override alternative (`CHECK_DOMAIN_BIN`/`BASH_WRITE_GUARD_BIN`) is a recorded dead end
(resolves once at module import, cannot select two binaries within one test run) and I did not
re-propose it.

I considered the git-materialization alternative you asked me to weigh (`git show
b64b2d53:<path>` into a tmp dir at test time instead of a vendored copy) and it is **already
settled, not open**: `plan.yaml:969-973,1187-1190` states the reason directly — CI checks out at
depth 1, so `git show` against a historical sha is unreachable there, which would make SC-06's proof
unrunnable in CI. The plan cites a direct in-repo precedent for the same choice,
`test-validate-digest.py:30-33`'s `check_prior_validator`, and four *other* `prior-*.fixture` files
already existed in this tree before this diff (`prior-check-plan-routes.py.fixture`,
`prior-harness_yaml.py.fixture`, `prior-validate-digest.py.fixture`,
`prior-harness_boundary.py.fixture.b64`) — these two are the same established convention applied to
two more guards, not a new pattern invented for this feature. The plan-panel review
(`notes/review-harness-code-reviewer-planpanel-c1.md:96-109`) independently reached and signed off
on the identical conclusion pre-build. Frozen bytes cannot rot into false-green for SC-06's claim (a
historical fact about the pre-change guard, immutable regardless of later edits); the only forward
risk is the generic one every existing mutant/fixture in this suite already carries (a future
`isolated_bin`/bin-layout change), not specific to size. Materializing from git would trade a small,
already-audited (`test-check-fixture-secrets.py` covers the fixtures tree) storage cost for a real
hermeticity regression in shallow clones. **This is adequacy, not excess — leave.**

## Secondary altitude checks

- **Single authoritative rule statement**: both `check-domain.sh:777-813` and
  `bash-write-guard.sh:736-761` call `harness_boundary.claim_worktrees` /
  `harness_boundary.claim_set_refusal` verbatim — neither guard restates the membership rule or the
  refusal wording locally. One home, no drift surface. **leave.**
- **DEC-218 placement**: it is the sole prose statement of the boundary rule in the diff; the two
  bash guards carry only call-sites, not a restated rule. No opinion on its content (out of scope).
  **leave.**

## Not re-litigated
FEAT-51/DEC-153 narrowing, DEC-218 content, `_expire`/`CLAIM_TTL_SECONDS` dead end, env-override
dead end, REQ-06 refusal wording — none touched.
