import pandas as pd
import numpy as np
import datetime
import os
import yaml
import General_Functions as gen

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))
datafile = os.path.normpath(config['datafilepath'] + config['datafilename'])

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


def GetAnalytics(vehDf, traDf, Startdate, Enddate, metric):
    vehDf = gen.filter_df_by_date(vehDf,Startdate,Enddate)
    traDf = gen.filter_df_by_date(traDf,Startdate,Enddate)
    
    journey_descriptives = JourneyDescriptives(vehDf,metric).descriptives_df
    metric_descriptives = MetricDescriptives(vehDf[metric]).descriptives_df
    all_descriptives = pd.concat([metric_descriptives,journey_descriptives])

    return all_descriptives

#----------------------------------------------------------------------------------------------------------------------

trainjournDf, vehjournDf = gen.build_frames_from_file(datafile)


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
