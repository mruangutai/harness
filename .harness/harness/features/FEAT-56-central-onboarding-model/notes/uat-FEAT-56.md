# UAT — FEAT-56 Central onboarding model
status: ready              # draft | ready | passed | failed
branch: feat/FEAT-56-central-onboarding-model
review_sha: 62debeaf9e77ecaf0423284220310abae0d3e706
covers: SC-09 (the only `verify: uat` criterion)

Everything else is green at this pin, re-run today, not inherited: unit suite exit 0 (34 files),
integration suite exit 0 (49 files), `check-omp-port.py` ok, `check-instruction-paths.py` 0
violations of 62 files, `test-fleet-product-config.py` 18/18, the team-config template parses as
YAML, and SC-01's ordered-marker block exits 0 at DB=3 < FL=10 < SG=11. Nine of ten SCs are met.
**This is the last gate.**

## What you are judging

Not whether the document is well written. **Whether it is the procedure you would actually run**,
and whether following it top to bottom would onboard a repository without misleading you.

## Setup — 1 minute

Open one file and keep it open:

```
git show 62debeaf:.claude/skills/harness-init/SKILL.md
```

It is 419 lines. You will read four regions of it, ~120 lines total. Line anchors below are that
blob's line numbers.

**Read it as if you are onboarding one concrete repository right now:**

> `mruangutai/kaya-web`, default branch `main`, a React front end for kaya-ai. Not in
> `.harness/factory/fleet.yaml` yet. You have push access to it, and later in the script you will
> be asked to imagine that you do not.

## Steps — five, about 9 minutes

- **U-01 (SC-09) · the ORDER — 2 min.** Read **lines 8–17** (the opening three-things paragraph and
  the one-file rule) and then **lines 153–186** (`### 2. Land harness.json, then register the
  repository`, all five numbered items).
  expect: the document tells you to land `kaya-web`'s `harness.json` on `main` **before** adding it
          to `fleet.yaml`, and line 155 gives you the reason reversing it fails **silently** — no
          symptom except an unattributed `FleetError` mid-build.
  answer yes/no: **would you have got the order right, and do you know why reversing it is
  dangerous rather than merely wrong?**
  result:

- **U-02 (SC-09) · the ONE-FILE RULE — 2 min.** Skim the whole blob for anything it tells you to
  write **into `kaya-web`**. Anchors that answer it directly: **lines 14–17** and **lines 187–190**.
  expect: exactly one file — `kaya-web`'s own `.harness/harness.json` — and an explicit list of what
          is NOT written there (`team-config.yaml`, expertise, `.harness/products/`, `bin/`, hooks,
          settings).
  answer yes/no: **does any step in the document ask you to write a file into `kaya-web` that the
  factory will not read?** (a "no" here is the PASS answer)
  result:

- **U-03 (SC-09) · the GAP, including no push access — 2 min.** Re-read **lines 160–168** (item 2)
  with this twist: `kaya-web`'s `main` is branch-protected and you **cannot** push to it.
  expect: the document tells you to open a PR against the default branch instead, states that
          onboarding stays **incomplete until that PR merges**, and warns that landing the file
          delegates control of what the factory reads to whoever can push `main`.
  answer yes/no: **do you know what to do — and what not to do — during the window where the config
  has not landed?**
  result:

- **U-04 (SC-09) · `--check-product-configs` — 2 min.** Read **lines 172–180** (item 4).
  expect: you would run
          `python3 .claude/skills/harness/bin/factory_config.py --check-product-configs --repo mruangutai/kaya-web`
          at that exact point — after the config lands and the fleet entry exists, **before** you
          create the central tree — and on exit 2 you would read the named
          `kaya-web@main:.harness/harness.json` and stop rather than proceed.
  answer yes/no: **would you have run it, at that moment, and known that exit 2 means stop?**
  result:

- **U-05 (SC-09) · the NARROWED STEP 1 — 1 min.** Read **lines 47–52** (`### 1. Install the eight
  prerequisites in this control-plane clone — HARD GATE`).
  expect: unmistakable that the eight prerequisites and the `core.hooksPath` step apply to **this
          control-plane clone**, never to `kaya-web`.
  answer yes/no: **would you ever have run step 1 inside `kaya-web`?** (a "no" here is the PASS
  answer)
  result:

## Your verdict — one line, you fill it in

```
UAT: PASS | FAIL     (on FAIL, name the step that would have misled you and what you would have done wrong)
```

**Only you set this.** On FAIL this consumes a fix cycle; the step you name is the work.
