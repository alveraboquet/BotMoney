from dataframes.TradesFrame import TradesFrame
from utils.Configuracion import Config
from utils.Funciones import instance, sleep_time, exception, summary
from utils.Logger import Logger
from utils.Notificaciones.TelgramBot import TelegramBot

from datetime import datetime
from time import time
from binance import Client

class ControllerStrategy():

    __config, __log, __bot = Config(), Logger(), TelegramBot()
    _DEBUG_= __config.is_debug()
    wait = lambda seg : time() + (seg - time() % seg)
    
    def __init__(self, config):
        self.config = config
        self.exchange = instance("Exchanges."+config.exchange+"."+config.wallet, config.wallet, config)
        self.strategy = instance("Exchanges."+config.exchange+"."+config.wallet+".strategies", "Strategy"+self.config.strategy)
        self.strategy.on_init(self.exchange, config)
        self.__bot.notify("Comenzamos con "+self.strategy.name)
        print("Comenzamos con "+self.strategy.name)
        self.count_exceptions = 0
        self.stop = False
        self.timer_summary = time() + (60 - time() % 60)
        
    def data(self):
        """Funcion para obtener los datos de la api"""
        self.close_orders()
        self.open_orders()
        self.timer_summary = summary(self.strategy.trades, self.timer_summary)
    
    def open_order(self, order):
        entry_price, order_e, quantity  = 0.0, None, 0.0
        if self.config.realtest:
            order_e = self.exchange.send_order_test(Client.SIDE_BUY, order.symbol_name, order.quantity)
            entry_price = float(self.exchange.get_current_price(order.symbol_name))
            quantity = order.quantity / entry_price
        else:
            order_e = self.exchange.send_order(order.side, order.symbol_name, order.quantity)
            entry_price, quantity = order_e.price, order_e.executed_qty
        row = self.strategy.on_buy(order, entry_price, quantity)
        #self.notificar(item_order=row)

    def open_orders(self):
        tmp_orders = self.strategy.get_orders_for_open()
        for index, order in tmp_orders.iterrows():
            if self.exchange.is_available_amount:
                self.open_order(order)
            else:
                self.strategy.on_cancel(order)
            
    
    def close_order(self, order):
        order_e, exit_price = None, 0.00
        if not self.config.realtest:
            order_e = self.exchange.close_order(order.side, order.symbol_name, order.quantity)
            exit_price, quantity = order_e.price, order_e.executed_qty
            
        else:
            self.exchange.update_amount(1)
            exit_price = float(self.exchange.get_current_price(order.symbol_name))
            quantity = order.quantity / exit_price
        trade = self.strategy.on_sell(order, exit_price, quantity)
        #self.notificar(trade)
        self.strategy.on_end_sell(trade)

    def close_orders(self):
        trades = self.strategy.get_orders_for_close()
        for index, order in trades.iterrows():
            self.close_order(order)
        del trades
    
    def notificar(self, trade:TradesFrame):
        """Funcion para notificar por telegram"""
        trace = ""
        trace = "Fecha: "+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for column in trade.columns:
            trace += f' # {column}: {trade[column]}'
            print(trace)
        
    def run(self):
        """Funcion para ejecutar el programa"""
        try:
            sleep_time(60)
            self.data()
            self.count_exceptions = 0
        except Exception as ex:
            exception(ex)
            self.count_exceptions += 1
            if self.count_exceptions == 3:
                self.count_exceptions = 0
                self.stop = self.strategy.stop