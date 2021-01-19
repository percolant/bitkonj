import os
import requests
import json
import asyncio
from bitkonj import db

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_BASEURL = 'https://api.binance.com'
BTC_BALANCE = float(os.getenv("BTC_BALANCE"))
USD_BALANCE = float(os.getenv("USD_BALANCE"))

headers = {
    'X-MBX-APIKEY': BINANCE_API_KEY
}

def get_current_btc_price():
    params = {
        'symbol': 'BTCUSDT'
    }
    response = requests.get(BINANCE_BASEURL + '/api/v3/ticker/price',
                            headers=headers,
                            params=params)
    if response.status_code == 200:
        return round(float(response.json()['price']))
    else:
        raise Exception(f"Code {response.status_code} from Binance")

def buy_all_btc(price, tick_id):
    global BTC_BALANCE, USD_BALANCE
    BTC_BALANCE = USD_BALANCE / price
    USD_BALANCE = 0
    db.save_order(price=price, op_type='buy', tick_id=tick_id)
    return BTC_BALANCE, USD_BALANCE

def sell_all_btc(price, tick_id):
    global BTC_BALANCE, USD_BALANCE
    USD_BALANCE = BTC_BALANCE * price
    BTC_BALANCE = 0
    db.save_order(price=price, op_type='sell', tick_id=tick_id)
    return BTC_BALANCE, USD_BALANCE

def long_time_no_action(tick_id, price):
    if tick_id - db.get_last_op_id() > 600 \
        and abs(db.get_last_op_price() - price) > 200:
            return True
    elif tick_id - db.get_last_op_id() > 300 \
        and abs(db.get_last_op_price() - price) > 100:
            return True
    else:
        return False
