#!/usr/bin/env python3
"""tests/integration/test-station-argument-spelling.py — witnesses that every
`gh-sync.py status` / `board-station.py` invocation quoted in the instruction
scope (.omp/commands/*.md and .claude/skills/**/*.md) names a station both
tools actually accept.

WHY THIS FILE EXISTS: FEAT-41 D-14 migrated the station CLI argument to
lowercase and left two instruction files behind teaching a spelling both
tools hard-refuse. Nothing caught that. This file is that witness.

THE SWEEP IS A PURE FUNCTION OF A ROOT, CALLED IN-PROCESS. Every helper below
takes an explicit root argument. There is no environment variable that
repoints the scope, no module-level scope override, no subprocess
re-invocation of this file, and therefore no recursion guard and no
conditionally-skipped rows. The negative control below calls the same
helpers on a scratch root inside the same process — it never reaches past
offenders().
"""
import glob
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, ".claude", "skills", "harness", "bin"))
import factory_config  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + " - " + name + (" (" + detail + ")" if detail and not ok else ""))


# ACCEPTED SETS ARE DERIVED, NEVER SPELLED — a hand-written list here would be the same
# defect this file is testing for. `gh-sync.py status` accepts the six MANDATED_STATIONS
# plus the terminal marker, matching gh-sync.py's own STATION_VALUES. `board-station.py`
# accepts only the six MANDATED_STATIONS — its own docstring says the terminal marker
# names no column and it validates against MANDATED_STATIONS alone.
ACCEPTED_STATIONS = {
    "gh-sync.py status": set(factory_config.MANDATED_STATIONS) | set(factory_config.TERMINAL_STATIONS),
    "board-station.py": set(factory_config.MANDATED_STATIONS),
}

EXPECTED_FILES = ("harness-plan.md", "github-mirror.md", "SKILL.md")
MIN_OCCURRENCES = 6

LIFECYCLE_FILES = {
    "plan": os.path.join(".omp", "commands", "harness-plan.md"),
    "patch": os.path.join(".omp", "commands", "harness-patch.md"),
    "playbook": os.path.join(".claude", "skills", "harness", "SKILL.md"),
    "build": os.path.join(".claude", "skills", "harness", "references", "build-phase.md"),
    "mirror": os.path.join(".claude", "skills", "harness", "references", "github-mirror.md"),
    "pm": os.path.join(".claude", "skills", "harness-spec-driven", "SKILL.md"),
    "plan_team": os.path.join(".claude", "skills", "harness", "teams", "plan.yaml"),
    "fix_team": os.path.join(".claude", "skills", "harness", "teams", "fix.yaml"),
}


def _load_lifecycle_files(root):
    loaded = {}
    for name, relative in LIFECYCLE_FILES.items():
        with open(os.path.join(root, relative), encoding="utf-8") as handle:
            loaded[name] = handle.read()
    return loaded


def _ordered(text, *needles):
    cursor = 0
    for needle in needles:
        found = text.find(needle, cursor)
        if found < 0:
            return False
        cursor = found + len(needle)
    return True


def _between(text, start, end):
    start_at = text.find(start)
    if start_at < 0:
        return ""
    end_at = text.find(end, start_at + len(start))
    return text[start_at:] if end_at < 0 else text[start_at:end_at]


def _flat(text):
    return re.sub(r"\s+", " ", text)


def _signature_violations(files):
    violations = []
    signature_order = (
        'approval_receipt="$(',
        "sign-approval",
        'resume_station="$(printf',
        'case "$resume_station" in',
        "gh-sync.py open <feature-dir>",
        'gh-sync.py status <feature-dir> "$resume_station"',
    )
    for name in ("plan", "patch"):
        section = _flat(_between(
            files[name],
            "**The signature is immediately followed by**",
            "\n- ",
        ))
        if not _ordered(section, *signature_order):
            violations.append(f"{name}: signature must capture and validate RESUME, then open before dynamic status")
        if "ready|building|review" not in section:
            violations.append(f"{name}: RESUME validation must accept exactly active post-signature stations")
    return violations


def _approval_reset_violations(files):
    violations = []
    approval_reset_rule = (
        "APPROVAL-RESET:",
        "gh-sync.py status <feature-dir> plan",
        "No `APPROVAL-RESET:` receipt means no remote call",
    )
    if not _ordered(_flat(files["pm"]), *approval_reset_rule):
        violations.append("pm: task mutations must condition Plan projection on the reset receipt")
    for step, end in (("- id: draft", "- id: scope"), ("- id: apply", "- id: goalcheck")):
        section = _flat(_between(files["plan_team"], step, end))
        if not _ordered(section, *approval_reset_rule):
            violations.append(f"plan_team {step}: task mutations must condition Plan projection on the reset receipt")
    return violations


def _build_phase_violations(files):
    violations = []
    build_entry = _flat(_between(files["build"], "1. **Build entry.**", "2. **The eng segment.**"))
    if not _ordered(
        build_entry,
        "github.build_entry",
        "recovery",
        "gh-sync.py open <feature-dir>",
        "gh-sync.py status <feature-dir> building",
        "before any task dispatch",
    ):
        violations.append("build: require the signature receipt, reserve open for recovery, and project Building before dispatch")
    validation = _flat(_between(files["build"], "4. **Entering validate**", "5. **ONE `validate` dispatch**"))
    if not _ordered(validation, "review_sha", "gh-sync.py status <feature-dir> review", "BEFORE"):
        violations.append("build: Review must be projected at validation entry before dispatch")
    fix_loop = _flat(_between(files["build"], "6. **The fix loop.**", "7. **The seam"))
    if not _ordered(
        fix_loop,
        "gh-sync.py status <feature-dir> building",
        "dispatch `fix`",
        "record it as the new `review_sha`",
        "next validation boundary",
        "gh-sync.py status <feature-dir> review",
        "before any subsequent validation dispatch or result handling",
    ):
        violations.append("build: each fix round must bracket dispatch with Building and next-boundary Review")
    return violations


def _reference_violations(files):
    violations = []
    if "gh-sync.py status" in files["fix_team"]:
        violations.append("fix_team: lifecycle checkpoints belong to the orchestrator, not the reader DAG")
    if not _ordered(
        _flat(files["playbook"]),
        "require the signature-created `github.build_entry` receipt",
        "gh-sync.py status <feature-dir> building",
        "before task dispatch",
        "gh-sync.py status <feature-dir> review",
        "before the `validate` dispatch",
        "gh-sync.py status <feature-dir> building",
        "before each `fix` dispatch",
        "gh-sync.py status <feature-dir> review",
        "at the next validation boundary",
    ):
        violations.append("playbook: active phase checkpoints must be explicit and ordered")
    if "same station to every unique recorded source, parent, and non-abandoned task card" not in _flat(files["mirror"]):
        violations.append("mirror: phase ownership must describe complete-card projection")
    return violations


def lifecycle_violations(files):
    return (
        _signature_violations(files)
        + _approval_reset_violations(files)
        + _build_phase_violations(files)
        + _reference_violations(files)
    )


def _swap_once(text, first, second):
    first_at = text.find(first)
    second_at = text.find(second, first_at + len(first))
    assert first_at >= 0 and second_at >= 0
    return text[:first_at] + second + text[first_at + len(first):second_at] + first + text[second_at + len(second):]

TOKEN_PATTERN = re.compile(r"(gh-sync\.py status|board-station\.py) \S+ ([A-Za-z_][A-Za-z_-]*)")


def scope_files(root):
    """Every instruction file in the sweep's scope: .omp/commands/*.md plus every
    .claude/skills/**/*.md. Nothing else (plan D-05): gh-sync.py quotes the old
    capitalized spelling as history, and .harness/harness/features is an immutable
    record, so a wider sweep would redden on text that must not change."""
    commands = glob.glob(os.path.join(root, ".omp", "commands", "*.md"))
    skills = glob.glob(os.path.join(root, ".claude", "skills", "**", "*.md"), recursive=True)
    return sorted(set(commands) | set(skills))


def occurrences(root):
    """(path, tool, token) for every quoted invocation of either tool in scope.

    Whitespace is collapsed before matching — load-bearing, not a convenience: the
    occurrence FEAT-41's migration missed spans a line break between the tool name and
    its argument, so a line-anchored pattern is blind to exactly the case this file
    exists for."""
    found = []
    for path in scope_files(root):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        collapsed = re.sub(r"\s+", " ", text)
        for match in TOKEN_PATTERN.finditer(collapsed):
            found.append((path, match.group(1), match.group(2)))
    return found


def offenders(root):
    """Every occurrence whose token is not in that tool's accepted set — the single
    predicate both cases below assert on, which is what lets the negative control run
    in-process."""
    return [(path, tool, token) for path, tool, token in occurrences(root)
            if token not in ACCEPTED_STATIONS[tool]]


def case_every_argument_is_accepted():
    scope = scope_files(REPO_ROOT)
    check("the instruction scope is non-empty", len(scope) > 0, str(len(scope)))

    found = occurrences(REPO_ROOT)
    check("at least the measured number of station-argument occurrences are found",
          len(found) >= MIN_OCCURRENCES, f"found {len(found)}, expected >= {MIN_OCCURRENCES}")

    basenames = {os.path.basename(path) for path, _tool, _token in found}
    for expected in EXPECTED_FILES:
        check(f"{expected} is among the swept occurrence files", expected in basenames, str(sorted(basenames)))

    bad = offenders(REPO_ROOT)
    check("every station argument in the instruction scope is an accepted station",
          bad == [], "; ".join(f"{path}:{tool}:{token}" for path, tool, token in bad))


def case_reddens_on_a_reintroduced_capital():
    with tempfile.TemporaryDirectory() as tmp:
        originals = (
            os.path.join(".omp", "commands", "harness-plan.md"),
            os.path.join(".claude", "skills", "harness", "references", "github-mirror.md"),
        )
        copies = {}
        for rel in originals:
            src = os.path.join(REPO_ROOT, rel)
            dst = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            copies[rel] = dst

        clean = offenders(tmp)
        check("the unmutated scratch copy reports no offender", clean == [],
              "; ".join(f"{path}:{tool}:{token}" for path, tool, token in clean))

        plan_copy = copies[os.path.join(".omp", "commands", "harness-plan.md")]
        with open(plan_copy, encoding="utf-8") as handle:
            before = handle.read()
        after = before.replace('status <feature-dir> "$resume_station"', "status <feature-dir> Ready")
        assert before != after, "the reintroduced-capital replace must not be a no-op"
        with open(plan_copy, "w", encoding="utf-8") as handle:
            handle.write(after)

        mutated = offenders(tmp)
        reddened = any(tool == "gh-sync.py status" and token == "Ready" and path == plan_copy
                        for path, tool, token in mutated)
        check("the sweep reddens on a reintroduced capital",
              bool(mutated) and reddened,
              "; ".join(f"{path}:{tool}:{token}" for path, tool, token in mutated))


def case_lifecycle_checkpoint_order_and_negative_controls():
    files = _load_lifecycle_files(REPO_ROOT)
    clean = lifecycle_violations(files)
    check("lifecycle instructions assign every checkpoint to its owner in event order",
          clean == [], "; ".join(clean))

    mutations = []

    literal = dict(files)
    literal["plan"] = literal["plan"].replace(
        'gh-sync.py status <feature-dir> "$resume_station"',
        "gh-sync.py status <feature-dir> ready",
        1,
    )
    mutations.append(("RESUME replaced by a literal", literal))

    status_first = dict(files)
    status_first["patch"] = _swap_once(
        status_first["patch"],
        "gh-sync.py open <feature-dir>",
        'gh-sync.py status <feature-dir> "$resume_station"',
    )
    mutations.append(("signature status placed before open", status_first))

    ignored_reset = dict(files)
    ignored_reset["pm"] = ignored_reset["pm"].replace("APPROVAL-RESET:", "RESET-IGNORED:", 1)
    mutations.append(("approval-reset receipt ignored", ignored_reset))

    late_build = dict(files)
    late_build["build"] = _swap_once(
        late_build["build"],
        "gh-sync.py status <feature-dir> building",
        "before any task dispatch",
    )
    mutations.append(("ordinary Build checkpoint placed after dispatch", late_build))

    late_validation = dict(files)
    late_validation["build"] = _swap_once(
        late_validation["build"],
        "gh-sync.py status <feature-dir> review",
        "5. **ONE `validate` dispatch**",
    )
    mutations.append(("validation checkpoint placed after dispatch", late_validation))

    fix_section = _between(files["build"], "6. **The fix loop.**", "7. **The seam")
    late_fix_section = _swap_once(
        fix_section,
        "gh-sync.py status <feature-dir> building",
        "dispatch `fix`",
    )
    late_fix = dict(files)
    late_fix["build"] = late_fix["build"].replace(fix_section, late_fix_section, 1)
    mutations.append(("must-fix Building placed after fix dispatch", late_fix))

    inside_dag = dict(files)
    inside_dag["fix_team"] += "\n# gh-sync.py status <feature-dir> review\n"
    mutations.append(("Review inserted inside the fix DAG", inside_dag))

    fix_section = _between(files["build"], "6. **The fix loop.**", "7. **The seam")
    late_review_section = _swap_once(
        fix_section,
        "gh-sync.py status <feature-dir> review",
        "before any subsequent validation dispatch or result handling",
    )
    late_review = dict(files)
    late_review["build"] = late_review["build"].replace(fix_section, late_review_section, 1)
    mutations.append(("post-fix Review placed after the next validation boundary", late_review))

    for label, mutated in mutations:
        violations = lifecycle_violations(mutated)
        check(f"lifecycle negative control reddens when {label}", bool(violations), repr(violations))




def main():
    for case in (
        case_every_argument_is_accepted,
        case_reddens_on_a_reintroduced_capital,
        case_lifecycle_checkpoint_order_and_negative_controls,
    ):
        case()
    if any(not row[1] for row in RESULTS):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
