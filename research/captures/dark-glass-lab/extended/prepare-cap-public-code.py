from pathlib import Path
import shutil
src=Path('/workspace/docs/liquid-glass/experiments/reconstruction');out=Path('/tmp/cap-profile-public-code');out.mkdir(exist_ok=True)
for pattern in ['*.py','*.json']:
 for p in src.glob(pattern):shutil.copy2(p,out/p.name)
p=out/'extended_fit.py';s=p.read_text();needle="        X+=p.get('shape_dx',0);Y+=p.get('shape_dy',0)\n";assert s.count(needle)==1
addition='''        profile=p.get('cap_edge_profile')
        if profile is not None:
            coefficients=np.asarray(profile,dtype=float)
            if not p['spline'] or coefficients.ndim!=1 or not 1<=len(coefficients)<=7 or not np.isfinite(coefficients).all():
                raise ValueError('Cap-depth profile needs one to seven finite spline coefficients')
            # Shape-relative depth/orientation expansion of the normal map.
            # It does not identify a physical solid or alter the silhouette.
            extra=cap_weight*(basis[...,:len(coefficients)]@coefficients)
            X-=extra*nx;Y-=extra*ny
'''
s=s.replace(needle,needle+addition);p.write_text(s)
shutil.copy2('/evidence/extended/test_cap_depth_profile.py',out/'test_cap_depth_profile.py')
p=out/'revision_replay.py';s=p.read_text();needle='def transmission_signature(study,p,scale):';assert s.count(needle)==1
s=s.replace(needle,'''def ray_implementation_digest():
    """Invalidate stored ray proofs when their generator/checker changes."""
    root=Path(__file__).parent
    names=['extended_fit.py','render.py','curvature.py','crowned_footprint.py',
           'chromatic_transmission.py','source_support.py','revision_replay.py']
    return hashlib.sha256(b''.join(name.encode()+b'\\0'+(root/name).read_bytes() for name in names)).hexdigest()


'''+needle).replace('payload=dict(case=study.case,parameters=optical,scale=scale)','payload=dict(case=study.case,parameters=optical,scale=scale,implementation=ray_implementation_digest())');p.write_text(s)
p=out/'test_revision_replay.py';s=p.read_text().replace('import unittest','import unittest\nfrom unittest.mock import patch',1);needle="\n\nif __name__=='__main__':unittest.main()";test='''
    def test_changed_ray_implementation_invalidates_proof(self):
        s=self.study();p={'sigma':2,'core_x':.1}
        original=transmission_signature(s,p,4)
        with patch('revision_replay.ray_implementation_digest',return_value='different implementation'):
            self.assertNotEqual(original,transmission_signature(s,p,4))
''';assert needle in s;s=s.replace(needle,'\n'+test+needle);p.write_text(s)
print(out)
