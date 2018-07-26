import pandas as pd
import numpy as np
import datetime
import os
import yaml
import General_Functions as gen

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))
datafile = os.path.normpath(config['datafilepath'] + config['datafilename'])


trainjournDf, vehjournDf = gen.build_frames_from_file(datafile)


#journeyIDs = data_set.journeyDf
f = lambda x: x in [0,1,2,3,4]
trainjournDf['WeekDay'] = trainjournDf['DayOfWeek'].apply(f)
Aggregation = ['RouteSignature','tiplocIndex','WeekDay','FiveMin']
trainjournDf['Grouping'] = trainjournDf[Aggregation].apply(tuple,axis=1)

a = trainjournDf.groupby(by=['Grouping'])
count = a['loadweigh.kg'].count().rename('count')
mean = a['loadweigh.kg'].mean().rename('mean')
stddev = a['loadweigh.kg'].std().rename('stddev')
median = a['loadweigh.kg'].median().rename('median')

b = pd.concat([count,mean,median,stddev],axis=1)
c = b[b['count']>10]

eight = vehjournDf.loc[vehjournDf['NumberOfVehicles']==8]
four = vehjournDf.loc[vehjournDf['NumberOfVehicles']==4]
date = trainjournDf.loc[trainjournDf['date'] == max(trainjournDf['date'])]