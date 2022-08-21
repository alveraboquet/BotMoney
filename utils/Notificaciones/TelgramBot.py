from utils.Configuracion import Config
from utils.Funciones import singleton
import requests

@singleton
class TelegramBot(object):
    
    __TOKEN, __CHAT_ID, __API = None, None, None
    __config = Config()

    def __init__(self):
        self.__TOKEN, self.__CHAT_ID, self.__API = self.__config.getTelegramIDs()
        pass

    def notify(self, message):
        try:
            results = requests.get((self.__API) % (str(self.__TOKEN), str(self.__CHAT_ID), message), )
            self.__log.info(results.json())
            return results
        except Exception as e:
            #exception(e)      
            pass
            