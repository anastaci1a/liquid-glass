"""Foreground-only refinement of the existing pixel-rounded artwork placement."""
import copy
import cv2
import numpy as np


def resize_and_center_artwork(study, factor, center_y, radius=18):
    """Scale current rectangles; retain horizontal centers within raster precision."""
    if not np.isfinite([factor, center_y, radius]).all() or not 0 < factor <= 2 or radius < 0:
        raise ValueError('Invalid artwork adjustment')
    from extended_fit import geometry
    result = copy.copy(study)
    result.foreground_layers = []
    result.artwork_layers = dict(study.artwork_layers)
    records = []
    for box, alpha, color in study.foreground_layers:
        if tuple(box) not in study.artwork_layers:
            result.foreground_layers.append((box, alpha, color))
            continue
        a, b, c, d = box
        width = max(1, round((c-a)*factor))
        height = max(1, round((d-b)*factor))
        old_center_x = (a+c-1)/2
        left = round(old_center_x-(width-1)/2)
        top = round(center_y-(height-1)/2)
        new = [left, top, left+width, top+height]
        if not (study.crop[0] <= left and study.crop[1] <= top and new[2] <= study.crop[2] and new[3] <= study.crop[3]):
            raise ValueError('Artwork outside crop')
        source, _ = study.artwork_layers[tuple(box)]
        pixels = cv2.resize(source, (width, height), interpolation=cv2.INTER_AREA)
        yy, xx = np.mgrid[:height, :width]
        sd, *_ = geometry(xx-(width-1)/2, yy-(height-1)/2, [width/2, height/2], radius)
        coverage = np.clip(.5-sd, 0, 1)
        result.foreground_layers.append((new, coverage, pixels))
        result.artwork_layers[tuple(new)] = (source, radius)
        records.append(dict(old_box=list(box), new_box=new, requested_size=[(c-a)*factor, (d-b)*factor], realized_size=[width, height], old_center_x=old_center_x, new_center_x=left+(width-1)/2, requested_center_y=center_y, realized_center_y=top+(height-1)/2, radius=radius))
    return result, records
