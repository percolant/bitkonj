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
COIN = os.getenv("COIN")
FIAT = os.getenv("FIAT")

headers = {
    'X-MBX-APIKEY': BINANCE_API_KEY
}

def init_db():
    params = {
        'symbol': f"{COIN}{FIAT}",
        'interval': '15m',
        'limit': 1000
    }
    response = requests.get(BINANCE_BASEURL + '/api/v3/klines',
                            headers=headers,
                            params=params)
    if response.status_code == 200:
        prices1 = []
        ts = response.json()[0][0]
        for p in response.json():
            prices1.append(float(p[4]))
        params = {
            'symbol': f"{COIN}{FIAT}",
            'interval': '15m',
            'limit': 1000,
            'endTime': ts - 1
        }
        response = requests.get(BINANCE_BASEURL + '/api/v3/klines',
                                headers=headers,
                                params=params)
        if response.status_code == 200:
            prices2 = []
            for p in response.json():
                prices2.append(float(p[4]))
            for p in prices2 + prices1:
                tick_id = db.save_tick(price=p)
                current_price = p
            db.save_order(
                price=current_price,
                op_type='buy',
                tick_id=tick_id
            )
        else:
            raise Exception(f"Code {response.status_code} from Binance, {response.json()}")
    else:
        raise Exception(f"Code {response.status_code} from Binance, {response.json()}")

def get_current_price():
    params = {
        'symbol': f"{COIN}{FIAT}",
        'interval': '15m',
        'limit': 1
    }
    response = requests.get(BINANCE_BASEURL + '/api/v3/klines',
                            headers=headers,
                            params=params)
    if response.status_code == 200:
        return response.json()[0][4]
    else:
        raise Exception(f"Code {response.status_code} from Binance, {response.json()}")

def buy_all(price, tick_id):
    cr_balance, f_balance = get_balance()

    URL = '/api/v3/order'
    timestamp = get_server_time()
    params = {
        'symbol': f"{COIN}{FIAT}",
        'side': 'BUY',
        'type': 'MARKET',
        'quoteOrderQty': f_balance,
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
        raise Exception(f"Code {response.status_code} from Binance, {response.json()}")

def sell_all(price, tick_id):
    cr_balance, f_balance = get_balance()

    URL = '/api/v3/order'
    timestamp = get_server_time()
    if COIN == 'BTC':
        cr_balance = int(float(cr_balance) * (10 ** 6)) / (10 ** 6)
    elif COIN == 'ETH':
        cr_balance = int(float(cr_balance) * (10 ** 5)) / (10 ** 5)
    elif COIN == 'AVAX':
        cr_balance = int(float(cr_balance) * (10 ** 2)) / (10 ** 2)
    elif COIN == 'XRP':
        cr_balance = int(float(cr_balance) * (10 ** 1)) / (10 ** 1)
    elif COIN == 'DASH':
        cr_balance = int(float(cr_balance) * (10 ** 5)) / (10 ** 5)
    elif COIN == 'LTC':
        cr_balance = int(float(cr_balance) * (10 ** 5)) / (10 ** 5)
    elif COIN == 'ADA':
        cr_balance = int(float(cr_balance) * (10 ** 1)) / (10 ** 1)

    params = {
        'symbol': f"{COIN}{FIAT}",
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': cr_balance,
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
        raise Exception(f"Code {response.status_code} from Binance, {response.json()}")

def get_server_time():
    URL = '/api/v3/time'
    response = requests.get(urljoin(BINANCE_BASEURL, URL),
                            headers=headers)
    if response.status_code == 200:
        return response.json()['serverTime']
    else:
        raise Exception(f"Code {response.status_code} from Binance, {response.json()}")

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
            if i['coin'] == COIN:
                cr_balance = i['free']
            if i['coin'] == FIAT:
                f_balance = i['free']
        return cr_balance, f_balance
    else:
        raise Exception(f"Code {response.status_code} from Binance, {response.json()}")
