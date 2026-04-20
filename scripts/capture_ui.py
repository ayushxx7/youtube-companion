import asyncio
from playwright.async_api import async_playwright
import os

async def capture_companion_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        print("Navigating to YouTube Companion Hub...")
        try:
            await page.goto("http://localhost:8501", wait_until="networkidle")
            await page.wait_for_timeout(5000)
            await page.screenshot(path="showcase/hub_landing.png")
            print("Captured hub_landing.png")
            
            # Switch to Upload Assistant
            await page.goto("http://localhost:8501/upload-assistant", wait_until="networkidle")
            await page.wait_for_timeout(5000)
            await page.screenshot(path="showcase/upload_assistant.png")
            print("Captured upload_assistant.png")
        except Exception as e:
            print(f"Failed to capture UI: {e}")

        await browser.close()

if __name__ == "__main__":
    if not os.path.exists("showcase"):
        os.makedirs("showcase")
    asyncio.run(capture_companion_ui())
