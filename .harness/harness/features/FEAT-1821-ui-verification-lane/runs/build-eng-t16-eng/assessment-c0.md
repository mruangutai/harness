# T-16 cycle 0 assessment

The reporter behavior and scoped probe pass, but the signed interface task is incomplete: `ui-manifest.ts` exports `traced_check_ids` on `UiManifest` while the optional per-record `trace` contract remains a private `CheckResult` declaration in `ui-reporter.ts`. Move/export the result-record trace shape through `ui-manifest.ts` and consume it in the reporter, without changing behavior or scope. Re-run only the signed T-16 probe and write the cycle-1 receipt.
