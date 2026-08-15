from pathlib import Path
import argparse, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from slsl_features.io import validate_npz
from slsl_features.landmarks import FEATURE_DIM
p=argparse.ArgumentParser(); p.add_argument("path",type=Path); a=p.parse_args()
files=[a.path] if a.path.is_file() else sorted(a.path.glob("*.npz"))
bad=0
for f in files:
    ok,reason=validate_npz(f,FEATURE_DIM); print(f"{'OK' if ok else 'INVALID'} {f}: {reason}"); bad+=not ok
raise SystemExit(1 if bad else 0)

