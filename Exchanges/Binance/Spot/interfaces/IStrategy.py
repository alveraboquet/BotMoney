from dataframes.KlinesFrame import KlinesFrame
from dataframes.SymbolFrame import SymbolFrame
from dataframes.TradesFrame import TradesFrame, StatusTrade
from dataframes.OrdersFrame import OrdersFrame, StatusOrder, TypeQty
from enum import Enum
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
        self.reset_elapsed_time()
        self.assets = ""
        self.df_symbols : SymbolFrame = self.exchange.get_symbols()
        self.trades : TradesFrame = TradesFrame.create_empty_trades()
        self.orders : OrdersFrame = OrdersFrame.create_empty_orders()

    def next_row(self, data:KlinesFrame = None):
        return data

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
        if self.df_symbols is None: 
            return None
        for symbol_name in self.df_symbols.index:
            self.signals(symbol_name=symbol_name, timeframe=self.interval, limit=self.config.limit)

    def entry_long(self, symbol_name, order_type=Client.ORDER_TYPE_MARKET, quantity=np.nan, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan, price=np.nan, type_qty : TypeQty = TypeQty.USD):
        self.orders = self.orders.create_order(symbol_name, price=price, order_type = order_type, side= Client.SIDE_BUY, quantity=quantity, side=Client.SIDE_BUY, stop_loss=stop_loss, take_profit=take_profit, trailing_stop=trailing_stop, trailing_profit=trailing_profit, type_qty=type_qty)
    
    def exit_long(self, symbol_name, order_type=Client.ORDER_TYPE_MARKET, quantity=np.nan, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan, price=np.nan, type_qty :TypeQty = TypeQty.USD):
        self.orders = self.orders.create_order(symbol_name, price=price, order_type = order_type, side= Client.SIDE_SELL, quantity=quantity, side=Client.SIDE_BUY, stop_loss=stop_loss, take_profit=take_profit, trailing_stop=trailing_stop, trailing_profit=trailing_profit, type_qty=type_qty)

    def get_orders_for_open(self):
        return self.orders.get_orders()

    def get_orders_for_close(self):
        return self.orders.get_orders(side=Client.SIDE_SELL)
    
    def on_buy(self, order, entry_price, quantity):
        self.trades = self.trades.set_trade(order.symbol_name, StatusTrade.LONG, quantity, order.stop_loss, order.take_profit, order.trailing_stop, order.trailing_profit, entry_price, exit_price=None)
        return self.trades.loc[order.symbol_name].copy()

    def on_sell(self, order, exit_price, quantity):
        self.trades = self.trades.set_trade(order.symbol_name, StatusTrade.LONG, quantity, order.stop_loss, order.take_profit, order.trailing_stop, order.trailing_profit, exit_price, exit_price=None)
        return self.trades.loc[order.symbol_name].copy()        