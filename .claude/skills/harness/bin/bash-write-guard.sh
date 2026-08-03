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

def mask_quoted(text):
    """Blank the CONTENTS of quoted spans, preserving length and the quotes.

    The redirect scan below is a regex over the raw command, so a `>` inside a
    quoted string was read as an operator. That blocked the MANDATED
    `Co-Authored-By: … <noreply@anthropic.com>` trailer on every agent commit, an
    arrow in a printed string, and an HTML comment in prose (Task #5).

    Masking rather than deleting keeps offsets and lengths intact, so a QUOTED
    redirect target still yields a capturable token: `> "src/x.py"` becomes
    `> "xxxxxxxxx"`, which still finds the redirect and still blocks. The guard
    fails safe — a masked span can only hide `>` characters that bash itself
    would treat as literal text, never an operator.
    """
    out, q = [], None
    for ch in text:
        if q:
            if ch == q:
                q = None; out.append(ch)
            else:
                out.append("x")
            continue
        if ch in "\"'":
            q = ch
        out.append(ch)
    return "".join(out)

SHELL_FEEDERS = {"bash", "sh", "zsh", "dash", "ksh"}


def strip_heredoc_bodies(text):
    """Drop heredoc BODIES, keeping the command line that opens them.

    A heredoc body is DATA, not shell syntax: `python3 - <<PY ... if a > b: ... PY`
    feeds a script to an interpreter, and reading that `>` as a redirect refused every
    inline script this repo runs (B-6). The `<<TAG` line itself is kept, so a real
    redirect on it — `cat <<EOF > src/main.py` — is still scanned and still blocks.

    EXCEPTION, and it is the whole reason this is safe: when the heredoc feeds a SHELL
    (`bash <<EOF`), the body IS code and its redirects are real. Those bodies are kept.
    An unrecognised feeder is treated as a shell too — the guard fails toward scanning.
    """
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        # Only an UNQUOTED << opens a heredoc; mask first so `echo "a <<b"` does not.
        m = re.search(r"<<-?\s*([\"']?)([A-Za-z_][A-Za-z0-9_]*)\1", mask_quoted(line))
        i += 1
        if not m:
            continue
        tag, dash = m.group(2), "<<-" in line
        try:
            words = [os.path.basename(w) for w in shlex.split(line)]
        except ValueError:
            # An unbalanced quote must not raise: this is a PreToolUse hook, and only
            # exit 2 blocks (DEC-100), so an uncaught exception fails OPEN. Keep the body.
            words = []
            keep_body = True
        else:
            # A shell ANYWHERE in the pipeline means the body is code, not data:
            # `cat <<EOF | bash` routes it to a shell just as surely as `bash <<EOF`,
            # and looking only at the first word let that shape through (a fail-open
            # this function introduced and this line closes).
            keep_body = (any(w in SHELL_FEEDERS for w in words)
                         or not words
                         or words[0] not in KNOWN_DATA_FEEDERS)
        while i < len(lines):
            body = lines[i]
            i += 1
            if (body.strip() if dash else body) == tag:
                out.append(body)
                break
            if keep_body:
                out.append(body)
    return "\n".join(out)


# Feeders whose heredoc body is inert DATA. Anything not listed keeps its body scanned,
# so a novel or obfuscated feeder cannot smuggle a redirect past the guard.
KNOWN_DATA_FEEDERS = {"cat", "python", "python3", "git", "tee", "jq", "sed", "awk",
                      "grep", "node", "ruby", "perl", "psql", "sqlite3", "mail", "ssh"}


def segments(text):
    """Split a compound command into its parts at UNQUOTED shell separators.

    `shlex.split` leaves `;` attached to the preceding token ('docs/a.md;'), so the
    guard's `if a in (";", "&&", ...)` break never fired and the NEXT command's name was
    collected as an operand — `rm -f docs/a.md; echo ok` was refused for "rm targets
    echo" (B-6). Splitting first makes each command's operand list actually end.
    """
    parts, cur, q, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if q:
            cur.append(ch)
            if ch == q:
                q = None
            i += 1
            continue
        if ch in "\"'":
            q = ch; cur.append(ch); i += 1; continue
        two = text[i:i + 2]
        if two in ("&&", "||"):
            parts.append("".join(cur)); cur = []; i += 2; continue
        if ch in ";\n|&":
            parts.append("".join(cur)); cur = []; i += 1; continue
        cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return [p for p in (s.strip() for s in parts) if p]


scan_text = strip_heredoc_bodies(cmd)
SEGMENTS = segments(scan_text)

# redirections:  > path   >> path   (not 2>/dev/null, >&2, >(...) etc.)
# Scanned over the MASKED text so quoted text cannot pose as an operator.
for _seg in SEGMENTS:
    for m in re.finditer(r"(?<![0-9&<])>{1,2}\s*([^\s;&|)]+)", mask_quoted(_seg)):
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

tokens = []
for _seg in SEGMENTS:
    try:
        tokens.append(shlex.split(_seg, posix=True))
    except ValueError:
        tokens.append(_seg.split())

# Each segment is one command, so its operand list ends at the segment boundary — no
# in-list separator hunting, which is what silently failed before (B-6).
for seg_tokens in tokens:
    for i, t in enumerate(seg_tokens):
        base = os.path.basename(t)
        args = seg_tokens[i + 1:]
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
