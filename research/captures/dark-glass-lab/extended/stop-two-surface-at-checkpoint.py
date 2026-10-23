"""Stop only this experiment after its first complete durable native step."""
import os,json,time,signal
from pathlib import Path
out=Path('/evidence/extended/active-switch/physical-two-surface')
pid=65596;expected=b'python3\0/evidence/extended/switch-two-surface-native-fit.py\0'
deadline=time.monotonic()+1800
while time.monotonic()<deadline:
    proc=Path(f'/proc/{pid}/cmdline')
    if not proc.exists():raise SystemExit('Experiment already ended; inspect before any action')
    if proc.read_bytes()!=expected:raise SystemExit('PID identity changed; no signal sent')
    path=out/'coupled-native-progress.json'
    if path.exists():
        try:record=json.loads(path.read_text())
        except json.JSONDecodeError:time.sleep(2);continue
        if len(record.get('history',[]))>=1:
            record['early_stop_reason']='Saved first-step local model predicts only tiny extra benefit from the new parameter (worst ratio1.01672984 vs material-only1.01674005). Retain one completed native validation; stop the remaining expensive steps. No claim of global convergence or a qualifying pass.'
            with (out/'one-step-native-settlement.json').open('x') as f:json.dump(record,f,indent=2)
            os.kill(pid,signal.SIGINT)
            print('Checkpoint retained; interrupted only the continuing two-surface experiment.',flush=True)
            break
    time.sleep(2)
else:raise SystemExit('Boundary timeout; no signal sent')
