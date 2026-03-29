import requests
import json
import time

# 🔹 Deployed API base URL
BASE_URL = "https://cloud-testing-3yl7.onrender.com"

instagram_usernames = [ 
    "____ubaid_____",
]

def stream_user(username, days=2):
    url = f"{BASE_URL}/scrape/reels?username={username}&days={days}"

    print(f"\n🚀 Starting: {username}")

    try:
        with requests.get(url, stream=True, timeout=300) as response:
            if response.status_code != 200:
                print(f"❌ Error: HTTP {response.status_code}")
                return

            for line in response.iter_lines():
                if not line:
                    continue

                decoded = line.decode()

                if not decoded.startswith("data:"):
                    continue

                try:
                    data = json.loads(decoded.replace("data: ", ""))

                    # ✅ START MESSAGE
                    if data.get("status") == "started":
                        print(f"{username} → 🔄 Stream started")
                        continue

                    # ✅ PROCESSING
                    if data.get("status") == "processing":
                        print(f"{username} → 🔗 {data['url']} (processing...)")
                        continue

                    # ✅ FINAL RESULT
                    if data.get("status") == "done":
                        print(f"{username} → ✅ {data['url']} ({data['posted_on']})")
                        continue

                    # ✅ fallback
                    if "url" in data:
                        print(f"{username} → {data['url']} ({data.get('posted_on')})")
                    else:
                        print(f"{username} → INFO: {data}")

                except Exception as e:
                    print(f"⚠️ Parse error: {e} | Raw: {decoded}")

    except Exception as e:
        print(f"❌ Error for {username}: {e}")


def main():
    for username in instagram_usernames:
        stream_user(username, days=2)
        time.sleep(3)


if __name__ == "__main__":
    main()