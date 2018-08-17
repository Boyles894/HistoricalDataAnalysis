########################################################################################
#
# (c) J. A. Pritchard
# Module to handle datasets used for model calibration
#
#
########################################################################################

import os
from datetime import datetime
import numpy as np
import pandas as pd

#import prediction_client.CddbInterface as CddbInterface
#import prediction_client.LocationParameter as LocationParameter
import JourneyConstants


class DataSet:
##########################################################################################
#
# Class to hold initial dataframes for journey, vehicle and train data,
# and to build/process a calibration dataframe for model calibration
#
##########################################################################################
    def __init__(self,
                 diagnosticLog):
        
        self.diagnosticLog = diagnosticLog
        self.diagnosticLog.info('Initialising data set...', os.path.basename(__file__))
        #self.diagnosticLog.writeEntry(1, os.path.basename(__file__), 'Initialising data set...')

        self.journeyDf = None
        self.vehicleDf = None
        self.trainDf = None
        self.baseIndexList = None

        self.sampleVehiclePredictions = None
        self.sampleTrainPredictions = None

    def buildFromActiveDataSet(self,
                               dataSetSpecification,
                               activeDataSet,
                               locationParameterList):

        ####################################################################################
        #
        # Data set parameters
        #   - description, selected date, selected TOCs
        #
        ####################################################################################

        # Get lists of processed tiplocs and tocs for which predictions are made.
        # # Should always have at least 1 TOC in the configuration!!!
        tocsForWhichPredictionsMade = dataSetSpecification.get('selected_tocs')['tocs_for_prediction']

        # List of required metrics.
        requiredMetrics = dataSetSpecification['required_metrics']


        ####################################################################################
        #
        #   Set up journey parameters
        #
        ####################################################################################
        identifiers_cfg = dataSetSpecification.get('identifiers')
        journeyIdentifiers = identifiers_cfg.get('journey')

        try:
            parameters_cfg = dataSetSpecification.get('parametersConfig')
            journeyParams = parameters_cfg['journeyParams']
            timeSlots = parameters_cfg['timeSlots']
            latenessBands = parameters_cfg['latenessBands']
            timePeriods = parameters_cfg['timePeriods']
            timetableChanges = parameters_cfg['timetableChanges']
            timetableChanges = [datetime.strptime(x, '%d/%m/%Y') for x in timetableChanges]
            self.diagnosticLog.info('Dataset Parameters Acquired', os.path.basename(__file__))
        except Exception as ex:
            self.diagnosticLog.writeException(1, os.path.basename(__file__), ex)
            raise


        # YAML has an idiosyncrasy with times, so they are expected as strings in the format '%H:%M'
        # This section converts the values to times
        timeMask = '%H:%M'
        for period in timePeriods:
            time_range = timePeriods.get(period)
            for t in time_range:
                time_range[t] = datetime.strptime(time_range[t], timeMask).time()


        for key in activeDataSet.journeySet:
            jny = activeDataSet.journeySet[key]
            if jny.loadingPredictionsRequired(
                    tocsForWhichPredictionsMade) and jny.hasRequiredMetrics(requiredMetrics):
                try:
					#Code to remove single journey known to cause problems
                    if jny._uniqueJourneyId == '201807188761106':
                        pass
                    else:
                        journeyLegsDf, vehicleLegsDf = jny.getCalibrationDataFrames(journeyIdentifiers,                                                            journeyParams,
																					timeSlots,
																					timePeriods,
																					timetableChanges,
																					latenessBands,
																					locationParameterList,
																					activeDataSet)



                except Exception as ex:
                    self.diagnosticLog.writeException(1, os.path.basename(__file__), ex)
                    raise

                try:
                    if self.journeyDf is None:
                        self.journeyDf = journeyLegsDf.copy()
                    else:
                        self.journeyDf = self.journeyDf.append(journeyLegsDf)

                    if self.vehicleDf is None:
                        self.vehicleDf = vehicleLegsDf.copy()
                    else:
                        self.vehicleDf = self.vehicleDf.append(vehicleLegsDf)

                except Exception as ex:
                    raise

        self.diagnosticLog.info('Journey Data Successfully Gathered', os.path.basename(__file__))

        if (self.journeyDf is not None) and (self.vehicleDf is not None):
            self.processRawDataFrames(dataSetSpecification)

    # def buildFromCalibDatabase(self, dataSourceCfg):
    #     sourceDetails = dataSourceCfg.get('dataSource')
    #     dbName = sourceDetails['sourceName']
    #     dataSetId = sourceDetails['dataSetId']
    #
    #     dbSource = DatabaseSource(dbName, dataSetId, self.diagnosticLog)
    #     self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Database Initialised')
    #     self.journeyDf = dbSource.getDataFrame('journeyLegDf')
    #     self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Journey dataframe built (' + str(len(self.journeyDf)) + 'rows)')
    #     self.vehicleDf = dbSource.getDataFrame('vehicleLegDf')
    #     self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Vehicle dataframe built (' + str(len(self.vehicleDf)) + 'rows)')
    #
    #     self.processRawDataFrames()

    def processRawDataFrames(self, dataSetSpecification):
        self.baseIndexList = pd.Series(dataSetSpecification['indexColumns'])
        self.setIndexTypes(dataSetSpecification['indexColumns'])
        #self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Index Columns: ' + ','.join(self.indexes.tolist()))
        self.indexDataFrame(self.journeyDf, self.baseIndexList.tolist(), retainCols=True)
        self.indexDataFrame(self.vehicleDf, self.baseIndexList.tolist(), retainCols=False)
        #self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Dataframes indexed')



        missingDataValue = dataSetSpecification['missingDataValue']
        dropNullColumns = dataSetSpecification['dropNullColumns']

        self.clearMissingValues(missingDataValue,dropNullColumns)
        #self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Missing values set to NaN')
        self.setCategorialVariables(dataSetSpecification['categories'])
        self.setCovariates(dataSetSpecification['covariates'])
        #self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Category columns set')
        
        self.trainDf = pd.DataFrame(index=self.journeyDf.index).copy()
        #self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Train dataframe initialised')
        
        self.trainAggregation(dataSetSpecification['covariates'])
        #self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Train dataframe populated: ' + str(len(self.trainDf)) + ' rows')
        self.diagnosticLog.info('Dataframes Successfully Formatted', os.path.basename(__file__))

    def saveDataFramesToFile(self, filepath):

        #self.diagnosticLog.writeEntry(9, os.path.basename(__file__), 'Saving dataset to: ' + filepath)

        try:
            indexes = pd.Series(self.baseIndexList)
            indexes.to_hdf(filepath, 'indexes', format='table')
            self.resetIndexes(self.journeyDf)
            self.journeyDf.to_hdf(filepath, 'journeyDf',format='table')

            self.resetIndexes(self.vehicleDf)
            self.vehicleDf.to_hdf(filepath, 'vehicleDf',format='table')

            self.resetIndexes(self.trainDf)
            self.trainDf.to_hdf(filepath, 'trainDf',format='table')

            if self.sampleVehiclePredictions is not None:
                self.resetIndexes(self.sampleVehiclePredictions)
                self.sampleVehiclePredictions.to_hdf(filepath, 'sampleVehiclePredictionsDf', format='table')

            if self.sampleTrainPredictions is not None:
                self.resetIndexes(self.sampleTrainPredictions)
                self.sampleTrainPredictions.to_hdf(filepath,'sampleTrainPredictionsDf', format='table')

            self.diagnosticLog.info('Dataset saved: ' + filepath, os.path.basename(__file__), )

        except Exception as ex:
            self.diagnosticLog.writeException(1, 'Failed to save dataset', ex)
            raise


    def loadDataFramesFromFile(self, filepath):
        self.baseIndexList = pd.read_hdf(filepath, 'indexes').tolist()
        self.journeyDf = pd.read_hdf(filepath,'journeyDf')
        self.indexDataFrame(self.journeyDf, self.baseIndexList, retainCols=True)
        self.vehicleDf = pd.read_hdf(filepath,'vehicleDf')
        self.indexDataFrame(self.vehicleDf, self.baseIndexList, retainCols=False)
        try:
            self.trainDf = pd.read_hdf(filepath,'trainDf')
            self.indexDataFrame(self.trainDf, self.baseIndexList, retainCols=False)
        except:
            pass
        try:
            self.sampleVehiclePredictions = pd.read_hdf(filepath, 'sampleVehiclePredictionsDf')
            self.indexDataFrame(self.sampleVehiclePredictions, self.baseIndexList, retainCols=False)
        except:
            pass
        try:
            self.sampleTrainPredictions = pd.read_hdf(filepath,'sampleTrainPredictionsDf')
            self.indexDataFrame(self.sampleTrainPredictions,self.baseIndexList,retainCols = False)
        except:
            pass

        


    def indexDataFrame(self, df, indexColumns,retainCols = False):

        # Note that one of the leg indexes (TiplocIndex) is used in model calibration
        # and must therefore be retained as a separate column.  Hence for the journey
        # dataframe, the columns are not dropped
        indexColumns = list(set(indexColumns).intersection(df.columns.tolist()))

        if retainCols == True:
            df.set_index(indexColumns, drop=False, inplace=True)
        else:            
            df.set_index(indexColumns, drop=True, inplace=True)


            
    def resetIndexes(self, df):

        # This function is useful to avoid issues with MultiIndexes when saving dataframes/
        # In the case of the journey dataframe, the index columns were not dropped and need to
        # be processed accordingly
        for col in df.columns:
             if col in df.index.names:
                 df.drop(col,axis=1,inplace=True)
        df.reset_index(inplace=True)

    def setIndexTypes(self, indexCols):
        for col in indexCols:
            if col in self.journeyDf.columns:
                self.journeyDf[col] = self.journeyDf[col].astype('category')
            if col in self.vehicleDf.columns:
                self.vehicleDf[col] = self.vehicleDf[col].astype('category')
    
    def setCategorialVariables(self, categoriesList):
        for category in categoriesList:
            if category in self.journeyDf.columns:
                self.journeyDf[category] = self.journeyDf[category].astype('category')
            if category in self.vehicleDf.columns:
                self.vehicleDf[category] = self.vehicleDf[category].astype('category')

    def setCovariates(self, covariatesList):
        for covariate in covariatesList:
            if covariate in self.journeyDf.columns:
                self.journeyDf[covariate] = self.journeyDf[covariate].astype('float')
            if covariate in self.vehicleDf.columns:
                self.vehicleDf[covariate] = self.vehicleDf[covariate].astype('float')

    
    def trainAggregation(self,covariatesList):
        tempDf = pd.DataFrame(index=self.trainDf.index).copy()
        tempDf['adjustedFigure'] = False
        for covariate in covariatesList:
            if covariate in self.vehicleDf.columns.tolist():
                tempDf['aggregatedData'] = self.vehicleDf[covariate].groupby(self.vehicleDf.index, sort=False).sum()
                if JourneyConstants.NumberOfVehicles in self.journeyDf.columns:
                    tempDf['vehiclesWithData'] = self.vehicleDf[covariate].groupby(self.vehicleDf.index, sort=False).count()
                    tempDf['scaling'] = self.journeyDf[JourneyConstants.NumberOfVehicles] / tempDf['vehiclesWithData']
                    tempDf.loc[(tempDf['scaling'] > 1) & (tempDf['vehiclesWithData'] > 0), 'adjustedFigure'] = True
                    tempDf.loc[(tempDf['vehiclesWithData'] == 0), 'scaling'] = 1
                    tempDf['aggregatedData'] = tempDf['aggregatedData'] * tempDf['scaling']


                self.trainDf[covariate] = tempDf['aggregatedData'].copy()
                self.trainDf['adjustedFigure'] = tempDf['adjustedFigure'].copy()

        #Note: trainLegDf will now be reindexed because it has a
        # single index of tuples (JourneyUid, tiplocIndex) rather than a
        # multi-index.
        self.trainDf = self.trainDf.reindex(self.trainDf.index)
        #self.trainDf.dropna(inplace=True)


    def clearMissingValues(self, MissingDataValue, dropNullColumns):
        # Where metrics have missing data, this is represented by a set value (currently -1)
        # This function replaces instances of that value with NaN
        # Columns which are completely null are optionally dropped

        self.journeyDf.replace(MissingDataValue,np.NaN,inplace=True)
        self.vehicleDf.replace(MissingDataValue,np.NaN,inplace=True)
        if dropNullColumns is True:
            self.journeyDf.dropna(axis=1, how ='all',inplace=True)
            self.vehicleDf.dropna(axis=1, how = 'all',inplace=True)


    def processMissingData(self, df, column, method = 'drop'):
        if method == 'drop':
            if column in df.columns.tolist():
                df = self._dropNaNFromColumn(df,column)

        return df

    def processZeroData(self,df,column, method = 'drop'):
        if method == 'drop':
            if column in df.columns.tolist():
                non_zero_mask = df[column] != 0
                df = df[non_zero_mask]
        return df


    def _dropNaNFromColumn(self,df,column):
        tempDf = pd.DataFrame(index=df.index.copy())
        tempDf[column] = df[column]
        df.drop(column, axis=1, inplace=True)
        tempDf.dropna(axis=0, how='any', inplace=True)
        return df.join(tempDf,how='right')



    def prepareModelCalibrationData(self, modelSpec, modelVariables):

        # Calibration dataframe may be indexed differently (e.g. at a vehicle level, sequence is included)
        self.calibrationIndexList = self.baseIndexList

        # Basis for group-by operations
        self.grouping = ['RouteSignature','tiplocIndex','MatchedDepartureTime']


        try:
            if modelSpec['aggregation'] == 'train':
                calibrationData = self.journeyDf.join(self.trainDf, how='right')
            elif modelSpec['aggregation'] == 'vehicle':
                calibrationData = self.journeyDf.join(self.vehicleDf, how='right')
                self.calibrationIndexList.append('sequence')
                self.grouping.append('sequence')
                #calibrationData.set_index('sequence', append=True, inplace=True, drop = False)
        except Exception as ex:
            self.diagnosticLog.writeEntry(5, 'Combining dataframes',
                                          'Chosen aggregation unavailable')
            raise

        if 'dependent' in modelVariables:
            dependentCfg = modelVariables.get('dependent')
        else:
            print('Warning: No Dependent Variable')
            dependentCfg = {}


        if 'covariates' in modelVariables:
            covariatesCfg = modelVariables.get('covariates')
        else:
            covariatesCfg = {}

        if 'categories' in modelVariables:
            categoriesCfg = modelVariables.get('categories')
        else:
            categoriesCfg = {}

        dependentsList = self.getVariableList(dependentCfg)
        if len(dependentsList) > 1:
            print("Warning: Multiple dependent variables specified in config")
        covariatesList = self.getVariableList(covariatesCfg)
        categoriesList = self.getVariableList(categoriesCfg)

        missingValueStrategyList = []
        dependentMissingValueStrategies = self.getMissingValueStrategyList(dependentCfg)
        covariateMissingValueStrategies = self.getMissingValueStrategyList(covariatesCfg)
        missingValueStrategyList = dependentMissingValueStrategies + covariateMissingValueStrategies

        for variable in missingValueStrategyList:
            calibrationData = self.processMissingData(calibrationData, variable[0], method=variable[1])

        dependentZeroValueStrategies = self.getZeroValueStrategyList(dependentCfg)
        covariateZeroValueStrategies = self.getZeroValueStrategyList(covariatesCfg)
        zeroValueStrategyList = dependentZeroValueStrategies + covariateZeroValueStrategies

        for variable in zeroValueStrategyList:
            calibrationData = self.processZeroData(calibrationData,variable[0])

        variableFilterList = []
        variableFilterList = variableFilterList + self.getVariableFilterList(dependentCfg)
        variableFilterList = variableFilterList + self.getVariableFilterList(covariatesCfg)

        for variable in variableFilterList:
            if variable[0] in calibrationData.columns:
                self.applyFilters(calibrationData, variable[0], variable[1], variable[2])

        categoryBaseDict = self.getCategoryBaseDict(categoriesCfg)
        for category, base in categoryBaseDict.items():
            category_values = calibrationData[category].unique()
            print(category, base)
            if str(base) not in category_values.astype(str):
                print(base, category_values.astype(str))

                self.diagnosticLog.writeEntry(5, 'Initialising DataSet', 'Base value not present for ' + category)
                print('Warning: Base value (' + str(base) + ') not present for ' + category)

        categorySelectionDict = self.getCategorySelectionDict(categoriesCfg)
        for category, variables in categorySelectionDict.items():
            if category in calibrationData.columns:
                calibrationData = calibrationData[calibrationData[category].isin(variables)]
                if len(variables) == 1:
                    categoriesList.remove(category)

        # Set aside test data for each grouping
        #blocks = [data.sample(frac=0.2,random_state = 200) for _,data in calibrationData.groupby(grouping)]
        #self.testData = pd.concat(blocks)
        #self.calibrationData = calibrationData.drop(self.testData.index)
        try:
            self.resetIndexes(calibrationData)
            selectedRows = None
            for _,data in calibrationData.groupby(self.grouping):
                if selectedRows is None:
                    selectedRows = data.sample(frac=0.2,random_state=42).index
                else:
                    selectedRows = selectedRows.union(data.sample(frac=0.2,random_state=42).index)

            testData = calibrationData.loc[calibrationData.index[selectedRows]]
            calibrationData.drop(testData.index)

            self.indexDataFrame(testData,self.calibrationIndexList,True)
            self.indexDataFrame(calibrationData,self.calibrationIndexList, True)
        except Exception as ex:
            pass

        self.testData = testData
        self.calibrationData = calibrationData

        # # Calculate Averages for dependent variables:
        # self.averagesDf = calibrationData[self.grouping]
        # for dependent in dependentsList:
        #     colName = 'AVG_' +  dependent
        #     averages = calibrationData.groupby(self.grouping, sort=False)[dependent].transform('mean')
        #
        #     self.averagesDf[colName] = averages



        # Select appropriate columns
        try:
            selectedVariablesList = []
            selectedVariablesList = dependentsList + covariatesList + categoriesList
            calibrationData = calibrationData[selectedVariablesList]
            for category in categoriesList:
                calibrationData[category] = calibrationData[category].astype('category')

        except Exception as ex:
            self.diagnosticLog.writeEntry(5, 'Initialising DataSet', 'Some selected variables missing')
            raise

        self.calibrationData = self.dropConstants(calibrationData)

        #Take first value in dependents list (there should only be one specified in config file anyway)
        self.dependentName = dependentsList[0]
        self.covariatesList = covariatesList
        self.categoriesList = categoriesList
        self.categoriesDict = categoryBaseDict

        self.independentsList = selectedVariablesList


    def applyFilters(self, df, column, minValue, maxValue):
        if minValue is not None:
            # print('Filter Min')
            # print(len(df))
            df = df[df[column] >= minValue]
            # print(len(df))
        if maxValue is not None:
            # print('Filter Max')
            # print(len(df))
            df = df[df[column] <= maxValue]
            # print(len(df))

        return df;


    def dropConstants(self, df):
        for col in df:
            if len(df[col].unique()) == 1:
                del df[col]
        return df


    def getVariableList(self, variablesConfig):
        variablesList = list(variablesConfig.keys())
        return variablesList


    def getCategoryBaseDict(self, categoryConfig):
        categoryBaseDict = {}
        for variable, options in categoryConfig.items():
            if 'base' in options.keys():
                categoryBaseDict[variable] = options['base']
        return categoryBaseDict


    def getCategorySelectionDict(self, categoryConfig):
        categorySelectionDict = {}
        for variable, options in categoryConfig.items():
            if 'selection' in options.keys():
                categorySelectionDict[variable] = options['selection']
        return categorySelectionDict


    def getMissingValueStrategyList(self, variablesConfig):
        missingValueStrategyList = []
        for variable, options in variablesConfig.items():
            if 'missingDataStrategy' in options.keys():
                missingValueStrategyList.append([variable, options['missingDataStrategy']])
        return missingValueStrategyList

    def getZeroValueStrategyList(self, variablesConfig):
        zeroValueStrategyList = []
        for variable, options in variablesConfig.items():
            if 'zeroValueStrategy' in options.keys():
                zeroValueStrategyList.append([variable, options['zeroValueStrategy']])
        return zeroValueStrategyList


    def getVariableFilterList(self, variablesConfig):
        variableFilterList = []
        for variable, options in variablesConfig.items():
            if 'minValue' in options.keys():
                minValue = options['minValue']
            else:
                minValue = None
            if 'maxValue' in options.keys():
                maxValue = options['maxValue']
            else:
                maxValue = None
            variableFilterList.append([variable, minValue, maxValue])
        return variableFilterList

# class DatabaseSource:
#     ##########################################################################################
#     #
#     # Class containing functions to extract dataframes from calibration database
#     #
#     ##########################################################################################
#     def __init__(self,
#                  dbName,
#                  dataSetId,
#                  diagnosticLog):
#
#         self.dbName = dbName
#         self.dataSetId = dataSetId
#         self.diagnosticLog = diagnosticLog
#         self.sourceDb = self._setDatabaseInterface(dbName)
#
#     def getDataFrame(self,
#                      dataFrameName):
#
#         self.sourceDb.openDbConnection()
#         dataFrameId = self._getDataFrameId(dataFrameName)
#         dataFrame = self._buildFrameFromDatabase(dataFrameId)
#         self.sourceDb.closeDbConnection()
#
#         return dataFrame
#
#     def _getDataFrameId(self,
#                         dataFrameName):
#
#         try:
#             availableDataFrameTuples = self.sourceDb.getDataFrameInfo(self.dataSetId)
#
#         except Exception as ex:
#             self.sourceDb.closeDbConnection()
#             self.diagnosticLog.writeEntry(5, 'Finding available dataframes',
#                                      'Failed to find available dataframes')
#             raise
#
#
#         try:
#             dataFrameId = -1
#             for tuple in availableDataFrameTuples:
#                 if tuple[2] == dataFrameName:
#                     dataFrameId = tuple[1]
#                     break
#
#             if dataFrameId == -1:
#                 raise ValueError
#             else:
#                 return dataFrameId
#
#
#         except (ValueError, Exception) as ex:
#             self.diagnosticLog.writeEntry(5, 'Building dataframe', 'Selected dataframe not found in database')
#             raise
#
#
#
#
#     # Function to build dataframe from database
#
#
#     def _buildFrameFromDatabase(self,dataFrameId):
#
#         # List of parameter names to be used for pandas data frame neaders.
#         parameterHeaders = list()
#         # Dictionary of column types.
#         parameterTypes = dict()
#         # Dictionary of parameter scopes.
#         parameterScope = {}
#
#         # Get the frame header information.
#         headerTuples = self.sourceDb.getDataFrameHeaders(self.dataSetId, dataFrameId)
#         self.diagnosticLog.writeEntry(9, os.path.basename(__file__), str(len(headerTuples)) + ' headers received for dataframe ' + str(dataFrameId))
#         for tuple in headerTuples:
#             parameterHeaders.append(tuple['header'].strip())
#             parameterTypes.update({tuple['col']: tuple['datatype'].strip()})
#             #Early datasets did not have scope defined
#             if tuple['scope'] is not None:
#                 parameterScope.update({tuple['header'].strip(): tuple['scope'].strip()})
#
#         # List of parameter data lists, on for each journey leg/vehicle.
#         parameterDataRows = list()
#         parameterDataRow = None
#         currentRow = -1
#         dataTuples = self.sourceDb.getDataFrameData(self.dataSetId, dataFrameId)
#
#         for dataTuple in dataTuples:
#             row = int(dataTuple['row'])
#             if row != currentRow:
#                 currentRow = row
#                 # If previous row exits, append it to parameterDataRows list
#                 if parameterDataRow != None:
#                     parameterDataRows.append(parameterDataRow)
#                 parameterDataRow = list()
#
#             dataType = parameterTypes[dataTuple['col']]
#             if dataType == 'str':
#                 parameterDataRow.append(dataTuple['data'].strip())
#             elif dataType == 'bool_':
#                 if dataTuple['data'].strip() == 'true':
#                     parameterDataRow.append(True)
#                 elif dataTuple['data'].strip() == 'false':
#                     parameterDataRow.append(False)
#                 else:
#                     parameterDataRow.append(-1)
#             elif dataType == 'int64':
#                 parameterDataRow.append(int(dataTuple['data']))
#             elif dataType == 'float64':
#                 parameterDataRow.append(float(dataTuple['data']))
#             else:
#                 raise ValueError('Unsupported Type')
#
#         # If final data row is not null, append it to parameterDataRows
#         if parameterDataRow != None:
#             parameterDataRows.append(parameterDataRow)
#
#
#         return pd.DataFrame.from_records(parameterDataRows, columns=parameterHeaders)
#
#
#
#
#
#     def _setDatabaseInterface(self, dbName):
#
#         self.diagnosticLog.writeEntry(5, os.path.basename(__file__),
#                                  'Selected source database: ' + dbName)
#
#         # Open connection to modelCalibration database to read dataframe data.
#         calib_db_cfg_file = os.path.normpath('./config/db/' + dbName + '.xml')
#         self.diagnosticLog.writeEntry(5, os.path.basename(__file__), 'Database connection settings will be loaded from: ' + calib_db_cfg_file)
#         calDb = CddbInterface.CalibDbInterface(calib_db_cfg_file, 'modelCalibrationConnection', self.diagnosticLog)
#         self.diagnosticLog.writeEntry(5, os.path.basename(__file__), 'Database interface initialised')
#         return calDb
#
#
