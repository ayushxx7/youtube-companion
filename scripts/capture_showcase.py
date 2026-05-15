import asyncio
from playwright.async_api import async_playwright
import os

async def capture_youtube_companion():
    os.makedirs("showcase", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Capture Analytics Dashboard
        print("📊 Capturing Analytics Intelligence Dashboard...")
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        await page.goto("http://localhost:8502", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(5000)
        await page.screenshot(path="showcase/analytics_dashboard.png", full_page=False)
        print("  ✓ analytics_dashboard.png")
        
        # Capture a second tab view (Video Deep Dive)
        await page.get_by_text("Video Deep Dive").click()
        await page.wait_for_timeout(3000)
        await page.screenshot(path="showcase/analytics_deep_dive.png", full_page=False)
        print("  ✓ analytics_deep_dive.png")
        
        await browser.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(capture_youtube_companion())
