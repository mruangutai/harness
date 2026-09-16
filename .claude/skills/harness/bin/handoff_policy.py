"""The plan-keyed handoff exemption (DEC-174), shared by every reader and writer that asks
whether a feature owes its seam notes: check-state.py's INV-17 and gh-sync.py's ship refusal
(BUG-1129). One predicate, so the invariant and the write it protects cannot drift apart."""
import os

import artifact_accessors


def exempt_reason(fdir):
    """The plan-keyed exemption (DEC-174). Returns a reason string when the feature owes no
    handoff notes, or "" when it does. The second value is a detail to append to the
    violation when the plan could not be read.

    A feature built entirely main-session-direct runs no squad, crosses no seam and is owed
    no note. THREE CONJOINED CONDITIONS, all necessary: (1) a plan.yaml exists — a PLAN.md
    does NOT qualify and is never read here; (2) its tasks: list is present and NON-EMPTY;
    (3) EVERY task carries an explicit execution_mode of exactly main-session-direct.

    KEYED ON THE PLAN'S EXECUTION MODES, NEVER ON THE NOTES' ABSENCE. Keyed on absence, the
    invariant would be satisfied by the exact condition it exists to detect.

    Condition 2 is a vacuity guard and excludes nobody in today's corpus — every plan.yaml
    on disk has a non-empty tasks: list. It is kept because "every task is
    main-session-direct" is VACUOUSLY TRUE over an empty list, so a stub plan, a
    half-written one, or one whose tasks: key was mistyped would otherwise be silently
    exempted from a seam invariant. What actually excludes FEAT-01 through FEAT-05 is
    condition 1, in all five cases.

    A DELIBERATE FALSE NEGATIVE: FEAT-06 and FEAT-07 are all-main-session-direct too, but on
    PLAN.md, so condition 1 keeps them non-exempt and they keep owing their notes. That is
    the safe direction and costs nothing — both already carry every note their status
    demands. Do not widen condition 1 to reach PLAN.md.

    FAIL CLOSED: any read error, parse error or non-mapping task entry is NOT exempt.
    """
    pp = os.path.join(fdir, "plan.yaml")
    if not os.path.isfile(pp):
        return "", ""
    try:
        pdoc = artifact_accessors.load_plan(pp) or {}
    except Exception as e:
        return "", f" (its plan.yaml does not parse, so no exemption could be evaluated: {e})"
    if not isinstance(pdoc, dict):
        return "", " (its plan.yaml is not a mapping, so no exemption could be evaluated)"
    tasks = pdoc.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return "", ""
    for t in tasks:
        if not isinstance(t, dict):
            return "", (" (its plan.yaml has a task that is not a mapping, so no "
                        "exemption could be evaluated)")
        if str(t.get("execution_mode", "")).strip() != "main-session-direct":
            return "", ""
    return (f"every task in its plan.yaml is execution_mode main-session-direct (DEC-174), "
            f"so no squad ran and no seam was crossed"), ""
