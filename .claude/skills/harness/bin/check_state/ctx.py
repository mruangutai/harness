"""The parse-once runner context and the primitives every family shares. (FEAT-69)"""
import glob, os, re, subprocess, sys
import artifact_accessors
import digest_record
import harness_boundary
import harness_yaml
def read(p):
    """The file's text, or None when it is absent, unreadable or not UTF-8."""
    try:
        return open(p, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return None

# THE STATION VOCABULARY IS DERIVED, NEVER SPELLED (FEAT-41 T-01/T-07). Both names below come
# from factory_config so this script cannot drift from harness.json's declaration — the drift
# that made a six-key mapping and a validator disagree, which is why FEAT-41 exists. The
# finished bucket is the table's own (FEAT-61 T-03), no longer a `("done",) +` concatenation
# this script spelled for itself.
import factory_config

TERMINAL_STATIONS = factory_config.TERMINAL_STATIONS
FINISHED_STATIONS = factory_config.FINISHED_STATIONS

# THE FEATURE'S STATION, READ FROM THE ONE FILE THAT RECORDS IT (FEAT-41 T-07). Every site
# below that used to read feature.json's `status` now calls this, so the vocabulary and the
# file live in exactly one place in this script instead of six.
#
# `station_of` takes the feature DIRECTORY, not a file, because every caller already holds one
# and the two callers that iterate feature.json globs still need that document for its OTHER
# keys (INV-28's `pr`, INV-6's shape). Splitting the station read from the document read is
# what lets those sites keep one open() each rather than gaining a second.
#
# RETURNS "" FOR EVERY UNKNOWABLE CASE — no plan, unparseable plan, no station, a station that
# is not a string. "" is the same value the old code produced from an absent feature.json
# status, so each caller's existing posture carries over unchanged rather than being redesigned
# alongside the migration.
def station_of(plan_doc):
    """The plan's station from its already-parsed document (FEAT-63: `Ctx.plan_docs`, which
    `_load_plan_docs` fills once and whose parse failure it reports once); "" for every
    unknowable case — no plan, an unparseable plan, no station, a station that is not a string."""
    if not isinstance(plan_doc, dict):
        return ""
    # `status: done  # with a trailing comment` is a shape the live corpus carries, so take the
    # first whitespace-delimited token — the same normalisation the feature.json reads used.
    token = str(plan_doc.get("status", "")).split()
    return token[0] if token else ""

def approved(txt):
    if not txt: return False
    m = re.search(r"^##\s+Approval\s*$(.*?)(?=^##\s|\Z)", txt, re.M | re.S)
    return bool(m) and re.search(r"status:\s*approved", m.group(1), re.I) is not None

def has_approval_block(txt):
    return bool(txt) and re.search(r"^##\s+Approval\s*$", txt, re.M) is not None

_MISSING = object()

# THE STEMS ARE LOWERCASE LITERALS AND ARE DELIBERATELY NOT DERIVED FROM THE STATION NAMES.
# The next editor's first instinct is to build the filename from the station; do not. The stems
# are seam names — plan, build, validate — and the stations are positions. They now happen to
# share a case, which is exactly what makes deriving look safe and still be wrong: `ready` and
# `building` both require notes/handoff-plan.md, and no station is named `validate` at all.
# Keeping the stems as their own literals also renames no file on disk.
#
# THE RESIDUAL LOSS, RECORDED RATHER THAN HIDDEN: validate and ship both folded into
# review, so the validate-to-ship crossing is no longer separately observable and
# handoff-validate.md cannot be demanded at review. It is demanded at done instead — the
# next boundary that proves review completed. One seam moves later; none is dropped.
#
# A STATION OUTSIDE STATUS_ORDER IS NOW A VIOLATION, NOT A SILENT SKIP (FEAT-41 T-07, A-03).
# It was a deliberate silent skip on the grounds that status was schema-required with a closed
# enum, so an unknown value was already denied at write time and a branch here would have been
# a second enforcement point for a rule the schema owned. THAT COMPENSATING CONTROL IS GONE:
# T-07 deleted the key from feature-schema.json, and the station now lives in plan.yaml, whose
# schema does not constrain the top-level `status` value at all. What denies an illegal station
# today is plan-merge.py's set-feature-station, which validates before it opens the file — an
# enforcement point on the WRITE ROUTE, not on the document. A hand-edited plan therefore
# reaches this loop with a station nothing has checked, and the old skip would have taken every
# such feature out of INV-17 without a word. It is reported instead.
#
# Despite the name, STATUS_ORDER is used as a SET — the membership test below is its only
# reader and nothing indexes it. So the marker sitting at the end implies no progression.
#
# STATUS_ORDER AND SEAM_NOTES ARE ONE VOCABULARY AND MOVE TOGETHER. SEAM_NOTES is indexed by a
# BARE SUBSCRIPT below, guarded only by that membership test, so rekeying one without the other
# does not degrade to a skip — it is a KeyError in the project's own state gate, for every
# well-formed feature on disk. Derived from factory_config rather than spelled, which makes the
# pairing structural: both are built from MANDATED_STATIONS, so neither can be rekeyed alone.
STATUS_ORDER = list(factory_config.MANDATED_STATIONS) + list(TERMINAL_STATIONS)
SEAM_NOTES = {
    "backlog":  [],
    "plan":     [],
    "ready":    ["plan"],
    "building": ["plan"],
    "review":   ["plan", "build"],
    "done":     ["plan", "build", "validate"],
    # THE TERMINAL STATIONS REQUIRE NO HANDOFF, and that is the whole difference from done. A
    # feature planned and never built (abandoned) or refused at intake (rejected, FEAT-1714)
    # crossed no seam, so there is no honest handoff note to write and none will be fabricated.
    # Keyed EXPLICITLY rather than omitted: an omitted key is now a KeyError rather than a
    # silent skip, since the station passes the membership test above by construction.
    **{station: [] for station in TERMINAL_STATIONS},
}
# EVERY STATION IN THE VOCABULARY HAS A SEAM ROW, asserted here rather than trusted. The two
# structures are derived from the same source, so the only way they can disagree is a hand-typed
# SEAM_NOTES key — and this is the check that catches it at startup instead of at the subscript,
# on whichever feature happens to sit at that station.

def _int_field(v):
    """int, or None. bool is rejected BEFORE the int check (INV-22's lesson: bool subclasses
    int, so `true` read as a budget of 1)."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str) and v.strip().isdigit():
        return int(v.strip())
    return None


def _iso_instant(v):
    """An aware datetime, or None. Accepts the two spellings the ledger writes — feature-record
    writes `+00:00`, older fixtures and gh write `Z` — and refuses a naive value rather than
    guessing its zone, since INV-43 compares instants across two writers."""
    if not isinstance(v, str) or not v.strip():
        return None
    from datetime import datetime
    try:
        parsed = datetime.fromisoformat(v.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


# =====================================================================================
# THE RUNNER CONTEXT (FEAT-62). Every shared source is parsed ONCE here and handed to the
# invariant functions; no invariant re-reads what the context already holds. Findings the
# loading itself produces (a plan that does not load, a harness.json that is not JSON, an
# era boundary that cannot be resolved) are the context's own and print FIRST -- before the
# baseline they printed at the position of the block that first needed the source, which
# is the same position for the common case and earlier for the rare ones; the ledger rules
# that ordering change (notes/build-divergences.md).
# =====================================================================================
class Ctx:
    """The parsed corpus one run of the checker judges.

    `features` is the ORDERED list of feature directory names the runner iterates -- sorted,
    where the baseline followed filesystem order (ruled; see the ledger) -- and `--feature`
    narrows it, so a repo-scoped invariant that loops `ctx.features` itself is narrowed too.
    """

    def _load_features(self, keep):
        # D-08 (FEAT-21 T-05), the OTHER half of the signed trade: dict KEYS stay bare basenames
        # (qualify one of the two name-derivation shapes and not the other and the station mirror
        # silently skips every feature), but a finding that names a PATH carries the DISCOVERED
        # segment-qualified path, so a reader can open exactly what the label names.
        H, root = self.H, self.root
        # corpus-scope: checkout-local
        self.feat_dirs = {os.path.basename(_d): os.path.relpath(_d, root)
                          for _d in glob.glob(os.path.join(H, "*", "features", "*"))
                          if os.path.isdir(_d)}
        self.features = sorted(self.feat_dirs)
        if keep is not None:
            self.features = [f for f in self.features if f in keep]

    def _selected(self, tail):
        """`{feature: path}` of `tail` inside each SELECTED feature directory that has it.
        The per-feature loads below read the audit's subject and nothing else (FEAT-1559): a
        narrowed or sparse run never opens another feature's BRIEF, plan or STATE.md."""
        out = {}
        for feat in self.features:
            path = os.path.join(self.root, self.feat_dirs[feat], tail)
            if os.path.isfile(path):
                out[feat] = path
        return out

    def _load_plans(self):
        # BRIEF/PLAN are PER-FEATURE since DEC-129 — .harness/<repo>/features/<FEAT>/{BRIEF,PLAN}.md.
        # Root-level singletons collided the moment a second feature existed.
        self.briefs = {f: read(p) for f, p in self._selected("BRIEF.md").items()}
        self.plans = {f: read(p) for f, p in self._selected("PLAN.md").items()}

    def _load_plan_docs(self):
        # plan.yaml (DEC-182) is loaded, never read as text. Kept in a SEPARATE dict rather than
        # merged into `plans`: every check below either reads markdown or reads a mapping, and one
        # dict holding both shapes is how a regex ends up running over a dict repr. A feature with
        # both files is refused by check-plan-routes; here the yaml simply wins, because a feature
        # mid-migration should be judged by the artifact its author is maintaining.
        bad = self.bad
        self.plan_docs = {}
        for _feat, _p in self._selected("plan.yaml").items():
            try:
                self.plan_docs[_feat] = artifact_accessors.load_plan(_p)
                self.plans.pop(_feat, None)
            except harness_yaml.YamlParseError as _e:
                # A plan that does not load is a VIOLATION, never a silent skip — the whole point
                # of DEC-182 is that a malformed plan stops being something a regex half-reads.
                bad.append(f"{self.fpath(_feat, 'plan.yaml')} does not load, so INV-3/4/5 cannot be checked "
                           f"for it: {_e}")

    def _load_states_and_abandoned(self):
        H, bad = self.H, self.bad
        # STATE.md is per-feature since DEC-120; read the selected ones.
        self.states = {f: read(p) for f, p in self._selected("STATE.md").items()}

        # Onboarding itself is signalled by harness.json + team-config.yaml (DEC-129), not a BRIEF:
        # a freshly-onboarded project legitimately has zero features yet.
        if not os.path.isfile(os.path.join(H, "harness.json")):
            bad.append(".harness/harness.json missing — not onboarded (or half-onboarded). Run /harness-init, in this clone.")
        # AN ABANDONED FEATURE'S BRIEF IS NEVER APPROVED, and that is the point rather than a
        # defect: it was planned and retired without being signed. Halting /harness entry over an
        # unapproved brief on a feature nobody will build trains the operator to ignore the gate,
        # which is the failure a gate exists to prevent. Read from plan.yaml's station (FEAT-41 T-07),
        # never inferred — and the try/except that guarded the old json.load is gone with it, because
        # `station_of` already returns "" for every unreadable and unparseable shape.
        self.abandoned = {f for f in self.features if self.station(f) in TERMINAL_STATIONS}

    def _load_eras(self):
        # INV-32 / INV-43 era boundaries, resolved ONCE (BUG-1071; see _era_start_for).
        self.era_start = self._era_start_for("INV-32", "panel_era_start", "adversarial panel")
        # INV-43 (BUG-1723) has the same shape of boundary for the same reason: a succession recorded
        # before the seam was graded cannot be re-recorded to satisfy it (history stays as recorded,
        # DEC-227), and an invariant that reddens the whole corpus trains its reader to ignore it.
        self.seam_era_start = self._era_start_for("INV-43", "seam_era_start", "graded seam")

    def _load_git_top(self):
        # THE GIT TOP LEVEL, resolved ONCE for INV-33 below (FEAT-41 T-14 / issue #867).
        #
        # RELATIVE TO THE GIT TOP LEVEL, NEVER TO `root`, and the reason CHANGED with the rebase while
        # the requirement did not. `root` is no longer CLAUDE_PROJECT_DIR: since FEAT-42 T-12 this script
        # resolves it through harness_boundary.resolve_root(_selfdir). That is the HARNESS root, which
        # still need not be the repository top level — a worktree checkout is the everyday case, and this
        # very file is being edited in one. `git show <sha>:<path>` takes a path relative to the
        # repository, so using `root` would silently miss every plan in a worktree.
        #
        # ONE subprocess for the whole run, not one per feature. None on failure, which is one of
        # INV-33's five deliberate silences: no git work tree is a state it cannot speak to.
        _tl = self.spawn(["git", "-C", self.root, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
        self.git_top = _tl.stdout.strip() if _tl is not None and _tl.returncode == 0 else None

    def spawn(self, argv, **options):
        """THE checker's one process boundary (FEAT-63 T-01, D-01): `subprocess.run(argv,
        **options)`, or None when the process could not be run at all -- OSError (the binary is
        absent, the cwd is gone) or subprocess.SubprocessError (the timeout a caller passes
        expired). Every call site keeps its own argv, cwd, text mode, capture and timeout; only
        the "could not run" decision lives here, once.
        gh absent or unauthenticated is an environmental precondition (DEC-138's verbatim
        clause), so it records nothing. Same posture as INV-25's git-absent branch."""
        try:
            return subprocess.run(argv, **options)
        except (OSError, subprocess.SubprocessError) as error:
            # Kept for the one caller that renders WHY it could not run (INV-31's CANNOT RUN).
            self.spawn_error = error
            return None

    def gh_ok(self, gh_bin):
        """Whether `gh auth status` succeeds, probed ONCE per binary and shared by INV-26 and
        INV-30 (each used to spawn its own probe)."""
        if gh_bin not in self._gh_ok:
            _auth = self.spawn([gh_bin, "auth", "status"], capture_output=True, text=True, timeout=15)
            self._gh_ok[gh_bin] = _auth is not None and _auth.returncode == 0
        return self._gh_ok[gh_bin]

    def station(self, feat):
        """The feature's plan.yaml station, from the document `_load_plan_docs` parsed once."""
        return station_of(self.plan_docs.get(feat))

    def _load_config(self):
        # `cj` is the parsed harness.json, consumed below by the test_kinds, github.sync and
        # gh-config checks. The JSON-validity violation is kept on its own merit — a config
        # that does not parse silently disables every check that reads it.
        # BOUND UNCONDITIONALLY. `cj` used to be assigned only inside the `if cfg:` below, so a
        # project with NO harness.json reached the consumers further down with the name unbound and
        # died with `NameError: name 'cj' is not defined`. That is a CRASH, and a crash exits 1 —
        # the same code a real violation exits — so /harness entry reported "violations found" for
        # an absent config file, with a traceback where a diagnosis should be.
        #
        # Pre-existing and reproduced on main at the same fixture before being fixed here; found
        # while landing DEC-182 because a plan.yaml fixture legitimately carries no harness.json.
        # Fixed in passing rather than left in a file this change already opens: check-state.py is
        # a DEC-174 carve-out, so the next person to touch it pays the full carve-out cost, and
        # leaving a known landmine for them is worse than a two-line diff here. The absent-config
        # case is already reported by the INV-1 check above; this only stops the crash.
        H, bad = self.H, self.bad
        cj = self.cj = {}
        cfg = read(os.path.join(H, "harness.json"))
        # `cj_valid` is False only when harness.json EXISTS and does not parse: the one finding
        # below covers that, and every other reader of the config (the era boundaries, INV-22's
        # budget, INV-37's sync flag) reads `cj` and stays quiet about it (FEAT-63 T-01).
        self.cj_valid = bool(cfg)
        if cfg:
            try:
                cj = self.cj = artifact_accessors.load_harness_json(
                    text=cfg, context=os.path.join(H, "harness.json"))
            except artifact_accessors.ArtifactAccessError as e:
                cj = self.cj = {}
                self.cj_valid = False
                bad.append(f".harness/harness.json is not valid JSON: {e}")

    def _load_handoff_baseline(self):
        cj, root = self.cj, self.root
        self.handoff_baseline = set()
        for _entry in cj.get("handoff_done_when_baseline", []) if isinstance(cj, dict) else []:
            if not isinstance(_entry, str):
                continue
            _path = os.path.relpath(_entry, root) if os.path.isabs(_entry) else _entry
            self.handoff_baseline.add(os.path.normpath(_path).replace(os.sep, "/"))

    def _assert_seam_rows(self):
        # EVERY STATION IN THE VOCABULARY HAS A SEAM ROW, asserted here rather than trusted. The two
        # structures are derived from the same source, so the only way they can disagree is a hand-typed
        # SEAM_NOTES key — and this is the check that catches it at startup instead of at the subscript,
        # on whichever feature happens to sit at that station.
        bad = self.bad
        _missing_seam_rows = [_s for _s in STATUS_ORDER if _s not in SEAM_NOTES]
        if _missing_seam_rows:
            bad.append("check-state.py: SEAM_NOTES has no row for station(s) %s — the seam table and "
                       "the station vocabulary have drifted, and INV-17 would raise KeyError on the "
                       "first feature at one of them." % ", ".join(_missing_seam_rows))

    def _load_hash_module(self):
        bad = self.bad
        try:
            _pm40 = harness_boundary.load_repo_module(
                "harness_plan_merge", os.path.join(sys.argv[2], "plan-merge.py"))
            self.signed_task_hash = _pm40.signed_task_hash
        except harness_boundary.RepoModuleError as _pme40:
            self.signed_task_hash = None
            # The ORIGINAL exception is rendered, not the boundary's wrapper: the reader wants
            # the type and text of what went wrong inside plan-merge.py (FEAT-63 T-01).
            bad.append("INV-40 CANNOT RUN its signed-text check: plan-merge.py did not import "
                       f"({type(_pme40.cause).__name__}: {_pme40.cause}), so an unledgered task-text change would go "
                       "unreported. The module ships with this repository.")

    def __init__(self, root, keep=None, scoped=False, owner=None):
        self.root = root
        self.H = os.path.join(root, ".harness")
        self.bad, self.warn = [], []
        # FEAT-1559: `scoped` is a sparse record-bearing worktree auditing its one active
        # feature; `owner` is its main checkout, where every landed record lives.
        self.scoped, self.owner = scoped, owner
        self._population = None
        self._load_features(keep)
        self._load_plans()
        self._load_plan_docs()
        self._load_states_and_abandoned()
        self._load_git_top()
        self._load_config()
        self._load_eras()
        self._load_handoff_baseline()
        self._assert_seam_rows()
        self.default_cycles = (_int_field((self.cj.get("budgets") or {}).get("max_total_cycles"))
                               if isinstance(self.cj, dict) else None)
        self._load_hash_module()

        # Per-feature caches filled on first use: the feature.json record (INV-6 family, INV-15's
        # verdict cross-check) and the run checkpoints (INV-16/36/15).
        self._records = {}
        self._run_states = {}
        self._gh_ok = {}
        self.spawn_error = None
        self._record_errors = {}
        self._digests = {}

    def population(self):
        """`[(feature, feature.json mapping or None)]` for a REPO-WIDE record predicate.

        Unscoped (a plain clone, or any run outside a sparse worktree): the selected features,
        exactly as before — `--feature` narrows it, as the table's scope rule says. Scoped: every
        LANDED record from the main corpus, with this checkout's own active record in place of
        its landed copy, so a predicate across features still sees all of them. In-progress
        siblings are never read (operator ruling, 2026-10-04). A main corpus that cannot be read
        raises feature_corpus.CorpusError; the caller reports it."""
        if not self.scoped:
            return [(f, self.record(f)[0]) for f in self.features]
        if self._population is None:
            import feature_corpus
            local = {f: self.record(f)[0] for f in self.features}
            landed = [(e["id"], e["document"]) for e in feature_corpus.records(self.owner)
                      if e["id"] not in local]
            self._population = sorted(landed + list(local.items()), key=lambda p: p[0])
        return self._population

    def fpath(self, feat, tail=""):
        _b = self.feat_dirs.get(feat) or os.path.join(".harness", "?", "features", feat)
        return _b + (os.sep + tail if tail else "")

    def feature_dir(self, feat):
        return os.path.join(self.root, self.feat_dirs[feat]) if feat in self.feat_dirs \
            else os.path.join(self.H, "?", "features", feat)

    def path(self, feat, tail):
        return os.path.join(self.feature_dir(feat), tail)

    def _era_start_for(self, inv, key, what):
        """The YYYY-MM-DD boundary before which `inv` grades nothing, or None: no config at all
        (INV-1 reports that; grade everything, the fail-CLOSED direction), null (this project has
        no pre-`what` era — the template default), or an unreadable value (reported, exempts
        nothing). A config that predates the key is a VIOLATION, not a silent default: defaulting
        to "grade everything" reddens every pre-era record in an un-upgraded project, and
        defaulting to "exempt everything" disables the invariant there without saying so; so it
        says so, once, and names the command that fixes it."""
        if not self.cj_valid:
            # The JSON-validity violation is raised on its own merit further down (`cj`).
            # (FEAT-63: `cj` is now loaded BEFORE the eras, so "further down" reads as
            # "in _load_config"; an absent config is INV-1's finding. Neither resolves an era.)
            return None
        raw = self.cj.get(key, _MISSING)
        if raw is _MISSING:
            self.bad.append(f"{inv}: .harness/harness.json has no `{key}`, so no {what} era can be "
                       f"resolved. Run /harness-init --upgrade (upgrade-config.py) against this "
                       f"clone's own harness.json, then set it to the date the {what} became available "
                       f"here, or null if this project never predated it.")
            return None
        if raw is None:
            return None
        if isinstance(raw, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", raw.strip()):
            return raw.strip()
        self.bad.append(f"{inv}: .harness/harness.json `{key}` is {raw!r}, which is neither null nor a "
                   f"YYYY-MM-DD date. Nothing is exempted while it is unreadable.")
        return None

    def _record_doc(self, feat, fy):
        """The parsed feature.json document, or None and the INV-6 finding that explains why:
        (doc, error)."""
        error = None
        # One canonical strict JSON reader owns duplicate-key, non-finite-value and
        # recorded-issue validation. A reader failure is loud below; it never reduces
        # the run set and lets INV-6, INV-7 or INV-8 pass over partial data.
        try:
            doc = artifact_accessors.load_feature_json(fy) or {}
        except artifact_accessors.FeatureJsonError as e:
            self._record_errors[feat] = e
            # A file that does not parse is a VIOLATION, never a silent skip — the whole
            # point of DEC-171 is that there is no quieter mode. Report and move on
            # so one broken feature cannot hide every other feature's invariants.
            error = (f"{self.fpath(feat, 'feature.json')} does not parse, so INV-6..8 and INV-12 "
                     f"cannot be checked for it: {e}")
            doc = None
        if doc is not None and not isinstance(doc, dict):
            error = f"{self.fpath(feat, 'feature.json')} is not a JSON mapping."
            doc = None
        return doc, error

    def _record_runs(self, feat, doc):
        """The parsed record's runs: entries as (runs, code_reviewing_runs, errors)."""
        errors, runs, code_reviewing_runs = [], [], []
        # `runs` stays a 3-tuple on purpose: INV-7 and the INV-22 loop below unpack it as
        # exactly three, so widening it here would break two invariants to serve one.
        # BUG-1080's exemption gets its own list instead.
        entries = doc.get("runs") or []
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"{feat}: a runs: entry is not a mapping ({entry!r}).")
                continue
            _squad = str(entry.get("squad", "")).strip()
            runs.append((str(entry.get("id", "")).strip(),
                         _squad,
                         str(entry.get("verdict", "")).strip()))
            # BUG-1080: a validator run that graded no CODE has no commit to pin. DEC-207
            # legalises exactly that run and spells it `code_grade: n_a`, so the record
            # states what was reviewed and INV-6 reads the claim rather than guessing.
            #
            # ABSENCE MEANS CODE REVIEW, so a pin is required. That is fail-CLOSED and it
            # is the OPPOSITE default from the `agent` key, where FEAT-31 made absence
            # deliberately benign — every run recorded before this key existed reviewed
            # code, and a silent exemption would retire the invariant on the whole corpus.
            # EXACT match, no strip and no case fold, so this test and
            # feature-schema.json's `enum: ["n_a"]` cannot disagree (panel Q2). A document
            # must never be schema-invalid and gate-exempt at the same time: any deviation
            # fails BOTH, which is the fail-closed direction.
            if _squad == "validator" and entry.get("code_grade") != "n_a":
                code_reviewing_runs.append(entry)
        return runs, code_reviewing_runs, errors

    def record_error(self, feat):
        """The FeatureJsonError the ONE parse of `feat`'s feature.json raised, or None. For the
        rows (INV-17, INV-21, INV-28, INV-44) whose own finding renders it (FEAT-63 T-02)."""
        self.record(feat)
        return self._record_errors.get(feat)

    def record(self, feat):
        """The feature.json record as INV-6..8 read it: (doc, runs, code_reviewing_runs, errors).
        `errors` are the parse-and-shape findings INV-6 reports; every other row of the family
        skips a record whose doc is None. Parsed once per feature."""
        if feat in self._records:
            return self._records[feat]
        fy = self.path(feat, "feature.json")
        errors, runs, code_reviewing_runs, doc = [], [], [], None
        if os.path.isfile(fy):
            doc, error = self._record_doc(feat, fy)
            if error is not None:
                errors.append(error)
        if doc is not None:
            runs, code_reviewing_runs, errors = self._record_runs(feat, doc)
        self._records[feat] = (doc, runs, code_reviewing_runs, errors)
        return self._records[feat]

    def run_verdicts(self, feat):
        """{run id: [verdicts]} as feature.json records them, for INV-15's cross-check."""
        doc, _runs, _crr, _errors = self.record(feat)
        out = {}
        for entry in ((doc or {}).get("runs") or []):
            if isinstance(entry, dict):
                out.setdefault(str(entry.get("id", "")).strip(), []).append(
                    str(entry.get("verdict", "")).strip())
        return out

    def run_states(self, feat):
        """Every runs/*/state.yaml under the feature as (path, rel, rundir, sdoc, error), in
        filesystem order like the baseline glob. `error` is INV-16's parse finding; sdoc is
        None when it is set."""
        if feat in self._run_states:
            return self._run_states[feat]
        out = []
        for sy in glob.glob(os.path.join(self.feature_dir(feat), "runs", "*", "state.yaml")):
            rel = os.path.relpath(sy, self.H)
            rundir = os.path.dirname(sy)
            # F-02, and this one had a LIVE fail-open the panel reproduced: `status: "complete"`
            # — quoted, legal YAML — does not match `^status:\s*complete`, so `complete` was
            # False and the completed-run checks below silently never fired.
            try:
                sdoc = harness_yaml.load_file(sy) or {}
            except harness_yaml.YamlParseError as e:
                out.append((sy, rel, rundir, None,
                            f"{rel}: state.yaml does not parse, so INV-15/16 cannot be "
                            f"checked for this run: {e}"))
                continue
            if not isinstance(sdoc, dict):
                out.append((sy, rel, rundir, None, f"{rel}: state.yaml is not a YAML mapping."))
                continue
            out.append((sy, rel, rundir, sdoc, None))
        self._run_states[feat] = out
        return out

    def lead_digest(self, dg):
        """(mapping, error) of one durable lead digest: digest_record's final fenced mapping,
        read ONCE and shared by INV-15 (the record exists and carries the required keys) and
        INV-46 (the verdict cross-check). Never validated against the live persona schema — a
        historical record may carry keys today's closed contract refuses (FEAT-1928 SC-07)."""
        if dg not in self._digests:
            try:
                self._digests[dg] = (digest_record.load_record(dg), None)
            except digest_record.DigestRecordError as _e:
                self._digests[dg] = (None, str(_e))
        return self._digests[dg]
