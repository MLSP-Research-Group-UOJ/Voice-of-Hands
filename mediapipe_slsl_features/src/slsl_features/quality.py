from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path
from .io import validate_npz
from .landmarks import FEATURE_DIM

def create_summary(metadata: Path, output_dir: Path) -> dict:
    with metadata.open(encoding="utf-8-sig", newline="") as f: rows=list(csv.DictReader(f))
    success=[r for r in rows if r["extraction_status"] in {"success","skipped_existing"}]
    durations=[float(r["duration_sec"]) for r in success]; ids=[r["clip_id"] for r in rows]
    missing=[]
    for r in success:
        p=output_dir/r["feature_path"]; ok,reason=validate_npz(p,FEATURE_DIM)
        if not ok: missing.append({"clip_id":r["clip_id"],"reason":reason})
    ratio_fields=["pose_detected_ratio","left_hand_detected_ratio","right_hand_detected_ratio",
                  "both_hands_detected_ratio","at_least_one_hand_detected_ratio","face_detected_ratio"]
    summary={"total_discovered_clips":len(rows),"successful_clips":sum(r["extraction_status"]=="success" for r in rows),
      "failed_clips":sum(r["extraction_status"]=="failed" for r in rows),"skipped_clips":sum(r["extraction_status"]=="skipped_existing" for r in rows),
      "total_duration_sec":sum(durations),"total_frames":sum(int(r["num_frames"]) for r in success),
      "duration_sec":{"average":sum(durations)/len(durations) if durations else 0,"minimum":min(durations,default=0),"maximum":max(durations,default=0)},
      "average_detection_ratios":{k:(sum(float(r[k]) for r in success)/len(success) if success else 0) for k in ratio_fields},
      "quality_counts":dict(Counter(r["quality_flag"] for r in rows)),
      "lowest_quality_clips":[r["clip_id"] for r in sorted(success,key=lambda x:float(x["at_least_one_hand_detected_ratio"]))[:20]],
      "duplicate_clip_ids":sorted(k for k,v in Counter(ids).items() if v>1),"missing_or_corrupted_outputs":missing}
    (output_dir/"quality_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (output_dir/"quality_summary.txt").write_text("\n".join(f"{k}: {v}" for k,v in summary.items()),encoding="utf-8")
    return summary

