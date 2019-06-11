import constants as CONST
import processingfileclass as pfc
import time
import fileaccess
import sys
import filemod

depthcount = 0

def getMoves(inputLine):
	#dont split quoted text into strings
	if "'" in inputLine or '"' in inputLine:
		singleQuotePos = inputLine.find("'")
		doubleQuotePos = inputLine.find('"')
		if singleQuotePos == -1:
			quoteType = '"'
		elif doubleQuotePos == -1:
			quoteType = "'"
		elif doubleQuotePos > singleQuotePos:
			quoteType = "'"
		else:
			quoteType = '"'
		
		quotePos = [i for i,c in enumerate(inputLine) if c == quoteType]
		while quotePos:
			for i in range(quotePos[0],quotePos[1]):
				if inputLine[i] == " ":
					inputLine = inputLine[:i] + chr(0) + inputLine[i+1:]
			quotePos.pop()
			quotePos.pop()
		
	words = inputLine.replace("."," .").split()
	#inputLine = inputLine.replace(chr(0)," ")
	#words = [word.replace(chr(0)," ") for word in words]
	
	#calls and link and xctl
	lineDict = {}
	if words[0] == "move":
		toPos = words.index("to")
		lineDict["move"] = words[1:toPos]
		lineDict["to"] = words[toPos+1:]
		
		lineDict[0] = [v for v in (lineDict["move"] + lineDict["to"]) if v[0] not in ["'",'"']]
		li = []
		for v in lineDict[0]:
			if "(" in v:
				temp = v[:v.index("(")]
				li.append(temp)
			else:
				li.append(v)
		lineDict[0] = li
		
	return lineDict
	
	
def getFieldsCopybooks(inputFile):
	lineNo = -1
	while lineNo < len(inputFile) - 1:
		lineNo += 1
		inputLine = inputFile[lineNo]
		if inputLine[6] != " ":
			continue
		if " data " in inputLine:
			if " division " in inputLine or " division." in inputLine:
				break
	inputFile = inputFile[lineNo:]
		
	
	lineNo = -1
	while lineNo < len(inputFile) - 1:
		lineNo += 1
		inputLine = inputFile[lineNo]
		if inputLine[6] != " ":
			continue
		if " procedure " in inputLine:
			if " division " in inputLine or " division." in inputLine:
				break
	inputFile = inputFile[:lineNo]
		
		
	file = []
	copybooks = []
	copybooksReplacing = []
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
				copybooks.append(copyFileName)
				#copyFile = fileaccess.loadFile(fileaccess.COPY,copyFileName)
				#if not copyFile:
				#	copyFile = fileaccess.loadFile(fileaccess.INC,copyFileName)
				
				if "replacing" in inputLine:
					inputLine = inputLine[inputLine.find("replacing") + len("replacing") + 1:-1].strip()
					inputLine = inputLine.replace("==","").replace("'","")
					replacedText = inputLine[:inputLine.find(" ")].upper()
					replacingText = inputLine[inputLine.rfind(" ") + 1:].upper()
					copybooksReplacing.append([replacedText,replacingText])
				else:
					copybooksReplacing.append([])
					
				#	copyFile = [l.replace(replacedText, replacingText) for l in copyFile]
				#file.extend(copyFile)
			continue
		
		file.append(inputLine)
	
	return file,copybooks,copybooksReplacing

def getFinalFields(file):
	file = filemod.processingFile(file)
	file = filemod.processingFileCleanData(file)
	file = [v[CONST.ZEROPAD:] for line in file]
	return file
	
	
def getProcedureDivision(inputFile):
	inputFile = [l[CONST.ZEROPAD:] for l in inputFile]
	
	for i,inputLine in enumerate(inputFile):
		if inputLine.startswith("procedure division"):
			inputFile = inputFile[i:]
			break
			
	for i,inputLine in enumerate(inputFile):
		if inputLine.startswith("id division") or inputLine.startswith("identification division"):
			inputFile = inputFile[:i]
			break

	
def getChart(component):
	PU = False
	fChart = []
	
	fileaccess.openLib(fileaccess.EXPANDED)
	fileaccess.openLib(fileaccess.SRCELIB)
	fileList = fileaccess.fileListLib(fileaccess.EXPANDED)
	fileaccess.writeDATA("log")
	srceFile = fileaccess.loadFile(fileaccess.SRCELIB,component)
	
	processingFile = fileaccess.loadFile(fileaccess.EXPANDED,component)
	processingFile = filemod.processingFile(processingFile)
	processingFile = filemod.processingFileClean(processingFile)
	
	
	
	#file = fileaccess.loadDATA("test")
	if processingFile and srceFile:
		file,copybooks,copybooksReplacing = getFieldsCopybooks(srceFile)
		srceFields = getFinalFields(file)
		processingFile = ProgramProcessingFile(processingFile)
		PU, fChart = generateChart(file)
		
	#fileaccess.writePickle(component,fChart)
	#f2 = fileaccess.loadPickle(component)
	
	fileaccess.closeLib(fileaccess.EXPANDED)
	fileaccess.closeLib(fileaccess.SRCELIB)
	
	return fChart
	