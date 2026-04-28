from fastapi import FastAPI
from bot import start_bot, run_search
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

app = FastAPI()
telegram_app = start_bot()
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup():
    # initialize bot
    await telegram_app.initialize()
    await telegram_app.start()

    # ✅ CORRECT WAY: start polling WITHOUT breaking loop
    asyncio.create_task(telegram_app.updater.start_polling())

    # scheduler
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
