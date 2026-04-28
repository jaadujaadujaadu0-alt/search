from fastapi import FastAPI
from bot import start_bot, run_search
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.sync_api import sync_playwright
import asyncio

app = FastAPI()
telegram_app = start_bot()
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()

    asyncio.create_task(telegram_app.updater.start_polling())

    scheduler.add_job(run_search, "interval", minutes=30, args=[telegram_app])
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()

@app.get("/")
def home():
    return {"status": "bot + api running"}

@app.get("/search")
def search(term: str):
    URL = "https://www.lamix.org/tools"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()
        page.goto(URL)

        page.wait_for_selector("#cli-input")
        page.fill("#cli-input", term)
        page.click("#search-btn")

        page.wait_for_load_state("networkidle")
        page.wait_for_selector("li.result-item")

        items = page.query_selector_all("li.result-item")

        results = []
        for item in items[:2]:
            name = item.query_selector(".country-name").inner_text()
            fire = " 🔥" if item.query_selector(".fire-emoji") else ""
            results.append(name + fire)

        browser.close()

        return {
            "term": term,
            "total": len(items),
            "results": results
        }
