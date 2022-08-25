import pandas as pd
import numpy as np
from enum import Enum
from binance import Client
from utils.Funciones import roe

class StatusTrade(Enum):
    LONG = 0
    SHORT = 1

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
    current_price = 'current_price'
    PNL = 'PNL'
    unPNL = 'unPNL'
    quantity = 'quantity'
    status = 'status'

    @staticmethod
    def dtypes():
        return ['str', 'str', 'float', 'str', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', StatusTrade]

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
        data : TradesFrame = TradesFrame(np.empty(0, dtype=list(zip(ColumnsTradesFrame.columns(), ColumnsTradesFrame.dtypes()))))
        return data

    def set_trade(self, symbol_name, status, quantity, stop_loss, take_profit, trailing_stop, trailing_profit, current_price, exit_price):

        if symbol_name in self.index:
            row = self.loc[symbol_name]

            if quantity is not None and row.quatity != quantity:
                self.at[symbol_name, ColumnsTradesFrame.quantity.value] = quantity

            if stop_loss is not None and row.stop_loss != stop_loss:
                self.at[symbol_name, ColumnsTradesFrame.stop_loss.value] = stop_loss

            if take_profit is not None and row.take_profit != take_profit:
                self.at[symbol_name, ColumnsTradesFrame.take_profit.value] = take_profit

            if trailing_stop is not None and row.quatity != trailing_stop:
                self.at[symbol_name, ColumnsTradesFrame.trailing_stop.value] = trailing_stop

            if trailing_profit is not None and row.quatity != trailing_profit:
                self.at[symbol_name, ColumnsTradesFrame.trailing_profit.value] = trailing_profit

            if current_price is not None and row.current_price != current_price:
                self.at[symbol_name, ColumnsTradesFrame.current_price.value] = current_price
                self.at[symbol_name, ColumnsTradesFrame.unPNL.value] = roe(row.entry_price, current_price) * quantity

            if exit_price is not None and row.exit_price != exit_price:
                self.at[symbol_name, ColumnsTradesFrame.exit_price.value] = exit_price
                self.at[symbol_name, ColumnsTradesFrame.PNL.value] = roe(row.entry_price, row.exit_price) * quantity

            return self
        else:
            row = {ColumnsTradesFrame.symbol_name.value : symbol_name,
                        ColumnsTradesFrame.quantity.value:quantity,
                        ColumnsTradesFrame.status.value:status,
                        ColumnsTradesFrame.stop_loss.value:stop_loss,
                        ColumnsTradesFrame.take_profit.value:take_profit,
                        ColumnsTradesFrame.trailing_stop.value:trailing_stop,
                        ColumnsTradesFrame.trailing_profit.value:trailing_profit}
            return self.append(row, ignore_index=True)
    
    def get_trades(self):
        return self.copy()
