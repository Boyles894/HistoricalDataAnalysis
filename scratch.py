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

dataframes = {}
trainjournDf, vehjournDf = gen.build_frames_from_file(datafile)

bank = {}
bank['train'] = trainjournDf.loc[trainjournDf['BankHoliday']==True]
bank['veh'] = vehjournDf.loc[vehjournDf['BankHoliday']==True]

school = {}
school['train'] = trainjournDf.loc[trainjournDf['SchoolHoliday']==True]
school['veh'] = vehjournDf.loc[vehjournDf['SchoolHoliday']==True]