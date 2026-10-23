# Completed bounded source-evidence recipes

All input URLs and downloaded-byte hashes are retained in official-metadata-fetch.json, variant-fetch.json and fragment-fetch.json. Original GETs used Node fetch with20–30s timeout and50MiB per-fragment cap. Master and selected variant resolve init/segment URI relative to the official variant URL; byte-concatenateinit+segment119 with no remux. No wholevideo fetched. Do not repeat completed downloads/scans without new provenance.

Native metadata:

    docker exec localica-dark-lab-check ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,profile,width,height,pix_fmt,color_range,color_space,color_transfer,color_primaries,chroma_location,r_frame_rate,avg_frame_rate,time_base,start_pts,start_time,duration,bit_rate,bits_per_raw_sample -show_entries format=format_name,start_time,duration,size,bit_rate -of json /evidence/extended/helper-toolbar-work/agent-toolbar-source-delivery/original-4k-segment119.mp4

Original-frame PTS:

    docker exec localica-dark-lab-check ffprobe -v error -select_streams v:0 -show_entries frame=pts,best_effort_timestamp,pts_time,best_effort_timestamp_time,pict_type,key_frame -of json /evidence/extended/helper-toolbar-work/agent-toolbar-source-delivery/original-4k-segment119.mp4

Successful native frame extraction (do not rerun/overwrite existingframes):

    docker exec localica-dark-lab-check ffmpeg -v error -threads 1 -filter_threads 1 -i /evidence/extended/helper-toolbar-work/agent-toolbar-source-delivery/original-4k-segment119.mp4 -vf "select='between(n,38,40)'" -fps_mode passthrough -frames:v 3 -pix_fmt rgb48be /evidence/extended/helper-toolbar-work/agent-toolbar-source-delivery/phase-%02d-original4k-rgb16.png

Completed phase/crop diagnostic:

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/agent-toolbar-code:/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-code/toolbar_source_delivery_phase_analysis.py

phase-analysis.py copied to that privatecode path; it reads saved3frames and oldfrozen target, preserves native16bitcrops and computes only nonoptical wholeframe phase controls. Color-converted decoded PNG is not unencoded original rendererRGB; compressed sourcefragments retained. No source/epoch adoption or score.
