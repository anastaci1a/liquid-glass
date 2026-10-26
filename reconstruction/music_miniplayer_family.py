"""One miniplayer glass model. Only major half-length varies by member."""
import json
from pathlib import Path
from spline_height_back import SplineFootprintBack
FAMILY_FILE=Path(__file__).resolve().parent/'families/music-mini-player.json'
def load_family():
    return json.loads(FAMILY_FILE.read_text())
def surface_for_length(major_half):
    family=load_family();g=family['geometry']
    if major_half<g['minor_half']:raise ValueError('Major half-length must cover the shared minor half')
    return SplineFootprintBack((major_half,g['minor_half']),g['corner_radius'],g['breaks'],g['height_controls'],cap_join_width=g['cap_join_width'])
def surface_for_member(member):
    family=load_family()
    return surface_for_length(family['members'][member]['major_half'])


def load_working_family():
    """Explicit public working selection; load_family keeps frozen baseline."""
    return json.loads((FAMILY_FILE.parent/'music-mini-player-working.json').read_text())


def working_surface_pair(member):
    """Same actual front/back for every member; major length alone varies."""
    import hashlib
    from hermite_height_back import HermiteFootprintBack
    from raised_front_optics import VerticalScaleBack
    family=load_working_family();g=family['geometry']
    half=(family['members'][member]['major_half'],g['minor_half'])
    if g.get('coordinate')=='shoulder_core':
        from shoulder_core_coordinate import ShoulderCoreSplineBack
        base=ShoulderCoreSplineBack(half,g['corner_radius'],g['shoulder_inset'],g['breaks'],g['height_controls'])
    else:
        base=SplineFootprintBack(half,g['corner_radius'],g['breaks'],g['height_controls'],cap_join_width=g['cap_join_width'])
    profile_file=Path(__file__).resolve().parent.parent/g['back_profile']
    if hashlib.sha256(profile_file.read_bytes()).hexdigest()!=g['back_profile_sha256']:
        raise ValueError('Working physical-height profile changed')
    back=HermiteFootprintBack(base,json.loads(profile_file.read_text()))
    return back,VerticalScaleBack(base,g['front_scale'])


def working_incident_response(filtered_samples):
    """Grade incident-filtered samples before actual primary power and AA."""
    from miniplayer_refinement_effects import low_luminance_body
    material=load_working_family()['material']
    return low_luminance_body(filtered_samples,material['gain'],material['bias'],material.get('low_luminance_lift',0.))


def working_artwork_study(study):
    """Preserve ordered original foreground, with declared content transform."""
    family=load_working_family()
    if 'artwork' not in family:return study
    from miniplayer_refinement_effects import artwork_study
    return artwork_study(study,**family['artwork'])


def working_outline(body,ungraded_blurred_guide,integrated_alpha):
    """Apply the selected display response after the ordered foreground.

    The guide contains incident blur and actual refraction, without body grade
    or assigned reflection light. Alpha is full-pixel geometric coverage.
    """
    material=load_working_family()['material'];outline=material.get('outline')
    if not isinstance(outline,dict):return body.copy()
    from miniplayer_refinement_effects import soft_channel_rim_dark
    return soft_channel_rim_dark(body,ungraded_blurred_guide,integrated_alpha,
                                 outline['curve_power'],outline.get('dark_neutral',0.))


def working_center(measured_center):
    """Common registration correction, in native reference pixels."""
    import numpy as np
    return np.asarray(measured_center,float)+load_working_family().get('registration',{}).get('center_shift_native',[0.,0.])


def working_contour(member):
    """Selected contour in native pixels for outline and exterior shadow."""
    from shoulder_core_coordinate import ShoulderCoreCoordinate
    f=load_working_family();g=f['geometry'];L=f['length_unit_native_pixels']
    if g.get('coordinate')!='shoulder_core':raise ValueError('No certified display contour for this selection')
    return ShoulderCoreCoordinate((f['members'][member]['major_half']*L,g['minor_half']*L),
                                  g['corner_radius']*L,g['shoulder_inset']*L)


def working_composite(study,raw_source,inside,supported,primary_power,
                      direct_reflected_radiance,outline_alpha,shadow_field):
    """Compose certified AA2 samples; this does not construct source support.

    Direct reflected radiance must already include its interface power. The
    exterior shadow affects supported clear subrays only. Unknown clear data
    stay unavailable. Outline and original ordered foreground remain separate.
    """
    import numpy as np
    from environment_radiance import decode_srgb,encode_srgb
    f=load_working_family();H,W=study.valid.shape
    if inside.shape!=(2*H,2*W) or raw_source.shape!=inside.shape+(3,):
        raise ValueError('Expected retained AA2 samples')
    if np.any(inside&~supported) or not np.isfinite(raw_source[inside]).all():
        raise ValueError('Unsupported lens samples')
    values=raw_source.copy();graded=working_incident_response(raw_source[inside])
    light=np.asarray(direct_reflected_radiance)
    if light.ndim==1:light=light[:,None]
    if light.shape not in [(int(inside.sum()),1),(int(inside.sum()),3)] or not np.isfinite(light).all() or np.any(light<0):
        raise ValueError('Expected finite nonnegative lens radiance')
    encoded=encode_srgb(primary_power[inside,None]*decode_srgb(graded)+light)
    if not np.isfinite(encoded).all() or encoded.min()<0 or encoded.max()>1:
        raise ValueError('Unbounded combined response')
    values[inside]=encoded;clear=~inside&supported
    shadow=f['material'].get('generated_shadow')
    if isinstance(shadow,dict):
        if shadow_field.shape!=inside.shape or not np.isfinite(shadow_field).all() or np.any((shadow_field<0)|(shadow_field>1+1e-12)):
            raise ValueError('Expected bounded exterior shadow field')
        values[clear]*=1-shadow['opacity']*shadow_field[clear,None]
    pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
    foreground=working_artwork_study(study)
    body=foreground.apply_foreground(pre.copy())
    guide=foreground.apply_foreground(raw_source.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32))
    return dict(pre_foreground=pre,complete=working_outline(body,guide,outline_alpha))
