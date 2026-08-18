# Segment 01 — main-session-direct: T-09 then T-08

Both tasks are `execution_mode: main-session-direct` and `depends_on: []`. **T-09 first** — it is the
only human-latency route in the plan (cross-repository pull request + operator merge) and T-07 cannot
start until it is merged. T-08 is independent and can be done while the T-09 pull request sits open.

Branch for this feature: `feat/FEAT-24-config-responsibility-split` (created, local only).
GitHub mirror: milestone #15, parent #501, T-09 → issue #510, T-08 → issue #509, both already moved
to `Building` and already `status: building` in `plan.yaml`.

---

## T-09 — kaya-ai's config moves onto the by-name board shape (issue #510)

Target file: `/Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.harness/harness.json`
(materialised by step 2 — it does not exist until then).

### Commands, in order

```
gh issue create --repo mruangutai/kaya-ai \
  --title "Move .harness/harness.json onto the by-name board shape" \
  --body-file <path to a body file you write>
# note the issue number it prints; call it <n>

python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/factory_workspace.py \
  --repo mruangutai/kaya-ai --issue <n>
# materialises /Users/molchairuangutai/GitHub/harness-factories/kaya-ai and cuts factory/issue-<n>

# ---- hand-edit the file (diff below) ----

# CORRECTION, recorded 2026-08-19 after the operator ran this: factory_land.py does NOT commit.
# It failed with `No commits between master and factory/issue-334` until the operator committed
# by hand in the checkout. Add `git -C <workspace>/kaya-ai commit` before factory_land. Backlog B-12.

python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/factory_land.py \
  --repo mruangutai/kaya-ai --issue <n>
# pushes and opens the pull request

# ---- merge the pull request ----
```

### The diff I expect — the whole change is the `github` block

Verified against `master` today: `github` is the last key of the file and occupies lines 245–253.
Nothing else in the file changes (`test_matrix`, `test_kinds`, `gates`, `budgets`, `cost_model`,
`dirty_tree_whitelist` are kaya's own — D-02/#336 D-03).

Current (lines 245–253):

```json
  "github": {
    "_note": "GitHub Issues mirror (DEC-138). sync is asked ONCE at /harness-init; ...",
    "sync": true,
    "repo": "mruangutai/kaya-ai",
    "project_number": 2,
    "project_id": "PVT_kwHOAAases4Bc7h3",
    "status_field": "PVTSSF_lAHOAAases4Bc7h3zhXgwuA",
    "in_progress_option": "47fc9ee4"
  }
```

Replacement — keep the existing `"_note"` line byte-for-byte, delete the four pinned-id keys, add
the two rationale notes and the board:

```json
  "github": {
    "_note": "<< the existing _note line, unchanged >>",
    "sync": true,
    "repo": "mruangutai/kaya-ai",
    "_board_done_note": "Board 2's `Done` option is RETAINED on purpose — 118 items sit there and the enabled `Item closed` workflow keeps landing cards in it.",
    "_board_ready_note": "`ready: Ready` is deliberate even though Ready is EMPTY. On this board `Backlog` means filed-and-untriaged and `Ready` means promoted for the factory, so a claim run that finds nothing has found the truth rather than hit a misconfiguration. Pointing intake at `Backlog` instead would hand the factory 82 untriaged items.",
    "board": {
      "owner": "mruangutai",
      "number": 2,
      "station_field": "Status",
      "stations": {
        "backlog": "Backlog",
        "ready": "Ready",
        "building": "Building",
        "review": "Review",
        "done": "Done"
      }
    }
  }
```

Four things the verify will fail on if they drift:

- `project_number`, `project_id`, `status_field`, `in_progress_option` must all be **gone**.
- The five station values are compared **literally**. I re-probed board 2 today —
  `gh project field-list 2 --owner mruangutai` returns Status options
  `Backlog, Plan, Ready, Building, Review, Done`, so all five names exist.
- `plan` must **not** be declared, even though the option exists — no code resolves it (D-06).
- `default_branch` must **not** appear anywhere in this file — it stays in `fleet.yaml` because
  `factory_workspace.py` reads it to create the checkout that holds this file (D-02).

### Verify (run after the merge — it reads `?ref=master`)

`plan.yaml` T-09 `verify:`, verbatim, run from the harness repo root. Its oracle is literal and
imports no production code.

---

## T-08 — the config template shows a declared board (issue #509)

Target file: `/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/templates/harness.json`
— `check-domain.sh --resolve` returns `NOBODY` for it, re-confirmed today.

### The diff I expect — one line, `_board_note` at line 154

`"board": null` on line 155 **stays null**. Only `_board_note` is rewritten. Suggested text (it
satisfies every clause of the T-08 verify — the six terms, the null sentence, and the word `loud`):

```json
    "_board_note": "Project board for the station mirror (FEAT-18): owner, number, station_field, and a stations mapping with exactly the five keys backlog, ready, building, review and done, each naming an option that exists on that board — every value resolved by name at runtime, never by a pinned id. null = this project has no board and no station is ever written. A board that is present but incomplete is a loud error naming the offending key, never a silently disabled feature.",
```

Do **not** add a board block, a commented-out example or placeholder ids — that is the pinned-id
defect FEAT-18 removed. Change nothing else in the file.

### Verify

`plan.yaml` T-08 `verify:`, verbatim, from the harness repo root. It asserts `board` is still
`null` and that `_board_note` names all six terms plus the null sentence plus `loud`/`error`.

---

## What I need back

1. T-09's issue number, and confirmation the pull request is **merged**.
2. The T-09 verify's output (`T-09 GREEN` or its failure lines).
3. The T-08 verify's output.
4. Whether you left the template's `_board_note` wording as suggested or changed it.

Then re-delegate me and I run the eng segment: T-01 → T-02 → {T-03, T-06} → T-04, stopping again
at T-05 (which must land in the same commit as T-04) and at T-07.
