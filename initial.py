import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
idno_date = np.array([idno_date[n_id-1][:8] for x in np.arange(n_id)])
no_days = len(np.unique(idno_date))
infoDf.loc[infoDf.shape[0]+1] = ['Number of Days' , int(no_days)]

#finding the first and last date and adding those to the info dataframe
#Start by creating a new dataframe with only the dates of the journeys

date = pd.DataFrame(data = [np.array([idno_date[n_id-1][:4] for x in np.arange(n_id)]), np.array([idno_date[n_id-1][4:6] for x in np.arange(n_id)]), np.array([idno_date[n_id-1][6:8] for x in np.arange(n_id)])], dtype='int64')
date = date.transpose()
date.columns = ['Year', 'Month', 'Day']
date.loc[115] =[2010,8,24 ]
date.loc[116] =[2019,10,24 ]
date.loc[117] =[2019,10,25 ]
max_year = (date.loc[date.Year == date.Year.max()])
max_month = (max_year.loc[max_year.Month == max_year.Month.max()])
max_date = (max_month.loc[max_month.Day == max_month.Day.max()])
min_year = (date.loc[date.Year == date.Year.min()])
min_month = (min_year.loc[min_year.Month == min_year.Month.min()])
min_date = (min_month.loc[min_month.Day == min_month.Day.min()])
print (min_date)
print (max_date)










