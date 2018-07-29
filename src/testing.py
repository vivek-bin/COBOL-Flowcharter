import constants as CONST
import zipfile as zip
import os
import time

srczip = False
inczip = False

def loadFile(inputFileName,lib):
	try:
		inputFile = open(lib+inputFileName+".txt")
		f = [l[:72].rstrip() for l in inputFile]
		inputFile.close()
	except IOError:
		f = []	
	return f

def isCobolProgram(inputFile):
	for inputLine in inputFile:
		if len(inputLine) < 8:
			continue
		if inputLine[6] != " ":
			continue
		inputLine = inputLine[6:].strip().lower()
		
		if inputLine == "eject" or inputLine == "eject.":
			continue
			
		if "identification " in inputLine or "id " in inputLine:
			if " division" in inputLine:
				return True
		return False
	return False
	
def fileLength(inputFileName,lib):
	i = -1
	f = open(lib+inputFileName+".txt")
	for i, l in enumerate(f):
		pass
	f.close()
	return i + 1
	
def fileLength2(inputFileName):
	i = -1
	f = srczip.read(inputFileName).split("\r\n")
	inczip.writestr(inputFileName,"\r\n".join(f))
	for i, l in enumerate(f):
		pass
	return i + 1
	
def t1():
	startTime = time.time()
	l=os.listdir(CONST.SRCELIB)
	l1=[li.rstrip(".txt") for li in l] 
	l2=l1[:5000]
	maxl = -1
	pname = ""
	for n in l1:
		len = fileLength(n,CONST.SRCELIB)
		if len > maxl:
			pname = n
			maxl = len
	print pname
	print maxl
	print time.time() - startTime
		
def t2():
	startTime = time.time()
	
	maxl = -1
	pname = ""
	l1 = srczip.namelist()[1:]
	for n in l1:
		len = fileLength2(n)
		if len > maxl:
			pname = n
			maxl = len
	print pname
	print maxl
	print time.time() - startTime
	
#sT = time.time()
#srczip = zip.ZipFile('D:\\CAAGIS flow tracker\\compressed\\COPYLIB.zip')
#inczip = zip.ZipFile('D:\\CAAGIS flow tracker\\compressed\\COPYLIB2.zip',"w",zip.ZIP_DEFLATED)
#t2()
#srczip.close()
#inczip.close()
#print time.time() - sT
	
def t6():
	startTime = time.time()
	l=os.listdir(CONST.COPYLIB)
	l1=[li.rstrip(".txt") for li in l] 
	l2=l1[:5000]
	for n in l1:
		if isCobolProgram(loadFile(n,CONST.COPYLIB)):
			print n
	print time.time() - startTime
	
	