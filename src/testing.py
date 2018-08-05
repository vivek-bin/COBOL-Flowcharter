import constants as CONST
import processingfileclass as pfc
import createTree
import fileaccess
import os
import time

def generateChart(file):
	fChart = []
	
	processingFile = pfc.ProgramProcessingFile(file)
	PU = createTree.ProcessingUnit(processingFile)
	print "getting chart"
	fChart = createTree.createChart(PU,True)
	
	return PU, fChart
	
	
def getChart(component):
	startTime = time.time()
	fileaccess.openLib(fileaccess.PROCESSING)
	fileList = fileaccess.fileListLib(fileaccess.PROCESSING)
	fileaccess.writeDATA("log")
	file = fileaccess.loadFile(fileaccess.PROCESSING,component)
	#file = fileaccess.loadDATA("test")
	PU, fChart = generateChart(file)
	
	fileaccess.closeLib(fileaccess.PROCESSING)
	
	print (time.time() - startTime)
	return PU, fChart
	
PU=[]
f=[]

def t1(component="VIB3248"):
	global PU,f
	PU, f = getChart(component)


