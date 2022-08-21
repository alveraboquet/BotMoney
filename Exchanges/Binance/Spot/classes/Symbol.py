from decimal import Decimal

class Symbol(object):

    def __init__(self, info):
        self.symbol = str(info['symbol'])
        self.price = Decimal(info['price'])