# Evidence

Immutable source arrays, images, media and historical reports are indexed in `index.json`. Filenames are logical provenance paths; duplicate bytes share one compressed object.

| Item | Storage |
| --- | --- |
| Small compressed objects | Ordinary Git blobs. |
| Large compressed objects | Git LFS under `large/`. |
| File identity | Original SHA-256 and byte length. |
| Verbatim reports | Compressed evidence; concise dispositions live in research records. |
| Downloads / dependencies | Original URLs and hashes; no full font installers or source videos. |

## Restore

Install Git LFS and `zstd`, then run from the repository root:

~~~sh
git lfs install
git lfs pull
node tools/evidence.cjs list historical-records
node tools/evidence.cjs restore historical-records/liquid-glass-review/pipeline-01 /tmp/glass-evidence
node tools/evidence.cjs verify historical-records
~~~

Restoration checks decompressed SHA-256, byte length and safe destination paths. It refuses to overwrite different bytes. Nothing depends on the old Localica directory.

## Interpretation

A captured version is immutable. It does not certify that another session was frozen or adopt an input proposal. Preserve original acceptance scope, failures and source uncertainty.

Machine ledgers and literal logs remain evidence, not living narrative. New explanatory records follow the [documentation conduct](../../DOCUMENTATION.md).

## Historical paths

`historical-records/` is an index namespace. Restoration strips that prefix, preserving original sibling paths between review notes and `dark-glass-lab/` evidence.

Older commands may expect `/evidence`. Mount the restored `dark-glass-lab/` there in an isolated container. Mount this repository's reconstruction code explicitly; do not depend on the old Localica checkout or its temporary dependencies.
