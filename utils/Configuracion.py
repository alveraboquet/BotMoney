import configparser
from utils.Constantes import Const
from utils.Funciones import singleton

@singleton
class Config(object):
    
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read(Const.CONFIG_FILE_NAME)
        

        self.__exchange_name = 'Binance'
        print('---------------------------------------')
        
    def setExchange(self, exchange_name):
        self.__exchange_name = exchange_name

    def getExchange(self):
        return self.__exchange_name

    def getApiKey(self):
        return self.__config[self.__exchange_name.upper()][Const.ATTR_KEY_NAME]

    def getApiSecret(self):
        return self.__config[self.__exchange_name.upper()][Const.ATTR_PWD_NAME]

    def getAppName(self):
        return self.__config['DEFAULT'][Const.ATTR_APP_NAME]
    
    def getNameFileLog(self):
        return self.__config['LOGGER'][Const.ATTR_FILE_LOG]

    def getIntervalLog(self):
        return int(self.__config['LOGGER'][Const.ATTR_INTERVAL_LOG])

    def getFreqLogLog(self):
        return self.__config['LOGGER'][Const.ATTR_FREQ_LOG]
    
    def getFormatLog(self):
        return self.__config['LOGGER'][Const.ATTR_FORMAT_LOG]

    def getConnectionString(self):
        return self.__config['DATABASE'][Const.CONNECTION_STRING]

    def is_debug(self):
        return self.__config['DEFAULT'][Const.DEBUG]

    def getTelegramIDs(self):
        return self.__config['TELEGRAM'][Const.TELEGRAM_TOKEN_ID], self.__config['TELEGRAM'][Const.TELEGRAM_CHAT_ID], self.__config['TELEGRAM'][Const.TELEGRAM_API_SEND_MESSAGE]
