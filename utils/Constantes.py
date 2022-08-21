from enum import Enum
from binance import Client

current_row = -1
previous_row = -2

class Const():
    CONFIG_FILE_NAME = 'config.ini'
    ATTR_KEY_NAME = 'api_key'
    ATTR_PWD_NAME = 'api_secret'
    ATTR_APP_NAME = 'app_name'
    ATTR_FILE_LOG = 'file_log'
    ATTR_INTERVAL_LOG = 'interval_log'
    ATTR_FREQ_LOG = 'freg_log'
    ATTR_FORMAT_LOG = 'format_log'

    KLINE_START_TIMESTAMP = 0
    KLINE_OPEN_PRICE = 1
    KLINE_HIGH_PRICE = 2
    KLINE_LOW_PRICE = 3
    KLINE_CLOSE_PRICE = 4
    KLINE_VOLUME = 5
    KLINE_END_TIMESTAMP = 6
    KLINE_QUOTE_ASSET_VOLUME = 7
    KLINE_NUM_TRADES = 8
    KLINE_TAKER_BUY_BASE_ASSET_VOLUME = 9
    KLINE_TAKER_BUY_QUOTE_ASSET_VOLUME = 10
    KLINE_CAN_IGNORE = 11
    KLINE_COLUMNS = ['start_timestamp', 'open', 'high', 'low', 'close', 'volume', 'end_timestamp', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'can_ignore']
    #COLUMNS_TABLE = ['START_TIMESTAMP', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'CLOSE_PRICE', 'VOLUME', 'END_TIMESTAMP', 'QUOTE_ASSET_VOLUME', 'NUM_TRADES', 'TAKER_BUY_BASE_ASSET_VOLUME', 'TAKER_BUY_QUOTE_ASSET_VOLUME', 'CAN_IGNORE', 'intervalo']
    DATA_TYPE_COLUMNS = ['i8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8']

    #DATA_TYPE_COLUMNS = ['NUMERIC', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'NUMERIC', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL']
    CONNECTION_STRING='connection_string'
    DEBUG = "debug"
    DIT = {'m':'D', 'h':'D', 'd':'M', 'w':'M', 'M':'Y'}
    TELEGRAM_TOKEN_ID = 'TOKEN_ID'
    TELEGRAM_CHAT_ID = 'CHAT_ID'
    TELEGRAM_API_SEND_MESSAGE = 'API_SEND_MESSAGE'
    KLINE_INTERVALS = [Client.KLINE_INTERVAL_1MINUTE, Client.KLINE_INTERVAL_3MINUTE, Client.KLINE_INTERVAL_5MINUTE, Client.KLINE_INTERVAL_15MINUTE, Client.KLINE_INTERVAL_30MINUTE, Client.KLINE_INTERVAL_1HOUR, Client.KLINE_INTERVAL_2HOUR, Client.KLINE_INTERVAL_4HOUR, Client.KLINE_INTERVAL_6HOUR, Client.KLINE_INTERVAL_8HOUR, Client.KLINE_INTERVAL_12HOUR, Client.KLINE_INTERVAL_1DAY, Client.KLINE_INTERVAL_3DAY, Client.KLINE_INTERVAL_1WEEK, Client.KLINE_INTERVAL_1MONTH]

class WalletType(Enum):
    Spot = 'Spot'
    Futures = 'Futures'    