"""THE INVARIANT TABLE: the one place a row is declared and the one place discretion lives. (FEAT-69)"""
from check_state.board import inv_13, inv_21, inv_24, inv_26, inv_28, inv_30, inv_37
from check_state.brief import inv_38, inv_41, inv_49
from check_state.corpus import inv_52
from check_state.feature_record import (
    collate_feat59,
    inv_1,
    inv_12,
    inv_18,
    inv_2,
    inv_22,
    inv_23,
    inv_33,
    inv_39,
    inv_40,
    inv_43,
    inv_47,
    inv_6,
    inv_7,
    inv_8,
)
from check_state.host import inv_19, inv_42, inv_45, inv_48
from check_state.plan import inv_3, inv_32, inv_34, inv_35, inv_4, inv_44, inv_5, inv_51
from check_state.run_state import inv_15, inv_16, inv_36, inv_46
from check_state.seams import inv_17
from check_state.worktrees import inv_25, inv_27, inv_29, inv_31
# INV-10 IS GONE, AND THE NUMBER IS RETIRED WITH IT. It ran check-docs.sh, the
# propagation checker, which no longer exists: the operator struck the whole
# stale-marker mechanism and replaced detection with deletion — a decision the tree
# flatly contradicts is struck from the record and removed from every gate, so
# nothing survives to contradict. Do NOT reuse "INV-10" for a new invariant; the
# number appears in shipped digests and reviews, and reusing it makes that history
# read as being about something it never was.
#
# What this costs, stated plainly so nobody rediscovers it as a surprise: nothing
# mechanical now checks that a doc statement a later decision falsified was actually
# removed. The replacement rule holds only while the striking really happens every
# time, and its enforcement is a human reading a diff.

# =====================================================================================
# THE INVARIANT TABLE (FEAT-62). One row per active INV number; a row is a record, never a
# bare pair, so the verbs below and the consolidation audit read the same metadata:
#
#   name       the token every finding row prints; retired numbers are NEVER reused (DEC-205)
#   run        `run(ctx)` for a repo-scoped row, `run(ctx, feat)` for a feature-scoped one
#   scope      "feature": the runner calls it once per feature in `ctx.features` (sorted, and
#              narrowed by --feature); "repo": once, and a repo row that loops features itself
#              loops `ctx.features`, so --feature narrows it too
#   reads      what the function opens -- `path:<repo-relative POSIX glob>`, `git:<operation>`,
#              `gh:<resource>` -- the join --changed runs, and the reads-lock's subject
#   contract   one line: what a VIOLATION or note from this row means
#   authority  the decision this row stands on; the audit refuses a citation that does not
#              resolve in DECISIONS-INDEX.md or that is STRUCK (DEC-188 made mechanical)
#
# GROUPS ARE THE BASELINE'S BLOCKS. The old file interleaved a family's invariants per feature
# (INV-6, then INV-33, then INV-7 ... for feature A, then the same for feature B); the runner
# keeps exactly that order by iterating `for group: for feature: for row`. A group's optional
# `collate` is the one joint emission the corpus has: the FEAT-59 family's single legacy note.
# =====================================================================================
from collections import namedtuple

Inv = namedtuple("Inv", "name run scope reads contract authority")
Group = namedtuple("Group", "name rows collate", defaults=(None,))

_FEATURE_JSON = "path:.harness/*/features/*/feature.json"
_PLAN_YAML = "path:.harness/*/features/*/plan.yaml"
_PLAN_MD = "path:.harness/*/features/*/PLAN.md"
_BRIEF = "path:.harness/*/features/*/BRIEF.md"
_STATE_MD = "path:.harness/*/features/*/STATE.md"
_HARNESS_JSON = "path:.harness/harness.json"
_RUN_STATE = "path:.harness/*/features/*/runs/*/state.yaml"
_HANDOFF = "path:.harness/*/features/*/notes/handoff-*.md"

INVARIANTS = (
    Group("plan-scalar", (
        Inv("INV-35", inv_35, "feature", (_PLAN_YAML,),
            "an unquoted ` #<digit>` in a plan.yaml plain scalar truncates the value silently", "DEC-182"),
    )),
    Group("goal-of-record", (
        Inv("INV-1", inv_1, "feature", (_BRIEF, _PLAN_YAML),
            "a feature's BRIEF.md is signed before its flows run", "DEC-129"),
    )),
    Group("state-has-goal", (
        Inv("INV-2", inv_2, "feature", (_STATE_MD, _BRIEF),
            "a feature with a STATE.md has a BRIEF.md", "DEC-129"),
    )),
    Group("plan-record", (
        Inv("INV-3", inv_3, "feature", (_PLAN_YAML, _PLAN_MD),
            "the plan carries an approval block; a pending signature is noted", "DEC-182"),
        Inv("INV-4", inv_4, "feature", (_PLAN_MD,),
            "every PLAN.md task carries change_type so the qa gate can apply", "DEC-129"),
        Inv("INV-5", inv_5, "feature", (_PLAN_YAML, _PLAN_MD, _STATE_MD),
            "STATE.md names no task its plan does not contain", "DEC-129"),
    )),
# INV-32 BEGIN (FEAT-45 T-07)
    Group("panel-record", (
        Inv("INV-32", inv_32, "feature", (_PLAN_YAML, _FEATURE_JSON, _HARNESS_JSON),
            "an approved plan carries the adversarial panel record the operator reviewed", "DEC-182"),
    )),
# INV-32 END (FEAT-45 T-07)
    Group("feature-record", (
        Inv("INV-6", inv_6, "feature", (_FEATURE_JSON,),
            "a validator run that reviewed code has a pinned review_sha", "DEC-50"),
        Inv("INV-33", inv_33, "feature", (_FEATURE_JSON, _PLAN_YAML, _PLAN_MD, "git:show", "git:log"),
            "a pinned review_sha still matches the plan bytes at a non-terminal station", "DEC-121"),
        Inv("INV-7", inv_7, "feature", (_FEATURE_JSON,),
            "cycles_used counts at least the FAIL runs recorded", "DEC-157"),
        Inv("INV-22", inv_22, "feature", (_FEATURE_JSON, _HARNESS_JSON),
            "recorded runs are counted against budgets.max_total_runs (a note)", "DEC-178"),
        Inv("INV-8", inv_8, "feature", (_FEATURE_JSON, "path:.harness/*/features/*/runs/*"),
            "a recorded run's directory exists on disk (a note)", "DEC-131"),
        Inv("INV-12", inv_12, "feature", (_FEATURE_JSON, "path:.harness/*/features/*/runs/*"),
            "a run directory on disk is recorded in feature.json (a note)", "DEC-131"),
    )),
    Group("omp-port", (
        Inv("INV-45", inv_45, "repo", ("path:.omp/config.yml", "path:.agents/skills/harness/bin/check-omp-port.py"),
            "an OMP-configured tree grades its roster, hook wiring and overlays through check-omp-port.py", "DEC-233"),
    )),
    Group("seams", (
        Inv("INV-17", inv_17, "feature", (_FEATURE_JSON, _PLAN_YAML, _HANDOFF, _HARNESS_JSON),
            "every seam a feature's station has crossed left a well-formed handoff note", "DEC-159"),
    )),
    Group("runs-without-record", (
        Inv("INV-18", inv_18, "feature", ("path:.harness/*/features/*/runs", _FEATURE_JSON),
            "a feature with run directories has a feature.json", "DEC-160"),
    )),
    Group("station-record", (
        Inv("INV-34", inv_34, "feature", (_FEATURE_JSON, _PLAN_YAML),
            "every feature directory carries a plan.yaml, the only place a station is recorded", "DEC-182"),
    )),
    Group("budgets", (
        Inv("INV-23", inv_23, "repo", (_FEATURE_JSON, _STATE_MD, "path:CLAUDE.md"),
            "feature.json, STATE.md and CLAUDE.md stay within their line budgets (notes)", "DEC-150"),
    )),
    Group("run-state", (
        Inv("INV-16", inv_16, "feature", (_RUN_STATE, "path:.claude/skills/harness/bin/run-state-schema.json"),
            "state.yaml is a checkpoint: whitelisted keys, declared step shape", "DEC-154"),
        Inv("INV-36", inv_36, "feature", (_RUN_STATE, "path:.harness/*/features/*/runs/*/.run-identity"),
            "a run directory's checkpoint carries the identity recorded when it was first written", "DEC-154"),
        Inv("INV-15", inv_15, "feature", (_RUN_STATE, "path:.harness/*/features/*/runs/*/digest.md", _FEATURE_JSON,
                                          "path:.claude/skills/harness/bin/digest_record.py"),
            "a complete lead-hosted run's digest.md exists and its final fenced mapping carries VERDICT, DIGEST and artifact", "DEC-156"),
        Inv("INV-46", inv_46, "feature", (_RUN_STATE, "path:.harness/*/features/*/runs/*/digest.md", _FEATURE_JSON,
                                          "path:.claude/skills/harness/bin/digest_record.py"),
            "a contract-clean lead digest's VERDICT agrees with every verdict feature.json records for that run", "DEC-156"),
    )),
    Group("glossary", (
        Inv("INV-19", inv_19, "repo", ("path:.harness/glossary.md",),
            "the domain's ubiquitous language is recorded (a note)", "DEC-162"),
    )),
    Group("mirror-container", (
        Inv("INV-21", inv_21, "feature", (_FEATURE_JSON, _HARNESS_JSON),
            "a mirrored feature with task issues records its parent container (a note)", "DEC-138"),
    )),
    Group("factory-claims", (
        Inv("INV-24", inv_24, "repo", (_FEATURE_JSON, "path:.harness/factory/fleet.yaml"),
            "a factory block names a fleet repository and no two features claim one issue", "DEC-203"),
    )),
    Group("branch-claims", (
        Inv("INV-52", inv_52, "repo", (_FEATURE_JSON, "git:ls-tree"),
            "no two landed features claim one branch, read from the main corpus on demand", "DEC-95"),
    )),
    Group("shipped-pr", (
        Inv("INV-28", inv_28, "feature", (_FEATURE_JSON, _PLAN_YAML, _HARNESS_JSON),
            "a Done feature records the pull request that shipped it (a note)", "DEC-138"),
    )),
    Group("worktree-place", (
        Inv("INV-25", inv_25, "repo", ("git:worktree-list",),
            "no git worktree stands outside the worktrees segment", "DEC-174"),
    )),
    Group("worktree-life", (
        Inv("INV-29", inv_29, "repo", ("git:worktree-list", _FEATURE_JSON, "path:.harness/factory/fleet.yaml"),
            "no worktree survives its feature reaching a terminal state", "DEC-203"),
    )),
    Group("build-entry", (
        Inv("INV-37", inv_37, "repo", (_FEATURE_JSON, _PLAN_YAML, _HARNESS_JSON),
            "an enabled mirror left a Build-entry receipt on every planned feature", "DEC-203"),
    )),
    Group("board", (
        Inv("INV-26", inv_26, "repo", (_FEATURE_JSON, _PLAN_YAML, _HARNESS_JSON, "gh:auth", "gh:board"),
            "the board agrees with the plan on disk for every mirrored card", "DEC-203"),
        Inv("INV-30", inv_30, "repo", (_FEATURE_JSON, _PLAN_YAML, _HARNESS_JSON, "gh:auth", "gh:milestones"),
            "a Done feature's milestone is closed, proving ship ran", "DEC-203"),
    )),
    Group("mirror-config", (
        Inv("INV-13", inv_13, "repo", (_HARNESS_JSON,),
            "the GitHub mirror is configured or explicitly off, never limbo", "DEC-138"),
    )),
    Group("layout", (
        Inv("INV-27", inv_27, "repo", ("path:.claude/skills/harness/bin/layout_migration.py",),
            "every layout surface speaks one language (layout_migration.scan)", "DEC-174"),
    )),
    Group("preload-weight", (
        Inv("INV-42", inv_42, "repo", ("path:.omp/agents/*.md", "path:.claude/skills/*/SKILL.md", _HARNESS_JSON,
                                       "path:.claude/skills/harness/bin/check-skill-weight.py"),
            "every declared preload resolves; excess preload weight is a note", "DEC-158"),
        Inv("INV-48", inv_48, "repo", ("path:.omp/agents/*.md", "path:.claude/skills/**/*.md",
                                       "path:.harness/harness/docs/DECISIONS-INDEX.md",
                                       "path:.claude/skills/harness/bin/check-skill-refs.py"),
            "every reference a skill makes resolves (check-skill-refs.scan)", "DEC-235"),
    )),
    Group("merge-hook", (
        Inv("INV-31", inv_31, "repo", ("git:config", "path:.claude/skills/harness/hooks/post-merge"),
            "this clone's core.hooksPath runs the harness post-merge hook", "DEC-203"),
    )),
    Group("brief-perspectives", (
        Inv("INV-38", inv_38, "feature", (_BRIEF, _PLAN_YAML),
            "every declared perspective is discharged by a tagged SC, and every SC tag is declared", "DEC-231"),
        Inv("INV-41", inv_41, "feature", (_BRIEF, _PLAN_YAML),
            "an SC that invokes a gate script scopes it to the feature", "DEC-231"),
        Inv("INV-49", inv_49, "feature", (_BRIEF, _HARNESS_JSON),
            "an SC resting on a kind with no runner, or verify: manual, is named under "
            "'## Verification gaps'", "DEC-163"),
    )),
    Group("ledger", (
        Inv("INV-39", inv_39, "feature", (_FEATURE_JSON, _BRIEF, _HARNESS_JSON),
            "cycles_used stays within the bound, and a raised bound is a recorded decision", "DEC-157"),
        Inv("INV-40", inv_40, "feature", (_FEATURE_JSON, _BRIEF, _PLAN_YAML, _HANDOFF),
            "every autonomous judgement -- mission, regate, succession, amendment -- leaves a ledger entry", "DEC-229"),
        Inv("INV-43", inv_43, "feature", (_FEATURE_JSON, _BRIEF, _HANDOFF, _HARNESS_JSON),
            "a succession judgement is recorded no later than the successor's first run", "DEC-227"),
        Inv("INV-47", inv_47, "feature", (_FEATURE_JSON, "path:.harness/*/features/*/notes/review-harness-*.md",
                                          "path:.claude/skills/harness/bin/digest_record.py"),
            "a validate run recorded PASS has no same-cycle member review at FAIL or BLOCKED", "DEC-156"),
    ), collate=collate_feat59),
    Group("abandoned-evidence", (
        Inv("INV-51", inv_51, "feature", (_PLAN_YAML, "path:.harness/*/features/*/runs/*/"),
            "an abandoned feature carries no runs/ evidence", "DEC-238"),
    )),
    Group("rejected-shape", (
        Inv("INV-44", inv_44, "feature", (_FEATURE_JSON, _PLAN_YAML, _BRIEF),
            "a REJECTED record has exactly one shape: one run, zero cycles, a reject judgement, nothing signed", "DEC-230"),
    )),
)

# Retired numbers stay in the catalogue so `--list` and old digests resolve; a retired number
# is never run and never reused (DEC-205).
RETIRED = {
    "INV-9": "DEC-233 — host enforcement moved to OMP; INV-45 grades the port surface",
    "INV-10": "check-docs.sh struck — a decision the tree contradicts is removed, not marked stale",
}
