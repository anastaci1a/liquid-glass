"""Freeze ONE independent partial source proposal before matched native replay.

Original SFfont/PSF fit used only unoccluded720. Aexterior glyph control is
heldout; no optical target pixel fitting and no geometry/material changes.
"""
import sys,json,hashlib,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
import toolbar_candidate as model
from progress_gate import error,evaluate
out=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-A-typography');proposal=out/'input-proposal';proposal.mkdir(exist_ok=True);package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());feas=json.loads((out/'feasibility.json').read_text());alpha=np.load(out/'selected-proposed-lastline-opacity-A.npy');oldpath=package/'inputs/source.png';old=np.asarray(Image.open(oldpath),float)/255;Tfull=np.asarray(Image.open(package/'inputs/target.png'),np.float32)/255;audit=json.loads(Path('/tmp/agent-toolbar-input-audit.json').read_text());co=np.array(audit['registration']['page_field']['background_coefficients']);yy,xx=np.mgrid[:1080,:1920];X=(xx-960)/960;Y=(yy-540)/540;paper=np.clip(np.stack([X**i*Y**j for i in range(5) for j in range(5-i)],axis=-1)@co,0,1)
# Known unoccluded run only. Bounds and8pxpaper taper are geometric; they do
# not use the glass target. Preceding unmodeled fragment remains old source.
box=[110,425,1350,545];taper=8.;x0,y0,x1,y1=box;dist=np.minimum.reduce([xx-x0,x1-1-xx,yy-y0,y1-1-yy]);u=np.clip(dist/taper,0,1);mask=u*u*(3-2*u);clean_run=paper*(1-alpha[...,None]);source_float=old*(1-mask[...,None])+clean_run*mask[...,None];source8=np.uint8(np.rint(np.clip(source_float,0,1)*255));Image.fromarray(source8).save(proposal/'source-typography-proposed.png');np.savez_compressed(proposal/'source-confidence.npz',typography_model_weight=mask,known_font_ink_alpha=alpha,legacy_source_preserved=mask==0)
newpath=proposal/'source-typography-proposed.png';newsha=hashlib.sha256(newpath.read_bytes()).hexdigest();oldsha=hashlib.sha256(oldpath.read_bytes()).hexdigest();q=copy.deepcopy(p);q['source_sha256']=newsha;(proposal/'incumbent-recipe-new-input.json').write_text(json.dumps(q,indent=2)+'\n');new=source8.astype(float)/255;delta=(new-old)*255;changed=np.any(source8!=np.asarray(Image.open(oldpath)),axis=2)
controls={}
for name,(a,b,c,d) in {'original_predeclared_broad_control':[60,425,480,555],'modeled_run_only_posthoc_diagnostic':[119,425,480,555]}.items():
    m=np.zeros((1080,1920),bool);m[b:d,a:c]=True
    def metric(I,mask):return {'pixels':int(mask.sum()),'RGB_RMSE_255':float(np.sqrt(np.mean(((I-Tfull)[mask]*255)**2)))}
    controls[name]={'old':metric(old,m),'proposed':metric(new,m),'old_ink':metric(old,m&(Tfull.min(2)<.4)),'proposed_ink':metric(new,m&(Tfull.min(2)<.4))}
supported=controls['original_predeclared_broad_control']['proposed']['RGB_RMSE_255']<controls['original_predeclared_broad_control']['old']['RGB_RMSE_255'];assert supported
manifest={'task':23,'type':'SEPARATE INPUT PROVENANCE PROPOSAL, NOT optical improvement','selected_font_by_720_train_only':feas['selected']['font'],'font_sha256':feas['selected']['font_sha256'],'raw_frame':'720/frame21578/PTS719.9859333333334','existing_registration_reused_no_refit':True,'fit_glass_pixels':0,'known_visible_words':'the world around us.','unknown_words_added':False,'partial_model_box_A':box,'paper_taper_px':taper,'paper_field_reused_exact_coefficients':co.tolist(),'reference_shadows_added':False,'old_source_sha256':oldsha,'proposed_source_sha256':newsha,'target_sha256':hashlib.sha256((package/'inputs/target.png').read_bytes()).hexdigest(),'output_mask_sha256':hashlib.sha256(Path('/tmp/agent-toolbar-run/frozen-masks.npz').read_bytes()).hexdigest(),'changed_pixels':int(changed.sum()),'changed_pixel_RGB_RMSE_255':float(np.sqrt(np.mean(delta[changed]**2))),'max_abs_RGB_difference_255':float(np.abs(delta).max()),'new_ink_in_historically_erased_region':feas['estimated_rectangle_new_predicted_ink_pixels'],'independent_A_outside_controls':controls,'provenance_status':'font/PSF/layout modeled from unoccluded observations; confidence NOT upgraded to directly observed RGB. No source/epoch adoption.','optical_geometry_material_shadow_glyphs_unchanged':True,'accepted_history_and_count_unchanged':True,'new_optical_passes':0,'matched_native_replay':'recipe and input/provenance frozen here BEFORE rendering below'}
(proposal/'input-proposal-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('FROZEN_INPUT_PROPOSAL',json.dumps({'newsha':newsha,'changed':int(changed.sum()),'independent_controls':controls}),flush=True)
case=p['case'];a,b,c,d=case['crop'];T=Tfull[b:d,a:c];C,cov=model.render(new,case,q,samples=4);oldC=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');oldcov=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');assert np.array_equal(cov,oldcov);masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');foreground=np.load(package/'derived-foreground.npz');shadow=model.gaussian_coverage_shadow(case,p)
def scores(C,source):
    s={}
    for name in ['glass','rim']:
        D=(C-T)[masks[name]]*255;s[name]={'rmse':float(np.sqrt(np.mean(D*D))),'pixels':int(masks[name].sum())}
    B=source[b:d,a:c];full=C*cov[...,None]+B*(1-shadow[...,None])*(1-cov[...,None]);s['shadow']=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
    for layer in p['foreground_layers']:
        aa=foreground[layer['name']][...,None];full=full*(1-aa)+np.array(layer['color'])*aa
    fg={}
    for layer in p['foreground_layers']:
        x0,y0,x1,y1=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[y0-b:y1-b,x0-a:x1-a]-T[y0-b:y1-b,x0-a:x1-a])**2))*255)
    return s,fg,full
before=json.loads((package/'primary-verification.json').read_text())['candidate'];oldscore,oldfg,_=scores(oldC,old);newscore,newfg,full=scores(C,new);new_epoch=hashlib.sha256(json.dumps({'accepted_epoch':before['epoch'],'proposed_input_sha256':newsha,'renderer_unchanged':True},sort_keys=True).encode()).hexdigest();state={'epoch':new_epoch,'observations':{'A':newscore}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
np.save(proposal/'material.npy',C);np.save(proposal/'alpha.npy',cov);np.save(proposal/'complete.npy',full);Image.fromarray(np.uint8(np.rint(np.clip(full,0,1)*255))).save(proposal/'incumbent-new-input-preview.png');report={'old_accepted_epoch':before['epoch'],'proposed_input_comparison_epoch':new_epoch,'old_source_E':error(oldscore),'proposed_source_E':error(newscore),'old_scores':oldscore,'new_scores':newscore,'old_foreground':oldfg,'new_foreground':newfg,'unchanged_optical_recipe_except_source_hash':True,'coverage_exact':True,'new_native_incumbent_reevaluation_renders':1,'cached_accepted_incumbent_rerenders':0,'progress_gate_expected_epoch_refusal':gate,'optical_passes':0,'source_adoption':'PENDING primary independent provenance/replay review. Accepted original source/epoch/history/count untouched.','limits':'Improved independent exterior text validation is input evidence; any changed glass/native score is NEVER an optical improvement or automatic epoch reset. No word/PSF/pose/color adjusted after this replay.'};(proposal/'matched-incumbent-reevaluation.json').write_text(json.dumps(report,indent=2)+'\n');print('INPUT_REEVALUATION',json.dumps(report),flush=True)
