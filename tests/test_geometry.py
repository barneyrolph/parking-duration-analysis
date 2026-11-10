from parking_duration.geometry import bounding_box_iou,box_size_difference

def test_iou_identical(): assert bounding_box_iou((0,0,10,10),(0,0,10,10))==1

def test_iou_disjoint(): assert bounding_box_iou((0,0,10,10),(20,20,30,30))==0

def test_size_difference(): assert box_size_difference((0,0,10,10),(0,0,20,10))==0.5
