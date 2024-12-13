import ccxt
import pandas as pd
import pytz
from typing import List, Optional

class BinanceClient:
    def __init__(self):
        self.exchange = ccxt.binance()

    def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        timezone: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data from Binance
        """
        try:
            # Convert timezone string to offset
            offset = int(timezone.replace('UTC', '').replace('+', '').replace('-', ''))
            tz = pytz.FixedOffset(offset * 60)

            # Initialize parameters
            since = self.exchange.parse8601(f'{start_date}T00:00:00Z')
            now = self.exchange.milliseconds()
            all_bars = []

            # Fetch data in chunks to handle rate limits
            while since < now:
                try:
                    bars = self.exchange.fetch_ohlcv(
                        symbol,
                        timeframe,
                        since,
                        limit=1000
                    )
                    if not bars:
                        break
                    
                    all_bars.extend(bars)
                    since = bars[-1][0] + 1
                except ccxt.NetworkError as e:
                    raise ValueError(f"Network error occurred: {e}")
                except ccxt.ExchangeError as e:
                    raise ValueError(f"Exchange error occurred: {e}")

            if not all_bars:
                return None

            # Convert to DataFrame
            df = pd.DataFrame(
                all_bars,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            # Handle timezone
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            df['timestamp'] = df['timestamp'].dt.tz_convert(tz)
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)

            # Forward fill missing values
            df['close'] = df['close'].ffill()

            return df

        except Exception as e:
            raise ValueError(f"Error fetching data: {e}")
