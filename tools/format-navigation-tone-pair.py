"""Publish exact saved reference/candidate panels; no scientific evaluation."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
records = []
for key in ['a', 'b']:
    source = ROOT / f'research/experiments/agent-navigation-neutral-06/trial-01/{key}-comparison.png'
    asset = ROOT / f'guide/assets/geometric-navigation-tone-held-{key}.png'
    image = Image.open(source).convert('RGB')
    width = (image.width - 4) // 3
    assert image.size == (3 * width + 4, 399) and width == 1080
    reference = image.crop((0, 64, width, image.height))
    candidate = image.crop((2 * (width + 2), 64, image.width, image.height))
    pair = Image.new('RGB', (2 * width + 2, image.height), 'white')
    pair.paste(reference, (0, 64))
    pair.paste(candidate, (width + 2, 64))
    draw = ImageDraw.Draw(pair)
    draw.text((8, 20), 'Apple reference', fill='black')
    draw.text((width + 10, 20), 'Held neutral tone: B boundary guard fails', fill='black')
    pair.save(asset)
    decoded = Image.open(asset).convert('RGB')
    assert decoded.crop((0, 64, width, image.height)).tobytes() == reference.tobytes()
    assert decoded.crop((width + 2, 64, 2 * width + 2, image.height)).tobytes() == candidate.tobytes()
    records.append(dict(source=str(source.relative_to(ROOT)),
                        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        asset=str(asset.relative_to(ROOT)),
                        SHA256=hashlib.sha256(asset.read_bytes()).hexdigest(),
                        width=pair.width, height=pair.height, top_caption=64,
                        gutter=2, native_panel_width=width,
                        presentation_panel_width=width,
                        body_pixels_exact=True, status='held-not-accepted'))
output = ROOT / 'research/presentation/navigation-tone-held.json'
output.write_text(json.dumps(dict(operation='Exact saved-panel extraction; no resizing',
    rays=0, source_queries=0, optical_renders=0, records=records), indent=2) + '\n')
