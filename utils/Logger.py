from utils.Configuracion import Config
import logging
import logging.handlers as handlers
from utils.Funciones import singleton

@singleton
class Logger:
    
    __logger  = None
    __config = Config()    

    def __init__(self):
        self.__logger = logging.getLogger(self.__config.getAppName())
        self.__logger.setLevel(logging.INFO)
        logHandler = handlers.TimedRotatingFileHandler(self.__config.getNameFileLog(), when=self.__config.getFreqLogLog(), interval=self.__config.getIntervalLog())
        logHandler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logHandler.setFormatter(formatter)
        self.__logger.addHandler(logHandler)
        self.__logger.info("Iniciando Logger")

    def info(self, message):
        self.__logger.info(message)
    
    def error(self, message):
        self.__logger.error(message)
    
    def debug(self, message):
        self.__logger.warning(message)
    
    def warning(self, message):
        self.__logger.warning(message)
    
    def critical(self, message):
        self.__logger.critical(message)
