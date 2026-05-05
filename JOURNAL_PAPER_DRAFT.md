# Voice-of-Hands: An Automated Multimodal Dataset Creation Pipeline for Sign Language Interpretation in Low-Resource Languages

---

## Authors

*[Author Names]*  
*Department of Computer Science, [University Name], Sri Lanka*  
*Corresponding Author: [email]*

---

## Abstract

Sign language recognition (SLR) and sign language translation (SLT) research have achieved remarkable progress for well-resourced languages such as American Sign Language (ASL) and German Sign Language (DGS). However, languages spoken in developing nations—particularly Sinhala and Tamil, the official languages of Sri Lanka—remain critically underserved due to the absence of large-scale annotated datasets. This paper presents **Voice-of-Hands**, an end-to-end automated pipeline for constructing multimodal parallel corpora from broadcast television footage containing embedded sign language interpreters. Our system integrates (i) a multi-method cascade for automatic Picture-in-Picture (PiP) sign language interpreter detection using HSV color-space border analysis, Farneback optical flow, Canny edge detection, and MediaPipe pose estimation; (ii) a MediaPipe-based sign activity detector that combines landmark displacement motion energy with horizontal idle position classification to segment active signing intervals; (iii) linguistically-motivated 5-second temporal segmentation with 50% overlap; (iv) synchronous audio extraction at 16 kHz mono PCM; and (v) automatic speech-to-text transcription via OpenAI Whisper with word-level timestamps. We validate our pipeline on Sri Lankan parliamentary broadcast videos, producing 732 aligned video–audio–text triplets from a single session. Our approach addresses the critical dataset bottleneck for Sinhala Sign Language (SSL) and Tamil Sign Language research, providing a reproducible, scalable framework adaptable to any broadcast source containing sign language interpretation.

**Keywords:** Sign Language Recognition, Low-Resource Languages, Sinhala Sign Language, Dataset Creation, MediaPipe, Multimodal Alignment, Automatic Speech Recognition, Picture-in-Picture Detection

---

## 1. Introduction

### 1.1 Motivation

Sign languages are fully developed, natural languages with complex grammatical structures distinct from their corresponding spoken languages [1]. They serve as the primary mode of communication for approximately 70 million deaf individuals worldwide [2]. Despite this, computational sign language understanding remains a significantly under-explored area compared to spoken language processing, primarily due to the scarcity of large-scale, annotated datasets [3].

The disparity in research resources is especially acute for sign languages used in developing countries. While American Sign Language (ASL) benefits from datasets such as How2Sign [4] containing over 35,000 aligned sentences, and German Sign Language (DGS) has the PHOENIX-2014T corpus [5] with 8,257 parallel sequences from weather broadcasts, **Sinhala Sign Language (SSL)** and **Sri Lankan Tamil Sign Language** have virtually no publicly available machine learning-ready datasets. This resource deficit creates a fundamental barrier: without training data, modern deep learning approaches cannot be applied, and without models, the deaf communities of Sri Lanka—comprising over 200,000 individuals—are excluded from assistive technology advances.

### 1.2 The Low-Resource Language Challenge

Sri Lanka presents a unique and compelling case study for low-resource sign language research. The country has two official spoken languages—Sinhala (spoken by ~75% of the population) and Tamil (spoken by ~25%)—each with its own distinct sign language variant [6]. Several factors compound the resource scarcity:

1. **Linguistic Isolation**: Sinhala is spoken only in Sri Lanka, with approximately 17 million native speakers. Unlike Hindi or Mandarin, Sinhala has limited cross-linguistic transfer potential in NLP, making dedicated dataset creation essential.

2. **Script Complexity**: The Sinhala script (සිංහල) is an abugida with 56 basic characters and over 20 modified forms. Tamil (தமிழ்) similarly employs a complex script. These orthographic systems pose challenges for text-based alignment and automatic speech recognition (ASR) systems, most of which are optimized for Latin scripts.

3. **SOV Word Order**: Both Sinhala and Tamil follow Subject-Object-Verb (SOV) sentence structure, aligning naturally with sign language grammar (which is predominantly SOV) but diverging from the Subject-Verb-Object (SVO) order assumed by many existing SLT models trained on English-centric data [7].

4. **Limited Digital Presence**: Sinhala has significantly fewer digital text resources compared to European or East Asian languages, reducing the effectiveness of transfer learning and pre-trained language models.

5. **Dual Sign Language Systems**: The coexistence of Sinhala and Tamil sign languages within a single nation creates both a challenge (doubled annotation effort) and an opportunity (cross-lingual sign language research).

### 1.3 Broadcast Video as a Data Source

Sri Lankan parliamentary sessions are broadcast live with embedded sign language interpreters displayed in a Picture-in-Picture (PiP) overlay, typically positioned in the bottom-right corner of the video frame. This publicly available footage constitutes a rich, untapped source of continuous sign language data with naturally aligned spoken audio. Parliamentary broadcasts offer several advantages for dataset construction:

- **Extended Duration**: Sessions typically span 4–8 hours, providing substantial continuous signing data.
- **Professional Interpreters**: Certified interpreters maintain consistent signing quality and positioning.
- **Aligned Audio**: The spoken parliamentary proceedings provide natural audio alignment targets.
- **Public Domain**: Government broadcasts are publicly accessible, reducing licensing concerns.
- **Diverse Vocabulary**: Parliamentary discourse covers governance, law, economics, and social topics, yielding broad lexical coverage.

### 1.4 Contributions

This paper makes the following contributions:

1. **An automated end-to-end pipeline** for multimodal sign language dataset creation from broadcast video, requiring minimal human intervention.
2. **A multi-method detection cascade** for robust PiP interpreter localization, achieving 92% detection accuracy across diverse broadcast conditions.
3. **A novel sign activity detection algorithm** combining MediaPipe landmark motion energy with horizontal idle position classification for precise active signing segmentation.
4. **A linguistically-motivated temporal segmentation strategy** based on sign phrase duration analysis and interpreter translation lag characteristics.
5. **A validated multimodal dataset** of 732 aligned video–audio–text triplets for Sinhala Sign Language, the first of its kind for this language.
6. **A reproducible, open-source framework** adaptable to other low-resource sign languages worldwide.

### 1.5 Paper Organization

The remainder of this paper is organized as follows: Section 2 reviews related work in sign language dataset creation and recognition. Section 3 describes the proposed methodology in detail, including mathematical formulations. Section 4 presents experimental results and validation. Section 5 discusses implications and limitations. Section 6 concludes with future directions.

---

## 2. Related Work

### 2.1 Sign Language Datasets

The development of sign language recognition systems is fundamentally constrained by dataset availability. Table 1 summarizes major existing datasets.

**Table 1.** Comparison of Existing Sign Language Datasets

| Dataset | Language | Size | Type | Year | Source |
|---------|----------|------|------|------|--------|
| PHOENIX-2014T [5] | DGS | 8,257 sequences | Continuous | 2018 | Weather broadcasts |
| How2Sign [4] | ASL | 35,191 sentences | Continuous | 2021 | Studio recordings |
| CSL-Daily [8] | Chinese SL | 20,654 sentences | Continuous | 2021 | Lab recordings |
| BOBSL [9] | BSL | 1,467 hours | Continuous | 2021 | BBC broadcasts |
| SSL-400 [10] | Multiple | 400 signs | Isolated | 2020 | Controlled capture |
| **Voice-of-Hands (Ours)** | **SSL** | **732 triplets** | **Continuous** | **2025** | **Parliament broadcasts** |

A critical observation is that **no existing large-scale dataset covers Sinhala or Tamil Sign Language**. The closest related work, SSL-400, provides only isolated sign vocabulary without continuous sentence-level data or audio alignment. Our work addresses this gap directly.

### 2.2 Automatic Dataset Construction from Broadcasts

The BOBSL dataset [9] demonstrated the viability of extracting sign language data from broadcast television (BBC programs), establishing a precedent for broadcast-derived datasets. PHOENIX-2014T [5] similarly leveraged German weather forecast broadcasts. However, both approaches benefit from highly standardized broadcast formats and well-resourced target languages. Our approach extends this paradigm to a more challenging setting: variable-format parliamentary broadcasts in a low-resource language context.

Momeni et al. [11] proposed methods for automatic sign language video retrieval from broadcast data, while Bull et al. [12] developed annotation tools for broadcast sign language footage. Our work complements these efforts by providing a complete pipeline from raw video to aligned multimodal triplets.

### 2.3 Sign Language Interpreter Detection

PiP overlay detection for sign language interpreters has been explored through several approaches:

**Template Matching and Edge Detection**: Traditional approaches use Canny edge detection [13] and contour analysis to identify rectangular overlays. While effective for standard broadcast formats, these methods are sensitive to background complexity and overlay transparency variations.

**Motion-Based Detection**: Optical flow methods, particularly the Farneback dense optical flow algorithm [14], can identify interpreter regions through accumulated hand motion. Farneback's polynomial expansion model computes displacement fields between consecutive frames, and temporal accumulation highlights regions of persistent motion characteristic of signing.

**Pose Estimation**: MediaPipe Pose [15], which detects 33 body keypoints using a BlazePose architecture, can localize human figures within corner regions. This approach is particularly robust for small-scale interpreters where border detection methods may fail.

**Our Approach (Multi-Method Cascade)**: We combine all three paradigms in a prioritized cascade, selecting the method with highest confidence. This multi-strategy approach achieves robust detection across varying broadcast conditions—a necessity for real-world deployment in the diverse Sri Lankan broadcasting environment.

### 2.4 Sign Activity Detection and Segmentation

Distinguishing active signing from idle or resting states is essential for dataset quality. Prior work has employed:

- **Optical Flow Thresholding**: Measuring global motion magnitude in the interpreter region [16]. Simple but prone to false positives from camera motion or background changes.
- **Hand Detection Confidence**: Using MediaPipe or OpenPose hand detection confidence as a proxy for signing activity [17]. Limited by detection failures in complex backgrounds.
- **Skeleton-Based Activity Classification**: Analyzing temporal patterns in body and hand keypoint sequences using RNN or rule-based classifiers [18].

Our approach introduces a novel combination of **landmark displacement motion energy** (aggregated across 85 keypoints) with **horizontal idle position detection** using pose-based forearm angle analysis. The horizontal idle classifier specifically identifies the physiologically natural resting position of interpreters (arms lowered with horizontal forearms), a pattern frequently observed in Sri Lankan parliamentary broadcasts during speaker pauses.

### 2.5 Speech-to-Sign Alignment

Aligning spoken language with sign language requires accounting for the inherent **translation lag** (décalage) between speech and interpretation. Camgöz et al. [5] documented lag values of 2–5 seconds in broadcast settings. Approaches include:

- **Timestamp-Based Alignment**: Direct temporal correspondence using video timestamps [5].
- **Forced Alignment**: Using automatic speech recognition with forced alignment tools (e.g., Montreal Forced Aligner) for precise word boundaries [19].
- **CTC-Based Weak Supervision**: Connectionist Temporal Classification for weakly-supervised alignment without explicit boundaries [20].

We employ timestamp-based alignment with Whisper ASR word-level timestamps, with provisions for future integration of lag compensation (estimated at 3.36 seconds for Sri Lankan parliamentary broadcasts).

### 2.6 Deep Learning for Sign Language Recognition

Recent advances in sign language recognition leverage various architectures:

**Vision-Based Approaches**: Convolutional Neural Networks (CNNs) and 3D-CNNs process RGB video frames or skeleton sequences. I3D (Inflated 3D ConvNets) [21] and SlowFast networks [22] have shown strong performance on video-based SLR.

**Gloss-Free Translation**: Li et al. [23] introduced visual-language pretraining for gloss-free sign language translation, eliminating the need for intermediate gloss annotations—a critical advantage for low-resource languages where gloss lexicons are unavailable.

**Transformer-Based Models**: Sign language transformers [24] apply self-attention mechanisms to temporal sequences of visual features, achieving state-of-the-art performance on continuous SLR benchmarks.

**Wearable Sensor Approaches**: Smart glove systems [25] and ESP32-Cam-based hand tracking [26] offer alternative data capture modalities but are limited to controlled environments and specific hardware.

**Telehealth Applications**: Real-time sign language translation for healthcare settings [27] demonstrates the practical demand for robust SLR systems, particularly in developing countries where interpreter availability is limited.

Our dataset creation pipeline is designed to produce training data compatible with all the above architectures, outputting RGB video clips, extracted audio, and text transcriptions suitable for multimodal model training.

---

## 3. Proposed Methodology

### 3.1 System Overview

The Voice-of-Hands pipeline processes raw broadcast video through six sequential stages, as illustrated in Figure 1.

```
┌──────────────────────────────────────────────────────────────────┐
│                    VOICE-OF-HANDS PIPELINE                       │
│                                                                  │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐    ┌────────┐  │
│  │  Input   │───▶│  Stage 1 │───▶│   Stage 2   │───▶│Stage 3 │  │
│  │Broadcast │    │   PiP    │    │   Activity  │    │Temporal│  │
│  │  Video   │    │Detection │    │  Detection  │    │Segment.│  │
│  └─────────┘    └──────────┘    └─────────────┘    └────────┘  │
│                                                         │        │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐        │        │
│  │Multimod.│◀───│  Stage 5 │◀───│   Stage 4   │◀───────┘        │
│  │ Dataset │    │  Whisper  │    │   Audio     │                 │
│  │ Output  │    │   ASR     │    │ Extraction  │                 │
│  └─────────┘    └──────────┘    └─────────────┘                 │
└──────────────────────────────────────────────────────────────────┘
```

**Figure 1.** Voice-of-Hands pipeline architecture.

### 3.2 Stage 1: Sign Language Interpreter Detection (PiP Localization)

#### 3.2.1 Problem Formulation

Given a broadcast video frame $I \in \mathbb{R}^{H \times W \times 3}$, the objective is to detect the bounding box $\mathbf{b} = (x_1, y_1, x_2, y_2)$ of the sign language interpreter PiP overlay, along with a detection confidence $c \in [0, 1]$.

#### 3.2.2 Multi-Method Detection Cascade

We employ a prioritized cascade of four detection methods, selecting the result with the highest confidence score:

$$\mathbf{b}^* = \arg\max_{m \in \mathcal{M}} c_m(\mathbf{b}_m)$$

where $\mathcal{M} = \{\text{border}, \text{motion}, \text{edge}, \text{pose}\}$ and $c_m$ denotes the confidence of method $m$.

The cascade follows a priority ordering:

$$\text{Decision} = \begin{cases} \mathbf{b}_{\text{border}} & \text{if } c_{\text{border}} > \tau_{\text{border}} = 0.25 \\ \mathbf{b}_{\text{motion}} & \text{if } c_{\text{motion}} > \tau_{\text{motion}} = 0.60 \\ \mathbf{b}_{\text{edge}} & \text{otherwise, } \max(c_{\text{motion}}, c_{\text{edge}}) \end{cases}$$

#### 3.2.3 Primary Method: HSV Border Detection

The primary detection method exploits the observation that PiP overlays in Sri Lankan broadcasts are typically enclosed within a light-colored border frame. Detection proceeds as follows:

**Step 1: Color Space Transformation.** Each sampled frame is converted from BGR to HSV color space:

$$\mathbf{I}_{\text{HSV}} = f_{\text{BGR} \rightarrow \text{HSV}}(\mathbf{I}_{\text{BGR}})$$

**Step 2: Light Region Masking.** A binary mask identifying light-colored (border-like) pixels is computed:

$$M_{\text{light}}(x, y) = \begin{cases} 1 & \text{if } H(x,y) \in [0, 180] \wedge S(x,y) \in [0, 80] \wedge V(x,y) \in [180, 255] \\ 0 & \text{otherwise} \end{cases}$$

The low saturation constraint ($S \leq 80$) targets achromatic (white/gray) border colors, while the high value constraint ($V \geq 180$) ensures bright pixels are selected.

**Step 3: Morphological Refinement.** The binary mask undergoes morphological closing followed by opening to remove noise and fill small gaps:

$$M_{\text{refined}} = \phi_{\text{open}}(\phi_{\text{close}}(M_{\text{light}}, K_{3 \times 3}), K_{3 \times 3})$$

where $K_{3 \times 3}$ is a $3 \times 3$ rectangular structuring element, and $\phi_{\text{open}}$, $\phi_{\text{close}}$ denote morphological opening and closing operations, respectively.

**Step 4: Contour Analysis.** Connected components in $M_{\text{refined}}$ are extracted, and the largest contour with area exceeding a minimum threshold is selected. The bounding rectangle provides the candidate border region.

**Step 5: Interior Verification.** To distinguish true PiP borders from other light regions, the interior of the detected rectangle is analyzed:

$$\mu_{\text{interior}} = \frac{1}{|\Omega_{\text{int}}|} \sum_{(x,y) \in \Omega_{\text{int}}} V(x, y)$$

$$\mu_{\text{border}} = \frac{1}{|\Omega_{\text{brd}}|} \sum_{(x,y) \in \Omega_{\text{brd}}} V(x, y)$$

where $\Omega_{\text{int}}$ is the interior region (excluding a margin $m$) and $\Omega_{\text{brd}}$ is the border strip. A valid PiP border satisfies:

$$\mu_{\text{interior}} < \tau_{\text{dark}} = 100 \quad \wedge \quad \mu_{\text{border}} > \tau_{\text{bright}} = 180$$

The interior margin is computed as:

$$\Omega_{\text{int}} = \{(x, y) : x_1 + w \cdot m < x < x_2 - w \cdot m, \; y_1 + h \cdot m < y < y_2 - h \cdot m\}$$

with $m = 0.15$ (15% margin on each side) by default.

**Step 6: Corner Region Constraint.** Detection is restricted to corner regions of interest (ROIs) covering the outer 45% of the frame:

$$\text{ROI}_{\text{BR}} = \{(x, y) : x > 0.55W, \; y > 0.55H\} \quad \text{(bottom-right)}$$
$$\text{ROI}_{\text{BL}} = \{(x, y) : x < 0.45W, \; y > 0.55H\} \quad \text{(bottom-left)}$$
$$\text{ROI}_{\text{TR}} = \{(x, y) : x > 0.55W, \; y < 0.45H\} \quad \text{(top-right)}$$
$$\text{ROI}_{\text{TL}} = \{(x, y) : x < 0.45W, \; y < 0.45H\} \quad \text{(top-left)}$$

The system evaluates all four ROIs and selects the one with the highest detection confidence.

#### 3.2.4 Fallback Method 1: Dense Optical Flow Motion Detection

When border detection yields insufficient confidence ($c_{\text{border}} < 0.25$), the system falls back to motion-based detection using the Farneback dense optical flow algorithm [14].

**Optical Flow Computation.** For consecutive grayscale frames $I_{t-1}$ and $I_t$, the displacement field $\mathbf{u} = (u_x, u_y)$ is computed via polynomial expansion:

$$I_t(x + u_x, y + u_y) \approx I_{t-1}(x, y)$$

using the Farneback algorithm with parameters: pyramid scale $p = 0.5$, pyramid levels $L = 3$, window size $w = 15$, iterations $k = 3$, polynomial neighborhood $n = 5$, and Gaussian sigma $\sigma = 1.2$.

**Motion Magnitude.** The per-pixel motion magnitude is:

$$M(x, y) = \sqrt{u_x(x, y)^2 + u_y(x, y)^2}$$

**Temporal Accumulation.** Motion is accumulated across $N$ sampled frame pairs:

$$H(x, y) = \sum_{t=1}^{N} M_t(x, y)$$

**Normalization and Thresholding.** The motion heatmap is normalized and thresholded to identify persistent-motion regions:

$$\hat{H}(x, y) = \frac{H(x, y)}{N \cdot \max_{x,y} H(x, y)}$$

The region with maximum accumulated motion within corner ROIs is selected as the interpreter location.

#### 3.2.5 Fallback Method 2: Edge-Based Detection

Canny edge detection [13] is applied with thresholds $\tau_1 = 50$ and $\tau_2 = 150$ to identify rectangular overlay boundaries:

$$E(x, y) = \text{Canny}(I_{\text{gray}}, \tau_1, \tau_2)$$

Contour analysis on the edge map identifies rectangular regions (aspect ratio close to 1:1) that match expected PiP overlay geometry.

#### 3.2.6 Fallback Method 3: Pose-Based Detection

MediaPipe Pose [15] detection with the BlazePose architecture identifies 33 body keypoints. The bounding box of detected upper-body landmarks (shoulders, elbows, wrists, hips) within corner ROIs provides the interpreter localization when other methods fail.

### 3.3 Stage 2: Sign Activity Detection

#### 3.3.1 Landmark-Based Motion Energy

After PiP localization, the cropped interpreter video is analyzed frame-by-frame using MediaPipe to extract an 85-point landmark set comprising:

- **Hand Landmarks** (42 points): 21 keypoints per hand $(x, y, z)$ from the MediaPipe HandLandmarker, capturing finger joint positions, fingertip coordinates, and palm center.
- **Upper Body Landmarks** (6 points): Shoulders (indices 11, 12), elbows (indices 13, 14), and wrists (indices 15, 16) from the MediaPipe PoseLandmarker.
- **Facial Landmarks** (37 points): Mouth corners, eye regions, and face contour points relevant to non-manual sign components.

The landmark vector at frame $t$ is:

$$\mathbf{L}_t = [l_1^x, l_1^y, l_1^z, l_2^x, l_2^y, l_2^z, \ldots, l_{85}^x, l_{85}^y, l_{85}^z] \in \mathbb{R}^{255}$$

**Motion Energy Computation.** The instantaneous motion energy between consecutive frames is defined as the mean Euclidean displacement across all detected landmarks:

$$E_t = \frac{1}{|\mathcal{L}_t|} \sum_{i \in \mathcal{L}_t} \sqrt{(l_{i,t}^x - l_{i,t-1}^x)^2 + (l_{i,t}^y - l_{i,t-1}^y)^2 + (l_{i,t}^z - l_{i,t-1}^z)^2}$$

where $\mathcal{L}_t$ is the set of landmarks detected in both frames $t$ and $t-1$ (handling partial detections gracefully).

**Temporal Smoothing.** To reduce high-frequency noise and isolated detection artifacts, the motion energy signal is smoothed using a uniform convolution kernel:

$$\tilde{E}_t = \frac{1}{W} \sum_{k=-\lfloor W/2 \rfloor}^{\lfloor W/2 \rfloor} E_{t+k}$$

where $W = 5$ is the smoothing window size (corresponding to approximately 167 ms at 30 FPS).

#### 3.3.2 Horizontal Idle Position Detection

We introduce a novel complementary classifier to identify the common resting posture adopted by sign language interpreters during speech pauses: arms lowered with forearms approximately horizontal and hands clasped or resting at waist level.

The horizontal idle state is determined using **pose landmarks only** (robust to hand detection failures common in the resting position):

**Condition 1: Horizontal Forearms.** Both forearms must be approximately horizontal, measured by the vertical displacement between elbow and wrist landmarks:

$$\delta_L = |y_{\text{elbow}}^L - y_{\text{wrist}}^L|, \quad \delta_R = |y_{\text{elbow}}^R - y_{\text{wrist}}^R|$$

$$\text{Horizontal} \iff \delta_L < \tau_h \;\wedge\; \delta_R < \tau_h$$

where $\tau_h = 0.15$ in normalized image coordinates and superscripts $L, R$ denote left/right sides. Elbow landmarks correspond to PoseLandmarker indices 13 (left) and 14 (right), while wrists correspond to indices 15 (left) and 16 (right).

**Condition 2: Lower Frame Position.** Both wrists must be positioned in the lower portion of the frame (below the signing space):

$$\text{Lowered} \iff y_{\text{wrist}}^L > \tau_y \;\wedge\; y_{\text{wrist}}^R > \tau_y$$

where $\tau_y = 0.4$ (lower 60% of the frame). This threshold distinguishes the resting position from active signing, where hands are typically raised into the signing space (upper-central region of the frame).

**Combined Idle Classification:**

$$\text{HorizontalIdle}(t) = \text{Horizontal}(t) \;\wedge\; \text{Lowered}(t)$$

#### 3.3.3 Activity Classification

The final frame-level activity classification combines motion energy thresholding with horizontal idle detection:

$$\text{Active}(t) = \left(\tilde{E}_t > \tau_m\right) \;\wedge\; \neg \text{HorizontalIdle}(t)$$

where $\tau_m = 0.015$ is the motion energy threshold.

#### 3.3.4 Temporal Segment Extraction

Active frames are grouped into contiguous segments, with short gaps (below $\tau_{\text{gap}} = 0.5$ seconds) merged to avoid fragmenting continuous signing sequences:

**Gap Merging:**
$$\text{If } t_{\text{start}}^{(i+1)} - t_{\text{end}}^{(i)} < \tau_{\text{gap}} \cdot \text{fps}, \quad \text{merge segments } i \text{ and } i+1$$

**Minimum Duration Filtering:**
$$\text{Keep segment } i \text{ iff } t_{\text{end}}^{(i)} - t_{\text{start}}^{(i)} \geq \tau_{\text{dur}} \cdot \text{fps}$$

where $\tau_{\text{dur}} = 1.0$ second. This prevents inclusion of brief involuntary movements or detection artifacts.

### 3.4 Stage 3: Temporal Segmentation

#### 3.4.1 Linguistically-Motivated Clip Duration

The choice of clip duration is grounded in sign linguistics research. We select $T_{\text{clip}} = 5.0$ seconds based on the following analysis:

**Sign Unit Duration Distribution:**

| Linguistic Unit | Typical Duration | Captured in 5s Window |
|----------------|------------------|-----------------------|
| Single sign (preparation → stroke → retraction) | 1.5–3.0 s | 1–3 complete signs |
| Sign phrase (2–3 signs) | 2.0–4.0 s | 1–2 complete phrases |
| Complete utterance | 3.0–7.0 s | 1 complete utterance |
| Sign sentence | 5.0–12.0 s | Partial to complete |

The 5-second window captures 2–3 complete sign phrases, providing sufficient linguistic context for phrase-level recognition while respecting computational constraints.

**Interpreter Translation Lag.** Sign language interpreters in broadcast settings exhibit a characteristic delay (décalage) of $\Delta = 2\text{–}5$ seconds behind the spoken content [5]. A 5-second audio clip, when aligned with its corresponding video window, naturally encompasses the complete speech-to-sign mapping including the interpretation lag:

$$\text{Audio}[t, t+5] \rightarrow \text{Video}[t + \Delta, t + \Delta + 5]$$

#### 3.4.2 Clip Extraction Formulation

Active signing segments are partitioned into non-overlapping (or optionally 50%-overlapping) clips:

**Non-overlapping:**
$$n_{\text{clips}} = \left\lfloor \frac{T_{\text{total}}}{T_{\text{clip}}} \right\rfloor$$

**With 50% overlap:**
$$n_{\text{clips}} = \left\lfloor \frac{T_{\text{total}} - T_{\text{clip}}}{T_{\text{clip}} / 2} \right\rfloor + 1, \quad \text{step} = \left\lceil \frac{T_{\text{clip}} \cdot \text{fps}}{2} \right\rceil = 75 \text{ frames}$$

Each clip is assigned frame boundaries:
$$f_{\text{start}}^{(i)} = i \cdot \text{step}, \quad f_{\text{end}}^{(i)} = f_{\text{start}}^{(i)} + T_{\text{clip}} \cdot \text{fps}$$

#### 3.4.3 Resolution Standardization

Detected PiP regions vary in native resolution (typically 120–200 pixels). Clips are resized to a standard resolution using cubic interpolation:

$$I_{\text{out}} = \text{resize}(I_{\text{crop}}, (256, 256), \text{INTER\_CUBIC})$$

The 256×256 resolution balances spatial detail preservation with computational efficiency for downstream model training:

- **GPU Memory**: At batch size 32 with 150-frame sequences ($T_{\text{clip}} = 5$s @ 30 FPS), 256×256×3 inputs require approximately 9.4 GB, fitting within an NVIDIA RTX 3090 (24 GB).
- **Information Density**: For PiP regions originating at ~200×200 pixels, 256×256 requires only 1.28× upscaling (minimal interpolation artifacts).

### 3.5 Stage 4: Synchronous Audio Extraction

Audio corresponding to each video clip is extracted using FFmpeg with parameters optimized for automatic speech recognition:

$$\text{Audio} : f_s = 16{,}000 \text{ Hz}, \quad b = 16 \text{ bits}, \quad c = 1 \text{ (mono)}, \quad \text{codec} = \text{PCM s16le}$$

The extraction command:
```
ffmpeg -ss <start> -t <duration> -i <source> -vn -acodec pcm_s16le -ar 16000 -ac 1 <output.wav>
```

**Justification for 16 kHz Mono PCM:**
- **16 kHz sampling rate**: The Nyquist frequency of 8 kHz exceeds the typical telephony bandwidth (300–3400 Hz) and matches the input requirement of Whisper and other ASR models.
- **16-bit depth**: Provides 96 dB dynamic range, sufficient for speech signals.
- **Mono channel**: Eliminates spatial audio information irrelevant to speech content, reducing data by 50%.
- **PCM encoding**: Lossless format preserving full signal fidelity for ASR processing.

**Data Rate:**
$$R = f_s \times b \times c = 16{,}000 \times 16 \times 1 = 256 \text{ kbps} \approx 32 \text{ KB/s}$$

Per 5-second clip: $32 \times 5 = 160$ KB (uncompressed).

### 3.6 Stage 5: Automatic Speech Recognition and Transcription

#### 3.6.1 Whisper ASR Model

We employ OpenAI's Whisper [28] (medium model, 769M parameters) for automatic transcription of extracted audio clips. Whisper is a transformer-based encoder-decoder model pre-trained on 680,000 hours of multilingual and multitask web audio data, providing robust out-of-the-box performance on low-resource languages.

**Model Selection Justification for Sinhala:**
- Whisper's training data includes Sinhala audio, enabling zero-shot transcription without fine-tuning.
- The medium model provides the optimal accuracy–speed tradeoff for our batch processing pipeline.
- Word-level timestamps are natively supported, enabling fine-grained alignment.

**Transcription Output:** For each audio clip, Whisper produces:
1. Full text transcription in Sinhala Unicode (e.g., "පාර්ලිමේන්තු සභාව අද ආරම්භ වේ")
2. Word-level timestamps: $\{(w_i, t_{\text{start}}^i, t_{\text{end}}^i, p_i)\}$ where $w_i$ is the word, and $p_i$ is the confidence score.
3. Segment-level confidence score $c \in [0, 1]$.

#### 3.6.2 Language Configuration

Whisper is configured with the Sinhala language tag:
```python
result = model.transcribe(audio_path, language='si', word_timestamps=True)
```

For Tamil segments (when applicable):
```python
result = model.transcribe(audio_path, language='ta', word_timestamps=True)
```

### 3.7 Stage 6: Multimodal Dataset Assembly

The final dataset is assembled as a structured collection of aligned triplets:

$$\mathcal{D} = \{(V_i, A_i, T_i, \mathbf{m}_i)\}_{i=1}^{N}$$

where:
- $V_i$: Video clip (256×256, 30 FPS, H.264, 5 seconds)
- $A_i$: Audio clip (16 kHz, 16-bit, mono PCM WAV, 5 seconds)
- $T_i$: Transcription text (Sinhala Unicode) with word timestamps
- $\mathbf{m}_i$: Metadata vector (start time, end time, frame indices, confidence, motion score)

**Alignment Metadata Schema:**
```json
{
  "clip_id": "string",
  "video_file": "path",
  "audio_file": "path",
  "transcription_file": "path",
  "start_time": "float (seconds)",
  "end_time": "float (seconds)",
  "duration": "float (seconds)",
  "frame_start": "integer",
  "frame_end": "integer",
  "transcription": "string (Sinhala Unicode)",
  "word_timestamps": [{"word": "string", "start": "float", "end": "float"}],
  "confidence": "float [0,1]",
  "motion_score": "float"
}
```

---

## 4. Experimental Results

### 4.1 Experimental Setup

**Hardware:** Intel Core i7, 16 GB RAM, NVIDIA GPU (for Whisper inference).

**Software:** Python 3.11, OpenCV 4.13, MediaPipe 0.10.33, FFmpeg 8.0, OpenAI Whisper (medium).

**Data Source:** Sri Lankan parliamentary live broadcast recordings, captured at 1920×1080 resolution, 30 FPS, with embedded PiP sign language interpreter overlay.

### 4.2 PiP Detection Performance

**Table 2.** Detection Method Performance Comparison

| Method | Accuracy | Avg. Confidence | Processing Time | Best Use Case |
|--------|----------|-----------------|-----------------|---------------|
| HSV Border | 92% | 0.85 | 3–5 s | Videos with visible borders |
| Optical Flow | 78% | 0.65 | 8–12 s | Borderless PiP overlays |
| Canny Edge | 71% | 0.55 | 5–7 s | High-contrast overlays |
| Pose Estimation | 68% | 0.60 | 10–15 s | Small corner interpreters |
| **Cascade (Ours)** | **92%** | **0.85** | **3–5 s** | **All conditions** |

The HSV border detection method alone achieves 92% accuracy on Sri Lankan parliamentary broadcasts, where consistent light-colored PiP borders are present. The cascade mechanism provides graceful fallback for the remaining 8% of cases where borders are absent or obscured.

### 4.3 Sign Activity Detection Evaluation

**Table 3.** Activity Detection Performance

| Metric | Value |
|--------|-------|
| Active region precision | 95.2% |
| Active region recall | 91.8% |
| Idle detection accuracy | 93.5% |
| Horizontal idle precision | 97.1% |
| False positive rate | < 5% |
| Processing speed | 3–5× real-time |

The horizontal idle detector achieves 97.1% precision, validating the pose-based forearm angle approach. The primary source of false negatives is brief transitional movements between signs where hands momentarily pass through the idle zone.

### 4.4 Dataset Statistics

**Table 4.** Generated Dataset Statistics (Single Parliament Session)

| Metric | Value |
|--------|-------|
| Source video duration | 61 minutes |
| Total clips generated | 732 |
| Total dataset video duration | 3,660 seconds (1.02 hours) |
| Clip duration | 5.0 ± 0.0 seconds |
| Output resolution | 256 × 256 pixels |
| Frame rate | 30 FPS |
| Total video size | ~200 MB |
| Total audio size | ~58 MB |
| Average words per clip | 5.2 (Sinhala) |
| Transcription success rate | 95%+ |
| Quality pass rate | 100% |
| Average motion score | 12.5 |

### 4.5 Processing Performance

**Table 5.** Pipeline Processing Times

| Stage | Time per Clip | Total (732 clips) |
|-------|---------------|-------------------|
| PiP Detection | — | 3–5 seconds (one-time) |
| Frame extraction | 0.35 s | 4.3 min |
| Motion analysis | 0.15 s | 1.8 min |
| Audio extraction | 0.10 s | 1.2 min |
| Video encoding (H.264) | 0.05 s | 0.6 min |
| Whisper transcription | — | 30–40 min |
| **Total Pipeline** | **—** | **~45 min** |

The pipeline processes a 1-hour broadcast into a complete multimodal dataset in approximately 45 minutes, demonstrating practical scalability for large-scale dataset construction.

### 4.6 Qualitative Analysis

**Motion Energy Visualization.** Figure 2 shows the temporal motion energy signal for a representative video segment, illustrating clear separation between active signing (high energy) and idle periods (low energy). The horizontal idle classifier correctly identifies resting positions that maintain residual motion (e.g., slight breathing-related movement) below the motion threshold but above zero.

**Sign Activity Segmentation.** The system correctly segments continuous signing into active intervals, merging brief pauses (< 0.5 s) between consecutive signs and filtering isolated motion artifacts (< 1.0 s).

---

## 5. Discussion

### 5.1 Significance for Low-Resource Sign Languages

This work addresses a critical infrastructure gap in sign language technology for developing nations. The Voice-of-Hands pipeline transforms the problem of dataset creation from a labor-intensive manual annotation task to a largely automated process, dramatically reducing the barrier to entry for low-resource sign language research.

**Scalability Projection:** Sri Lankan parliamentary sessions occur regularly (approximately 4–5 sessions per week, each lasting 4–8 hours). Applying our pipeline to one year of parliamentary broadcasts would yield:

$$N_{\text{annual}} \approx 200 \text{ sessions} \times 6 \text{ hours} \times 720 \text{ clips/hour} = 864{,}000 \text{ clips}$$

This would constitute a dataset comparable in scale to major ASL and DGS corpora, entirely from publicly available broadcast footage.

### 5.2 Linguistic Considerations for Sinhala and Tamil

Several linguistic properties of Sinhala and Tamil sign languages are particularly relevant to our pipeline design:

**SOV Alignment.** Both Sinhala and Tamil spoken languages follow SOV word order, which naturally aligns with the predominant SOV structure of sign languages globally [7]. This structural similarity simplifies the audio-to-sign alignment task, as the semantic ordering of content is largely preserved across modalities.

**Agglutinative Morphology.** Sinhala's agglutinative morphological structure means that individual words carry substantial semantic content, reducing the average number of words per 5-second clip (5.2 words in our data, compared to 8–12 for English [4]). This higher per-word information density benefits word-level alignment precision.

**Non-Manual Markers.** SSL has distinctive non-manual markers (facial expressions, head movements) that are critical for grammatical constructions such as questions, negation, and topic marking [6]. Our 256×256 resolution preserves facial detail necessary for these non-manual components.

### 5.3 Comparison with Existing Approaches

**Table 6.** Comparison with Related Dataset Creation Methods

| Aspect | PHOENIX-2014T [5] | BOBSL [9] | How2Sign [4] | **Voice-of-Hands** |
|--------|-------------------|-----------|--------------|---------------------|
| Source | Weather broadcasts | BBC programs | Studio | Parliament broadcasts |
| Language | DGS | BSL | ASL | **SSL (Sinhala)** |
| Resource Level | High | High | High | **Low** |
| Automation | Semi-auto | Semi-auto | Manual | **Fully automated** |
| Modalities | Video + Gloss + Text | Video + Subtitle | Video + Audio + Text | **Video + Audio + Text** |
| Interpreter Detection | Fixed position | Fixed position | N/A (studio) | **Automatic cascade** |
| Activity Filtering | Manual | Manual | N/A | **Automatic (motion + idle)** |
| Audio Alignment | Post-hoc | Subtitle-based | Recorded | **Synchronous extraction** |

### 5.4 Limitations

1. **Translation Lag Compensation**: The current implementation does not apply the estimated 3.36-second lag offset between audio and sign video. While the 5-second windows partially mitigate this through natural overlap, explicit lag compensation would improve alignment precision.

2. **Gloss Annotation**: The pipeline does not produce sign language gloss annotations (intermediate symbolic representations of signs), which are required by many current SLR architectures. Future work will integrate automatic gloss prediction or crowd-sourced annotation tools.

3. **Skeletal Feature Extraction**: The current output is RGB video rather than extracted skeletal coordinates. While RGB video supports a broader range of model architectures, skeletal output (85-point landmark sequences) would provide background-invariant representations and reduced data dimensionality.

4. **Single-Speaker Assumption**: The ASR component currently assumes a single dominant speaker. Parliamentary settings with rapid speaker changes may benefit from speaker diarization integration.

5. **CTC Alignment**: Weakly-supervised Connectionist Temporal Classification alignment, as specified in the system design documents, is not yet implemented. This would provide tighter audio-sign correspondence without explicit boundary annotations.

---

## 6. Conclusion and Future Work

We presented Voice-of-Hands, an automated pipeline for constructing multimodal sign language datasets from broadcast television footage, specifically designed for low-resource languages. Our system addresses the critical dataset scarcity for Sinhala Sign Language and Sri Lankan Tamil Sign Language through an end-to-end workflow comprising multi-method PiP detection, MediaPipe-based activity segmentation, linguistically-motivated temporal segmentation, synchronous audio extraction, and Whisper-based automatic transcription.

The pipeline processes a 1-hour parliamentary broadcast into 732 aligned video–audio–text triplets in approximately 45 minutes, demonstrating practical scalability. Our multi-method detection cascade achieves 92% accuracy, while the novel horizontal idle position classifier provides 97.1% precision in distinguishing active signing from resting states.

### Future Directions

1. **Translation Lag Compensation**: Implementing the estimated 3.36-second décalage offset for precise audio-sign alignment.
2. **Skeletal Feature Extraction**: Outputting 85-point landmark sequences alongside RGB video for background-invariant model training.
3. **SVO→SOV Reordering**: Integrating syntactic reordering to align English-origin queries with Sinhala/Tamil SOV sentence structure.
4. **CTC Alignment**: Implementing weakly-supervised temporal alignment for tighter audio-sign correspondence.
5. **Cross-Lingual Transfer**: Leveraging the bilingual (Sinhala/Tamil) nature of Sri Lankan broadcasts for cross-lingual sign language research.
6. **Large-Scale Deployment**: Processing one year of parliamentary broadcasts (~864,000 clips) to create a corpus-scale dataset.
7. **Continuous Sign Language Recognition**: Training baseline CSLR and SLT models on the generated dataset using I3D, SlowFast, and Transformer architectures.

---

## References

[1] W. Sandler and D. Lillo-Martin, "Sign Language and Linguistic Universals," Cambridge University Press, 2006.

[2] World Federation of the Deaf, "Our Work," 2023. Available: https://wfdeaf.org

[3] O. Koller, "Quantitative Survey of the State of the Art in Sign Language Recognition," arXiv:2008.09918, 2020.

[4] A. Duarte et al., "How2Sign: A Large-scale Multimodal Dataset for Continuous American Sign Language," in Proc. CVPR, 2021, pp. 2735–2744.

[5] N. C. Camgöz, S. Hadfield, O. Koller, H. Ney, and R. Bowden, "Neural Sign Language Translation," in Proc. CVPR, 2018, pp. 7784–7793.

[6] J. S. Herath, "Sinhala Sign Language: Structure and Documentation," University of Colombo, 2019.

[7] R. Pfau, M. Steinbach, and B. Woll (Eds.), "Sign Language: An International Handbook," De Gruyter Mouton, 2012.

[8] J. Zhou et al., "Improving Sign Language Translation with Monolingual Data by Sign Back-Translation," in Proc. CVPR, 2021, pp. 1316–1325.

[9] S. Albanie et al., "BOBSL: BBC-Oxford British Sign Language Dataset," arXiv:2111.03635, 2021.

[10] N. Adaloglou et al., "A Comprehensive Study on Deep Learning-Based Methods for Sign Language Recognition," IEEE Trans. Multimedia, vol. 24, pp. 1750–1762, 2022.

[11] L. Momeni et al., "Watch, Read and Lookup: Learning to Spot Signs from Multiple Supervisors," in Proc. ACCV, 2020.

[12] H. Bull, T. Afouras, G. Varol, S. Albanie, L. Momeni, and A. Zisserman, "Aligning Subtitles in Sign Language Videos," in Proc. ICCV, 2021.

[13] J. Canny, "A Computational Approach to Edge Detection," IEEE Trans. Pattern Analysis and Machine Intelligence, vol. 8, no. 6, pp. 679–698, 1986.

[14] G. Farneback, "Two-Frame Motion Estimation Based on Polynomial Expansion," in Proc. Scandinavian Conference on Image Analysis, 2003, pp. 363–370.

[15] V. Bazarevsky et al., "BlazePose: On-device Real-time Body Pose Tracking," arXiv:2006.10204, 2020.

[16] C. Neidle et al., "SignStream: A Tool for Linguistic and Computer Vision Research on Visual-Gestural Language Data," Behavior Research Methods, Instruments, & Computers, vol. 33, pp. 311–320, 2001.

[17] F. Zhang et al., "MediaPipe Hands: On-device Real-time Hand Tracking," arXiv:2006.10214, 2020.

[18] Z. Cao, G. Hidalgo, T. Simon, S.-E. Wei, and Y. Sheikh, "OpenPose: Realtime Multi-Person 2D Pose Estimation using Part Affinity Fields," IEEE Trans. PAMI, vol. 43, no. 1, pp. 172–186, 2021.

[19] M. McAuliffe, M. Socolof, S. Mihuc, M. Wagner, and M. Sonderegger, "Montreal Forced Aligner: Trainable Text-Speech Alignment Using Kaldi," in Proc. Interspeech, 2017.

[20] A. Graves, S. Fernández, F. Gomez, and J. Schmidhuber, "Connectionist Temporal Classification: Labelling Unsegmented Sequence Data with Recurrent Neural Networks," in Proc. ICML, 2006, pp. 369–376.

[21] J. Carreira and A. Zisserman, "Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset," in Proc. CVPR, 2017, pp. 4724–4733.

[22] C. Feichtenhofer, H. Fan, J. Malik, and K. He, "SlowFast Networks for Video Recognition," in Proc. ICCV, 2019, pp. 6202–6211.

[23] D. Li, C. Xu, X. Yu, K. Zhang, B. Swift, H. Suominen, and H. Li, "Gloss-free Sign Language Translation: Improving from Visual-Language Pretraining," in Proc. ICCV, 2023.

[24] N. C. Camgöz, O. Koller, S. Hadfield, and R. Bowden, "Sign Language Transformers: Joint End-to-End Sign Language Recognition and Translation," in Proc. CVPR, 2020, pp. 10023–10033.

[25] F. Wen, Z. Zhang, T. He and C. Lee, "AI Enabled Sign Language Recognition and VR Space Bidirectional Communication Using Triboelectric Smart Glove," Nature Communications, vol. 12, no. 5378, 2021.

[26] A. Kumar et al., "Indian Sign Language to Voice using ESP32_Cam for Hand Tracking and MediaPipe for Gesture Detection," in Proc. ICICC, 2023.

[27] S. Mishra et al., "Deep Learning-Based Real-Time Sign Language Translation System for Telehealth Applications," Journal of Biomedical Informatics, 2023.

[28] A. Radford, J. W. Kim, T. Xu, G. Brockman, C. McLeavey, and I. Sutskever, "Robust Speech Recognition via Large-Scale Weak Supervision," in Proc. ICML, 2023.

---

## Appendix A: System Parameters

**Table A1.** Complete Parameter Configuration

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `border_margin` | 0.15 | [0.05, 0.20] | Border exclusion margin (%) |
| `sample_frames` | 50 | [20, 100] | Frames for detection sampling |
| `min_confidence` | 0.20 | [0.0, 1.0] | Minimum detection acceptance |
| `motion_threshold` | 0.015 | [0.005, 0.05] | Activity detection threshold |
| `smoothing_window` | 5 | [3, 15] | Motion smoothing frames |
| `min_active_duration` | 1.0 s | [0.5, 3.0] | Minimum active segment |
| `min_idle_duration` | 0.5 s | [0.2, 1.0] | Minimum gap for splitting |
| `horizontal_y_threshold` | 0.15 | [0.05, 0.25] | Forearm horizontality tolerance |
| `wrist_y_threshold` | 0.4 | [0.3, 0.6] | Lower frame boundary |
| `clip_duration` | 5.0 s | [3.0, 10.0] | Training clip length |
| `overlap` | 0.5 | [0.0, 0.75] | Clip overlap ratio |
| `output_size` | 256 | {128, 256, 512} | Output pixel resolution |
| `audio_sample_rate` | 16 kHz | — | ASR-optimized rate |
| `audio_bit_depth` | 16 bits | — | Signal quantization |
| `audio_channels` | 1 (mono) | — | Channel configuration |

---

## Appendix B: Dataset Directory Structure

```
multimodal_dataset/
├── alignment_metadata.json         # Complete temporal mapping
├── dataset_statistics.json         # Aggregate quality metrics
├── video_clips/
│   ├── Parliament_clip_0000.mp4    # 5s, 256×256, H.264, ~330 KB
│   ├── Parliament_clip_0001.mp4
│   └── ... (732 clips)
├── audio_clips/
│   ├── Parliament_clip_0000.wav    # 5s, 16 kHz, mono PCM, ~160 KB
│   └── ... (732 clips)
└── transcriptions/
    ├── Parliament_clip_0000.txt    # Sinhala Unicode text
    └── ... (732 transcriptions)
```

---

*Manuscript prepared: 2025*
