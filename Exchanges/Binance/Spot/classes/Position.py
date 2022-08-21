from decimal import Decimal

class Position(object):
    '''Informacion sobre la posicion'''
    def __init__(self, position, symbol):

        pos = list(filter(lambda x: True if x['symbol']==symbol else False, position))[0]
        print(pos)
        self.symbol = pos['symbol']
        self.position_amt = Decimal(pos['positionAmt'])
        self.entry_price = Decimal(pos['entryPrice'])
        self.mark_price = Decimal(pos['markPrice'])
        self.un_realized_profit = Decimal(pos['unRealizedProfit'])
        self.liquidation_price = Decimal(pos['liquidationPrice'])
        self.leverage = Decimal(pos['leverage'])
        self.max_notional_value = Decimal(pos['maxNotionalValue'])
        self.margin_type = pos['marginType']
        self.isolated_margin = Decimal(pos['isolatedMargin'])
        self.is_auto_add_margin = pos['isAutoAddMargin']
        self.position_side = pos['positionSide']
        self.notional = Decimal(pos['notional'])
        self.isolated_wallet = Decimal(pos['isolatedWallet'])
        self.position_time = 0
        self.update_time = pos['updateTime']
        