- 2026-08-14: FEAT-20 cycle 2. My legacy pattern for check-state.sh was "the join of H then
  features then *", read off the commonest site. 15 of 15 discovery sites match
  `os.path.join(H, "features"`; only 13 carry the trailing `"*"` — :95 (os.listdir) and :97
  (feature.json) do not. A detector shipped on the wildcard-shaped pattern would have reported
  CLEAN on a tree with two dead discovery sites. The pattern must be the weakest fragment every
  stale site necessarily contains, greped against the real file before the row is written.
- 2026-08-14: T-04's mandated-literal grep was case-sensitive while the substance block I told the
  documentor to reproduce spelled the same phrase in caps. My discriminating-ness pre-check used
  `grep -ic`, which hid the collision — the check would have gone red on correct work.
