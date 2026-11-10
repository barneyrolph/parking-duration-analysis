from __future__ import annotations
from pathlib import Path
import cv2
import numpy as np
from matplotlib.path import Path as PolygonPath
from .polygon import get as get_polygon
from .tracking import find_active_duplicate,find_reidentification_match,remove_session_from_other_states


def _row(data,departure_video,present_at_end=False):
    duration=data['last_seen']-data['arrival']
    return {'video':data['arrival_video'],'departure_video':departure_video,'session_id':data['session_id'],
    'original_track_id':data['original_track_id'],'final_track_id':data['current_track_id'],
    'id_change_count':data['id_change_count'],'present_at_start':data['present_at_start'],
    'present_at_end':present_at_end,'arrival_seconds':round(data['arrival'],1),
    'departure_seconds':round(data['last_seen'],1),'duration_minutes':round(duration/60,2)}


def process_video(video_path,time_offset,carried,next_session_id,is_final,model,cfg):
    cap=cv2.VideoCapture(str(video_path))
    if not cap.isOpened(): raise FileNotFoundError(video_path)
    try:
        fps=cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps<=0: raise ValueError(f'Invalid frame rate: {video_path}')
        width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES,total//2); ok,middle=cap.read()
        if not ok: raise RuntimeError(f'Could not read middle frame: {video_path}')
        points=get_polygon(middle,cfg.parking_polygon_file); polygon=PolygonPath(points); cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        stem=Path(video_path).stem; outdir=Path(cfg.output_directory); outdir.mkdir(parents=True,exist_ok=True)
        writer=None
        if cfg.write_annotated_video:
            writer=cv2.VideoWriter(str(outdir/f'{stem}_parking_annotated.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))
            if not writer.isOpened(): raise RuntimeError('Could not open annotated video writer')
        active={}; pending={}; candidates={}; lost={}; suppressed={}; sessions=[]
        for data in carried or []: lost[f"previous_clip_session_{data['session_id']}"]=data
        frame_num=0; stopped=False
        while True:
            ok,frame=cap.read()
            if not ok: break
            frame_num+=1; clip_time=frame_num/fps; now=time_offset+clip_time
            for tid in [k for k,v in pending.items() if now-v['lost_time']>=cfg.recovery_delay_seconds]: lost[tid]=pending.pop(tid)
            result=model.track(frame,persist=True,tracker=cfg.tracker,classes=cfg.vehicle_classes,conf=cfg.confidence,verbose=False)[0]
            ids=[]; boxes=[]; classes=[]
            if result.boxes.id is not None:
                ids=result.boxes.id.int().cpu().tolist(); boxes=result.boxes.xyxy.cpu().tolist(); classes=result.boxes.cls.int().cpu().tolist()
            detected=set(ids); seen=set(); inside_ids=set()
            for dup,primary in list(suppressed.items()):
                if primary not in active or dup not in detected: suppressed.pop(dup,None)
            for tid in [k for k in active if k not in detected]:
                data=active.pop(tid); data.update(lost_time=now,lost_reason='not_visible'); pending[tid]=data
            arr=np.array(points,dtype=np.int32); overlay=frame.copy(); cv2.fillPoly(overlay,[arr],(0,255,255)); cv2.addWeighted(overlay,.15,frame,.85,0,frame); cv2.polylines(frame,[arr],True,(0,255,255),2)
            for tid,box,cid in zip(ids,boxes,classes):
                x1,y1,x2,y2=box; bbox=(x1,y1,x2,y2); point=((x1+x2)/2,(y1+y2)/2)
                if tid in suppressed:
                    cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),(255,0,255),2); continue
                is_inside=polygon.contains_point(point); seen.add(tid); colour=(0,255,0) if is_inside else (0,0,255)
                if is_inside:
                    inside_ids.add(tid)
                    if tid not in active:
                        c=candidates.setdefault(tid,{'first_seen':now,'last_seen':now,'last_position':point,'last_box':bbox,'class_id':cid})
                        c.update(last_seen=now,last_position=point,last_box=bbox,class_id=cid)
                        if now-c['first_seen']>=cfg.recovery_delay_seconds:
                            recovered=pending.pop(tid,None) or lost.pop(tid,None)
                            if recovered:
                                recovered.update(current_track_id=tid,last_seen=now,last_position=point,last_box=bbox,class_id=cid,lost_reason=None)
                                active[tid]=recovered; remove_session_from_other_states(recovered['session_id'],tid,pending,lost); candidates.pop(tid,None)
                            else:
                                duplicate,_=find_active_duplicate(point,bbox,cid,active,cfg)
                                if duplicate is not None: suppressed[tid]=duplicate; candidates.pop(tid,None); continue
                                old=find_reidentification_match(point,bbox,cid,now,lost,cfg)
                                if old is not None:
                                    data=lost.pop(old); data.update(current_track_id=tid,last_seen=now,last_position=point,last_box=bbox,class_id=cid,lost_reason=None); data['id_change_count']+=1
                                    active[tid]=data; remove_session_from_other_states(data['session_id'],tid,pending,lost); candidates.pop(tid,None)
                                else:
                                    first=c['first_seen']; active[tid]={'session_id':next_session_id,'arrival':first,'arrival_video':stem,'first_seen':first,'last_seen':now,'present_at_start':first<=cfg.present_at_start_threshold,'last_position':point,'last_box':bbox,'class_id':cid,'original_track_id':tid,'current_track_id':tid,'id_change_count':0,'lost_reason':None}; next_session_id+=1; candidates.pop(tid,None)
                    else: active[tid].update(last_seen=now,last_position=point,last_box=bbox,class_id=cid,current_track_id=tid)
                label=f'Tracker {tid}'
                if tid in active: label=f"Session {active[tid]['session_id']} Tracker {tid} {'IN' if is_inside else 'OUT'} Changes {active[tid]['id_change_count']}"
                elif tid in candidates: label=f"Tracker {tid} CANDIDATE {now-candidates[tid]['first_seen']:.1f}s"
                cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),colour,2); cv2.putText(frame,label,(int(x1),max(20,int(y1)-10)),cv2.FONT_HERSHEY_SIMPLEX,.55,colour,2)
            for tid in [k for k in active if k in seen and k not in inside_ids]:
                data=active.pop(tid); data.update(lost_time=now,lost_reason='left_polygon'); pending[tid]=data
            active_sessions={v['session_id'] for v in active.values()}; pending_sessions={v['session_id'] for v in pending.values()}
            for tid,data in list(lost.items()):
                if data['session_id'] in active_sessions|pending_sessions: lost.pop(tid,None); continue
                if now-data['last_seen']>cfg.reidentification_window_seconds:
                    if data['last_seen']-data['arrival']>=cfg.min_park_duration_seconds: sessions.append(_row(data,stem))
                    lost.pop(tid,None)
            for tid,data in list(candidates.items()):
                if now-data['last_seen']>cfg.absence_grace_seconds: candidates.pop(tid,None)
            cv2.putText(frame,f'Clip Time: {clip_time:.1f}s | Continuous Time: {now:.1f}s',(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            if writer: writer.write(frame)
            if cfg.show_live_video:
                cv2.imshow('Parking Tracking',frame)
                if cv2.waitKey(1)&0xFF==ord('q'): stopped=True; break
            if frame_num%100==0 and total: print(f'{frame_num}/{total} ({frame_num/total*100:.0f}%)')
        duration=frame_num/fps; end=time_offset+duration
        remaining={}
        for data in list(active.values())+list(pending.values())+list(lost.values()):
            sid=data['session_id']
            if sid not in remaining or data['last_seen']>remaining[sid]['last_seen']: remaining[sid]=data
        if is_final or stopped:
            for data in remaining.values():
                if data['last_seen']-data['arrival']>=cfg.min_park_duration_seconds: sessions.append(_row(data,stem,end-data['last_seen']<=cfg.absence_grace_seconds))
            carry=[]
        else: carry=list(remaining.values())
        return sessions,carry,next_session_id,duration
    finally:
        cap.release()
        if 'writer' in locals() and writer: writer.release()
        cv2.destroyAllWindows()
