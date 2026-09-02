---
name: harness-code-risk-grading
description: Keep Python functions readable by grading cyclomatic, cognitive, and ABC complexity. Apply before review whenever changing Python.
user-invocable: false
---

# Code-risk grading

Write functions that remain easy to read, change, and review. Aim for **grade 4 or better in
production code** and **grade 3 or better in test code**. These are design bars, not an invitation
to make unrelated cleanup changes or to split coherent logic into meaningless helpers.

## Habits that keep a function at or above the bar

### Return early instead of nesting

Before — grade 4: the happy path is indented below an exceptional case, adding cognitive nesting.

```python
def display_name(user):
    if user is not None:
        if user.is_active:
            return user.name
    return "anonymous"
```

After — grade 5: the error case exits first, so the happy path stays flat.

```python
def display_name(user):
    if user is None or not user.is_active:
        return "anonymous"
    return user.name
```

The cognitive score falls because the second decision no longer nests beneath the first.

### Give one loop to one function

Before — grade 3: the inner loop adds both cyclomatic branches and cognitive nesting.

```python
def matching_pairs(left, right):
    pairs = []
    for item in left:
        for candidate in right:
            if item == candidate:
                pairs.append(item)
    return pairs
```

After — grade 4: extract the inner search when it has its own reason to change.

```python
def matching_pairs(left, right):
    return [item for item in left if contains(right, item)]


def contains(items, target):
    for item in items:
        if item == target:
            return True
    return False
```

The original function loses nested-loop cognitive cost; the helper has one loop and one decision.

### Name a compound condition

Before — grade 4: a long condition adds boolean operands and conceals the decision's purpose.

```python
def can_publish(user, document):
    return user.is_active and user.is_editor and document.is_draft and not document.is_locked
```

After — grade 5: the caller carries one named decision, while the predicate owns its details.

```python
def can_publish(user, document):
    return is_editable_draft(user, document)


def is_editable_draft(user, document):
    return user.is_active and user.is_editor and document.is_draft and not document.is_locked
```

The public function's ABC and cognitive scores fall; the predicate is independently reviewable.

### Handle the error case first

Before — grade 4: work is nested below the success condition.

```python
def parse_port(value):
    if value.isdigit():
        port = int(value)
        if 0 < port < 65536:
            return port
    raise ValueError("invalid port")
```

After — grade 5: reject invalid input at the boundary and leave the normal path unindented.

```python
def parse_port(value):
    if not value.isdigit():
        raise ValueError("invalid port")
    port = int(value)
    if not 0 < port < 65536:
        raise ValueError("invalid port")
    return port
```

The happy path no longer sits inside a decision; cognitive nesting falls even when the same cases
remain.

### One reason to change per function

Before — grade 3: parsing, validation, and rendering couple unrelated branches.

```python
def render_limit(value):
    if not value.isdigit():
        raise ValueError("limit")
    if int(value) > 100:
        return "too high"
    return f"limit: {value}"
```

After — grade 4: validation has one reason to change and rendering has another.

```python
def parse_limit(value):
    if not value.isdigit():
        raise ValueError("limit")
    return int(value)


def render_limit(value):
    return "too high" if value > 100 else f"limit: {value}"
```

Separating responsibilities keeps each function's decisions and ABC assignments local.

## Reference

The grader evaluates three metrics independently and assigns the **worst** resulting band. It never
averages them.

| Grade | Cyclomatic | Cognitive | ABC |
|---|---:|---:|---:|
| 5 | <= 4 | <= 3 | <= 8 |
| 4 | <= 8 | <= 9 | <= 20 |
| 3 | <= 10 | <= 15 | <= 26 |
| 2 | <= 20 | <= 30 | <= 45 |
| 1 | above any grade-2 limit | above any grade-2 limit | above any grade-2 limit |

For example, a function with cyclomatic 4, cognitive 16, and ABC 7 is **grade 2**: cyclomatic and
ABC look good, but cognitive is the worst metric and controls the grade.

Cognitive is a **Sonar-style approximation**, not SonarSource's algorithm; do not expect the same
number as a Sonar report. Shell scripts and TypeScript are not graded at all. This grading also does
not fix code already below the bar: that cleanup is separate and deliberately not a touch-it-fix-it
ratchet.

## Review semantics and self-check

A gated function below its bar and not grade 2 — grade 1 anywhere, or grade 3 in production — is a **high** finding and fails review under the existing review rule. A
grade-2 function passes only with a written reason naming the function. Before review, inspect your
changed Python functions with:

```sh
python3 <HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main HEAD)" --head HEAD
```

The tool is evidence, not the last word: improve a function when its shape is hard to understand even
if the numbers pass.

## Worked examples

```python
def add_one(value):
    return value + 1
```
EXPECTED GRADE: 5

```python
def four_way(value):
    result = 0
    if value == 0:
        result += 0
    if value == 1:
        result += 1
    if value == 2:
        result += 2
    if value == 3:
        result += 3
    return result
```
EXPECTED GRADE: 4

```python
def five_way(value):
    result = 0
    if value == 0:
        result += 0
    if value == 1:
        result += 1
    if value == 2:
        result += 2
    if value == 3:
        result += 3
    if value == 4:
        result += 4
    return result
```
EXPECTED GRADE: 4

```python
def eight_way(value):
    result = 0
    if value == 0:
        result += 0
    if value == 1:
        result += 1
    if value == 2:
        result += 2
    if value == 3:
        result += 3
    if value == 4:
        result += 4
    if value == 5:
        result += 5
    if value == 6:
        result += 6
    if value == 7:
        result += 7
    return result
```
EXPECTED GRADE: 3

```python
def twenty_way(value):
    result = 0
    if value == 0:
        result += 0
    if value == 1:
        result += 1
    if value == 2:
        result += 2
    if value == 3:
        result += 3
    if value == 4:
        result += 4
    if value == 5:
        result += 5
    if value == 6:
        result += 6
    if value == 7:
        result += 7
    if value == 8:
        result += 8
    if value == 9:
        result += 9
    if value == 10:
        result += 10
    if value == 11:
        result += 11
    if value == 12:
        result += 12
    if value == 13:
        result += 13
    if value == 14:
        result += 14
    if value == 15:
        result += 15
    if value == 16:
        result += 16
    if value == 17:
        result += 17
    if value == 18:
        result += 18
    if value == 19:
        result += 19
    return result
```
EXPECTED GRADE: 1
