# Parking Duration Analysis

A modular refactor of `parking_duration_1.04.py`. It analyses sequential clips from one fixed camera, lets the operator draw and reuse a parking polygon, tracks COCO vehicle classes with Ultralytics YOLO, reconciles temporary or changed tracker IDs, and exports qualifying parking sessions.

## Install

Python 3.10 or 3.11 is recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
copy config.example.json config.json
```

Edit `config.json`, especially `videos`, then run:

```powershell
parking-duration --config config.json
```

You can override the configured videos, in chronological order:

```powershell
parking-duration --config config.json TLC00016.AVI TLC00017.AVI TLC00018.AVI
```

For unattended processing:

```powershell
parking-duration --config config.json --no-display
```

## Modules

- `config.py`: validated run settings
- `polygon.py`: polygon drawing and JSON persistence
- `geometry.py`: IoU, centre-distance and size calculations
- `tracking.py`: duplicate suppression and re-identification matching
- `processor.py`: per-frame and cross-clip session state machine
- `pipeline.py`: model loading and sequential clip orchestration
- `export.py`: CSV and run summary
- `cli.py`: command-line entry point

## Behaviour retained from Version 1.04

- candidate stabilisation before session creation
- same-ID recovery
- changed-ID re-identification
- stricter matching after long absences
- duplicate tracker-box suppression
- session continuity across consecutive clips
- `present_at_start` and `present_at_end` flags
- annotated troubleshooting video

The default tracker is Ultralytics `botsort.yaml`. If Version 1.04 used a customised `parking_botsort.yaml`, place that file in the repository and set `"tracker": "parking_botsort.yaml"` in `config.json`.

## Outputs

Outputs are written under `outputs/` and include the CSV plus one annotated MP4 per input clip. The CSV preserves the Version 1.04 columns.

## Testing

```powershell
python -m pip install -e .[dev]
pytest
ruff check .
```

Before relying on the refactor, run Version 1.04 and this repository against the same representative clips and compare the CSV and annotated video. Tracker output can vary with Ultralytics, PyTorch and model versions, so keep the environment fixed during the comparison.

## Privacy and publication

Do not commit source footage, annotated footage, number plates, CSV survey outputs, model weights, local paths, credentials or the saved site polygon. Confirm employer permission and third-party licence obligations before making the repository public.

## Licence

No open-source licence is granted yet. Replace `LICENSE` only after confirming who owns the code and which licence is approved.
