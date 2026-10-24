# Farther finite emitter: useful parallax tradeoff

Scaling the finite panel and its distance by two reduces the expanded regression of the closer panel. It still fails the family guards. The older numerical-baseline body errors improve overall, but expanded partial/foreground failures remain and current-working20 comparisons fail. No source distance or replacement model is accepted.

| Reference | Far-field shallow42 E | Closer-panel46 E | Farther-panel48 E |
| --- | ---: | ---: | ---: |
| Expanded A | 8.190509 | 10.898802 | 8.288537 |
| Expanded B | 7.072735 | 7.405899 | 6.920617 |
| Compact A | 22.547641 | 20.143621 | 21.576158 |
| Compact B | 21.610871 | 19.342706 | 20.676230 |

The panel is at global z1770 native pixels, centered at x960/y540. All linear panel dimensions scale with distance, keeping the same apparent annular pattern and radiance four. This is a scale/distance comparison, not a fixed-size source moved farther away. Lens geometry, normals, source lookup, material and blur stay unchanged.

All four comparisons were inspected. Cap lighting varies with placement, but the thin rim, localized bloom and body/source pattern still differ from the reference. Clipping is zero. Every original/current-working and closer-panel guard remains recorded without waiver.

| Reference | Comparison | Measurements |
| --- | --- | --- |
| Expanded A | [Image](expanded-a-comparison.png) | [Metrics](expanded-a-metrics.json) |
| Expanded B | [Image](expanded-b-comparison.png) | [Metrics](expanded-b-metrics.json) |
| Compact A | [Image](compact-a-comparison.png) | [Metrics](compact-a-metrics.json) |
| Compact B | [Image](compact-b-comparison.png) | [Metrics](compact-b-metrics.json) |

Four closer-panel pre-foreground, complete-image and score identities pass. The unchanged shared emitter's synthetic controls are reused. There are 1487085 new light-plane intersections, the same number of cached panel samples, four candidates and four identities. No new lens ray, source query, filter or fit runs.

The [protocol](protocol.json) runs from 12:05:35.254 to 12:13:35.254 UTC. Science finishes at 12:05:55.020. The [unexecuted preparation](../miniplayer-finite-emitter-47/README.md) remains separate and retains zero scientific work. The [result](result.json), [checkpoint](checkpoint.json), [bindings](bindings.json) and [ledger](ledger.json) preserve exact scope.

The far-field, closer-panel and farther-panel comparison is now complete. No third height or material adjustment follows inside this question. A numerical sampling check can test the thin reflection component without claiming an optical improvement or changing the original scoring protocol.
