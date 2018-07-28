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
			while inputLine[6] != " " or ("." not in inputLine and "end-exec" not in inputLine.lower()):
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
				
				if "replacing" in inputLine:
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
	
	for i, inputLine in enumerate(inputFile):
		inputLine = inputLine.lower().rstrip()
		if len(inputLine) < 8:
			continue
		if inputLine[6] != " ":
			continue
		if inputLine.replace(".","").strip() == "eject":
			continue
			
		inputLine = inputLine[7:]

		if inputLine[:4] == "    ":
			inputLine = " ".join(inputLine.split())
			inputLine = inputLine.replace("( ","(").replace(" )",")")
			words = inputLine.split()
			
			inputLine = prevWord = words[0]
			for currWord in words[1:]:
				if currWord[0] != "(" or keywords.isKeyword(prevWord):
					inputLine += " "
				inputLine += currWord
				prevWord = currWord
					
			#inputLine = inputLine.replace(" (","(")
			inputLine = "    " + inputLine
		else:
			inputLine = " ".join(inputLine.split())
		file.append(str(i).zfill(CONST.ZEROPAD) + inputLine)
		
	return file

def processingFileClean(inputFile):
	file = []
	dataDivisionPos = procedureDivisionPos = 0
	for inputLine in inputFile:
		if inputLine[CONST.ZEROPAD:len("data division")+CONST.ZEROPAD] == "data division":		#line count CONST.ZEROPAD digits
			break
		dataDivisionPos += 1
	for inputLine in inputFile:
		if inputLine[CONST.ZEROPAD:len("procedure division")+CONST.ZEROPAD] == "procedure division":		#line count CONST.ZEROPAD digits
			break
		procedureDivisionPos += 1
	
	file = inputFile[:dataDivisionPos+1]
	inputFile = inputFile[dataDivisionPos+1:]
	procedureDivisionPos -= dataDivisionPos+1
	
	line = ""
	for inputLine in inputFile[:procedureDivisionPos]:
		if line:
			line += " " + inputLine[CONST.ZEROPAD:].strip()
		else:
			line = inputLine
			
		if inputLine[-1] == ".":
			file.append(line)
			line = ""
	file.append(inputFile[procedureDivisionPos])
	
	inputFile = inputFile[procedureDivisionPos+1:]
	
	line = ""
	lineNo = -1
	execFlag = False
	for inputLine in inputFile:
		lineNo = inputLine[:CONST.ZEROPAD]
		inputLine = inputLine[CONST.ZEROPAD:]
		
		inputWords = inputLine.replace(".","").split()
		
		if not inputWords:
			if line:
				file.append(line)
				line = ""
			file.append(lineNo + inputLine)
			continue
		
		if inputLine[0] != " " and len(inputWords) == 2 and inputWords[1] == "section":
			if line:
				file.append(line)
				line = ""
			file.append(lineNo + inputWords[0]+".")
			continue			
		
		if inputWords[0] == "exec":
			execFlag = True
		if "end-exec" in inputWords:
			file.append(lineNo + inputLine)
			execFlag = False
			continue
		if execFlag:
			file.append(lineNo + inputLine)
			continue
			
		if  keywords.isMainVerb(inputWords[0]) or inputLine[0] != " ":
			if line:
				file.append(line)
			line = lineNo + inputLine
		else:
			if line:
				line = line + " " + inputLine.strip()
			else:
				line = lineNo + inputLine
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
			
		if "identification " in inputLine or "id " in inputLine:
			if " division" in inputLine:
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
			while lineNo < len(inputFile)-1 and (inputLine[6] != " " or ("." not in inputLine and "end-exec" not in inputLine.lower())):
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
		print (fileName)
		writeProcessingExpand(fileName)
	print (time.time() - startTime)

def t1():
	writeAllProcessingExpand(100)
	
	