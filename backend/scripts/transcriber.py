import os
import json
from datetime import datetime
from pathlib import Path
import assemblyai as aai

aai.settings.api_key = os.getenv("ASSEMBLY_AI_KEY")

# 🔹 Paths
DOWNLOAD_DIR = Path(r"C:\Users\ramka\Documents\Reel_script_generator_\applicationCode\local\backend\utlis\videos")
OUTPUT_FILE = Path(r"C:\Users\ramka\Documents\Reel_script_generator_\applicationCode\local\backend\utlis\transcriptions.json")

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


# 🔹 Actual transcription logic
def transcribe(video_path):
    print(f"🎙️ Transcribing: {video_path}")
    try:
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            language_detection=True,
            speech_model=aai.SpeechModel.best
        )
        transcript = transcriber.transcribe(video_path, config=config)
        if transcript.status == aai.TranscriptStatus.error:
            return None
        return transcript.text
    except: return None

# 🔹 FIXED: now handles ONE file
def transcribe_file(video_path):
    try:
        text = transcribe(video_path)
        print("✅ Transcription done")
        return text
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None


# 🔹 Save transcription
def save_transcript(video_path, text):
    filename = os.path.basename(video_path)

    data = {}

    # ✅ SAFE READ
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            print("⚠️ Corrupted JSON, resetting file")
            data = {}

    # ✅ UPDATE DATA
    data[filename] = {
        "text": text,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # ✅ ATOMIC WRITE (NO CORRUPTION)
    temp_file = OUTPUT_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    os.replace(temp_file, OUTPUT_FILE)  # 🔥 atomic swap