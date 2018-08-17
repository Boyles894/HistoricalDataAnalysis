import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import yaml
import General_Functions as gen
import DiagnosticLog

pd.options.mode.chained_assignment = None

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))

filepath = os.path.normpath(config['datafilepath'] + config['datafilename'])

def plot_loadweigh(Df, plot_name, save=False):
    avg = Df.iloc[Df.loc[:,'loadweigh.kg'].nonzero()].loc[:,'loadweigh.kg'].groupby(Df['FiveMin']).mean()
    std = Df.iloc[Df.loc[:,'loadweigh.kg'].nonzero()].loc[:,'loadweigh.kg'].groupby(Df['FiveMin']).std()
    plt.errorbar(avg.index, avg.iloc[avg.nonzero()], yerr=std, linestyle='none',  marker='o', color='black', markersize=4, elinewidth=1, ecolor='dimgrey' )
    plt.plot(Df['FiveMin'], Df['loadweigh.kg'], linestyle='none', marker='x', markersize=0.7, color='red') 
    plt.grid()
    plt.ylim(0,avg.max()+(avg.max()/4))
    plt.xticks(np.arange(Df['FiveMin'].min().astype(int)-1, 25))
    plt.ylabel('Loadweigh (kg)')
    plt.xlabel('Time of day (24h clock)')
    plt.title(plot_name)
    if save==True:
        plt.savefig('C:\\Users\\lwb1u18\\Internship\Analytics Results\Plots\ '+plot_name+'.png')
        logging.writeEntry(5, 'Loadweigh plot Saved', 'C:\\Users\\lwb1u18\\Internship\Analytics Results\Plots\ '+plot_name+'.png')
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
                    logging.writeEntry(5, 'Weekday plot Saved', 'C:\\Users\\lwb1u18\\Internship\Analytics Results\Plots\WeekdayPlots\\'+station+ '\ '+station+' on a '+day+'.png') 
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
            logging.writeEntry(5, 'Multiday plot Saved', 'C:\\Users\\lwb1u18\\Internship\Analytics Results\Plots\WeekdayPlots\\'+station+ '\\'+station+'.png' )
        plt.show()            
#---------------------------------------------------------------------------------------------------------------------------
logging = DiagnosticLog.buildDiagnosticLog(config)

trainjournDf, vehjournDf = gen.build_frames_from_file(filepath)
logging.writeEntry(7, 'Created Dataframes', 'Vehicle and Journey Dataframes Created')

plots={}
for station in config['stations']:
    plots[station] = trainjournDf.loc[trainjournDf['tiploc'] == station]
    if station == 'GTWK':
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














    