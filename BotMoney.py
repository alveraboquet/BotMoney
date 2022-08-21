import argparse
from decimal import Decimal

def arguments():
        str_intervals = "\n\t - ".join(Const.KLINE_INTERVALS)
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--exchange', help='Exchange donde vamos a realizar traiding', required=True)
        parser.add_argument('-w', '--wallet', help='Exchange donde vamos a realizar traiding', required=True)
        parser.add_argument('-t', '--strategy', help=f'estrategia que queremos ejecutar {str_intervals}', required=True)
        parser.add_argument('-b', '--backtest', help=f'Realizar un backtest', action='store_true')
        parser.add_argument('-r', '--realtest', help=f'Test con datos reales', action='store_true')
        parser.add_argument('-f', '--file', help=f'fichero de configuracion')
        parser.add_argument('-m', '--multi_backtest', help=f'Numero de velas en el dataset', action='store_true')
        parser.add_argument('-d', '--download_data', help=f'Numero de velas en el dataset', action='store_true')
        parser.add_argument('-a', '--asset', help=f'Numero de velas en el dataset')
        parser.add_argument('-i', '--interval', help=f'Numero de velas en el dataset')
        #argumentos for download data
        parser.add_argument('-st', '--start_date', help=f'Fecha de incio para descargar datos Ej:1 Jul, 2021')
        parser.add_argument('-et', '--end_date', help=f'Fecha de incio para descargar datos Ej:1 Jul, 2022')
        #parser.add_argument('-sy', '--symbol', help=f'Fecha de incio para descargar datos Ej:1 Jul, 2022')
        args = parser.parse_args()
        
        Const.CONFIG_FILE_NAME = args.file
        #return args.exchange, args.symbol, args.interval, args.strategy, float(args.amount), args.backtest, args.date_backtest
        return args

from utils.Constantes import Const
args = arguments()
from utils.Funciones import singleton, instance

class App():
    #python3 BotMoneyStream.py -e Spot -s BUSD -i 1m -t one_hull -a 10 --file config.ini --limit 200 --realtest
    #python3 BotMoneyStream.py -e Spot -s BUSD -i 1h -t one_hull -a 10 --file config.ini --limit 200 --backtest -st "1 Jan, 2021" -et "14 Jul, 2022" -sy BTCBUSD
    @staticmethod
    def main():
        if not args.download_data:
            if not args.multi_backtest:
                if not args.backtest:
                    strategy = instance("Exchanges."+args.exchange+"."+args.wallet+".controllers", "ControllerStrategy", args)
                    while not strategy.stop:
                        strategy.run()
                else:
                    strategy = instance("Exchanges."+args.exchange+"."+args.wallet+".controllers", "ControllerBacktest", args)
                    strategy.backtest_run(args)
            else:
                strategy = instance("Exchanges."+args.exchange+"."+args.wallet+".controllers", "ControllerBacktest", args)
                strategy.multi_backtest(args)
        else:
            strategy = instance("Exchanges."+args.exchange+"."+args.wallet+".controllers", "ControllerBacktest", args)
            strategy.download_data(args)

if __name__=='__main__':    
    App.main() 