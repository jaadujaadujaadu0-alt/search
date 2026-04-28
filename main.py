from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()

URL = "https://www.lamix.org/tools"


@app.get("/")
def home():
    return {"status": "api running"}


@app.get("/search")
def search(term: str):
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
