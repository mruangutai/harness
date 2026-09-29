"""FEAT-70 clean-pin receipts. Usage (from the FEAT-70 worktree root):
    python3 notes/receipt-scripts/feat70-cleanpin.py <pin-sha> <baseline-sha>
Creates (or reuses) detached checkouts under .claude/worktrees/harness/ for the pin and the baseline
(never fetching, never deleting a pre-existing worktree), asserts both identities and
`git status --porcelain` empty, discovers the plan corpus at the pin, runs feat70-baseline.py ONCE in
each checkout (every byte, hash, diff and verdict below derives from those two executions plus the
SC-03 cross-run and the two grade assertions, each run once), compares after replacing ONLY each
measurement's absolute root with `<checkout>`, and writes notes/clean-pin-byte-receipts.generated.md
carrying `implementation_pin: <full sha>`.

A difference that survives the one normalisation is listed with its exact bytes and is RED unless
notes/divergence-rulings.json carries an operator ruling naming that exact record (case + ordinal +
stream, or scratch index + stream); the ruling's author, date and reason are printed beside it."""
import datetime, difflib, hashlib, json, os, subprocess, sys

ROOT = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.dirname(HERE)
pin, baseline = sys.argv[1], sys.argv[2]
OWN = ".harness/harness/features/FEAT-70-long-file-plan-merge-package"
MAIN = ROOT.split("/.claude/worktrees/")[0]          # the repository's root checkout, worktree or not
WT = os.path.join(MAIN, ".claude", "worktrees", "harness")
pin_dir = os.path.join(WT, f"feat70-cleanpin-{pin[:8]}")
base_dir = os.path.join(WT, f"feat70-base-{baseline[:8]}")
for d, ref in ((pin_dir, pin), (base_dir, baseline)):
    if not os.path.isdir(d):
        subprocess.run(["git", "-C", MAIN, "worktree", "add", "--detach", d, ref], check=True, capture_output=True)
full = {}
for label, d, ref in (("pin", pin_dir, pin), ("baseline", base_dir, baseline)):
    full[label] = subprocess.check_output(["git", "-C", d, "rev-parse", "HEAD"], text=True).strip()
    assert full[label].startswith(ref), f"{label} checkout is at {full[label]}, not {ref}"
    assert not subprocess.check_output(["git", "-C", d, "status", "--porcelain"], text=True), f"{label} checkout is dirty"

plan_list = f"/tmp/feat70-plans-{full['pin'][:8]}.txt"
plans = [l for l in subprocess.check_output(["git", "-C", pin_dir, "ls-files", ".harness/harness/features/*/plan.yaml"],
                                            text=True).splitlines() if not l.startswith(OWN + "/")]
open(plan_list, "w").write("\n".join(plans) + "\n")

# `--reuse`: read an existing measurement JSON instead of executing again. The receipt still derives
# from exactly one execution per side — the one whose `started`/`finished` stamps it prints — so an
# operator ruling recorded after the fact does not force a second measurement.
runs = {}
for label, d in (("baseline", base_dir), ("pin", pin_dir)):
    out = f"/tmp/feat70-{label}-{full[label][:8]}.json"
    if "--reuse" in sys.argv and os.path.exists(out):
        print(f"== {label}: reusing {out}", flush=True)
    else:
        print(f"== {label} measurements in {d}", flush=True)
        subprocess.run([sys.executable, os.path.join(HERE, "feat70-baseline.py"), d, plan_list, out], check=True)
    runs[label] = json.load(open(out))
started = min(runs[l]["started"] for l in runs)

# --- SC-03 cross-run: the PIN's regression case against each implementation, plus a standalone
# reproduction capturing plan and ledger bytes (the case deletes its fixture in `finally`). ---
SC03 = "case_feat70_record_amendments_after_a_block_scalar_splice"
def sc03_run(cli_root):
    code = (
        "import importlib.util,sys,os,json,shutil,subprocess\n"
        "os.environ.pop('HARNESS_AGENT_TYPE',None)\n"
        f"sys.path.insert(0,{os.path.join(pin_dir, 'tests', 'integration')!r})\n"
        f"s=importlib.util.spec_from_file_location('suite',{os.path.join(pin_dir, 'tests', 'integration', 'test-plan-merge.py')!r}); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
        f"m.{SC03}()\n"
        "checks=[(n,bool(ok),(d or '')[:600]) for n,ok,d in m.RESULTS]\n"
        "root,plan,fj=m._amend_fixture(plan_text=m._BLOCK_FIRST_PLAN)\n"
        "m.run_verb('sign-approval','--file',plan,'--by','X','--date','2026-01-01')\n"
        "pb,fb=m.read(plan),m.read(fj)\n"
        "r=m._record(plan,m._digest_with(m._BLOCK_FIRST_AMENDMENTS),root)\n"
        "pa,fa=m.read(plan),m.read(fj)\n"
        "shutil.rmtree(root,ignore_errors=True)\n"
        "print(json.dumps({'checks':checks,'argv':['record-amendments','--file','<fixture>/plan.yaml','--digest','<fixture>/digest.md'],'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'plan_before':pb,'plan_after':pa,'ledger_before':fb,'ledger_after':fa}))\n")
    env = dict(os.environ, PLAN_MERGE_BIN=os.path.join(cli_root, ".claude", "skills", "harness", "bin", "plan-merge.py"))
    env.pop("HARNESS_AGENT_TYPE", None)
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=pin_dir, timeout=600)
    data = json.loads(p.stdout.strip().splitlines()[-1])
    data["command"] = f"PLAN_MERGE_BIN={env['PLAN_MERGE_BIN']} python3 -c '<the pin suite: {SC03}(); then the same fixture signed and recorded, bytes captured>'"
    return data
sc03 = {"baseline": sc03_run(base_dir), "pin": sc03_run(pin_dir)}

ASSERT = os.path.join(HERE, "feat70-grade-assert.py")
green = subprocess.run([sys.executable, ASSERT, full["pin"], full["baseline"]], capture_output=True, text=True, cwd=ROOT)
red = subprocess.run([sys.executable, ASSERT, full["pin"], full["baseline"], "--tree", full["baseline"]], capture_output=True, text=True, cwd=ROOT)
finished = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")

# --- comparisons ---------------------------------------------------------------------------------
sha = lambda s: None if s is None else hashlib.sha1(s.encode("utf-8", "surrogateescape")).hexdigest()
def norm(text, root):
    return None if text is None else text.replace(root, "<checkout>")
rulings = {}
rpath = os.path.join(NOTES, "divergence-rulings.json")
if os.path.exists(rpath):
    for r in json.load(open(rpath)):
        rulings[r["record"]] = r

def diff_lines(a, b):
    return [l for l in difflib.unified_diff((a or "").splitlines(), (b or "").splitlines(), lineterm="", n=0)
            if l.startswith(("-", "+")) and not l.startswith(("---", "+++"))]

# suites
b_cases, p_cases = runs["baseline"]["cases"], runs["pin"]["cases"]
pre_existing = [c for c in p_cases if c != SC03]
cases_identical = b_cases == pre_existing and len(pre_existing) == 107
suite_ok = {l: runs[l]["suite"]["exit"] == 0 and not runs[l]["suite"]["fail_lines"] for l in ("baseline", "pin")}
sc03_present = SC03 in p_cases

# behavioural ledger, aligned by ordinal after dropping the pin's SC-03 invocations
b_led = runs["baseline"]["ledger"]
p_led = [r for r in runs["pin"]["ledger"] if r["case"] != SC03]
ledger_diffs = []          # (record-id, stream, old, new, ruling)
count_diff = len(b_led) != len(p_led)
ordinal = {}
for i, (b, p) in enumerate(zip(b_led, p_led)):
    ordinal[b["case"]] = ordinal.get(b["case"], 0) + 1
    rid = f"{b['case']}#{ordinal[b['case']]}"
    if b["case"] != p["case"]:
        ledger_diffs.append((rid, "case", b["case"], p["case"], None)); continue
    fields = {"argv": (" ".join(norm(a, base_dir) for a in b["argv"]), " ".join(norm(a, pin_dir) for a in p["argv"])),
              "exit": (str(b["exit"]), str(p["exit"])),
              "stdout": (norm(b["stdout"], base_dir), norm(p["stdout"], pin_dir)),
              "stderr": (norm(b["stderr"], base_dir), norm(p["stderr"], pin_dir)),
              "plan_before": (norm(b["plan_before"], base_dir), norm(p["plan_before"], pin_dir)),
              "plan_after": (norm(b["plan_after"], base_dir), norm(p["plan_after"], pin_dir))}
    for stream, (x, y) in fields.items():
        if x != y:
            ledger_diffs.append((rid, stream, x, y, rulings.get(f"{rid}:{stream}")))
behavioral_pass = not count_diff and all(r[4] for r in ledger_diffs)

# scratch plans, aligned by index
b_sc, p_sc = runs["baseline"]["scratch"], runs["pin"]["scratch"]
scratch_diffs = []
scratch_count_diff = len(b_sc["records"]) != len(p_sc["records"]) or b_sc["plans"] != p_sc["plans"]
for i, (b, p) in enumerate(zip(b_sc["records"], p_sc["records"])):
    rid = f"scratch#{i}:{b['plan']}:{' '.join(b['argv'][:1])}"
    for stream in ("argv", "exit", "stdout", "stderr", "after_sha", "plan_after"):
        x = " ".join(b["argv"]) if stream == "argv" else b[stream]
        y = " ".join(p["argv"]) if stream == "argv" else p[stream]
        if stream == "after_sha":     # bytes are stored only for a command that changed its plan
            x, y = (x, y) if b["before_sha"] != b["after_sha"] or p["before_sha"] != p["after_sha"] else (None, None)
        x, y = norm(str(x) if stream == "exit" else x, b_sc["scratch_root"]), norm(str(y) if stream == "exit" else y, p_sc["scratch_root"])
        if x != y:
            scratch_diffs.append((rid, stream, x, y, rulings.get(f"{rid}:{stream}")))
scratch_pass = not scratch_count_diff and all(r[4] for r in scratch_diffs)

sc03_red = sc03["baseline"]["exit"] != 0 and "IndexError" in sc03["baseline"]["stderr"] and not all(c[1] for c in sc03["baseline"]["checks"])
sc03_green = sc03["pin"]["exit"] == 0 and all(c[1] for c in sc03["pin"]["checks"])
overall = all([cases_identical, suite_ok["baseline"], suite_ok["pin"], sc03_present, behavioral_pass, scratch_pass,
               sc03_red, sc03_green, green.returncode == 0, red.returncode != 0])

# --- the receipt ---------------------------------------------------------------------------------
P = "PASS"; F = "FAIL"
out = ["# FEAT-70 — clean-checkout implementation-pin receipts (GENERATED by receipt-scripts/feat70-cleanpin.py; do not edit)", "",
       f"implementation_pin: {full['pin']}", f"baseline: {full['baseline']}", "",
       f"baseline_existing_cases: {len(b_cases)}/107 {P if suite_ok['baseline'] and cases_identical else F}",
       f"pin_existing_cases: {len(pre_existing)}/107 {P if suite_ok['pin'] and cases_identical else F}",
       f"sc03_regression: baseline {'red' if sc03_red else 'NOT RED'}, pin {'green' if sc03_green else 'NOT GREEN'}",
       f"behavioral_identity: {P if behavioral_pass else F}",
       f"scratch_identity: {P if scratch_pass else F}",
       f"grade_assert: pin exit {green.returncode} (green required), baseline exit {red.returncode} (red required)",
       f"overall: {P if overall else F}", "",
       f"Written {finished} (measurements started {started}), AFTER the pin it names; this file and its commit are not inside the pin — no receipt or script is claimed to exist in the pin.", "",
       f"- implementation pin: `{full['pin']}`", f"- baseline: `{full['baseline']}` (the worktree's base; origin/main when it was cut)",
       f"- pin checkout: `{pin_dir}` (detached, `git status --porcelain` empty, asserted)",
       f"- baseline checkout: `{base_dir}` (detached, `git status --porcelain` empty, asserted)",
       f"- one execution per measurement per checkout: `feat70-baseline.py <checkout> <plan-list> <json>` ran once in each (baseline {runs['baseline']['started']}→{runs['baseline']['finished']}, pin {runs['pin']['started']}→{runs['pin']['finished']}); the SC-03 cross-run and the two grade assertions ran once each at receipt time; the JSONs are the only source of every byte, hash, diff and verdict here.",
       "- normalisation: each measurement's own absolute root (the checkout, or the scratch copy's root for the scratch-plan script) replaced by `<checkout>`, on both sides, and nothing else. Every remaining difference is listed below verbatim; it is RED unless `notes/divergence-rulings.json` carries the operator's ruling for that exact record and stream.",
       "- determinism applied identically on both sides by the same driver, never to the tool's bytes: fixture directories from a counter under one fixed root; the tool's clock frozen inside the recording shim (`reset_at` would otherwise differ by the seconds between the two executions); consecutive `subprocess.Popen` calls serialised inside `case_concurrency_real` (the lock race is the scheduler's outcome, not the tool's; the plain suite run below still races for real).",
       f"- scratch-plan corpus: {len(plans)} `plan.yaml` tracked at the pin, discovered by `git ls-files` in the pin checkout, this feature's own record excluded (`{OWN}`), the same list handed to both sides; each side ran in a scratch copy of its checkout with that directory removed (`{b_sc['scratch_root']}` / `{p_sc['scratch_root']}`, deleted after the run).", "",
       "## Suite receipts (plain runs, real concurrency)", "",
       "| side | command | exit | FAIL lines | CASES | stdout sha | stderr sha |", "|---|---|---|---|---|---|---|"]
for l in ("baseline", "pin"):
    s = runs[l]["suite"]
    out.append(f"| {l} | `python3 tests/integration/test-plan-merge.py` in `{runs[l]['root']}` | {s['exit']} | {len(s['fail_lines'])} | {len(runs[l]['cases'])} | {s['stdout_sha'][:12]} | {s['stderr_sha'][:12]} |")
out += ["", f"Pre-existing case identities identical and 107 in number: **{'yes' if cases_identical else 'NO'}**; the pin adds `{SC03}`: **{'yes' if sc03_present else 'NO'}**.", "",
        "## Behavioural identity ledger (every CLI subprocess the 107 cases fork, via the recording shim)", "",
        f"- baseline invocations: {len(b_led)}; pin invocations excluding `{SC03}`: {len(p_led)}; counts {'equal' if not count_diff else '**DIFFER**'}",
        f"- records compared per invocation, aligned by case identity and per-case ordinal: argv, exit, stdout, stderr, plan bytes before, plan bytes after",
        f"- differing records: {len(ledger_diffs)}; of which ruled by the operator: {sum(1 for r in ledger_diffs if r[4])}", ""]
for rid, stream, x, y, ruling in ledger_diffs:
    out += [f"### `{rid}` — {stream} — {'RULED by ' + ruling['by'] + ' ' + ruling['date'] + ': ' + ruling['reason'] if ruling else '**UNRULED**'}", "```"] + diff_lines(x, y) + ["```", ""]
if not ledger_diffs:
    out += ["none", ""]
out += ["## Scratch-plan identity (the corpus above, per command)", "",
        f"- commands: baseline {len(b_sc['records'])}, pin {len(p_sc['records'])}; {'equal' if not scratch_count_diff else '**DIFFER**'}",
        f"- differing records: {len(scratch_diffs)}; ruled: {sum(1 for r in scratch_diffs if r[4])}", ""]
for rid, stream, x, y, ruling in scratch_diffs:
    out += [f"### `{rid}` — {stream} — {'RULED by ' + ruling['by'] + ' ' + ruling['date'] + ': ' + ruling['reason'] if ruling else '**UNRULED**'}", "```"] + diff_lines(x, y)[:40] + ["```", ""]
if not scratch_diffs:
    out += ["none", ""]
import collections
verbs = collections.Counter((r["argv"][0], r["exit"]) for r in p_sc["records"])
out += ["Pin-side command/exit census: " + ", ".join(f"`{v}`→{e}: {n}" for (v, e), n in sorted(verbs.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))), "",
        "## SC-03 red-first (the pin's regression case and fixture against each implementation)", ""]
for l in ("baseline", "pin"):
    d = sc03[l]
    out += [f"### {l}", f"- command: `{d['command']}`", f"- record-amendments exit {d['exit']}; stdout sha {sha(d['stdout'])[:12]}; stderr sha {sha(d['stderr'])[:12]}",
            f"- plan bytes sha before/after: {sha(d['plan_before'])[:12]} / {sha(d['plan_after'])[:12]} ({'unchanged' if d['plan_before'] == d['plan_after'] else 'changed'}); ledger bytes sha before/after: {sha(d['ledger_before'])[:12]} / {sha(d['ledger_after'])[:12]} ({'unchanged' if d['ledger_before'] == d['ledger_after'] else 'changed'})",
            "- checks: " + "; ".join(f"{'PASS' if ok else 'FAIL'} {n}" for n, ok, _ in d["checks"]),
            "- stderr tail:", "```", d["stderr"].rstrip()[-700:], "```", ""]
out += ["## SC-01: feat70-grade-assert.py at the pin — green", "", f"`python3 notes/receipt-scripts/feat70-grade-assert.py {full['pin']} {full['baseline']}` → exit {green.returncode}", "```", (green.stdout + green.stderr).rstrip(), "```", "",
        "## SC-01 red-first: the same assertion graded over the baseline tree — red", "", f"`python3 notes/receipt-scripts/feat70-grade-assert.py {full['pin']} {full['baseline']} --tree {full['baseline']}` → exit {red.returncode}", "```", (red.stdout + red.stderr).rstrip()[:3000], "```", "",
        "## code_grade records (from the two feat70-baseline.py executions)", ""]
for l in ("baseline", "pin"):
    g = runs[l]["code_grade"]
    out += [f"- {l}: {len(g['functions'])} function(s) over {len(g['files'])} file(s); below bar 4: {[(f['qualname'], f['grade']) for f in g['functions'] if f['grade'] < 4]}"]
path = os.path.join(NOTES, "clean-pin-byte-receipts.generated.md")
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[:12]))
print(f"... written {path}")
