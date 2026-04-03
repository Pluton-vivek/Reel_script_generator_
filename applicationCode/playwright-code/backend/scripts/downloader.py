import os
import json
import time
import csv
import random
import yt_dlp
from datetime import datetime

# --- CONFIG UPDATED ---
JSON_PATH = r"utlis\downloads\links\reels.json"
DOWNLOAD_DIR = r"utlis\downloads\videos"
CSV_PATH = r"utlis\downloads\status\downloaded.csv"
COOKIE_JSON = r"utlis\cookies\instagram_cookies.json"
COOKIE_TXT = r"utlis\cookies\cookies.txt"

# Ensure directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

def convert_cookies():
    if not os.path.exists(COOKIE_JSON): return None
    try:
        with open(COOKIE_JSON, "r") as f:
            cookies = json.load(f)
        with open(COOKIE_TXT, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            for c in cookies:
                domain = c['domain']
                f.write(f"{domain}\tTRUE\t{c['path']}\t{str(c['secure']).upper()}\t{int(c.get('expires', time.time()+86400))}\t{c['name']}\t{c['value']}\n")
        return COOKIE_TXT
    except: return None

def load_history():
    history = set()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if row: history.add(row[0])
    return history

def log_status(url, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists: writer.writerow(["url", "status", "timestamp"])
        writer.writerow([url, status, timestamp])

def download_reel(url):
    print(f"⬇️ Downloading: {url}")
    cookie_path = convert_cookies()
    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "cookiefile": cookie_path,
        "quiet": True,
        "noplaylist": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        log_status(url, "SUCCESS")
        return True
    except Exception as e:
        log_status(url, f"FAILED: {str(e)[:50]}")
        return False

def watcher():
    print(f"🚀 Watcher started. Monitoring: {JSON_PATH}")
    processed = load_history()
    while True:
        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    reels = json.load(f)
                for item in reels:
                    url = item.get("url")
                    if url and url not in processed:
                        if download_reel(url):
                            processed.add(url)
                            wait = random.randint(2, 7)
                            print(f"⏳ Waiting {wait}s...")
                            time.sleep(wait)
            except: pass 
        time.sleep(5)

if __name__ == "__main__":
    watcher()