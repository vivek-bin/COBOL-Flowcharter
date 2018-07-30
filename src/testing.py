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
	
	file1 = fileaccess.loadFile(fileaccess.PROCESSING,"VIID246")
	processingFile = pfc.ProgramProcessingFile(file1)
		
	PU = createTree.ProcessingUnit(processingFile)
	
	fChart = createTree.createChart(PU,True)
	
	print (time.time() - startTime)
	
	return fChart
	
f = t1()
