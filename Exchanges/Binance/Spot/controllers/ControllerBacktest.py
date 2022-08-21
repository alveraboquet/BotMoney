import pandas as pd
import numpy as np
from utils.ExtendedDataFrame import ExtendedDataFrame 
from backtesting import Backtest, Strategy
from backtesting.test import SMA, GOOG
from utils.singleton import instance
import csv
from utils.Constantes import Const
from utils.Funciones import * 
import os.path
from os import path
from pathlib import Path  

class ControllerBacktest(Strategy):

    def init(self):
        self.status = 0
        pass
   
    def next(self):
        if self.status == 0 and self.data.SIGNAL[-1] == 1:
            self.buy()
            self.status = 1
        elif self.status == 1 and self.data.SIGNAL[-1] == -1:
            #self.trades[0].close()
            self.status = 0

    @staticmethod
    def backtest_run(args):      
        exchange = instance("Exchange."+args.exchange, args.exchange, args)  
        full_path_file = exchange.get_iterator_data(args.symbol, args.interval, args.start_date, args.end_date)
        symbol_str = full_path_file.split('/')[-1].split('-')[0]
        with open(full_path_file) as csv_file:
            candels = csv.reader(csv_file, delimiter=',')
            candels = [ele for ele in list(candels) if ele != []]
            data = ExtendedDataFrame(np.array(list(candels), dtype='d'), columns=Const.KLINE_COLUMNS)
            data = change_index_df(data, 'FECHA_INICIO',
                                    ['START_TIMESTAMP', 'END_TIMESTAMP'],
                                    ['FECHA_INICIO', 'FECHA_FIN'],
                                    interval=args.interval)
            module_strategy = instance("Exchange."+args.exchange+".Strategies", "Strategies")
            strategy = getattr(module_strategy, args.strategy)
            data = strategy(data)
            data_test = data[data.SIGNAL == 1]
            data = data[data.index >= data_test.index.values[0]]
            status = 0
            data['current_signal'] = 0
            for date in data.index:
                if status == 0 and data.loc[date].SIGNAL == 1:
                    data.at[date, 'entry_price'] = data.loc[date].CLOSE_PRICE
                    data.at[date, 'entry_date'] = data.loc[date].FECHA_INICIO
                    data.at[date, 'current_signal'] = 2
                    status = 2
                elif status == 2 and data.loc[date].SIGNAL == -1:
                    data.at[date, 'entry_price'] = data.loc[date].CLOSE_PRICE
                    data.at[date, 'entry_date'] = data.loc[date].FECHA_INICIO
                    data.at[date, 'current_signal'] = -1
                    status = 0                    
            data = data[data.current_signal != 0]
            data['exit_price'] = data['entry_price'].shift(-1)
            data['exit_date'] = data['entry_date'].shift(-1)
            row = data.iloc[-1]
            if row.current_signal == 2:
                id = data.index.values[-1]
                data.at[id, 'exit_price'] = float(exchange.get_current_price(symbol_str))
                data.at[id, 'exit_date'] = datetime.now()
            data = data.dropna()
            data['ROE'] = (data['exit_price'] / data['entry_price']) -1 
            data['% ROE'] = ((data['exit_price'] / data['entry_price']) -1)*100
            data['tiempo'] = data['exit_date'] - data['entry_date']
            data['Retorno'] = data['ROE'] * 100
            minf = data['FECHA_INICIO'].min()
            maxf = data['FECHA_INICIO'].max()
            data.set_index('FECHA_INICIO', inplace=True)
            grupo = data['ROE'].resample(rule='M').agg(['sum'])
            grupo['sum'] =grupo['sum']*100
            tiempo = data['tiempo'].sum()
            PnL = data['ROE'].sum() * 100
            num_trades = len(data)*2
            print('Simbolo:', symbol_str)
            print('Fecha. Ininio:', minf)
            print('Fecha. Fin:', maxf)
            print('Ganancias:', PnL)
            print('Retorno:', data['Retorno'].sum())
            print('Tiempo:', tiempo)
            print('Trades:', num_trades)
            print('Min Pnl:', data['ROE'].min()*100)
            print('Max Pnl:', data['ROE'].max()*100)
            print('Min Time Trade:', data['tiempo'].min())
            print('Max Time Trade:', data['tiempo'].max())
            print('Avg Time Trade:', data['tiempo'].mean())
            print(grupo)
    

    @staticmethod
    def download_data(args):
        exchange = instance("Exchange."+args.exchange, args.exchange, args)  
        data = exchange.get_stadistics_symbols()
        symbols = data.index.values
        iterator = 0
        for item in symbols:
            exchange.get_iterator_data_all(item, args.interval, args.start_date, args.end_date)
            iterator += 1
            sys.stdout.write('\b'*(10000*len(f"Descargando paquete {symbols}...{iterator} / {len(symbols)}")))
            sys.stdout.write(f"Descargando paquete {symbols}...{iterator} / {len(symbols)}")
            sys.stdout.flush()
            sleep(1)
        return data

    @staticmethod
    def multi_backtest(args):
        directorio = f'./data_test/multiple/{args.interval}'
        #f = open(f'data_test/{interval}/multiple/{symbol_name}.csv', 'r')
        '''
        contenido = os.listdir(directorio)
        data = None
        for file in contenido:
            with open(path.join(directorio, file)) as csv_file:
                candels = csv.reader(csv_file, delimiter=',')
                candels = [ele for ele in list(candels) if ele != []]
                data_temp = ExtendedDataFrame(np.array(list(candels), dtype='d'), columns=Const.KLINE_COLUMNS)
                data_temp = change_index_df(data_temp, 'FECHA_INICIO', ['START_TIMESTAMP', 'END_TIMESTAMP'], ['FECHA_INICIO', 'FECHA_FIN'], interval=args.interval)
                data_temp['SYMBOL'] = file.split('-')[0].split('.')[0]
                if data is None:
                    data = data_temp.copy()
                else:
                    data = pd.concat([data, data_temp.copy()])
                del data_temp
        data.to_csv("data_set.csv", index=False)
        

        with open("/workspaces/BotMoney/data_test/multiple/1h/data_set.csv") as csv_file:
            candels = csv.reader(csv_file, delimiter=',')
            next(candels)
            candels = [ele for ele in list(candels) if ele != []]
            cols = Const.KLINE_COLUMNS
            cols.append('SYMBOL')
            data = ExtendedDataFrame(np.array(list(candels), dtype='d'), columns=cols)
            data = change_index_df(data, 'FECHA_INICIO',
                                    ['START_TIMESTAMP', 'END_TIMESTAMP'],
                                    ['FECHA_INICIO', 'FECHA_FIN'],
                                    interval=args.interval)*
        '''   
        data = ExtendedDataFrame(pd.read_csv('/workspaces/BotMoney/data_test/multiple/1h/data_set.csv'))
        data.sort_values(by=['START_TIMESTAMP'], inplace = True, )
        
        lista_symbol = list(set(data.SYMBOL.values.tolist()))
        data_final = None
        for item in lista_symbol:
            temp_data = data[data.SYMBOL==item].copy()
            temp_data['PCT'] = temp_data.CLOSE_PRICE.pct_change(periods=24)
            temp_data['VOLUME_24h'] = temp_data.VOLUME.rolling(24).sum()
            temp_data['ASSET_VOLUME_24h'] = temp_data.QUOTE_ASSET_VOLUME.rolling(24).sum()
            temp_data['VOLUME_24h_PREV'] = temp_data.VOLUME_24h.shift(1)
            temp_data['ASSET_VOLUME_24h_PREV'] = temp_data.ASSET_VOLUME_24h.shift(1)
            temp_data['PCT_PREV'] = temp_data.PCT.shift(1)
            temp_data.dropna(inplace=True)
            if data is None:
                data_final = temp_data.copy()
            else:
                data_final = pd.concat([data_final, temp_data.copy()])     
            del temp_data
        print(data_final)
        input('...')
        lista_time = list(set(data_final.START_TIMESTAMP.values.tolist()))
        lista_time = sorted(lista_time)
        temp_data = data_final[data_final.START_TIMESTAMP==lista_time[0]].copy()
        print(temp_data)
        input('...')
        for item in lista_time[1:]:
            temp_data = data_final[data_final.START_TIMESTAMP==item].copy()
            print(temp_data)
            input('...')
