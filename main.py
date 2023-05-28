from flask import Flask, request
import requests
import json
import os
from src.trading import BinanceTrading
from src.logger import logger

app = Flask(__name__)

binance_trading = BinanceTrading(os.environ.get('API_KEY'), os.environ.get('API_SECRET_KEY'))


@app.route('/webhook', methods=['POST'])
def tradingview_request():
    data = json.loads(request.data)
    logger.info(data)

    passphrase = os.environ.get('PASSPHRASE')
    if data.get('passphrase') != passphrase:
        logger.warning('Wrong passphrase')
        return {
            'code': 'error',
            'message': 'Invalid passphrase'
        }

    symbol = data.get('symbol')
    leverage = data.get('leverage')
    quantity = data.get('quantity')
    price = data.get('price')
    max_quantity_ratio = data.get('max_quantity_ratio')
    message = data.get('message')
    logger.info(f'symbol: {symbol}, leverage: {leverage}, price: {price}, quantity: {quantity}, '
                f'max_quantity_ratio: {max_quantity_ratio}, message: {message}')

    if message in ['Sell', 'Sell Alert']:
        logger.info(f'SELL: symbol: {symbol}, leverage: {leverage}, price: {price}, quantity: {quantity}, '
                    f'max_quantity_ratio: {max_quantity_ratio}')
        binance_trading.sell(symbol, leverage, price, quantity, max_quantity_ratio)
    elif message in ['Buy', 'Buy Alert']:
        logger.info(f'BUY: symbol: {symbol}, leverage: {leverage}, price: {price}, quantity: {quantity}, '
                    f'max_quantity_ratio: {max_quantity_ratio}')
        binance_trading.buy(symbol, leverage, price, quantity, max_quantity_ratio)

    return {"message": "successful"}


@app.route('/', methods=['GET'])
def home():
    return 'Hello, World!'


if __name__ == "__main__":
    print(f"My IP: {requests.get('https://api.my-ip.io/ip').text}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT')))
