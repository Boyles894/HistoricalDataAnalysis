import pandas as pd
import numpy as np
import datetime
import yaml

filepath = 'C:\\Users\\lwb1u18\\Internship\\datafiles\\fulldata20180720.h5'

config = yaml.load(open("config.yml", 'r'))

f = lambda x : datetime.date(int(x[:4]), int(x[4:6]), int(x[6:8]))

def indexDataFrame(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)
        
class Descriptives():
    def __init__(self, data_series,missing_data_value = -1):
        self.total_count = data_series.size
        values = data_series.dropna()
        self.non_null_count = values.size
        self.non_null_percent = round(100*self.non_null_count / self.total_count,2)
        non_missing_data_mask = values != missing_data_value
        values = values[non_missing_data_mask]      
        self.useful_count = values.size
        self.useful_percent = round(100*self.useful_count / self.total_count,2)
        self.mean = round(values.mean(),2)
        self.median = values.median()
        self.std = round(values.std(),2)
        zero_readings = values[values == 0]
        self.zero_count = zero_readings.size
        self.zero_percent = round(100*self.zero_count / self.total_count,2)

def GetAnalytics(vehDf, traDf, Startdate, Enddate):
    vehDf = vehDf.loc[(vehDf['date'] >= str(Startdate)) & (vehDf['date'] <= str(Enddate))]
    traDf = traDf.loc[(traDf['date'] >= str(Startdate)) & (traDf['date'] <= str(Enddate))]
    
    geninfoDf = pd.DataFrame(columns= ('Parameter Name', 'Value')) 
    geninfoDf.loc[geninfoDf.shape[0]+1] = ['No. of Days With Data' , traDf.date.nunique()]
    geninfoDf.loc[geninfoDf.shape[0]+1] = ['Earliest Date', min(traDf.date).date()]
    geninfoDf.loc[geninfoDf.shape[0]+1] = ['Earliest Date', max(traDf.date).date()]
    delta = min(traDf.date).date() - max(traDf.date).date()
    delta = (np.abs(delta.days))
    geninfoDf.loc[geninfoDf.shape[0]+1] = ['Fraction of Days with Data', format((traDf.date.nunique()/(delta+1)), '.2g')]
    
    geninfoDf.loc[geninfoDf.shape[0]+1] = ['No. of Journeys', traDf.UniqueJourneyId.nunique()]
    geninfoDf.loc[geninfoDf.shape[0]+1] = ['No. of Journey Legs', traDf.shape[0]]
    geninfoDf.loc[geninfoDf.shape[0]+1] = ['Average No. of Legs Per Journey',format((traDf.shape[0]/traDf.UniqueJourneyId.nunique()), '.3g')]
 
    for s in config['data_types']:    
        countsDf = (vehDf.loc[:,s].groupby(level=[0,1]).count())
        geninfoDf.loc[geninfoDf.shape[0]+1] = ['Trains made up of 12 units all giving '+s ,sum(countsDf == 12)]
        geninfoDf.loc[geninfoDf.shape[0]+1] = ['Trains made up of 8 units all giving '+s ,sum(countsDf == 8)]
        geninfoDf.loc[geninfoDf.shape[0]+1] = ['Trains made up of 4 units all giving '+s ,sum(countsDf == 4)]
        geninfoDf.loc[geninfoDf.shape[0]+1] = ['Number of trains missing complete '+ s +' data' ,traDf.shape[0] - (sum(countsDf == 4)+sum(countsDf==8)+sum(countsDf==12))]
    
    metric_descriptives = pd.DataFrame()
    for metric in config['data_types']:
        sez =pd.Series()
        for attr_name in dir(Descriptives(vehDf[metric])):
            if attr_name[0] != '_':
                attr_value = getattr(Descriptives(vehDf[metric]), attr_name)
                sez.loc[attr_name] = attr_value
        metric_descriptives = pd.concat([metric_descriptives, sez], axis=1, sort=False)
        metric_descriptives.rename(index=str, columns={0:metric,}, inplace=True)
    
    geninfoDf.set_index('Parameter Name', inplace=True) 
    return geninfoDf, metric_descriptives

#----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

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

allgeninfoDf, allmetric_descriptives = GetAnalytics(vehjournDf, trainjournDf, config['startdate'], config['enddate'])
befgeninfoDf, befmetric_descriptives = GetAnalytics(vehjournDf, trainjournDf, config['startdate'], config['splitdate'])
aftgeninfoDf, aftmetric_descriptives = GetAnalytics(vehjournDf, trainjournDf, config['splitdate'], config['enddate'])
  
geninfoDf = pd.concat([allgeninfoDf, befgeninfoDf, aftgeninfoDf], axis=1)
geninfoDf.columns=['Full Data Range', 'Data before '+str(config['splitdate']), 'Data after '+str(config['splitdate'])]

metric_dfs={}
for metric in config['data_types']:
    metric_dfs[metric] = pd.concat([allmetric_descriptives[metric], befmetric_descriptives[metric], aftmetric_descriptives[metric]], axis=1)
    metric_dfs[metric].columns=['Full Data Range', 'Data before '+str(config['splitdate']), 'Data after '+str(config['splitdate'])]
    #metric_dfs[metric].to_csv('C:\\Users\\lwb1u18\\Internship\Analytics Dataframes\ '+str(metric)+'infoDf-19072018.csv')

#geninfoDf.to_csv('C:\\Users\\lwb1u18\\Internship\Analytics Dataframes\geninfoDf-19072018.csv')