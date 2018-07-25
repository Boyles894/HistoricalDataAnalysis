import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import datetime
import os
import yaml

def get_dir(x):
    if x[-7:-1] == 'VICTRI' or x[0:5] == 'BRGHT':
        return True
    elif x[-6:-1] == 'BRGHT' or x[0:7] == 'VICTRIC'  or x[0:7] == 'VICTRIE':
        return False

def indexDataFrame(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)
        
def create_Dfs(filepath):

    #Read in raw dataframes and index columns from datafile
    #Index dataframes accordingly
    #The assumption is that the datafile will contain the correct dataframes
    indexes = pd.read_hdf(filepath, 'indexes')
    journeyDf = pd.read_hdf(filepath, 'journeyDf')
    indexDataFrame(journeyDf, indexes.tolist(), retainCols=True)
    vehicleDf = pd.read_hdf(filepath, 'vehicleDf')
    indexDataFrame(vehicleDf, indexes.tolist(), retainCols=False)
    trainDf = pd.read_hdf(filepath, 'trainDf')
    indexDataFrame(trainDf, indexes.tolist(), retainCols=False)

    # Check to see if journeyDf contains a 'date' column.  If not, generate one from the
    # UniqueJourneyId (assumed to be the rid).
    if 'date' in journeyDf.columns.tolist():
        pass
    else:
        # Function to extract date from rid
        f = lambda x: datetime.date(int(x[:4]), int(x[4:6]), int(x[6:8]))
        journeyDf['date'] = pd.to_datetime(journeyDf.UniqueJourneyId.apply(f))
    
    #Convert 5 min column to represent an actual time of day    
    t = lambda x: (5.*x)/60.
    journeyDf['FiveMin'] = journeyDf['FiveMin'].astype(float).apply(t)
    
    # Adds a column that states wether the train is headed north or south
    journeyDf.loc[:, 'northbound'] = journeyDf['RouteSignature'].apply(get_dir)  

    #Build complete train/journey dataframe
    trainjournDf = pd.concat([journeyDf,trainDf], axis=1, sort='false')

    #Build complete vehicle/journey dataframe
    vehjournDf = journeyDf.join(vehicleDf, how='right')
    vehjournDf.set_index('sequence', append=True, inplace=True, drop = False)

    return trainjournDf, vehjournDf, journeyDf
        
def select_dates(vehDf, traDf, Startdate, Enddate):
    vehDf = vehDf.loc[(vehDf['date'] >= str(Startdate)) & (vehDf['date'] <= str(Enddate))]
    traDf = traDf.loc[(traDf['date'] >= str(Startdate)) & (traDf['date'] <= str(Enddate))]
    return vehDf, traDf