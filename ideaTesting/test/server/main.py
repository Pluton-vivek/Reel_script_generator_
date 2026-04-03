import asyncio
import sys
import os
import json
import time
import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()

app = FastAPI()

INSTA_USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("PASSWORD")
BASE = "https://www.instagram.com"
COOKIE_JSON = r"cookies/instagram_cookies.json"
os.makedirs(os.path.dirname(COOKIE_JSON), exist_ok=True)

HEADLESS = True


# ---------------- HELPERS ---------------- #

def get_cutoff(days=0, months=0, years=0):
    total_days = days + (months * 30) + (years * 365)
    if total_days == 0:
        total_days = 2
    return datetime.now(timezone.utc) - timedelta(days=total_days)


def save_session(context):
    with open(COOKIE_JSON, "w", encoding="utf-8") as f:
        json.dump(context.cookies(), f)


def login(page, context):
    print("🔑 Logging in...")
    
    page.goto(f"{BASE}/accounts/login/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    try:
        page.wait_for_selector('input[name="email"]', timeout=15000)

        page.fill('input[name="email"]', INSTA_USERNAME)
        page.fill('input[name="pass"]', PASSWORD)

        # 👇 More reliable than get_by_role in IG
        page.locator('text="Log in"').click()

        page.wait_for_timeout(5000)

        # Handle popups
        for _ in range(2):
            try:
                btn = page.locator('button:has-text("Not Now")').first
                if btn:
                    btn.click()
                    time.sleep(1)
            except:
                pass

        page.wait_for_selector('svg[aria-label="Home"], img[alt*="profile"]', timeout=15000)

        print("✅ Login success")
        save_session(context)
        return True

    except Exception as e:
        print(f"🔥 Login failed: {e}")
        page.screenshot(path="login_debug.png")
        return False


def get_reel_date(reel_page, url):
    try:
        reel_page.goto(url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(1)

        reel_page.wait_for_selector("time", timeout=8000)
        dt = reel_page.locator("time").first.get_attribute("datetime")

        if dt:
            return datetime.fromisoformat(dt.replace("Z", "+00:00"))

    except:
        print(f"❌ Failed date: {url}")

    return None


# ---------------- SCRAPER ---------------- #

def scrape_reels_stream(username, days=0, months=0, years=0):
    TARGET = f"{BASE}/{username}/reels/"
    CUTOFF_DATE = get_cutoff(days, months, years)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-dev-shm-usage", "--no-sandbox"]
        )

        context = browser.new_context()
        page = context.new_page()
        reel_page = context.new_page()

        # 🍪 Load cookies
        if os.path.exists(COOKIE_JSON):
            with open(COOKIE_JSON, "r") as f:
                context.add_cookies(json.load(f))
            print("🍪 Cookies loaded")
        else:
            login(page, context)

        # 🚀 Open reels page
        page.goto(TARGET, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        if "login" in page.url:
            print("⚠️ Session expired → relogin")
            login(page, context)
            page.goto(TARGET, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)

        yield f"data: {json.dumps({'status': 'started', 'target': username})}\n\n"

        seen = set()
        old_streak = 0

        try:
            for scroll in range(40):

                # 👇 ORIGINAL WORKING SELECTOR (keep this!)
                links = page.locator('a[href^="/"][href*="/reel/"]:not([href*="?"])')

                count = links.count()

                for i in range(count):
                    try:
                        href = links.nth(i).get_attribute("href")
                    except:
                        continue

                    if not href:
                        continue

                    url = BASE + href.split("?")[0]

                    # ❌ skip junk
                    if url.endswith("/reels/"):
                        continue

                    if url in seen:
                        continue

                    seen.add(url)

                    yield f"data: {json.dumps({'url': url, 'status': 'processing'})}\n\n"

                    date = get_reel_date(reel_page, url)

                    if not date:
                        yield f"data: {json.dumps({'url': url, 'status': 'failed_date'})}\n\n"
                        continue

                    yield f"data: {json.dumps({'url': url, 'posted_on': date.isoformat(), 'status': 'done'})}\n\n"

                    # ✅ SAFE compare
                    if date < CUTOFF_DATE:
                        old_streak += 1
                    else:
                        old_streak = 0

                    if old_streak >= 6:
                        print("⏹️ Cutoff reached")
                        browser.close()
                        return

                # scroll
                page.evaluate("window.scrollBy(0, 2500)")
                time.sleep(random.uniform(2, 4))

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        browser.close()


# ---------------- API ---------------- #

@app.get("/scrape/reels")
def scrape_endpoint(username: str, days: int = 0, months: int = 0, years: int = 0):
    return StreamingResponse(
        scrape_reels_stream(username, days, months, years),
        media_type="text/event-stream"
    )


@app.get("/")
def home():
    return {"status": "ready"}