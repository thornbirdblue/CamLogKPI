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

# camera open start end end log
# camera startPreview start and end log
CamLog = (r'openCamera E',r'openCamera X',r'StartPreview E',r'StartPreview X')


# save log record
logs = []

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

class AppLogType:
	'adb log dir info'
	logCnt = 0
	__path = ''
	__dir = ''
	__file = ''
	__time = ['','','','','','','','','','','','','','','','']			### !!! 8 pair time record must more than len(CamLog)!!!

	def __init__(self,path,dir,file):
		self.__path = path
		self.__dir = dir
		self.__file = file
		AppLogType.logCnt+=1
	
	def __ScanCamLog(self,fd):
		if debugLog >= debugLogLevel[1]:
			print 'INFO: begin -------------------------------------> scan camera log!'

		while 1:
			line = fd.readline()
			
			if not line:
				print 'INFO: Finish read file!\n'
				break;

			if debugLog >= debugLogLevel[2]:
				print 'INFO: Read line is :'+line
		
			for i in range(0,len(CamLog)):
				if debugLog >= debugLogLevel[2]:
					print 'INFO: Camera log-> '+CamLog[i]

				log = re.compile(CamLog[i])
		
				if debugLog >= debugLogLevel[2]:
					print 'INFO: Scan log-> '+log.pattern

				search = re.search(log,line)
				if search:
					if debugLog >= debugLogLevel[1]:
						print 'INFO: Search Camera log->'+search.group()
					
					timeFormat = re.compile(r'\s\d{2}:\d{2}:\d{2}.\d+')
					
					if debugLog >= debugLogLevel[2]:
						print 'INFO: TimeFormat-> '+timeFormat.pattern
					
					time = re.search(timeFormat,line)
					if time:
						if debugLog >= debugLogLevel[2]:
							print 'INFO: Find key time-> '+time.group()
						
						self.__time[i] = time.group()
						
						if debugLog >= debugLogLevel[1]:
							print 'INFO: Time -> '+self.__time[i]
	

	def ScanCameraLog(self):
		if debugLog >= debugLogLevel[1]:
			print 'Parse file: '+os.path.join(self.__path,self.__file)
		try:
			fd = open(os.path.join(self.__path,self.__file),'r')	
			
			if debugLog >= debugLogLevel[2]:
				print 'INFO: open file :'+os.path.join(self.__path,self.__file)

			self.__ScanCamLog(fd)

			fd.close()

		except IOError:
			print "open file ERROR: Can't open"+os.path.join(self.__path,self.__file)
			sys.exit()

			
		
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
				print '\nFound Dir: '+name
			
			log = AppLogType(dirname,name,file)
			logs.append(log)
			log.ScanCameraLog()

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
						print 'Log level is: '+str(debugLog)
					else:
						print 'cmd para ERROR: '+sys.argv[i+1]+' is not int num!!!'
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
