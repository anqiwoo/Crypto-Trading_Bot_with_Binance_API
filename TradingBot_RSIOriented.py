# Algorithm to use:
# Buy 1 ETH If RSI(relative strength index, used in technical analysis) < 30
# Sell 1 ETH If RSI > 70

import os
from binance.client import Client
from binance import ThreadedWebsocketManager
from pprint import pprint  # To print prettier
from time import sleep

import talib
import numpy as np

TEST_NET = True  # Use the Binance TestNet instead of real trading platform
RSI_MIM_PERIOD = 2  # Ususally it is 14, but to test fast, we use 2 here
RSI_OVERBOUGHT = 70  # According to the Algorithm
RSI_OVERSOLD = 30  # According to the Algorithm
kline_closed_values = []

# RSI logic to trade


def rsi_trading_logic(last_rsi):
    if last_rsi > RSI_OVERBOUGHT:
        try:
            print('Sell!')
            order = client.order_market_sell(symbol=symbol, quantity=1)
            pprint(order)
            return True
        except Exception as e:
            print(e)
            return False
    elif last_rsi < RSI_OVERSOLD:
        try:
            print('Buy!')
            order = client.order_limit_buy(symbol=symbol, quantity=1)
            pprint(order)
            return True
        except Exception as e:
            print(e)
            return False
    else:
        print('Do nothing... Just wait and watch!')


def handle_kline_message(candle_msg):
    '''Process the kline message received'''
    pprint(f"kline message type: {candle_msg['e']}")
    pprint(candle_msg)
    kline = candle_msg['k']  # Access the key 'k'
    is_kline_closed = kline['x']  # If true, then the kline is closed.

    # last received or closed symbol's (Here is ETH) close price
    kline_closed_value = kline['c']

    if is_kline_closed:
        print('kline closed at: {}'.format(kline_closed_value))
        kline_closed_values.append(float(kline_closed_value))
        print(kline_closed_values)

        # RSI calculations
        if len(kline_closed_values) > RSI_MIM_PERIOD:
            kline_np_closed_values = np.array(kline_closed_values)
            rsi = talib.RSI(kline_np_closed_values, RSI_MIM_PERIOD)
            print('RSI valuesL ', rsi)
            last_calc_rsi = rsi[-1]
            print(f'RSI for trading calculations: {last_calc_rsi}')
            success = rsi_trading_logic(last_calc_rsi)
            print('trading was: ', success)
            twm.stop()


def main():
    pprint(client.get_account())

    # Get latest price from Binance API
    eth_price = client.get_symbol_ticker(symbol='ETHUSDT')
    print(eth_price)

    # Start the websocket manager and register callback for the bitcoin price
    twm.start()
    twm.start_kline_socket(
        callback=handle_kline_message, symbol=symbol, interval='1m')

    twm.join()  # main will exit if no join added


if __name__ == '__main__':
    if TEST_NET:
        # For Windows User, you can set your environment variable by searching 'env' in the start panel and there you go.
        api_key = os.environ.get('BINANCE_TESTNET_KEY')
        api_secret = os.environ.get('BINANCE_TESTNET_PASSWORD')

        client = Client(api_key, api_secret, testnet=True)
        print("Using Binance Testnet Server...")

    twm = ThreadedWebsocketManager()
    symbol = 'ETHUSDT'  # The Trading Target. Can be changed, like 'BTCUSDT'
    main()
