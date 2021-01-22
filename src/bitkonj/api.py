import os
import requests
import json
import asyncio
import hashlib
import hmac
from urllib.parse import urljoin, urlencode
from bitkonj import db

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_BASEURL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': BINANCE_API_KEY
}

def get_current_btc_price():
    params = {
        'symbol': 'BTCEUR'
    }
    response = requests.get(BINANCE_BASEURL + '/api/v3/ticker/price',
                            headers=headers,
                            params=params)
    if response.status_code == 200:
        return round(float(response.json()['price']))
    else:
        raise Exception(f"Code {response.status_code} from Binance")

def buy_all_btc(price, tick_id):
    btc_balance, eur_balance = get_balance()

    URL = '/api/v3/order'
    timestamp = get_server_time()
    params = {
        'symbol': 'BTCEUR',
        'side': 'BUY',
        'type': 'MARKET',
        'quoteOrderQty': eur_balance,
        'timestamp': timestamp
    }

    query_string = urlencode(params)
    params['signature'] = hmac.new(
        BINANCE_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    response = requests.post(urljoin(BINANCE_BASEURL, URL),
                             headers=headers,
                             params=params)
    if response.status_code == 200:
        db.save_order(price=price, op_type='sell', tick_id=tick_id)
        return get_balance()
    else:
        raise Exception(f"Code {response.status_code} from Binance")

def sell_all_btc(price, tick_id):
    btc_balance, eur_balance = get_balance()

    URL = '/api/v3/order'
    timestamp = get_server_time()
    btc_balance = int(float(btc_balance) * (10 ** 6)) / (10 ** 6)
    params = {
        'symbol': 'BTCEUR',
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': btc_balance,
        'timestamp': timestamp
    }

    query_string = urlencode(params)
    params['signature'] = hmac.new(
        BINANCE_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    response = requests.post(urljoin(BINANCE_BASEURL, URL),
                             headers=headers,
                             params=params)
    if response.status_code == 200:
        db.save_order(price=price, op_type='sell', tick_id=tick_id)
        return get_balance()
    else:
        raise Exception(f"Code {response.status_code} from Binance")

def long_time_no_action(tick_id, price):
    if db.get_last_op_type() == 'buy':
        if tick_id - db.get_last_op_id() > 300 \
            and abs(db.get_last_op_price() - price) > 2000:
                return True

        if tick_id - db.get_last_op_id() > 900 \
            and abs(db.get_last_op_price() - price) > 1000:
                return True
    else:
        if tick_id - db.get_last_op_id() > 1800 \
            and abs(db.get_last_op_price() - price) > 2000:
                return True

    return False

def get_server_time():
    URL = '/api/v3/time'
    response = requests.get(urljoin(BINANCE_BASEURL, URL),
                            headers=headers)
    if response.status_code == 200:
        return response.json()['serverTime']
    else:
        raise Exception(f"Code {response.status_code} from Binance")

def get_balance():
    URL = '/sapi/v1/capital/config/getall'
    params = {
        'timestamp': get_server_time()
    }
    query_string = urlencode(params)
    params['signature'] = hmac.new(
        BINANCE_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    response = requests.get(urljoin(BINANCE_BASEURL, URL),
                            headers=headers,
                            params=params)
    if response.status_code == 200:
        for i in response.json():
            if i['coin'] == 'BTC':
                btc_balance = i['free']
            if i['coin'] == 'EUR':
                eur_balance = i['free']
        return btc_balance, eur_balance
    else:
        raise Exception(f"Code {response.status_code} from Binance")
