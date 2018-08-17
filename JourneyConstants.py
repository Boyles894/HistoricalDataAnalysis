# -*- coding: utf-8 -*-
########################################################################################
#
# © Govia Thameslink Railway 2017
#
# Constant definitions for the various journey fields.
#
########################################################################################


# Metric names
ForecastLoadMetricName = 'load.forecast'
ForecastLoadPercentMetricName = 'load.forecast.percent'
PredictedLoadMetricName = 'load.predicted'
PredictedLoadPercentMetricName = 'load.predicted.percent' # CACI mix up forecasts and precictions!
EstimatedLoadMetricName = 'load.actual.derived'
LocPredictedLoadMetricName = 'location.predicted'
LocEstimatedLoadMetricName = 'location.actual.derived'

LoadWeighMetricName = 'loadweigh.kg'
GatelineMetricName = 'gateline.transaction'
ShoeCountPeopleMetricName = 'shoecount.people'
ShoeCountMaleMetric = 'shoecount.male'
ShoeCountRightMetric = 'shoecount.right'
CommuterhiveMetric   = 'commuterhive.interaction'


# Journey message field names
Rid = 'rid'
Uid = 'uid'
RunsOnDate = 'runsOn'
TocId = 'tocId'
TrainId = 'trainId'
UniqueJourneyId = 'uniqueJourneyId'

Locations = 'locations'
LocationTiploc = 'tiploc'
LocationTiplocIndex = 'tiplocIndex'
LocationTiplocSuffix = 'tiplocSuffix'
LocationCancelled = 'cancelled'
LocationCancelledTrueValue = 'T'
LocationPlannedGbttDeparture = 'plannedGbttDeparture'
LocationPlannedWttDeparture = 'plannedWttDeparture'
LocationActualDeparture = 'actualDeparture'
LocationPlannedGbttArrival = 'plannedGbttArrival'
LocationPlannedWttArrival = 'plannedWttArrival'
LocationActualArrival = 'actualArrival'
LocationPlannedPlatform = 'plannedPlatform'
LocationActualPlatform = 'actualPlatform'

Units = 'units'

Vehicles = 'vehicles'
VehicleSequence = 'sequence'
VehiclePaintedNumber = 'vehiclePaintedNumber'

Metrics = 'metrics'        

TotalSeats = 'seats'
MaxStandees = 'standing'

MissingMetricValue = -1.0
#Number of carriages in each unit.
#Currently fixed for GatEx 387/2.  May be better set in a config file
UnitLength = 4

# Fields derived from Journey message fields
UniqueJourneyId = 'UniqueJourneyId'
RouteSignature = 'RouteSignature'
PlannedRouteSignature = 'PlannedRouteSignature'
JourneySignature = 'JourneySignature'
JourneyLegKey = 'JourneyLegKey'
ServicePartCancelled = 'ServicePartCancelled'
DepartureTime = 'DepartureTime'
HourOfDay = 'HourOfDay'
DayOfWeek = 'DayOfWeek'
WeekOfYear = 'WeekOfYear'
HasArrived = 'HasArrived'
HasDeparted = 'HasDeparted'
RouteTimeBand = 'RouteTimeBand'
NumberOfVehicles = 'NumberOfVehicles'
LatenessBand = 'LB'
TimetableBand = 'TimetableBand'
PSDI = 'PSDI'
BankHoliday = 'BankHoliday'
Schoolholiday = 'SchoolHoliday'
MatchedScheduleTime = 'MatchedScheduleTime'
MatchedDepartureTime = 'MatchedDepartureTime'

# External event fields.
ExternalEvent = 'ExternalEvent'

# Timestamp formats.
JourneyMsgTimestampFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
LocationMsgTimestampFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
