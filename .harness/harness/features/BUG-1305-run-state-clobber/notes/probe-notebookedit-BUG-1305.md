# NotebookEdit route probe — BUG-1305

The literal `NotebookEdit` route is absent from this OMP host. This is host absence, not an
invocation-time refusal: no call named `NotebookEdit` can be constructed, so no such payload can
reach Harness.

route_reachable: no

Command issued:

```text
omp --help
```

Verbatim output (version line and the complete `Available Tools` section):

```text
omp v18.1.11
Available Tools (default-enabled unless noted):
  read          - Read file contents
  bash          - Execute bash commands
  edit          - Edit files with find/replace
  write         - Write files (creates/overwrites)
  grep          - Search file contents
  glob          - Find files by glob pattern
  lsp           - Language server protocol (code intelligence)
  python        - Execute Python code (requires: omp setup python)
  notebook      - Edit Jupyter notebooks
  browser       - Browser automation (Puppeteer)
  computer      - Native host desktop capture and input (disabled by default)
  task          - Launch sub-agents for parallel tasks
  todo          - Manage todo/task lists
  web_search    - Search the web
  ask           - Ask user questions (interactive mode only)
```

The `notebook` row is present and has not been omitted, but it is a different tool name; there is
no `NotebookEdit` entry in the host inventory.

guard_fires: n_a

This follows from `route_reachable: no` under T-11 step 1: the absent route cannot deliver a call
to the guard, so the probe stops before asking whether that guard fires.

Command issued:

```text
omp --help
```

Verbatim output (version line and the complete `Available Tools` section):

```text
omp v18.1.11
Available Tools (default-enabled unless noted):
  read          - Read file contents
  bash          - Execute bash commands
  edit          - Edit files with find/replace
  write         - Write files (creates/overwrites)
  grep          - Search file contents
  glob          - Find files by glob pattern
  lsp           - Language server protocol (code intelligence)
  python        - Execute Python code (requires: omp setup python)
  notebook      - Edit Jupyter notebooks
  browser       - Browser automation (Puppeteer)
  computer      - Native host desktop capture and input (disabled by default)
  task          - Launch sub-agents for parallel tasks
  todo          - Manage todo/task lists
  web_search    - Search the web
  ask           - Ask user questions (interactive mode only)
```

The statement at `check-domain.sh:1931` that POST sees `NotebookEdit` is vacuous on this host:
the host cannot emit that tool name. No `## Reported` section is owed because the measured result
is an absent route, not a reachable unguarded route.
