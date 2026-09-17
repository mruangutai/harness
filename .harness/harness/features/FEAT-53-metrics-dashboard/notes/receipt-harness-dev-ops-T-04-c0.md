# T-04 receipt

Client toolchain pins are installed and committed. Resolved `@astryxdesign/core`: `0.6.2`. Implementation commit: `37281189e744918c5ed4a84ffbacf69f81fb7c96` (`[harness:t-04] Pin dashboard client toolchain`).

## Fail-first proof

Run from the FEAT-53 worktree root before implementation:

```sh
python3 -c "import json,re;p=json.load(open('.claude/skills/harness/bin/dashboard/client/package.json'));d=dict(p.get('dependencies',{}),**p.get('devDependencies',{}));missing=[k for k in ['react','react-dom','@astryxdesign/core','@tanstack/react-router','@tanstack/react-query','@tanstack/charts','d3-scale','vite','typescript','vitest','jsdom','@testing-library/react'] if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+',str(d.get(k,'')))];assert not missing, missing;assert p.get('scripts',{}).get('test')=='vitest run', p.get('scripts')" && python3 -c "import pathlib;t=pathlib.Path('.claude/skills/harness/bin/dashboard/client/vitest.config.ts').read_text();assert 'jsdom' in t;assert 'vitest.setup.ts' in t;s=pathlib.Path('.claude/skills/harness/bin/dashboard/client/vitest.setup.ts').read_text();assert 'ResizeObserver' in s"
```

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import json,re;p=json.load(open('.claude/skills/harness/bin/dashboard/client/package.json'));d=dict(p.get('dependencies',{}),**p.get('devDependencies',{}));missing=[k for k in ['react','react-dom','@astryxdesign/core','@tanstack/react-router','@tanstack/react-query','@tanstack/charts','d3-scale','vite','typescript','vitest','jsdom','@testing-library/react'] if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+',str(d.get(k,'')))];assert not missing, missing;assert p.get('scripts',{}).get('test')=='vitest run', p.get('scripts')
                               ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '.claude/skills/harness/bin/dashboard/client/package.json'
```

Exit status: 1.

## Signed verification after implementation

Run verbatim from the FEAT-53 worktree root:

```sh
python3 -c "import json,re;p=json.load(open('.claude/skills/harness/bin/dashboard/client/package.json'));d=dict(p.get('dependencies',{}),**p.get('devDependencies',{}));missing=[k for k in ['react','react-dom','@astryxdesign/core','@tanstack/react-router','@tanstack/react-query','@tanstack/charts','d3-scale','vite','typescript','vitest','jsdom','@testing-library/react'] if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+',str(d.get(k,'')))];assert not missing, missing;assert p.get('scripts',{}).get('test')=='vitest run', p.get('scripts')" && python3 -c "import pathlib;t=pathlib.Path('.claude/skills/harness/bin/dashboard/client/vitest.config.ts').read_text();assert 'jsdom' in t;assert 'vitest.setup.ts' in t;s=pathlib.Path('.claude/skills/harness/bin/dashboard/client/vitest.setup.ts').read_text();assert 'ResizeObserver' in s"
```

```text
(no output)
```

Exit status: 0.

## Installation proof

`npm install` completed successfully: `added 162 packages in 13s`.

```text
harness-metrics-client@ /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.claude/skills/harness/bin/dashboard/client
└── @astryxdesign/core@0.6.2
```

Eligible amendments: none.
