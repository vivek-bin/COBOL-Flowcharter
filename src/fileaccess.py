import zipfile
import constants as CONST
import pickle
from nodes import *

SRCE = 0
COPY = 1
INC = 2
EXPANDED = 3
PROCESSING = 4
TREES = 5

zips = [False,False,False,False,False,False]
zipPaths = [False,False,False,False,False,False]
filePaths = [False,False,False,False,False,False]

#zips[SRCE] = zips[COPY] = zips[INC] = zips[EXPANDED] = zips[PROCESSING] = zips[TREES] = False
zipPaths[SRCE] = CONST.SRCEZIP
zipPaths[COPY] = CONST.COPYZIP
zipPaths[INC] = CONST.INCZIP
zipPaths[EXPANDED] = CONST.EXPANDEDZIP
zipPaths[PROCESSING] = CONST.PROCESSINGZIP
zipPaths[TREES] = CONST.TREESZIP

filePaths[SRCE] = "MTP.CCCV000.SRCELIB."
filePaths[COPY] = "MTP.CCCV000.COPYLIB."
filePaths[INC] = "MTP.CCCV000.INCLUDE."
filePaths[EXPANDED] = "MTP.CCCV000.EXPANDED."
filePaths[PROCESSING] = "MTP.CCCV000.PROCESSING."
filePaths[TREES] = "MTP.CCCV000.TREES."

def openLib(lib,mode="r"):
	if mode in ["w","a"]:
		zips[lib] = zipfile.ZipFile(zipPaths[lib],mode,zipfile.ZIP_DEFLATED)
	else:
		zips[lib] = zipfile.ZipFile(zipPaths[lib],mode)
	
def fileListLib(lib):
	fileList = zips[lib].namelist()
	fileList = [fileName[len(filePaths[lib]):] for fileName in fileList]
	return fileList
	
def loadFile(lib,fileName):
	try:
		f = zips[lib].read(filePaths[lib]+fileName.upper())
		f = f.split("\r\n")
	except KeyError:
		f = []
		
	if lib in (SRCE,COPY,INC):
		f = [l[:72].rstrip() for l in f]
	else:
		f = [l.rstrip() for l in f]
	return f
	
def writeFile(lib,fileName,file):
	zips[lib].writestr(filePaths[lib]+fileName,"\r\n".join(file))

def closeLib(lib):
	zips[lib].close()

	
	
def loadDATA(inputFileName):
	f = []
	try:
		iFile = open(CONST.DATA+inputFileName+".txt")

		f = [l.rstrip() for l in iFile]
		iFile.close()
	except IOError:
		f = []
	return f
	
def appendDATA(inputFileName,inputLine):
	try:
		iFile = open(CONST.DATA+inputFileName+".txt","a")

		iFile.write(inputLine+"\n")
		iFile.close()
		return False
	except IOError:
		return False

def writeDATA(inputFileName,inputLine=""):
	try:
		iFile = open(CONST.DATA+inputFileName+".txt","w")

		iFile.write(inputLine+"\n")
		iFile.close()
		return False
	except IOError:
		return False

def writeLOG(inputLine):
	appendDATA("log",inputLine)



def writePickle(outputFileName,file):
	outputFile = open(CONST.TREES+filePaths[TREES]+outputFileName,"wb")
	pickle.dump(file,outputFile)
	outputFile.close()
	
def loadPickle(outputFileName):
	outputFile = open(CONST.TREES+filePaths[TREES]+outputFileName,"rb")
	file = pickle.load(outputFile)
	outputFile.close()
	return file




