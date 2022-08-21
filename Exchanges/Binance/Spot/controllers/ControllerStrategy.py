from utils.Configuracion import Config
from utils.Funciones import instance, sleep_time, exception
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
    '''
    def notify_common(self):
        data_tmp = self.strategy.get_assets_buys()
        texto = 'Resumen:\n'
        un_pnl_total = 0.0
        notifica = False
        for symbol_name in data_tmp.index:
            row = self.strategy.on_notify(symbol_name)
            un_pnl_total += row.pnl_partial
            texto += f'\tS: {symbol_name} - G: {round(100*row.pnl_partial, 2)}\n'
            notifica = True
        texto += f'Total uPnl: {round(100*un_pnl_total, 2)}\n'
        texto += f'Total Pnl: {round(100*self.pnl_total, 2)}'
        del data_tmp
        if notifica:
            self.__bot.notify(texto)

    def notify_in_interval(self):
        if time() >= self.time_notify:
            self.notify_common()
            self.time_notify = time() + (60 - time() % 60)
    '''
    def data(self):
        """Funcion para obtener los datos de la api"""
        self.close_orders()
        self.open_orders()
        self.notify_in_interval()
    
    def open_order(self, trade):
        entry_price, order, quantity  = 0.0, None, 0.0
        if self.config.realtest:
            order = self.exchange.send_order_test(Client.SIDE_BUY, trade.symbol_name, trade.quantity)
            entry_price = float(self.exchange.get_current_price(trade.symbol_name))
        else:
            order = self.exchange.send_order(trade.side, trade.symbol_name, trade.quantity)
            entry_price, quantity = order.price, order.executed_qty
        row = self.strategy.on_buy(trade, entry_price, quantity)
        self.notificar(item_order=row)

    def open_orders(self):
        trades = self.strategy.get_trades_create_for_buy()
        for index, trade in trades.iterrows():
            if self.exchange.is_available_amount:
                self.open_order(trade)
            '''
            else:
                if (not replace_list is None) and len(replace_list) > 0:
                    del_item = replace_list.pop(0)
                    self.close_order(del_item)
                    self.open_order(symbol_name)
                else:
                    self.strategy.on_exclude_buy(symbol_name)
            '''
    
    def close_order(self, trade):
        order, exit_price = None, 0.00
        if not self.config.realtest:
            order = self.exchange.close_order(trade.side, trade.symbol_name, trade.quantity)
            exit_price = order.price
        else:
            self.exchange.update_amount(1)
            exit_price = float(self.exchange.get_current_price(trade.symbol_name))
        trade = self.strategy.on_sell(trade, exit_price)
        self.notificar(trade)
        self.strategy.on_end_sell(trade)

    def close_orders(self):
        trades = self.strategy.get_trades_create_for_sell()
        for index, trade in trades.iterrows():
            self.close_order(trade)
        del trades
    '''
    def notificar(self, str_start="", item_order=None):
        """Funcion para notificar por telegram"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.config.realtest:
            now = item_order["entry_date"]
        trace = f'Activo: {item_order["symbol_name"]}'
        trace += f' # Op: {item_order["side"]}'
        trace += f' # Disponible: {round(self.exchange.balance.free, 8)}'
        trace += f' # Op. Gan: {round(100*item_order["pnl_partial"], 2)}'
        trace += f' # Ganancia: {round(100*self.pnl_total, 2)}'
        trace += f' # Op. Precio: {round(item_order["entry_price"], 8)}'
        trace += f' # Ct. Precio: {round(item_order["current_price"], 8)}'
        trace += f' # SL: {round(item_order["stop_loss"], 8)}'
        trace += f' # TK: {round(item_order["take_profit"], 8)}'
        trace += f' # TS: {round(item_order["trailing_stop"], 8)}'
        trace += f' # TP: {round(item_order["trailing_profit"], 8)}'
        trace += f' # uPnL: {round(100*self.un_pnl_total, 8)}'
        trace += f' # Inversion: {round(self.exchange.amount, 8)}'
        if self.config.realtest:
            texto = str_start+f'Fecha: {item_order["entry_date"]} -'+trace
            print(texto)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            texto = f'Fecha: {now} \n'+trace.replace(' # ', '\n').strip()
            self.__bot.notify(texto)
    '''
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