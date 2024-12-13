import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QPushButton, QMessageBox, QComboBox, QSpinBox,
    QFormLayout, QRadioButton, QDoubleSpinBox, QGroupBox,
    QStyleFactory
)
from PyQt5.QtCore import Qt
from matplotlib import pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from binance_client import BinanceClient
from trading_analyzer import TradingAnalyzer
import config
from styles import DARK_THEME, LIGHT_THEME

class DateSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.binance_client = BinanceClient()
        self.trading_analyzer = TradingAnalyzer()
        self.dark_mode = True
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Crypto Trading Analyzer')
        self.setMinimumSize(800, 600)
        
        # Основной layout
        main_layout = QHBoxLayout()
        
        # Левая панель с настройками
        settings_panel = QVBoxLayout()
        
        # Группа настроек данных
        data_group = QGroupBox("Настройки данных")
        data_layout = QFormLayout()

        # Выбор даты
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        data_layout.addRow('Дата начала:', self.date_edit)

        # Выбор торговой пары
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(config.TRADING_PAIRS)
        data_layout.addRow('Торговая пара:', self.symbol_combo)

        # Выбор таймфрейма
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(config.TIMEFRAMES)
        data_layout.addRow('Таймфрейм:', self.timeframe_combo)

        data_group.setLayout(data_layout)
        settings_panel.addWidget(data_group)

        # Группа настроек торговли
        trading_group = QGroupBox("Настройки торговли")
        trading_layout = QVBoxLayout()

        # Метод расчета TP и SL
        self.manual_radio = QRadioButton("Ручной расчет")
        self.manual_radio.setChecked(True)
        self.auto_radio = QRadioButton("Автоматический (ATR)")
        trading_layout.addWidget(self.manual_radio)
        trading_layout.addWidget(self.auto_radio)

        # Параметры TP/SL
        tp_sl_layout = QFormLayout()
        
        self.tp_percent = QDoubleSpinBox()
        self.tp_percent.setValue(5.0)
        self.tp_percent.setRange(0.0, 100.0)
        self.tp_percent.setSuffix("%")
        tp_sl_layout.addRow('Take Profit:', self.tp_percent)

        self.sl_percent = QDoubleSpinBox()
        self.sl_percent.setValue(3.0)
        self.sl_percent.setRange(0.0, 100.0)
        self.sl_percent.setSuffix("%")
        tp_sl_layout.addRow('Stop Loss:', self.sl_percent)

        self.multiplier_spin = QDoubleSpinBox()
        self.multiplier_spin.setValue(2.0)
        self.multiplier_spin.setRange(0.0, 100.0)
        tp_sl_layout.addRow('ATR множитель:', self.multiplier_spin)

        trading_layout.addLayout(tp_sl_layout)
        trading_group.setLayout(trading_layout)
        settings_panel.addWidget(trading_group)

        # Группа индикаторов
        indicator_group = QGroupBox("Индикаторы")
        indicator_layout = QFormLayout()

        self.atr_period = QSpinBox()
        self.atr_period.setValue(config.DEFAULT_ATR_PERIOD)
        indicator_layout.addRow('ATR период:', self.atr_period)

        self.rsi_period = QSpinBox()
        self.rsi_period.setValue(config.DEFAULT_RSI_PERIOD)
        indicator_layout.addRow('RSI период:', self.rsi_period)

        self.ema_period = QSpinBox()
        self.ema_period.setValue(config.DEFAULT_EMA_PERIOD)
        indicator_layout.addRow('EMA период:', self.ema_period)

        indicator_group.setLayout(indicator_layout)
        settings_panel.addWidget(indicator_group)

        # Размер позиции
        position_size_group = QGroupBox("Размер позиции")
        position_size_layout = QFormLayout()
        self.position_size = QDoubleSpinBox()
        self.position_size.setValue(100.0)
        self.position_size.setRange(0.0, 1000000.0)
        position_size_layout.addRow('Размер позиции (USDT):', self.position_size)
        position_size_group.setLayout(position_size_layout)
        settings_panel.addWidget(position_size_group)

        # Часовой пояс
        timezone_group = QGroupBox("Часовой пояс")
        timezone_layout = QVBoxLayout()
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([f'UTC+{i}' for i in range(13)] + [f'UTC-{i}' for i in range(1, 13)])
        timezone_layout.addWidget(self.timezone_combo)
        timezone_group.setLayout(timezone_layout)
        settings_panel.addWidget(timezone_group)

        # Кнопки управления
        control_layout = QHBoxLayout()
        
        # Переключатель темы
        self.theme_button = QPushButton('Светлая тема')
        self.theme_button.clicked.connect(self.toggle_theme)
        control_layout.addWidget(self.theme_button)
        
        # Кнопка загрузки данных
        self.load_button = QPushButton('Загрузить данные')
        self.load_button.clicked.connect(self.load_data)
        control_layout.addWidget(self.load_button)
        
        settings_panel.addLayout(control_layout)
        
        # Добавляем растягивающийся спейсер
        settings_panel.addStretch()

        # Добавляем левую панель в основной layout
        left_widget = QWidget()
        left_widget.setLayout(settings_panel)
        left_widget.setMaximumWidth(300)
        main_layout.addWidget(left_widget)

        # Правая панель для графиков
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)
        
        # Применяем темную тему по умолчанию
        self.apply_theme(DARK_THEME)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_theme(DARK_THEME)
            self.theme_button.setText('Светлая тема')
        else:
            self.apply_theme(LIGHT_THEME)
            self.theme_button.setText('Темная тема')

    def apply_theme(self, theme):
        self.setStyleSheet(theme)
        
        # Обновляем стиль графика
        if hasattr(self, 'figure'):
            self.figure.set_facecolor('#2D2D2D' if self.dark_mode else '#FFFFFF')
            for ax in self.figure.get_axes():
                ax.set_facecolor('#2D2D2D' if self.dark_mode else '#FFFFFF')
                ax.tick_params(colors='white' if self.dark_mode else 'black')
                ax.spines['bottom'].set_color('white' if self.dark_mode else 'black')
                ax.spines['top'].set_color('white' if self.dark_mode else 'black')
                ax.spines['left'].set_color('white' if self.dark_mode else 'black')
                ax.spines['right'].set_color('white' if self.dark_mode else 'black')
                ax.title.set_color('white' if self.dark_mode else 'black')
                ax.xaxis.label.set_color('white' if self.dark_mode else 'black')
                ax.yaxis.label.set_color('white' if self.dark_mode else 'black')
            self.canvas.draw()

    def load_data(self):
        try:
            # Обновляем размер позиции в конфиге
            config.POSITION_SIZE = self.position_size.value()
            
            # Получаем параметры из GUI
            start_date = self.date_edit.date().toString('yyyy-MM-dd')
            symbol = self.symbol_combo.currentText()
            timeframe = self.timeframe_combo.currentText()
            timezone = self.timezone_combo.currentText()

            # Загружаем данные
            df = self.binance_client.fetch_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                timezone=timezone
            )

            if df is None or df.empty:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось получить данные')
                return

            # Рассчитываем индикаторы
            try:
                df = self.trading_analyzer.calculate_indicators(
                    df=df,
                    atr_period=self.atr_period.value(),
                    rsi_period=self.rsi_period.value(),
                    ema_period=self.ema_period.value()
                )
            except ValueError as e:
                QMessageBox.warning(self, 'Ошибка', str(e))
                return

            # Генерируем сигналы
            df = self.trading_analyzer.generate_signals(df)

            # Рассчитываем TP/SL
            df = self.trading_analyzer.calculate_tp_sl(
                df=df,
                is_manual=self.manual_radio.isChecked(),
                tp_percent=self.tp_percent.value(),
                sl_percent=self.sl_percent.value(),
                atr_multiplier=self.multiplier_spin.value()
            )

            # Анализируем данные и получаем историю торговли
            df, trade_history = self.trading_analyzer.analyze_data(df, symbol)

            # Сохраняем результаты
            self.save_results(df, trade_history, symbol, timezone)

            # Показываем график
            self.plot_data(df)

            # Показываем итоговый баланс
            final_balance = self.trading_analyzer.get_final_balance()
            QMessageBox.information(
                self,
                'Успех',
                f'Анализ успешно завершен\nИтоговый баланс: {final_balance:.2f} USDT'
            )

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}')

    def save_results(self, df, trade_history, symbol, timezone):
        try:
            save_dir = 'trade_signals'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # Генерируем уникальное имя файла с временной меткой
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(save_dir, f'trade_signals_{symbol.replace("/", "_")}_{timezone}_{timestamp}.xlsx')
            
            # Пробуем сохранить файл
            with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='All Data', index=False)
                if not trade_history.empty:
                    trade_history.to_excel(writer, sheet_name='Trade History', index=False)
            
            QMessageBox.information(
                self,
                'Успешно',
                f'Результаты сохранены в файл:\n{save_path}'
            )
        except PermissionError:
            QMessageBox.warning(
                self,
                'Ошибка сохранения',
                'Не удалось сохранить файл. Возможно, он открыт в Excel.\n'
                'Пожалуйста, закройте файл и попробуйте снова.'
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                'Ошибка сохранения',
                f'Произошла ошибка при сохранении файла:\n{str(e)}'
            )

    def plot_data(self, df):
        self.figure.clear()
        
        # Преобразуем 'timestamp' в datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # График цены и EMA
        ax1 = self.figure.add_subplot(111)
        ax1.plot(df['timestamp'], df['close'], label='Цена закрытия', color='#00FF00' if self.dark_mode else 'blue')
        ax1.plot(df['timestamp'], df['EMA'], label='EMA', color='#FF4444', alpha=0.7)
        
        # Отмечаем сигналы на графике
        buy_signals = df[df['Trade_Type'] == 'BUY']
        sell_signals = df[df['Trade_Type'] == 'SELL']
        
        ax1.scatter(buy_signals['timestamp'], buy_signals['close'], 
                   color='#00FF00', marker='^', label='Buy Signal')
        ax1.scatter(sell_signals['timestamp'], sell_signals['close'], 
                   color='#FF4444', marker='v', label='Sell Signal')
        
        ax1.set_title('Анализ цены и сигналов')
        ax1.set_ylabel('Цена')
        ax1.legend()
        ax1.grid(True, alpha=0.2)
        
        # Поворот меток времени
        ax1.tick_params(axis='x', rotation=45)
        
        self.figure.tight_layout()
        self.apply_theme(DARK_THEME if self.dark_mode else LIGHT_THEME)
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DateSelector()
    window.show()
    sys.exit(app.exec_())
