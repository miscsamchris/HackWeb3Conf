import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import telethon.tl.types as types
# Use your own values from my.telegram.org
api_id = '29693344'
api_hash = '3392872ecb9769d292fce8ea9bf818e6'
bot_token = '7799557371:AAGkM0-1D1hW8kgrvLr-clPz5EK8SqtaUBM'

import base64
import requests
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime
import pandas as pd
from openai import OpenAI
import json

# Initialize OpenAI client
openai_client = OpenAI(api_key='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')

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
# Create the client and connect
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
binance_client = BinanceClient(
    api_key='dPUfrc4V4JRPvDQO4XgX49zlfXNKbvRGRWFYvSTWmT6MHwdRp3LeWid686CzWT9L',
    private_key_path='test-prv-key.pem',
    testnet=True
)

def get_balance():
    """
    Get the balance of the allowed assets
    """
    balances = binance_client.get_wallet_balance()
    print(balances)
    allowed_assets = ['USDT','BTC','ETH','BONK','DOGE']
    for asset, balance in balances.items():
        if asset in allowed_assets:
            print(f"{asset}: {balance['free']}")
    return balances

def get_price(symbol):
    """
    Get the price of a symbol.
    """
    market_info = client.get_market_price(symbol)
    if 'price' in market_info:
        return f"Current Price: ${market_info['price']:,.2f}, 24h Change: {market_info['price_change']}%, 24h High: ${market_info['high_24h']:,.2f}, 24h Low: ${market_info['low_24h']:,.2f}, 24h Volume: {market_info['volume_24h']:,.4f}"
    else:
        print("Error:", market_info)
        return "No Data Found"

def execute_market_buy(symbol, quote_quantity):
    """
    Execute a market buy order using quote asset quantity (e.g., USDT)
    """
    return binance_client.execute_market_buy(symbol, quote_quantity)

def execute_market_sell(symbol, quantity):
    """
    Execute a market sell order using base asset quantity (e.g., BTC)
    """
    return binance_client.execute_market_sell(symbol, quantity)

@client.on(events.NewMessage(pattern='/report'))
async def start(event):
    await event.respond('Hello! I am your bot.')
    raise events.StopPropagation

async def ai_trading_decision(symbol=None):
    """
    Get trading decision from OpenAI based on current market data for ETH pairs
    If no symbol is provided, analyzes all ETH pairs
    """
    ETH_PAIRS = [
        'ETHUSDT',  # ETH/USDT pair
        'ETHBTC',   # ETH/BTC pair
        'ETHBONK',  # ETH/BONK pair
        'ETHDOGE'   # ETH/DOGE pair
    ]
    
    # If no specific symbol is provided, analyze all pairs
    pairs_to_analyze = [symbol] if symbol else ETH_PAIRS
    trading_results = []
    
    # Get current balance once for all pairs
    balances = binance_client.get_wallet_balance()
    
    for pair in pairs_to_analyze:
        try:
            price_info = binance_client.get_market_price(pair)
            
            system_prompt = """You are a cryptocurrency trading assistant. Analyze the market data and balance information provided to make a trading decision. 
            Respond with a JSON object containing:
            - action: "BUY" or "SELL" or "HOLD"
            - quantity: amount to trade (for BUY in quote currency, for SELL in base currency)
            - reasoning: brief explanation of decision
            Consider the trading pair's quote currency when suggesting quantities.
            """
            
            user_prompt = f"""
            Current market data for {pair}:
            {price_info}
            
            Available balances:
            {json.dumps(balances, indent=2)}
            
            Make a trading decision based on this information.
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            decision = json.loads(response.choices[0].message.content)
            
            # Execute the trade based on AI decision
            result = None
            if decision['action'] == 'BUY':
                result = binance_client.execute_market_buy(pair, float(decision['quantity']))
                trading_results.append(f"{pair} - Executed BUY: {result}")
            elif decision['action'] == 'SELL':
                result = binance_client.execute_market_sell(pair, float(decision['quantity']))
                trading_results.append(f"{pair} - Executed SELL: {result}")
            else:
                trading_results.append(f"{pair} - Holding position. {decision['reasoning']}")
                
        except Exception as e:
            trading_results.append(f"{pair} - Error: {str(e)}")
    
    # Return combined results
    return "\n\n".join(trading_results)

async def periodic_action():
    while True:
        user_id = 652152357
        trading_results = await ai_trading_decision()
        await client.send_message(user_id, trading_results)
        await asyncio.sleep(60)

async def main():
    # Start the periodic action
    asyncio.create_task(periodic_action())
    # Run the client until disconnected
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())