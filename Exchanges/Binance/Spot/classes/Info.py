from decimal import Decimal


class Info(object):
    def __init__(self, osymbol) -> None:
        super().__init__()
        self.quote_asset = osymbol['quoteAsset']
        self.symbol_name = osymbol['symbol']
        for f in osymbol['filters']:
            if f['filterType'] == 'PRICE_FILTER':
                self.tick_size = float(f['tickSize'])
            if f['filterType'] == 'LOT_SIZE':
                self.step_size = float(f['stepSize'])
            if f['filterType'] == 'MIN_NOTIONAL':
                self.notional = Decimal(f['minNotional'])
