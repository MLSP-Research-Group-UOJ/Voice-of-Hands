from types import SimpleNamespace as NS
from pathlib import Path
import csv, sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from slsl_features.landmarks import FEATURE_DIM, build_frame, feature_columns
from slsl_features.io import atomic_save_npz, validate_arrays, validate_npz

def lm(x=0,y=0,z=0,v=1): return NS(x=x,y=y,z=z,visibility=v)
def group(n): return NS(landmark=[lm(i/100,i/200,i/300) for i in range(n)])
def result(pose=True,left=True,right=True,face=True):
    p=group(33) if pose else None
    if p: p.landmark[11]=lm(0,0,0); p.landmark[12]=lm(2,0,0)
    return NS(pose_landmarks=p,left_hand_landmarks=group(21) if left else None,right_hand_landmarks=group(21) if right else None,face_landmarks=group(468) if face else None)
def test_dimension_and_order():
    assert FEATURE_DIM==257 and len(feature_columns())==257
    assert feature_columns()[0]=="pose.nose.x" and feature_columns()[-4:]==["pose_present","left_hand_present","right_hand_present","face_present"]
def test_normalization_and_presence():
    vec,mask,ok=build_frame(result()); assert ok and mask.tolist()==[1,1,1,1]
    assert np.isclose(vec[4],-.5) and np.isclose(vec[8],.5)
def test_zero_shoulder_and_missing():
    r=result(left=False,right=False,face=False); r.pose_landmarks.landmark[12]=lm(0,0,0)
    vec,mask,ok=build_frame(r); assert not ok and mask.tolist()==[1,0,0,0] and np.isfinite(vec).all()
    vec,mask,ok=build_frame(result(False,False,False,False)); assert not ok and not mask.any() and not vec[:-4].any()
def test_validation_and_npz(tmp_path):
    f=np.zeros((2,257),np.float32); m=np.zeros((2,4),np.uint8); validate_arrays(f,m,25,257)
    f[0,0]=np.nan
    try: validate_arrays(f,m,25,257); assert False
    except ValueError: pass
    f[0,0]=0; p=tmp_path/"x.npz"; atomic_save_npz(p,features=f,presence_mask=m,fps=np.float32(25),num_frames=np.int64(2),duration_sec=np.float32(.08),source_filename=np.str_("x.mp4"),feature_version=np.str_("v"))
    assert validate_npz(p,257)[0]
def test_sinhala_roundtrip_and_duplicates(tmp_path):
    p=tmp_path/"s.csv"; rows=[{"clip_id":"x","text":"සිංහල"},{"clip_id":"x","text":"අකුරු"}]
    with p.open("w",encoding="utf-8-sig",newline="") as f: w=csv.DictWriter(f,fieldnames=["clip_id","text"]);w.writeheader();w.writerows(rows)
    with p.open(encoding="utf-8-sig") as f: loaded=list(csv.DictReader(f))
    assert loaded[0]["text"]=="සිංහල" and len({r["clip_id"] for r in loaded})<len(loaded)

