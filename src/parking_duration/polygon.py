from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np

_points=[]
def _mouse(event,x,y,flags,param):
    del flags,param
    if event==cv2.EVENT_LBUTTONDOWN:_points.append((x,y))
    elif event==cv2.EVENT_RBUTTONDOWN and _points:_points.pop()

def draw(frame):
    _points.clear(); name='Draw Parking Area'; cv2.namedWindow(name); cv2.setMouseCallback(name,_mouse)
    print('Left click: add point | Right click: undo | Enter: finish')
    while True:
        display=frame.copy()
        for point in _points: cv2.circle(display,point,5,(0,255,0),-1)
        if len(_points)>1:
            arr=np.array(_points,dtype=np.int32); overlay=display.copy()
            if len(_points)>=3:
                cv2.fillPoly(overlay,[arr],(0,255,255)); cv2.addWeighted(overlay,.2,display,.8,0,display)
            cv2.polylines(display,[arr],False,(0,255,255),2)
        cv2.imshow(name,display)
        if cv2.waitKey(1)==13 and len(_points)>=3:break
    cv2.destroyWindow(name); return list(_points)

def save(points,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps({'points':[{'x':int(x),'y':int(y)} for x,y in points]},indent=2),encoding='utf-8')

def load(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    points=[(int(p['x']),int(p['y'])) for p in data['points']]
    if len(points)<3: raise ValueError('Parking polygon must have at least three points')
    return points

def get(frame,path):
    path=Path(path)
    if path.exists():
        try: return load(path)
        except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as e: print(f'Could not load polygon: {e}')
    points=draw(frame); save(points,path); return points
