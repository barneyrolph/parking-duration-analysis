from __future__ import annotations
from pathlib import Path
import time
from ultralytics import YOLO
from .processor import process_video
from .export import write_sessions,print_summary

def run(cfg):
    if not cfg.videos: raise ValueError('No videos configured')
    missing=[v for v in cfg.videos if not Path(v).exists()]
    if missing: raise FileNotFoundError(f"Missing videos: {', '.join(missing)}")
    started=time.perf_counter(); model=YOLO(cfg.model_name); all_sessions=[]; carried=[]; next_id=1; offset=0.0
    for i,video in enumerate(cfg.videos):
        sessions,carried,next_id,duration=process_video(video,offset,carried,next_id,i==len(cfg.videos)-1,model,cfg)
        all_sessions.extend(sessions); offset+=duration
    path=cfg.csv_path(); write_sessions(path,all_sessions); print_summary(all_sessions,path,time.perf_counter()-started)
    return all_sessions
