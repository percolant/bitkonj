#!python3

import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
import requests
import json
from bitkonj import api, db


logging.basicConfig(level=logging.INFO)

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_BASEURL = 'https://api.binance.com'
COIN = os.getenv("COIN")
FIAT = os.getenv("FIAT")

headers = {
    'X-MBX-APIKEY': BINANCE_API_KEY
}

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)

def auth(func):

    async def wrapper(message):
        if message['from']['id'] != int(TELEGRAM_USER_ID):
            return await message.reply("Access Denied", reply=False)
        return await func(message)

    return wrapper

@dp.message_handler(commands=['start'])
@auth
async def start(message: types.Message):
    """Not using this for now, find out how asyncio works"""
    await message.reply("bitkonj started")

async def run():
    await bot.send_message(TELEGRAM_CHAT_ID, f"{COIN}/{FIAT} Started. MACD strategy")
    api.init_db()

    while True:
        await asyncio.sleep(900)
        price = api.get_current_price()
        ma10pre = db.get_ma(10)
        ma20pre = db.get_ma(20)
        tick_id = db.save_tick(price=price)
        ma10 = db.get_ma(10)
        ma20 = db.get_ma(20)
        ma50 = db.get_ma(50)
        ma100 = db.get_ma(100)
        if db.get_last_op_type() == 'buy':
            if ma20 > ma100:
                if ma20 > ma50:
                    if ma20 > ma10 and ma10pre > ma20pre:
                        await bot.send_message(
                            TELEGRAM_CHAT_ID,
                            f"SOLD {COIN} for {price} {FIAT}"
                        )
                        api.sell_all(price, tick_id)
        else:
            if ma20 < ma100:
                if ma20 < ma50:
                    if ma20 < ma10 and ma10pre < ma20pre:
                        await bot.send_message(
                            TELEGRAM_CHAT_ID,
                            f"BOUGHT {COIN} for {price} {FIAT}"
                        )
                        api.buy_all(price, tick_id)

def main():
    # executor.start_polling(dp, skip_updates=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
