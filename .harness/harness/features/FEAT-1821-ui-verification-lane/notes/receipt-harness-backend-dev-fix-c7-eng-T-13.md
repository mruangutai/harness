# T-13 receipt — fail-closed reporter producer

The reporter now marks the bundle summary failed when any recorded execution has emitted errors; inspection records retain the required `evidence` record status so the independent gate can explicitly refuse its errors as an inspection setup failure. Schema `harness-ui-results/1` and all listed/applicable/observed/missing accounting are unchanged.

The existing `incomplete accounting` top-level probe now also constructs a real inspection record with deterministic valid WebP attachments and `inspection setup failure` in its real Playwright result errors. It asserts reporter `summary.status: failed`, record error text, and that the real Python gate exits nonzero with text naming the inspection setup failure. The seven named top-level cases are unchanged.

## Signed verification

Command:

```sh
node --experimental-strip-types --test .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts
```

Verbatim output:

```text
✔ missing record (95.710917ms)
✔ duplicate (134.19625ms)
✔ mismatched title (89.483708ms)
✔ empty WebP (91.230291ms)
Traceback (most recent call last):
  File "/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ui-reporter-parser-hpEzY9/.claude/skills/harness/bin/ui_contract.py", line 467, in <module>
    sys.exit(main())
             ~~~~^^
  File "/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ui-reporter-parser-hpEzY9/.claude/skills/harness/bin/ui_contract.py", line 463, in main
    return _run_check(args) if args.cmd == "check" else _run_gate(args)
           ~~~~~~~~~~^^^^^^
  File "/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ui-reporter-parser-hpEzY9/.claude/skills/harness/bin/ui_contract.py", line 443, in _run_check
    manifest = load_manifest(args.design, args.require_predicates, args.require_inspection_evidence, args.expect)
  File "/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ui-reporter-parser-hpEzY9/.claude/skills/harness/bin/ui_contract.py", line 145, in load_manifest
    lines = pathlib.Path(design).read_text(encoding="utf-8").splitlines()
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/pathlib/__init__.py", line 787, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/pathlib/__init__.py", line 771, in open
    return io.open(self, mode, buffering, encoding, errors=errors, newline=newline) as f:
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ui-reporter-parser-hpEzY9/.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md'
✔ parser error (144.815084ms)
✔ reporter error (89.448334ms)
✔ incomplete accounting (178.789625ms)
ℹ tests 7
ℹ suites 0
ℹ pass 7
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 936.94925
```

The parser-error fixture intentionally imports a copied reporter with no DESIGN.md; its Python traceback is expected fixture behavior. The command exits 0 with all seven named probes passing (7/7).

Focused inspection proof is asserted inside `incomplete accounting`: emitted `summary.status` is `failed`; the real record carries `inspection setup failure`; and the real `ui_contract.py gate` process has a nonzero exit and output matching `inspection setup failure`.
