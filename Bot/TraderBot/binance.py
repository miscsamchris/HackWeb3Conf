import base64
import requests
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime
import pandas as pd

class BinanceClient:
    def __init__(self, api_key, private_key_path, testnet=True):
        self.API_KEY = api_key
        self.PRIVATE_KEY_PATH = private_key_path
        self.BASE_URL = 'https://testnet.binance.vision' if testnet else 'https://api.binance.com'
        
        # Load the private key
        with open(self.PRIVATE_KEY_PATH, 'rb') as f:
            self.private_key = load_pem_private_key(data=f.read(), password=None)

    def _get_server_time(self):
        """Get Binance server time"""
        return requests.get(f'{self.BASE_URL}/api/v3/time').json()['serverTime']

    def _sign_request(self, params):
        """Sign the request parameters"""
        payload = '&'.join([f'{param}={value}' for param, value in params.items()])
        signature = base64.b64encode(
            self.private_key.sign(
                payload.encode('ASCII'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        )
        return signature
    
    def get_historical_data(self, symbol, interval='1d', limit=500, start_time=None, end_time=None):
        """
        Get historical kline/candlestick data
        
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :param interval: Kline interval. Options: 1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M
        :param limit: Number of records to get (max 1000)
        :param start_time: Start time in milliseconds or datetime
        :param end_time: End time in milliseconds or datetime
        :return: DataFrame with historical data
        """
        # Convert datetime to milliseconds if provided
        if isinstance(start_time, datetime):
            start_time = int(start_time.timestamp() * 1000)
        if isinstance(end_time, datetime):
            end_time = int(end_time.timestamp() * 1000)

        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time

        response = requests.get(
            f'{self.BASE_URL}/api/v3/klines',
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
                df[col] = df[col].astype(float)
            
            # Set timestamp as index
            df.set_index('timestamp', inplace=True)
            
            # Keep only essential columns
            return df[['open', 'high', 'low', 'close', 'volume', 'quote_volume', 'trades']]
        
        return response.json()
    
    def get_quote(self, symbol):
        """
        Get current quote (bid/ask) for a symbol
        
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :return: Dictionary containing bid/ask prices and quantities
        """
        response = requests.get(
            f'{self.BASE_URL}/api/v3/ticker/bookTicker',
            params={'symbol': symbol}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'symbol': data['symbol'],
                'bid_price': float(data['bidPrice']),
                'bid_quantity': float(data['bidQty']),
                'ask_price': float(data['askPrice']),
                'ask_quantity': float(data['askQty']),
                'spread': float(data['askPrice']) - float(data['bidPrice']),
                'spread_percentage': ((float(data['askPrice']) / float(data['bidPrice'])) - 1) * 100
            }
        return response.json()

    def get_detailed_quote(self, symbol):
        """
        Get detailed quote including 24h stats
        
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :return: Dictionary containing detailed quote information
        """
        # Get basic quote
        quote = self.get_quote(symbol)
        
        # Get 24h ticker data
        response = requests.get(
            f'{self.BASE_URL}/api/v3/ticker/24hr',
            params={'symbol': symbol}
        )
        
        if response.status_code == 200:
            ticker = response.json()
            quote.update({
                'last_price': float(ticker['lastPrice']),
                'price_change': float(ticker['priceChange']),
                'price_change_percent': float(ticker['priceChangePercent']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume_24h': float(ticker['volume']),
                'quote_volume_24h': float(ticker['quoteVolume']),
                'weighted_avg_price': float(ticker['weightedAvgPrice']),
                'trades_24h': int(ticker['count'])
            })
        return quote

    def get_wallet_balance(self):
        """Get account wallet balances"""
        params = {'timestamp': self._get_server_time()}
        params['signature'] = self._sign_request(params)

        headers = {'X-MBX-APIKEY': self.API_KEY}
        response = requests.get(
            f'{self.BASE_URL}/api/v3/account',
            headers=headers,
            params=params
        )

        account_info = response.json()
        if 'balances' in account_info:
            non_zero_balances = {}
            for balance in account_info['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                if free > 0 or locked > 0:
                    non_zero_balances[balance['asset']] = {
                        'free': free,
                        'locked': locked
                    }
            return non_zero_balances
        return account_info

    def create_order(self, symbol, side, order_type, quantity, price=None):
        """
        Create a new order
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :param side: 'BUY' or 'SELL'
        :param order_type: 'LIMIT' or 'MARKET'
        :param quantity: Amount to trade
        :param price: Price for limit orders (optional for market orders)
        """
        # Get current price if needed for validation
        current_price = float(requests.get(
            f'{self.BASE_URL}/api/v3/ticker/price',
            params={'symbol': symbol}
        ).json()['price'])
        print(current_price)
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': str(quantity),
            'timestamp': self._get_server_time()
        }

        if order_type == 'LIMIT':
            if price is None:
                # Set price to 1% below current for SELL, 1% above for BUY
                multiplier = 0.99 if side == 'SELL' else 1.01
                price = round(current_price * multiplier, 2)
            params['price'] = str(price)
            params['timeInForce'] = 'GTC'

        params['signature'] = self._sign_request(params)
        
        headers = {'X-MBX-APIKEY': self.API_KEY}
        response = requests.post(
            f'{self.BASE_URL}/api/v3/order',
            headers=headers,
            data=params
        )
        return response.json()
    
    def get_market_price(self, symbol):
        """
        Get latest market price for a symbol
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :return: Current price as float and 24h price change percentage
        """
        # Get ticker information
        response = requests.get(
            f'{self.BASE_URL}/api/v3/ticker/24hr',
            params={'symbol': symbol}
        )
        ticker = response.json()
        
        if 'lastPrice' in ticker:
            return {
                'symbol': symbol,
                'price': float(ticker['lastPrice']),
                'price_change': float(ticker['priceChangePercent']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume_24h': float(ticker['volume'])
            }
        return ticker
    
    def execute_quote(self, symbol, side, order_type, quantity=None, quote_quantity=None, price=None, time_in_force='GTC'):
        """
        Execute a quote (place an order) with various options
        
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :param side: 'BUY' or 'SELL'
        :param order_type: 'MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT', 'TAKE_PROFIT_LIMIT'
        :param quantity: Amount of base asset (e.g., BTC in BTCUSDT)
        :param quote_quantity: Amount of quote asset (e.g., USDT in BTCUSDT)
        :param price: Limit price (required for LIMIT orders)
        :param time_in_force: 'GTC' (Good Till Cancel), 'IOC' (Immediate or Cancel), 'FOK' (Fill or Kill)
        :return: Order response
        """
        # Prepare base parameters
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'timestamp': self._get_server_time()
        }

        # Add quantity parameters based on order type
        if order_type.upper() == 'MARKET':
            if quote_quantity and side.upper() == 'BUY':
                params['quoteOrderQty'] = quote_quantity
            elif quantity:
                params['quantity'] = quantity
            else:
                raise ValueError("Either quantity or quote_quantity must be provided for MARKET orders")
        else:
            if not quantity:
                raise ValueError("Quantity is required for non-MARKET orders")
            params['quantity'] = quantity

        # Add price and time_in_force for LIMIT orders
        if 'LIMIT' in order_type.upper():
            if not price:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = time_in_force

        # Sign the request
        params['signature'] = self._sign_request(params)

        # Execute the order
        headers = {'X-MBX-APIKEY': self.API_KEY}
        response = requests.post(
            f'{self.BASE_URL}/api/v3/order',
            headers=headers,
            data=params
        )

        return response.json()

    def execute_market_buy(self, symbol, quote_quantity):
        """
        Execute a market buy order using quote asset quantity (e.g., USDT)
        
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :param quote_quantity: Amount of quote asset to spend
        :return: Order response
        """
        return self.execute_quote(
            symbol=symbol,
            side='BUY',
            order_type='MARKET',
            quote_quantity=quote_quantity
        )

    def execute_market_sell(self, symbol, quantity):
        """
        Execute a market sell order using base asset quantity (e.g., BTC)
        
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :param quantity: Amount of base asset to sell
        :return: Order response
        """
        return self.execute_quote(
            symbol=symbol,
            side='SELL',
            order_type='MARKET',
            quantity=quantity
        )

    def execute_limit_order(self, symbol, side, quantity, price):
        """
        Execute a limit order
        
        :param symbol: Trading pair (e.g., 'BTCUSDT')
        :param side: 'BUY' or 'SELL'
        :param quantity: Amount of base asset
        :param price: Limit price
        :return: Order response
        """
        return self.execute_quote(
            symbol=symbol,
            side=side,
            order_type='LIMIT',
            quantity=quantity,
            price=price
        )

def main():
    # Initialize client
    client = BinanceClient(
        api_key='dPUfrc4V4JRPvDQO4XgX49zlfXNKbvRGRWFYvSTWmT6MHwdRp3LeWid686CzWT9L',
        private_key_path='test-prv-key.pem',
        testnet=True
    )

    # Example usage:
    
    # Get wallet balances
    print("\nWallet Balances:")
    balances = client.get_wallet_balance()
    print(balances)
    # for asset, balance in balances.items():
    #     print(f"{asset}:")
    #     print(f"  Free: {balance['free']}")
    #     print(f"  Locked: {balance['locked']}")

    # Create a limit sell order
    print("\nCreating order:")
    order = client.create_order(
        symbol='KAIAUSDT',
        side='SELL',
        order_type='LIMIT',
        quantity=0.001,
        price=None  # Will auto-calculate based on current price
    )
    print(order)
    
    print("\nBTC/USDT Market Info:")
    market_info = client.get_market_price('BTCUSDT')
    if 'price' in market_info:
        print(f"Current Price: ${market_info['price']:,.2f}")
        print(f"24h Change: {market_info['price_change']}%")
        print(f"24h High: ${market_info['high_24h']:,.2f}")
        print(f"24h Low: ${market_info['low_24h']:,.2f}")
        print(f"24h Volume: {market_info['volume_24h']:,.4f}")
    else:
        print("Error:", market_info)
        
    # Get historical data
    print("\nHistorical Data:")
    historical_data = client.get_historical_data('BTCUSDT', interval='1d', limit=10)
    print(historical_data)
    
    print("\nBTC/USDT Quote Information:")
    
    # # Get basic quote
    # quote = client.get_quote('BTCUSDT')
    # print("\nBasic Quote:")
    # print(f"Bid: ${quote['bid_price']:,.2f} ({quote['bid_quantity']:.4f})")
    # print(f"Ask: ${quote['ask_price']:,.2f} ({quote['ask_quantity']:.4f})")
    # print(f"Spread: ${quote['spread']:,.2f} ({quote['spread_percentage']:.4f}%)")
    
    # # Get detailed quote
    # detailed = client.get_detailed_quote('BTCUSDT')
    # print("\nDetailed Quote:")
    # print(f"Last Price: ${detailed['last_price']:,.2f}")
    # print(f"24h Change: ${detailed['price_change']:,.2f} ({detailed['price_change_percent']}%)")
    # print(f"24h High: ${detailed['high_24h']:,.2f}")
    # print(f"24h Low: ${detailed['low_24h']:,.2f}")
    # print(f"24h Volume: {detailed['volume_24h']:,.4f}")
    # print(f"24h Quote Volume: ${detailed['quote_volume_24h']:,.2f}")
    # print(f"24h Weighted Avg Price: ${detailed['weighted_avg_price']:,.2f}")
    # print(f"24h Number of Trades: {detailed['trades_24h']:,}")
    
    # Get multiple quotes at once
    # symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    # print("\nMultiple Symbol Quotes:")
    # for symbol in symbols:
    #     quote = client.get_quote(symbol)
    #     print(f"\n{symbol}:")
    #     print(f"Bid: ${quote['bid_price']:,.2f}")
    #     print(f"Ask: ${quote['ask_price']:,.2f}")
    #     print(f"Spread: {quote['spread_percentage']:.4f}%")
        
    try:
        # Market buy example (spending 100 USDT)
        market_buy = client.execute_market_buy('BTCUSDT', quote_quantity=100)
        print("\nMarket Buy Order:")
        print(f"Order ID: {market_buy.get('orderId')}")
        print(f"Status: {market_buy.get('status')}")
        print(f"Filled: {market_buy.get('executedQty')} BTC")
        print(f"Spent: {market_buy.get('cummulativeQuoteQty')} USDT")

        # Market sell example (selling 0.001 BTC)
        market_sell = client.execute_market_sell('BTCUSDT', quantity=0.001)
        print("\nMarket Sell Order:")
        print(f"Order ID: {market_sell.get('orderId')}")
        print(f"Status: {market_sell.get('status')}")
        print(f"Filled: {market_sell.get('executedQty')} BTC")
        print(f"Received: {market_sell.get('cummulativeQuoteQty')} USDT")

        # # Limit buy example
        # current_price = float(client.get_quote('BTCUSDT')['ask_price'])
        # limit_price = current_price * 0.99  # 1% below current price
        # limit_buy = client.execute_limit_order(
        #     symbol='BTCUSDT',
        #     side='BUY',
        #     quantity=0.001,
        #     price=limit_price
        # )
        # print("\nLimit Buy Order:")
        # print(f"Order ID: {limit_buy.get('orderId')}")
        # print(f"Status: {limit_buy.get('status')}")
        # print(f"Price: {limit_buy.get('price')} USDT")
        # print(f"Quantity: {limit_buy.get('origQty')} BTC")

    except Exception as e:
        print(f"Error executing orders: {str(e)}")
    

if __name__ == "__main__":
    main()