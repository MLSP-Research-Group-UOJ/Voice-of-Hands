# Pending Tasks from Implementation vs Specification Analysis

**Document Date**: April 14, 2026  
**Source**: Implementation_vs_Specification_Analysis.md  
**Overall Current Compliance**: 53%

---

## Priority Levels

- 🔴 **CRITICAL**: Breaks core functionality, must implement
- 🟠 **HIGH**: Significantly reduces effectiveness
- 🟡 **MEDIUM**: Specification refinements, nice to have

---

## 🔴 CRITICAL Priority Tasks

### 1. Implement Interpreter Lag (Decalage) Compensation
**Phase**: 3 - Handling Synchronization and Decalage  
**Current Status**: Not implemented (10% compliance)  
**Impact**: HIGH - Breaks speech-sign alignment

**Problem**: Audio and video are currently extracted at the same timestamp, but sign language interpreters lag ~3.36 seconds behind speech.

**Current Implementation**:
```python
# timestamp_extractor.py - Line 380
start_time = i * clip_duration  # ❌ No lag compensation
audio_clip = extract_audio(start_time, duration)
video_clip = extract_video(start_time, duration)
```

**Required Implementation**:
```python
INTERPRETER_LAG = 3.36  # seconds

audio_start = i * clip_duration
video_start = audio_start + INTERPRETER_LAG  # Offset by lag

audio_clip = extract_audio(audio_start, duration)
video_clip = extract_video(video_start, duration)
```

**Files to Modify**:
- `timestamp_extractor.py`
- `run_audio_extraction.py`

**Estimated Effort**: 1-2 days

---

### 2. Add Pre/Post Audio Buffers
**Phase**: 3 - Handling Synchronization and Decalage  
**Current Status**: Not implemented (10% compliance)  
**Impact**: HIGH - May truncate complete gestures

**Problem**: Need buffer windows to ensure complete sign gestures are captured.

**Required Implementation**:
```python
PRE_BUFFER = 2.0   # seconds before audio
POST_BUFFER = 5.0  # seconds after audio

# For video clip with lag compensation
clip_start = audio_start - PRE_BUFFER
clip_end = audio_end + POST_BUFFER + INTERPRETER_LAG
```

**Files to Modify**:
- `timestamp_extractor.py`
- `sli_detector.py`

**Estimated Effort**: 1-2 days

---

## 🟠 HIGH Priority Tasks

### 3. Skeletal Feature Extraction (85-point landmarks)
**Phase**: 5 - Skeletal Feature Extraction  
**Current Status**: MediaPipe used only for detection, not extraction (20% compliance)  
**Impact**: MEDIUM-HIGH - Limits background invariance and increases data size

**Problem**: Currently outputs RGB video (256×256×3 = ~28MB per 5s clip). Should extract skeletal landmarks instead for background-invariant, compact representation.

**Required Landmarks** (85 points total):
- 21 per hand × 2 hands = 42 points
- 6 upper body points (shoulders, elbows, wrists)
- 37 facial expression points

**Required Implementation**:
```python
# New file: skeletal_extractor.py
import mediapipe as mp
import numpy as np

class SkeletalFeatureExtractor:
    def __init__(self):
        self.holistic = mp.solutions.holistic.Holistic(
            static_image_mode=False,
            model_complexity=1
        )
    
    def extract_85_landmarks(self, video_path, output_path):
        """Extract 85-point skeletal features from video"""
        # Extract: 42 hand + 6 body + 37 face = 85 landmarks
        # Save as .npy file instead of RGB video
        pass
```

**Output**: 85 landmarks × 3 coordinates × frames = ~10KB per 5s clip (2800× smaller!)

**Files to Create**:
- `skeletal_extractor.py`

**Files to Modify**:
- `timestamp_extractor.py` (add option for skeletal output)
- `quick_start.py` (add --skeletal flag)

**Estimated Effort**: 2-4 weeks

---

### 4. K=30 Uniform Frame Sampling
**Phase**: 5 - Skeletal Feature Extraction  
**Current Status**: Not implemented (0% compliance)  
**Impact**: MEDIUM - Part of skeletal feature spec

**Problem**: Need to sample exactly 30 frames uniformly spaced across each clip for consistent skeletal representation.

**Required Implementation**:
```python
def uniform_sample_frames(total_frames, k=30):
    """Select K evenly spaced frames"""
    return np.linspace(0, total_frames-1, k, dtype=int)

# In skeletal extraction
sample_indices = uniform_sample_frames(total_frames, k=30)
for idx in sample_indices:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = cap.read()
    # Extract landmarks from this frame
```

**Files to Modify**:
- `skeletal_extractor.py` (new file)

**Estimated Effort**: 2-3 days (part of skeletal extraction)

---

### 5. Save Skeletal Data as .npy Files
**Phase**: 5 - Skeletal Feature Extraction  
**Current Status**: Only RGB video output (0% compliance)  
**Impact**: MEDIUM - Cannot use skeletal features for training

**Problem**: Need to export skeletal landmarks as numpy arrays for ML training.

**Required Output Format**:
```python
# Shape: (30 frames, 85 landmarks, 3 coordinates)
landmarks_array = np.zeros((30, 85, 3))

# Save per clip
np.save('clip_001_landmarks.npy', landmarks_array)

# Metadata
metadata = {
    'clip_id': 'clip_001',
    'landmarks_shape': (30, 85, 3),
    'landmark_types': {
        'left_hand': [0, 21],
        'right_hand': [21, 42],
        'body': [42, 48],
        'face': [48, 85]
    }
}
```

**Files to Create**:
- Update `skeletal_extractor.py` with save functionality

**Files to Modify**:
- `dataset_utils.py` (add skeletal data analysis)

**Estimated Effort**: 1 week

---

### 6. CTC-based Weakly Supervised Alignment
**Phase**: 6 - Deferred Post-Processing  
**Current Status**: Not implemented (0% compliance)  
**Impact**: MEDIUM - Requires manual annotation without this

**Problem**: Need automatic sign boundary detection without frame-level annotation.

**Required Implementation**:
```python
# New file: ctc_aligner.py
import torch
import torch.nn as nn

class SignLanguageCTCAligner(nn.Module):
    def __init__(self, num_signs, hidden_dim=256):
        super().__init__()
        self.encoder = nn.LSTM(85*3, hidden_dim, bidirectional=True)
        self.classifier = nn.Linear(hidden_dim*2, num_signs + 1)
        self.ctc_loss = nn.CTCLoss(blank=0)
    
    def forward(self, skeletal_features):
        # Input: (frames=30, batch, features=85*3)
        encoded, _ = self.encoder(skeletal_features)
        logits = self.classifier(encoded)
        return logits
    
    def align(self, features, transcript):
        """Learn sign boundaries from transcript only"""
        logits = self.forward(features)
        return self.ctc_loss(logits, transcript, ...)
```

**Files to Create**:
- `ctc_aligner.py`
- `train_ctc_alignment.py`

**Dependencies**: PyTorch

**Estimated Effort**: 4-6 weeks

---

### 7. SVO→SOV Grammatical Reordering
**Phase**: 6 - Deferred Post-Processing  
**Current Status**: Not implemented (0% compliance)  
**Impact**: MEDIUM - Linguistic misalignment

**Problem**: Spoken Sinhala (SVO) has different word order than Sri Lankan Sign Language (SOV).

**Required Implementation**:
```python
# New file: linguistic_processor.py
import spacy  # or stanza for Sinhala NLP

class SinhalaToSSLReorderer:
    def __init__(self):
        self.nlp = spacy.load('si_core_news_sm')  # If available
    
    def reorder_svo_to_sov(self, text: str) -> str:
        """Convert Sinhala sentence structure to SSL signing order"""
        doc = self.nlp(text)
        
        # Identify: Subject, Verb, Object
        subject = [t for t in doc if 'subj' in t.dep_]
        verb = [t for t in doc if 'VERB' in t.pos_]
        obj = [t for t in doc if 'obj' in t.dep_]
        
        # Reorder: SVO → SOV
        reordered = subject + obj + verb
        return ' '.join([t.text for t in reordered])
```

**Files to Create**:
- `linguistic_processor.py`

**Files to Modify**:
- `timestamp_extractor.py` (apply reordering to transcriptions)

**Dependencies**: 
- spaCy or Stanza with Sinhala language support
- May need to train custom POS tagger for Sinhala

**Estimated Effort**: 3-4 weeks

---

## 🟡 MEDIUM Priority Tasks

### 8. Raw 10-15s Extraction Windows
**Phase**: 2 - Temporal Segmentation  
**Current Status**: Only 5s direct extraction (60% compliance)  
**Impact**: MEDIUM - Missing prosodic buffer

**Problem**: Specification recommends extracting larger 10-15s raw clips first, then segmenting into 5s training clips.

**Required Architecture**:
```
1. Extract 10-15s RAW clips (prosodic window)
2. Segment RAW into 5s training clips
3. Maintain relationship between raw and processed
```

**Required Implementation**:
```python
# Two-stage extraction
def extract_hierarchical_clips(video_path, output_dir):
    RAW_DURATION = 12.0  # 10-15s range
    TRAIN_DURATION = 5.0
    
    # Stage 1: Extract raw clips
    for i, raw_start in enumerate(range(0, total_duration, RAW_DURATION)):
        raw_clip = extract_video(raw_start, RAW_DURATION)
        raw_path = f"{output_dir}/raw/clip_{i:03d}_raw.mp4"
        
        # Stage 2: Segment raw into training clips
        for j in range(int(RAW_DURATION / TRAIN_DURATION)):
            train_start = j * TRAIN_DURATION
            train_clip = raw_clip[train_start:train_start+TRAIN_DURATION]
            train_path = f"{output_dir}/train/clip_{i:03d}_{j:02d}.mp4"
            
            # Maintain relationship in metadata
            metadata['parent_raw_clip'] = f"clip_{i:03d}_raw.mp4"
```

**Files to Modify**:
- `timestamp_extractor.py`
- `quick_start.py` (add --hierarchical flag)

**Estimated Effort**: 1-2 weeks

---

### 9. Output Frame Normalization
**Phase**: 1 - Spatial Preprocessing  
**Current Status**: Grayscale used only internally for detection (80% compliance)  
**Impact**: LOW - May help with motion blur

**Problem**: Specification recommends grayscale + contrast enhancement for output clips.

**Required Implementation**:
```python
def normalize_output_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Normalize to [0, 1]
    normalized = enhanced / 255.0
    
    return normalized
```

**Files to Modify**:
- `timestamp_extractor.py` (add --normalize flag)
- `sli_detector.py` (option for normalized output)

**Estimated Effort**: 3-5 days

---

### 10. Hierarchical Segmentation Metadata
**Phase**: 2 - Temporal Segmentation  
**Current Status**: Not implemented (0% compliance)  
**Impact**: LOW - Organization improvement

**Problem**: Need to track relationship between raw clips and processed training clips.

**Required Metadata Structure**:
```json
{
  "clip_id": "train_001_02",
  "parent_raw_clip": "raw_001.mp4",
  "parent_timestamp": 10.0,
  "raw_duration": 12.0,
  "train_duration": 5.0,
  "hierarchy_level": "train",
  "siblings": ["train_001_01", "train_001_02", "train_001_03"]
}
```

**Files to Modify**:
- `timestamp_extractor.py` (enhance metadata)
- `dataset_utils.py` (analyze hierarchical relationships)

**Estimated Effort**: 1 week

---

## Summary Table

| # | Task | Phase | Priority | Effort | Compliance |
|---|------|-------|----------|--------|------------|
| 1 | Interpreter lag compensation | 3 | 🔴 Critical | 1-2 days | 10% |
| 2 | Pre/post buffers | 3 | 🔴 Critical | 1-2 days | 10% |
| 3 | Skeletal feature extraction | 5 | 🟠 High | 2-4 weeks | 20% |
| 4 | K=30 frame sampling | 5 | 🟠 High | 2-3 days | 0% |
| 5 | Skeletal .npy output | 5 | 🟠 High | 1 week | 0% |
| 6 | CTC alignment | 6 | 🟠 High | 4-6 weeks | 0% |
| 7 | SVO→SOV reordering | 6 | 🟠 High | 3-4 weeks | 0% |
| 8 | Raw 10-15s windows | 2 | 🟡 Medium | 1-2 weeks | 60% |
| 9 | Output normalization | 1 | 🟡 Medium | 3-5 days | 80% |
| 10 | Hierarchical metadata | 2 | 🟡 Medium | 1 week | 0% |

---

## Already Completed (No Action Needed) ✅

| Component | Compliance |
|-----------|-----------|
| Audio extraction (mono 16kHz PCM) | 100% |
| Whisper ASR transcription | 100% |
| Word-level timestamps | 100% |
| Sinhala language support | 100% |
| Metadata JSON structure | 100% |
| PiP dynamic border detection | 80% (better than spec!) |
| 5-second temporal segmentation | 60% (functional) |

---

## Recommended Implementation Order

### Phase 1: Critical Fixes (Weeks 1-2)
1. Implement interpreter lag offset (**Task 1**)
2. Add pre/post buffer windows (**Task 2**)
3. Test alignment quality on sample data

### Phase 2: Skeletal Pipeline (Weeks 3-6)
4. Create skeletal extractor with MediaPipe Holistic (**Task 3**)
5. Implement K=30 sampling (**Task 4**)
6. Add .npy output format (**Task 5**)
7. Test on dataset, compare video vs skeletal

### Phase 3: Advanced Processing (Weeks 7-12)
8. Implement hierarchical segmentation (**Task 8**)
9. Add output normalization option (**Task 9**)
10. Build CTC alignment module (**Task 6**)
11. Implement linguistic reordering (**Task 7**)
12. Create hierarchical metadata tracking (**Task 10**)

### Phase 4: Validation & Optimization (Weeks 13-14)
- Validate all components on full dataset
- Performance optimization
- Documentation updates
- User testing

---

## Quick Wins (Can implement immediately)

1. **Lag compensation** (Task 1) - Single parameter addition
2. **Output normalization** (Task 9) - Optional flag, backward compatible
3. **K=30 sampling** (Task 4) - Simple numpy operation

---

## Dependencies & Prerequisites

| Task | Dependencies | Prerequisites |
|------|-------------|---------------|
| CTC Alignment | PyTorch, torchaudio | Skeletal features implemented |
| SVO→SOV Reordering | spaCy/Stanza, Sinhala model | NLP pipeline setup |
| Skeletal Extraction | MediaPipe Holistic | None |
| All others | Existing dependencies | Current codebase |

---

## Impact Assessment

**Without implementing CRITICAL tasks**:
- ❌ Dataset will have misaligned speech-sign pairs
- ❌ May train models that learn incorrect temporal relationships
- ❌ Research validity compromised

**Without implementing HIGH priority tasks**:
- ⚠️ Models will be background-dependent
- ⚠️ Larger storage requirements (2800× more space)
- ⚠️ Need manual annotation for sign boundaries
- ⚠️ Linguistic structure mismatches

**Without implementing MEDIUM priority tasks**:
- ℹ️ Loss of prosodic context
- ℹ️ Suboptimal organization
- ℹ️ Minor quality degradation

---

**Last Updated**: April 14, 2026  
**Next Review**: After Phase 1 completion  
**Document Version**: 1.0
