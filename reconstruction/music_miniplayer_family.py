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
    base=SplineFootprintBack((family['members'][member]['major_half'],g['minor_half']),g['corner_radius'],g['breaks'],g['height_controls'],cap_join_width=g['cap_join_width'])
    profile_file=Path(__file__).resolve().parent.parent/g['back_profile']
    if hashlib.sha256(profile_file.read_bytes()).hexdigest()!=g['back_profile_sha256']:
        raise ValueError('Working physical-height profile changed')
    back=HermiteFootprintBack(base,json.loads(profile_file.read_text()))
    return back,VerticalScaleBack(base,g['front_scale'])
