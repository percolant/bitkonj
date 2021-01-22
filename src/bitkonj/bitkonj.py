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

headers = {
    'X-MBX-APIKEY': BINANCE_API_KEY
}

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)

RUNNING = False

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
    global RUNNING
    RUNNING = True
    await message.reply("bitkonj started")

async def run():
    await bot.send_message(TELEGRAM_CHAT_ID, f"Started.")

    try:
        current_price = api.get_current_btc_price()
        tick_id = db.save_tick(price=current_price)
        db.save_order(
            price=current_price,
            op_type='buy',
            tick_id=tick_id
        )
    except Exception as e:
        await bot.send_message(TELEGRAM_CHAT_ID, f"Error: {e}. STOPPING!")
        return False

    while True:
        current_price = api.get_current_btc_price()
        tick_id = db.save_tick(price=current_price)
        last_op_type = db.get_last_op_type()
        last_op_price = db.get_last_op_price()

        if last_op_type == 'buy':
            # if price diff is < 20, skip
            if abs(last_op_price - current_price) < 20:
                continue

            # if last buy price is < current price -> sell everything
            if last_op_price < current_price:
                try:
                    BTC_BALANCE, USD_BALANCE \
                        = api.sell_all_btc(current_price, tick_id)
                    await bot.send_message(
                        TELEGRAM_CHAT_ID,
                        f"Sold for {current_price}. Balance: {USD_BALANCE} USD."
                    )
                except Exception as e:
                    await bot.send_message(
                        TELEGRAM_CHAT_ID,
                        f"Error: {e}. STOPPING!"
                    )
                    return False
            else:
                if api.long_time_no_action(tick_id, current_price):
                    try:
                        BTC_BALANCE, USD_BALANCE \
                            = api.sell_all_btc(current_price, tick_id)
                        await bot.send_message(
                            TELEGRAM_CHAT_ID,
                            f"Sold for {current_price}. Balance: {USD_BALANCE} USD."
                        )
                    except Exception as e:
                        await bot.send_message(
                            TELEGRAM_CHAT_ID,
                            f"Error: {e}. STOPPING!"
                        )
                        return False

        if last_op_type == 'sell':
            # if price diff is < 20, skip
            if abs(last_op_price - current_price) < 20:
                continue

            # if last sell price is > current price -> buy everything
            if last_op_price > current_price:
                try:
                    BTC_BALANCE, USD_BALANCE \
                        = api.buy_all_btc(current_price, tick_id)
                    await bot.send_message(
                        TELEGRAM_CHAT_ID,
                        f"Bought for {current_price}. Balance: {BTC_BALANCE} BTC."
                    )
                except Exception as e:
                    await bot.send_message(
                        TELEGRAM_CHAT_ID,
                        f"Error: {e}. STOPPING!"
                    )
                    return False
            else:
                if api.long_time_no_action(tick_id, current_price):
                    try:
                        BTC_BALANCE, USD_BALANCE \
                            = api.buy_all_btc(current_price, tick_id)
                        await bot.send_message(
                            TELEGRAM_CHAT_ID,
                            f"Bought for {current_price}. Balance: {BTC_BALANCE} BTC."
                        )
                    except Exception as e:
                        await bot.send_message(
                            TELEGRAM_CHAT_ID,
                            f"Error: {e}. STOPPING!"
                        )
                        return False

        await asyncio.sleep(1)

def main():
    # executor.start_polling(dp, skip_updates=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
