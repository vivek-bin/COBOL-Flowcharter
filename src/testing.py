import createTree
import fileaccess as fa
import os
import time
import tooltip
import constants as CONST
	
def t9(component="VIID246"):
	startTime = time.time()
	
	log = fa.loadDATA("log")
	log = [l[8:] for l in log]
	
	for i in range(len(log)):
		l = log[i]
		if l.strip() == "exit.":
			ln = log[i+1]
			if ln[4] != " ":
				print i 
				break
	
	print (time.time() - startTime)
	
	
t9()
