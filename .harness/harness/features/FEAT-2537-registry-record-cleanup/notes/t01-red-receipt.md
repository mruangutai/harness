# T-01 red receipt — case 18 rewrite against the unmodified module (inflight_registry.py at a24eacee)

Command: `python3 tests/integration/test-inflight-registry.py` (exit 1). The case-18 lines and the summary:

```
FAIL - case18: a strict read of the v1 persona map refuses it as unreadable
FAIL - case18: a locked writer finds no claim in the v1 persona map ((None, 1))
FAIL - case18: the writer warns that the v1 persona map is treated as empty
PASS - case18: the writer leaves an empty v2 file for the v1 persona map
FAIL - case18: a strict read of the v1 empty map refuses it as unreadable
PASS - case18: a locked writer finds no claim in the v1 empty map
FAIL - case18: the writer warns that the v1 empty map is treated as empty
PASS - case18: the writer leaves an empty v2 file for the v1 empty map
PASS - case18 control: a strict read of the missing file is unchanged
PASS - case18 control: a strict read leaves the missing file as found
PASS - case18 control: a locked writer's answer for the missing file is unchanged
PASS - case18 control: a locked writer leaves the missing file as before
PASS - case18 control: a strict read of the empty file is unchanged
PASS - case18 control: a strict read leaves the empty file as found
PASS - case18 control: a locked writer's answer for the empty file is unchanged
PASS - case18 control: a locked writer leaves the empty file as before
PASS - case18 control: a strict read of the corrupt text is unchanged
PASS - case18 control: a strict read leaves the corrupt text as found
PASS - case18 control: a locked writer's answer for the corrupt text is unchanged
PASS - case18 control: a locked writer leaves the corrupt text as before
PASS - case18 control: a strict read of the non-object text is unchanged
PASS - case18 control: a strict read leaves the non-object text as found
PASS - case18 control: a locked writer's answer for the non-object text is unchanged
PASS - case18 control: a locked writer leaves the non-object text as before
PASS - case18 control: a strict read of the live v2 claim is unchanged
PASS - case18 control: a strict read leaves the live v2 claim as found
PASS - case18 control: a locked writer's answer for the live v2 claim is unchanged
PASS - case18 control: a locked writer leaves the live v2 claim as before
FAIL - 5/191 checks failed
```

The v1 direction is RED (5 assertions: strict reads return [] instead of refusing, the writer reports expired=1 for the persona map, and no warning is emitted). The writer-producible controls are GREEN (20/20). The control literals were derived beforehand by running each control against the unmodified module.
