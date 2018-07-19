import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import datetime
import yaml

config = yaml.load(open("config.yml", 'r'))

f = lambda x : datetime.date(int(x[:4]), int(x[4:6]), int(x[6:8]))

def indexDataFrame(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)
        
if __name__ == '__main__':

    filepath = 'C:\\Users\\lwb1u18\\Internship\\datafiles\\fulldata20180717.h5'

    indexes = pd.read_hdf(filepath, 'indexes')
    journeyDf = pd.read_hdf(filepath, 'journeyDf')
    indexDataFrame(journeyDf, indexes.tolist(), retainCols=True)
    vehicleDf = pd.read_hdf(filepath, 'vehicleDf')
    indexDataFrame(vehicleDf, indexes.tolist(), retainCols=False)
    try:
        trainDf = pd.read_hdf(filepath, 'trainDf')
        indexDataFrame(trainDf, indexes.tolist(), retainCols=False)
    except:
        pass
        
journeyDf.insert(4, 'date', journeyDf.UniqueJourneyId.apply(f))
journeyDf['date'] = pd.to_datetime(journeyDf['date'])
trainjournDf = pd.concat([journeyDf,trainDf], axis=1, sort='false')
vehjournDf = journeyDf.join(vehicleDf, how='right')
vehjournDf.set_index('sequence', append=True, inplace=True, drop = False)
trainjournDf.rename(columns={'loadweigh':'loadweigh.kg' , 'bluetooth':'bluetooth.devices'}, inplace=True)
vehjournDf.rename(columns={'loadweigh':'loadweigh.kg' , 'bluetooth':'bluetooth.devices'}, inplace=True)
vehjournDf = vehjournDf.loc[(vehjournDf['date'] <= str(config['splitdate']))]
trainjournDf = trainjournDf.loc[(trainjournDf['date'] <= str(config['splitdate']))]
    




Victric_lo = trainjournDf.reset_index(drop=True).set_index('FiveMin')
Victric_lo.index = Victric_lo.index.astype(int)
Victric_lo.sort_index(ascending=True, axis=0, inplace=True)
Victric_lo = Victric_lo.loc[Victric_lo['tiploc'] == 'VICTRIC']

g = Victric_lo.loc[:,'loadweigh.kg'].groupby(Victric_lo.index).mean()
g.plot(color='black')
#Victric_lo['loadweigh.kg'].plot(linestyle='none', marker='x', markersize=0.5, color='red')
plt.ylim(0,60000)