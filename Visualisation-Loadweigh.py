import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import datetime
import os
import yaml
pd.options.mode.chained_assignment = None

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))

filepath = os.path.normpath(config['datafilepath'] + config['datafilename'])

f = lambda x : datetime.date(int(x[:4]), int(x[4:6]), int(x[6:8]))
    

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
        
    t = lambda x: (5.*x)/60.
    journeyDf['FiveMin'] = journeyDf['FiveMin'].astype(float).apply(t)

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

def get_dir(x):
    if x[-7:-1] == 'VICTRI':
        return True
    elif x[-6:-1] == 'BRGHT':
        return False
    
def plot_loadweigh(Df, plot_name, save=False):
    avg = Df.iloc[Df.loc[:,'loadweigh.kg'].nonzero()].loc[:,'loadweigh.kg'].groupby(Df['FiveMin']).mean()
    std = Df.iloc[Df.loc[:,'loadweigh.kg'].nonzero()].loc[:,'loadweigh.kg'].groupby(Df['FiveMin']).std()
    plt.errorbar(avg.index, avg.iloc[avg.nonzero()], yerr=std,  marker='o', color='black', markersize=4, elinewidth=1, ecolor='dimgrey' )
    plt.plot(Df['FiveMin'], Df['loadweigh.kg'], linestyle='none', marker='x', markersize=0.7, color='red') 
    plt.grid()
    plt.ylim(0,avg.max()+(avg.max()/4))
    plt.xticks(np.arange(Df['FiveMin'].min().astype(int)-1, 25))
    plt.ylabel('Loadweigh (kg)')
    plt.xlabel('Time of day (24h clock)')
    plt.title(plot_name)
    if save==True:
        plt.savefig('C:\\Users\\lwb1u18\\Internship\Analytics Results\Plots\ '+plot_name+'.png')
    plt.show()
    plt.clf()
    
    
def plot_weekday(Df, plot_name):
    avg = Df.iloc[Df.loc[:,'loadweigh.kg'].nonzero()].loc[:,'loadweigh.kg'].groupby(Df['FiveMin']).mean()
    std = Df.iloc[Df.loc[:,'loadweigh.kg'].nonzero()].loc[:,'loadweigh.kg'].groupby(Df['FiveMin']).std()
    plt.errorbar(avg.index, avg.iloc[avg.nonzero()], yerr=std, linestyle='none', marker='o', color='navy', markersize=4, elinewidth=1, ecolor='dimgrey' )
    plt.plot(Df['FiveMin'], Df['loadweigh.kg'], linestyle='none', marker='x', markersize=1.5, color='mediumpurple')
    plt.grid()
    plt.ylim(0,avg.max()+(avg.max()/4))
    plt.xticks(np.arange(Df['FiveMin'].min().astype(int)-1, 25))
    plt.ylabel('Loadweigh (kg)')
    plt.xlabel('Time of day (24h clock)') 
    plt.title(plot_name)
    
def create_weekday_plots(save=False):
    for station in plots:
        for day in config['weekdays']:
            try:
                plot_weekday(weekday_plots[station+'_'+day], station+' on a '+day)
                if save==True:
                    plt.savefig('C:\\Users\\lwb1u18\\Internship\Analytics Results\Plots\WeekdayPlots\\'+station+ '\ '+station+' on a '+day+'.png')
                plt.show()
            except KeyError:
                pass
            
def create_multiday_plots(save=False):
    for station in plots:
        for day in config['weekdays']:
            try:
                avg = weekday_plots[station+'_'+day].iloc[weekday_plots[station+'_'+day].loc[:,'loadweigh.kg'].nonzero()].loc[:,'loadweigh.kg'].groupby(weekday_plots[station+'_'+day]['FiveMin']).mean()
                avg.plot( marker='x', linestyle='none', label=day)
            except KeyError:
                pass
        plt.ylim(0,6000)
        plt.grid()
        plt.xticks(np.arange(plots[station]['FiveMin'].min().astype(int)-1, 25))
        plt.ylabel('Loadweigh (kg)')
        plt.xlabel('Time of day (24h clock)')
        plt.title(station)
        plt.legend()
        if save == True:
            plt.savefig('C:\\Users\\lwb1u18\\Internship\Analytics Results\Plots\WeekdayPlots\\'+station+ '\\'+station+'.png')
        plt.show()            
#---------------------------------------------------------------------------------------------------------------------------

trainjournDf, vehjournDf, journeyDf = create_Dfs(filepath)


select_dates(vehjournDf, trainjournDf, config['startdate'], config['splitdate'])

plots={}
for station in config['stations']:
    plots[station] = trainjournDf.loc[trainjournDf['tiploc'] == station]
    if station == 'GTWK':
        plots['GTWK'].loc[:, 'northbound'] = plots['GTWK']['RouteSignature'].apply(get_dir)  
        plots['northbound'+station] = plots[station].loc[plots[station]['northbound']==True]
        plots['southbound'+station] = plots[station].loc[plots[station]['northbound']==False]
        del plots[station]
        
#plot_loadweigh(plots['VICTRIC'], 'London Victoria line', )   
#plot_loadweigh(plots['BRGHTN'], 'Brighton line', )    
#plot_loadweigh(plots['northboundGTWK'], 'Gatwick Northbound line',)    
#plot_loadweigh(plots['southboundGTWK'], 'Gatwick Southbound line',)
        

weekday_plots = {}
for station in plots:
    plots[station].loc[:, 'weekday'] = plots[station]['date'].dt.weekday_name
    for day in config['weekdays']:
        weekday_plots[station+'_'+day] = plots[station].loc[plots[station]['weekday'] == day]
        if weekday_plots[station+'_'+day].shape[0]==0:
            del weekday_plots[station+'_'+day]


create_weekday_plots()    
create_multiday_plots() 












    