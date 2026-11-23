set -eu
export HARNESS_PROJECT_DIR="$PWD"
python3 - <<'CHECK'
import ast, pathlib, yaml
workflow = pathlib.Path('.github/workflows/tests.yml').read_text(); checks = []
steps = [step for job in yaml.safe_load(workflow)['jobs'].values() for step in job.get('steps', [])]
for name in ('Unit suite', 'Validate feature execution state', 'Plan-route gate', 'Canonical-reader audit', 'Instruction-path gate', 'Layout gate', 'Repository-state gate', 'Integration suite (shard ${{ matrix.shard }}/4)', 'Validate shard completeness'):
    found = [step.get('env', {}) for step in steps if step.get('name') == name]
    checks.append((name, len(found) == 1 and found[0].get('HARNESS_PROJECT_DIR') == '${{ github.workspace }}' and 'CLAUDE_PROJECT_DIR' not in found[0]))
guidance = [line for line in workflow.splitlines() if 'Discovery did not run' in line and 'Check ' in line]
checks.append(('two guidance lines', len(guidance) == 2)); checks.extend((line.strip(), 'Check HARNESS_PROJECT_DIR' in line and 'CLAUDE_PROJECT_DIR' not in line) for line in guidance)
for path, target in (('tests/integration/test-harness-yaml.py', 'REPO_ROOT'), ('tests/integration/test-validate-feature-json.py', 'REPO_ROOT'), ('tests/unit/test-harness-yaml-corpus.py', 'REPO'), ('tests/unit/test-team-catalog.py', 'REPO'), ('tests/unit/test-plan-depends-on.py', '_REPO')):
    nodes = [node.value for node in ast.parse(pathlib.Path(path).read_text()).body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == target for t in node.targets)]
    keys = [n.args[0].value for node in nodes for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'get' and n.args and isinstance(n.args[0], ast.Constant)]
    checks.append((path, len(nodes) == 1 and 'HARNESS_PROJECT_DIR' in keys and 'CLAUDE_PROJECT_DIR' not in keys))
for name, passed in checks: print('OK' if passed else 'FAIL', name)
assert all(passed for _, passed in checks)
CHECK
python3 tests/integration/test-harness-yaml.py
python3 tests/integration/test-validate-feature-json.py
python3 tests/unit/test-harness-yaml-corpus.py
python3 tests/unit/test-team-catalog.py
python3 tests/unit/test-plan-depends-on.py

