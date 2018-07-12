import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def indexDataFrame(df, indexColumns, retainCols=False):
    if retainCols == True:
        df.set_index(indexColumns, drop=False, inplace=True)
    else:
        df.set_index(indexColumns, drop=True, inplace=True)

if __name__ == '__main__':

    filepath = 'C:\\Users\\lwb1u18\\Internship\\Historical Data Analysis\\Datafiles\\26042017.h5'

    indexes = pd.read_hdf(filepath, 'indexes')
    journeyDf = pd.read_hdf(filepath, 'journeyDf')
    # Note that one of the leg indexes (TiplocIndex) is used in model calibration
    # and must therefore be retained as a separate column.  Hence for the journey
    # dataframe, the columns are not dropped
    indexDataFrame(journeyDf, indexes.tolist(), retainCols=True)
    vehicleDf = pd.read_hdf(filepath, 'vehicleDf')
    indexDataFrame(vehicleDf, indexes.tolist(), retainCols=False)
    try:
        trainDf = pd.read_hdf(filepath, 'trainDf')
        indexDataFrame(trainDf, indexes.tolist(), retainCols=False)
    except:
        pass

# Joining both the train and vehicle dataframes with the journey data frames
# Creates two dataframes, onw wth the train as a whole and one with the individual vehicles

trainjournDf = pd.concat([journeyDf,trainDf], axis=1, sort='false')
vehjournDf = journeyDf.join(vehicleDf, how='right')

#Creating the new dataframe containing the required parameters

infoDf = pd.DataFrame(columns= ('Parameter Name', 'Value')) 

# calculating the number of days and adding to the info dataframe

idDF = (trainjournDf.reset_index(drop=True).UniqueJourneyId)
n_id = idDF.nunique()
idno_date = idDF.unique()
idno_date = np.array([idno_date[x][:8] for x in np.arange(n_id)])
no_days = len(np.unique(idno_date))
infoDf.loc[infoDf.shape[0]+1] = ['No. of Days' , int(no_days)]

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
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Days with Data', (no_days/(delta+1))]

#Adding number of journeys and number of legs to the infoDF

infoDf.loc[infoDf.shape[0]+1] = ['No. of Journeys', n_id]
infoDf.loc[infoDf.shape[0]+1] = ['No. of Journey Legs', trainjournDf.shape[0]]
infoDf.loc[infoDf.shape[0]+1] = ['Average No. of Legs Per Journey',(trainjournDf.shape[0]/n_id)]

# Adding number of vehicle and train data points to ifoDF

infoDf.loc[infoDf.shape[0]+1] = ['No. of Vehicles', (vehjournDf.shape[0])]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Loadweigh Data', ((vehjournDf.loadweigh.notna().sum())/(vehjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of "0" Loadweigh measurements', (sum(vehjournDf.loadweigh == 0))/(vehjournDf.shape[0])]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Loadweigh' , vehjournDf.loadweigh.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Loadweigh Standard Deviaton' , vehjournDf.loadweigh.std()]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Bluetooth Data', ((vehjournDf.bluetooth.notna().sum())/(vehjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Bluetooth' , vehjournDf.bluetooth.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Bluetooth Standard Deviaton' , vehjournDf.bluetooth.std()]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Manual Count Data', ((vehjournDf.manualcount.notna().sum())/(vehjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Manual Count' , vehjournDf.manualcount.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Manual Count Standard Deviaton' , vehjournDf.manualcount.std()]






