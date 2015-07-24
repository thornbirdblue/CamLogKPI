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
#	liuchangjian	2015-07-24	v1.0		add xls save
#
###########################################################################

#!/bin/python
import sys,os,re,string,time,datetime,xlwt

# app log pattern
appLogType = r'app_log_'

# camera open start end end log
# camera startPreview start and end log		!!! must a pair set
CamLog = (r'openCamera E',r'openCamera X',r'StartPreview E',r'StartPreview X')


# save log record			!!! Save all log data !!!
logs = []

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

# save file name
fileName='cam_kpi_data.xls'
SumTags=['Least','Max','Avg']


class AppLogType:
	'adb log dir info'
	logCnt = 0
	__path = ''
	__dir = ''
	__file = ''
	__time = ['','','','','','','','','','','','','','','','']			### !!! 8 pair time record must to more than len(CamLog)!!!
	__CamLogList = []								### log time's array
	__CamTimeKPI = []								### every time kpi

	def __init__(self,path,dir,file):
		self.__path = path
		self.__dir = dir
		self.__file = file
		AppLogType.logCnt+=1
	
	def __CalTime(self,date1,date2):
 		Tdate1=time.strptime(date1,"%m-%d %H:%M:%S.%f")
    		Tdate2=time.strptime(date2,"%m-%d %H:%M:%S.%f")
    		Sdate1=datetime.datetime(Tdate1[0],Tdate1[1],Tdate1[2],Tdate1[3],Tdate1[4],Tdate1[5])
    		Sdate2=datetime.datetime(Tdate2[0],Tdate2[1],Tdate2[2],Tdate2[3],Tdate2[4],Tdate2[5])
    		return Sdate2-Sdate1
		

	def __CalKPI(self,time):
		KPITime=self.__time
		for i in range(0,len(time)):						# a group
			if not time[i]:
				if debugLog >= debugLogLevel[-1]:
					print 'INFO: Time Array len is :'+str(i)
				break

			if i%2==1 and i!=0:
				if debugLog >= debugLogLevel[2]:
					print 'INFO: KPI time is '+time[i-1]+" "+time[i]

				KPITime[i/2] = self.__CalTime(time[i-1],time[i])
				if debugLog >= debugLogLevel[1]:
					print 'INFO: Group '+str(i/2)+' KPI: '+str(KPITime[i/2])
		return KPITime		


	
	def __ScanCamLog(self,fd):
		if debugLog >= debugLogLevel[1]:
			print 'INFO: begin -------------------------------------> scan camera log!'

		while 1:
			line = fd.readline()
			
			if not line:
				print 'INFO: Finish Parse file!\n'
				break;

			if debugLog >= debugLogLevel[2]:
				print 'INFO: Read line is :'+line
		
			for i in range(0,len(CamLog)):							# Adapter every key tag
				if debugLog >= debugLogLevel[2]:
					print 'INFO: Camera log-> '+CamLog[i]

				log = re.compile(CamLog[i])
		
				if debugLog >= debugLogLevel[2]:
					print 'INFO: Scan log-> '+log.pattern

				search = re.search(log,line)
				if search:
					if debugLog >= debugLogLevel[1]:
						print 'INFO: Search Camera log->'+search.group()
					
					timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d+')
					
					if debugLog >= debugLogLevel[2]:
						print 'INFO: TimeFormat-> '+timeFormat.pattern
					
					time = re.search(timeFormat,line)
					if time:
						if debugLog >= debugLogLevel[2]:
							print 'INFO: Find key time-> '+time.group()
						
						self.__time[i] = time.group()
						
						if debugLog >= debugLogLevel[1]:
							print 'INFO: Time -> '+self.__time[i]
					
					## Save one group
					if i == len(CamLog) - 1:
				
						if debugLog >= debugLogLevel[-1]:
							print 'INFO: Record one goup len num -> '+str(len(CamLog) - 1)

						if debugLog >= debugLogLevel[1]:
							print 'INFO: !!!---------------------------------Add one group record !!!'

						# Save a group 
						self.__CamLogList.append(self.__time)

						# calc KPI
						self.__CamTimeKPI.append(self.__CalKPI(self.__time))
	

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
	def GetName(self):
		return self.__file

	def GetCamLogList(self):
		return self.__CamLogList
		
	def GetCamTimeKPI(self):
		return self.__CamTimeKPI
		
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

def OutPutData(xl,Ssheet,mlog):
	xl.add_sheet(mlog.GetName())

# Save data to excel
def SaveLogKPI():
	xlwb = xlwt.Workbook(encoding='utf-8')
	SumSheet = xlwb.add_sheet('Sum')

	for i in range(0,len(SumTags)):
		SumSheet.write(0,i+3,SumTags[i])

	for mlog in logs:
		OutPutData(xlwb,SumSheet,mlog)

	xlwb.save(fileName)	


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
	print 'Total Parse file num: '+str(AppLogType.logCnt)

	SaveLogKPI()
	print 'Save'
