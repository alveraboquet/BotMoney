from utils.Funciones import * 
from utils.Configuracion import Config
from utils.Notificaciones.TelgramBot import TelegramBot
from binance import Client
from utils.Logger import Logger

class IExchange():

    __client, __config, __log, __bot = None, Config(), Logger(), TelegramBot()
    _DEBUG_= __config.is_debug()
    symbols = []
    def __init__(self, args):
        self.__client = Client(self.__config.getApiKey(), self.__config.getApiSecret())
        self.asset = args.asset

    def update_data_exchange(self):
        raise NotImplementedError("Metodo no implentado")

    def get_symbols(self):
        raise NotImplementedError("Metodo no implentado")

    def get_candels(self, symbol_name, interval=Client.KLINE_INTERVAL_1MINUTE, limit=500):
        raise NotImplementedError("Metodo no implentado")
      
    def get_balance(self, asset):
        raise NotImplementedError("Metodo no implentado")

    def close_order(self, side, symbol_name, quantity):
        raise NotImplementedError("Metodo no implentado")
    
    def get_pip(self, symbol_name):
        raise NotImplementedError("Metodo no implentado")
        
    def close_order_test(self, side, symbol_name, quantity):
        raise NotImplementedError("Metodo no implentado")

    def send_order_test(self, side, symbol_name, amount):
        raise NotImplementedError("Metodo no implentado")

    def send_order(self, side, symbol_name, amount):
        raise NotImplementedError("Metodo no implentado")

    def get_current_price(self, symbol_name):
        raise NotImplementedError("Metodo no implentado")

    def update_amount(self, sign=0):
        raise NotImplementedError("Metodo no implentado")

    def get_books_order(self, symbol_name):
        raise NotImplementedError("Metodo no implentado")

    def get_order(self, symbol_name, order_id):
        raise NotImplementedError("Metodo no implentado")

    def get_iterator_data(self, symbol_name, interval, start_time, end_time):
        raise NotImplementedError("Metodo no implentado")

    def get_iterator_data_all(self, symbol_name, interval, start_time, end_time):
        raise NotImplementedError("Metodo no implentado")
