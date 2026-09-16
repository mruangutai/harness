# Observations - harness-backend-dev

- 2026-09-06: T-02 (BUG-1309) — routing skip()'s new build_entry recording through save_recorded crashed the pre-existing not_onboarded test (feature.json absent -> save_recorded's absent-file refusal replaced the SKIP message). Guarded skip()'s record attempt on os.path.isfile(feature.json) first. Any future 'record on exit' hook added to skip()/die()/refuse() needs the same guard whenever feature.json's existence is not already guaranteed.
