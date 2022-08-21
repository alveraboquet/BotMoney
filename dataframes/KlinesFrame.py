import pandas as pd
import numpy as np
from utils.Funciones import to_datetime
from utils.Constantes import Const

class KlinesFrame(pd.DataFrame):

    def __init__(self, *args, **kwargs):
        super(KlinesFrame, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return KlinesFrame

    def change_index_df(self, index_col, old_cols, new_cols):
        self['end_timestamp'] = self['end_timestamp'].astype(np.longlong)
        self['start_timestamp'] = self['start_timestamp'].astype(np.longlong)
        for idx, x in enumerate(old_cols): self[new_cols[idx]] = self[x].apply(to_datetime)
        self.set_index(index_col, inplace=True)
        return self

    @staticmethod
    def init(candels, symbol_name=None, interval=None, filter_time=None):
        data : KlinesFrame = KlinesFrame(np.array(candels, dtype='d'), columns=Const.KLINE_COLUMNS)
        data = data.change_index_df('fecha_inicio', ['start_timestamp', 'end_timestamp'], ['fecha_inicio', 'fecha_fin'])
        data['symbol_name'] = symbol_name
        data['interval'] = interval
        if filter_time is not None:
            data = data[ data['start_timestamp'] <= filter_time].copy()
        return data.copy()

    def type_data(self, dtype):
        for c, t in dtype:
            self[c] = self[c].astype(t)
        return self
