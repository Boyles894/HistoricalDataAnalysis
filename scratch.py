# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 09:56:23 2018

@author: lwb1u18
"""
import pandas as pd
import numpy as np
import datetime
import os
import yaml
import General_Functions as gen
import holidays

config_file = os.path.normpath('./config.yml')
config = yaml.load(open(config_file, 'r'))
datafile = config['datafilepath']+config['datafilename']

trainjournDf, vehjournDf = gen.build_frames_from_file(datafile)

trainjournDf.to_csv('../../Tableau/datafiles/trainjournDF_match2.csv')
vehjournDf.to_csv('../../Tableau/datafiles/vehjournDF_match2.csv')

a = trainjournDf.loc[trainjournDf['TimetableBand'] == 6]
b = trainjournDf.loc[trainjournDf['TimetableBand'] == 7]