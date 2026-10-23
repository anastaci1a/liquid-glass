from pathlib import Path
source=Path('/evidence/extended/switch-spectral-reflection-probe.py').read_text();exec(source.split("root=Path(")[0]);root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-23.json').read_text())['current'];out=root.parent/'spectral-reflection-probe';best=json.loads((out/'running.json').read_text())['best'];p={**old['parameters'],'spectral_profile':best['parameters']}
for name in ['a','b']:
 s=SpectralStudy(root/name);s.comparison(s.render(p,np.array(old['material'])),out/f'peek-{name}.png',p)
