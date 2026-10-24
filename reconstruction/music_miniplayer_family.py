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
