from pathlib import Path
import json,sys
B=Path(__file__).parent;P=B/sys.argv[1];r=json.loads((P/'result.json').read_text());v=json.loads((P/'verification.json').read_text());assert v['passed'];p=json.loads((P/'protocol.json').read_text());recipe=json.loads((P/'final-recipe.json').read_text());choices=json.loads((P/'choices.json').read_text())
text='# '+sys.argv[1].title()+' complete cycle\n\nOwn arithmetic replay and source-coordinate spot checks pass. Original masks and partial cohorts remain fixed. This is a working comparison, not a full-fidelity acceptance. Dispersion is excluded.\n\n'
text+='| Stage | Recorded decision |\n| --- | --- |\n| Geometry / registration | '+p['native']+'; corrected common center and independent position arrays |\n'
for name,item in choices.items():text+='| '+name+' | '+item['chosen']+'; original failures retained |\n'
text+='| Own verification | Four completed composites, metrics, source-coordinate parity and exact angular-gap contribution |\n\n'
text+='| Reference | E | SSIM | Partial RMSE | Failed starting100 guards |\n| --- | ---: | ---: | ---: | --- |\n'
for x in r['records']:
 s=x['scores'];fails=', '.join(k for k,y in x['starting100_guards'].items() if not y) or 'None';text+=f"| {x['member']} {x['reference'].upper()} | {s['E']:.5f} | {s['ssim']:.6f} | {s['partial']['RMSE']:.5f} | {fails} |\n"
text+='\nExpanded-only rim training selects the outline. Compact uses identical settings. All other stage rankings use equal-reference training cohorts, excluding held pixels. Original guards remain evaluation evidence.\n\n'
text+='[Recipe](final-recipe.json), [all stage scores](all-metrics.json), [source gates](blur-source-FIRST.json), [integration](integration.json), [own verification](verification.json), [fixed diagnostics](fixed-diagnostics.json) and [ledger](ledger.json) retain the detailed evidence.\n\n'
text+='Outline integration reports a successive-order difference, not a certified global error bound. Exterior shadow affects clear subrays only. The source mosaic and annular scene remain conditional; later reflected power is unassigned.\n'
if sys.argv[1]=='pass3':text=text.replace('Expanded-only rim training selects the outline.', 'Fixed expanded upper/lower peak training selects the outline; these training pixels exclude held samples.')
(P/'README.md').write_text(text)
