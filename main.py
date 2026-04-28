from fastapi import FastAPI
from bot import start_bot, run_search
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI()
telegram_app = start_bot()

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()

    scheduler.add_job(run_search, "interval", minutes=30, args=[telegram_app])
    scheduler.start()

@app.get("/")
def home():
    return {"status": "bot running"}
