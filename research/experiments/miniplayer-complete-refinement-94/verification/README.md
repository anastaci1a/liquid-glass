# Own verification

The primary researcher verified all twenty-eight material candidates directly. No helper was assigned. A separate algebraic implementation reproduced the twelve shadow, twelve highlight and four combined arrays within `5.961e-8` absolute RGB, under the declared `1e-7` replay tolerance. This rounding tolerance does not alter any acceptance guard.

Every original metric and guard reproduced exactly from its saved complete array. Four geometry-baseline identities also reproduce exactly. Original masks, partial cohorts and foreground ordering are unchanged. Fully covered pixels remain exact under the exterior-only shadow.

Three anisotropic ellipse-plus-disk areas and first moments pass against an independent ellipse-perimeter calculation. This extends the disk controls without claiming optical or radiance convergence.

[Replay results](result.json), [area controls](area-controls.json), [ledger](ledger.json) and [input hashes](hashes.json) preserve the scope. No ray, source query, filter, fit or new candidate ran. Full-image and fixed-crop inspection supplements numerical verification; visible defects are retained in the main report.
