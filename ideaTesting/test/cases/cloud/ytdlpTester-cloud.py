import json
import requests
import time
import os

# --- PATH FIX ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "server", "downloads", "reels.json"))

API_URL = "https://ytdlpcloud.onrender.com/enqueue"

BATCH_SIZE = 5
DELAY_BETWEEN_BATCHES = 2

# ---------------- LOAD REELS ----------------
def load_reels():
    print("📂 Loading from:", JSON_PATH)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls = [item["url"] for item in data if item.get("url")]

    print("📦 Loaded URLs:", len(urls))
    return urls

# ---------------- SEND BATCH ----------------
def send_batch(batch):
    try:
        response = requests.post(
            API_URL,
            json={
                "urls": batch,
                "force": True   # 🔥 bypass history filter
            }
        )

        print("📡 Response:", response.json())

    except Exception as e:
        print(f"🚨 Error sending batch: {e}")

# ---------------- MAIN ----------------
def main():
    urls = load_reels()

    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i:i + BATCH_SIZE]

        print(f"\n🚀 Sending batch {i//BATCH_SIZE + 1}")
        send_batch(batch)

        time.sleep(DELAY_BETWEEN_BATCHES)

    print("\n🎉 All batches sent!")

if __name__ == "__main__":
    main()