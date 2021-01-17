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
last_action = 'BUY'
last_buy = 1000
last_sell = 100000
btc_balance = 0.008
usd_balance = 0


def auth(func):

    async def wrapper(message):
        if message['from']['id'] != TELEGRAM_USER_ID:
            return await message.reply("Access Denied", reply=False)
        return await func(message)

    return wrapper

@dp.message_handler(commands=['start', 'help'])
@auth
async def send_welcome(message: types.Message):
    await message.reply("Starting...")

async def report():
    global last_action, last_buy, last_sell, btc_balance, usd_balance
    db.init()

    # GET THE CURRENT PRICE FOR BITCOIN
    params = {
        'symbol': 'BTCUSDT'
    }
    try:
        response = requests.get(BINANCE_BASEURL + '/api/v3/ticker/price',
                                headers=headers,
                                params=params)
    except Exception:
        return False
    if response.status_code == 200:
        price = round(float(response.json()['price']))
    else:
        await bot.send_message(
            TELEGRAM_CHAT_ID,
            f"Код {response.status_code}! Сматываю удочки! ПЕРЕЗАПУСТИ МЕНЯ, БРАТАН!"
        )
        raise Exception(f"{response.status_code} error!")

    if last_buy == 0:
        last_buy = price
    if last_sell == 0:
        last_sell = price
    price, coin, action, average_price = db.tick(price, last_buy, last_sell, last_action)

    if action == 'BUY' and last_action != 'BUY':
        last_action = 'BUY'
        last_buy = price
        btc_balance = usd_balance / price
        usd_balance = 0
        await bot.send_message(
            TELEGRAM_CHAT_ID,
            f"{price} --- {action} --- {btc_balance}",
            disable_notification=True
        )

    if action == 'SELL' and last_action != 'SELL':
        last_action = 'SELL'
        last_sell = price
        usd_balance = btc_balance * price
        btc_balance = 0
        await bot.send_message(
            TELEGRAM_CHAT_ID,
            f"{price} --- {action} --- {usd_balance}",
            disable_notification=True
        )

async def run():
    while True:
        await report()
        await asyncio.sleep(1)


if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
