from gettext import npgettext
from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE, SYMBOL_TYPE_SPOT, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT
from utils.Funciones import exception, to_timestamp_gtc
from binance.enums import *
from binance.helpers import round_step_size
from time import sleep

from dataframes.KlinesFrame import KlinesFrame

from utils.Configuracion import Config
from utils.Notificaciones.TelgramBot import TelegramBot
from utils.Funciones import singleton, instance, interval_to_second

from Exchanges.Binance.Spot.classes.Symbol import Symbol
from Exchanges.Binance.Spot.classes.Balance import Balance
from Exchanges.Binance.Spot.classes.Order import Order
from Exchanges.Binance.Spot.classes.Info import Info
from Exchanges.Binance.Spot.classes.Book import Book
from dataframes import SymbolFrame
import urllib.parse
import csv
import os.path
from os import path
import numpy as np
from utils.Logger import Logger
from decimal import Decimal
from Exchanges.Binance.Spot.interfaces.IExchange import IExchange
from datetime import datetime
from time import time

@singleton
class Spot(IExchange):

    symbols = []
    def __init__(self, args):
        super().__init__(args)
        self.update_data_exchange()

    def update_data_exchange(self):
        oinfo_exchange = self.__client.get_exchange_info()
        oinfo_symbols = oinfo_exchange['symbols']
        oinfo_symbols_filter = list(filter(lambda x: True if x['quoteAsset']==self.asset and 'SPOT' in x['permissions'] and  x['isSpotTradingAllowed'] and x['status'] == 'TRADING' else False, oinfo_symbols))
        self.symbols = [Info(str_symbol) for str_symbol in oinfo_symbols_filter if not str_symbol['symbol'] in ['BTCBUSD', 'BNBBUSD', 'KP3RBUSD', 'ETHBUSD', 'TUSDBUSD', 'USDCBUSD', 'USDTBUSD','USDPBUSD']]

    def get_symbols(self):
        symbol_list = ",".join(['"'+symbol.symbol_name+'"' for symbol in self.symbols]).replace("'", '"')
        symbol_list_string = urllib.parse.quote("["+symbol_list+"]")
        datos = self.__client.get_ticker(symbols=symbol_list_string)
        data_symbol : SymbolFrame = SymbolFrame.SymbolFrame.init(datos, fields_order=[SymbolFrame.ColumnsSymbolFrame.priceChangePercent.value])
        return data_symbol

    def get_candels(self, symbol_name, interval=Client.KLINE_INTERVAL_1MINUTE, limit=500):
        '''Obtiene las velas del activo'''
        segundos = interval_to_second(interval)
        filter_time = ((time() - time() % (segundos))*1000)-1
        candels = self.__client.get_klines(symbol=symbol_name, interval=interval, limit=limit)
        last_time = candels[len(candels)-1][6]
        while last_time < (time()*1000):
            candels = self.__client.get_klines(symbol=symbol_name, interval=interval, limit=limit)
            last_time = candels[len(candels)-1][6]
        data : KlinesFrame = KlinesFrame.init(candels, symbol_name, interval, filter_time=filter_time)
        return data
      
    def get_balance(self, asset):
        '''Obtiene el balance del activo'''
        try:
            info = self.__client.get_account()
            return Balance(info, asset)
        except Exception as excep:
            exception(self.__log, self.__bot)
        return None

    def close_order(self, side, symbol_name, quantity):
        '''Cierra una orden'''
        symbol = list(filter(lambda x: True if x.symbol_name==symbol_name else False, self.symbols))[0]
        quantity = round_step_size(quantity, symbol.step_size)
        str_order = self.__client.create_order(symbol=symbol.symbol_name,
                                                        side=side,
                                                        type=ORDER_TYPE_MARKET,
                                                        quantity=quantity,
                                                        timestamp=to_timestamp_gtc(datetime.now()))                                                     
        if str_order:
            order = Order(str_order)
            order_id = order.order_id
            while order.status != Client.ORDER_STATUS_FILLED:
                sleep(1)
                order = self.get_order(symbol.symbol_name, order_id)
                self.__bot.notify("Bucle de orden close")
            self.update_amount()
            return order
        return None
    
    def get_pip(self, symbol_name):
        '''Obtiene el pip del activo'''
        symbol = list(filter(lambda x: True if x.symbol_name==symbol_name else False, self.symbols))[0]
        return float(symbol.tick_size)
        
    def close_order_test(self, side, symbol_name, quantity):
        '''Cierra una orden'''
        symbol = list(filter(lambda x: True if x.symbol_name==symbol_name else False, self.symbols))[0]
        quantity = round_step_size(quantity, symbol.step_size)
        str_order = self.__client.create_test_order(symbol=symbol.symbol_name,
                                                        side=side,
                                                        type=ORDER_TYPE_MARKET,
                                                        quantity=quantity,
                                                        timestamp=to_timestamp_gtc(datetime.now()))
        self.update_amount(1)
        return None

    def send_order_test(self, side, symbol_name, amount):
        '''Envia una orden'''
        symbol = list(filter(lambda x: True if x.symbol_name==symbol_name else False, self.symbols))[0]
        if symbol.notional >= self.amount:
            value = symbol.notional+1
            amount = Decimal(value)
        
        str_order = self.__client.create_test_order(symbol=symbol.symbol_name,
                                                        side=side,
                                                        type=ORDER_TYPE_MARKET,
                                                        quoteOrderQty=amount,
                                                        timestamp=to_timestamp_gtc(datetime.now()))
        self.update_amount(-1)                                                        
        return None

    def send_order(self, side, symbol_name, amount):
        '''Envia una orden'''
        symbol = list(filter(lambda x: True if x.symbol_name==symbol_name else False, self.symbols))[0]
        if symbol.notional >= self.amount:
            value = symbol.notional+1
            amount = Decimal(value)
        str_order = self.__client.create_order(symbol=symbol.symbol_name,
                                                        side=side,
                                                        type=ORDER_TYPE_MARKET,
                                                        quoteOrderQty=amount,
                                                        timestamp=to_timestamp_gtc(datetime.now()))
        if str_order:
            order = Order(str_order)
            order_id = order.order_id
            while order.status != Client.ORDER_STATUS_FILLED:
                sleep(1)
                order = self.get_order(symbol.symbol_name, order_id)
                self.__bot.notify("Bucle de orden")
            self.update_amount(0)             
            return order
        return None

    def get_current_price(self, symbol_name) -> Decimal:
        '''Obtiene el precio actual'''
        oticker = self.__client.get_symbol_ticker(symbol=symbol_name)
        ticker = Symbol(oticker)
        return ticker.price

    def update_amount(self, sign=0):
        """Funcion para actualizar el disponible"""
        if not self.test:
            self.balance = self.get_balance() #Correcto
        else:
            self.balance.free = self.balance.free + (sign*self.amount)
        self.is_available_amount = (self.balance.free - self.amount) > 0

    def get_books_order(self, symbol_name):
        """Funcion para obtener los books de ordenes"""
        try:
            ojson = self.__client.get_order_book(symbol=symbol_name, limit=1000)
            book = Book(ojson)
            return book
        except Exception as error:
            exception(error)
            return None

    def get_order(self, symbol_name, order_id):
        try:
            oOrder = self.__client.get_order(symbol=symbol_name, orderId=order_id, timestamp=to_timestamp_gtc(datetime.now()))
            return Order(oOrder)
        except Exception as error:
            exception(error)
            return None

    def get_iterator_data(self, symbol_name, interval, start_time, end_time):
        st = start_time.replace(',', '').replace(' ', '_')
        et = end_time.replace(',', '').replace(' ', '_')
        directory = f'./data_test/simple/{interval}'
        if not path.exists(directory):
             os.makedirs(directory)
        filename = f'{symbol_name}-{st}-{et}.csv'
        full_path = path.join(directory, filename)
        if path.exists(full_path):
            return full_path
        else:
            f = open(full_path, 'w')
            writer = csv.writer(f)
            for kline in self.__client.get_historical_klines_generator(symbol_name, interval, start_str=start_time, end_str=end_time):
                writer.writerow(kline)
            f.close()
            return full_path 


    def get_iterator_data_all(self, symbol_name, interval, start_time, end_time):
        f = open(f'data_test/{interval}/multiple/{symbol_name}.csv', 'w')
        writer = csv.writer(f)
        for kline in self.__client.get_historical_klines_generator(symbol_name, interval, start_str=start_time, end_str=end_time):
            writer.writerow(kline)
        f.close()
        print('Descarga',symbol_name, interval, 'completa', sep= ' ')        