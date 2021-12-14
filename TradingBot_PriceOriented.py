# Algorithm to use:
# Buy 1 ETH If BTC is greater than 10k and less than 40k
# Sell 1 ETH Otherwise

import os
from binance.client import Client
from binance import ThreadedWebsocketManager
from pprint import pprint  # To print prettier
from time import sleep

TEST_NET = True  # Use the Binance TestNet instead of real trading platform


def btc_values_received(msg):
    '''Process the BTC values received in the last 24 hours'''
    pprint(msg)
    if msg['e'] != 'error':
        print(msg['e'])
        btc_price['BTCUSDT'] = float(msg['c'])
    else:
        btc_price['error'] = True


def trade_ETH_at_BTC():
    while True:
        # Error check to make sure WebSocket is working
        if btc_price['error']:
            # stop and restart socket (cleanup)
            twm.stop()
            sleep(2)
            twm.start()
            btc_price['error'] = False
        else:
            # According to the Trading Algorithm
            if 10000 < btc_price['BTC'] < 40000:
                try:
                    print('Buying when BTCUSDT price:', btc_price['BTCUSDT'])
                    order = client.order_market_buy(
                        symbol='ETHUSDT', quantity=1)
                    pprint(order)
                    break
                except Exception as e:
                    print(e)
                    break
            else:
                try:
                    print('Selling when BTCUSDT price:', btc_price['BTCUSDT'])
                    order = client.order_market_sell(
                        symbol='ETHUSDT', quantity=1)
                    pprint(order)
                    break
                except Exception as e:
                    print(e)
                    break
        sleep(0.1)


def main():
    pprint(client.get_account())
    print(client.get_asset_balance(asset='BNB'))  # BTC, ETH, USDT

    # Get latest price from Binance API
    eth_price = client.get_symbol_ticker(symbol='ETHUSDT')
    print(eth_price)

    # Start the websocket manager and register callback for the bitcoin price
    twm.start()
    twm.start_symbol_ticker_socket(
        callback=btc_values_received, symbol='BTCUSDT')

    # Wait here to receive some BTC value initially through websocket callback
    while not btc_price['BTCUSDT']:
        sleep(0.1)

    # Call buy ETH function with a while loop to keep a track on BTC price
    trade_ETH_at_BTC()
    twm.join()
    twm.stop()


if __name__ == '__main__':
    if TEST_NET:
        # For Windows User, you can set your environment variable by searching 'env' in the start panel and there you go.
        api_key = os.environ.get('BINANCE_TESTNET_KEY')
        api_secret = os.environ.get('BINANCE_TESTNET_PASSWORD')

        client = Client(api_key, api_secret, testnet=True)
        print("Using Binance Testnet Server...")

    # Add BTC price and instantiates ThreadedWebsocketManager()
    btc_price = {'BTCUSDT': None, 'error': False}
    twm = ThreadedWebsocketManager()
    main()
