// Run only after the20 single passes and the first verified paired experiment.
const fs=require('fs'),cp=require('child_process');
const repo='/mnt/user/live/projects/localica/localica-docs-publish',root=repo+'/../localica-feedback/dark-glass-lab/extended',id='active-segmented-selector';
const r=JSON.parse(fs.readFileSync(root+'/'+id+'/paired/pass-01.json'));
const single=JSON.parse(fs.readFileSync(repo+'/docs/liquid-glass/experiments/reconstruction/studies/'+id+'/accepted.json'));
if(r.previous.scores[0].loss>single.scores.loss+1e-8||r.previous.scores[0].glass.rmse>single.scores.glass.rmse+1e-8)throw Error('First paired baseline regresses the retained single');
const file=repo+'/docs/liquid-glass/reconstruction.md';let s=fs.readFileSync(file,'utf8'),start=s.indexOf('## Active segmented selector\n'),end=s.indexOf('\n## Scores\n',start);if(start<0||end<0)throw Error('Missing section');
const section=`## Active segmented selector

Frames A/B: 16.4 / 16.35 seconds in Apple's Details video. These 4× stills show paired pass 1, following at least 20 initial experiments. B was selected by silhouette dimensions after the original16.5s frame proved to have a different interaction shape; this is a posthoc matched-state test, not blind validation. One normalized optical map and material are shared across the two observed positions; the initial paired state protects the retained first-reference result.

[![Active segmented selector, background A: Apple left, reconstruction right](assets/study-active-segmented-selector-progress-a.png)](assets/study-active-segmented-selector-progress-a.png)

[![Active segmented selector, background B: Apple left, reconstruction right](assets/study-active-segmented-selector-progress-b.png)](assets/study-active-segmented-selector-progress-b.png)

- The incident texture uses solid SF outlines with selected red text; the exterior retains gray text. Hidden track geometry, font choice, pre-refraction recoloring and layout transfer remain explicit estimates, not photographic recovery or proof of Apple's pipeline.
- Earlier source estimates are archived and excluded: [track registration](experiments/reconstruction/studies/active-segmented-selector/invalid-track-registration/status.json), [caption proxy](experiments/reconstruction/studies/active-segmented-selector/invalid-lensed-caption-proxy/status.json).
- [Shared recipe and paired experiments](experiments/reconstruction/studies/active-segmented-selector/paired/accepted.json) · [Current measurements and source limits](experiments/reconstruction/segmented-gallery-progress.json) · [Initial experiments](experiments/reconstruction/studies/active-segmented-selector/passes.jsonl). Paired calibration and final motion are in progress; native score masks and source hashes remain fixed.
`;
s=s.slice(0,start)+section+s.slice(end);
const marker='| Active switch, pass 24 |';const pos=s.indexOf(marker);if(pos<0)throw Error('Missing score insertion point');const at=s.indexOf('\n',pos)+1;
const [a,b]=r.current.scores;const row=`| Active segmented selector, pass 1 | ${a.loss.toFixed(3)} / ${b.loss.toFixed(3)} | ${a.glass.rmse.toFixed(3)} / ${b.glass.rmse.toFixed(3)} | 20 / 1 | In progress |\n`;
s=s.slice(0,at)+row+s.slice(at);fs.writeFileSync(file,s);
const test=repo+'/docs/liquid-glass/experiments/reconstruction/comparison.cjs';let js=fs.readFileSync(test,'utf8');js=js.replace(".count(),18,'Enhance every primary A/B pair'", ".count(),19,'Enhance every primary A/B pair'").replace('PASS18 primary pairs','PASS19 primary pairs');fs.writeFileSync(test,js);
cp.execFileSync(repo+'/../fix-permissions.sh',[file,test],{stdio:'inherit'});
