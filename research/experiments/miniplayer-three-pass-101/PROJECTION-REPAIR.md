# Projection prerequisite repair

The first gentler contour attempt stopped before source sampling. The core projection reached a narrow angular bracket while its normal residual still exceeded the unchanged tolerance. No image was produced.

The revised solver removes bracket width as an early success condition. It allows at most 80 iterations, then applies the original residual check. It does not change the support function, normals or acceptance tolerance.

The fixed failing grid passes. Independent finite differences, central inversion and physical scaling pass in [controls](projection-repair-result.json). The original source snapshot and failed ledger remain preserved. A separately recorded corrected execution follows within the original pass deadline.
