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
def create_avgDf(trainDf, vehDf, non_zero=False, predicted_only=False):
    avg_frames = {}
    for Df, name in zip([trainDf, vehDf], ['Train', 'Vehicle']):
        if name == 'Train':
            grouping = ['RouteSignature', pd.Grouper(level='tiplocIndex'), 'MatchedDepartureTime']
        else:
            grouping = ['RouteSignature', pd.Grouper(level='tiplocIndex'), 'MatchedDepartureTime', pd.Grouper(level='sequence')]
        
        if non_zero==True:
            Df = gen.remove_zeros(Df, 'loadweigh.kg')
            Df = gen.remove_nan(Df, 'loadweigh.kg')
            
        if predicted_only==True and 'prediction' in Df.columns.tolist():
            Df = gen.remove_nan(Df, 'prediction')
            
        groups = Df.groupby(grouping, sort=False)
        averages = groups['loadweigh.kg'].transform('mean')
        counts = groups['loadweigh.kg'].transform('count')
        error = groups['loadweigh.kg'].transform('sem')
        
        avg_frames[name] = pd.DataFrame()
        avg_frames[name]['loadweigh.kg'] = Df['loadweigh.kg']
#        avg_frames[name]['Group Key'] = groups
        avg_frames[name]['AVG Group Loadweigh'] = averages
        avg_frames[name]['Group Counts'] = counts
        avg_frames[name]['from_avg'] = abs(avg_frames[name]['loadweigh.kg'] - avg_frames[name]['AVG Group Loadweigh']) 
        avg_frames[name]['Dataset RMSE'] = rmse(avg_frames[name]['AVG Group Loadweigh'], avg_frames[name]['loadweigh.kg'])
        avg_frames[name]['Grouped Error'] = error
        if 'prediction' in Df.columns.tolist():
            avg_frames[name]['prediction'] = Df['prediction'] 
            
    return avg_frames
        
averages_frames = create_avgDf(trainjournDf, vehjournDf, non_zero=True, predicted_only=True)
#averagesDf['Train'].to_csv('../../Tableau/datafiles/train_averages_nonzero.csv')
#averagesDf['Vehicle'].to_csv('../../Tableau/datafiles/vehicle_averages_nonzero.csv')
#vehjournDf.to_csv('../../Tableau/datafiles/vehjourn_20180814.csv')
#trainjournDf.to_csv('../../Tableau/datafiles/trainjourn_20180814.csv')