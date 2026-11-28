"""FEAT-2581 T-03 clean-pin receipts. Usage, from the FEAT-2581 worktree root:
    python3 <notes>/receipt-scripts/feat2581-cleanpin.py <pin-sha> [--reuse]

Creates (or reuses) clean detached checkouts of the baseline and the pin under
.claude/worktrees/harness/ (never fetching, never editing either checkout, never deleting a
pre-existing worktree), asserts each checkout's SHA and an empty status, then runs
feat2581-ledger-driver.py once per side, baseline first, writing notes/measurements/<side>.jsonl.gz.
--reuse rereads those measurement files instead of executing again, so a ruling recorded later never
forces a second execution. Everything below is derived from the two measurement files, the two
refs and notes/divergence-rulings.json, by the rules T-03 states, and written to
notes/clean-pin-byte-receipts.generated.md and notes/build-divergences.md."""
import ast
import base64
import datetime
import difflib
import functools
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

BASE = "e12381fde910eb05728004476a10d741d6918010"
OWN = ".harness/harness/features/FEAT-2581-feature-record-package"
NOTES = OWN + "/notes/"
TT = "tests/integration/test-typescript-typecheck.py"
OMP = "tests/unit/omp-hooks.test.ts"
BN = ".claude/skills/harness/bin/"
SCRIPTS = ("feat2581-cleanpin.py", "feat2581-grade-assert.py", "feat2581-ledger-driver.py",
           "recorder/sitecustomize.py", "feat2581-bun-preload.js", "feat2581-replay.py")
RK = {"suite": {"argv", "cwd", "exit", "stdout", "stderr", "cases"},
      "cli": {"argv", "cwd", "exit", "stdout", "stderr", "file_before", "file_after"},
      "gate": {"argv", "cwd", "exit", "stdout", "stderr"},
      "replay": {"argv", "exit", "stdout", "stderr", "before", "after"},
      "audit": {"exit", "stdout", "stderr"}}
MARKERS = dict(enumerate(["is not importable, so this file CANNOT be checked", "CRASHED while checking this file",
                          "was not importable) — budget is", "INV-23 CANNOT RUN for", "INV-37 CANNOT RUN",
                          "INV-26 CANNOT RUN", "INV-40 CANNOT RUN", "INV-7 CANNOT RUN for",
                          "refusal evidence CANNOT be checked", "harness.json cannot be validated"], 1))
TB = {1: ("check-domain.py", "_feature_json_schema_problems"), 2: ("check-domain.py", "_feature_json_schema_problems"),
      3: ("check-domain.py", "_feature_json_budget"), 4: ("check_state/feature_record.py", "_inv23_feature_json"),
      5: ("check_state/board.py", "_inv37_import"), 6: ("check_state/board.py", "_inv26_import"),
      7: ("check_state/ctx.py", "Ctx._load_hash_module"), 8: ("check_state/feature_record.py", "inv_7"),
      9: ("check_state/run_state.py", "_refusal_completion"), 10: ("harness_config.py", "_jsonschema"),
      11: ("check_state/table.py", "_EVIDENCE_READER")}
VERDICTS = ("grade_bar", "unit_files", "integration_files", "case_identity", "cli_identity", "replay_identity",
            "d02_inventory", "canonical_reader_audit", "overall")
SIDES = ("baseline", "pin")
CLASSES = ("checkout", "copied", "bun")
CALIBRATION = b"feat2581 raw\r\nline\rend\xe2\x80\x94\n"
INV_LIST = ([b"INV-7"], [b"INV-15"], [b"INV-46"], [b"INV-37"])

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True,
                      text=True).stdout.strip()
HERE = os.path.dirname(os.path.abspath(__file__))
pin = sys.argv[1]
REUSE = "--reuse" in sys.argv
MAIN = ROOT.split("/.claude/worktrees/")[0]
WT = os.path.join(MAIN, ".claude", "worktrees", "harness")
CHECKOUT = {"baseline": os.path.join(WT, "feat2581-base-" + BASE[:8]), "pin": os.path.join(WT, "feat2581-pin-" + pin[:8])}
REF = {"baseline": BASE, "pin": pin}


def git(*args, cwd=ROOT, text=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=text)


def show(ref, path):
    return git("show", ref + ":" + path, text=False).stdout


# ---------------------------------------------------------------- checkouts and measurement ---
def prepare_checkouts():
    for side, path in CHECKOUT.items():
        if not os.path.isdir(path):
            subprocess.run(["git", "-C", MAIN, "worktree", "add", "--detach", path, REF[side]], check=True,
                           capture_output=True)
        head = git("rev-parse", "HEAD", cwd=path).stdout.strip()
        assert head == REF[side], "%s checkout is at %s, not %s" % (side, head, REF[side])
        assert git("status", "--porcelain", cwd=path).stdout == "", "%s checkout is dirty" % side


def measure():
    meta = {}
    for side in ("baseline", "pin"):
        out = os.path.join(ROOT, NOTES, "measurements", side + ".jsonl.gz")
        meta_path = os.path.join(ROOT, NOTES, "measurements", side + ".meta.json")
        if REUSE and os.path.exists(out) and os.path.exists(meta_path):
            print("== %s: reusing %s" % (side, out), flush=True)
        else:
            argv = [sys.executable, os.path.join(HERE, "feat2581-ledger-driver.py"), side, CHECKOUT[side], BASE, out]
            started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            subprocess.run(argv, check=True)
            finished = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            with open(meta_path, "w", encoding="utf-8") as handle:
                json.dump({"command": argv, "started": started, "finished": finished}, handle, indent=2)
                handle.write("\n")
        with open(meta_path, encoding="utf-8") as handle:
            meta[side] = json.load(handle)
    return meta


# ------------------------------------------------------------------------- derivation -----------
def canonical(value):
    return isinstance(value, str) and re.fullmatch(
        r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?", value) is not None \
        and base64.b64encode(base64.b64decode(value, validate=True)).decode("ascii") == value


def kind_ok(rid, r):
    kind = r.get("kind")
    if kind not in RK or not isinstance(r.get("streams"), dict) or set(r["streams"]) != RK[kind]:
        return False
    return (kind == "cli") == (r.get("class") in CLASSES) and (kind == "suite") == rid.startswith("suite#")


def streams_ok(streams):
    if not all(canonical(v) or (v is None and k in ("file_before", "file_after")) for k, v in streams.items()):
        return False
    return re.fullmatch(rb"-?[0-9]+", base64.b64decode(streams["exit"], validate=True)) is not None


class Measured:
    def __init__(self):
        self.root = {s: CHECKOUT[s] for s in ("baseline", "pin")}
        self.raw = {}
        self.M = {}
        for side in self.root:
            path = os.path.join(ROOT, NOTES, "measurements", side + ".jsonl.gz")
            with open(path, "rb") as handle:
                self.raw[side] = handle.read()
            rows = [json.loads(x.decode("utf-8")) for x in gzip.decompress(self.raw[side]).splitlines()]
            assert len({r["id"] for r in rows}) == len(rows) > 0, side
            self.M[side] = {r["id"]: r for r in rows}
        self.check_shapes()

    def check_shapes(self):
        bad = [(side, rid) for side, records in self.M.items() for rid, r in records.items()
               if not (kind_ok(rid, r) and streams_ok(r["streams"]))]
        bad += [("both", i) for i in set(self.M["baseline"]) & set(self.M["pin"])
                if self.M["baseline"][i]["kind"] != self.M["pin"][i]["kind"]]
        assert not bad, ("malformed measurement records", sorted(bad)[:10])

    def nz(self, side, value):
        return None if value is None else base64.b64decode(value, validate=True).replace(self.root[side].encode(), b"<checkout>")

    def st(self, side, rid, key):
        return self.nz(side, self.M[side][rid]["streams"][key])

    def of_kind(self, side, kind):
        return [r for r in self.M[side].values() if r["kind"] == kind]


# Rendering (the account). Injective: a backslash is doubled, undecodable bytes are \b{hh}, any
# character that is not printable (tab included) is \x{h}, a trailing space is \x{20}, and a line
# longer than 64 rendered characters continues on lines prefixed `\c ` so a long delta is localised.
def esc(ch):
    if ch == "\\":
        return "\\\\"
    if 0xdc80 <= ord(ch) <= 0xdcff:
        return "\\b{%02x}" % (ord(ch) - 0xdc00)
    return ch if ch.isprintable() else "\\x{%x}" % ord(ch)


def tokens(line):
    kept = line.rstrip(" ")
    return [esc(ch) for ch in kept] + ["\\x{20}"] * (len(line) - len(kept))


def rendered(data):
    if data is None:
        return ["\\absent"]
    out = []
    for line in data.decode("utf-8", "surrogateescape").split("\n"):
        t = tokens(line)
        out += [("\\c " if i else "") + "".join(t[i:i + 64]) for i in range(0, max(len(t), 1), 64)]
    return out


def payload(data):
    return "absent" if data is None else repr(data)


def lines(*xs):
    return "".join(x + "\n" for x in xs)


def account_diff(old, new):
    return ["| " + x for x in difflib.unified_diff(rendered(old), rendered(new), "old", "new", n=2, lineterm="")]


def body_pair(old, new):
    return lines("old: " + payload(old), "new: " + payload(new), "account:", *account_diff(old, new))


def body_unaligned(side, streams):
    acc = [y for k in sorted(streams) for y in ["| stream %s:" % k] + ["|   " + x for x in rendered(streams[k])]]
    return lines("side: " + side, *["stream %s: %s" % (k, payload(streams[k])) for k in sorted(streams)], "account:", *acc)


def source_only(f, q, old, new):
    return lines("source_only: source text read through git show at the baseline and the pin, never captured output",
                 "file: " + BN + f, "symbol: " + q, "old_source: " + payload(old), "new_source: " + payload(new),
                 "account:", *account_diff(old, new))


def segment(ref, f, q):
    source = show(ref, BN + f).decode("utf-8")
    tree = ast.parse(source)

    def step(node, part):
        return next(x for x in node.body if getattr(x, "name", None) == part
                    or (isinstance(x, ast.Assign) and part in [getattr(y, "id", None) for y in x.targets]))
    return ast.get_source_segment(source, functools.reduce(step, q.split("."), tree), padded=True).encode("utf-8")


def record_divergences(m, i):
    a, b = m.M["baseline"].get(i), m.M["pin"].get(i)
    if not (a and b):
        return {i + ":unaligned"}
    return {i + ":" + k for k in a["streams"] if m.st("baseline", i, k) != m.st("pin", i, k)}


def divergent_ids(m):
    """Every differing stream of an aligned non-suite record, and every one-sided record."""
    ids = {i for s in m.M for i, r in m.M[s].items() if r["kind"] != "suite"}
    return set().union(*(record_divergences(m, i) for i in ids))


def wanted_files():
    py = {x for x in git("ls-tree", "-r", "--name-only", BASE, "tests/unit", "tests/integration").stdout.split()
          if re.fullmatch(r"tests/(unit|integration)/test[-_][^/]*\.py", x)}
    return (py - {"tests/integration/test-feature-json-merge.py"}) | {OMP}


def check_suite_records(m, SU, want):
    assert set(SU["baseline"]) == want == set(SU["pin"]), "suite records are not one per file per side"
    for s, f, r in ((s, f, r) for s in SU for f, r in SU[s].items()):
        assert m.nz(s, r["streams"]["cwd"]) == b"<checkout>", (s, f, "cwd")
        assert base64.b64decode(r["streams"]["argv"], validate=True).split(b"\0")[-1] == f.encode(), (s, f, "argv")


def item11_hit(argv, line):
    return b"--list" in argv and line.split()[:1] in INV_LIST


def marker_hit(item, line):
    return MARKERS[item].encode() in line and not (item == 6 and b"gh_board.py" in line)


def unreached_bodies(measured):
    return {"d02#%d:unreached" % i: source_only(*TB[i], segment(BASE, *TB[i]), segment(pin, *TB[i]))
            for i in range(1, 12) if i not in measured}


class Derived:
    def __init__(self, m, rulings):
        self.m = m
        self.rulings = rulings
        self.D = divergent_ids(m)
        self.SU = {s: {i[6:]: r for i, r in m.M[s].items() if r["kind"] == "suite"} for s in m.M}
        self.want = wanted_files()
        check_suite_records(m, self.SU, self.want)
        self.bf = {f for f in self.want if self.xc("baseline", f)}
        self.cw = sorted(self.want - self.bf)

    # suites
    def sv(self, s, f, k):
        return self.m.nz(s, self.SU[s][f]["streams"][k])

    def xc(self, s, f):
        return int(self.sv(s, f, "exit"))

    def fail_lines(self, s, f):
        return [l for k in ("stdout", "stderr") for l in self.sv(s, f, k).split(b"\n")
                if l.split()[:1] and l.split()[0].startswith(b"FAIL")]

    def markers(self, s, f):
        return [l for l in self.sv(s, f, "stdout").split(b"\n") if l.split()[:1] and l.split()[0] in (b"ok", b"ok:", b"PASS", b"PASS:")]

    def unittest_lines(self, s, f):
        return [l for l in self.sv(s, f, "cases").split(b"\n") if l]

    def entries(self, s, f):
        if f == OMP:
            raw = base64.b64decode(self.SU[s][f]["streams"]["cases"], validate=True)
            root = self.m.root[s].encode()
            return [("%s %s %s" % (next((y.tag for y in e if y.tag in ("failure", "error", "skipped")), "passed"),
                                    e.get("classname"), e.get("name"))).encode().replace(root, b"<checkout>")
                    for e in ET.fromstring(raw).iter("testcase")]
        return self.markers(s, f) + self.unittest_lines(s, f)

    def method(self, f):
        if f == OMP:
            return "bun-junit"
        return ["unnamed", "marker", "unittest", "marker+unittest"][bool(self.markers("baseline", f)) + 2 * bool(self.unittest_lines("baseline", f))]

    def identity(self, s, f):
        if self.method(f) == "unnamed" or (f != OMP and len(self.entries("baseline", f)) < 2):
            return self.sv(s, f, "stdout")
        return b"".join(e + b"\n" for e in self.entries(s, f))

    def case_line(self, f):
        same = "SAME" if self.identity("baseline", f) == self.identity("pin", f) else "DIFFERENT"
        return "case_set: %s %s %d %d %s" % (f, self.method(f), len(self.entries("baseline", f)),
                                             len(self.entries("pin", f)), same)

    # gates
    def hits(self, item, record, data):
        if item == 11:
            argv = base64.b64decode(record["streams"]["argv"], validate=True).split(b"\0")
            return [l for l in data.split(b"\n") if item11_hit(argv, l)]
        return [l for l in data.split(b"\n") if marker_hit(item, l)]

    def count(self, item, s):
        return sum(len(self.hits(item, r, self.m.nz(s, r["streams"][k]))) for r in self.m.of_kind(s, "gate") for k in ("stdout", "stderr"))

    def gate_streams(self):
        """(divergence id, record id, stream) for each differing gate stdout or stderr."""
        pairs = ((x,) + tuple(x.rsplit(":", 1)) for x in self.D if x.startswith("gate#"))
        return [(x, j, k) for x, j, k in pairs if k in ("stdout", "stderr")]

    def item_hit(self, i, j, k):
        M = self.m.M
        return any(j in M[s] and self.hits(i, M[s][j], self.m.st(s, j, k)) for s in M)

    def d02(self):
        DR = {(i, x) for x, j, k in self.gate_streams() for i in range(1, 12) if self.item_hit(i, j, k)}
        measured = {i for i in range(1, 12) if self.count(i, "baseline") + self.count(i, "pin")}
        return DR, measured

    def diverged_body(self, x):
        m = self.m
        i, k = x.rsplit(":", 1)
        if k != "unaligned":
            return body_pair(m.st("baseline", i, k), m.st("pin", i, k))
        side = "baseline" if i in m.M["baseline"] else "pin"
        return body_unaligned(side, {kk: m.st(side, i, kk) for kk in m.M[side][i]["streams"]})

    def bodies(self):
        B = {x: self.diverged_body(x) for x in self.D}
        DR, measured = self.d02()
        for f in self.bf - {TT}:
            B["baseline#" + f] = body_unaligned("baseline", {k: self.sv("baseline", f, k) for k in ("exit", "stdout", "stderr")})
        for f in (f for f in self.cw if self.identity("baseline", f) != self.identity("pin", f)):
            B["cases#" + f] = body_pair(self.identity("baseline", f), self.identity("pin", f))
        B.update(unreached_bodies(measured))
        return B, DR, measured

    def ruled(self, rid):
        r = self.rulings.get(rid)
        return bool(r) and all(isinstance(r.get(k), str) and r[k].strip() != "" for k in ("by", "date", "reason"))


def test_changes():
    names = git("diff", "--name-only", "--no-renames", BASE, pin, "--", "tests").stdout.split()
    out = {}
    for f in names:
        out[f] = subprocess.run(["git", "-c", "diff.suppressBlankEmpty=false", "diff", "--no-color", "--no-ext-diff",
                                 "--no-textconv", "--no-renames", "--diff-algorithm=myers", "--indent-heuristic",
                                 "--inter-hunk-context=0", "--src-prefix=a/", "--dst-prefix=b/", "-U3", BASE, pin,
                                 "--", f], cwd=ROOT, capture_output=True, check=True).stdout
    return out


def grade_runs():
    script = os.path.join(HERE, "feat2581-grade-assert.py")
    runs = {}
    for side, ref in (("pin", pin), ("baseline", BASE)):
        runs[side] = subprocess.run([sys.executable, script, "--ref", ref], cwd=ROOT, capture_output=True, text=True)
    return runs


def audit_count(m, side):
    found = re.findall(rb"(?m)^([0-9]+) unresolved reader site\(s\) across ([0-9]+) Python file\(s\)$",
                       m.nz(side, m.M[side]["audit"]["streams"]["stdout"]))
    assert len(found) == 1, (side, found)
    return found[0]


def load_rulings():
    path = os.path.join(ROOT, NOTES, "divergence-rulings.json")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("[]\n")
    with open(path, encoding="utf-8") as handle:
        return {r["record"]: r for r in json.load(handle)}


# ---------------------------------------------------------------------------- receipt -----------
def script_lines():
    out = []
    for name in SCRIPTS:
        rel = NOTES + "receipt-scripts/" + name
        with open(os.path.join(ROOT, rel), "rb") as handle:
            out.append("script_sha256: %s %s" % (rel, hashlib.sha256(handle.read()).hexdigest()))
    return out


def suite_lines(d):
    out = sorted("baseline_failing: %s %d %d" % (f, d.xc("baseline", f), len(d.fail_lines("baseline", f))) for f in d.bf)
    return out + sorted(d.case_line(f) for f in d.cw)


def d02_line(d, i, measured):
    if i in measured:
        return "d02_item: %d MEASURED %d %d" % (i, d.count(i, "baseline"), d.count(i, "pin"))
    return "d02_item: %d UNREACHED" % i


def gate_lines(m, d, DR, measured):
    out = ["gate_captures: %d %d" % tuple(len(m.of_kind(s, "gate")) - 1 for s in SIDES)]
    out += sorted(d02_line(d, i, measured) for i in range(1, 12))
    residual = {x for x in d.D if x.startswith("gate#")} - {x for _, x in DR}
    out.append("d02_item: residual %d" % len(residual))
    return out + sorted("d02_item_record: %d %s" % y for y in DR)


def all_ruled(d, ids):
    return all(d.ruled(i) for i in ids)


def files_ok(d, prefix):
    clean = all(not d.xc("pin", f) and d.fail_lines("pin", f) == d.fail_lines("baseline", f)
                for f in d.cw if f.startswith(prefix))
    return clean and all_ruled(d, ("baseline#" + f for f in d.bf - {TT} if f.startswith(prefix)))


def case_identity_ok(d, B):
    under_two = [f for f in d.cw if len(d.entries("baseline", f)) < 2 and git("diff", "--quiet", BASE, pin, "--", f).returncode]
    return all_ruled(d, (i for i in B if i.startswith("cases#"))) and not under_two and bool(d.entries("baseline", OMP))


def cli_identity_ok(m, d, B):
    classes_ok = all(sum(r.get("class") == k for r in m.of_kind(s, "cli")) for s in m.M for k in CLASSES)
    excluded = ("gate#", "replay#", "audit", "cases#", "baseline#", "d02#")
    return classes_ok and all_ruled(d, (i for i in B if not i.startswith(excluded)))


def calibration_ok(m):
    return all(base64.b64decode(m.M[s]["gate#calibration#1"]["streams"]["stdout"], validate=True) == CALIBRATION
               for s in m.M)


def gates_captured(m, DR, measured):
    """Each side captured a gate beyond calibration, and every MEASURED item has a differing stream."""
    return all(len(m.of_kind(s, "gate")) > 1 for s in m.M) and all(any(i == j for j, _ in DR) for i in measured)


def d02_inventory_ok(m, d, B, DR, measured):
    ruled = all_ruled(d, (i for i in B if i.startswith(("gate#", "d02#"))))
    return calibration_ok(m) and gates_captured(m, DR, measured) and ruled


def grade_bar_ok(grades):
    twelve = set(re.findall(r"(?m)^below_bar: (\S+) \d$", grades["baseline"].stdout))
    return grades["pin"].returncode == 0 and grades["baseline"].returncode == 1 and len(twelve) == 12


def audit_ok(m, au):
    return m.nz("pin", m.M["pin"]["audit"]["streams"]["exit"]) == b"0" and au[1][0] == b"0"


def verdict_lines(m, d, derived, grades, au):
    B, DR, measured = derived
    verdict = {
        "grade_bar": grade_bar_ok(grades),
        "unit_files": files_ok(d, "tests/unit/"),
        "integration_files": files_ok(d, "tests/integration/"),
        "case_identity": case_identity_ok(d, B),
        "cli_identity": cli_identity_ok(m, d, B),
        "replay_identity": all_ruled(d, (i for i in B if i.startswith("replay#"))),
        "d02_inventory": d02_inventory_ok(m, d, B, DR, measured),
        "canonical_reader_audit": audit_ok(m, au),
    }
    verdict["overall"] = all(verdict.values()) and all_ruled(d, B)
    return ["%s: %s" % (k, "PASS" if verdict[k] else "FAIL") for k in VERDICTS]


def receipt_lines(m, d, derived, grades):
    B, DR, measured = derived
    au = [audit_count(m, s) for s in SIDES]
    out = ["implementation_pin: " + pin, "baseline: " + BASE]
    out += ["checkout_root: %s %s" % (s, m.root[s]) for s in SIDES]
    out += script_lines() + suite_lines(d) + gate_lines(m, d, DR, measured)
    out.append("audit_scanned_files: %s %s" % (au[0][1].decode(), au[1][1].decode()))
    out += sorted("divergence: %s %s" % (i, "RULED" if d.ruled(i) else "UNRULED") for i in B)
    return out + verdict_lines(m, d, derived, grades, au)


def measurement_provenance(m, meta, side):
    raw = m.raw[side]
    run = meta[side]
    return ["measured %s at %s: %s .. %s, command %s" % (side, REF[side], run["started"], run["finished"],
                                                         " ".join(run["command"])),
            "measurement file %s.jsonl.gz: %d gzip bytes, raw sha256 %s, decompressed jsonl sha256 %s" % (
                side, len(raw), hashlib.sha256(raw).hexdigest(), hashlib.sha256(gzip.decompress(raw)).hexdigest())]


def provenance_lines(m, meta, grades):
    info = ["", "# provenance (not derived lines)", ""]
    for side in SIDES:
        info += measurement_provenance(m, meta, side)
    info.append("checkouts were detached at the two SHAs with an empty `git status --porcelain` before measuring")
    info.append("grade at the pin (exit %d), at the baseline (exit %d):" % (grades["pin"].returncode, grades["baseline"].returncode))
    info += ["    " + x for x in (grades["pin"].stdout + grades["baseline"].stdout).splitlines()]
    info.append("generated %s by %s" % (datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), " ".join(sys.argv)))
    return info


def write_divergences(B):
    TC = test_changes()
    parts = [b"# FEAT-2581 build divergences\n\nGenerated by feat2581-cleanpin.py. Every record below is derived from\n"
             b"notes/measurements/*.jsonl.gz and the two refs; the operator rules each one in\n"
             b"notes/divergence-rulings.json.\n\n"]
    parts += [("divergence: %s\n%send_divergence\n\n" % (i, B[i])).encode("utf-8") for i in sorted(B)]
    parts += [b"test_change: " + f.encode() + b"\n" + TC[f] + b"end_test_change\n\n" for f in sorted(TC)]
    with open(os.path.join(ROOT, NOTES, "build-divergences.md"), "wb") as handle:
        handle.write(b"".join(parts))


def write_receipt(lines):
    with open(os.path.join(ROOT, NOTES, "clean-pin-byte-receipts.generated.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def print_summary(out, d, B):
    print("\n".join(out[-len(VERDICTS):]))
    print("divergences: %d (%d unruled)" % (len(B), sum(not d.ruled(i) for i in B)))


def main():
    prepare_checkouts()
    meta = measure()
    m = Measured()
    d = Derived(m, load_rulings())
    B, DR, measured = d.bodies()
    grades = grade_runs()
    out = receipt_lines(m, d, (B, DR, measured), grades)
    write_receipt(out + provenance_lines(m, meta, grades))
    write_divergences(B)
    print_summary(out, d, B)


main()
