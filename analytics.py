import pandas as pd
import numpy as np
import datetime
import os
import yaml
import General_Functions as gen

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))
datafile = os.path.normpath(config['datafilepath'] + config['datafilename'])

<<<<<<< HEAD
        
class Descriptives():
    def __init__(self, data_series,missing_data_value = -1):
=======
#filepath = 'C:\\Users\\lwb1u18\\Internship\\datafiles\\fulldata20180720.h5'

class JourneyDescriptives():
    def __init__(self,df,filter_variable = None):
        if 'date' not in df.columns:
            print('Dataframe has no date column')
            return

        if filter_variable is not None:
            if filter_variable not in df.columns:
                print(filter_variable + ' not in dataframe')
            else:
                df = df.dropna(subset=[filter_variable])


        self.days_with_data = df.date.nunique()
        if self.days_with_data > 0:
            self.earliest_date = min(df.date).date()
            self.latest_date = max(df.date).date()
            delta = np.abs((self.earliest_date - self.latest_date).days)
            self.frac_days_with_data = round(self.days_with_data/delta,2)
        else:
            self.earliest_date = None
            self.latest_date = None
            self.frac_days_with_data = 0

        self.journey_count = df.UniqueJourneyId.nunique()
        self.journey_leg_count = df.shape[0]
        if self.journey_count > 0:
            self.legs_per_journey = round(self.journey_leg_count/self.journey_count,2)
        else:
            self.legs_per_journey = None

        dict_descriptives = {}
        dict_descriptives['# of days with data'] = self.days_with_data
        dict_descriptives['Earliest date'] = self.earliest_date
        dict_descriptives['Latest date'] = self.latest_date
        dict_descriptives['Fraction of days with data'] = self.frac_days_with_data
        dict_descriptives['# of journeys'] = self.journey_count
        dict_descriptives['# of journey legs'] = self.journey_leg_count
        dict_descriptives['Average # of legs per journey'] = self.legs_per_journey

        self.descriptives_df = pd.DataFrame.from_dict(dict_descriptives, orient='index',columns=['value'])

class MetricDescriptives():
    def __init__(self, data_series, drop_zeros = True, missing_data_value = -1):
>>>>>>> _JAP
        self.total_count = data_series.size

        #Drop null values
        values = data_series.dropna()
        self.non_null_count = values.size
        self.non_null_percent = round(100*self.non_null_count / self.total_count,2)

        #Drop known missing data
        non_missing_data_mask = values != missing_data_value
        values = values[non_missing_data_mask]

        #Get information about zero readings
        zero_readings = values[values == 0]
        self.zero_count = zero_readings.size
        self.zero_percent = round(100 * self.zero_count / self.total_count, 2)

        if drop_zeros is True:
            non_zero_mask = values != 0
            values = values[non_zero_mask]

        self.useful_count = values.size
        self.useful_percent = round(100*self.useful_count / self.total_count,2)
        self.mean = round(values.mean(),2)
        self.median = values.median()
        self.firstqpercentile = round(values.quantile(0.25),2)
        self.lastqpercentile = round(values.quantile(0.75),2)
        self.iq_range = self.lastqpercentile - self.firstqpercentile
        self.std = round(values.std(),2)

        dict_descriptives = {}
        dict_descriptives['Non null readings'] = self.non_null_count
        dict_descriptives['Non null data (%)'] = self.non_null_percent
        dict_descriptives['Zero readings'] = self.zero_count
        dict_descriptives['Zero readings (%)'] = self.zero_percent
        dict_descriptives['Non-zero readings'] = self.useful_count
        dict_descriptives['Non-zero data (%)'] = self.useful_percent
        dict_descriptives['Mean'] = self.mean
        dict_descriptives['Median'] = self.median
        dict_descriptives['25th Percential'] = self.firstqpercentile
        dict_descriptives['75th Percential'] = self.lastqpercentile
        dict_descriptives['Interquartile Range'] = self.iq_range
        dict_descriptives['Standard Deviation'] = self.std

        self.descriptives_df = pd.DataFrame.from_dict(dict_descriptives, orient='index',columns=['value'])




def index_df(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)
        
def build_frames_from_file(filepath):

    #Read in raw dataframes and index columns from datafile
    #Index dataframes accordingly
    #The assumption is that the datafile will contain the correct dataframes
    indexes = pd.read_hdf(filepath, 'indexes')
    journeyDf = pd.read_hdf(filepath, 'journeyDf')
    index_df(journeyDf, indexes.tolist(), retainCols=True)
    vehicleDf = pd.read_hdf(filepath, 'vehicleDf')
    index_df(vehicleDf, indexes.tolist(), retainCols=False)
    trainDf = pd.read_hdf(filepath, 'trainDf')
    index_df(trainDf, indexes.tolist(), retainCols=False)

    # Check to see if journeyDf contains a 'date' column.  If not, generate one from the
    # UniqueJourneyId (assumed to be the rid).
    if 'date' in journeyDf.columns.tolist():
        pass
    else:
        # Function to extract date from rid
        f = lambda x: datetime.date(int(x[:4]), int(x[4:6]), int(x[6:8]))
        journeyDf['date'] = pd.to_datetime(journeyDf.UniqueJourneyId.apply(f))

    #Build complete train/journey dataframe
    trainjournDf = pd.concat([journeyDf,trainDf], axis=1, sort='false')

    #Build complete vehicle/journey dataframe
    vehjournDf = journeyDf.join(vehicleDf, how='right')
    vehjournDf.set_index('sequence', append=True, inplace=True, drop = False)

    return trainjournDf, vehjournDf

def filter_df_by_date(df, start_date,end_date):
    if 'date' not in df.columns:
        print('Dataframe has no date column')
        return df

    mask = (df['date'] >= str(start_date)) & (df['date'] <= str(end_date))
    return df[mask]








def GetAnalytics(vehDf, traDf, Startdate, Enddate, metric):
    #vehDf = vehDf.loc[(vehDf['date'] >= str(Startdate)) & (vehDf['date'] <= str(Enddate))]
    #traDf = traDf.loc[(traDf['date'] >= str(Startdate)) & (traDf['date'] <= str(Enddate))]
    vehDf = filter_df_by_date(vehDf,Startdate,Enddate)
    traDf = filter_df_by_date(traDf,Startdate,Enddate)
    
    # geninfoDf = pd.DataFrame(columns= ('Parameter Name', 'Value'))
    # geninfoDf.loc[geninfoDf.shape[0]+1] = ['No. of Days With Data' , traDf.date.nunique()]
    # geninfoDf.loc[geninfoDf.shape[0]+1] = ['Earliest Date', min(traDf.date).date()]
    # geninfoDf.loc[geninfoDf.shape[0]+1] = ['Earliest Date', max(traDf.date).date()]
    # delta = min(traDf.date).date() - max(traDf.date).date()
    # delta = (np.abs(delta.days))
    # geninfoDf.loc[geninfoDf.shape[0]+1] = ['Fraction of Days with Data', format((traDf.date.nunique()/(delta+1)), '.3g')]
    #
    # geninfoDf.loc[geninfoDf.shape[0]+1] = ['No. of Journeys', traDf.UniqueJourneyId.nunique()]
    # geninfoDf.loc[geninfoDf.shape[0]+1] = ['No. of Journey Legs', traDf.shape[0]]
    # geninfoDf.loc[geninfoDf.shape[0]+1] = ['Average No. of Legs Per Journey',format((traDf.shape[0]/traDf.UniqueJourneyId.nunique()), '.3g')]
 
    # for s in config['data_types']:
    #     countsDf = (vehDf.loc[:,s].groupby(level=[0,1]).count())
    #     geninfoDf.loc[geninfoDf.shape[0]+1] = ['Trains made up of 12 units all giving '+s ,sum(countsDf == 12)]
    #     geninfoDf.loc[geninfoDf.shape[0]+1] = ['Trains made up of 8 units all giving '+s ,sum(countsDf == 8)]
    #     geninfoDf.loc[geninfoDf.shape[0]+1] = ['Trains made up of 4 units all giving '+s ,sum(countsDf == 4)]
    #     geninfoDf.loc[geninfoDf.shape[0]+1] = ['Number of trains missing complete '+ s +' data' ,traDf.shape[0] - (sum(countsDf == 4)+sum(countsDf==8)+sum(countsDf==12))]

    journey_descriptives = JourneyDescriptives(vehDf,metric).descriptives_df
    metric_descriptives = MetricDescriptives(vehDf[metric]).descriptives_df
    all_descriptives = pd.concat([metric_descriptives,journey_descriptives])

        # sez =pd.Series()
        # for attr_name in dir(Descriptives(vehDf[metric])):
        #     if attr_name[0] != '_':
        #         attr_value = getattr(Descriptives(vehDf[metric]), attr_name)
        #         sez.loc[attr_name] = attr_value
        # metric_descriptives = pd.concat([metric_descriptives, sez], axis=1, sort=False)
        # metric_descriptives.rename(index=str, columns={0:metric,}, inplace=True)

    return all_descriptives

#----------------------------------------------------------------------------------------------------------------------

<<<<<<< HEAD
trainjournDf, vehjournDf, journeyDf = gen.create_Dfs(filepath)
trainjournDf.to_csv('../../Tableau/datafiles/trainjournDf.csv')
vehjournDf.to_csv('../../Tableau/datafiles/vehjournDf.csv')
=======
trainjournDf, vehjournDf = build_frames_from_file(datafile)

periods = config['periods']
metrics = config.get('metrics')

descriptives = {}

for metric in metrics:

    descriptives_df = None

    for period in periods:
        startdate = periods[period]['startdate']
        enddate = periods[period]['enddate']

        if enddate is None:
            enddate = datetime.date.today()

        if descriptives_df is None:
            descriptives_df = GetAnalytics(vehjournDf,trainjournDf,startdate,enddate,metric)
            descriptives_df.rename(columns={'value':period},inplace=True)
        else:
            descriptives_df[period] = GetAnalytics(vehjournDf,trainjournDf,startdate,enddate,metric)['value']

    descriptives[metric] = descriptives_df

>>>>>>> _JAP

#allmetric_descriptives = GetAnalytics(vehjournDf, trainjournDf, config['startdate'], config['enddate'])
#befmetric_descriptives = GetAnalytics(vehjournDf, trainjournDf, config['startdate'], config['splitdate'])
#aftmetric_descriptives = GetAnalytics(vehjournDf, trainjournDf, config['splitdate'], config['enddate'])
  
#geninfoDf = pd.concat([allgeninfoDf, befgeninfoDf, aftgeninfoDf], axis=1)
#geninfoDf.columns=['Full Data Range', 'Data before '+str(config['splitdate']), 'Data after '+str(config['splitdate'])]

#metric_dfs={}
#for metric in config['data_types']:
#    metric_dfs[metric] = pd.concat([allmetric_descriptives[metric], befmetric_descriptives[metric], aftmetric_descriptives[metric]], axis=1)
#    metric_dfs[metric].columns=['Full Data Range', 'Data before '+str(config['splitdate']), 'Data after '+str(config['splitdate'])]
    #metric_dfs[metric].to_csv('C:\\Users\\lwb1u18\\Internship\Analytics Results\Dataframes\ '+str(metric)+'infoDf-19072018.csv')

#geninfoDf.to_csv('C:\\Users\\lwb1u18\\Internship\Analytics Results\ Dataframes\geninfoDf-19072018.csv')