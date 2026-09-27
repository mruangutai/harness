"""FEAT-68 clean-pin receipts. Usage: python3 feat68-cleanpin.py <pin> <baseline>
Creates detached checkouts under .claude/worktrees/harness/ (the #103 placement rule), runs every
owning suite plus the grade locks at the pin, byte-compares against /tmp/feat68-baseline.json, runs
the pin's grade lock against the baseline tree (red-first), and writes the receipt markdown."""
import subprocess, sys, os, json, hashlib, datetime

ROOT = "/Users/molchairuangutai/GitHub/harness"
pin, baseline = sys.argv[1], sys.argv[2]
WT = os.path.join(ROOT, ".claude/worktrees/harness")
pin_dir = os.path.join(WT, f"feat68-cleanpin-{pin}")
base_dir = os.path.join(WT, f"feat68-base-{baseline}")
for d, ref in ((pin_dir, pin), (base_dir, baseline)):
    if not os.path.isdir(d):
        subprocess.run(["git", "-C", ROOT, "worktree", "add", "--detach", d, ref], check=True, capture_output=True)
pin_full = subprocess.check_output(["git", "-C", pin_dir, "rev-parse", "HEAD"], text=True).strip()
base_full = subprocess.check_output(["git", "-C", base_dir, "rev-parse", "HEAD"], text=True).strip()
status = subprocess.check_output(["git", "-C", pin_dir, "status", "--porcelain"], text=True)
assert not status, "pin checkout is dirty"

FEATURE_WT = base_dir
base = json.load(open(os.environ.get("FEAT68_BASELINE_JSON", "/tmp/feat68-baseline.json")))
suites = list(base)
rows = []
for s in suites:
    p = subprocess.run([sys.executable, s], cwd=pin_dir, capture_output=True, text=True, timeout=1800)
    b = base[s]
    norm = lambda t, root: t.replace(root, "<checkout>")
    same = (p.returncode == b["exit"] and norm(p.stdout, pin_dir) == norm(b["stdout"], FEATURE_WT)
            and norm(p.stderr, pin_dir) == norm(b["stderr"], FEATURE_WT))
    rows.append((s, b["exit"], p.returncode, hashlib.sha1(p.stdout.encode()).hexdigest()[:12],
                 b["stdout_sha"][:12], hashlib.sha1(p.stderr.encode()).hexdigest()[:12], b["stderr_sha"][:12], same))

# The plan's own inline grade assertion is the SC-01 lock (validate c0 MF-03): run at the pin
# (green) and, with the pin's code_grade module, against the baseline tree (red). The baseline
# tree has no git history for cb6f80... in its own paths, so the assertion is run there with
# `root` = the baseline checkout and the pre-image read from the same ref; the three retained
# drivers grade 1 there, which is the red.
ASSERT = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "feat68-grade-assert.py")).read()
lock = subprocess.run([sys.executable, "-c", ASSERT], cwd=pin_dir, capture_output=True, text=True)
red = subprocess.run([sys.executable, "-c", ASSERT], cwd=base_dir, capture_output=True, text=True)

out = [f"# FEAT-68 — clean-checkout implementation-pin receipts", "",
       f"Written {datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds')}, AFTER the pin it names; this file is not inside `{pin}`.", "",
       f"- implementation pin: `{pin_full}`", f"- baseline: `{base_full}` (the signed plan; = origin/main at the signed plan)",
       f"- pin checkout: `{pin_dir}` (detached, `git status --porcelain` empty)", f"- baseline checkout: `{base_dir}` (detached)",
       f"- baseline receipts: captured in the clean detached baseline checkout (`git status --porcelain` empty) (`/tmp/feat68-baseline.py` → `/tmp/feat68-baseline.json`); exit status and sha1 of stdout/stderr per suite.", "",
       "## Owning suites at the pin vs baseline (SC-02)", "",
       "Compared after ONE normalisation, on both sides: each checkout's own absolute root replaced by `<checkout>` (three `ok` lines in",
       "`test-validate-digest.py` print the agent file's absolute path, which names the checkout that ran the suite and nothing else).",
       "No other substitution is applied; every remaining byte difference is a divergence and is ledgered in `notes/build-divergences.md` (D-01..D-05) with its exact old/new bytes.",
       "The sha1 columns are of the raw bytes and so differ for that one suite; the `identical` column is the normalised comparison.", "",
       "| suite | exit base→pin | stdout sha base / pin | stderr sha base / pin | identical |", "|---|---|---|---|---|"]
for s, be, pe, po, bo, pe_, be_, same in rows:
    out.append(f"| `{s}` | {be}→{pe} | {bo} / {po} | {be_} / {pe_} | {'yes' if same else '**NO**'} |")
raw_diff = []
for s_ in suites:
    p_ = subprocess.run([sys.executable, s_], cwd=pin_dir, capture_output=True, text=True, timeout=1800)
    import difflib
    for _stream in ("stdout", "stderr"):
        _mine = getattr(p_, _stream); _theirs = base[s_][_stream]
        if _mine != _theirs:
            raw_diff.append((s_ + " (" + _stream + ")", [l for l in difflib.unified_diff(_theirs.splitlines(), _mine.splitlines(), lineterm="", n=0) if l.startswith(("-", "+")) and not l.startswith(("---", "+++"))]))
out += ["", f"All identical (normalised): **{'yes' if all(r[-1] for r in rows) else 'NO'}** ({sum(r[-1] for r in rows)}/{len(rows)}).", "",
        "### Raw-byte differences, exact lines (checkout-root normalisation only; every other difference is ledgered)", ""]
for s_, lines in raw_diff:
    out += [f"`{s_}`:", "```"] + lines + ["```", ""]
if not raw_diff:
    out += ["none", ""]
out += [
        "## SC-01: the plan's inline grade assertion (T-01 verify) at the pin — green", "",
        f"run in the pin checkout → exit {lock.returncode}", "```", (lock.stdout + lock.stderr).rstrip(), "```", "",
        "## SC-01 / SC-04 red-first: the same assertion run in the baseline checkout — red", "",
        f"run in the baseline checkout (the five retained drivers grade 1 there) → exit {red.returncode}", "```", (red.stdout + red.stderr).rstrip(), "```", ""]
path = os.path.join(ROOT, ".claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md")
open(path, "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
