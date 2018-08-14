import pandas as pd
import numpy as np
import os
import yaml
import General_Functions as gen

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))

filepath = config['datafilepath']+config['datafilename']
trainjournDf, vehjournDf = gen.build_frames_from_file(filepath)

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2)).mean()

# Calculate Averages for dependent variables:
def create_avgDf(trainDf, vehDf, non_zero=False):
    avg_frames = {}
    for Df, name in zip([trainDf, vehDf], ['Train', 'Vehicle']):
        if name == 'Train':
            grouping = ['RouteSignature', pd.Grouper(level='tiplocIndex'), 'MatchedDepartureTime']
        else:
            grouping = ['RouteSignature', pd.Grouper(level='tiplocIndex'), 'MatchedDepartureTime', pd.Grouper(level='sequence')]
        
        if non_zero==True:
            Df = gen.remove_zeros(Df)
            Df = gen.remove_nan(Df)
        averages = Df.groupby(grouping, sort=False)['loadweigh.kg'].transform('mean')
        counts = Df.groupby(grouping, sort=False)['loadweigh.kg'].transform('count')
        error = Df.groupby(grouping, sort=False)['loadweigh.kg'].transform('sem')
        
        avg_frames[name] = pd.DataFrame()
        avg_frames[name]['Date']=Df['date']
        avg_frames[name]['loadweigh.kg'] = Df['loadweigh.kg']
        avg_frames[name]['AVG_Loadweigh'] = averages
        avg_frames[name]['Counts'] = counts
        avg_frames[name]['from_avg'] = abs(avg_frames[name]['loadweigh.kg'] - avg_frames[name]['AVG_Loadweigh']) 
        avg_frames[name]['Dataset RMSE'] = rmse( avg_frames[name]['AVG_Loadweigh'], avg_frames[name]['loadweigh.kg'])
        avg_frames[name]['Grouped Error'] = error
        
    return avg_frames
        
averagesDf = create_avgDf(trainjournDf, vehjournDf, non_zero=True)
averagesDf['Train'].to_csv('../../Tableau/datafiles/train_averages_nonzero.csv')
averagesDf['Vehicle'].to_csv('../../Tableau/datafiles/vehicle_averages_nonzero.csv')
vehjournDf.to_csv('../../Tableau/datafiles/vehjourn_20180814.csv')
trainjournDf.to_csv('../../Tableau/datafiles/trainjourn_20180814.csv')