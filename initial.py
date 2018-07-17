import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import yaml

config = yaml.load(open("config.yml", 'r'))


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

# Joining both the train and vehicle dataframes with the journey data frames
# Creates two dataframes, one wth the train as a whole and one with the individual vehicles - Also renames the loadweigh and buetooth columns

trainjournDf = pd.concat([journeyDf,trainDf], axis=1, sort='false')
vehjournDf = journeyDf.join(vehicleDf, how='right')
vehjournDf.set_index('sequence', append=True, inplace=True, drop = False)
trainjournDf.rename(columns = {'loadweigh.kg':'loadweigh', 'bluetooth.devices':'bluetooth'}, inplace=True)
vehjournDf.rename(columns = {'loadweigh.kg':'loadweigh', 'bluetooth.devices':'bluetooth'}, inplace=True)

#Creating the new dataframe containing the required parameters

infoDf = pd.DataFrame(columns= ('Parameter Name', 'Value')) 

# calculating the number of days and adding to the info dataframe

idDF = (trainjournDf.reset_index(drop=True).UniqueJourneyId)
n_id = idDF.nunique()
idno_date = idDF.unique()
idno_date = np.array([idno_date[x][:8] for x in np.arange(n_id)])
no_days = len(np.unique(idno_date))
infoDf.loc[infoDf.shape[0]+1] = ['No. of Days With Data' , int(no_days)]

#finding the first and last date and adding those to the info dataframe
#Start by creating a new dataframe with only the dates of the journeys

date = pd.DataFrame(data = [np.array([idno_date[x][:4] for x in np.arange(n_id)]), np.array([idno_date[x][4:6] for x in np.arange(n_id)]), np.array([idno_date[x][6:8] for x in np.arange(n_id)])], dtype='int64')
date = date.transpose()
date.columns = ['Year', 'Month', 'Day']

# Sort through the newly created dataframes by year, then month then day to find the earliest and latest dates

max_year = (date.loc[date.Year == date.Year.max()])
max_month = (max_year.loc[max_year.Month == max_year.Month.max()])
max_date = (max_month.loc[max_month.Day == max_month.Day.max()])
min_year = (date.loc[date.Year == date.Year.min()])
min_month = (min_year.loc[min_year.Month == min_year.Month.min()])
min_date = (min_month.loc[min_month.Day == min_month.Day.min()])

#Format the date and add it to the info database

max_date = max_date.reset_index()
min_date = min_date.reset_index()
max_date = datetime.date(max_date.Year.loc[0], max_date.Month.loc[0], max_date.Day.loc[0])
min_date = datetime.date(min_date.Year.loc[0], min_date.Month.loc[0], min_date.Day.loc[0])
infoDf.loc[infoDf.shape[0]+1] = ['Earliest Date' , min_date]
infoDf.loc[infoDf.shape[0]+1] = ['Latest Date' , max_date]

#finding the percentage of days with data and adding it to infoDF

delta = min_date - max_date
delta = (np.abs(delta.days))
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Days with Data', format((no_days/(delta+1)), '.2g')]

#Adding number of journeys and number of legs to the infoDF

infoDf.loc[infoDf.shape[0]+1] = ['No. of Journeys', n_id]
infoDf.loc[infoDf.shape[0]+1] = ['No. of Journey Legs', trainjournDf.shape[0]]
infoDf.loc[infoDf.shape[0]+1] = ['Average No. of Legs Per Journey',format((trainjournDf.shape[0]/n_id), '.3g')]

# Adding metric data per vehicle to infoDF

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


# Looking at the metrics for the vehicles specifically using groupby  

for s in config['data_types']:    
    countsDf = (vehjournDf.loc[:,s].groupby(level=[0,1]).count())
    infoDf.loc[infoDf.shape[0]+1] = ['Trains made up of 12 units all giving '+s ,sum(countsDf == 12)]
    infoDf.loc[infoDf.shape[0]+1] = ['Trains made up of 8 units all giving '+s ,sum(countsDf == 8)]
    infoDf.loc[infoDf.shape[0]+1] = ['Trains made up of 4 units all giving '+s ,sum(countsDf == 4)]
    infoDf.loc[infoDf.shape[0]+1] = ['Number of trains missing complete '+ s +' data' ,idDF.shape[0] - (sum(countsDf == 4)+sum(countsDf==8)+sum(countsDf==12))]

infoDf.set_index('Parameter Name', inplace=True)
infoDf.to_csv('C:\\Users\\lwb1u18\\Internship\Analytics Dataframes\InfoDF20180717.csv')
