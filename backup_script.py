#!/usr/bin/python
import os, sys, shutil, filecmp, time

#convert the standard time to pacific local time, not important but makes it easier for me to test
def getPacificTime():
	timeStruct = time.gmtime()
	hour = None
	if timeStruct[3] < 8:
		hour = 24-(8-timeStruct[3])
	else:
		hour = timeStruct[3]-8
	timeTuple = hour, timeStruct[4], timeStruct[5]
	return timeTuple


def backup_files(folderPath, destPath="/usr/backups"):
	MAXBACKUPS = 20
	#if the folderPath is a file, just copy it over. no need for fancy stuff
	if os.path.isfile(folderPath):
		shutil.copy2(folderPath, destPath)
		return true
	fufilled = False
	#if folderPath is written with a "\" at the end, remove it
	folderPath = folderPath.rstrip(os.sep)
	#acquire the destFolder, the function takes the folder name of folderPath and creates a folder in the destPath with a number attached to it
	for i in range(MAXBACKUPS):
		destPathTest = os.path.join(destPath,(os.path.basename(folderPath) + str(i)))
		if not os.path.exists(destPathTest):
			fufilled = True
			destPath = destPathTest
			break
	#if there are MAXBACKUPS number of folders than it cycles through again until it gets to the folder that is the oldest, it then deletes the folder contents and makes the destPath the empty folder
	if not fufilled:
		for i in range(MAXBACKUPS):			
			destPathTest = os.path.join(destPath,(os.path.basename(folderPath) + str(i)))
			fmTime = os.path.getmtime(destPathTest)
			destPathTest = os.path.join(destPath,(os.path.basename(folderPath) + str(i+1)))
			if not os.path.exists(destPathTest):				
				destPathTest = os.path.join(destPath,(os.path.basename(folderPath) + str(0)))
			ldTime = os.path.getmtime(destPathTest)
			if ldTime < fmTime:
				destPath = destPathTest
				shutil.rmtree(destPath)
				break
			
	os.mkdir(destPath)
	#walks through the entire directory tree of the folderPath and copies it over to destPath
	for root,dirs,files in os.walk(folderPath):
		curDestPath = os.path.join(destPath, root[len(folderPath)+1:])
		if not os.path.exists(curDestPath):
			os.mkdir(curDestPath)
		for s in dirs:
			os.mkdir(os.path.join(curDestPath, s))
		for s in files:
			tempSrc = os.path.join(root, s)
			tempDest = os.path.join(curDestPath, s)
			if os.path.exists(tempSrc):
				shutil.copy2(tempSrc, tempDest)
			else:
				msg = "error: " + tempSrc + " doesnt exist"
				print msg

		
SERVERPATH ="/home/theman515/SigmaServer/world"
SCREEN = "625.minecraft"
#main loop checks to see if the time to backup the world file is now and to see if the server crashed (we were running plus+ modpack, it happened a lot)
#IMPORTANT: this assumes you're running your minecraft server through a gnu screen using a launch script named "launch" without the quotes
while(1):
	timeStruct = getPacificTime()
	if (timeStruct[0] == 4 and timeStruct[1] == 0 and timeStruct[2] == 0) or (timeStruct[0] == 16 and timeStruct[1] == 0 and timeStruct[2] == 0):
		print "alerting the server, 60 seconds"
		curTime = time.time()
		os.system("screen -S " + SCREEN + " -p 0 -X stuff \"/say server is shutting down in 60 seconds\015\"")
		while time.time()-curTime<=30:
			pass
		os.system("screen -S " + SCREEN + " -p 0 -X stuff \"/say server is shutting down in 30 seconds\015\"")
		while time.time()-curTime <= 50:
			pass
		os.system("screen -S " + SCREEN + " -p 0 -X stuff \"/say server is shutting down in 10 seconds\015\"")
		while time.time()-curTime <= 60:
			pass
		print "shutting down the server"
		os.system("screen -S " + SCREEN + " -p 0 -X stuff \"stop\015\"")
		print "backing up the server"
		backup_files(SERVERPATH)
		curTime = time.time()
		while time.time()-curTime < 10:
			pass
		print "relaunching the server"
		os.system("screen -S " + SCREEN + " -p 0 -X stuff \"./launch\015\"")
		print "done"
	fil = os.popen("ps -e")
	output = ""
	#gets all the output from os.popen
	while True:
		stri = fil.readline()
		output += stri
		if stri == "":
			break
	if output.find("launch") == -1:
		msg = "server crashed, restarting"
		print msg
		os.system("screen -S " + SCREEN + " -p 0 -X stuff \"./launch\015\"")
		curTime = time.time()
		while time.time() -curTime < 1:
			pass