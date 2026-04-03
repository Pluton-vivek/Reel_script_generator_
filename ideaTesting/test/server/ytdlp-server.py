import os
import json
import time
import csv
import random
import yt_dlp
from datetime import datetime
from fastapi import FastAPI
from threading import Thread
from queue import Queue
from pydantic import BaseModel
from typing import List

app = FastAPI()

# --- PATH SETUP (IMPORTANT FIX) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads", "videos")
CSV_PATH = os.path.join(BASE_DIR, "downloads", "status", "downloaded.csv")
COOKIE_JSON = os.path.join(BASE_DIR, "cookies", "instagram_cookies.json")
COOKIE_TXT = os.path.join(BASE_DIR, "cookies", "cookies.txt")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

# --- QUEUE ---
download_queue = Queue()

# ---------------- COOKIES ----------------
def convert_cookies():
    if not os.path.exists(COOKIE_JSON):
        print("⚠️ No cookie JSON found")
        return None

    try:
        with open(COOKIE_JSON, "r") as f:
            cookies = json.load(f)

        with open(COOKIE_TXT, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            for c in cookies:
                domain = c['domain']
                f.write(
                    f"{domain}\tTRUE\t{c['path']}\t"
                    f"{str(c['secure']).upper()}\t"
                    f"{int(c.get('expires', time.time()+86400))}\t"
                    f"{c['name']}\t{c['value']}\n"
                )

        return COOKIE_TXT

    except Exception as e:
        print("❌ Cookie conversion failed:", e)
        return None

# ---------------- HISTORY ----------------
def load_history():
    history = set()

    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)

            for row in reader:
                if row:
                    history.add(row[0])

    print(f"📜 History loaded: {len(history)} items")
    return history

def log_status(url, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(CSV_PATH)

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["url", "status", "timestamp"])

        writer.writerow([url, status, timestamp])

# ---------------- DOWNLOAD ----------------
def download_reel(url):
    print(f"⬇️ Downloading: {url}")

    cookie_path = convert_cookies()

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "cookiefile": cookie_path,
        "quiet": True,
        "noplaylist": True,
        "user_agent": "Mozilla/5.0"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        log_status(url, "SUCCESS")
        return True

    except Exception as e:
        log_status(url, f"FAILED: {str(e)[:80]}")
        print("❌ Download failed:", e)
        return False

# ---------------- WORKER ----------------
def worker():
    print("🚀 Worker started...")

    while True:
        url = download_queue.get()

        if url is None:
            print("🛑 Worker stopping...")
            break

        download_reel(url)

        wait = random.randint(2, 5)
        print(f"⏳ Waiting {wait}s...")
        time.sleep(wait)

        download_queue.task_done()

# ---------------- START WORKER ----------------
@app.on_event("startup")
def start_worker():
    Thread(target=worker, daemon=True).start()

# ---------------- REQUEST MODEL ----------------
class ReelBatch(BaseModel):
    urls: List[str]
    force: bool = False   # 🔥 allow override

# ---------------- API ----------------

@app.get("/")
def home():
    return {"status": "Server running 🚀"}

@app.post("/enqueue")
def enqueue_reels(batch: ReelBatch):
    added = 0
    history = load_history()

    print("📥 Incoming URLs:", len(batch.urls))

    for url in batch.urls:
        if batch.force or url not in history:
            print("➕ Adding:", url)
            download_queue.put(url)
            added += 1
        else:
            print("⛔ Skipped (already in history):", url)

    return {
        "message": "Batch received",
        "queued": added,
        "queue_size": download_queue.qsize()
    }

@app.get("/queue-status")
def queue_status():
    return {"queue_size": download_queue.qsize()}

@app.get("/status")
def get_status():
    history = list(load_history())
    return {"total_downloaded": len(history)}