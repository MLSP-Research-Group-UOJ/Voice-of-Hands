from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path

TARGET=["clip_id","feature_path","raw_text","clean_text","youtube_video_id","source_url","source_title","start_time","end_time","duration_sec","num_frames","feature_dim","signer_id","split","alignment_status","quality_flag"]
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def duplicates(rows):
    c=Counter(r.get("clip_id","").strip() for r in rows); return sorted(k for k,v in c.items() if k and v>1)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--transcripts",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True); p.add_argument("--unmatched-report",type=Path); p.add_argument("--include-poor",action="store_true"); a=p.parse_args()
    features,transcripts=read(a.metadata),read(a.transcripts)
    for label,rows in (("metadata",features),("transcript",transcripts)):
        if not rows or "clip_id" not in rows[0]: raise ValueError(f"{label} CSV requires clip_id")
    fd,td=duplicates(features),duplicates(transcripts)
    if fd or td: raise ValueError(f"Duplicate clip IDs; metadata={fd}, transcripts={td}")
    fm={r["clip_id"]:r for r in features}; tm={r["clip_id"]:r for r in transcripts}; common=sorted(fm.keys()&tm.keys())
    rows=[]
    for cid in common:
        f,t=fm[cid],tm[cid]
        if f["extraction_status"]=="failed" or (f["quality_flag"]=="poor" and not a.include_poor): continue
        merged={**t,**f,"clip_id":cid,"split":""}; rows.append({k:merged.get(k,"") for k in TARGET})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",encoding="utf-8-sig",newline="") as out:
        w=csv.DictWriter(out,fieldnames=TARGET); w.writeheader(); w.writerows(rows)
    report={"feature_clips_without_text":sorted(fm.keys()-tm.keys()),"transcript_rows_without_features":sorted(tm.keys()-fm.keys()),"excluded_failed_or_poor":[c for c in common if c not in {r['clip_id'] for r in rows}]}
    rp=a.unmatched_report or a.output.with_name(a.output.stem+"_unmatched.json"); rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":main()

