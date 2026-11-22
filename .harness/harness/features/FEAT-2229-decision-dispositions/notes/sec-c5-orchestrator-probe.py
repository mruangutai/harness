"""Orchestrator-run actual-CLI controls for SEC-C4-01 at pin c163d5ea (security c5's planned
probe set, executed by a shell-holding tier). Uses the pinned integration module's fixture
builders and run_check, which invokes the real plan-merge.py check.

    env -u HARNESS_AGENT_TYPE python3 sec-c5-orchestrator-probe.py \
        <checkout>/tests/integration/test-plan-decision-dispositions.py
"""
import importlib.util
import sys

TEST = sys.argv[1]
spec = importlib.util.spec_from_file_location("t", TEST)
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

SPOOF, REAL, row, plan_text, _docs = t.SPOOF, t.REAL_TEN, t.row, t.plan_text, t._docs
N = [0, 0]


def rec(name, ok, out):
    N[0 if ok else 1] += 1
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        print("     " + out.replace("\n", "\n     ")[:600])


def spoof_fails(name, docs):
    rc, out = t.run_check(plan_text([row(clause=SPOOF)]), setup=_docs(docs))
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    rec("spoof-fails  " + name, rc == 1 and any("decisions_affected[0] DEC-10" in l and "clause" in l
                                                 for l in fails), out)


def genuine_passes(name, docs):
    rc, out = t.run_check(plan_text([row(clause=REAL)]), setup=_docs(docs))
    rec("genuine-pass " + name, rc == 0, out)


def genuine_absent(name, docs):
    """No real DEC-10 heading at all: the genuine clause must fail too (no section)."""
    rc, out = t.run_check(plan_text([row(clause=REAL)]), setup=_docs(docs))
    rec("no-section   " + name, rc == 1, out)


def pair(name, spoof_heading, nl="\n"):
    docs = f"## {spoof_heading}{nl}{nl}{SPOOF}{nl}{nl}## DEC-10 — Ten{nl}{nl}{REAL}{nl}"
    spoof_fails(name, docs)
    genuine_passes(name, docs)
    genuine_absent(name + " (only the spoof heading present)",
                   f"## {spoof_heading}{nl}{nl}{SPOOF}{nl}{nl}{REAL}{nl}")


# 1. identifier continuations — never DEC-10. (`DEC-10-` and `DEC-10—x` are mislabelled here:
#    by DEC_ID_END a line-end hyphen and a joined em dash are delimiters, so both ARE DEC-10's
#    heading and print FAIL by design — see sec-c5-orchestrator-probe.md.)
for cont in ("DEC-100", "DEC-10x", "DEC-10X", "DEC-10é", "DEC-10_a", "DEC-10-1", "DEC-10.5",
             "DEC-10/x", "DEC-10a — title", "DEC-10-extra", "DEC-10_", "DEC-10-", "DEC-10—x",
             "DEC-10x:", "DEC-10x (x)"):
    pair(f"continuation {cont!r}", cont)

# 2. malformed heading formats — never a DEC-10 section
for bad in ("##DEC-10 — Ten", "####### DEC-10 — Ten", "    ## DEC-10 — Ten", "## -DEC-10",
            "## xDEC-10", "## dec-10 — Ten", "## DEC 10 — Ten", "## DEC-010 — Ten"):
    docs = f"{bad}\n\n{SPOOF}\n"
    rc, out = t.run_check(plan_text([row(clause=SPOOF)]), setup=_docs(docs))
    rec(f"malformed   {bad!r} is not a DEC-10 section (spoof fails)", rc == 1, out)

# 3. delimiters after the full identifier — all are DEC-10's heading
for real in ("DEC-10", "DEC-10 ", "DEC-10\t", "DEC-10  ", "DEC-10: Ten", "DEC-10:Ten",
             "DEC-10 (Ten)", "DEC-10(Ten)", "DEC-10 — Ten", "DEC-10—Ten", "DEC-10 – Ten",
             "DEC-10–Ten", "DEC-10 - Ten", "DEC-10\tTen", "DEC-10 -- Ten"):
    for lvl in ("##", "#", "###", "######"):
        for indent in ("", " ", "  ", "   "):
            genuine_passes(f"delimiter {indent + lvl + ' ' + real!r}",
                           f"{indent}{lvl} {real}\n\n{REAL}\n")
    genuine_passes(f"delimiter tab-after-hashes {('##\t' + real)!r}", f"##\t{real}\n\n{REAL}\n")

# 4. CRLF and trailing whitespace shapes
pair("CRLF line endings, spoof DEC-10x", "DEC-10x — not ten", nl="\r\n")
genuine_passes("CRLF bare `## DEC-10`", f"## DEC-10\r\n\r\n{REAL}\r\n")
genuine_passes("CRLF `## DEC-10 — Ten`", f"## DEC-10 — Ten\r\n\r\n{REAL}\r\n")
genuine_passes("trailing spaces `## DEC-10   `", f"## DEC-10   \n\n{REAL}\n")
genuine_passes("trailing tab `## DEC-10\\t`", f"## DEC-10\t\n\n{REAL}\n")
genuine_passes("closing hashes `## DEC-10 ##`", f"## DEC-10 ##\n\n{REAL}\n")

# 5. bounded neighbouring clauses: the spoof section's text never leaks into DEC-10's section
docs = (f"## DEC-10 — Ten\n\n{REAL}\n\n## DEC-10x — not ten\n\n{SPOOF}\n\n## DEC-11 — Eleven\n\n"
        "Only eleven says this.\n")
spoof_fails("neighbour: DEC-10x section after DEC-10 does not extend DEC-10", docs)
genuine_passes("neighbour: DEC-10 section before DEC-10x still resolves", docs)
docs = f"## DEC-10 — Ten\n\n{REAL}\n\n### DEC-10.5 sub\n\n{SPOOF}\n"
rc, out = t.run_check(plan_text([row(clause=SPOOF)]), setup=_docs(docs))
rec("neighbour: deeper `### DEC-10.5` stays inside DEC-10's section (spoof found, passes)", rc == 0, out)

# 6. fence controls — a spoof heading inside a fence never resolves
for opener, closer in (("```", "```"), ("~~~", "~~~"), ("~~~ a`b", "~~~")):
    docs = f"{opener}\n## DEC-10 — Ten\n{SPOOF}\n{closer}\n\n## DEC-10 — Ten\n\n{REAL}\n"
    spoof_fails(f"fence {opener!r}: fenced spoof heading is content", docs)
    genuine_passes(f"fence {opener!r}: genuine heading after the fence resolves", docs)

print(f"\n{N[0]} ok, {N[1]} FAIL, {N[0] + N[1]} observations")
sys.exit(1 if N[1] else 0)
