# T-04 receipt — Install pinned Chromium

Branch: `feat/FEAT-1821-ui-verification-lane`

Changed path: `.github/workflows/tests.yml`

Fail-first exact signed assertion (before edit), exit `1`:

```sh
python3 -c "import pathlib,yaml; d=yaml.safe_load(pathlib.Path('.github/workflows/tests.yml').read_text()); steps=[s for j in d['jobs'].values() for s in j.get('steps',[])]; i=next(i for i,s in enumerate(steps) if s.get('name')=='Install the dashboard Chromium'); s=steps[i]; assert steps[i-1].get('run')=='npm ci --prefix .claude/skills/harness/bin/dashboard/client' and s.get('working-directory')=='.claude/skills/harness/bin/dashboard/client' and s.get('run')=='npx playwright install --with-deps chromium'"
```

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
StopIteration
```

Post-edit exact signed assertion, exit `0` (no output):

```sh
python3 -c "import pathlib,yaml; d=yaml.safe_load(pathlib.Path('.github/workflows/tests.yml').read_text()); steps=[s for j in d['jobs'].values() for s in j.get('steps',[])]; i=next(i for i,s in enumerate(steps) if s.get('name')=='Install the dashboard Chromium'); s=steps[i]; assert steps[i-1].get('run')=='npm ci --prefix .claude/skills/harness/bin/dashboard/client' and s.get('working-directory')=='.claude/skills/harness/bin/dashboard/client' and s.get('run')=='npx playwright install --with-deps chromium'"
```

Scoped `git diff --check -- .github/workflows/tests.yml`, diff, and status passed: the only workflow change is the required three-line Chromium-install step plus surrounding blank lines immediately after dashboard client `npm ci`.

No browser download, npm install, UI lane, formatter, linter, project-wide test, or build ran.
