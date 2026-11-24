# Parking Duration Analysis

A modular Python application for estimating vehicle parking duration from sequential video clips recorded by a fixed camera. It uses Ultralytics YOLO to track COCO vehicle classes within a user-defined parking area, reconciles temporary or changed tracker IDs across frames and clips, and exports qualifying parking sessions.

This project is a proof of concept for estimating vehicle parking duration from recorded video. It is not intended to provide evidence for enforcement or other decisions affecting individuals without independent human verification. Users are responsible for ensuring they have the necessary authority and lawful basis to process any video footage used with the software.

## How it works

1. **Load the video sequence**  
   Input clips are processed in chronological order so that parking sessions can continue across consecutive video files.

2. **Define the parking area**  
   The operator draws a polygon around the area to be analysed. The polygon is saved and can be reused for subsequent runs using the same camera view.

3. **Detect and track vehicles**  
   Ultralytics YOLO detects and tracks supported COCO vehicle classes in each frame. Tracking IDs are used to follow individual vehicles over time.

4. **Identify vehicles within the parking area**  
   Tracked vehicles are evaluated against the parking polygon. Vehicles that remain within the area are treated as potential parking sessions.

5. **Maintain vehicle identity**  
   The application attempts to handle temporary tracking loss and tracker ID changes by comparing detections and previously observed vehicles. This reduces the chance of a single parking event being incorrectly recorded as multiple sessions.

6. **Maintain continuity between clips**  
   Vehicle state is carried between sequential clips so that a vehicle already parked when one clip ends can continue the same session when the next clip begins.

7. **Create parking sessions**  
   Once a vehicle satisfies the configured parking criteria, its observed arrival, departure and duration are recorded as a parking session.

8. **Export and review the results**  
   Completed sessions are written to CSV. An annotated video is also produced for each input clip so that detections, tracking behaviour and calculated sessions can be visually reviewed.

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
parking-duration --config config.json CLIP_1.AVI CLIP_2.AVI CLIP_3.AVI
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

Outputs are written under `outputs/` and include:

- A CSV containing the detected parking sessions and their calculated durations.
- One annotated MP4 for each input clip, allowing the tracking results to be visually reviewed.

The annotated videos should be used to verify the automated results, particularly where the output may be used for further analysis.

## Known Security Limitations

### File path validation

The application accepts paths for input videos, outputs, the tracking configuration, and the parking polygon. These paths are not currently restricted to predefined or approved directories.

Users should therefore only run the application with trusted configuration files and path values.

### YOLO model loading

The configured YOLO model is passed to the Ultralytics library without restricting model loading to an approved local file or verifying the model's integrity with a checksum.

Only models from trusted sources should be used.

## Testing

```powershell
python -m pip install -e .[dev]
pytest
ruff check .
```

## Security

Security vulnerabilities should not be reported through public GitHub issues.

Please see [SECURITY.md](SECURITY.md) for information about reporting vulnerabilities privately.

## Licence

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.