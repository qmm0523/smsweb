#!/usr/bin/env python
#!coding=utf-8
# author 92ez.com
# last modify 2015-08-23 22:03:40

import re
import os
import web
import sys
import json
import psutil
import signal
import MySQLdb
import webbrowser
import subprocess


urls = (
	"/","index",
	"/getUSB","getUSB",
	"/getProcess","getProcess",
	"/getSMS","getSMS",
	"/download","download",
	"/getARFCN","getARFCN",
	"/doSniffer","doSniffer",
	"/stopSniffer","killProcess"
)

#static 
render = web.template.render('static',cache = False)

#init program
class index:
	def GET(self):
		subprocess.Popen("rm -rf *.dat",shell = True)
		subprocess.Popen("service mysql restart",shell = True)
		subprocess.Popen("killall ccch_scan cell_log osmocon 2>/dev/null",shell = True)

		return render.index("static")

class getUSB:
	def POST(self):
		global USBLIST
		USBLIST = []
		for i in range(50):
			if os.path.exists('/dev/ttyUSB'+str(i)):
				USBLIST.append(i)
		return json.dumps({"total":len(USBLIST),"rows":USBLIST})

class getProcess:
	def POST(self):
		processList = psutil.pids()

		haveToSeeProcess = []
		
		for psIndex in range(len(processList)):
			currentProcess = psutil.Process(processList[psIndex]) 
			if(currentProcess.name() == 'ccch_scan'):
				haveToSeeProcess.append(currentProcess.name())
			if(currentProcess.name() == 'cell_log'):
				haveToSeeProcess.append(currentProcess.name())
			if(currentProcess.name() == 'osmocon'):
				haveToSeeProcess.append(currentProcess.name())
			if(currentProcess.name() == 'mysqld'):
				haveToSeeProcess.append(currentProcess.name())
		
		print haveToSeeProcess

class download:
	def POST(self):
		deviceId = web.input().get('deviceId')

		downloadCommand = ['xterm','-e','./osmocon','-m','c123xor','-s','/tmp/osmocom_l2_'+ str(deviceId) ,'-p','/dev/ttyUSB'+ str(deviceId),'./layer1.compalram.bin']
		downloadProcess = subprocess.Popen(downloadCommand,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
		return json.dumps({"res":0})

class getARFCN:
	def POST(self):
		deviceId = web.input().get('deviceId')
		cellLogshell = ["./cell_log","-s","/tmp/osmocom_l2_"+str(deviceId),"-O"];
		arfcnScan = subprocess.Popen(cellLogshell,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
		scanlog = arfcnScan.communicate()
		arfcnScan.wait()
		scanloginfo = ";".join(scanlog)
		scanbase = re.findall(r"ARFCN\=[^)]+\)",scanloginfo)
		return json.dumps({"arfcn":scanbase,"total":len(scanbase)})

class doSniffer:
 	def POST(self):
 		arfcnId = web.input().get('arfcnId')

		sniffcommand = ["xterm","-e","./ccch_scan","-s","/tmp/osmocom_l2_0","-i","127.0.0.1","-a",arfcnId]

		snifferProcess =  subprocess.Popen(sniffcommand,stderr=subprocess.PIPE,stdout=subprocess.PIPE)

		return json.dumps({"res":0,"pid":snifferProcess.pid})

class killProcess:
	def POST(self):
		pid = web.input().get('pid')
		subprocess.Popen("kill "+pid,shell = True)
		return json.dumps({"res":0})

class getSMS:
	def POST(self):
		mysql = Database()
		page = int(web.input().get("page"))
		rows = int(web.input().get("rows"))
		limitCount = (page-1)*rows
		data = mysql.query("SELECT * FROM sms_data limit "+str(limitCount)+","+str(rows)+";")
		length = mysql.query("SELECT id FROM sms_data")
		SMSStr =[]
		for row in data:
			thisMsg = row['sms_message']
			thisType = str(row['type'])
			thisTime = str(row['time'])
			thisTel = str(row['sms_from'])
			thisCenter = str(row['sms_to'])
			thisId = str(row['id'])
			SMSStr.append({"content":thisMsg,"id":thisId,"time":thisTime,"type":thisType,"to":thisCenter,"from":thisTel})

		return '{"rows":'+  json.dumps(SMSStr)+',"total":'+ str(len(length))+'}'

class Database:
	host = '127.0.0.1'
	user = 'root'
	password = 'root'
	db = 'smshack'
	charset = 'utf8'

	def __init__(self):
		self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db,charset=self.charset)
		self.cursor = self.connection.cursor()
 
	def insert(self, query):
		try:
				self.cursor.execute(query)
				self.connection.commit()
		except:
				self.connection.rollback()
 
	def query(self, query):
		cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
		cursor.execute(query)
		return cursor.fetchall()
 
	def __del__(self):
		self.connection.close()
				
if __name__ == "__main__":
	webbrowser.open("http://localhost:"+sys.argv[1], new=0, autoraise=True)
	app = web.application(urls,globals())
	app.run()
