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
idno_date = np.array([int(x) for x in idno_date])
print (type(idno_date[67]))
no_days = len(np.unique(idno_date))
infoDf.loc[1] = ['Number of Days' , no_days]
