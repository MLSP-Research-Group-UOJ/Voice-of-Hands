import whisper
import time

# =========================
# AUDIO FILE
# =========================
AUDIO_FILE = "audio8.wav"   # change your audio file path here

# =========================
# MODELS TO TEST
# =========================
models = ["tiny", "base", "small"]

# =========================
# RUN ALL MODELS
# =========================
for model_name in models:

    print("\n" + "="*50)
    print(f"Loading Model : {model_name}")
    print("="*50)

    # Load model
    model = whisper.load_model(model_name)

    # Start time
    start = time.time()

    # Transcribe audio
    result = model.transcribe(AUDIO_FILE)

    # End time
    end = time.time()

    # Processing time
    processing_time = end - start

    # =========================
    # OUTPUT
    # =========================
    print(f"\nModel : {model_name}")
    print(f"Processing Time : {processing_time:.2f} seconds")

    print("\nTranscribed Text:")
    print(result["text"])

    print("\nDetected Language:")
    print(result["language"])

print("\nCompleted Testing All Models!")