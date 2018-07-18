# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 09:38:08 2018

@author: jap1e09
"""

import pandas as pd

def indexDataFrame(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)

class Descriptives():
    def __init__(self, data_series,missing_data_value = -1):
        self.data_series = data_series
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
        self.values = values
        
        zero_readings = values[values == 0]
        self.zero_count = zero_readings.size
        self.zero_percent = round(100*self.zero_count / self.total_count,2)
        
        

if __name__ == '__main__':

    metrics = ['loadweigh.kg', 'bluetooth.devices']
    
    #filepath = 'C:\\Users\\lwb1u18\\Internship\\datafiles\\fulldata20180717.h5'
    filepath = './datafiles/cddb.h5'

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


filepath = './datafiles/cddb.h5'

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

metric_descriptives = {}

for metric in metrics:
    if metric in vehicleDf.columns:
        metric_descriptives[metric] = Descriptives(vehicleDf[metric])

