# Observations - harness-backend-dev

- 2026-08-23: never mutate gh-sync.py/test-gh-sync.py while a background test-gh-sync.py run against them is in flight (T-04 mutant test) — each test case shells out to gh-sync.py fresh from disk per subprocess, so an edit mid-run silently contaminates whichever cases execute after the edit lands. Wait for the run to fully finish (check via the background-task notification, not by polling the log file — it is block-buffered and shows nothing until the process exits) before editing again.
