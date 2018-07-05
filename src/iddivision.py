PATH = "E:\\CAAGIS flow tracker\\MTP\\MTP\\"
SRCELIB = PATH + "SRCELIB\\"
COPYLIB = PATH + "COPYLIB\\"
INCLUDE = PATH + "INCLUDE\\"
EXPANDED = PATH + "EXPANDED\\"
PROCESSING = PATH + "PROCESSING\\"


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
			
		if inputLine.find("identification ") != -1 or inputLine.find("id ") != -1:
			if inputLine.find(" division") != -1:
				return True
		return False
	return False
	
	
def t6():
	import os
	import time
	startTime = time.time()
	l=os.listdir(COPYLIB)
	l1=[li.rstrip(".txt") for li in l] 
	l2=l1[:5000]
	for n in l1:
		if isCobolProgram(loadFile(n,COPYLIB)):
			print n
	print time.time() - startTime
	
	