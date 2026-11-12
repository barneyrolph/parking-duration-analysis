# Parking Duration Analysis

A modular Python script that analyses sequential clips from one fixed camera, lets the operator draw and reuse a parking polygon, tracks COCO vehicle classes with Ultralytics YOLO, reconciles temporary or changed tracker IDs, and exports qualifying parking sessions.

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


## Outputs

Outputs are written under `outputs/` and include the CSV plus one annotated MP4 per input clip.

## Testing

```powershell
python -m pip install -e .[dev]
pytest
ruff check .
```

## Licence

No open-source licence is granted yet. Replace `LICENSE` only after confirming who owns the code and which licence is approved.
