import pandas as pd
import numpy as np
import talib
from virtual_trader import VirtualTrader

class TradingAnalyzer:
    def __init__(self):
        self.virtual_trader = VirtualTrader()

    def calculate_indicators(self, df, atr_period, rsi_period, ema_period):
        """Calculate technical indicators"""
        try:
            # Проверяем наличие необходимых колонок
            required_columns = ['high', 'low', 'close']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Column {col} not found in dataframe")

            # Рассчитываем индикаторы
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=atr_period)
            df['RSI'] = talib.RSI(df['close'], timeperiod=rsi_period)
            df['EMA'] = talib.EMA(df['close'], timeperiod=ema_period)

            # Заполняем NaN значения
            df['ATR'] = df['ATR'].fillna(method='ffill')
            df['RSI'] = df['RSI'].fillna(method='ffill')
            df['EMA'] = df['EMA'].fillna(method='ffill')

            return df

        except Exception as e:
            raise ValueError(f"Error calculating indicators: {str(e)}")

    def generate_signals(self, df):
        """Generate buy/sell signals based on indicators"""
        try:
            df['buy_signal'] = False
            df['sell_signal'] = False

            # Генерируем сигналы
            for i in range(1, len(df)):
                # Buy signal conditions
                if (df['close'].iloc[i] > df['EMA'].iloc[i] and  # Цена выше EMA
                    df['RSI'].iloc[i] < 70 and  # RSI не перекуплен
                    df['close'].iloc[i-1] <= df['EMA'].iloc[i-1]):  # Пересечение снизу вверх
                    df.loc[i, 'buy_signal'] = True

                # Sell signal conditions
                elif (df['close'].iloc[i] < df['EMA'].iloc[i] and  # Цена ниже EMA
                      df['RSI'].iloc[i] > 30 and  # RSI не перепродан
                      df['close'].iloc[i-1] >= df['EMA'].iloc[i-1]):  # Пересечение сверху вниз
                    df.loc[i, 'sell_signal'] = True

            return df

        except Exception as e:
            raise ValueError(f"Error generating signals: {str(e)}")

    def calculate_tp_sl(self, df, is_manual, tp_percent, sl_percent, atr_multiplier):
        """Calculate Take Profit and Stop Loss levels"""
        try:
            df['TP'] = None
            df['SL'] = None
            df['PNL_Percent'] = None  # Добавляем колонку для PNL в процентах
            
            for i in range(len(df)):
                if df['buy_signal'].iloc[i] or df['sell_signal'].iloc[i]:
                    entry_price = df['close'].iloc[i]
                    
                    if is_manual:
                        # Manual calculation based on percentages
                        if df['buy_signal'].iloc[i]:
                            tp_value = entry_price * (1 + tp_percent / 100)
                            sl_value = entry_price * (1 - sl_percent / 100)
                        else:  # sell signal
                            tp_value = entry_price * (1 - tp_percent / 100)
                            sl_value = entry_price * (1 + sl_percent / 100)
                    else:
                        # ATR-based calculation
                        atr = df['ATR'].iloc[i]
                        if df['buy_signal'].iloc[i]:
                            tp_value = entry_price + (atr * atr_multiplier)
                            sl_value = entry_price - (atr * atr_multiplier)
                        else:  # sell signal
                            tp_value = entry_price - (atr * atr_multiplier)
                            sl_value = entry_price + (atr * atr_multiplier)

                    df.loc[i, 'TP'] = tp_value
                    df.loc[i, 'SL'] = sl_value
                    
                    # Рассчитываем PNL в процентах
                    if df['buy_signal'].iloc[i]:
                        df.loc[i, 'PNL_Percent'] = (tp_value - entry_price) / entry_price * 100
                    else:
                        df.loc[i, 'PNL_Percent'] = (entry_price - tp_value) / entry_price * 100

            return df

        except Exception as e:
            raise ValueError(f"Error calculating TP/SL levels: {str(e)}")

    def analyze_data(self, df, symbol):
        """Analyze trading data and return updated dataframe with trade history"""
        try:
            # Добавляем символ в датафрейм
            df['symbol'] = symbol
            
            # Инициализируем колонки для торговли
            df['Trade_Type'] = None  # Buy/Sell/None
            df['Trade_Balance'] = None  # Balance after trade
            df['Position_Size'] = None  # Size of position
            
            # Выполняем виртуальную торговлю
            df = self.virtual_trader.process_trades(df)
            
            # Получаем историю сделок
            trade_history = self.virtual_trader.get_trade_history_df()
            
            # Добавляем PNL в процентах для закрытых сделок
            if not trade_history.empty:
                trade_history['PNL_Percent'] = trade_history.apply(
                    lambda x: ((x['Exit Price'] - x['Entry Price']) / x['Entry Price'] * 100) if x['Type'] == 'BUY'
                    else ((x['Entry Price'] - x['Exit Price']) / x['Entry Price'] * 100) if x['Type'] == 'SELL'
                    else None, axis=1
                )

            return df, trade_history

        except Exception as e:
            raise ValueError(f"Error analyzing data: {str(e)}")

    def get_final_balance(self):
        """Get final balance after all trades"""
        return self.virtual_trader.balance
