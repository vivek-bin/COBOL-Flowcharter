import constants as CONST
import processingfileclass as pfc
import createTree
import fileaccess
import os

import time

def t1():
	import os
	import time
	startTime = time.time()
	fChart = []
	
	fileaccess.openLib(fileaccess.PROCESSING)
	
	file1 = fileaccess.loadFile(fileaccess.PROCESSING,"VIIDB48")
	#file1 = fileaccess.loadDATA("test")
	processingFile = pfc.ProgramProcessingFile(file1)
	print (time.time() - startTime)
	
	PU = createTree.ProcessingUnit(processingFile)
	print (time.time() - startTime)
	
	fChart = createTree.createChart(PU,True)
	print (time.time() - startTime)
	
	return PU, fChart
	
PU, f = t1()
