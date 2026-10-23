from pathlib import Path
import json,subprocess,hashlib
repo=Path('/workspace/research-docs-publish')
root=repo.parent/'evidence/dark-glass-lab/extended'
replay=root/'music-home-vector-corrected-replay-21'
for n in ['a','b']:
 v=json.loads((replay/n/'final/verification.json').read_text())
 assert v['output_scale']==4 and v['frames']==120 and v['motion_support']['actual_native_px']>0
 assert 'exterior_context' in v['motion_support']
 assert v['gif']['master_relative_scale']==1 and v['files']['motion.gif']['bytes']<10_000_000
 assert (replay/n/'final/gif-qa.json').exists()
subprocess.run(['node',str(root/'paired_finalize.cjs'),'music-home-vector','music-home-vector-corrected-replay-21','--stage-only'],cwd=repo,check=True)
public=repo/'docs/liquid-glass/experiments/reconstruction'
p=public/'home-gallery-progress.json';r=json.loads(p.read_text())
r['status']='Final paired study; corrected single-to-paired boundary and21 native paired passes verified'
r['initial_historical_passes']=12;r['additional_single_passes']=10;r['total_initial_passes']=22
r['limits']='Two observed backgrounds in one Apple video. Context-dependent lighting is tested over their narrow brightness range; unrecovered presentation pixels remain estimates. Independent replay/source/media reports are stored with the paired study.'
r['media_code_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
for n in ['a','b']:
 v=json.loads((replay/n/'final/verification.json').read_text());r.setdefault('final_motion',{})[n]=dict(axis=v['motion_support']['axis'],travel_over_L=v['travel_over_L'],output_scale=v['output_scale'],gif=v['gif'],video_sha256=v['files']['motion.mp4']['sha256'])
p.write_text(json.dumps(r,indent=2)+'\n')
path=root/'progress.json';p=json.loads(path.read_text());p['finished']['music-home-vector'].update(initial_historical_passes=12,additional_single_passes=10,total_initial_passes=22,boundary_verified=True,pr=427);p['active']='active-segmented-selector';p['branch']='research/active-segmented-selector-222';path.write_text(json.dumps(p,indent=2)+'\n')
subprocess.run([str(repo.parent/'fix-permissions.sh'),str(public/'studies/music-home-vector/paired'),str(public/'home-gallery-progress.json'),str(root/'progress.json'),str(replay)],check=True)
