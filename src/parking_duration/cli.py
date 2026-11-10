from __future__ import annotations
import argparse
from pathlib import Path
from .config import Config
from .pipeline import run

def parser():
    p=argparse.ArgumentParser(description='Estimate parking durations from sequential video clips.')
    p.add_argument('videos',nargs='*',help='Videos in chronological order; overrides config')
    p.add_argument('--config',default='config.json',type=Path)
    p.add_argument('--no-display',action='store_true')
    return p

def main():
    args=parser().parse_args(); cfg=Config.from_json(args.config)
    if args.videos: cfg.videos=args.videos
    if args.no_display: cfg.show_live_video=False
    run(cfg); return 0
