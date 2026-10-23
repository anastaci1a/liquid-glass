# Trial-report recovery

The continuation script incorrectly reused the first-stage final-report filename. Its20-step report has been copied unchanged to continuation-settlement.json. The complete original10-step progress record retains exact final parameters/material/history; those are independently replayed to reconstruct its native report. The original first-stage native report bytes are lost. No accepted/public recipe or count changed. The faulty script is archived; final writes now use distinct filenames and exclusive creation. This is an evidence-bookkeeping correction, not a new experiment/pass.

Recovery complete: first-stage-recovered-report.json independently replays the saved10-step parameters. Both E values match their original console record within1e-9:15.276824905112036 and16.60570560678378. It is explicitly a reconstructed report, not the overwritten original bytes.
