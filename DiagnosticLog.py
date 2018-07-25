# -*- coding: utf-8 -*-
########################################################################################
#
# © Govia Thameslink Railway 2017
#
# Class providing thread safe logging.
# A new file is started when the log exceeds a threshold size to prevent it from getting
# too large to read conveniently.
#
# Instance Constructor Parameters:
# ===============================
#  filepath
#    Basic path for file. The actual log file name will be basic path name plus a 
#    timestamp.
#
#  maxLoggedVerbosity
#    In order to control the amount of data logged a maximum logging level is set when
#    the class is instantiated and only messages with a logging level less than or equal 
#    to this level are actually written to the log.
#
#      The verbosity level convention adopted is as follows:
#      0 - None
#         Program runs faster but no logging is produced.
#
#      3 - Minimal
#         Fatal exceptions and failures of push port connection are logged.
#
#      6 - High
#        Incomming and outgoing messages along with important intermediate  
#        results are logged.
#
#      9 - Verbose
#        Full trace of function calls recorded. 
#
#
#  maxFileLength
#    The approximate maximum length in bytes that the log file can grow to before a
#    new log file is created for subsequent entries. 
#
#
# Public Methods:
# ==============
#  writeEntry(verbosity, context, entry)
#    Writes an entry to the log provided that the entry verbosity level is less than or
#    equal to the maximum logging level set when the log was created. The context is a
#    short string identifying the circumstances of the entry and the entry is a longer
#    string providing the information to be logged.
#
#  writeException(verbosity, context, ex):
#    Writes exception information to the log provided that the entry verbosity level is 
#    less than or equal to the maximum logging level set when the log was created. The 
#    context is a short string identifying the circumstances in which the exception was 
#    raised.
#
########################################################################################
import inspect
import os
import threading
import datetime
import time
import traceback

from datetime import datetime

#Global logging
#verbosity levels set to make it easier to trace logging in an IDE
#
#Logging Levels (descriptions now in line with python logging levels)
critical = 1
error = 3
warning = 5
info = 7
debug = 9
verbose = 9




# Class to handle common functions (e.g. file handling) for all log types
class BaseLog(object):

    #
    # Instance constructor.
    def __init__(self, path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput = False):
        super().__init__()
        self._path = path
        self.baseFileName = filename
        self._filepath = os.path.join(path, filename)
        self._timeStampedFilepath = os.path.normpath(self._buildTimeStampedFilename())
        self._maxLoggedVerbosity = maxLoggedVerbosity
        self.maxFileLength = maxFileLength
        self.retentionDays = retentionDays
        self.threadLock = threading.Lock()

        self.logMessageCount = 0
        self.consoleOutput = consoleOutput


    #
    # Helper method to build a time stamped filename to allow for slicing of the
    # log tp prervent it becomming too big to read conveniently.
    def _buildTimeStampedFilename(self):
        return self._filepath + '_' + datetime.utcnow().strftime('%Y_%m_%d__%H_%M_%S') + '.log'

    #
    # Helper method to slice the log into seperate files when it is becomming too large
    # to read conveniently.
    def _sliceFile(self):
        try:
            if os.path.isfile(self._timeStampedFilepath) == True:
                statinfo = os.stat(self._timeStampedFilepath)
                if statinfo.st_size >= self.maxFileLength:
                    self._timeStampedFilepath = self._buildTimeStampedFilename()

        except Exception as ex:
            # Don't want to bring the system down just because logging
            # has failed!
            pass

    #
    # Helper method to delete older log files.
    def deleteOldLogFiles(self):
        try:
            now = datetime.datetime.now()

            for fileName in os.listdir(self._path):
                if not os.path.isdir(fileName):
                    fullPathName = os.path.join(self._path, fileName)
                    createTime = datetime.datetime.fromtimestamp(os.path.getctime(fullPathName))
                    daysOld = (now - createTime).days

                    if daysOld > self.retentionDays:
                        os.remove(fullPathName)

        except:
            pass  # Failure should not stop program!
     


    #
    # Method to write text to a file.
    def _writeEntry(self, text):
            lockAquired = False
            f = None
            fileOpen = False

            try:
                self.threadLock.acquire()
                lockAquired = True

                # Start a new file if the log has got too large to read conveniently.
                self._sliceFile()
 
                # Periodically remove old log files
                if self.logMessageCount % 100 == 0:
                    self.deleteOldLogFiles()
 
                f = open(self._timeStampedFilepath, 'a')
                fileOpen = True
                f.write('%s\n' % (text))

                if self.consoleOutput is True:
                    print(text)

            except Exception:
                # Don't want to bring the system down just because logging 
                # has failed!
                pass
                
 
            finally:
            # Ensure that log is closed and thread lock released.
                if fileOpen == True:
                    f.close()
                if lockAquired == True:
                    self.threadLock.release()
 




class DiagnosticLog(BaseLog):
    #
    # Instance constructor.
    def __init__(self, path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput=False):
        super().__init__(path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput)



    #
    # Functions to replicate python's standard logging syntax
    def debug(self,message,context = 'Log'):
        self.writeEntry(debug,context,message)

    def info(self,message,context = 'Log'):
        self.writeEntry(info,context,message)

    def warning(self,message,context = 'Log'):
        self.writeEntry(warning,context, message)

    def error(self,message,context = 'Log'):
        self.writeEntry(error,context, message)

    def critical(self,message,context = 'Log'):
        self.writeEntry(critical,context, message)


    #
    # Method to log a standard event.  
    def writeEntry(self, verbosity, context, entry, writeTrace = 0):

        if verbosity <= self._maxLoggedVerbosity:

            # Increment the message count
            self.logMessageCount += 1

            if verbosity == critical:
                msgLevel = 'CRITICAL'
            elif verbosity == error:
                msgLevel = 'ERROR'
            elif verbosity == warning:
                msgLevel = 'WARNING'
            elif verbosity == info:
                msgLevel = 'INFO'
            elif verbosity == debug:
                msgLevel = 'DEBUG'
            else:
                msgLevel = ''

            msgTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            callingTrace = ''

            logMessage = '%d \t %s \t %s \t %s \t %s \t %s' % (self.logMessageCount, msgTime, msgLevel, entry, context, callingTrace)
            self._writeEntry(logMessage)


    #
    # Method to log an exception.  
    def writeException(self, verbosity, context, ex):
        if verbosity <= self._maxLoggedVerbosity:
            lockAquired = False
            f = None
            fileOpen = False

            try:
                self.threadLock.acquire() 
                lockAquired = True

                # Start a new file if the log has got too large to read conveniently.
                self._sliceFile()

                f = open(self._timeStampedFilepath, 'a')
                fileOpen = True
                f.write('Exception: %s: %s:\n' % (context, time.ctime(time.time())))
                traceback.print_exc(file=f)
                f.write('\n\n')

                if self.consoleOutput is True:
                    print('Exception: ' + context)

            except Exception:
                # Don't want to bring the system down just because logging 
                # has failed!
                pass
                 
            finally:
                # Ensure that log is closed and thread lock released.
                if fileOpen == True:
                    f.close()
                if lockAquired == True:
                    self.threadLock.release()
 

class MessageLog(BaseLog):
    #
    # Instance constructor.
    def __init__(self, path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput=False):
        super().__init__(path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput)
        self.receivedMessageCount = 0
        self.sentMessageCount = 0

    def writeMessage(self,message,inbound = True):
        self.receivedMessageCount += 1



########################################################################################
#
# Utility method to build diagnostic log from an appropriate YAML
# configuration.
#
########################################################################################
def buildDiagnosticLog(config):

    # Get the logging configuration and set up the diagnostic log.
    try:
        diagnosticCfg = config.get('logging')
        return DiagnosticLog(diagnosticCfg['path'],
                             diagnosticCfg['filename'],
                             int(diagnosticCfg['maxLoggedVerbosity']),
                             int(diagnosticCfg['maxFileLength']),
                             int(diagnosticCfg['retentionDays']),
                             diagnosticCfg['consoleOutput'])
    except:
        print('Failed to start diagnostic logging')


# New functions to build separate logs to consume messages from the queues.
def buildJourneyMessageLog(config):
    try:
        journeyMsgLogConfig = config.get('journeyMessageLog')
        return MessageLog(journeyMsgLogConfig['path'],
                          journeyMsgLogConfig['filename'],
                          journeyMsgLogConfig['maxLoggedVerbosity'],
                          journeyMsgLogConfig['maxFileLength'],
                          journeyMsgLogConfig['retentionDays'],
                          journeyMsgLogConfig['consoleOutput'])
    except:
        print('Failed to start journey message logging')

def buildLocationMessageLog(config):
    try:
        locationMsgLogConfig = config.get('locationMessageLog')
        return MessageLog(locationMsgLogConfig['path'],
                          locationMsgLogConfig['filename'],
                          locationMsgLogConfig['maxLoggedVerbosity'],
                          locationMsgLogConfig['maxFileLength'],
                          locationMsgLogConfig['retentionDays'],
                          locationMsgLogConfig['consoleOutput'])
    except:
        print('Failed to start location message logging')

 
'''

class BaseLog(object):
    # Class to handle common functions (e.g. file handling) for all log types

    #
    # Instance constructor.
    def __init__(self, path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput = False):
        super().__init__()
        self._path = path
        self.baseFileName = filename
        self._filepath = os.path.join(path, filename)
        self._timeStampedFilepath = os.path.normpath(self._buildTimeStampedFilename())
        self._maxLoggedVerbosity = maxLoggedVerbosity
        self.maxFileLength = maxFileLength
        self.retentionDays = retentionDays
        self.threadLock = threading.Lock()
        self.lockAcquired = False
        self.fileOpen = False

        self.logMessageCount = 0
        self.consoleOutput = consoleOutput




    def _getFileHandler(self):
        f = None

        self.threadLock.acquire()
        self.lockAquired = True

        # Start a new file if the log has got too large to read conveniently.
        self._sliceFile()

        f = open(self._timeStampedFilepath, 'a')
        self.fileOpen = True

        return f;


    def _closeFileHandler(self,f):
        # Ensure that log is closed and thread lock released.
        if self.fileOpen == True:
            f.close()
            self.fileOpen = False
        if self.lockAquired == True:
            self.threadLock.release()
            self.lockAcquired = False

    #
    # Helper method to build a time stamped filename to allow for slicing of the
    # log tp prervent it becomming too big to read conveniently.
    def _buildTimeStampedFilename(self):
        return self._filepath + '_' + datetime.utcnow().strftime('%Y_%m_%d__%H_%M_%S') + '.log'

    #
    # Helper method to slice the log into seperate files when it is becomming too large
    # to read conveniently.
    def _sliceFile(self):
        try:
            if os.path.isfile(self._timeStampedFilepath) == True:
                statinfo = os.stat(self._timeStampedFilepath)
                if statinfo.st_size >= self.maxFileLength:
                    self._timeStampedFilepath = self._buildTimeStampedFilename()

        except Exception as ex:
            # Don't want to bring the system down just because logging
            # has failed!
            pass

    def deleteOldLogFiles(self):
        try:
            now = datetime.datetime.now()

            for fileName in os.listdir(self._path):
                if not os.path.isdir(fileName):
                    fullPathName = os.path.join(self._path, fileName)
                    createTime = datetime.datetime.fromtimestamp(os.path.getctime(fullPathName))
                    daysOld = (now - createTime).days

                    if daysOld > self.retentionDays:
                        os.remove(fullPathName)

        except:
            pass  # Failure should not stop program!

class DiagnosticLog(BaseLog):
    #
    # Instance constructor.
    def __init__(self, path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput=False):
        super().__init__(path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput)


    def getTraceMessage(self,n):
        #Function to read information from the stack about the nth previous function call
        traceMessage = None
        try:
            stackElement = inspect.stack()[n]
            functionName = stackElement[3]
            moduleName = stackElement[1].split("/")[-1]
            lineNumber = stackElement[2]

            traceMessage = '[%s:%s:%d]' % (moduleName, functionName, lineNumber)

        except:

            traceMessage = '[]'

        return traceMessage

    #
    # Functions to replicate python's standard logging syntax
    def debug(self,message,context = 'Log'):
        self.writeEntry(debug,context,message)

    def info(self,message,context = 'Log'):
        self.writeEntry(info,context,message)

    def warning(self,message,context = 'Log'):
        self.writeEntry(warning,context, message)

    def error(self,message,context = 'Log'):
        self.writeEntry(error,context, message)

    def critical(self,message,context = 'Log'):
        self.writeEntry(critical,context, message)


    #
    # Method to log a standard event.  
    def writeEntry(self, verbosity, context, entry, writeTrace = 0):

        if verbosity <= self._maxLoggedVerbosity:

            self.logMessageCount += 1

            # Periodically remove old log files
            if self.logMessageCount % 10 == 0:
                self.deleteOldLogFiles()
                
            f = None
            try:
                f = self._getFileHandler()

                msgCount = self.logMessageCount

                if verbosity == critical:
                    msgLevel = 'CRITICAL'
                elif verbosity == error:
                    msgLevel = 'ERROR'
                elif verbosity == warning:
                    msgLevel = 'WARNING'
                elif verbosity == info:
                    msgLevel = 'INFO'
                elif verbosity == debug:
                    msgLevel = 'DEBUG'
                else:
                    msgLevel = ''

                if context == 'Log' and verbosity <= critical:
                    #If this has been called via one of the new functions to match python's standard logging,
                    #the actual calling function is one element further down the trace
                    stackContext = 3
                    stackCallingFunction = 4

                    contextMessage = self.getTraceMessage(stackContext)
                    callingTrace = self.getTraceMessage(stackCallingFunction)
                else:
                    contextMessage = context
                    callingTrace = ''
                    #stackContext = 2
                    #stackCallingFunction = 3



                msgTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                logMessage = '%d \t %s \t %s \t %s \t %s \t %s\n' % (msgCount, msgTime, msgLevel, entry, contextMessage, callingTrace)
                #logMessage = 'Log Entry %d: %s: %s:\n%s\n%s\n\n' \
                #             % (self.logMessageCount, context, time.ctime(time.time()), entry, traceMessages)
                f.write(logMessage)

                if self.consoleOutput is True:
                    print(logMessage)

            except Exception:
                # Don't want to bring the system down just because logging 
                # has failed!
                pass
                
 
            finally:
                # Ensure that log is closed and thread lock released.
                self._closeFileHandler(f)

    #
    # Method to log an exception.  
    def writeException(self, verbosity, context, ex):
        filename = None
        line = None
        function_trace = None
        try:
            filename = inspect.stack()[1][1]
            line = inspect.stack()[1][2]
            function_trace = []
            for i in range(1,5):
                function_trace.append(inspect.stack()[i][3])
        except:
            filename = 'unknown'
            line = 0
            function_trace = []

        if verbosity <= self._maxLoggedVerbosity:
            f = None
            try:
                f = self._getFileHandler()
                self.logMessageCount += 1
                f.write('Log Message %d:\n' % self.logMessageCount)
                f.write('Exception: %s: %s:\n' % (context, time.ctime(time.time())))
                f.write('Caught in file %s at line %d\n' % (filename, line))
                f.write('Function trace: %s\n' % function_trace)
                f.write(str(ex))
                traceback.print_exc(file=f)
                f.write('\n\n')

                if self.consoleOutput is True:
                    print('Exception: ' + context)

            except Exception:
                # Don't want to bring the system down just because logging
                # has failed!
                pass

            finally:
                # Ensure that log is closed and thread lock released.
                self._closeFileHandler(f)

class MessageLog(BaseLog):
    #
    # Instance constructor.
    def __init__(self, path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput=False):
        super().__init__(path, filename, maxLoggedVerbosity, maxFileLength, retentionDays, consoleOutput)
        self.receivedMessageCount = 0
        self.sentMessageCount = 0

    def writeMessage(self,message,inbound = True):
        self.receivedMessageCount += 1

        #Periodically remove old log files
        if self.receivedMessageCount % 1000 == 0:
            self.deleteOldLogFiles()

        f = None
        try:
            f = self._getFileHandler()
            msgTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            if inbound == True:
                msgCount = self.receivedMessageCount
                logMessage = 'Message %d received at %s:\n %s\n\n' % (msgCount, msgTime, message)
            else:
                self.sentMessageCount +=1
                msgCount = self.sentMessageCount
                logMessage = 'Message %d sent at %s:\n %s\n\n' % (msgCount, msgTime, message)

            f.write(logMessage)

            if self.consoleOutput is True:
                print(logMessage)

        except Exception:
            # Don't want to bring the system down just because logging
            # has failed!
            pass


        finally:
            # Ensure that log is closed and thread lock released.
            self._closeFileHandler(f)



########################################################################################
#
# Utility method to build diagnostic log from an appropriate YAML
# configuration.
#
########################################################################################
def buildDiagnosticLog(config):

    # Get the logging configuration and set up the diagnostic log.
    try:
        diagnosticCfg = config.get('logging')
        return DiagnosticLog(diagnosticCfg['path'],
                             diagnosticCfg['filename'],
                             int(diagnosticCfg['maxLoggedVerbosity']),
                             int(diagnosticCfg['maxFileLength']),
                             int(diagnosticCfg['retentionDays']),
                             diagnosticCfg['consoleOutput'])
    except:
        print('Failed to start diagnostic logging')


# New functions to build separate logs to consume messages from the queues.
def buildJourneyMessageLog(config):
    try:
        journeyMsgLogConfig = config.get('journeyMessageLog')
        return MessageLog(journeyMsgLogConfig['path'],
                          journeyMsgLogConfig['filename'],
                          journeyMsgLogConfig['maxLoggedVerbosity'],
                          journeyMsgLogConfig['maxFileLength'],
                          journeyMsgLogConfig['retentionDays'],
                          journeyMsgLogConfig['consoleOutput'])
    except:
        print('Failed to start journey message logging')

def buildLocationMessageLog(config):
    try:
        locationMsgLogConfig = config.get('locationMessageLog')
        return MessageLog(locationMsgLogConfig['path'],
                          locationMsgLogConfig['filename'],
                          locationMsgLogConfig['maxLoggedVerbosity'],
                          locationMsgLogConfig['maxFileLength'],
                          locationMsgLogConfig['retentionDays'],
                          locationMsgLogConfig['consoleOutput'])
    except:
        print('Failed to start location message logging')

'''