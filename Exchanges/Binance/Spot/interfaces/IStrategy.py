from dataframes.KlinesFrame import KlinesFrame
from dataframes.SymbolFrame import SymbolFrame
from dataframes.TradesFrame import TradesFrame, StatusTrade
import numpy as np
from utils.Funciones import interval_to_second
from time import time
from binance import Client
class IStrategy:
    '''
    Clase generica de una estrategia de trading
    '''
    name = "No name"
    has_stoploss = False
    has_takeprofit = False
    has_trailing_profit = False
    has_trailing_stoploss = False         
    def __init__(self, name, exchange, config):
        self.name = name
        self.config = config
        self.exchange = exchange
        self.stop = False
        self.interval = config.interval
        self.seconds = interval_to_second(self.interval)
        self.assets = ""
        self.df_symbols : SymbolFrame = self.exchange.get_symbols()
        self.df_trades : TradesFrame = TradesFrame.create_empty_trades()
        self.df_trades = self.df_trades.create_trade('BTCBUSD', Client.SIDE_BUY, 10, Client.ORDER_TYPE_MARKET)
        print(self.df_trades)
        self.reset_elapsed_time()

    def reset_elapsed_time(self):
        '''Metodo que reinica el tiempo transcurrido'''
        self.elapsed_time = time() + (self.seconds - time() % self.seconds)

    def get_assets(self, **kwargs) -> SymbolFrame:
        '''Metodo que retorna los activos que seran utilizados para compra/venta'''
        raise Exception("Not implemented")

    def signals(self, symbol_name :str, timeframe : str, limit : int) -> KlinesFrame:
        data : KlinesFrame = None
        try:
            data = self.exchange.get_candels(symbol_name, interval=timeframe, limit=limit)
            data = self.next_row(data)
        except Exception as error:
            if data is not None:
                data.drop(data.index, inplace=True)

    def is_finish_time(self):
        return (time() >= self.elapsed_time)
    
    def apply_signals(self):
        if self.df_symbols is None: return None
        for symbol_name in self.df_symbols.index:
            self.signals(symbol_name=symbol_name, interval=self.interval, limit=self.config.limit)

    def entry_long(self, symbol_name, order_type=Client.ORDER_TYPE_MARKET, quantity=np.nan, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan):
        self.df_trades = self.df_trades.create_trade(symbol_name, Client.SIDE_BUY, quantity, order_type)
    
    def exit_long(self, symbol_name, order_type=Client.ORDER_TYPE_MARKET, quantity=np.nan, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan):
        self.df_trades = self.df_trades.create_trade(symbol_name, Client.SIDE_SELL, quantity, order_type)

    def modify_trailing_stop(self, symbol_name, order_type=Client.ORDER_TYPE_MARKET, quantity=np.nan, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan):
        self.df_trades = self.df_trades.create_trade(symbol_name, Client.SIDE_SELL, quantity, order_type)

    def modify_trailing_profit(self, symbol_name, order_type=Client.ORDER_TYPE_MARKET, quantity=np.nan, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan):
        self.df_trades = self.df_trades.create_trade(symbol_name, Client.SIDE_SELL, quantity, order_type)

    def get_trades_created_for_buy(self):
        return self.df_trades.get_trades(status=StatusTrade.CREATED,side=Client.SIDE_BUY)

    def get_trades_send_for_buy(self):
        return self.df_trades.get_trades(status=StatusTrade.SEND,side=Client.SIDE_BUY)

    def get_trades_send_for_sell(self):
        return self.df_trades.get_trades(status=StatusTrade.SEND,side=Client.SIDE_SELL)
