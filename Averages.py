import pandas as pd
import numpy as np
import os
import datetime
import yaml
import General_Functions as gen

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))

filepath = config['datafilepath']+config['datafilename']
trainjournDf, vehjournDf = gen.build_frames_from_file(filepath)

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

def remove_zeros(DF):
    return DF.loc[DF['loadweigh.kg']!=0]

# Calculate Averages for dependent variables:
def create_avgDf(trainDf, vehDf, non_zero=False):
    avg_frames = {}
    for Df, name in zip([trainDf, vehDf], ['Train', 'Vehicle']):
        if name == 'Train':
            grouping = 'JourneyLegKey'
        else:
            grouping = ['JourneyLegKey', 'sequence']
        
        if non_zero==True:
            Df = remove_zeros(Df)
        averages = Df.groupby(grouping, sort=False)['loadweigh.kg'].transform('mean')
        counts = Df.groupby(grouping, sort=False)['loadweigh.kg'].transform('count')
        
        avg_frames[name] = Df['JourneyLegKey'].to_frame()
        avg_frames[name]['loadweigh.kg'] = Df['loadweigh.kg']
        avg_frames[name]['AVG_Loadweigh'] = averages
        avg_frames[name]['Counts'] = counts
        avg_frames[name]['from_avg'] = abs(avg_frames[name]['loadweigh.kg'] - avg_frames[name]['AVG_Loadweigh']) 
        avg_frames[name]['RMSE'] = rmse( avg_frames[name]['AVG_Loadweigh'], avg_frames[name]['loadweigh.kg'])
        
    return avg_frames


        
averagesDf = create_avgDf(trainjournDf, vehjournDf, non_zero=True)
averagesDf['Train'].to_csv('../../Tableau/datafiles/train_averages_nonzero.csv')
averagesDf['Vehicle'].to_csv('../../Tableau/datafiles/vehicle_averages_nonzero.csv')