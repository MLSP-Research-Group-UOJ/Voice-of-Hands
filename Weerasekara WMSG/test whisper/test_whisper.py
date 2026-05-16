import whisper
import os

# ==============================
# 🔹 SETTINGS
# ==============================

MODEL_SIZE = "small"   # "small" / "medium"
AUDIO_FILE = "audio/audio4.m4a"  # 👉 එක audio file එක
OUTPUT_FOLDER = "transcriptions"

# ==============================
# 🔹 LOAD MODEL
# ==============================

print(f"Loading Whisper model: {MODEL_SIZE}...")
model = whisper.load_model(MODEL_SIZE, device="cuda")

# ==============================
# 🔹 CREATE OUTPUT FOLDER
# ==============================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==============================
# 🔹 TRANSCRIBE SINGLE FILE
# ==============================

print(f"\nProcessing: {AUDIO_FILE}")

try:
    result = model.transcribe(
    AUDIO_FILE,   
    language="si",
    task="transcribe"
)

    base_name = os.path.splitext(os.path.basename(AUDIO_FILE))[0]

    # Save text
    output_file = os.path.join(OUTPUT_FOLDER, base_name + ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])

    # Save timestamps
    timestamp_file = os.path.join(OUTPUT_FOLDER, base_name + "_timestamps.txt")
    with open(timestamp_file, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            f.write(f"[{start:.2f}s - {end:.2f}s] {text}\n")

    print("\nTranscription:")
    print(result["text"])
    print(f"Saved: {output_file}")

except Exception as e:
    print(f"Error: {e}")

# ==============================
# 🔹 DONE
# ==============================

print("\n✅ Done!")