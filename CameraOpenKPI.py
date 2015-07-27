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
#	liuchangjian	2015-07-25	v1.0		adb_log sheet save is ok
#	liuchangjian	2015-07-27	v1.0		release version 1.0
#
###########################################################################

#!/bin/python
import sys,os,re,string,time,datetime,xlwt

# save log record			!!! Save all log data !!!
logs = []

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

# save file name
fileName='cam_kpi_data.xls'
SumTags=['FileName','Type']
SumTypes=['Least','Max','Avg']
file_col_width = 6000				# col width

class AppLogType:
	'adb log dir info'
	# app log pattern
	appLogType = r'app_log_'

	# camera open start end end log
	# camera startPreview start and end log		!!! must a pair set
	CamKPITags = ('Open time(ms)','StartPreview time(ms)')
	CamLog = (r'openCamera\(\S\): E',r'openCamera\(\S\): X',r'QCamera2HardwareInterface:startPreview\(\): E',r'QCamera2HardwareInterface::startPreview\(\): X')
	
	logCnt = 0
	__path = ''
	__dir = ''
	__file = ''
	__time = []			### !!! 8 pair time record must to more than len(CamLog)!!!
	__CamLogList = []								### log time's array
	__CamTimeKPI = []								### every time kpi

	def __init__(self,path,dir,file):
		self.__path = path
		self.__dir = dir
		self.__file = file
		AppLogType.logCnt+=1
		self.__time = []
		self.__CamLogList  = []
		self.__CamTimeKPI = []
	
	def __CalTime(self,date1,date2):
		Tdate1=time.strptime(date1,"%m-%d %H:%M:%S.%f")
    		Tdate2=time.strptime(date2,"%m-%d %H:%M:%S.%f")
		
		date1=date1.partition(' ')
		d1=date1[2].partition('.')
		if debugLog >= debugLogLevel[-1]:
			print 'INFO: Data 1 '+d1[0]+"."+d1[2]

		date2=date2.partition(' ')
		d2=date2[2].partition('.')
		if debugLog >= debugLogLevel[-1]:
			print 'INFO: Data 2 '+d2[0]+"."+d2[2]
 		
    		Sdate1=datetime.datetime(1990,Tdate1[1],Tdate1[2],Tdate1[3],Tdate1[4],Tdate1[5])
    		Sdate2=datetime.datetime(1990,Tdate2[1],Tdate2[2],Tdate2[3],Tdate2[4],Tdate2[5])
    		return int(time.mktime(Sdate2.timetuple())*1000)+string.atoi(d2[2])-int(time.mktime(Sdate1.timetuple())*1000)-string.atoi(d1[2])
		

	def __CalKPI(self,time):
		count = 0
		kpiTime=[]
		for i in range(0,len(time)):						# a group
			count+=1
			if not time[i]:
				if debugLog >= debugLogLevel[-1]:
					print 'INFO: Time Array len is :'+str(i)
				break

			if count%2==0:
				if debugLog >= debugLogLevel[2]:
					print 'INFO: KPI time is '+time[i-1]+" "+time[i]

				kpiTime.append(self.__CalTime(time[i-1],time[i]))
				
		if debugLog >= debugLogLevel[2]:
			print 'INFO: Group KPI Data: '+str(kpiTime)
					
		# Save a group data		
		self.__CamTimeKPI.append(kpiTime)


	
	def __ScanCamLog(self,fd):
		if debugLog >= debugLogLevel[2]:
			print 'INFO: begin scan camera log!'

		while 1:
			line = fd.readline()
			
			if not line:
				if debugLog >= debugLogLevel[2]:
					print 'INFO: Finish Parse file!\n'
				break;

			if debugLog >= debugLogLevel[-1]:
				print 'INFO: Read line is :'+line
		
			for i in range(0,len(AppLogType.CamLog)):							# Adapter every key tag
				if debugLog >= debugLogLevel[-1]:
					print 'INFO: Camera log-> '+AppLogType.CamLog[i]

				log = re.compile(AppLogType.CamLog[i])
		
				if debugLog >= debugLogLevel[2]:
					print 'INFO: Scan log-> '+log.pattern

				search = re.search(log,line)
				if search:
					if debugLog >= debugLogLevel[1]:
						print 'INFO: Scan log-> '+log.pattern
						print 'INFO: Search Camera log->'+search.group()
						print 'line is: '+line
					
					timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d+')
					
					if debugLog >= debugLogLevel[2]:
						print 'INFO: TimeFormat-> '+timeFormat.pattern
					
					time = re.search(timeFormat,line)
					if time:
						if debugLog >= debugLogLevel[2]:
							print 'INFO: Find key time-> '+time.group()
						
						self.__time.append(time.group())
						
						if debugLog >= debugLogLevel[2]:
							print 'INFO: Time -> '+self.__time[i]
					
					## Save one group
					if i == len(AppLogType.CamLog) - 1:
				
						if debugLog >= debugLogLevel[-1]:
							print 'INFO: Record one goup len num -> '+str(len(AppLogType.CamLog) - 1)

						if debugLog >= debugLogLevel[1]:
							print self.__time

						# Save a group 
						self.__CamLogList.append(self.__time)

						# calc KPI
						self.__CalKPI(self.__time)

						self.__time=[]	

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
		if debugLog >= debugLogLevel[2]:
			print 'Cam Log list len: '+str(len(self.__CamLogList))

		return self.__CamLogList
		
	def GetCamTimeKPIIndex(self,index):
		if debugLog >= debugLogLevel[2]:
			print 'Cam Time KPI index '+str(index)+' is : '+str(self.__CamTimeKPI[index])
		return self.__CamTimeKPI[index]
	
	def GetCamTimeKPI(self):
		if debugLog >= debugLogLevel[2]:
			print 'Cam Time KPI list len: '+str(len(self.__CamTimeKPI))
		return self.__CamTimeKPI
		
# Only exec in one adb_log directory!!! Can't have two adb_log dir
def ScanFiles(arg,dirname,files):
	if debugLog >= debugLogLevel[-1]:
		print dirname

	for file in files:
		logType = re.compile(AppLogType.appLogType)

		if debugLog >= debugLogLevel[-1]:
			print AppLogType.appLogType
			print file
		
		m = re.match(logType,file)
		if m:
			path,name = os.path.split(dirname)

			if debugLog >= debugLogLevel[2]:
				print '\nFound Dir: '+name
			
			log = AppLogType(dirname,name,file)
			logs.append(log)
			log.ScanCameraLog()

def OutPutData(xl,Ssheet,mlog,index):
	if debugLog >= debugLogLevel[1]:
		print "\nSave sheet: "+mlog.GetName()
	
	sheet = xl.add_sheet(mlog.GetName())

	# Ssheet save
	Ssheet.col(0).width = 9000
	Ssheet.write(index*3+1,0,mlog.GetName())

	Ssheet.col(2).width=file_col_width
	for i in range(0,len(SumTypes)):
		Ssheet.write(index*3+1+i,1,SumTypes[i])
	
	# sheet save	
	for i in range(0,len(AppLogType.CamLog)):
		sheet.col(i+1).width=file_col_width
		sheet.write(0,i+1,AppLogType.CamLog[i])

	for i in range(0,len(AppLogType.CamKPITags)):
		col_p=i+1+len(AppLogType.CamLog)+1
		sheet.col(col_p).width=file_col_width
		sheet.write(0,col_p,AppLogType.CamKPITags[i])
	
	log = mlog.GetCamLogList()

	for i in range(0,len(log)):
		sheet.write(i+1,0,i+1)
		
	excel_date_fmt = 'MM-DD h:mm:ss.0'
	style = xlwt.XFStyle()
	style.num_format_str = excel_date_fmt
		
	for i in range(0,len(log)):
		data = log[i]
		
		if debugLog >= debugLogLevel[2]:
			print 'Group '+str(i+1)+' data len: '+str(len(data))
		
		for j in range(0,len(data)):
			if debugLog >= debugLogLevel[2]:
				print data[j]
			sheet.write(i+1,j+1,data[j],style)
	
		KPIIndexData = mlog.GetCamTimeKPIIndex(i)
	
		if debugLog >= debugLogLevel[2]:
			print 'KPI index data is '+str(KPIIndexData)
		
		if len(KPIIndexData) < len(AppLogType.CamKPITags):
			print 'ERROR: kpi data len '+str(len(KPIIndexData))+' is less than need('+str(len(AppLogType.CamKPITags))+')!!!'
			return
		else:
			for j in range(0,len(AppLogType.CamKPITags)):
				sheet.write(i+1,j+1+len(AppLogType.CamLog)+1,KPIIndexData[j])


	# Save min max avg data to SumSheet
	KPIData = mlog.GetCamTimeKPI()

	if debugLog >= debugLogLevel[1]:
		print 'KPI data is '+str(KPIData)

	s_col_pos = len(SumTags)

	for i in range(0,len(AppLogType.CamKPITags)):
		GroupList = [x[i] for x in KPIData]
		
		if debugLog >= debugLogLevel[2]:
			print 'Group data is '+str(GroupList)
		
		GroupList.sort()
		
		if debugLog >= debugLogLevel[2]:
			print 'Sort Group data is '+str(GroupList)

		Ssheet.write(index*3+1,s_col_pos+i,GroupList[0])
		Ssheet.write(index*3+1+1,s_col_pos+i,GroupList[-1])
		Ssheet.write(index*3+1+2,s_col_pos+i,sum(GroupList)/len(GroupList))


# Save data to excel
def SaveLogKPI():
	xlwb = xlwt.Workbook(encoding='utf-8')
	SumSheet = xlwb.add_sheet('Sum')

	for i in range(0,len(SumTags)):
		SumSheet.col(i).width=file_col_width
		SumSheet.write(0,i,SumTags[i])
	
	for i in range(0,len(AppLogType.CamKPITags)):
		col_p=len(SumTags)+i
		SumSheet.col(col_p).width=file_col_width
		SumSheet.write(0,col_p,AppLogType.CamKPITags[i])

	for mlog in logs:
		OutPutData(xlwb,SumSheet,mlog,logs.index(mlog))

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
