# Calculate Averages for dependent variables:
        self.averagesDf = calibrationData[journeyLegKey].to_frame()
        for dependent in dependentsList:
            if modelParameters['aggregation'] == 'train':
                grouping = journeyLegKey
            else:
                grouping = [journeyLegKey,'sequence']

            colName = 'AVG_' +  dependent
            averages = calibrationData.groupby(grouping, sort=False)[dependent].transform('mean')

            self.averagesDf[colName] = averages