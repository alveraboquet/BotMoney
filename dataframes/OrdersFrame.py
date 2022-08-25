import pandas as pd
import numpy as np
from enum import Enum
from binance import Client
from datetime import datetime
class StatusOrder(Enum):
    CREATED = 0
    SEND = 1
    COMPLETED = 2
    PARTIAL = 3

class TypeQty(Enum):
    USD=0
    PERCENT=1
    QTY=2

class ColumnsOrderFrame(Enum):
    symbol_name = 'symbol_name'
    create_date = 'create_date'
    price = 'price'
    quantity = 'quantity'
    side = 'side'
    order_type = 'order_type'
    status = 'status'
    stop_loss = 'stop_loss'
    take_profit = 'take_profit'
    trailing_stop = 'trailing_stop'
    trailing_profit = 'trailing_profit'
    type_qty = 'type_qty'

    @staticmethod
    def dtypes():
        return ['str', 'str', 'float', 'float', 'str', 'str', StatusOrder, 'float', 'float', 'float', 'float']

    @staticmethod
    def columns():
        return [column.value for column in ColumnsOrderFrame]

class OrdersFrame(pd.DataFrame):

    def __init__(self, *args, **kwargs):
        super(OrdersFrame, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return OrdersFrame

    @staticmethod
    def create_empty_orders():
        data : OrdersFrame = OrdersFrame(np.empty(0, dtype=list(zip(ColumnsOrderFrame.columns(), ColumnsOrderFrame.dtypes()))))
        return data

    def create_order(self, symbol_name, price=np.nan, quantity=np.nan, side=Client.SIDE_BUY, order_type=Client.ORDER_TYPE_MARKET, status = StatusOrder.CREATED, stop_loss = np.nan, take_profit = np.nan, trailing_stop = np.nan, trailing_profit = np.nan, type_qty: TypeQty = TypeQty.USD):

        row = {ColumnsOrderFrame.symbol_name.value : symbol_name,
                    ColumnsOrderFrame.side.value:side,
                    ColumnsOrderFrame.create_date.value:datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ColumnsOrderFrame.quantity.value:quantity,
                    ColumnsOrderFrame.order_type.value:order_type,
                    ColumnsOrderFrame.status.value:status,
                    ColumnsOrderFrame.stop_loss.value:stop_loss,
                    ColumnsOrderFrame.take_profit.value:take_profit,
                    ColumnsOrderFrame.trailing_stop.value:trailing_stop,
                    ColumnsOrderFrame.trailing_profit.value:trailing_profit,
                    ColumnsOrderFrame.price.value:price,
                    ColumnsOrderFrame.type_qty.value:type_qty}
        return self.append(row, ignore_index=True)

    def get_orders(self, status=StatusOrder.CREATED, side=Client.SIDE_BUY):
        return self[((self.status==status) & (self.side == side))].copy()
