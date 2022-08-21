'''
, 'orderListId': -1
, 'clientOrderId': 'IAW91Yxqbf9OAvsqHWV6OQ'
, 'transactTime': 1656155842992
, 'price': '0.00000000'
, 'origQty': '270.00000000'
, 'executedQty': '270.00000000'
, 'cummulativeQuoteQty': '99.98100000'
, 'status': 'FILLED'
, 'timeInForce': 'GTC'
, 'type': 'MARKET'
, 'side': 'BUY'
, 'fills': [{'price': '0.37030000'
, 'qty': '270.00000000'
, 'commission': '0.00031347'
, 'commissionAsset': 'BNB'
, 'tradeId': 61869113}]}
'''

class Order():
    '''Clase para manejar las ordenes de compra y venta'''

    def __init__(self, str_order):
        self.order_id = str_order['orderId']
        self.client_order_id = str_order['clientOrderId']
        self.executed_qty = str_order['executedQty']
        self.side = str_order['side']
        self.status = str_order['status']
        self.cum_qty = float(str_order['cummulativeQuoteQty'])
        self.orig_qty = float(str_order['origQty'])
        self.price = float(sum([item['price'] for item in str_order['fills']])/len(str_order['fills']))