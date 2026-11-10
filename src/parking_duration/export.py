from __future__ import annotations
import csv
from pathlib import Path
FIELDS=['video','departure_video','session_id','original_track_id','final_track_id','id_change_count','present_at_start','present_at_end','arrival_seconds','departure_seconds','duration_minutes']

def write_sessions(path,sessions):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS); writer.writeheader(); writer.writerows(sessions)

def print_summary(sessions,path,runtime):
    print('\n========================')
    print('PARKING SUMMARY')
    print('========================')
    print(f'Parking sessions: {len(sessions)}')
    if sessions:
        print(f"Average duration: {sum(s['duration_minutes'] for s in sessions)/len(sessions):.1f} mins")
    h,rem=divmod(runtime,3600); m,s=divmod(rem,60)
    print(f'CSV saved: {path}')
    print(f'Total processing runtime: {int(h):02d}:{int(m):02d}:{s:05.2f}')
