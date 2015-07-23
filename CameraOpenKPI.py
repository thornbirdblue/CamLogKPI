##########################################################################
#	CopyRight	(C)	VIVO,2020	All Rights Reserved!
#
#	Module:		!!!In one adb_log exec!!! Scan camera open log and calc open time
#
#	File:		CameraOpenKPI.py
#
#	Author:		liuchangjian
#
#	Data:		2015-07-23
#
#	E-mail:		liuchangjian@vivo.com.cn
#
###########################################################################

###########################################################################
#
#	History:
#	Name		Data		Ver		Act
#--------------------------------------------------------------------------
#	liuchangjian	2015-07-23	v1.0		create
#
###########################################################################

#!/bin/python
import sys,os,re,string

# app log pattern
appLogType = r'app_log_'

# save log record
logs = []

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

class AppLogType:
	'adb log dir info'
	logCnt = 0
	
	def __init__(self,name):
		self.dirname = name
		AppLogType.logCnt+=1

	def ScanCameraLog(self,file):
		if debugLog >= debugLogLevel[2]:
			print "Parse file: "+file
		
# Only exec in one adb_log directory!!! Can't have two adb_log dir
def ScanFiles(arg,dirname,files):
	if debugLog >= debugLogLevel[-1]:
		print dirname

	for file in files:
		logType = re.compile(appLogType)

		if debugLog >= debugLogLevel[-1]:
			print appLogType
			print file
		
		m = re.match(logType,file)
		if m:
			path,name = os.path.split(dirname)

			if debugLog >= debugLogLevel[2]:
				print "Found file: "+name
			
			log = AppLogType(name)
			logs.append(log)
			log.ScanCameraLog(name)

def ParseArgv():
	if len(sys.argv) > appParaNum+1:
		CameraOpenKPIHelp()
		sys.exit()
	else:
		for i in range(1,len(sys.argv)):
			if sys.argv[i] == '-h':
				CameraOpenKPIHelp()
				sys.exit()
			elif sys.argv[i] == '-d':
				if sys.argv[i+1]:
					debug = string.atoi(sys.argv[i+1],10)
					if type(debug) == int:
						global debugLog
						debugLog = debug						
						print "Log level is: "+str(debugLog)
					else:
						print "cmd para ERROR: "+sys.argv[i+1]+" is not int num!!!"
				else:
					CameraOpenKPIHelp()
					sys.exit()

def CameraOpenKPIHelp():
	print 'Command Format :'
	print '		CameraOpenKPI [-d 0/1/2] | [-h]'

appParaNum = 2

if __name__ == '__main__':
	ParseArgv()
	print 'Local DIR: '+os.getcwd()+'\n'
	os.path.walk(os.getcwd(),ScanFiles,())
	print '\n\nTotal Parse file num: '+str(AppLogType.logCnt)
