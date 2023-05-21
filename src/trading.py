from binance.client import Client
import time
import requests
import hmac
import hashlib

from src.logger import logger


class BinanceLeverage:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret, testnet=True)
        self.leverage_mapping = {}
        self.client.API_URL = Client.API_TESTNET_URL

    def change_leverage(self, symbol, leverage):
        try:
            self.leverage_mapping[symbol] = leverage
            self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
        except Exception as e:
            logger.warning(f"Error changing leverage for {symbol} to {leverage}. Error: {str(e)}")


def get_server_time():
    """
    Get Binance server time.
    """
    URL = "https://testnet.binancefuture.com/fapi/v1/time"
    response = requests.get(URL)
    return response.json()["serverTime"]


class BinanceBalance:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret, testnet=True)
        self.client.API_URL = Client.API_TESTNET_URL

    def get_max_qty(self, symbol, leverage):
        account_balance = self.client.futures_account_balance()
        ticker_price = self.client.futures_symbol_ticker(symbol=symbol)
        mark_price = float(ticker_price['price'])
        for asset in account_balance:
            if asset['asset'] == symbol[-4:]:
                balance = float(asset['balance'])
        return balance * leverage / mark_price


class BinanceOrder:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret, testnet=True)
        self.leverage = BinanceLeverage(api_key, api_secret)
        self.balance = BinanceBalance(api_key, api_secret)
        self.client.API_URL = Client.API_TESTNET_URL

    def get_precision(self, symbol):
        info = self.client.futures_exchange_info()
        for x in info['symbols']:
            if x['symbol'] == symbol:
                return x['quantityPrecision']

    def create_order(self, side, symbol, leverage, price, quantity=None, max_quantity_ratio=0.1):
        logger.warning(self)
        self.leverage.change_leverage(symbol, leverage)
        if not quantity:
            quantity = self.balance.get_max_qty(symbol, leverage) * max_quantity_ratio
        precision = self.get_precision(symbol)
        quantity = float(round(quantity, precision))

        params = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'timeInForce': 'GTC',
            'quantity': quantity,
            'closePosition': price,
            'recvWindow': 5000,
            'timestamp': get_server_time()
        }

        logger.warning('p========EDUARDO _ PRIVATE KEY =======' + self.client.API_SECRET)
        logger.warning('p========EDUARDO _ params =======' + str(params))
        logger.warning('p========EDUARDO _ API KEY =======' + self.client.API_KEY)


        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(self.client.API_SECRET.encode('utf-8'), query_string.encode('utf-8'),
                             hashlib.sha256).hexdigest()

        params['signature'] = signature

        self.client.futures_create_order(**params)


class BinanceTrading:
    def __init__(self, api_key, api_secret):
        self.order = BinanceOrder(api_key, api_secret)
    def buy(self, symbol, leverage, price, quantity=None, max_quantity_ratio=0.1):
        self.order.create_order(Client.SIDE_BUY, symbol, leverage, price, quantity, max_quantity_ratio)

    def sell(self, symbol, leverage, price, quantity=None, max_quantity_ratio=0.1):
        self.order.create_order(Client.SIDE_SELL, symbol, leverage, price, quantity, max_quantity_ratio)
