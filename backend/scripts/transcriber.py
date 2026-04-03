import os
import json
import time
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG UPDATED ---
DOWNLOAD_DIR = r"utlis\downloads\videos"
TRANSCRIPT_JSON = r"utlis\downloads\transcriptions\transcriptions.json"

# Logic for directories
TRANSCRIPT_DIR = os.path.dirname(TRANSCRIPT_JSON)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

aai.settings.api_key = os.getenv("ASSEMBLY_AI_KEY")

def init_json():
    if not os.path.exists(TRANSCRIPT_JSON):
        with open(TRANSCRIPT_JSON, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_transcripts():
    if not os.path.exists(TRANSCRIPT_JSON): return {}
    try:
        with open(TRANSCRIPT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_transcript(file_name, text):
    data = load_transcripts()
    data[file_name] = {
        "text": text,
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    temp_path = TRANSCRIPT_JSON + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(temp_path, TRANSCRIPT_JSON)

def transcribe_file(file_path):
    print(f"🎙️ Transcribing: {file_path}")
    try:
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            language_detection=True,
            speech_model=aai.SpeechModel.best
        )
        transcript = transcriber.transcribe(file_path, config=config)
        if transcript.status == aai.TranscriptStatus.error:
            return None
        return transcript.text
    except: return None

def transcriber_watcher():
    init_json()
    print(f"👀 Watcher active on: {DOWNLOAD_DIR}")
    while True:
        history = load_transcripts()
        if os.path.exists(DOWNLOAD_DIR):
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith(('.mp4', '.mkv', '.mov'))]
            for file_name in files:
                if file_name in history: continue
                file_path = os.path.join(DOWNLOAD_DIR, file_name)
                try:
                    initial_size = os.path.getsize(file_path)
                    time.sleep(3)
                    if initial_size != os.path.getsize(file_path): continue 
                except: continue
                
                text = transcribe_file(file_path)
                if text:
                    save_transcript(file_name, text)
                    print(f"✅ Transcribed: {file_name}")
        time.sleep(10)

if __name__ == "__main__":
    transcriber_watcher()