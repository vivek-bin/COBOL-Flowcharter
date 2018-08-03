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
	
	fChart = createTree.createChart(PU,True)
	
	return PU, fChart
	
	
def t1():
	startTime = time.time()
	fileaccess.openLib(fileaccess.PROCESSING)
	fileList = fileaccess.fileListLib(fileaccess.PROCESSING)
	fileaccess.writeDATA("log")
	file = fileaccess.loadFile(fileaccess.PROCESSING,"VIB3248")
	#file = fileaccess.loadDATA("test")
	PU, fChart = generateChart(file)
	
	fileaccess.closeLib(fileaccess.PROCESSING)
	
	print (time.time() - startTime)
	return PU, fChart
	

PU, f = t1()


