from __future__ import annotations
from .geometry import bounding_box_iou,box_size_difference,position_distance

def remove_session_from_other_states(session_id,keep_track_id,pending,lost):
    for mapping in (pending,lost):
        for key in [k for k,v in mapping.items() if v['session_id']==session_id and k!=keep_track_id]: mapping.pop(key,None)

def find_active_duplicate(point,box,class_id,active,cfg):
    best,best_iou=None,0.0
    for track_id,data in active.items():
        if data['class_id']!=class_id: continue
        if position_distance(point,data['last_position'])>cfg.duplicate_centre_distance_pixels: continue
        iou=bounding_box_iou(box,data['last_box'])
        if iou>=cfg.duplicate_iou_threshold and iou>best_iou: best,best_iou=track_id,iou
    return best,best_iou

def find_reidentification_match(point,box,class_id,now,lost,cfg):
    best,best_score=None,float('inf')
    for old_id,data in lost.items():
        gap=now-data['last_seen']
        if gap>cfg.reidentification_window_seconds or data['class_id']!=class_id: continue
        dist=position_distance(point,data['last_position']); size=box_size_difference(box,data['last_box']); iou=bounding_box_iou(box,data['last_box'])
        if gap>cfg.older_match_threshold_seconds:
            if dist>cfg.older_match_distance_pixels or size>cfg.older_match_max_size_difference or iou<cfg.older_match_min_iou: continue
        elif dist>cfg.reidentification_distance_pixels or size>cfg.max_box_size_difference: continue
        score=dist+size*25+gap*cfg.time_penalty_per_second-iou*20
        if score<best_score: best,best_score=old_id,score
    return best
