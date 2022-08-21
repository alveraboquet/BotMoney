from decimal import Decimal


class Balance:
    '''Clase para manejae el balance de la cuenta'''
    def __init__(self, ojson, symbol_name):
        obalances = ojson['balances']
        oasset = list(filter(lambda x: True if x['asset']==symbol_name else False, obalances))[0]
        self.asset = oasset['asset']
        self.free = Decimal(oasset['free'])
        self.locked = Decimal(oasset['locked'])
        self.update_time = ojson['updateTime']
        self.maker_comission = Decimal(ojson["makerCommission"])
        self.taker_comission =Decimal(ojson["takerCommission"])
        self.buyer_comission =Decimal(ojson["buyerCommission"])
        self.seller_comission =Decimal(ojson["sellerCommission"])
        self.can_trade = ojson["canTrade"]
        self.can_with_draw = ojson["canWithdraw"]
        self.can_deposit = ojson["canDeposit"]
        self.account_type = ojson["accountType"]