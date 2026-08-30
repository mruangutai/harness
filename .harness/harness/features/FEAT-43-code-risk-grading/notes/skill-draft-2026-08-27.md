# Writing code that stays under the complexity bar

Every function you write is graded 1 to 5. **The bar is grade 4.** The worst of three measures wins,
so you cannot trade a clean one against a bad one.

| grade | cyclomatic | cognitive | ABC |
| --- | --- | --- | --- |
| 5 | ≤ 4 | ≤ 3 | ≤ 8 |
| **4 — the bar** | **≤ 8** | **≤ 9** | **≤ 20** |
| 3 | ≤ 10 | ≤ 15 | ≤ 26 |
| 2 | ≤ 20 | ≤ 30 | ≤ 45 |
| 1 | > 20 | > 30 | > 45 |

## What the three measures actually count

**Cyclomatic** counts decision points plus one. Every `if`, `for`, `while`, `except`, `and`, `or`,
comprehension and `case` adds one. It tells you how many tests the function needs.

**Cognitive** counts breaks in linear reading **and adds the nesting depth each time**. An `if` at
the top level costs 1. The same `if` three levels deep costs 4. This is the one that punishes
nesting, and it is usually the one that fails you.

**ABC** is the magnitude of assignments, branches and conditions — `√(A²+B²+C²)`. Every function
call counts as a branch. It catches the long straight function the other two miss.

## The habits that keep you at grade 4

**Return early.** Guard clauses at the top, one level deep, instead of wrapping the body in `if`.
Every level of nesting you remove costs cognitive complexity nothing and saves it a lot.

**One loop per function.** A loop inside a loop costs 1 + 2 = 3 before the body does anything. If
you need two, the inner one is a function.

**Name the condition.** `if a and b and not c:` costs 3. `if is_eligible(x):` costs 1, and the
reader learns what it means.

**Handle errors at one level.** A `try` wrapping a loop wrapping an `if` stacks three nesting
increments onto everything inside. Extract the body.

**Split on the seam, not on the line count.** Cutting a function in half to satisfy a number, with
the halves sharing five variables, makes the code worse and a reviewer will say so. Split where the
responsibility changes.

## What this does not do

The numbers never overrule a human reviewer. A change with every function at grade 5 can still be
rejected. And a function that is genuinely irreducible — a parser, a dispatch table — can ship at
grade 2 with a stated reason.
