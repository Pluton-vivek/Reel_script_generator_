from playwright.sync_api import sync_playwright
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("PASSWORD")
OUTPUT_JSON = r"demoScripts\utlis\downloads\links\target_profiles.json"
LIMIT = 100
HEADLESS = False

def login(page):
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
    except:
        print("⚠️ Login might need verification")
def discover_creators():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()
        page = context.new_page()

        login(page)
        
        print(f"🔍 Accessing discovery pool...")
        page.goto("https://www.instagram.com/explore/people/", wait_until="domcontentloaded")
        time.sleep(4) # Let initial profiles load

        discovered_urls = set()
        last_height = page.evaluate("document.body.scrollHeight")
        
        while len(discovered_urls) < LIMIT:
            # 1. Collect current visible profiles
            links = page.locator('a[href^="/"]').all()
            for link in links:
                href = link.get_attribute("href")
                if href:
                    username = href.strip("/")
                    # Filtering system keywords
                    if "/" not in username and username not in ["explore", "reels", "direct", "stories", "emails", "about"]:
                        profile_reels_url = f"https://www.instagram.com/{username}/reels/"
                        if profile_reels_url not in discovered_urls:
                            discovered_urls.add(profile_reels_url)
                            print(f"✨ Found ({len(discovered_urls)}/{LIMIT}): {username}")
                
                if len(discovered_urls) >= LIMIT: break

            if len(discovered_urls) >= LIMIT: break

            # 2. Scroll down to trigger more loading
            print("📜 Scrolling for more...")
            page.mouse.wheel(0, 4000) 
            time.sleep(3) # Wait for network to fetch next batch

            # 3. Check if we actually scrolled or hit a wall
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                # Try one more aggressive scroll or look for a 'Load More' button
                page.keyboard.press("End")
                time.sleep(2)
                if page.evaluate("document.body.scrollHeight") == last_height:
                    print("🛑 No more profiles loading. Stopping at current count.")
                    break
            last_height = new_height

        # --- SAVE ---
        os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(list(discovered_urls), f, indent=4)
            
        print(f"\n✅ Finished! Collected {len(discovered_urls)} profiles.")
        browser.close()

if __name__ == "__main__":
    discover_creators()