from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()

URL = "https://www.lamix.org/tools"

@app.get("/")
def home():
    return {"message": "Lamix API running"}

@app.get("/search")
def search(term: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL)
        page.wait_for_selector("#cli-input")

        page.fill("#cli-input", term)
        page.click("#search-btn")

        page.wait_for_load_state("networkidle")
        page.wait_for_selector("li.result-item")

        items = page.query_selector_all("li.result-item")
        total = len(items)

        results = []
        for item in items[:2]:  # only first 2
            name_el = item.query_selector(".country-name")
            fire_el = item.query_selector(".fire-emoji")

            name = name_el.inner_text().strip() if name_el else ""
            fire = " 🔥" if fire_el else ""

            results.append(name + fire)

        browser.close()

        return {
            "term": term,
            "total": total,
            "results": results
        }
