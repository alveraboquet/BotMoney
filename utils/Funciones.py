import importlib
import sys, os
from time import time
from binance.helpers import interval_to_milliseconds
from datetime import datetime
import numpy as np
from dataframes.TradesFrame import TradesFrame

from utils.Notificaciones.TelgramBot import TelegramBot

bot=TelegramBot()

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

def instance(module : str, class_name : str, *args, **kw):
    module = importlib.import_module(module+'.'+class_name)
    class_ = getattr(module, class_name)
    return class_(*args, **kw)

def to_datetime(timestamp):
    fecha = datetime.utcfromtimestamp(timestamp/1000)
    return np.datetime64(fecha).astype('datetime64[s]')

def exception(log, bot) -> None:
    try:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        bot.notify("Excepcion revisar el Log.")
        log.error(('\t%s - %s - %d - %s') % (exc_type, fname, exc_tb.tb_lineno, e.with_traceback(exc_tb), ))
        while (exc_tb):
            if exc_tb and exc_tb.tb_next:
                exc_tb = exc_tb.tb_next
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno, e.with_traceback(exc_tb))
                log.error(('\t%s - %s - %d - %s') % (exc_type, fname, exc_tb.tb_lineno, e.with_traceback(exc_tb), ))
            exc_tb = exc_tb.tb_next  
    except Exception as e:
        print(e)

def sleep_time(seconds : float) -> None:
    """Funcion para esperar un tiempo"""
    sleep_t = time() + (seconds - time() % seconds)
    while time() <= sleep_t:
        pass

def roe(entry_price : float, current_price :float) -> float:
    """Funcion para obtener el ratio"""
    pgain : float = 0.0
    if entry_price > 0:
        pgain = ((current_price / entry_price) - 1)
    return pgain

def interval_to_second(interval):
    letra = interval[-1:]
    DIT2 = {'m':1, 'h':60, 'd':1440}
    return 60*DIT2[letra]*int(interval[:-1])

def to_timestamp_gtc(dt): 
    return int((dt - datetime(1970, 1, 1)).total_seconds() * 1000)

def summary(trades : TradesFrame, timer : int):
    if time() >= timer:
        texto = 'Resumen:\n'
        un_pnl_total = 0.0
        notifica = False
        for _, trade in trades.iterrows():
            un_pnl_total += trade.unPNL
            pnl_total += trade.PNL
            texto += f'\tS: {trade.symbol_name} - G: {round(100*trade.unPNL, 2)}\n'
            notifica = True
        texto += f'Total uPnl: {round(100*un_pnl_total, 2)}\n'
        texto += f'Total Pnl: {round(100*pnl_total, 2)}'
        if notifica:
            bot.notify(texto)
        timer = time() + (60 - time() % 60)
    return timer
    