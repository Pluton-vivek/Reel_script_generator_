from playwright.sync_api import sync_playwright
import time
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG  ---
USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("PASSWORD")
TARGET = "https://www.instagram.com/shahidkapoor/reels/"
BASE = "https://www.instagram.com"

JSON_PATH = r"utlis\downloads\links\reels.json"
COOKIE_JSON = r"utlis\cookies\instagram_cookies.json" 
HEADLESS = False

# Ensure directories exist
os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
os.makedirs(os.path.dirname(COOKIE_JSON), exist_ok=True)
HEADLESS = False

# Ensure directories exist
os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
os.makedirs(os.path.dirname(COOKIE_JSON), exist_ok=True)

def get_cutoff(years=2):
    return datetime.now() - timedelta(days=years * 365)

CUTOFF_DATE = get_cutoff()

def save_session(context):
    cookies = context.cookies()
    with open(COOKIE_JSON, "w", encoding="utf-8") as f:
        json.dump(cookies, f)

def login(page, context):
    page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
    try:
        page.locator('text="Allow all cookies"').click(timeout=5000)
    except: pass

    page.wait_for_selector('input[name="username"], input[name="email"]', timeout=15000)
    try:
        page.fill('input[name="username"]', USERNAME)
    except:
        page.fill('input[name="email"]', USERNAME)
    try:
        page.fill('input[name="password"]', PASSWORD)
    except:
        page.fill('input[name="pass"]', PASSWORD)

    time.sleep(1.5)
    page.locator('text="Log in"').click()
    try:
        page.wait_for_selector('svg[aria-label="Home"]', timeout=15000)
        print("✅ Login successful")
        save_session(context)
    except:
        print("⚠️ Login might need verification")

def get_reel_date(reel_page, url):
    try:
        reel_page.goto(url, wait_until="domcontentloaded")
        time.sleep(1.2)
        reel_page.wait_for_selector("time", timeout=5000)
        dt = reel_page.locator("time").first.get_attribute("datetime")
        return datetime.fromisoformat(dt.replace("Z", ""))
    except: return None

def append_to_json(entry):
    data = []
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: data = []

    if any(item["url"] == entry["url"] for item in data):
        return 

    data.append(entry)
    temp_path = JSON_PATH + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(temp_path, JSON_PATH)
    print(f"💾 Added to JSON: {entry['url']}")

def scrape_reels():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()
        page, reel_page = context.new_page(), context.new_page()
        login(page, context)
        page.goto(TARGET, wait_until="domcontentloaded")
        
        seen, old_streak = set(), 0
        try:
            for scroll in range(50):
                save_session(context)
                links = page.locator('a[href*="/reel/"]')
                for i in range(links.count()):
                    href = links.nth(i).get_attribute("href")
                    if not href: continue
                    url = BASE + href.split('?')[0]
                    if url in seen: continue
                    seen.add(url)
                    
                    date = get_reel_date(reel_page, url)
                    if not date: continue
                    
                    entry = {"url": url, "posted_on": str(date), "is_within_cutoff": date >= CUTOFF_DATE}
                    append_to_json(entry)

                    if date < CUTOFF_DATE: old_streak += 1
                    else: old_streak = 0
                    if old_streak >= 6: return
                page.evaluate("window.scrollBy(0, 2500)")
                time.sleep(2)
        except KeyboardInterrupt: pass
        browser.close()

if __name__ == "__main__":
    scrape_reels()