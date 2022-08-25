from Exchanges.Binance.Spot.interfaces.IStrategy import IStrategy
from utils.Constantes import Const

class StrategyCrossOver(IStrategy):
    def __init__(self):
        pass

    def on_init(self, exchange, config):
        super().__init__("CrossOver", exchange, config)
        self.has_stoploss=True
        self.has_takeprofit=False
        self.has_trailing_profit=False
        self.has_trailing_stoploss=False
        
    def next_row(self, data):
        '''Metodo que retorna una señal de compra/venta para cada activo'''
        print(data)
        input('...')
        return data