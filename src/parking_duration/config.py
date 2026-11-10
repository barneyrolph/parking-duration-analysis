from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass
class Config:
    videos: list[str] = field(default_factory=list)
    model_name: str = "yolov8s.pt"
    tracker: str = "parking_botsort.yaml"
    output_csv: str | None = None
    confidence: float = 0.30
    vehicle_classes: list[int] = field(default_factory=lambda:[2,3,5,7])
    min_park_duration_seconds: float = 120
    present_at_start_threshold: float = 5
    absence_grace_seconds: float = 2.5
    reidentification_window_seconds: float = 90.0
    reidentification_distance_pixels: float = 100.0
    max_box_size_difference: float = 0.7
    recovery_delay_seconds: float = 4.0
    duplicate_iou_threshold: float = 0.70
    duplicate_centre_distance_pixels: float = 60.0
    older_match_threshold_seconds: float = 12.0
    older_match_distance_pixels: float = 30.0
    older_match_max_size_difference: float = 0.20
    older_match_min_iou: float = 0.80
    time_penalty_per_second: float = 0.5
    show_live_video: bool = True
    write_annotated_video: bool = True
    parking_polygon_file: str = "parking_polygon.json"
    output_directory: str = "outputs"

    @classmethod
    def from_json(cls, path: str|Path) -> "Config":
        data=json.loads(Path(path).read_text(encoding='utf-8'))
        unknown=set(data)-set(cls.__dataclass_fields__)
        if unknown: raise ValueError(f"Unknown configuration keys: {', '.join(sorted(unknown))}")
        return cls(**data)

    def csv_path(self) -> Path:
        name=self.output_csv
        if not name:
            stem=Path(self.videos[0]).stem if self.videos else 'parking_sessions'
            name=f"parking_sessions_{stem}.csv"
        return Path(self.output_directory)/name
