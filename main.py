import os
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("BOT_TOKEN")

START_TIME = datetime.strptime("08:00", "%H:%M")
PAIR_DURATION = 80
BREAK_DURATION = 10

def pair_time(pair_number):
    minutes = (pair_number - 1) * (PAIR_DURATION + BREAK_DURATION)
    start = START_TIME + timedelta(minutes=minutes)
    end = start + timedelta(minutes=PAIR_DURATION)
    return start.strftime("%H:%M"), end.strftime("%H:%M")

async def main():
    print("Bot is running")

if __name__ == "__main__":
    asyncio.run(main())
