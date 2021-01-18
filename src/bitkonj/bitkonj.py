#!python3

import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
import requests
import json
from util import db


logging.basicConfig(level=logging.INFO)

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_BASEURL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': BINANCE_API_KEY
}

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)

RUNNING = False

def auth(func):

    async def wrapper(message):
        if message['from']['id'] != TELEGRAM_USER_ID:
            return await message.reply("Access Denied", reply=False)
        return await func(message)

    return wrapper

@dp.message_handler(commands=['start'])
@auth
async def start(message: types.Message):
    global RUNNING = True
    # RUNNING = True
    await message.reply("bitkonj started")

async def main():
    print(RUNNING)

async def run():
    while True:
        await main()
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
