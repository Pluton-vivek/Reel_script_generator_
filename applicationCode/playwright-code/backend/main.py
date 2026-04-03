import os
import json
from fastapi import FastAPI

# imports
from scripts.scraper import scrape_reels_stream
from scripts.downloader import download_reel
from scripts.transcriber import (
    transcribe_file,
    save_transcript
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- HELPER -------- #
def collect_reels(username: str, days=0, months=0, years=0):
    urls = []
    # This might be returning a generator OR a single string by mistake
    stream = scrape_reels_stream(username, days, months, years)

    # 1. Check if stream is just a single string (common bug)
    if isinstance(stream, str):
        print("⚠️ Warning: Scraper returned a string, not a list/generator.")
        stream = [stream] 

    for chunk in stream:
        try:
            # Basic cleanup
            if not isinstance(chunk, str) or not chunk.strip():
                continue
                
            clean_chunk = chunk.replace("data: ", "").strip()
            
            # 2. Attempt to parse JSON
            data = json.loads(clean_chunk)
            
            url = data.get("url")
            status = data.get("status")

            # 3. STRICT VALIDATION: Only accept if status is 'done' AND URL is valid
            if status == "done" and isinstance(url, str):
                if url.startswith("http") and "instagram.com" in url:
                    urls.append(url)
                else:
                    print(f"⚠️ Filtering out invalid URL: {url}")
            
        except (json.JSONDecodeError, TypeError, ValueError):
            # This silently ignores 'a', 'e', and other non-JSON noise
            continue

    return urls


# -------- MAIN PIPELINE -------- #
@app.get("/pipeline")
def run_pipeline(username: str, days: int = 0, months: int = 0, years: int = 0):

    results = []

    print("🚀 Pipeline started")

    # 1️⃣ SCRAPE
    reel_urls = collect_reels(username, days, months, years)

    print(f"🔗 Found {len(reel_urls)} reels")

    if not reel_urls:
        return {"status": "no reels found"}

    # 2️⃣ PROCESS
    for url in reel_urls:
        try:
            if not url.startswith("http"):
                print(f"⚠️ Skipping invalid URL: {url}")
                continue

            print(f"\n⬇️ Processing: {url}")

            # ✅ DOWNLOAD (returns exact file)
            video_path = download_reel(url)

            if not video_path:
                results.append({
                    "url": url,
                    "status": "download_failed"
                })
                continue

            print("🎯 Using file:", video_path)

            # ✅ TRANSCRIBE correct file
            text = transcribe_file(video_path)

            if not text:
                results.append({
                    "url": url,
                    "status": "transcription_failed"
                })
                continue

            # ✅ SAVE
            file_name = os.path.basename(video_path)
            save_transcript(file_name, text)

            results.append({
                "url": url,
                "status": "success",
                "file": file_name,
                "transcription": text
            })

        except Exception as e:
            print("🔥 Pipeline error:", e)

            results.append({
                "url": url,
                "status": "error",
                "error": str(e)
            })

    return {
        "username": username,
        "total": len(results),
        "results": results
    }

from fastapi.responses import StreamingResponse
import json

@app.get("/response")
def run_pipeline(username: str, days: int = 0, months: int = 0, years: int = 0):

    def stream():
        yield "["  # Start JSON array

        first = True  # To handle commas properly

        # 1️⃣ SCRAPE
        reel_urls = collect_reels(username, days, months, years)

        if not reel_urls:
            yield "]"
            return

        # 2️⃣ PROCESS
        for url in reel_urls:
            try:
                if not url.startswith("http"):
                    continue

                video_path = download_reel(url)
                if not video_path:
                    continue

                text = transcribe_file(video_path)
                if not text:
                    continue

                # Build object
                obj = {
                    "reel": url,
                    "transcription": text
                }

                # Add comma if not first item
                if not first:
                    yield ","
                else:
                    first = False

                # Stream JSON object
                yield json.dumps(obj)

            except Exception as e:
                # Optional: include errors as objects
                error_obj = {
                    "reel": url,
                    "error": str(e)
                }

                if not first:
                    yield ","
                else:
                    first = False

                yield json.dumps(error_obj)

        yield "]"  # End JSON array

    return StreamingResponse(stream(), media_type="application/json")