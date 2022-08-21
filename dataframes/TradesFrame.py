import pandas as pd
import numpy as np
from enum import Enum
from binance import Client

class StatusTrade(Enum):
    BOUGTH = 0
    SOLD = 1
    
class ColumnsTradesFrame(Enum):
    symbol_name = 'symbol_name' 
    entry_date = 'entry_date' 
    entry_price = 'entry_price'
    exit_date = 'exit_date'
    exit_price = 'exit_price'
    stop_loss = 'stop_loss'
    take_profit = 'take_profit'
    trailing_stop = 'trailing_stop'
    trailing_profit = 'trailing_profit'
    PNL = 'PNL'
    unPNL = 'unPNL'
    quantity = 'quantity'
    status = 'status'

    @staticmethod
    def dtypes():
        return ['str', 'str', 'float', 'str', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'str', 'str', StatusTrade]

    @staticmethod
    def columns(): 
        return [column.value for column in ColumnsTradesFrame]

class TradesFrame(pd.DataFrame):

    def __init__(self, *args, **kwargs):
        super(TradesFrame, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return TradesFrame

    @staticmethod
    def create_empty_trades():
        print(ColumnsTradesFrame.columns())
        print(list(zip(ColumnsTradesFrame.columns(), ColumnsTradesFrame.dtypes())))
        data : TradesFrame = TradesFrame(np.empty(0, dtype=list(zip(ColumnsTradesFrame.columns(), ColumnsTradesFrame.dtypes()))))
        return data

    def create_trade(self, symbol_name, side, order_type, quantity=np.nan, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan):
        row = {ColumnsTradesFrame.symbol_name.value : symbol_name, 
                    ColumnsTradesFrame.side.value:side, 
                    ColumnsTradesFrame.quantity.value:quantity, 
                    ColumnsTradesFrame.order_type.value:order_type,
                    ColumnsTradesFrame.status.value:StatusTrade.CREATED,
                    ColumnsTradesFrame.stop_loss.value:stop_loss,
                    ColumnsTradesFrame.take_profit.value:take_profit,
                    ColumnsTradesFrame.trailing_stop.value:trailing_stop,
                    ColumnsTradesFrame.trailing_profit.value:trailing_profit}
        return self.append(row, ignore_index=True)
    
    def get_trades(self, status=StatusTrade.CREATED, side=Client.SIDE_SELL):
        return self[status==status & side == side].copy()
