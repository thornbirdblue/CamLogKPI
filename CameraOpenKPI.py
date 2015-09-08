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
#	liuchangjian	2015-07-28	v1.1		resolve sheet dup name and null tag write pos questions
#	liuchangjian	2015-07-30	v1.3		correct time is xx.xx.xx.xxxxxx! There is six num in ms!
#	liuchangjian	2015-09-08	v2.0		fix error code in file can't scan bug!!! Use rb mode to open file!	
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
fileName=''
ScanPath=''
SumTags=['FileName','Type']
SumTypes=['Least','Max','Avg']
file_col_width = 4500				# col width

class AppLogType:
	'adb log dir info'
	# app log pattern
	appLogType = r'app_log_'

	# camera open start end end log
	# camera startPreview start and end log		!!! must a pair set
	CamKPITags = ('Open time(ms)','StartPreview(ms)','Sum time(ms)','Total time(ms)')
	CamLog = ('openCamera E','openCamera X','startPreview E','startPreview X')
	CamLogPattern = (r'openCamera\(\S\): E',r'openCamera\(\S\): X',r'QCamera2HardwareInterface:startPreview\(\): E',r'QCamera2HardwareInterface::startPreview\(\): X')
	CamLogPos = ('openCamera : E','openCamera : X','QCamera2HardwareInterface:startPreview : E','QCamera2HardwareInterface:startPreview : X')

	logNames=[]
	
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

		## 2015-08-11 liuchangjian correct time is xx.xx.xx.xxxxxx! There is six num in ms begin
		Sdata1C = time.mktime(Sdate1.timetuple())*1000
		Sdata2C = time.mktime(Sdate2.timetuple())*1000
		
		if len(d1[2]) == 3 :
			ms2 = string.atoi(d2[2])
			ms1 = string.atoi(d1[2])
		elif len(d1[2]) == 6:
			ms2 = string.atoi(d2[2])/1000
			ms1 = string.atoi(d1[2])/1000

		time2 = Sdata2C+ms2
		time1 = Sdata1C+ms1
		
		## 2015-08-11 liuchangjian correct time is xx.xx.xx.xxxxxx! There is six num in ms End
		
		if debugLog >= debugLogLevel[2]:
			print 'Cal Time is '+str(time2)+" - "+str(time1)

		return int(time2 - time1)
		

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
				
		if debugLog >= debugLogLevel[1]:
			print 'INFO: Group KPI Data: '+str(kpiTime)
				
		# Save a group data		
		self.__CamTimeKPI.append(kpiTime)
		
		SumTime=0
		for i in range(0,len(kpiTime)):
			SumTime +=kpiTime[i]

		# Save Sum time
		kpiTime.append(SumTime)			

		# Save Total time		
		kpiTime.append(self.__CalTime(time[0],time[-1]))

	
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

				log = re.compile(AppLogType.CamLogPattern[i])
		
				if debugLog >= debugLogLevel[-1]:
					print 'INFO: Scan log-> '+log.pattern

				search = re.search(log,line)
				if search:
					if debugLog >= debugLogLevel[1]:
						print 'INFO: Search Camera log->'+search.group()
						print 'line is: '+line
					
					timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d+')
					
					if debugLog >= debugLogLevel[2]:
						print 'INFO: TimeFormat-> '+timeFormat.pattern
					
					time = re.search(timeFormat,line)
					if time:
						if debugLog >= debugLogLevel[2]:
							print 'INFO: Find key time-> '+time.group()

						# patch-> cal tag position and write to the right pos
						if debugLog >= debugLogLevel[1]:
							tags = search.group()
							print tags
							#print 'INFO: pos is '+str(AppLogType.CamLogPos.index(tags))+' time list len is'+str(len(self.__time))

						pos = AppLogType.CamLogPos.index(search.group()) - len(self.__time)
						if pos:						
							if debugLog >= debugLogLevel[-1]:
								print 'WARNING: There is '+str(pos)+' data null!!!'

							for i in range(0,pos):
								self.__time.append(time.group())
								
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
			fd = open(os.path.join(self.__path,self.__file),'rb')								# 2015-09-08 liuchangjian fix error code in file bug!!! change r to rb mode!
			
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
			print 'AppLogType Cam Time KPI index '+str(index)+' is : '+str(self.__CamTimeKPI[index])
		return self.__CamTimeKPI[index]
	
	def GetCamTimeKPI(self):
		if debugLog >= debugLogLevel[2]:
			print 'AppLogType Cam Time KPI : '
			print self.__CamTimeKPI
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
	LogName = mlog.GetName()
	if debugLog >= debugLogLevel[2]:
		print "\nSave sheets: "
		print AppLogType.logNames

	if LogName in AppLogType.logNames:
		for i in range(1,99):
			if (LogName+'_'+str(i)) in AppLogType.logNames:
				continue
			else:
				LogName = LogName+'_'+str(i)
				if debugLog >= debugLogLevel[2]:
					print 'Rename sheet name to '+LogName
				AppLogType.logNames.append(LogName)
				sheet = xl.add_sheet(LogName)
				if debugLog >= debugLogLevel[1]:
					print "\nSave sheet: "+LogName
				break
	else:
		AppLogType.logNames.append(mlog.GetName())
		sheet = xl.add_sheet(mlog.GetName())
		if debugLog >= debugLogLevel[1]:
			print "\nSave sheet: "+mlog.GetName()

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
		sheet.col(col_p).width=3000
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
	
	if KPIData:
		for i in range(0,len(AppLogType.CamKPITags)):
			GroupList = [x[i] for x in KPIData]
		
			if debugLog >= debugLogLevel[1]:
				print 'Group data is '+str(GroupList)

			# remove 0 item
			GList = []
			for j in range(0,len(GroupList)):
				if GroupList[j] == 0:
					print 'WARNING: Remove List '+str(j)+'! Val is '+str(GroupList[j])
				# liuchangjian 2015-09-08 del else code! fix zero bug!
				GList.append(GroupList[j])				
		
			GList.sort()
		
			if debugLog >= debugLogLevel[2]:
				print 'Sort Group data is '+str(GList)

			Ssheet.write(index*3+1,s_col_pos+i,GList[0])
			Ssheet.write(index*3+1+1,s_col_pos+i,GList[-1])
			Ssheet.write(index*3+1+2,s_col_pos+i,sum(GList)/len(GList))
	else:
		print 'WARNing: There is no Camera log in '+LogName+' file!!!'


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
	
	if fileName:
		xlwb.save(fileName+'.xls')	
	else:
		xlwb.save('cam_kpi_data.xls')	


def ParseArgv():
	if len(sys.argv) > appParaNum+1:
		CameraOpenKPIHelp()
		sys.exit()
	else:
		for i in range(1,len(sys.argv)):
			if sys.argv[i] == '-h':
				Usage()
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
			elif sys.argv[i] == '-o':
				if sys.argv[i+1]:
					global fileName
					fileName = sys.argv[i+1]
					print 'OutFileName is '+fileName
				else:
					Usage()
					sys.exit()
			elif sys.argv[i] == '-p':
				if sys.argv[i+1]:
					global ScanPath
					ScanPath = sys.argv[i+1]
					print 'Scan dir path is '+ScanPath
				else:
					Usage()
					sys.exit()
					

def Usage():
	print 'Command Format :'
	print '		CameraOpenKPI [-d 1/2/3] [-o outputfile] [-p path] | [-h]'

appParaNum = 6

if __name__ == '__main__':
	ParseArgv()

	print ScanPath.strip()
	if not ScanPath.strip():
		spath = os.getcwd()
	else:
		spath = ScanPath
	
	print 'Scan DIR: '+spath+'\n'

	os.path.walk(spath,ScanFiles,())
	print 'Total Parse file num: '+str(AppLogType.logCnt)

	if AppLogType.logCnt:
		SaveLogKPI()
