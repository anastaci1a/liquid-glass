"""Lossless RGB code-value loading for 8/16-bit research PNG inputs.

No transfer-function, ICC, alpha-compositing or exposure operation is applied.
A 16-bit PNG may carry a decoded 10-bit video; its original encoding metadata
remains separate provenance. The returned values are encoded RGB, not radiance.
"""
from pathlib import Path
import cv2
import numpy as np


def read_encoded_rgb(path,dtype=np.float64):
    dtype=np.dtype(dtype)
    if dtype not in (np.dtype(np.float32),np.dtype(np.float64)):
        raise ValueError('Use float32 or float64 for normalized RGB')
    path=Path(path)
    if not path.is_file():raise ValueError(f'Missing raster input: {path}')
    raw=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
    if raw is None or raw.ndim!=3 or raw.shape[2]!=3 or raw.dtype not in (np.uint8,np.uint16):
        raise ValueError('Opaque three-channel uint8/uint16 RGB raster required')
    rgb=np.array(raw[...,::-1],dtype=dtype,order='C')
    return rgb/np.iinfo(raw.dtype).max
