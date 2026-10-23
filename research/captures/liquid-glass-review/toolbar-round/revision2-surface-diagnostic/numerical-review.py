"""Saved-field numerical review plus NEW selected-point FD refinement only."""
import importlib.util,json
import numpy as np
s=importlib.util.spec_from_file_location('c','/tmp/agent-toolbar-surface-compatibility.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);d=c.d
out=d.out;grid=np.load(out/'compatibility-0.02-fields.npz');sd=d.empirical.boundary(grid['x'],grid['y'],d.p)[0]
near=grid['inside']&(sd>=-.0002)
x=np.array([1.5,1.52,1.,.5]);y=np.array([.88,.88,.5,.5]);samples=[]
for h in [1e-5,1e-6]:
    v,cv,M,K=c.derivatives(d.accepted_v,x,y,h)
    for i in range(len(x)):
        samples.append({'x':float(x[i]),'y':float(y[i]),'finite_h':h,'signed_boundary_L':float(d.empirical.boundary(x,y,d.p)[0][i]),'curl':float(cv[i]),'M':float(M[i]),'K':float(K[i]),'rho':float(K[i]/cv[i]) if abs(cv[i])>1e-14 else None,'necessary_margin_c_times_K_minus_Mc':float(cv[i]*(K[i]-M[i]*cv[i]))})
fine=json.loads((out/'fine-04.json').read_text())['configs'][4];rk=json.loads((out/'fine-04-RK01.json').read_text())['configs'][0];sp=json.loads((out/'spatial-02-RK01.json').read_text())['configs'][0]
report={'new_selected_point_derivative_refinement':samples,'saved_grid_02_boundary_crossing_diagnostics':{'near_boundary_points':int(near.sum()),'robust_classified_near_boundary':int((near&grid['robust']).sum()),'limits':'Boundary switch F=identity outside footprint can pollute central derivatives. All6near-boundary nodes are unresolved/notrobust, not used to argue exact surface incompatibility.'},'representative_n1_5_g2':{'path_height_RMS_L_grid04_RK02':fine['path_height_difference_L']['rms'],'path_height_RMS_L_grid04_RK01':rk['path_height_difference_L']['rms'],'path_height_RMS_L_grid02_RK01':sp['path_height_difference_L']['rms'],'forward_map_vector_RMS_px_grid04':[p['forward_map_vector_error_native_px'].get('rms') for p in rk['paths']],'forward_map_vector_RMS_px_grid02':[p['forward_map_vector_error_native_px'].get('rms') for p in sp['paths']]},'limits':['Path mismatch stable under RK/spatial refinement, whereas forward-map stencil errors are NOT spatially converged; no best-approximation/lower-bound claim','Required-clearance PDE residual is ill-conditioned near small curl and branch-transition sets; retain full fields/threshold sensitivity, not a recovered h','Wrong-branch necessary condition is numerical evidence for exact-map mismatch in this specified camera/interface family, not all Apple surfaces or all close approximations'],'new_optical_renders':0}
(out/'numerical-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
