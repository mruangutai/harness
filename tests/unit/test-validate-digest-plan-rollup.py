#!/usr/bin/env python3
"""Unit floor for BUG-2582 T-02: the plan-team reader carve-out in validate-digest's roll-up.

The plan team's readers return FAIL to carry findings, and pm's `apply` step resolves those
findings in the same run. DEC-123's worst-member roll-up forced the team VERDICT to FAIL anyway.
The carve-out ranks a plan-team reader's FAIL as PASS only when every finding attributed to it is
recorded `resolved` in the feature's plan.yaml, checked on disk. Every other team, mission or
unresolvable case keeps worst-wins.

    VALIDATE_DIGEST=<path to validate-digest.py>  optional: load another validator (red-first)
    ./test-validate-digest-plan-rollup.py         -> exit 0 all pass, 1 otherwise
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(ROOT / "tests"))

import harness_boundary  # noqa: E402
import panel_findings  # noqa: E402
from harness_config_support import write_config  # noqa: E402

vd = harness_boundary.load_repo_module(
    "validate_digest_plan_rollup", os.environ.get("VALIDATE_DIGEST") or str(BIN / "validate-digest.py"))

FEATURE = "BUG-99-fixture"
RUN = "2026-11-27-01-plan-product"
PRODUCT = "harness-product-lead"
WORST = "worst member verdict"
NOT_APPLIED = "plan-team reader carve-out not applied"
TASK = {"id": "T-01", "title": "fixture task", "change_type": "bugfix",
        "execution_mode": "main-session-direct", "execution_reason": "fixture", "files": ["x.py"],
        "verify": "true", "intent": "fixture"}
SCOPE_READER = "harness-code-reviewer"

failures = []


def report(name, ok, detail=""):
    if ok:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


def finding(summary, reader=SCOPE_READER):
    return {"reader": reader, "kind": "substance", "scope": "none", "severity": "high",
            "summary": summary, "why": "fixture",
            "exposure": {"trigger": "plausible", "vs_today": "regression", "control": "chance"}}


def row(item, disposition="resolved", **override):
    out = {"id": panel_findings.finding_id(item["reader"], item["summary"]),
           "severity": item["severity"], "reader": item["reader"], "kind": item["kind"],
           "summary": item["summary"], "disposition": disposition}
    if disposition == "resolved":
        out["resolved_by"] = "T-01"
    out.update(override)
    return out


def members(**verdicts):
    """The plan team's six member entries; `verdicts` overrides a step's verdict."""
    steps = (("draft", "harness-pm"), ("scope", SCOPE_READER),
             ("should-not-exist", "fable-advisor"), ("design", "harness-ui-reviewer"),
             ("apply", "harness-pm"), ("goalcheck", "harness-pm"))
    base = {"scope": "FAIL"}
    base.update(verdicts)
    return [{"step": step, "persona": persona, "verdict": base.get(step, "PASS"),
             "headline": "fixture", "files_touched": []} for step, persona in steps]


def build(root, disk_findings=(), mission="plan", plan_text=None, with_plan=True,
          with_panel=True):
    """The fixture checkout; returns the feature directory."""
    (root / ".harness").mkdir(parents=True, exist_ok=True)
    (root / ".harness" / "team-config.yaml").write_text("agents: {}\n")
    write_config(root / ".harness" / "harness.json")
    feature = root / ".harness" / "harness" / "features" / FEATURE
    (feature / "runs" / RUN).mkdir(parents=True, exist_ok=True)
    (feature / "feature.json").write_text(json.dumps({
        "feature_id": FEATURE, "branch": "none", "pr": None, "review_sha": "none",
        "cycles_used": 0, "max_total_cycles": 10, "runs": [],
        "judgements": [{"at": "2026-11-27T00:00:00+00:00", "by": "operator", "kind": "mission",
                        "decision": mission, "reason": "fixture"}],
        "mission": mission}))
    if plan_text is not None:
        (feature / "plan.yaml").write_text(plan_text)
    elif with_plan:
        doc = {"schema": "plan/1", "feature": FEATURE, "status": "plan",
               "approval": {"status": "pending"}, "tasks": [TASK]}
        if with_panel:
            doc["panel"] = {"findings": list(disk_findings)}
        (feature / "plan.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))
    return feature


def product_digest(feature, verdict="PASS", findings=(), team="plan", member_list=None):
    digest = {"headline": "plan ready", "team": team, "cycles_used": 0,
              "members": member_list if member_list is not None else members(),
              "must_fix": [], "files_touched": [], "expertise_update": [],
              "branch": "none", "escalations": [], "adequacy_notes": [], "sc_status": [],
              "needs_approval": True, "severity_max": "high", "matrix_ok": "none",
              "coverage_gaps": [], "findings": [dict(item) for item in findings],
              "readers": [{"reader": "scope", "status": "ran", "persona": SCOPE_READER,
                           "reason": "none"},
                          {"reader": "should-not-exist", "status": "ran",
                           "persona": "fable-advisor", "reason": "none"},
                          {"reader": "design", "status": "ran",
                           "persona": "harness-ui-reviewer", "reason": "none"},
                          {"reader": "goalcheck", "status": "ran", "persona": "harness-pm",
                           "reason": "none"}],
              "open_questions": []}
    digest["steps_run"] = len(digest["members"])
    return {"VERDICT": verdict, "DIGEST": digest,
            "artifact": str(feature / "runs" / RUN / "digest.md")}


def other_lead_digest(lead, feature, run):
    digest = {"headline": "fixture", "team": "build", "steps_run": 1, "cycles_used": 0,
              "members": [{"step": "build", "persona": "backend-dev", "verdict": "FAIL",
                           "headline": "fixture", "files_touched": []}],
              "must_fix": [], "branch": "none", "files_touched": [], "open_questions": [],
              "escalations": [], "expertise_update": [], "sc_status": [], "adequacy_notes": [],
              "needs_approval": "none", "severity_max": "none", "matrix_ok": "none",
              "coverage_gaps": [], "findings": [], "readers": []}
    if lead == "harness-eng-lead":
        digest["amendments"] = []
    return {"VERDICT": "PASS", "DIGEST": digest,
            "artifact": str(feature / "runs" / run / "digest.md")}


def errors_of(persona, obj, feature, live=None):
    """validate()'s errors; `live` is the hook's live dispatch mission, None offline."""
    return vd.validate(persona, obj, feature_dir=str(feature), mission=live)


def joined(errors):
    return " | ".join(errors) if errors else "no errors"


def worst_error(errors, naming=None):
    return any(WORST in e.lower() and (naming is None or f"returned {naming}" in e)
               for e in errors)


def not_applied(errors, reason):
    return any(NOT_APPLIED in e.lower() and reason in e for e in errors)


def run_case(name, body):
    try:
        ok, detail = body()
    except Exception as exc:  # noqa: BLE001  a base-tree red must still print its line
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    report(name, ok, detail)


def in_fixture(body):
    """Run `body(root)` in a fresh fixture directory."""
    def wrapped():
        with tempfile.TemporaryDirectory() as tmp:
            return body(Path(os.path.realpath(tmp)))
    return wrapped


F1 = finding("first fixture finding")
F2 = finding("second fixture finding")


def accepted(verdict="PASS", findings=(F1, F2), disk=None, member_list=None, live=None,
             **build_kw):
    """A case expecting no errors at all."""
    def body(root):
        feature = build(root, [row(f) for f in findings] if disk is None else disk, **build_kw)
        errors = errors_of(PRODUCT, product_digest(feature, verdict, findings,
                                                   member_list=member_list), feature, live)
        return not errors, joined(errors)
    return in_fixture(body)


def denied(reason=None, naming=None, findings=(F1, F2), disk=None, member_list=None,
           team="plan", alternatives=(), live=None, **build_kw):
    """A case expecting the worst-member refusal and, with `reason`, the not-applied text."""
    def body(root):
        feature = build(root, [row(f) for f in findings] if disk is None else disk, **build_kw)
        errors = errors_of(PRODUCT, product_digest(feature, "PASS", findings, team, member_list),
                           feature, live)
        ok = worst_error(errors, naming)
        if reason is not None:
            ok = ok and any(not_applied(errors, text) for text in (reason, *alternatives))
        return ok, joined(errors)
    return in_fixture(body)


def relief_with_reader(reader):
    items = (finding("first fixture finding", reader), finding("second fixture finding", reader))
    return accepted(findings=items)


WITNESS_FINDINGS = (finding("first fixture finding", "code-reviewer"),
                    finding("second fixture finding", "code-reviewer"))


def write_fan_in(feature):
    """The lead's reader fan-in, as panel-c1.md, carrying the two witness findings."""
    fan_in = {"DIGEST": {
        "readers": [{"reader": step, "status": "ran", "persona": persona, "reason": "fixture"}
                    for step, persona in (("scope", SCOPE_READER),
                                          ("should-not-exist", "fable-advisor"),
                                          ("design", "harness-ui-reviewer"))],
        "findings": [{key: item[key] for key in ("reader", "severity", "kind", "summary",
                                                 "exposure")}
                     for item in WITNESS_FINDINGS]}}
    panel_md = feature / "runs" / RUN / "panel-c1.md"
    panel_md.write_text("# Plan panel fan-in, fixture\n\n```yaml\n"
                        + yaml.safe_dump(fan_in, sort_keys=False) + "```\n")
    return panel_md


def plan_merge(root, stdin_text, *argv):
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    env.pop("HARNESS_AGENT_TYPE", None)
    return subprocess.run([sys.executable, str(BIN / "plan-merge.py"), *argv],
                          input=stdin_text, cwd=root, env=env, capture_output=True,
                          text=True, timeout=60)


def resolved_panel(plan):
    panel = yaml.safe_load(plan.read_text())["panel"]
    for item in panel["findings"]:
        item["disposition"] = "resolved"
        item["resolved_by"] = "T-01"
    return yaml.safe_dump(panel, sort_keys=False)


@in_fixture
def case_producer_witness(root):
    feature = build(root, with_panel=False)
    plan = feature / "plan.yaml"
    recorded = plan_merge(root, "", "record-panel", "--file", str(plan), "--digest",
                          str(write_fan_in(feature)), "--cycle", "1")
    if recorded.returncode != 0:
        return False, f"record-panel exit={recorded.returncode} {recorded.stderr.strip()}"
    resolved = plan_merge(root, resolved_panel(plan), "set-panel", "--file", str(plan),
                          "--value-file", "/dev/stdin")
    if resolved.returncode != 0:
        return False, f"set-panel exit={resolved.returncode} {resolved.stderr.strip()}"
    errors = errors_of(PRODUCT, product_digest(feature, "PASS", WITNESS_FINDINGS), feature)
    return not errors, joined(errors)


def case_apply_prompt_resolves():
    team = yaml.safe_load((ROOT / ".claude/skills/harness/teams/plan.yaml").read_text())
    step = next(s for s in team["steps"] if s.get("id") == "apply")
    prompt = " ".join(str(step.get("prompt", "")).split())
    spots = [prompt.find(t) for t in ("plan-merge.py record-panel", "plan-merge.py set-panel",
                                      "plan-merge.py check")]
    missing = [t for t in ("disposition: resolved", "resolved_by", "scope: mission")
               if t not in prompt]
    ok = -1 not in spots and spots == sorted(spots) and not missing
    return ok, f"verb positions {spots}, missing {missing}"


def other_lead(lead, run, member_list=None, team="build"):
    @in_fixture
    def body(root):
        feature = build(root, [row(F1), row(F2)])
        obj = other_lead_digest(lead, feature, run)
        if member_list is not None:
            obj["DIGEST"]["members"] = member_list
            obj["DIGEST"]["steps_run"] = len(member_list)
        obj["DIGEST"]["team"] = team
        errors = errors_of(lead, obj, feature)
        return worst_error(errors), joined(errors)
    return body


def case_reader_personas_match_team_file():
    team = yaml.safe_load((ROOT / ".claude/skills/harness/teams/plan.yaml").read_text())
    declared = {s["id"]: s.get("persona") for s in team["steps"]
                if s.get("id") in vd.PLAN_READER_STEPS}
    return declared == vd.PLAN_READER_PERSONAS, f"team file {declared!r}"


def without_step(step):
    return [m for m in members() if m["step"] != step]


def wrong_scope_persona():
    """The scope slot reported under a persona the team file does not declare for it."""
    member_list = members()
    next(m for m in member_list if m["step"] == "scope")["persona"] = "harness-security-reviewer"
    return member_list


SLOT_FINDINGS = (finding("first fixture finding", "scope"),
                 finding("second fixture finding", "scope"))


def skipped_advisor():
    member_list = without_step("should-not-exist")
    member_list.insert(2, {"step": "should-not-exist", "persona": "fable-advisor",
                           "status": "skipped", "reason": "fixture: the persona did not resolve"})
    return member_list


@in_fixture
def case_duplicate_step(root):
    feature = build(root, [row(F1), row(F2)])
    member_list = members()
    member_list.insert(2, {"step": "scope", "persona": "harness-security-reviewer",
                           "verdict": "ESCALATE", "headline": "fixture", "files_touched": []})
    errors = errors_of(PRODUCT, product_digest(feature, "PASS", (F1, F2), member_list=member_list),
                       feature)
    ok = worst_error(errors, "ESCALATE") and not_applied(errors, "duplicated reader step")
    return ok, joined(errors)


def relief_cases():
    return [
        ("bug2582-control-fail-verdict-valid", accepted(verdict="FAIL")),
        ("bug2582-relief-resolved", accepted()),
        ("bug2582-relief-reader-code-reviewer", relief_with_reader("code-reviewer")),
        ("bug2582-relief-reader-slot", relief_with_reader("scope")),
        ("bug2582-relief-dispatch-mission-plan", accepted(live="plan")),
        ("bug2582-relief-skipped-advisor", accepted(member_list=skipped_advisor())),
        ("bug2582-producer-witness", case_producer_witness),
        ("bug2582-apply-prompt-resolves", case_apply_prompt_resolves),
        ("bug2582-reader-personas-match-team-file", case_reader_personas_match_team_file),
    ]


def disk_denials():
    malformed = row(F2)
    del malformed["summary"]
    either = ("plan.yaml missing or unloadable",)
    return [
        ("bug2582-deny-open-on-disk", denied("is not resolved", disk=[row(F1), row(F2, "open")])),
        ("bug2582-deny-historical-open",
         denied("is not resolved",
                disk=[row(F1), row(F2), row(finding("an earlier fixture finding"), "open")])),
        ("bug2582-deny-absent-from-plan",
         denied("absent from plan.yaml panel.findings", disk=[row(F1)])),
        ("bug2582-deny-mismatched-row",
         denied("has no matching plan.yaml panel row",
                disk=[row(F1), row(F2, reader="fable-advisor")])),
        ("bug2582-deny-folded-disposition",
         denied("panel.findings malformed", alternatives=either,
                disk=[row(F1), row(F2, disposition="Resolved")])),
        ("bug2582-deny-malformed-row",
         denied("panel.findings malformed", alternatives=either, disk=[row(F1), malformed])),
        ("bug2582-deny-no-plan", denied("plan.yaml missing or unloadable", with_plan=False)),
        ("bug2582-deny-unloadable-plan",
         denied("plan.yaml missing or unloadable",
                plan_text=f"schema: plan/1\nfeature: {FEATURE}\nstatus: plan\ntasks: []\n")),
        ("bug2582-deny-mission-patch", denied("mission is not plan", mission="patch")),
    ]


def attribution_denials():
    return [
        ("bug2582-deny-no-findings",
         denied("no findings attributed to scope", findings=(), disk=[])),
        ("bug2582-deny-unattributable",
         denied("matches no member or more than one",
                findings=(F1, F2, finding("a stray fixture finding", "someone-else")))),
        ("bug2582-deny-ambiguous",
         denied("matches no member or more than one",
                disk=[row(F1), row(F2), row(finding("a pm fixture finding", "harness-pm"))])),
    ]


def roster_denials():
    return [
        ("bug2582-deny-duplicate-step", case_duplicate_step),
        ("bug2582-deny-missing-slot",
         denied("reader step design missing", member_list=without_step("design"))),
        ("bug2582-deny-persona-swap",
         denied("is not the team's", findings=SLOT_FINDINGS, member_list=wrong_scope_persona())),
        ("bug2582-deny-dispatch-mission-patch",
         denied("dispatch mission is not plan", live="patch")),
    ]


def rank_denials():
    return ([("bug2582-deny-team-build", denied(team="build"))]
            + [(f"bug2582-deny-nonreader-{step}",
                denied(member_list=members(scope="PASS", **{step: "FAIL"})))
               for step in ("draft", "apply", "goalcheck")]
            + [(f"bug2582-deny-{verdict.lower()}",
                denied(naming=verdict, member_list=members(scope=verdict)))
               for verdict in ("ESCALATE", "BLOCKED")])


def other_lead_cases():
    return [
        ("bug2582-other-lead-eng", other_lead("harness-eng-lead", "2026-11-27-02-build-engineering")),
        ("bug2582-other-lead-validator",
         other_lead("harness-validator-lead", "2026-11-27-02-validate-validator")),
        ("bug2582-guard-eng-lead-plan-steps",
         other_lead("harness-eng-lead", "2026-11-27-02-build-engineering",
                    member_list=members(), team="plan")),
    ]


def main():
    for name, body in (relief_cases() + disk_denials() + attribution_denials()
                       + roster_denials() + rank_denials() + other_lead_cases()):
        run_case(name, body)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
