from pathlib import Path
import argparse, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from slsl_features.config import HolisticConfig
from slsl_features.extractor import run
from slsl_features.quality import create_summary

def main():
    p=argparse.ArgumentParser(description="Extract SLSL MediaPipe Holistic landmark sequences")
    p.add_argument("--input-dir",type=Path,required=True); p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--metadata",type=Path); p.add_argument("--recursive",action="store_true")
    p.add_argument("--model-complexity",type=int,choices=(0,1,2),default=1)
    p.add_argument("--min-detection-confidence",type=float,default=.5); p.add_argument("--min-tracking-confidence",type=float,default=.5)
    p.add_argument("--overwrite",action="store_true"); p.add_argument("--max-clips",type=int)
    p.add_argument("--debug-dir",type=Path); p.add_argument("--debug-clips",nargs="*",default=[])
    a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    metadata=a.metadata or a.output_dir/"extraction_metadata.csv"
    cfg=HolisticConfig(model_complexity=a.model_complexity,min_detection_confidence=a.min_detection_confidence,min_tracking_confidence=a.min_tracking_confidence)
    try: run(a.input_dir,a.output_dir,metadata,a.recursive,a.overwrite,a.max_clips,cfg,a.debug_dir,set(a.debug_clips))
    except KeyboardInterrupt: print("Interrupted. Completed outputs and checkpoint metadata are preserved. Re-run the same command to resume."); return 130
    create_summary(metadata,a.output_dir); print(f"Done. Metadata: {metadata}"); return 0
if __name__=="__main__": raise SystemExit(main())

