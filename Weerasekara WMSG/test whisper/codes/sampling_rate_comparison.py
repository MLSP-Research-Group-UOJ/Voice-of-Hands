import librosa
from mutagen import File
import pandas as pd
import os

# Folder containing your audio files
audio_folder = r"C:\Users\SITHARA\Desktop\test_whisper\audio"

# Supported audio formats
supported_formats = [".wav", ".m4a"]

results = []

# Read all audio files in folder
for filename in os.listdir(audio_folder):

    file_path = os.path.join(audio_folder, filename)

    # Check file format
    if os.path.splitext(filename)[1].lower() in supported_formats:

        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=None)

            # Get metadata
            audio_info = File(file_path)

            # Duration
            duration = librosa.get_duration(y=audio, sr=sr)

            # Bitrate
            bitrate = getattr(audio_info.info, 'bitrate', 'N/A')

            # Channels
            channels = getattr(audio_info.info, 'channels', 'N/A')

            # File size
            file_size = os.path.getsize(file_path) / (1024 * 1024)

            # Store results
            results.append({
                "File Name": filename,
                "Format": os.path.splitext(filename)[1],
                "Sampling Rate (Hz)": sr,
                "Bitrate": bitrate,
                "Channels": channels,
                "Duration (s)": round(duration, 2),
                "File Size (MB)": round(file_size, 2)
            })

            print(f"Processed: {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Create DataFrame
df = pd.DataFrame(results)

# Save all results into ONE CSV file
output_csv = os.path.join(audio_folder, "all_audio_comparison.csv")

df.to_csv(output_csv, index=False)

print("\nCSV file created successfully!")
print("Saved at:", output_csv)

# Display table
print(df)