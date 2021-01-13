import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
import requests
import json
from util import db, vars


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

    price, coin, action, average_price = db.tick(price)

    if action == 'BUY':
        vars.CURRENT_BTC_BALANCE = vars.CURRENT_USD_BALANCE / price
        vars.CURRENT_USD_BALANCE = 0
        await bot.send_message(
            TELEGRAM_CHAT_ID,
            f"{price} --- {average_price} --- {action} --- {vars.CURRENT_BTC_BALANCE}",
            disable_notification=True
        )
        db.order(price, coin, 'buy')
    elif action == 'SELL':
        vars.CURRENT_USD_BALANCE = vars.CURRENT_BTC_BALANCE * price
        vars.CURRENT_BTC_BALANCE = 0
        await bot.send_message(
            TELEGRAM_CHAT_ID,
            f"{price} --- {average_price} --- {action} --- {vars.CURRENT_USD_BALANCE}",
            disable_notification=True
        )
        db.order(price, coin, 'sell')

async def run():
    while True:
        await report()
        await asyncio.sleep(1)


if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
