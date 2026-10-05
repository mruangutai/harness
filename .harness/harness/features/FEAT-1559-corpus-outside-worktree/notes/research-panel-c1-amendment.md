# Reproducible panel-c1 planning amendment; Python source, not implementation.
import pathlib, subprocess, yaml
root=pathlib.Path('/Users/molchairuangutai/GitHub/harness')
wt=root/'.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree'
f=wt/'.harness/harness/features/FEAT-1559-corpus-outside-worktree'
p=f/'plan.yaml'
plan=yaml.safe_load(p.read_text())
for t in plan['tasks']:
    if t['id']=='T-01':
        t['intent'] += '\nSafety ruling required before execution: absent tracked paths alone cannot prove sparse-induced damage. Ambiguous deletions and mixed genuine dirt retain exit 8 and complete nonmutation. Do not whitelist deletions. Mandatory hidden-feature repair requires trustworthy operation-bound provenance or explicit operator scope revision; the current unconditional dirty-refusal and clean-after-merge promises conflict. Fresh IDs absent from all artifact segments remain explicit absent-record refusals.\n'
    if t['id']=='T-04':
        t['intent'] += '\nCreation-order ruling required: cmd_create discards the artifact segment and invokes git worktree add without creating the record first. Test an absent-new-ID case: diagnose absent record, return hook exit 0, and never assert convergence. Record-bearing creation cases retain convergence. New-ID convergence cannot be promised under the unchanged excluded-creator contract. This and dirty-deletion provenance are signature-blocking rulings, not implementation discretion.\n'
    if t['id']=='T-05':
        a=t['intent'].index('Add collected non-regression tests')
        b=t['intent'].index('Add read-only real-owner',a)
        t['intent']=t['intent'][:a]+'Record immutable pre_change_sha-to-review_sha whole-feature diff and historical owner-byte comparison once in the non-regression receipt: exact endpoints, raw exits and explicit unavailable-endpoint skips. Do not permanently collect frozen assertions. Keep collected fresh synthetic-clone directory retention, normalized finding sets against recorded baseline, and live conversion-manifest validation. No moving-ref baseline substitutes.\n\n'+t['intent'][b:]
        t['intent'] += '\nFull-suite subject is a disposable ordinary full non-linked clone at immutable review_sha, not the synthetic fixture. Run registered unit and integration kinds from harness.json and record exact clone path, cwd/root, checkout class, HEAD, commands, raw exits and timings. Preserve CI, depth and runner selection.\n'
    if t['id']=='T-06':
        t['intent'] += '\nchange_type docs deliberately classifies the committed receipt-only diff, not host operational risk. Conversion remains main-session-direct with all dirty-state nonmutation safeguards.\n'
q=f/'notes/research-panel-c1-proposal.md'
q.write_text(yaml.safe_dump({'decisions':plan['decisions'],'tasks':plan['tasks']},sort_keys=False))
cmd=['python3',str(root/'.agents/skills/harness/bin/plan-merge.py'),'apply','--file',str(p),'--proposal',str(q)]
r=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
text='COMMAND: '+' '.join(cmd)+'\n'+r.stdout+'EXIT: '+str(r.returncode)+'\n'
(f/'notes/research-panel-c1-apply-receipt.md').write_text(text)
print(text,end='')
if 'APPROVAL-RESET:' in r.stdout:
    cmd=['python3',str(root/'.agents/skills/harness/bin/gh-sync.py'),'sync',str(f)]
    s=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    text='COMMAND: '+' '.join(cmd)+'\n'+s.stdout+'EXIT: '+str(s.returncode)+'\n'
    with (f/'notes/research-panel-c1-apply-receipt.md').open('a') as out: out.write(text)
    print(text,end='')
raise SystemExit(r.returncode)
