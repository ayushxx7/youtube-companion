"""Capture all views of the yt-dashboard for showcase."""
import asyncio
from playwright.async_api import async_playwright
import os

OUTPUT_DIR = "/Users/air/thevibecoder/projects/self/youtube-companion/showcase/yt-dashboard"
URL = "http://localhost:8503"
VIEWS = ["📊 Public Overview", "🎥 Video Explorer", "📈 Analytics", "🔐 Studio (Coming Soon)"]

async def capture():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for view_name in VIEWS:
            safe_name = view_name.lower().replace(" ", "_").replace("📊", "").replace("🎥", "").replace("📈", "").replace("🔐", "").replace("(", "").replace(")", "").strip("_").strip()
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()
            await page.goto(URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_selector("h1", timeout=10000)
            await asyncio.sleep(3)
            
            # Click the view radio button
            try:
                await page.click(f"text={view_name}", timeout=5000)
                await asyncio.sleep(5)
            except Exception as e:
                print(f"⚠️ Could not click {view_name}: {e}")
            
            filepath = os.path.join(OUTPUT_DIR, f"{safe_name}.png")
            await page.screenshot(path=filepath, full_page=True)
            print(f"✅ Captured {view_name} → {filepath}")
            await context.close()
        
        await browser.close()
        print("🎉 All captures complete!")

asyncio.run(capture())
