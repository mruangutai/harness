"""FEAT-2581 T-03 recorder, loaded through PYTHONPATH into every Python process of one side's run.

It is inert unless FEAT2581_LEDGER names the side's ledger directory (outside both checkouts).
Everything it writes goes there; it changes no byte or value a test receives or prints.

- feature-record.py processes (wherever the file lives): run the identical command once as a child
  with a recursion marker, record argv, cwd, exit, stdout, stderr and the --file bytes before and
  after, relay both streams byte for byte, and exit with the child's status. The child runs under
  one fixed clock.
- check-state.py / check-domain.py children whose stdout (and stderr, or stderr=STDOUT) a test
  captures through communicate: record the exact pipe bytes before any decoding, then hand the
  test exactly the str or bytes it would have received.
- unittest results of the suite's top process: one `<outcome> <test id>` line per result.
- tempfile naming: one fixed root and a per-test-file counter, so fixture paths are the same bytes
  on both sides.
- FEAT2581_CLOCK_ONLY: install the fixed clock and nothing else (the replay).
"""
import os
import sys

_LEDGER = os.environ.get("FEAT2581_LEDGER")
_FIXTURES = "/tmp/feat2581-fixtures"
_ENV_KEYS = ("FEAT2581_LEDGER", "FEAT2581_CHECKOUT", "FEAT2581_TESTFILE", "FEAT2581_TESTINDEX",
             "FEAT2581_RECORDER", "FEAT2581_BUN", "FEAT2581_CLOCK_ONLY")
_GATES = ("check-state.py", "check-domain.py")


def _install_clock():
    """Bind every `datetime.datetime` name a later import takes to one fixed instant."""
    import datetime as _dt
    base = _dt.datetime
    fixed = base(2026, 1, 1, 0, 0, 0, tzinfo=_dt.timezone.utc)

    class _Meta(type):
        def __instancecheck__(cls, obj):
            return isinstance(obj, base)

        def __subclasscheck__(cls, sub):
            return issubclass(sub, base)

    class datetime(base, metaclass=_Meta):  # noqa: N801 - keeps the public name and repr
        @classmethod
        def now(cls, tz=None):
            return fixed.astimezone(tz) if tz is not None else fixed.replace(tzinfo=None)

        @classmethod
        def utcnow(cls):
            return fixed.replace(tzinfo=None)

        @classmethod
        def today(cls):
            return fixed.replace(tzinfo=None)

    datetime.__module__ = "datetime"
    _dt.datetime = datetime


def _locked_counter(name):
    """A per-test-file counter shared by every process of that file's run."""
    import fcntl
    directory = os.path.join(_LEDGER, "ctr")
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "%s.%s" % (_slug(os.environ.get("FEAT2581_TESTFILE", "none")), name))
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        raw = os.read(fd, 64)
        value = int(raw or b"0") + 1
        os.lseek(fd, 0, 0)
        os.ftruncate(fd, 0)
        os.write(fd, str(value).encode())
        return value
    finally:
        os.close(fd)


def _slug(text):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in text)


def _b64(data):
    import base64
    return base64.b64encode(data).decode("ascii")


def _write_record(record):
    import json
    directory = os.path.join(_LEDGER, "rec")
    os.makedirs(directory, exist_ok=True)
    name = "%s-%d-%d" % (record["kind"], os.getpid(), _locked_counter("rec"))
    tmp = os.path.join(directory, "." + name)
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(record, handle)
    os.replace(tmp, os.path.join(directory, name + ".json"))


def _fail(reason):
    """A required stream could not be captured: no record, and the side's run is refused."""
    directory = os.path.join(_LEDGER, "errors")
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, "%d-%d.txt" % (os.getpid(), _locked_counter("err"))), "w") as handle:
        handle.write(reason + "\n")


def _argv_bytes(argv):
    return b"\0".join(os.fsencode(str(a)) for a in argv)


def _file_arg(argv):
    for index, arg in enumerate(argv):
        if arg == "--file" and index + 1 < len(argv):
            return argv[index + 1]
        if arg.startswith("--file="):
            return arg[len("--file="):]
    return None


def _read_or_none(path):
    if path is None or not os.path.isfile(path):
        return None
    with open(path, "rb") as handle:
        return handle.read()


def _cli_class(script):
    if os.environ.get("FEAT2581_BUN"):
        return "bun"
    checkout = os.path.realpath(os.environ.get("FEAT2581_CHECKOUT", "/nonexistent"))
    return "checkout" if os.path.realpath(script).startswith(checkout + os.sep) else "copied"


def _write_all(fd, data):
    view = memoryview(data)
    while view:
        view = view[os.write(fd, view):]


def _intercept_cli():
    """Run the identical command once as a child; record it; relay; exit with its status."""
    import subprocess
    target = _file_arg(sys.argv[1:])
    before = _read_or_none(target)
    env = dict(os.environ, FEAT2581_CLI_CHILD="1")
    try:
        child = subprocess.run(list(sys.orig_argv), env=env, capture_output=True)
    except OSError as exc:
        _fail("feature-record.py child did not start: %r" % (exc,))
        raise
    after = _read_or_none(target)
    ordinal = _locked_counter("cli")
    to_b64 = lambda v: None if v is None else _b64(v)  # noqa: E731
    _write_record({
        "id": "%s#%d" % (os.environ.get("FEAT2581_TESTFILE", "none"), ordinal),
        "kind": "cli", "class": _cli_class(sys.argv[0]),
        "streams": {"argv": _b64(_argv_bytes(sys.orig_argv)), "cwd": _b64(os.fsencode(os.getcwd())),
                    "exit": _b64(str(child.returncode).encode()), "stdout": _b64(child.stdout),
                    "stderr": _b64(child.stderr), "file_before": to_b64(before),
                    "file_after": to_b64(after)}})
    _write_all(1, child.stdout)
    _write_all(2, child.stderr)
    if child.returncode < 0:
        import signal
        signal.signal(-child.returncode, signal.SIG_DFL)
        os.kill(os.getpid(), -child.returncode)
    os._exit(child.returncode)


def _gate_script(args):
    if isinstance(args, (str, bytes, os.PathLike)):
        args = [args]
    argv = [os.fsdecode(a) if isinstance(a, (bytes, os.PathLike)) else str(a) for a in args]
    if not argv:
        return None
    script = argv[0]
    if os.path.basename(script).startswith("python") and len(argv) > 1:
        script = argv[1]
    return argv if os.path.basename(script) in _GATES else None


def _inject_env(env):
    """A child given an explicit env still loads the recorder for the same test file."""
    env = dict(env)
    for key in _ENV_KEYS:
        if key in os.environ and key not in env:
            env[key] = os.environ[key]
    recorder = os.environ.get("FEAT2581_RECORDER")
    paths = [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p]
    if recorder and recorder not in paths:
        env["PYTHONPATH"] = os.pathsep.join([recorder, *paths])
    return env


def _install_subprocess_hooks():
    import inspect
    import subprocess
    popen = subprocess.Popen
    original_init = popen.__init__
    original_communicate = popen.communicate
    signature = inspect.signature(original_init)

    def __init__(self, *args, **kwargs):
        bound = signature.bind(self, *args, **kwargs)
        if bound.arguments.get("env") is not None:
            bound.arguments["env"] = _inject_env(bound.arguments["env"])
        argv = _gate_script(bound.arguments.get("args"))
        stdout, stderr = bound.arguments.get("stdout"), bound.arguments.get("stderr")
        captured = stdout == subprocess.PIPE and stderr in (subprocess.PIPE, subprocess.STDOUT)
        cwd = bound.arguments.get("cwd")
        self._feat2581_gate = (argv, os.fsdecode(cwd) if cwd is not None else os.getcwd()) \
            if argv and captured else None
        original_init(*bound.args, **bound.kwargs)

    def communicate(self, input=None, timeout=None):
        gate = getattr(self, "_feat2581_gate", None)
        if not gate:
            return original_communicate(self, input, timeout)
        text = self.text_mode
        saved = (self.stdin, self.stdout, self.stderr)
        codecs = {}
        if text:
            for name in ("stdin", "stdout", "stderr"):
                stream = getattr(self, name)
                if stream is not None:
                    codecs[name] = (stream.encoding, stream.errors)
                    setattr(self, name, stream.buffer)
            if isinstance(input, str):
                input = input.encode(*codecs["stdin"])
            self.text_mode = False
        try:
            out, err = original_communicate(self, input, timeout)
        finally:
            if text:
                self.text_mode = True
                self.stdin, self.stdout, self.stderr = saved
        argv, cwd = gate
        _write_record({
            "id": "gate#%s#%d" % (os.environ.get("FEAT2581_TESTFILE", "none"), _locked_counter("gate")),
            "kind": "gate",
            "streams": {"argv": _b64(_argv_bytes(argv)), "cwd": _b64(os.fsencode(cwd)),
                        "exit": _b64(str(self.returncode).encode()), "stdout": _b64(out or b""),
                        "stderr": _b64(err or b"")}})
        if text:
            out = None if out is None else self._translate_newlines(out, *codecs["stdout"])
            err = None if err is None else self._translate_newlines(err, *codecs["stderr"])
        return out, err

    popen.__init__ = __init__
    popen.communicate = communicate


def _install_tempfile():
    import tempfile
    os.makedirs(_FIXTURES, exist_ok=True)
    tag = "f%s-" % os.environ.get("FEAT2581_TESTINDEX", "x")

    class _Names:
        def __iter__(self):
            return self

        def __next__(self):
            return "%s%05d" % (tag, _locked_counter("tmp"))

    tempfile.tempdir = _FIXTURES
    tempfile._get_candidate_names = lambda: _Names()


def _install_unittest_cases():
    import unittest.result as result

    def emit(outcome, test):
        directory = os.path.join(_LEDGER, "cases")
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, _slug(os.environ["FEAT2581_TESTFILE"]) + ".txt"), "ab") as h:
            h.write(("%s %s\n" % (outcome, test.id())).encode("utf-8", "surrogateescape"))

    def wrap(name, outcome):
        original = getattr(result.TestResult, name)

        def method(self, test, *rest):
            emit(outcome, test)
            return original(self, test, *rest)
        setattr(result.TestResult, name, method)

    for name, outcome in (("addSuccess", "success"), ("addSkip", "skip"), ("addFailure", "failure"),
                          ("addError", "error"), ("addExpectedFailure", "expected_failure"),
                          ("addUnexpectedSuccess", "unexpected_success")):
        wrap(name, outcome)
    original_subtest = result.TestResult.addSubTest

    def addSubTest(self, test, subtest, outcome):
        if outcome is not None:
            emit("subtest_failure", subtest)
        return original_subtest(self, test, subtest, outcome)
    result.TestResult.addSubTest = addSubTest


def _chain_system_sitecustomize():
    """This file shadows the interpreter's own sitecustomize (Homebrew's sets sys.executable and
    adds its site-packages); run that one first so every process starts exactly as it would."""
    here = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    for entry in list(sys.path):
        if not entry or os.path.realpath(entry) == here:
            continue
        path = os.path.join(entry, "sitecustomize.py")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                code = compile(handle.read(), path, "exec")
            exec(code, {"__name__": "sitecustomize", "__file__": path, "__builtins__": __builtins__})
            return


def _main():
    _chain_system_sitecustomize()
    if not _LEDGER:
        return
    if os.environ.get("FEAT2581_CLOCK_ONLY"):
        _install_clock()
        return
    if os.path.basename(sys.argv[0] if sys.argv else "") == "feature-record.py":
        if os.environ.pop("FEAT2581_CLI_CHILD", None):
            _install_clock()
        else:
            _intercept_cli()
    _install_subprocess_hooks()
    _install_tempfile()
    if os.environ.pop("FEAT2581_TOP", None):
        _install_unittest_cases()


_main()
