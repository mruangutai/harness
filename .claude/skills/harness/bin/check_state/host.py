"""The OMP port and the skill tree resolve: INV-19/42/45/48. (FEAT-69)"""
import os, sys
import harness_boundary
# --- INV-9 retired under DEC-233; the number is never reused (DEC-205). Host enforcement is
# `.omp/extensions/harness-hooks.ts`, and its wiring is graded by check-omp-port.py — INV-45
# since the 2026-09-21 ruling (the row ran unnumbered as `OMP-PORT` before it). The
# gate keys on `.omp/config.yml` so a scratch tree that carries no OMP surface (every
# fixture in tests/) grades its own invariants without the whole port surface.
def _omp_port_findings(ctx, omp_check):
    """check-omp-port.py's stderr lines when it fails; nothing when it passes or could not run."""
    _omp_result = ctx.spawn(
        [sys.executable, omp_check, ctx.root],
        text=True,
        capture_output=True,
    )
    if _omp_result is None or _omp_result.returncode == 0:
        return []
    return [_line.strip() for _line in (_omp_result.stderr or "").splitlines() if _line.strip()]

def inv_45(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    _omp_cfg = os.path.join(root, ".omp", "config.yml")
    if os.path.isfile(_omp_cfg):
        _omp_check = os.path.join(root, ".agents", "skills", "harness", "bin", "check-omp-port.py")
        if not os.path.isfile(_omp_check):
            bad.append("OMP is configured but check-omp-port.py is missing — nothing grades the "
                       "roster, hook wiring or provider overlays.")
        else:
            bad.extend(_omp_port_findings(ctx, _omp_check))
    return bad, warn

# --- INV-19 (DEC-162): no glossary means the domain's ubiquitous language lives
# nowhere — "create lazily" fired zero times across three shipped features while
# enums and status vocabularies were being pinned. Warn-level: flows still run, but
# pm's next plan pass owes the file. The map precondition went with the map tier.
def inv_19(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    if not os.path.isfile(os.path.join(H, "glossary.md")):
        warn.append("no .harness/glossary.md — the domain's ubiquitous language is unrecorded "
                    "(DEC-162). pm authors it, seeded from shipped features' pinned vocabulary.")
    return bad, warn

# --- INV-42 (FEAT-60 SC-08, DEC-174 direct work): preload weight. Every autoloadSkills
# entry is text paid on every spawn; check_skill_weight measures it per agent and for the
# universal set and compares against budgets.preload_warn_words. An excess is a NOTE and
# never a violation — weight is a cost the operator trades off, not a defect. What IS a
# violation is the module's own error list: a preload that resolves to nothing (the agent
# spawns without a rule it was declared to carry) or a references/ file named as a preload
# (SC-11). The import posture is INV-27's: the module ships with the tree.
def inv_42(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    try:
        # register=True: dataclasses resolve the module by name during exec (FEAT-61 T-03 —
        # the registration, and its removal after a failed exec, live in load_repo_module).
        _csw = harness_boundary.load_repo_module(
            "check_skill_weight", os.path.join(sys.argv[2], "check-skill-weight.py"),
            register=True)
    except harness_boundary.RepoModuleError as _cswe:
        _cswe = _cswe.cause      # render what failed inside check-skill-weight.py, not the wrapper
        _csw = None
        bad.append("INV-42 CANNOT RUN: check-skill-weight.py did not import (%s: %s), so an "
                   "agent preloading a missing skill would go unreported. The module ships with "
                   "this repository — restore .claude/skills/harness/bin/check-skill-weight.py."
                   % (type(_cswe).__name__, _cswe))
    if _csw is not None:
        try:
            _wres = harness_boundary.call_repo_module(_csw, "scan", root)
        except harness_boundary.RepoModuleError as _wse:
            _wres, _wse = None, _wse.cause
            bad.append("INV-42 CANNOT RUN: the preload scan raised (%s: %s)."
                       % (type(_wse).__name__, _wse))
        if _wres is not None:
            bad.extend(f"INV-42 {_e}." for _e in _wres.errors)
            warn.extend(f"INV-42 {_n}. Cut per DEC-158 (rule, one clause, pointer) or raise "
                        f"budgets.preload_warn_words in .harness/harness.json." for _n in _wres.notes())
    return bad, warn

# --- INV-48: every reference a skill makes resolves. A skill citing a deleted DEC, an
# unimplemented INV, a missing path, a heading a sibling no longer has, or a skill/agent
# name that does not exist is a rule the reading agent cannot follow and no validator
# catches (a deleted decision and a never-implemented invariant were each cited for weeks, DEC-235). A finding
# IS a violation: unlike weight it is a defect, not a cost. Import posture as INV-42.
# (Written as INV-45 on skills/optimization-pass; renumbered at the 2026-09-22 rebase because
# the 2026-09-21 ruling gave INV-45 to the OMP port row. The import and call are typed per
# FEAT-63: RepoModuleError at the boundary, CANNOT RUN here.)
def inv_48(ctx):
    bad, warn = [], []
    root = ctx.root
    try:
        _csr = harness_boundary.load_repo_module(
            "check_skill_refs", os.path.join(sys.argv[2], "check-skill-refs.py"), register=True)
    except harness_boundary.RepoModuleError as _csre:
        _csr, _csre = None, _csre.cause
        bad.append("INV-48 CANNOT RUN: check-skill-refs.py did not import (%s: %s). The module "
                   "ships with this repository — restore .claude/skills/harness/bin/check-skill-refs.py."
                   % (type(_csre).__name__, _csre))
    if _csr is not None:
        try:
            bad.extend(f"INV-48 {_f}" for _f in harness_boundary.call_repo_module(_csr, "scan", root))
        except harness_boundary.RepoModuleError as _srse:
            _srse = _srse.cause
            bad.append("INV-48 CANNOT RUN: the reference scan raised (%s: %s)."
                       % (type(_srse).__name__, _srse))
    return bad, warn
