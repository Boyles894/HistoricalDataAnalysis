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

# Joining both the train and vehicle dataframes with the journey data frames, also adds a date column
# Creates two dataframes, one wth the train as a whole and one with the individual vehicles - Also renames the loadweigh and buetooth columns
        
journeyDf.insert(4, 'date', journeyDf.UniqueJourneyId.apply(f))
#journeyDf['date'] = pd.to_datetime(journeyDf['date'])
trainjournDf = pd.concat([journeyDf,trainDf], axis=1, sort='false')
vehjournDf = journeyDf.join(vehicleDf, how='right')
vehjournDf.set_index('sequence', append=True, inplace=True, drop = False)
trainjournDf.rename(columns = {'loadweigh.kg':'loadweigh', 'bluetooth.devices':'bluetooth'}, inplace=True)
vehjournDf.rename(columns = {'loadweigh.kg':'loadweigh', 'bluetooth.devices':'bluetooth'}, inplace=True)


