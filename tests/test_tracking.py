from parking_duration.config import Config
from parking_duration.tracking import find_reidentification_match

def test_recent_reidentification():
    lost={1:{'last_seen':10.0,'class_id':2,'last_position':(10,10),'last_box':(0,0,20,20)}}
    assert find_reidentification_match((12,10),(1,0,21,20),2,12,lost,Config())==1
