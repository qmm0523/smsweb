#!/usr/bin/env python
#!coding=utf-8
# author 92ez.com

import webbrowser
import subprocess
import signal
import serial
import time
import json
import sys
import web
import re
import os

urls = (
	"/","index",
	"/killdev","killDev",
	"/getUSB","getUSB",
	"/getSMS","getSMS",
	"/download","download",
	"/readARFCN","readARFCN",
	"/getARFCN","getARFCN",
	"/smartARFCN","smartARFCN",
	"/doSniffer","doSniffer",
	"/stopSniffer","killProcess"
)

#static 
render = web.template.render('static',cache = False)

#init program
class index:
	def GET(self):
		subprocess.Popen("rm -rf *.dat",shell = True)
		return render.index("static")

class killDev:
	def POST(self):
		subprocess.Popen("killall ccch_scan cell_log osmocon 2>/dev/null",shell = True)
		return json.dumps({"res":0}) 

class getUSB:
	def POST(self):
		global USBLIST
		USBLIST = []

		subPro2 = subprocess.Popen('ls /dev | grep ttyUSB', shell=True,stdout = subprocess.PIPE)
		subPro2.wait()
		ttylog = subPro2.communicate()

		ttyusbList = ttylog[0].split('\n')

		del ttyusbList[len(ttyusbList)-1]

		for u in range(len(ttyusbList)):
			USBLIST.append('/dev/'+ttyusbList[u])

		return json.dumps({"total":len(USBLIST),"rows":USBLIST})

class download:
	def POST(self):
		global OSMOCOM_L2

		OSMOCOM_L2 = []
		sw = serial.Serial(USBLIST[0],9600)
		keyPort = ['10','11','12','14','15','16','17','19']
		del USBLIST[0]

		for dev in USBLIST:
			try:
				downloadCommand = ['xterm','-e',sys.path[0]+'/osmocombb_x64/osmocon','-m','c123','-s','/tmp/osmocom_l2_'+ str(USBLIST.index(dev)) ,'-p',dev,sys.path[0]+'/osmocombb_x64/layer1.compalram.bin']
				downloadProcess = subprocess.Popen(downloadCommand,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
				OSMOCOM_L2.append('/tmp/osmocom_l2_'+ str(USBLIST.index(dev)))
				time.sleep(1)
			except Exception,e:
				return json.dumps({"res":-1,"msg":str(e)})

		for port in keyPort:
			try:
				sw.write(port+'|200')
				time.sleep(2)
			except Exception,e:
				return json.dumps({"res":-1,"msg":str(e)})
		return json.dumps({"res":0})

class readARFCN:
	def POST(self):
		arfcnlist = []
		for line in open(sys.path[0]+"/arfcn.log"): 
			arfcnlist.append(line.replace('\n',''))
		return json.dumps({"res":0,"rows":arfcnlist[:-1],"date":arfcnlist[-1]})

class getARFCN:
	def POST(self):
		try:
			cellLogshell = [sys.path[0]+"/osmocombb_x64/cell_log","-s","/tmp/osmocom_l2_0","-O"];
			arfcnScan = subprocess.Popen(cellLogshell,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
			scanlog = arfcnScan.communicate()
			arfcnScan.wait()
			scanloginfo = ";".join(scanlog)
			scanbase = re.findall(r"ARFCN\=[^)]+\)",scanloginfo)
		except Exception,e:
			return json.dumps({"res":-1,"msg":str(e)})
		return json.dumps({"res":0,"arfcn":scanbase,"total":len(scanbase)})

class smartARFCN:
	def POST(self):
		return json.dumps({"res":0})

class doSniffer:
	def POST(self):
		arfcnId = web.input().get('arfcnId')
		sniffcommand = ["xterm","-e",sys.path[0]+"/osmocombb_x64/ccch_scan","-s","/tmp/osmocom_l2_1","-i","127.0.0.1","-a",arfcnId]
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
		# data = mysql.query("SELECT * FROM sms_data limit "+str(limitCount)+","+str(rows)+";")
		# total = mysql.query("SELECT id FROM sms_data")
		SMSStr =[]
		for row in data:
			thisMsg = row['sms_message']
			thisType = str(row['type'])
			thisTime = str(row['time'])
			thisTel = str(row['sms_from'])
			thisCenter = str(row['sms_to'])
			thisId = str(row['id'])
			SMSStr.append({"content":thisMsg,"id":thisId,"time":thisTime,"type":thisType,"to":thisCenter,"from":thisTel})

		return json.dumps({"rows":SMSStr,"total":100})
				
if __name__ == "__main__":
	webbrowser.open("http://localhost:"+sys.argv[1], new=0, autoraise=True)
	app = web.application(urls,globals())
	app.run()
