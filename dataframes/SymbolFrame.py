from enum import Enum
import pandas as pd
import numpy as np
from binance import Client
from utils.Constantes import Const, StatusTrade
from datetime import datetime
from utils.Funciones import * 

class ColumnsSymbolFrame(Enum):
    priceChange = "priceChange" 
    priceChangePercent = "priceChangePercent"
    weightedAvgPrice ="weightedAvgPrice"
    prevClosePrice = "prevClosePrice"
    lastPrice = "lastPrice"
    lastQty = "lastQty"
    bidPrice ="bidPrice"
    bidQty = "bidQty"
    askPrice = "askPrice"
    askQty = "askQty"
    openPrice = "openPrice"
    highPrice = "highPrice"
    lowPrice = "lowPrice" 
    volume = "volume"
    quoteVolume = "quoteVolume"    

class SymbolFrame(pd.DataFrame):

    @staticmethod
    def get_float_field() -> list:
        fields = ["priceChange", "priceChangePercent", "weightedAvgPrice", "prevClosePrice", "lastPrice", "lastQty", "bidPrice", "bidQty", "askPrice", "askQty", "openPrice", "highPrice", "lowPrice", "volume", "quoteVolume"]
        return fields

    def __init__(self, *args, **kwargs):
        super(SymbolFrame, self).__init__(*args, **kwargs)
    
    def type_data(self):
        fields = SymbolFrame.get_float_field()
        for field in fields:
            self[field] = self[field].astype(float)
        self['symbol_name'] = self['symbol']
        return self

    @property
    def _constructor(self):        
        return SymbolFrame

    @staticmethod
    def init(data : object, fields_order : list = None):
        data : SymbolFrame = SymbolFrame(data)
        data = data.type_data()
        if fields_order is not None:
            data = data.sort_values(by=fields_order, ascending=False)
        data.set_index('symbol', inplace=True)
        return data

    @staticmethod
    def refresh(data, exchange):
        data_stats_tmp = exchange.get_stadistics_symbols()
        data_stats_tmp = data_stats_tmp[['lastPrice', 'bidPrice', 'askPrice', 'priceChangePercent', 'priceChange', 'volume', 'quoteVolume']].copy()
        data.drop(labels=['lastPrice_new', 'bidPrice_new', 'askPrice_new', 'priceChangePercent_new', 'priceChange_new', 'volume_new','quoteVolume_new'], axis=1, inplace=True, errors='ignore')
        data = data.join(data_stats_tmp, on="symbol", rsuffix='_new')
        data = data.sort_values(by=['priceChangePercent_new'], ascending=False)
        data['order'] = range(0, 0+len(data))
        data_stats_not = data[~(((data.order < 3)) | (data.signal.isin([StatusTrade.BUY])))]
        data = data[(((data.order < 3)) | (data.signal.isin([StatusTrade.BUY])))]
        #data_stats_not = data[~(((data.order > 0)) | (data.signal.isin([StatusTrade.BUY])))]
        #data = data[(((data.order >= 0)) | (data.signal.isin([StatusTrade.BUY])))]
        data.drop(labels=['lastPrice', 'bidPrice', 'askPrice', 'priceChangePercent', 'priceChange', 'volume','quoteVolume'], axis=1, inplace=True, errors='ignore')
        data.rename(columns={'lastPrice_new':'lastPrice', 'bidPrice_new':'bidPrice', 'askPrice_new':'askPrice', 'priceChangePercent_new':'priceChangePercent', 'priceChange_new':'priceChange', 'volume_new':'volume','quoteVolume_new':'quoteVolume'}, inplace=True)
        data_stats_not.drop(labels=['lastPrice', 'bidPrice', 'askPrice', 'priceChangePercent', 'priceChange', 'volume','quoteVolume'], axis=1, inplace=True, errors='ignore')
        data_stats_not.rename(columns={'lastPrice_new':'lastPrice', 'bidPrice_new':'bidPrice', 'askPrice_new':'askPrice', 'priceChangePercent_new':'priceChangePercent', 'priceChange_new':'priceChange', 'volume_new':'volume','quoteVolume_new':'quoteVolume'}, inplace=True)        
        return data, data_stats_not
    
    def get_list_symbols(self):
        lista = self.index.values.copy()
        lista.sort()
        return lista
    
    def set_values(self, symbol_name, row):
        self.at[symbol_name, 'IND_SIGNAL'] = 0
        self.at[symbol_name, 'stop_loss_prev'] = 0.0
        if (not row is None) and (not row.empty):
            self.at[symbol_name, 'IND_SIGNAL'] = row.SIGNAL
            self.at[symbol_name, 'has_stop_loss'] = row.has_stop_loss
            self.at[symbol_name, 'has_take_profit'] = row.has_take_profit
            self.at[symbol_name, 'has_trailing_stop'] = row.has_trailing_stop
            self.at[symbol_name, 'has_trailing_profit'] = row.has_trailing_profit
            self.at[symbol_name, 'trailing_stop'] = row.trailing_stop
            self.at[symbol_name, 'trailing_profit'] = row.trailing_profit
            self.at[symbol_name, 'stop_loss_prev'] = row.stop_loss
        return self

    def update_signals(self):
        self['signal'] = np.where((self.signal == StatusTrade.NO_SIGNAL) & (self.IND_SIGNAL == 1), StatusTrade.SIGNAL, self.signal)
        self['signal'] = np.where((self.signal == StatusTrade.BUY) & (self.IND_SIGNAL == -1), StatusTrade.SELL, self.signal)
        return self
    
    def set_price(self, symbol_name, exchange, price=None):
        if price is None:
            price = float(exchange.get_current_price(symbol_name))
            self.at[symbol_name, 'current_price'] = price
        else:
            self.at[symbol_name, 'current_price'] = price
        self.at[symbol_name, 'pnl_partial'] = roe(self.loc[symbol_name].entry_price, price)
        return self

    def check_symbols_to_sell(self, exchange):
        data_tmp = self.get_assets_buys()
        bdone = False
        for symbol_name in data_tmp.index:
            current_price = float(exchange.get_current_price(symbol_name))
            row = self.loc[symbol_name]
            prev_current_price = row.current_price
            self.set_price(symbol_name, exchange)
            stop_loss = row.stop_loss

            on_sell = (row.has_stop_loss and current_price < stop_loss)
            on_sell = on_sell or (row.has_take_profit and current_price > row.take_profit)
            on_sell = on_sell or (row.has_trailing_stop and prev_current_price > row.trailing_stop and current_price < row.trailing_stop)
            on_sell = on_sell or (row.has_trailing_profit and prev_current_price > row.trailing_profit and current_price < row.trailing_profit)

            if on_sell:
                self.at[symbol_name, 'signal'] = StatusTrade.SELL
                self.set_price(symbol_name, exchange)
                bdone = True
        del data_tmp        
        return self, bdone

    def get_assets_buys(self):
        '''Funcion que devuelve los assets que se deben comprar'''
        return self[self.signal == StatusTrade.BUY].copy()
    
    def get_assets_sells(self):
        '''Funcion que devuelve los assets que se deben vender'''
        return self[self.signal == StatusTrade.SELL].copy()

    def get_assets_signals(self):
        '''Funcion que devuelve los assets que no se deben hacer nada'''
        return self[self.signal == StatusTrade.SIGNAL].copy()

    def has_stop_loss(self, symbol_name):
        '''Funcion que devuelve True si el asset tiene un stop_loss'''
        return self.loc[symbol_name].has_stop_loss
    
    def has_take_profit(self, symbol_name):
        '''Funcion que devuelve True si el asset tiene un take_profit'''
        return self.loc[symbol_name].has_take_profit

    def set_stop_loss(self, symbol_name, stop_loss):
        '''Funcion que establece el stop_loss del asset'''
        self.at[symbol_name, 'stop_loss'] = stop_loss
        return self

    def set_take_profit(self, symbol_name, take_profit):
        '''Funcion que establece el take_profit del asset'''
        self.at[symbol_name, 'take_profit'] = take_profit
        return self
    
    def set_trailing_stop(self, symbol_name, trailing_stop):
        '''Funcion que establece el trailing_stop del asset'''
        self.at[symbol_name, 'trailing_stop'] = trailing_stop
        return self
    
    def set_trailing_profit(self, symbol_name, trailing_profit):
        '''Funcion que establece el trailing_profit del asset'''
        self.at[symbol_name, 'trailing_profit'] = trailing_profit
        return self

    def on_stop_loss(self, symbol_name):
        '''Funcion que establece el has_stop_loss del asset'''
        self.at[symbol_name, 'has_stop_loss'] = True
        return self
    
    def off_stop_loss(self, symbol_name):
        '''Funcion que establece el has_stop_loss del asset'''
        self.at[symbol_name, 'has_stop_loss'] = False
        return self
    
    def on_take_profit(self, symbol_name):
        '''Funcion que establece el has_take_profit del asset'''
        self.at[symbol_name, 'has_take_profit'] = True
        return self
    
    def off_take_profit(self, symbol_name):
        '''Funcion que establece el has_take_profit del asset'''
        self.at[symbol_name, 'has_take_profit'] = False
        return self
    
    def on_trailing_stop(self, symbol_name):
        '''Funcion que establece el has_trailing_stop del asset'''
        self.at[symbol_name, 'has_trailing_stop'] = True
        return self
    
    def off_trailing_stop(self, symbol_name):
        '''Funcion que establece el has_trailing_stop del asset'''
        self.at[symbol_name, 'has_trailing_stop'] = False
        return self
    
    def on_trailing_profit(self, symbol_name):
        '''Funcion que establece el has_trailing_profit del asset'''
        self.at[symbol_name, 'has_trailing_profit'] = True
        return self
    
    def off_trailing_profit(self, symbol_name):
        '''Funcion que establece el has_trailing_profit del asset'''
        self.at[symbol_name, 'has_trailing_profit'] = False
        return self
    
    def set_symbol_to_buy(self, symbol_name, price, quantity):
        self.at[symbol_name, 'entry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.at[symbol_name, 'signal'] = StatusTrade.BUY
        self.at[symbol_name, 'entry_price'] = price
        self.at[symbol_name, 'side'] = Client.SIDE_BUY
        self.at[symbol_name, 'quantity'] = quantity
        self.at[symbol_name, 'pnl_partial'] = 0.0
        self.at[symbol_name, 'symbol_name'] = symbol_name
        self.at[symbol_name, 'current_price'] = price
        return self

    def get_row(self, symbol):
        return self.loc[symbol].copy()

    def set_signal(self, symbol_name, signal: StatusTrade):
        self.at[symbol_name, 'signal'] = signal
        return self

    def reset_symbol(self, symbol_name):
        self.at[symbol_name, 'signal'] = StatusTrade.NO_SIGNAL
        self.at[symbol_name, 'entry_price'] = 0.0
        self.at[symbol_name, 'side'] = 'None'
        self.at[symbol_name, 'quantity'] = 0.0
        self.at[symbol_name, 'pnl_partial'] = 0.0
        self.at[symbol_name, 'entry_date'] = ""
        self.at[symbol_name, 'current_price'] = 0.0
        self.at[symbol_name, 'stop_loss'] = 0.0
        self.at[symbol_name, 'take_profit'] = 0.0
        self.at[symbol_name, 'trailing_stop'] = 0.0
        self.at[symbol_name, 'trailing_profit'] = 0.0
        self.at[symbol_name, 'has_stop_loss'] = False
        self.at[symbol_name, 'has_take_profit'] = False
        self.at[symbol_name, 'has_trailing_stop'] = False
        self.at[symbol_name, 'has_trailing_profit'] = False
        return self
    
    def set_side(self, symbol_name, side):
        self.at[symbol_name, 'side'] = side
        return self

    def set_elapsed_time(self):
        self['elapsed_time'] = 0
        self['ratio_time'] = 0
        today = datetime.now()
        self['elapsed_time'] =  np.where(self.entry_date != "", today - pd.to_datetime(self.entry_date, format="%Y-%m-%d %H:%M:%S"), today-today)
        self['elapsed_time'] = self['elapsed_time'].apply(pd.to_timedelta).astype('timedelta64[m]').astype(int)
        self['ratio_time'] =  np.where( self['elapsed_time'] > 0, (100 * ((self['current_price'] / self['entry_price']) -1)) / self['elapsed_time'], 0)
        return self
    
    def set_pnl(self, symbol_name, pnl):
        self.at[symbol_name, 'pnl_partial'] = pnl
        return self