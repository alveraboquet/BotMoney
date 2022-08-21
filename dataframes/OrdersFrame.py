import pandas as pd
import numpy as np
from enum import Enum
from binance import Client

class StatusOrder(Enum):
    CREATED = 0
    SEND = 1
    COMPLETED = 2
    PARTIAL = 3

class ColumnsOrderFrame(Enum):
    symbol_name = 'symbol_name' 
    create_date = 'create_date' 
    price = 'price'
    quantity = 'quantity'
    side = 'side'
    order_type = 'order_type'
    status = 'status'

    @staticmethod
    def dtypes():
        return ['str', 'str', 'float', 'float', 'str', 'str', StatusOrder]

    @staticmethod
    def columns(): 
        return [column.value for column in ColumnsOrderFrame]

class OrdersFrame(pd.DataFrame):

    def __init__(self, *args, **kwargs):
        super(OrdersFrame, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return OrdersFrame
    
    def create_order(self, symbol_name, price=np.nan, quantity=np.nan, side=Client.SIDE_BUY, order_time=Client.ORDER_TYPE_MARKET, status = StatusOrder.CREATED):
        pass
    

