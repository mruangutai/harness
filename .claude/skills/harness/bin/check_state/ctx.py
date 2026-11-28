"""The parse-once runner context and the primitives every family shares. (FEAT-69)"""
import glob, json, os, re, subprocess
import artifact_accessors
import harness_boundary
import harness_yaml
from feature_record import read as record_read
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
# keys (INV-6's shape). Splitting the station read from the document read is
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

# SHIPPED IS ONE LINE OF TEXT, NEVER A PARSE (FEAT-2206). A shipped feature is checked for
# nothing, so deciding that a feature shipped must not depend on anything that can change after
# it shipped: not the strict plan loader, not the plan schema, not the YAML library. The decision
# reads exactly one column-zero `status:` line. Anything else -- no plan, unreadable bytes, no such
# line, two status keys whatever their values, a status nested under another key -- is "not
# shipped", and the feature keeps every check (fail closed: a plan nobody can read is never
# silently excused). Keys are counted before any value is read, so a second declaration whose
# value is a list, empty or a number still makes the plan ambiguous rather than invisible.
_STATUS_KEY = re.compile(r"""^(['"]?)status\1[ \t]*:""", re.M)
_STATUS_LINE = re.compile(r"^status:[ \t]*(['\"]?)([A-Za-z][\w-]*)\1[ \t]*(?:#.*)?$", re.M)


def lenient_station(feature_dir):
    """The station on plan.yaml's single top-level `status:` line, or "" when the plan does not
    declare exactly one top-level status key, or that one key's value is not a plain token."""
    try:
        with open(os.path.join(feature_dir, "plan.yaml"), encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return ""
    if len(_STATUS_KEY.findall(text)) != 1:
        return ""
    found = _STATUS_LINE.findall(text)
    return found[0][1] if len(found) == 1 else ""


def is_shipped(feature_dir):
    """Whether the feature at `feature_dir` has shipped (station `done`)."""
    return lenient_station(feature_dir) == "done"


def comparison_record(path):
    """A shipped feature.json as raw comparison data: the parsed mapping, or None. Never a
    finding -- a shipped record is read only so another feature's claims can be compared with it.
    The canonical strict JSON-mapping read, without the feature schema the strict loader adds."""
    try:
        return artifact_accessors.load_json_mapping(path)
    except (artifact_accessors.ArtifactAccessError, RecursionError):
        return None


def _landed_entry(entry):
    """One landed feature_corpus entry as a population triple. A shipped record reuses the
    document the census already parsed and is re-read leniently only when the strict parse gave
    none, so it still contributes its claims as comparison data."""
    if not is_shipped(entry["path"]):
        return entry["id"], entry["document"], False
    doc = entry["document"]
    if not isinstance(doc, dict):
        doc = comparison_record(os.path.join(entry["path"], "feature.json"))
    return entry["id"], doc, True


def _discover_feature_dirs(H, root):
    """`{feature basename: root-relative directory}` for every feature directory on disk."""
    # corpus-scope: checkout-local
    found = (d for d in glob.glob(os.path.join(H, "*", "features", "*")) if os.path.isdir(d))
    return {os.path.basename(d): os.path.relpath(d, root) for d in found}


def _split_shipped(root, feat_dirs, keep):
    """(audit subjects, shipped set) of the features `keep` selects (None: all), sorted."""
    selected = [f for f in sorted(feat_dirs) if keep is None or f in keep]
    shipped = {f for f in selected if is_shipped(os.path.join(root, feat_dirs[f]))}
    return [f for f in selected if f not in shipped], shipped


def approved(txt):
    if not txt: return False
    m = re.search(r"^##\s+Approval\s*$(.*?)(?=^##\s|\Z)", txt, re.M | re.S)
    return bool(m) and re.search(r"status:\s*approved", m.group(1), re.I) is not None

def has_approval_block(txt):
    return bool(txt) and re.search(r"^##\s+Approval\s*$", txt, re.M) is not None

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
        self.feat_dirs = _discover_feature_dirs(self.H, self.root)
        # A SHIPPED FEATURE IS NEVER AN AUDIT SUBJECT (FEAT-2206). It leaves the subject list here,
        # before any up-front load below opens its BRIEF, plan or STATE.md and before any
        # per-feature row runs; only the cross-feature comparisons read it again, as data
        # (`population`, INV-29, INV-52). `feat_dirs` keeps every discovered directory.
        self.features, self.shipped = _split_shipped(self.root, self.feat_dirs, keep)

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
        # INV-32's era boundary, resolved ONCE (BUG-1071): the YYYY-MM-DD before which INV-32
        # grades nothing, or None - null (no pre-adversarial-panel era, the schema default) or no
        # valid config (reported by _load_config, and runner.main grades nothing then).
        self.era_start = self.cj["panel_era_start"] if self.cj_valid else None

    def _load_git_top(self):
        # THE GIT TOP LEVEL, resolved ONCE for INV-33 below (FEAT-41 T-14 / issue #867).
        #
        # RELATIVE TO THE GIT TOP LEVEL, NEVER TO `root`, and the reason CHANGED with the rebase while
        # the requirement did not. Since FEAT-42 T-12 this script resolves `root` through
        # harness_boundary.resolve_root(_selfdir), which reads the Harness project-root environment override, never a host's
        # session variable. That is the HARNESS root, which
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
        INV-37 (each used to spawn its own probe)."""
        if gh_bin not in self._gh_ok:
            _auth = self.spawn([gh_bin, "auth", "status"], capture_output=True, text=True, timeout=15)
            self._gh_ok[gh_bin] = _auth is not None and _auth.returncode == 0
        return self._gh_ok[gh_bin]

    def station(self, feat):
        """The feature's plan.yaml station, from the document `_load_plan_docs` parsed once."""
        return station_of(self.plan_docs.get(feat))

    def _load_config(self):
        # `cj` is the validated harness.json, read ONCE here and consumed by every
        # config-dependent check. A missing or invalid config is one exact violation and
        # `cj_valid` False: runner.main then stops before any config-dependent grading, so
        # no check ever runs on defaults it invented (FEAT-2297). `cj` stays bound (to {})
        # so construction itself never crashes on the failure it is reporting.
        path = os.path.join(self.H, "harness.json")
        try:
            self.cj = artifact_accessors.load_harness_json(path)
            self.cj_valid = True
        except artifact_accessors.ArtifactAccessError as e:
            self.cj, self.cj_valid = {}, False
            self.bad.append(f".harness/harness.json is invalid: {e}")

    def _load_hash_module(self):
        bad = self.bad
        try:
            _pm40 = harness_boundary.load_repo_module("plan_merge.approval")
            self.signed_task_hash = _pm40.signed_task_hash
        except harness_boundary.RepoModuleError as _pme40:
            self.signed_task_hash = None
            # The ORIGINAL exception is rendered, not the boundary's wrapper: the reader wants
            # the type and text of what went wrong inside plan_merge/approval.py (FEAT-63 T-01).
            bad.append("INV-40 CANNOT RUN its signed-text check: plan_merge/approval.py did not import "
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
        self.default_cycles = self.cj["budgets"]["max_total_cycles"] if self.cj_valid else None
        self._load_hash_module()

        # Per-feature caches filled on first use: the feature.json record (INV-6 family).
        self._records = {}
        self._gh_ok = {}
        self.spawn_error = None
        self._record_errors = {}

    def population(self):
        """`[(feature, feature.json mapping or None, shipped)]` for a REPO-WIDE record predicate,
        sorted by feature.

        Unscoped (a plain clone, or any run outside a sparse worktree): the selected features,
        exactly as before — `--feature` narrows it, as the table's scope rule says. Scoped: every
        LANDED record from the main corpus, with this checkout's own active record in place of
        its landed copy, so a predicate across features still sees all of them. In-progress
        siblings are never read (operator ruling, 2026-10-04). A main corpus that cannot be read
        raises feature_corpus.CorpusError; the caller reports it.

        A SHIPPED record is comparison data only (FEAT-2206): read lazily, here, by
        `comparison_record`, never through `record` or the strict reader, so nothing about it is
        ever reported -- an unreadable one simply contributes no claim."""
        if not self.scoped:
            return sorted(self._local_population(), key=lambda p: p[0])
        if self._population is None:
            import feature_corpus
            local = self._local_population()
            mine = {f for f, _doc, _shipped in local}
            landed = [_landed_entry(e) for e in feature_corpus.records(self.owner)
                      if e["id"] not in mine]
            self._population = sorted(landed + local, key=lambda p: p[0])
        return self._population

    def _local_population(self):
        """This checkout's selected records: subjects through `record`, shipped ones as data."""
        return ([(f, self.record(f)[0], False) for f in self.features]
                + [(f, comparison_record(self.path(f, "feature.json")), True)
                   for f in self.shipped])

    def fpath(self, feat, tail=""):
        _b = self.feat_dirs.get(feat) or os.path.join(".harness", "?", "features", feat)
        return _b + (os.sep + tail if tail else "")

    def feature_dir(self, feat):
        return os.path.join(self.root, self.feat_dirs[feat]) if feat in self.feat_dirs \
            else os.path.join(self.H, "?", "features", feat)

    def path(self, feat, tail):
        return os.path.join(self.feature_dir(feat), tail)

    def _record_doc(self, feat, fy):
        """The parsed feature.json document, or None and the INV-6 finding that explains why:
        (doc, error)."""
        error = None
        # One canonical strict JSON reader owns duplicate-key, non-finite-value and
        # recorded-issue validation. A reader failure is loud below; it never reduces
        # the run set and lets INV-6 or INV-7 pass over partial data.
        try:
            doc = record_read.load_feature_json(fy) or {}
        except record_read.FeatureJsonError as e:
            self._record_errors[feat] = e
            # A file that does not parse is a VIOLATION, never a silent skip — the whole
            # point of DEC-171 is that there is no quieter mode. Report and move on
            # so one broken feature cannot hide every other feature's invariants.
            error = (f"{self.fpath(feat, 'feature.json')} does not parse, so INV-6 and INV-7 "
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
            # schemas/feature.json's `enum: ["n_a"]` cannot disagree (panel Q2). A document
            # must never be schema-invalid and gate-exempt at the same time: any deviation
            # fails BOTH, which is the fail-closed direction.
            if _squad == "validator" and entry.get("code_grade") != "n_a":
                code_reviewing_runs.append(entry)
        return runs, code_reviewing_runs, errors

    def record_error(self, feat):
        """The FeatureJsonError the ONE parse of `feat`'s feature.json raised, or None. For the
        rows (INV-21, INV-44) whose own finding renders it (FEAT-63 T-02)."""
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
