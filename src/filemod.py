import constants as CONST
import keywords

def writeFile(inputFileName,lib,inputList):
	try:
		inputFile = open(lib+inputFileName+".txt","w")
		inputFile.writelines( "%s\n" % row for row in inputList)
		inputFile.close()
	except IOError:
		print ("couldnt write file")
	
def loadFile(inputFileName,lib):
	f = []
	try:
		inputFile = open(lib+inputFileName+".txt")
		
		if lib in (CONST.SRCELIB,CONST.COPYLIB,CONST.INCLUDE):
			f = [l[:72].rstrip() for l in inputFile]
		else:
			f = [l.rstrip() for l in inputFile]
		inputFile.close()
	except IOError:
		pass
	return f

def expandFile(inputFile):
	file = []
	
	lineNo = -1
	while lineNo < len(inputFile) - 1:
		lineNo += 1
		inputLine = inputFile[lineNo]
		if len(inputLine) < 8:
			file.append(inputLine)
			continue
		if inputLine[6] != " ":
			file.append(inputLine)
			continue
		
		inputLineStrip = inputLine[7:].lower()
		inputLineStrip = " ".join(inputLineStrip.split())
		if inputLineStrip[:5] == "copy " or inputLineStrip[:8] == "exec sql":
			specialBlock = []
			specialBlock.append(inputLine)
			while inputLine[6] != " " or (inputLine.find(".") == -1 and inputLine.lower().find("end-exec") == -1):
				lineNo += 1
				inputLine = inputFile[lineNo]
				if len(inputLine) < 8:
					inputLine += "        "
				specialBlock.append(inputLine)
			
			inputLine = ""
			for specialLine in specialBlock:
				if specialLine[6] == " ":
					inputLine += specialLine[7:]
			inputLine = " ".join(inputLine.split()).lower().replace("."," ")
			
			expandFlag = True
			if inputLine[:5] == "copy ":
				copyFileName = inputLine[5:inputLine.find(" ",5)]
			elif inputLine[:17] == "exec sql include ":
				copyFileName = inputLine[17:inputLine.find(" ",17)]
			else:
				expandFlag = False
			
			for specialLine in specialBlock:
				if specialLine[6] == " " and expandFlag:
					specialLine = specialLine[:6] + "*" + specialLine[7:]
				file.append(specialLine)
				
			if expandFlag:
				copyFile = loadFile(copyFileName,CONST.COPYLIB)
				if not copyFile:
					copyFile = loadFile(copyFileName,CONST.INCLUDE)
				
				if inputLine.find("replacing") != -1:
					inputLine = inputLine[inputLine.find("replacing") + len("replacing") + 1:-1].strip()
					inputLine = inputLine.replace("==","").replace("'","")
					replacedText = inputLine[:inputLine.find(" ")].upper()
					replacingText = inputLine[inputLine.rfind(" ") + 1:].upper()
					
					copyFile = [l.replace(replacedText, replacingText) for l in copyFile]
				file.extend(copyFile)
			continue
		
		file.append(inputLine)
	
	return file

def processingFile(inputFile):
	file = []
	
	for inputLine in inputFile:
		inputLine = inputLine.lower().rstrip()
		if len(inputLine) < 8:
			continue
		if inputLine[6] != " ":
			continue
		if inputLine.replace(".","").strip() == "eject":
			continue
			
		inputLine = inputLine[7:]

		if inputLine[:4] == "    ":
			inputLine = "    " + " ".join(inputLine.split())
		else:
			inputLine = " ".join(inputLine.split())
		file.append(inputLine)
		
	return file

def processingFileClean(inputFile):
	file = []
	procedureDivisionPos = 0
	for inputLine in inputFile:
		if inputLine[:18] == "procedure division":
			break
		procedureDivisionPos += 1
	file = inputFile[:procedureDivisionPos+1]
	inputFile = inputFile[procedureDivisionPos+1:]
	
	line = ""
	execFlag = False
	for inputLine in inputFile:
		inputWords = inputLine.replace(".","").split()
		if not inputWords:
			if line:
				file.append(line)
				line = ""
			file.append(inputLine)
			continue
		
		if inputLine[0] != " " and len(inputWords) == 2 and inputWords[1] == "section":
			if line:
				file.append(line)
				line = ""
			file.append(inputWords[0]+".")
			continue			
		
		if inputWords[0] == "exec":
			execFlag = True
		if "end-exec" in inputWords:
			file.append(inputLine)
			execFlag = False
			continue
		if execFlag:
			file.append(inputLine)
			continue
			
		if  keywords.isMainVerb(inputWords[0]) or inputLine[0] != " ":
			if line:
				file.append(line)
			line = inputLine
		else:
			if line:
				line = line + " " + inputLine.strip()
			else:
				line = inputLine
	if line:
		file.append(line)
	
	return file

def isCobolProgram(inputFile):
	for inputLine in inputFile:
		if len(inputLine) < 8:
			continue
		if inputLine[6] != " ":
			continue
		
		inputLine = " ".join(inputLine[6:].split()).lower()
				
		if inputLine == "eject" or inputLine == "eject.":
			continue
			
		if inputLine.find("identification ") != -1 or inputLine.find("id ") != -1:
			if inputLine.find(" division") != -1:
				return True
		
		if inputLine[:5] == "copy ":
			if inputLine[5:13].replace(".","").strip() in ["igacces","pcr33010","pcr33019","tccp002"]:
				return True
		
		return False
	return False

def writeProcessingExpand(component):
	src = loadFile(component,CONST.SRCELIB)
	if not isCobolProgram(src):
		if component[2:4].lower() != "ms":
			print ("not COBOL:" + component)
		writeFile(component,CONST.EXPANDED,src)
		#writeFile(component,CONST.PROCESSING,src)
	else:
		expandSrce = expandFile(src)
		writeFile(component,CONST.EXPANDED,expandSrce)
		writeFile(component,CONST.PROCESSING,processingFileClean(processingFile(expandSrce)))
	
def getIncludedCopybooks(inputFile):
	file = []
	
	lineNo = -1
	while lineNo < len(inputFile) - 1:
		lineNo += 1
		inputLine = inputFile[lineNo]
		if len(inputLine) < 8:
			continue
		if inputLine[6] != " ":
			continue
		
		inputLineStrip = inputLine[7:].lower()
		inputLineStrip = " ".join(inputLineStrip.split())
		if inputLineStrip[:5] == "copy " or inputLineStrip[:8] == "exec sql":
			specialBlock = []
			specialBlock.append(inputLine)
			while lineNo < len(inputFile)-1 and (inputLine[6] != " " or (inputLine.find(".") == -1 and inputLine.lower().find("end-exec") == -1)):
				lineNo += 1
				inputLine = inputFile[lineNo]
				if len(inputLine) < 8:
					inputLine += "        "
			
			inputLine = ""
			for specialLine in specialBlock:
				if specialLine[6] == " ":
					inputLine += specialLine[7:]
			inputLine = " ".join(inputLine.split()).lower().replace("."," ")
			
			expandFlag = True
			if inputLine[:5] == "copy ":
				copyFileName = inputLine[5:inputLine.find(" ",5)]
			elif inputLine[:17] == "exec sql include ":
				copyFileName = inputLine[17:inputLine.find(" ",17)]
			else:
				expandFlag = False
				
			if expandFlag:
				file.append(copyFileName)
			continue
		
	return file
	
def writeAllProcessingExpand(count=999999):
	import os
	import time
	startTime = time.time()
	list = os.listdir(CONST.SRCELIB)
	list = [fileName.rstrip(".txt") for fileName in list]
	processingList = list[:count]
		
	for fileName in processingList:
		writeProcessingExpand(fileName)
	print (time.time() - startTime)

def t1():
	writeAllProcessingExpand(100)
	
	