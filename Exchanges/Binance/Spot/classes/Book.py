import pandas as pd
from decimal import Decimal

class Book():

    def __init__(self, ojson):
        self.last_update_time = ojson['lastUpdateId']
        self.e_time = ojson['E']
        self.t_time = ojson['T']
        self.data_bids = pd.DataFrame(ojson['bids'], columns=['price', 'lot_size'])
        self.data_asks = pd.DataFrame(ojson['asks'], columns=['price', 'lot_size'])
        self.data_bids.price = self.data_bids.price.astype(float)
        self.data_bids.lot_size = self.data_bids.lot_size.astype(float)
        self.data_asks.lot_size = self.data_asks.lot_size.astype(float)
        self.data_asks.price = self.data_asks.price.astype(float)
        self.data_asks['type'] = 1
        self.data_bids['type'] = -1
        self.data_bids['total'] = self.data_bids.price * self.data_bids.lot_size
        self.data_asks['total'] = self.data_asks.price * self.data_asks.lot_size

        self.data_book = pd.concat([self.data_bids, self.data_asks])
        
        
        