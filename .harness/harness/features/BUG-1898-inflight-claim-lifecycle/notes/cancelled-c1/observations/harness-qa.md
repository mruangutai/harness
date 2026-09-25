# Observations — harness-qa — BUG-1898-inflight-claim-lifecycle

- 2026-09-24: The baseline 0aa337f1 validator suite can release root-seeded sentinels even though its BUG-1898 cases use throwaway roots; measure the real wrapper plus baseline suite before deeming its sentinel binding disconnected.
