import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import yaml

config = yaml.load(open("config.yml", 'r'))

f = lambda x : datetime.date(int(x[:4]), int(x[4:6]), int(x[6:8]))

def indexDataFrame(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)
        
class Descriptives():
    def __init__(self, data_series,missing_data_value = -1):
      #  self.data_series = data_series
        self.total_count = data_series.size
        
        values = data_series.dropna()
        self.non_null_count = values.size
        self.non_null_percent = round(100*self.non_null_count / self.total_count,2)
        
        non_missing_data = values != missing_data_value
        values = values[non_missing_data]      
        self.useful_count = values.size
        self.useful_percent = round(100*self.useful_count / self.total_count,2)
                       
        self.mean = round(values.mean(),2)
        self.median = values.median()
        self.std = round(values.std(),2)
 #       self.values = values
        
        zero_readings = values[values == 0]
        self.zero_count = zero_readings.size
        self.zero_percent = round(100*self.zero_count / self.total_count,2)

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

# Selects only a certain range of dates to be included in the analysis 
#vehjournDf = vehjournDf.loc[vehjournDf['date'] <= '2018-05-23']
#trainjournDf = trainjournDf.loc[trainjournDf['date'] <= '2018-05-23']


infoDf = pd.DataFrame(columns= ('Parameter Name', 'Value')) 

infoDf.loc[infoDf.shape[0]+1] = ['No. of Days With Data' , trainjournDf.date.nunique()]
infoDf.loc[infoDf.shape[0]+1] = ['Earliest Date', min(trainjournDf.date).date()]
infoDf.loc[infoDf.shape[0]+1] = ['Earliest Date', max(trainjournDf.date).date()]
delta = min(trainjournDf.date).date() - max(trainjournDf.date).date()
delta = (np.abs(delta.days))
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Days with Data', format((trainjournDf.date.nunique()/(delta+1)), '.2g')]

infoDf.loc[infoDf.shape[0]+1] = ['No. of Journeys', trainjournDf.UniqueJourneyId.nunique()]
infoDf.loc[infoDf.shape[0]+1] = ['No. of Journey Legs', trainjournDf.shape[0]]
infoDf.loc[infoDf.shape[0]+1] = ['Average No. of Legs Per Journey',format((trainjournDf.shape[0]/trainjournDf.UniqueJourneyId.nunique()), '.3g')]

# Adding metric data per vehicle to infoDF
'''
infoDf.loc[infoDf.shape[0]+1] = ['No. of Vehicle Legs', (vehjournDf.shape[0])]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Loadweigh Data (Not NaN or 0)', format(((vehjournDf.loadweigh.notna().sum())-(sum(vehjournDf.loadweigh == 0))) /(vehjournDf.shape[0]), '.2g')]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of "0" Vehicle Loadweigh measurements', format((sum(vehjournDf.loadweigh == 0))/(vehjournDf.shape[0]), '.2g')]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Loadweigh' , format(vehjournDf.loadweigh.groupby(vehjournDf.loadweigh == 0).mean().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Vehicle Loadweigh Standard Deviaton' , format(vehjournDf.loadweigh.groupby(vehjournDf.loadweigh == 0).std().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Bluetooth Data', format(((vehjournDf.bluetooth.notna().sum())/(vehjournDf.shape[0])), '.2g')]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Bluetooth' ,  format(vehjournDf.bluetooth.groupby(vehjournDf.bluetooth == 0).mean().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Vehicle Bluetooth Standard Deviaton' , format(vehjournDf.bluetooth.groupby(vehjournDf.bluetooth == 0).std().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Manual Count Data', format(((vehjournDf.manualcount.notna().sum())/(vehjournDf.shape[0])), '.2g')]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Manual Count' , format(vehjournDf.manualcount.groupby(vehjournDf.manualcount == 0).mean().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Vehicle Manual Count Standard Deviaton' , format(vehjournDf.manualcount.groupby(vehjournDf.manualcount == 0).std().iloc[0], '.2f')]

#adding metric data per train to infoDf

infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Trains with Loadweigh Data (Not NaN or 0)', format(((trainjournDf.loadweigh.notna().sum())-(sum(trainjournDf.loadweigh == 0)))/(trainjournDf.shape[0]), '.2g')]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Train Loadweigh' , format(trainjournDf.loadweigh.groupby(trainjournDf.loadweigh == 0).mean().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Train Loadweigh Standard Deviaton' , format(trainjournDf.loadweigh.groupby(trainjournDf.loadweigh == 0).std().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Trains with Bluetooth Data', format(((trainjournDf.bluetooth.notna().sum()-(sum(trainjournDf.bluetooth == 0)))/(trainjournDf.shape[0])), '.2g')]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Train Bluetooth' , format(trainjournDf.bluetooth.groupby(trainjournDf.bluetooth == 0).mean().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Train Bluetooth Standard Deviaton' , format(trainjournDf.bluetooth.groupby(trainjournDf.bluetooth == 0).std().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Trains with Manual Count Data', format(((trainjournDf.manualcount.notna().sum()-(sum(trainjournDf.manualcount == 0)))/(trainjournDf.shape[0])), '.2g')]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Train Manual Count' , format(trainjournDf.manualcount.groupby(trainjournDf.manualcount == 0).mean().iloc[0], '.2f')]
infoDf.loc[infoDf.shape[0]+1] = ['Train Manual Count Standard Deviaton' , format(trainjournDf.manualcount.groupby(trainjournDf.manualcount == 0).std().iloc[0], '.2f')]
'''

# Looking at the metrics for the vehicles specifically using groupby  

for s in config['data_types']:    
    countsDf = (vehjournDf.loc[:,s].groupby(level=[0,1]).count())
    infoDf.loc[infoDf.shape[0]+1] = ['Trains made up of 12 units all giving '+s ,sum(countsDf == 12)]
    infoDf.loc[infoDf.shape[0]+1] = ['Trains made up of 8 units all giving '+s ,sum(countsDf == 8)]
    infoDf.loc[infoDf.shape[0]+1] = ['Trains made up of 4 units all giving '+s ,sum(countsDf == 4)]
    infoDf.loc[infoDf.shape[0]+1] = ['Number of trains missing complete '+ s +' data' ,trainjournDf.shape[0] - (sum(countsDf == 4)+sum(countsDf==8)+sum(countsDf==12))]


        
metric_descriptives = pd.Series()

for metric in config['data_types']:
    sez =pd.Series()
    for attr_name in dir(Descriptives(vehicleDf[metric])):
        if attr_name[0] != '_':
            attr_value = getattr(Descriptives(vehicleDf[metric]), attr_name)
            sez.loc[attr_name] = attr_value
    metric_descriptives = pd.concat([metric_descriptives, sez], axis=1, sort=False)
            

    

#infoDf.set_index('Parameter Name', inplace=True)
#infoDf.to_csv('C:\\Users\\lwb1u18\\Internship\Analytics Dataframes\InfoDf-before-20180523.csv')
