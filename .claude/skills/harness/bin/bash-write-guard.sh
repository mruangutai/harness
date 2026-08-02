#!/usr/bin/env bash
# PreToolUse Bash hook — close the CASUAL Bash write bypass (DEC-151).
#
# Field incident: qa, denied a source edit by check-domain, made the same edit
# via `perl -pi` from Bash — the domain hook only sees Write/Edit. This guard
# does not make Bash-write extraction "winnable" in general (DEC-85 stands);
# it parses the COMMON in-place editors and redirections, which is what an
# agent under pressure actually reaches for. Unparseable commands pass — the
# guard converts casual bypass into deliberate obfuscation, which the post-run
# tree audit then catches.
#
# Policy:
#   - reviewers (code/security/ui) — READ-ONLY: any detected write pattern is
#     denied outright, no path analysis. Their job is findings, never fixes.
#   - dev-ops — exempt (trusted by design, owns builds/deploy; DEC-85).
#   - every other harness agent — a detected write whose target path is
#     extractable and OUTSIDE the agent's domain (per team-config.yaml,
#     shared paths included) is denied; in-domain and unparseable pass.
#   - main session and non-harness agents — ungoverned, exit 0.
set -uo pipefail

payload=$(cat)

agent="$(printf '%s' "$payload" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("agent_type", "") or "")
except Exception:
    print("")
' 2>/dev/null)"
[ -n "$agent" ] || exit 0
case "$agent" in
  harness-dev-ops) exit 0 ;;
  harness-*) ;;
  *) exit 0 ;;
esac

_self="${BASH_SOURCE[0]:-$0}"
_selfdir="$(cd "$(dirname "$_self")" && pwd)"
_derived="$(cd "$_selfdir/../../../.." && pwd)"
root="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$root" ] || [ ! -r "$root/.harness/team-config.yaml" ]; then
  [ -r "$_derived/.harness/team-config.yaml" ] && root="$_derived" || root="${root:-$(pwd)}"
fi
manifest="$root/.harness/team-config.yaml"
[ -r "$manifest" ] || exit 0   # not onboarded — fail open like check-domain

HOOK_PAYLOAD="$payload" python3 - "$agent" "$manifest" "$root" <<'PY'
import sys, os, re, json, shlex

agent, manifest, root = sys.argv[1:4]
try:
    d = json.loads(os.environ.get("HOOK_PAYLOAD") or "")
except Exception:
    sys.exit(0)
cmd = ((d.get("tool_input") or {}).get("command") or "")
if not cmd:
    sys.exit(0)

REVIEWERS = {"harness-code-reviewer", "harness-security-reviewer", "harness-ui-reviewer"}

# --- detect write patterns and extract candidate target paths where parseable ---
findings = []   # (pattern-name, [paths])

# redirections:  > path   >> path   (not 2>/dev/null, >&2, >(...) etc.)
for m in re.finditer(r"(?<![0-9&<])>{1,2}\s*([^\s;&|)]+)", cmd):
    p = m.group(1)
    if p.startswith(("&", "(", "/dev/")):
        continue
    findings.append(("redirect", [p]))

def trailing_files(args, drop_first_script=False):
    out, skip, saw_expr = [], False, False
    for a in args:
        if skip:
            skip = False; saw_expr = True; continue
        if a in ("-e", "-E", "--expression", "-f", "--file"):
            skip = True; continue          # the next token is an expression/script, not a target
        if not a or a.startswith("-") or a in (";", "&&", "||"):
            continue                       # empty covers BSD `sed -i ''`
        out.append(a)
    if drop_first_script and not saw_expr and out:
        out = out[1:]                      # bare `sed -i 's/a/b/' file`: first arg is the script
    return out

try:
    tokens = shlex.split(cmd, posix=True)
except ValueError:
    tokens = cmd.split()

for i, t in enumerate(tokens):
    base = os.path.basename(t)
    rest = tokens[i + 1:]
    # stop this command's args at a separator
    args = []
    for a in rest:
        if a in (";", "&&", "||", "|"):
            break
        args.append(a)
    if base in ("sed", "perl") and any(a.startswith(("-i", "-pi", "-ni")) or a == "-p" and "-i" in args for a in args):
        findings.append((f"{base} in-place", trailing_files(args, drop_first_script=(base == "sed"))))
    elif base == "tee":
        findings.append(("tee", [a for a in trailing_files(args) if a != "-"]))
    elif base in ("mv", "cp") and len(trailing_files(args)) >= 2:
        findings.append((base, trailing_files(args)[-1:]))
    elif base == "rm":
        findings.append(("rm", trailing_files(args)))
    elif base == "sponge":
        findings.append(("sponge", trailing_files(args)))
    elif base == "awk" and any(a == "-i" or a.startswith("inplace") for a in args):
        findings.append(("awk inplace", trailing_files(args)))

if not findings:
    sys.exit(0)

def deny(reason):
    print(f"bash-write-guard: BLOCKED — {reason}", file=sys.stderr)
    print("  File changes go through the Write tool, where your domain is enforced. "
          "A path the domain hook denied does not become writable by switching tools — "
          "that is guardrail evasion (DEC-151). If the file should be yours, raise it "
          "as an open_question.", file=sys.stderr)
    sys.exit(2)

if agent in REVIEWERS:
    pats = ", ".join(sorted({f[0] for f in findings}))
    deny(f"{agent} is READ-ONLY and this command writes files ({pats}). "
         f"Report the finding; never fix.")

# --- non-reviewers: check extractable paths against the agent's domain ---
lines = open(manifest, encoding="utf-8").read().splitlines()
mine, shared, cur = [], [], None
for ln in lines:
    s = ln.strip()
    m = re.match(r"^-?\s*(?:name|- name):\s*(\S+)", s)
    if m:
        cur = m.group(1).strip("\"'"); continue
    if s.startswith("shared:"):
        cur = "__shared__"; continue
    pm = re.search(r"path:\s*([^,}\s]+)", s)
    if pm:
        p = pm.group(1).strip("\"'")
        if cur == agent and "read: true" not in s:
            mine.append(p)
        elif cur == "__shared__":
            shared.append(p)

def glob_to_re(pat):
    out, i = [], 0
    while i < len(pat):
        if pat.startswith("**", i):
            out.append(".*"); i += 2
            if pat.startswith("/", i):
                out.append("/?"); i += 1
        elif pat[i] == "*":
            out.append("[^/]*"); i += 1
        elif pat[i] == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(pat[i])); i += 1
    return re.compile("^" + "".join(out) + "$")

def matches(path, pat):
    pat = pat.rstrip("/")
    if pat in (".", ""):
        return False
    if pat.endswith("/**"):
        base = pat[:-3]
        return bool(glob_to_re(base).match(path) or glob_to_re(base + "/**").match(path))
    return bool(glob_to_re(pat).match(path) or glob_to_re(pat + "/**").match(path))

allowed = mine + shared
for name, paths in findings:
    for p in paths:
        ap = os.path.abspath(os.path.join(root, p)) if not os.path.isabs(p) else p
        rel = os.path.relpath(ap, os.path.abspath(root))
        # Worktree carve-out (DEC-153): disposable checkouts are where sanctioned
        # perturbation proofs live — qa mutates source there to prove a test
        # discriminates. The MAIN checkout stays hard-protected. Reviewers never
        # reach this branch (denied on any write pattern above).
        if re.match(r"^\.claude/worktrees/", rel):
            continue
        cands = [rel]
        if rel.startswith(".."):
            continue  # outside repo — not this hook's problem
        # tmp/cache noise is not a domain question
        # NB: no `^/` alternative -- relpath means an out-of-repo absolute target
        # already hit the `..` continue above, so it was dead (review of PR #4).
        if re.match(r"^(\.pytest_cache|node_modules|__pycache__|\.venv)", rel):
            continue
        if not any(matches(r, g) for r in cands for g in allowed):
            deny(f"{agent}: `{name}` targets {rel}, outside your domain.")

sys.exit(0)
PY
