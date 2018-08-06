import createTree
import fileaccess
import os
import time

	
def t9(component="VIID246"):
	startTime = time.time()
	
	chart = createTree.getChart(component)
	
	
	
	
	print (time.time() - startTime)
	
	return chart
	
	

