# UAT — FEAT-53 metrics dashboard

status: ready
branch: feat/FEAT-53
review_sha: daba2af5513a0316f57ed8729576acb0e582708b

The automated and inspection gates are green. This user-run script is the remaining ship gate.

## Setup

From the Harness checkout, run:

```sh
python3 .agents/skills/harness/bin/dashboard/serve.py
```

Open http://127.0.0.1:8971/ in a desktop browser.

## Steps

- U-01 (SC-02): Follow only the setup above from a clean checkout and open `/`.
  expect: the working dashboard loads without requiring any undocumented setup.
  result:

- U-02 (SC-08): Open a feature that shipped before metrics trend collection existed.
  expect: the trend area states that data is unavailable and shows no zero or flat chart.
  result:

- U-03 (SC-11): Choose a window and Repository, open a KPI tile, then open one feature or bug row from that KPI panel.
  expect: the URL reaches `/work/$id` and preserves both selected query parameters through each navigation.
  result:

- U-04 (SC-24): On `/`, use each Status card as a filter and inspect feature, bug, grilling, and linked-worktree rows.
  expect: the ranked cards filter the list and the displayed source locations open without any GitHub access.
  result:

- U-05 (SC-26): View `/` at 1440px and 1920px widths.
  expect: the centred page shows the shared header, the seven KPIs in 4+3 geometry, then the work list opened by the Status cards, with fourteen-point sparklines spanning each tile.
  result:

- U-06 (SC-27): Switch the work list between Kanban and Table, then filter by Station, Status, and Kind.
  expect: both layouts show the same matching rows and each row exposes the signed operational fields without a Repository list filter.
  result:

- U-07 (SC-28): Open a feature or bug detail route, then try the corresponding action on a grilling or worktree row.
  expect: feature/bug detail starts with its operational header and KPI content, while grilling/worktree content expands inline and has no detail route.
  result:
