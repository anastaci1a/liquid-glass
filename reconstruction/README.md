# Reconstruction engine

Shared tracing, geometry adapters, rendering, historical studies and focused tests.

[Current models](current-models.json) select the primary geometric versions. Earlier empirical recipes remain reproducible historical references, independent of whether their image scores are lower.

| Module | Responsibility |
| --- | --- |
| `geometric_optics.py` | Surface-derived normals, path statuses and ray transport. |
| `geometric_render.py` | Native integration, support handling and separated material layers. |
| `studies/` | Frozen public recipes, source excerpts and accepted records. |
| `test_geometric*.py` | Geometry/rendering/transport checks. |

Historical empirical modules remain for reproducibility. Their presence is not authorization to reuse independent displacement corrections in new geometric research.

Run `python3 -m unittest discover -s reconstruction -p 'test_geometric*.py'` after installing `requirements.txt`.
