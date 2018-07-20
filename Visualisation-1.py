import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import datetime
import yaml
pd.options.mode.chained_assignment = None

config = yaml.load(open("config.yml", 'r'))

f = lambda x : datetime.date(int(x[:4]), int(x[4:6]), int(x[6:8]))
    

def indexDataFrame(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)
        
if __name__ == '__main__':

    filepath = 'C:\\Users\\lwb1u18\\Internship\\datafiles\\fulldata20180720.h5'

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
    

plt_1 = trainjournDf.reset_index(drop=True).set_index('FiveMin')
plt_1.index = plt_1.index.astype(int)
plt_1.sort_index(ascending=True, axis=0, inplace=True)
plots={}
for station in config['stations']:
    plots[station] = plt_1.loc[plt_1['tiploc'] == station]
    if station == 'GTWK':
        plots[station].loc[:, 'northbound'] = np.nan
        for i in np.arange(plots['GTWK'].shape[0]):
            if plots['GTWK'].loc[:, 'RouteSignature'].iloc[i][-7:-1] == 'VICTRI':
                plots[station].loc[:, 'northbound'].iloc[i] = True
            elif plots['GTWK'].loc[:, 'RouteSignature'].iloc[i][-6:-1] == 'BRGHT':
                plots[station].loc[:, 'northbound'].iloc[i] = False
        plots['northbound'+station] = plots[station].loc[plots[station]['northbound']==True]
        plots['southbound'+station] = plots[station].loc[plots[station]['northbound']==False]
            
            
def plot_loadweigh(Df, plot_name):
    avg = Df.loc[:,'loadweigh.kg'].groupby(Df.index).mean()
    avg.plot(color='black', linestyle='none', marker='o')
    Df['loadweigh.kg'].plot(linestyle='none', marker='x', markersize=0.5, color='red')
    plt.ylim(0,avg.max()+(avg.max()/4))
    plt.ylabel('Loadweigh (kg)')
    plt.xlabel('Time of day in 5 minute intervals')
    plt.title()
    plt.show()
    plt.clf()
 
    
plot_loadweigh(plots['VICTRIC'], 'London Victoria')   
plot_loadweigh(plots['BRGHTN'], 'Brighton')    
plot_loadweigh(plots['northboundGTWK'], 'Gatwick Northbound')    
plot_loadweigh(plots['southboundGTWK'], 'Gatwick Southbound') 










  