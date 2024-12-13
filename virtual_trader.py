import pandas as pd
from typing import Optional, List
import config

class Trade:
    def __init__(
        self,
        entry_time: pd.Timestamp,
        symbol: str = None,
        entry_price: float = None,
        position_size: float = None,
        trade_type: str = None,
        tp_price: float = None,
        sl_price: float = None,
        exit_time: pd.Timestamp = None,
        exit_price: float = None,
        pnl: float = None,
        status: str = 'OPEN',
        balance_after: float = None,
        unused_balance: float = None
    ):
        self.entry_time = entry_time
        self.symbol = symbol
        self.entry_price = entry_price
        self.position_size = position_size  # В USDT
        self.trade_type = trade_type
        self.tp_price = tp_price
        self.sl_price = sl_price
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.pnl = pnl
        self.status = status
        self.balance_after = balance_after
        self.unused_balance = unused_balance  # Баланс, не использованный в сделке

    def close_trade(self, exit_time: pd.Timestamp, exit_price: float, reason: str = 'SIGNAL'):
        """Close the trade and calculate PNL"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        
        # Рассчитываем PNL в USDT
        if self.trade_type == 'BUY':
            percent_change = (exit_price - self.entry_price) / self.entry_price
        else:  # SELL
            percent_change = (self.entry_price - exit_price) / self.entry_price
            
        self.pnl = round(self.position_size * percent_change, 2)
        
        # Устанавливаем статус закрытия
        if reason == 'TP':
            self.status = 'TP_HIT'
        elif reason == 'SL':
            self.status = 'SL_HIT'
        else:
            self.status = 'CLOSED_BY_SIGNAL'
        
        # Рассчитываем итоговый баланс
        # Добавляем к неиспользованному балансу (unused_balance) сумму позиции и PNL
        self.balance_after = round(self.unused_balance + self.position_size + self.pnl, 2)
        
        return self.pnl

    def to_dict(self):
        """Convert trade to dictionary for DataFrame"""
        return {
            'Entry Time': self.entry_time,
            'Symbol': self.symbol,
            'Type': self.trade_type,
            'Entry Price': self.entry_price,
            'Position Size (USDT)': self.position_size,
            'TP': self.tp_price,
            'SL': self.sl_price,
            'Exit Time': self.exit_time,
            'Exit Price': self.exit_price,
            'PNL (USDT)': self.pnl,
            'Status': self.status,
            'Balance After': self.balance_after
        }

class VirtualTrader:
    def __init__(self):
        self.balance = config.INITIAL_BALANCE
        self.trades: List[Trade] = []
        self.current_trade: Optional[Trade] = None

    def process_trades(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process trades based on signals"""
        df_copy = df.copy()  # Создаем копию для безопасного изменения
        
        # Инициализируем необходимые колонки
        if 'Trade_Type' not in df_copy.columns:
            df_copy['Trade_Type'] = None
        if 'Trade_Balance' not in df_copy.columns:
            df_copy['Trade_Balance'] = None
        if 'Position_Size' not in df_copy.columns:
            df_copy['Position_Size'] = None
        
        for i in range(len(df_copy)):
            current_time = df_copy.index[i]
            current_price = df_copy['close'].iloc[i]
            
            # Если есть открытая сделка
            if self.current_trade:
                # Сначала проверяем TP/SL
                trade_closed = self._check_tp_sl(
                    df_copy['high'].iloc[i],
                    df_copy['low'].iloc[i],
                    current_time
                )
                
                # Если сделка не закрыта по TP/SL, проверяем новые сигналы
                if not trade_closed:
                    # Если есть новый сигнал, закрываем текущую сделку
                    if df_copy['buy_signal'].iloc[i] or df_copy['sell_signal'].iloc[i]:
                        self._close_current_trade(current_time, current_price)
                        trade_closed = True

                if trade_closed:
                    df_copy.loc[i, 'Trade_Balance'] = self.balance

            # Проверяем новые сигналы для входа
            if not self.current_trade:
                if df_copy['buy_signal'].iloc[i]:
                    trade = self._open_trade(
                        entry_time=current_time,
                        symbol=df_copy['symbol'].iloc[i],
                        entry_price=current_price,
                        trade_type='BUY',
                        tp_price=df_copy['TP'].iloc[i],
                        sl_price=df_copy['SL'].iloc[i]
                    )
                    if trade:
                        df_copy.loc[i, 'Trade_Type'] = 'BUY'
                        df_copy.loc[i, 'Trade_Balance'] = self.balance
                        df_copy.loc[i, 'Position_Size'] = trade.position_size

                elif df_copy['sell_signal'].iloc[i]:
                    trade = self._open_trade(
                        entry_time=current_time,
                        symbol=df_copy['symbol'].iloc[i],
                        entry_price=current_price,
                        trade_type='SELL',
                        tp_price=df_copy['TP'].iloc[i],
                        sl_price=df_copy['SL'].iloc[i]
                    )
                    if trade:
                        df_copy.loc[i, 'Trade_Type'] = 'SELL'
                        df_copy.loc[i, 'Trade_Balance'] = self.balance
                        df_copy.loc[i, 'Position_Size'] = trade.position_size

        return df_copy

    def calculate_position_size(self, price: float) -> float:
        """Calculate position size in USDT based on current balance and position size percentage"""
        position_size = round(self.balance * (config.POSITION_SIZE / 100.0), 2)
        return max(10.0, min(position_size, self.balance))  # Минимум 10 USDT, максимум - весь баланс

    def _open_trade(
        self,
        entry_time: pd.Timestamp,
        symbol: str,
        entry_price: float,
        trade_type: str,
        tp_price: float,
        sl_price: float
    ) -> Optional[Trade]:
        """Open a new trade"""
        # Проверяем, достаточно ли баланса
        if self.balance <= 10:  # Минимальный баланс для торговли
            return None
            
        position_size = self.calculate_position_size(entry_price)
        
        # Проверяем минимальный размер позиции
        if position_size < 10:  # Минимальный размер в USDT
            return None
        
        # Рассчитываем неиспользованный баланс
        unused_balance = round(self.balance - position_size, 2)
        
        # Создаем новую сделку
        self.current_trade = Trade(
            entry_time=entry_time,
            symbol=symbol,
            entry_price=entry_price,
            position_size=position_size,
            trade_type=trade_type,
            tp_price=tp_price,
            sl_price=sl_price,
            unused_balance=unused_balance
        )

        # Обновляем баланс
        self.balance = unused_balance

        return self.current_trade

    def _check_tp_sl(
        self,
        high_price: float,
        low_price: float,
        current_time: pd.Timestamp
    ) -> bool:
        """Check if TP or SL is hit"""
        if not self.current_trade:
            return False

        trade = self.current_trade
        trade_closed = False

        if trade.trade_type == 'BUY':
            if high_price >= trade.tp_price:  # TP hit
                pnl = trade.close_trade(current_time, trade.tp_price, 'TP')
                self.balance = trade.balance_after
                trade_closed = True
            elif low_price <= trade.sl_price:  # SL hit
                pnl = trade.close_trade(current_time, trade.sl_price, 'SL')
                self.balance = trade.balance_after
                trade_closed = True
        else:  # SELL trade
            if low_price <= trade.tp_price:  # TP hit
                pnl = trade.close_trade(current_time, trade.tp_price, 'TP')
                self.balance = trade.balance_after
                trade_closed = True
            elif high_price >= trade.sl_price:  # SL hit
                pnl = trade.close_trade(current_time, trade.sl_price, 'SL')
                self.balance = trade.balance_after
                trade_closed = True

        if trade_closed:
            self.trades.append(trade)
            self.current_trade = None

        return trade_closed

    def _close_current_trade(self, exit_time: pd.Timestamp, exit_price: float) -> None:
        """Close current trade by signal"""
        if self.current_trade:
            self.current_trade.close_trade(exit_time, exit_price)
            self.balance = self.current_trade.balance_after
            self.trades.append(self.current_trade)
            self.current_trade = None

    def get_trade_history_df(self) -> pd.DataFrame:
        """Get trade history as DataFrame"""
        if not self.trades:
            return pd.DataFrame()

        trade_data = []
        for trade in self.trades:
            trade_data.append(trade.to_dict())

        return pd.DataFrame(trade_data)
