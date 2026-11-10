from __future__ import annotations
import math

def box_area(box):
    x1,y1,x2,y2=box
    return max(1.0,x2-x1)*max(1.0,y2-y1)

def bounding_box_iou(a,b):
    ax1,ay1,ax2,ay2=a; bx1,by1,bx2,by2=b
    ix1,iy1=max(ax1,bx1),max(ay1,by1); ix2,iy2=min(ax2,bx2),min(ay2,by2)
    inter=max(0.0,ix2-ix1)*max(0.0,iy2-iy1)
    if inter<=0:return 0.0
    union=box_area(a)+box_area(b)-inter
    return inter/union if union>0 else 0.0

def position_distance(a,b): return math.dist(a,b)
def box_size_difference(a,b):
    aa,ab=box_area(a),box_area(b)
    return abs(aa-ab)/max(aa,ab)
