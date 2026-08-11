# UAT — SC-01 — GraphQL cost of a station move

**Status: `MET` — run 2026-08-10 by the main session at the operator's explicit instruction, after the operator amended SC-01 to strike its total clause. Result at the bottom of this file.**

**Original status: `ready`. The operator runs this; no agent may.** The measurement writes to a Projects v2
board, and that write is outside every agent's authorization in this flow. Nobody may mark this
passed but you.

**What is being proven** (`BRIEF.md:39-41`): a single station move costs **2** GraphQL points against
**104** today, and a four-task `factory_decompose` costs single-digit points in total.

---

## Read this first — three things that will ruin the run if skipped

**1. The fixture. Board 6 and `mruangutai/harness-factory-smoke-a1` are RETAINED FIXTURES.** Do not
delete either. They are not scratch and they are not cleanup owed (`plan.yaml` `approval.rulings` (2)
and (3); `feature.yaml sc01_ruling`). What is being preserved is *a working station field with four
items in known states*. `factory_decompose` **moves items between stations**, so the field survives
the proof but the item states do not unless you put them back. A proof that leaves them moved has
spent the fixture to measure a number.

**2. `factory_decompose` takes the board from the FLEET FILE, not from a flag.** `_main` calls
`factory_config.load_fleet()` with no argument unless `--fleet` is given, and `FLEET_PATH` is
`.harness/factory/fleet.yaml` (`factory_config.py:50`). **That file today declares
`board.number: 3`, `station_field: Status`, `repos: mruangutai/harness`** — not board 6. Run step 4
without an explicit `--fleet` and the run writes stations onto board 3, which you never snapshotted,
while this procedure carefully protects a board nothing touched. **Step 0 exists to stop that.**

**3. Ordering.** `gh project item-list` costs **31** points (`BRIEF.md:153`) and each restore
`item-edit` costs 1. If the snapshot or the restore falls inside the differenced window, the number
you measure is contaminated and your one run is wasted. **Steps 1, 6 and 7 sit OUTSIDE the
differenced window by construction. Do not "optimize" them back inside it** — they are 67 points of
budget spent deliberately so the window contains only what is under test. And **never** use
`gh project field-list` to get option ids: that is the 102-point call this feature exists to remove.
Step 1b gets the same ids for **1** point.

---

## Step 0 — pin the fleet (local file reads, 0 points)

Point `FLEET` at a fleet file whose `board.number` is **6** and whose `repos:` names the fixture repo.
If none exists, copy `.harness/factory/fleet.yaml`, change `board.number` to 6, set `repos:` to
`mruangutai/harness-factory-smoke-a1`, and save it outside the repo (e.g. `~/feat11-fleet.yaml`).

```bash
FLEET=~/feat11-fleet.yaml
python3 - "$FLEET" <<'PY'
import sys, yaml
f = yaml.safe_load(open(sys.argv[1]))
b = f["board"]
print("owner        :", b["owner"])
print("board.number :", b["number"])
print("station_field:", b["station_field"])
print("stations     :", b["stations"])
print("repos        :", [r["name"] for r in f["repos"]])
assert b["number"] == 6, "STOP: this fleet does not point at board 6"
print("OK — this fleet targets board 6")
PY
```

Then set, **from what that printed** — do not assume the field is called `Station`:

```bash
OWNER=mruangutai
BOARD=6
FIELD=<the station_field value printed above>
```

If the assert fires, fix the fleet file before going further. Every later step reads `$FIELD`, so a
wrong value here fails loudly at step 1b rather than silently at step 4.

---

## Step 1 — BEFORE snapshot (outside the window)

### 1a. Record every item's current station value, and discover the JSON key — 31 points

```bash
gh project item-list "$BOARD" --owner "$OWNER" --format json --limit 100 \
  > ~/feat11-uat-before.json

STATION_KEY=$(python3 - "$FIELD" <<'PY'
import json, os, sys
items = json.load(open(os.path.expanduser("~/feat11-uat-before.json")))["items"]
if not items:
    sys.exit("STOP: the board returned zero items — snapshot nothing, restore nothing")
want = sys.argv[1].lower().replace(" ", "")
keys = [k for k in items[0] if k.lower().replace(" ", "") == want]
if not keys:
    sys.exit("STOP: no key matches the station field %r. Keys present: %s"
             % (sys.argv[1], sorted(items[0])))
print(keys[0])
PY
) || exit 1
echo "STATION_KEY=$STATION_KEY"

python3 - "$STATION_KEY" <<'PY'
import json, os, sys
k = sys.argv[1]
for it in json.load(open(os.path.expanduser("~/feat11-uat-before.json")))["items"]:
    print(it["id"], "|", it.get("title"), "|", it.get(k))
PY
```

Keep `~/feat11-uat-before.json` and the printed `STATION_KEY` — **the record is the file, not your
memory.** Step 7 reads both back. The script stops rather than guessing if the key is not found,
because a comparison against a key that does not exist reports "restored" for every item whatever
the board says.

### 1b. Record the station option **ids** and the project node id — 1 point

The restore in step 6 needs option **ids**; `item-list` gives you option **names**. Taking them now,
with the feature's own cheap query, is what keeps a 102-point `field-list` out of this procedure.

```bash
gh api graphql \
  -f query='query($owner: String!, $number: Int!, $field: String!) {
  repositoryOwner(login: $owner) {
    __typename
    ... on ProjectV2Owner {
      projectV2(number: $number) {
        id
        field(name: $field) {
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -F number="$BOARD" -f field="$FIELD" \
  > ~/feat11-uat-field.json
cat ~/feat11-uat-field.json
```

Record from it: `projectV2.id` (the `PVT_…` node id), `field.id`, and every option's `id` + `name`.
An empty or null `field` here means `$FIELD` is wrong — go back to step 0. Every restore in step 6
uses these three values.

---

## Step 2 — the baseline reading (the window OPENS here)

```bash
gh api rate_limit --jq .resources.graphql.used
```

Record as **B0**. `rate_limit` is REST and costs 0 GraphQL points, so every reading in this script is
free and you may take as many as you like.

---

## Step 3 — the per-move measurement (SC-01's discriminating clause)

Call **the shipped function**, not hand-issued `gh` calls — the claim is about what a station move
costs, and this is the code that performs one. Pick an item id from your step-1a record and pass
**the station it is already in**, so the move is a no-op on the fixture and needs no restore.

```bash
python3 -c '
import sys; sys.path.insert(0, ".claude/skills/harness/bin")
import factory_gh
factory_gh.project_field_set("'"$OWNER"'", '"$BOARD"', "<ITEM_ID>", "'"$FIELD"'", "<ITS_CURRENT_STATION_NAME>")'
gh api rate_limit --jq .resources.graphql.used
```

Record as **B1**. **`B1 - B0` is the per-move number and it must be 2** — one resolve plus one write.
Against the 104 recorded today, this is the clause that carries the feature.

---

## Step 4 — the four-task `factory_decompose` (SC-01 as written)

From the repo root, **with `--fleet` explicit** (see step 0 — omitting it targets board 3):

```bash
python3 .claude/skills/harness/bin/factory_decompose.py <FEATURE_DIR> \
  --fleet "$FLEET" \
  --repo mruangutai/harness-factory-smoke-a1
gh api rate_limit --jq .resources.graphql.used
```

Record as **B2**. **`B2 - B1` is SC-01's total.**

**Before running, check the dispositions — this costs nothing and it decides what the number means.**
Open `<FEATURE_DIR>/feature.yaml`'s `factory:` block (a local read, no API call). A task is `new` if
it has no recorded issue, `partial` if it has an issue but its board item or station was never set.

| disposition | what the run does per task | GraphQL cost per task |
|---|---|---|
| `new` | creates an issue (REST), `project item-add`, then one station move | item-add (**never measured**) + 2 |
| `partial` | `_find_existing_item_id` → `project_items` (`factory_decompose.py:307`), then one move | **31** + 2 |

Plus **1** for the run's single station-field validation (`factory_decompose.py:377` → `:261`).

**Prefer an all-`partial` feature dir.** It moves the four existing items and creates nothing, so the
fixture is fully restorable by step 6. An all-`new` run adds four issues and four board items that
step 6 cannot undo without deleting things.

---

## Step 5 — difference it, and interpret it honestly

| number | expect | means |
|---|---|---|
| `B1 - B0` | **2** | SC-01's per-move clause. **Met or not met on its own.** |
| `B2 - B1` | see below | SC-01's total clause |

The measured floor for the total, from components this feature did **not** change, is
`1 + 4 × (per-task cost above)`: **9 plus four unmeasured `item-add` mutations** on an all-`new` run,
or **133** on an all-`partial` run.

**If `B1 - B0` is 2 and the total is double-digit, the feature works and SC-01's total clause was
mis-specified.** Record exactly that — it is a plan-level correction that goes back to the operator,
not a build defect and not a fix cycle. Equally, do not mark SC-01 met on the per-move clause alone:
report both numbers and let the record carry the split.

---

## Step 6 — RESTORE (outside the window; the window closed at B2)

For **every** item whose station value in the step-1a listing differs from what the run left, put it
back. One `item-edit` per item, 1 point each:

```bash
gh project item-edit \
  --id <ITEM_ID> \
  --project-id <PVT_ID_FROM_STEP_1b> \
  --field-id <FIELD_ID_FROM_STEP_1b> \
  --single-select-option-id <OPTION_ID_MATCHING_THE_RECORDED_NAME>
```

The option ids come from step 1b — that is why 1b took ids and not just names.

---

## Step 7 — VERIFY the restore by re-reading — 31 points

Do not assume the writes landed.

```bash
gh project item-list "$BOARD" --owner "$OWNER" --format json --limit 100 \
  > ~/feat11-uat-after.json

python3 - "$STATION_KEY" <<'PY'
import json, os, sys
k = sys.argv[1]
before = {i["id"]: i for i in json.load(open(os.path.expanduser("~/feat11-uat-before.json")))["items"]}
after  = {i["id"]: i for i in json.load(open(os.path.expanduser("~/feat11-uat-after.json")))["items"]}
if not before:
    sys.exit("CANNOT VERIFY: the before-snapshot is empty")
missing_key = [i for i in list(before.values())[:1] if k not in i]
if missing_key:
    sys.exit("CANNOT VERIFY: station key %r is not present on the snapshot items — "
             "re-derive it as in step 1a; a comparison on an absent key reports clean for everything" % k)
gone = [i for i in before if i not in after]
moved = [i for i in before if i in after and after[i].get(k) != before[i].get(k)]
added = [i for i in after if i not in before]
if gone or moved:
    print("NOT RESTORED — moved: %s | missing from the board: %s" % (moved or "none", gone or "none"))
elif added:
    print("RESTORED CLEAN for the snapshotted items, but the run ADDED items the snapshot "
          "cannot restore: %s (an all-`new` disposition run — see step 4)" % added)
else:
    print("RESTORED CLEAN")
PY
```

**Anything other than `RESTORED CLEAN` means the fixture is still spent.** Repeat step 6 for the
listed ids and re-run this step. `CANNOT VERIFY` is a failure of the check, not a pass — never read
it as clean.

---

## Budget spent outside the window, on purpose

| step | call | points |
|---|---|---|
| 1a | `project item-list` | 31 |
| 1b | `api graphql` (the cheap field query) | 1 |
| 6 | `item-edit` × 4 | 4 |
| 7 | `project item-list` | 31 |
| | **total** | **67** |

67 points of the 5000/hour budget buys a measurement that does not spend the fixture. Moving any of
them inside the differenced window to save them stops the number measuring what SC-01 asks about.

## Recording the result

Report: `B1 - B0` (per move), `B2 - B1` (total), the disposition mix you ran, the fleet file you
pinned in step 0, and what step 7 printed. **You decide met / not_met; this script does not.**


---

# RESULT — 2026-08-10 — SC-01 per-move clause: **MET**

Run by the main session, on the operator's explicit instruction in session `factory`. The struck
total clause means steps 4-7 were not run: no `factory_decompose`, no restore needed.

## The measurement

| Reading | Value |
|---|---|
| B0, before | 925 |
| B1, after `project_field_set` | 927 |
| **B1 - B0** | **2** |

Command, verbatim — the shipped function, not hand-issued `gh` calls:

```
factory_gh.project_field_set("mruangutai", 6, "PVTI_lAHOAAases4Bf5NHzg15zec", "Station", "Ready")
```

## The A/B, measured in the same session on the same board

The "104 today" figure was recorded before the change. It was re-measured here so the comparison is
one measurement against another rather than a new number against a remembered one:

| Call | Points |
|---|---|
| `gh project field-list 6` | 102 |
| `gh project view 6` | 2 |
| **old path total** | **104** |
| **new path (`project_field_set`)** | **2** |

## The fixture

No restore was required: the item was already in `Ready` and was set to `Ready`, so the call was a
real write through the shipped path and a no-op on the fixture's state. Verified by re-reading the
board afterwards and diffing station values for all four items — **RESTORED CLEAN**, nothing moved,
nothing added, nothing missing.

## What was NOT measured

SC-01's total clause, struck by the operator on 2026-08-10. A four-task `factory_decompose` was never
run. The reason it was struck is issue #217: `_find_existing_item_id` reads the whole board once per
`partial` task, measured on board 3 at 203 points, so the total floors near 812 regardless of this
feature. The 31-point figure in step 4's table above is stale and superseded by that measurement.
