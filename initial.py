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
vehjournDf.set_index('sequence', append=True, inplace=True, drop = False)


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

# Adding metric data per vehicle to ifoDF

infoDf.loc[infoDf.shape[0]+1] = ['No. of Vehicles', (vehjournDf.shape[0])]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Loadweigh Data (Not NaN or 0)', (vehjournDf.loadweigh.notna().sum())-(sum(vehjournDf.loadweigh == 0)) /(vehjournDf.shape[0])]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of "0" Loadweigh measurements', (sum(vehjournDf.loadweigh == 0))/(vehjournDf.shape[0])]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Loadweigh' , vehjournDf.loadweigh.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Vehicle Loadweigh Standard Deviaton' , vehjournDf.loadweigh.std()]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Bluetooth Data', ((vehjournDf.bluetooth.notna().sum())/(vehjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Bluetooth' , vehjournDf.bluetooth.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Vehicle Bluetooth Standard Deviaton' , vehjournDf.bluetooth.std()]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Vehicles with Manual Count Data', ((vehjournDf.manualcount.notna().sum())/(vehjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Vehicle Manual Count' , vehjournDf.manualcount.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Vehicle Manual Count Standard Deviaton' , vehjournDf.manualcount.std()]

#adding metric data per train to infoDf

infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Trains with Loadweigh Data', ((trainjournDf.loadweigh.notna().sum())/(trainjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Train Loadweigh' , trainjournDf.loadweigh.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Train Loadweigh Standard Deviaton' , trainjournDf.loadweigh.std()]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Trains with Bluetooth Data', ((trainjournDf.bluetooth.notna().sum())/(vehjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Train Bluetooth' , trainjournDf.bluetooth.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Train Bluetooth Standard Deviaton' , trainjournDf.bluetooth.std()]
infoDf.loc[infoDf.shape[0]+1] = ['Fraction of Trains with Manual Count Data', ((trainjournDf.manualcount.notna().sum())/(vehjournDf.shape[0]))]
infoDf.loc[infoDf.shape[0]+1] = ['Mean Train Manual Count' , trainjournDf.manualcount.mean()]
infoDf.loc[infoDf.shape[0]+1] = ['Train Manual Count Standard Deviaton' , trainjournDf.manualcount.std()]


# Looking at the metrics for the vehicles specifically - the for loop iterates over the 'sequence' column and then checks if the data
#is nan. This is done for the loadweigh, bluetooth and manualcount data   

for s in ['loadweigh', 'bluetooth', 'manualcount']:
    veh12=0
    veh8=0
    veh4=0
    for i in np.arange(vehjournDf.shape[0]):
        if vehjournDf.index[i][2] == 0 and vehjournDf.index[i-12][2] == 0 and sum(vehjournDf.loc[:, s].iloc[i-12:i].isnull()) == 0 and sum(vehjournDf.loc[:,s].iloc[i-12:i]!=0) == 12:
           veh12 = veh12 +1
        elif vehjournDf.index[i][2] == 0 and vehjournDf.index[i-8][2] == 0 and sum(vehjournDf.loc[:, s].iloc[i-8:i].isnull()) == 0 and sum(vehjournDf.loc[:,s].iloc[i-8:i]!=0) == 8:
            veh8 = veh8+1
        elif vehjournDf.index[i][2] == 0 and vehjournDf.index[i-4][2] == 0 and sum(vehjournDf.loc[:, s].iloc[i-4:i].isnull()) == 0 and sum(vehjournDf.loc[:,s].iloc[i-4:i]!=0) == 4:
            veh4=veh4+1
    infoDf.loc[infoDf.shape[0]+1] = [s,veh12]
    infoDf.loc[infoDf.shape[0]+1] = [s,veh8]
    infoDf.loc[infoDf.shape[0]+1] = [s,veh4]
        
infoDf.loc[28][0] = 'Trains made up of 12 units all giving loadweigh'       
infoDf.loc[29][0] = 'Trains made up of 8 units all giving loadweigh'    
infoDf.loc[30][0] = 'Trains made up of 4 units all giving loadweigh'
infoDf.loc[31][0] = 'Trains made up of 12 units all giving bluetooth'
infoDf.loc[32][0] = 'Trains made up of 8 units all giving bluetooth'
infoDf.loc[33][0] = 'Trains made up of 4 units all giving bluetooth'
infoDf.loc[34][0] = 'Trains made up of 12 units all giving manualcount'
infoDf.loc[35][0] = 'Trains made up of 8 units all giving manualcount'    
infoDf.loc[36][0] = 'Trains made up of 4 units all giving manualcount' 

#calculating how many trains have an incomplete dataset and adding it to infoDF
missing_loadweigh = idDF.shape[0] - (infoDf.loc[28][1]+infoDf.loc[29][1]+infoDf.loc[30][1])  
missing_bluetooth = idDF.shape[0] - (infoDf.loc[31][1]+infoDf.loc[32][1]+infoDf.loc[33][1])
missing_manualcount = idDF.shape[0] - (infoDf.loc[34][1]+infoDf.loc[35][1]+infoDf.loc[36][1])
infoDf.loc[infoDf.shape[0]+1] = ['Number of Trains missing complete vehicle loadweigh data', missing_loadweigh]
infoDf.loc[infoDf.shape[0]+1] = ['Number of Trains missing complete vehicle bluetooth data', missing_bluetooth] 
infoDf.loc[infoDf.shape[0]+1] = ['Number of Trains missing complete vehicle  manualcount data', missing_manualcount]





