"""Bounded original4k frame/codec phase controls, NOT optical scores or fits."""
from pathlib import Path
import numpy as np
import cv2
import json
import hashlib
from PIL import Image

r = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-source-delivery')
phases = json.loads((r/'segment119-frame-phase.json').read_text())['frames'][38:41]
old = np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png'), float)/255
rows = []
for i, p in enumerate(phases, 1):
    f = r/f'phase-{i:02d}-original4k-rgb16.png'
    raw = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
    assert raw.shape == (2160, 3840, 3) and raw.dtype == np.uint16
    C = raw[..., ::-1].astype(float)/65535
    down = cv2.resize(C, (1920, 1080), interpolation=cv2.INTER_AREA)
    difference = (down-old)*255
    rows.append({'file': f.name, 'png_sha256': hashlib.sha256(f.read_bytes()).hexdigest(),
                 'native_dimensions': [3840, 2160], 'decoded_RGB_bits_per_channel': 16,
                 'source_encoded_bits_per_sample': 10, 'segment_frame_index': 38+i-1,
                 'original_PTS': p['pts'], 'original_PTS_time': p['pts_time'],
                 'whole_original_HD_phase_control_RGB_RMSE_255': float(np.sqrt(np.mean(difference*difference))),
                 'outside_known_text_control_RGB_RMSE_255': float(np.sqrt(np.mean(difference[425:555, 60:480]**2))),
                 'comparison': 'AREA2xdownsample ONLYforwholeframecodec/phase diagnostic;notreferenceproposal,notopticalscoreorfit'})
    cv2.imwrite(str(r/f'phase-{i:02d}-d-native4k-crop.png'), raw[900:1100, 1920:2240])
    cv2.imwrite(str(r/f'phase-{i:02d}-outside-text-native4k-crop.png'), raw[850:1110, 120:960])
Image.fromarray(np.uint8(np.rint(old[450:550, 960:1120]*255))).save(r/'old-HD-d-native-crop.png')
Image.fromarray(np.uint8(np.rint(old[425:555, 60:480]*255))).save(r/'old-HD-outside-text-native-crop.png')
result = {'controls': rows, 'original_HD_native_frame_index': 21279, 'original_HD_frame_PTS': 710.0093,
          'HLS_first_frame_PTS_minus_playlist_cumulative_start': .033366666668,
          'limits': 'Original4kdelivered sourcefragment, no localrescale/reencodeinproposal;RGBArea2x ONLYphase/codecdiagnostic. Main10 420 format establishes storedsampling/precision, not originalUIrenderacquisitionbandwidth or sourcePSF. No E/sourceepoch/sourceadoption.'}
(r/'phase-native-proposal.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(rows), flush=True)
