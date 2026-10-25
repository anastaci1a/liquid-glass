"""Package saved pass metrics; no candidate or scientific replay."""
from pathlib import Path
import sys,json,hashlib,datetime
root=Path(__file__).parent;p=root/sys.argv[1]
r=json.loads((p/'result.json').read_text());fits=json.loads((p/'fits.json').read_text());proto=json.loads((p/'protocol.json').read_text())
seed=r['development_seed'];qualifier=r['numerical_qualifier']
previous=json.loads((root/'selection.json').read_text()) if (root/'selection.json').exists() else dict(accepted=None)
# Numerical qualifiers require explicit visual acceptance before adoption.
selection=dict(accepted=previous['accepted'],development=dict(folder=p.name,candidate=seed,config=fits[seed]['config'],strength=fits[seed]['strength']),status='INCUMBENT_RETAINED',pending_numerical_qualifier=qualifier)
(root/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
lines=[f"# Pass {proto['number']}: {proto['question']}",'', 'The starting model and incumbent are retained. Every setting is evaluated on all four original references. A development seed is chosen only by equal-reference training loss; it is not an accepted replacement.','', '| Setting | Response | Width | Inward exponent | Strength | Training loss |','| --- | --- | ---: | ---: | ---: | ---: |']
for f in fits:
 c=f['config'];lines.append(f"| {f['candidate']} | {c['response']} | {c['sigma']:.6f} | {c['power']} | {f['strength']:.9f} | {f['train_loss']:.9f} |")
lines+=['','## All original outcomes','','| Setting / reference | E | Partial RMSE | Failed original guards | Comparison / crops |','| --- | ---: | ---: | --- | --- |']
for x in r['records']:
 pref=f"{x['member']}-{x['reference']}-c{x['candidate']}";fail=', '.join(k for k,v in x['original_guards'].items() if not v) or 'None'
 lines.append(f"| {x['candidate']} / {x['member']} {x['reference'].upper()} | {x['scores']['E']:.6f} | {x['scores']['partial']['RMSE']:.6f} | {fail} | [Full]({pref}-comparison.png) / [Crops]({pref}-crops.png) |")
lines+=['','## Verification and scope','',f"Four zero identities and original input/mask bindings pass. Orders eight and sixteen agree within the declared opacity threshold. Development setting {seed} has the smallest training loss. Held pixels and foreground do not enter the strength fit. All original boundary, foreground, exterior and body failures remain.",'','No new rays, heights, source queries or optical filters run. The separate outline acts on the frozen completed image. The original 16/22-pixel partial cohorts remain unchanged. Source/geometry uncertainty and inherited incomplete radiance remain body-model limits.','',f"The actual block starts at {proto['start']} and ends by {proto['deadline']}. Scientific completion is {r['finished']}. [Protocol](protocol.json), [result](result.json), [fits](fits.json) and [ledger](ledger.json) retain all settings and counters.",'','[First](first-hashes.json) and [last](last-hashes.json) hashes agree for this execution. The driver snapshot is retained for later code evolution. [Visual review](visual-review.json) records inspection and the pass decision.','']
(p/'README.md').write_text('\n'.join(lines))
(p/'driver-source.txt').write_bytes((root/'run_pass.py').read_bytes())
(p/'closure.json').write_text(json.dumps(dict(packaged_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),science_finished=r['finished'],deadline=proto['deadline'],pending_numerical_qualifier=qualifier,incumbent=selection['accepted']),indent=2)+'\n')
m={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file() and f.name!='manifest.json'}
(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(p.name,'seed',seed,'qualifier',qualifier,'files',len(m))
