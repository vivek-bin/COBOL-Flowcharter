import constants as CONST
import keywords
import processingfileclass as pfc
import nodes
import time
import fileaccess
import sys

depthcount = 0

class ProcessingUnit:
	def __init__(self,inputArg=False):
		self.performReturnStack = []
		self.performEndStack = []
		self.paraStack = []
		self.processedLines = []		#list of all lines processed
		self.programCounter = 0			#points to next sentence to be executed
		self.inputFile = []
		self.paraCall = False
		self.paraReturn = False
		self.currentPara = ""

		if inputArg.__class__ is ProcessingUnit:
			self.performReturnStack = inputArg.performReturnStack[:]
			self.performEndStack = inputArg.performEndStack[:]
			self.paraStack = inputArg.paraStack[:]
			self.processedLines = inputArg.processedLines[:]
			self.programCounter = inputArg.programCounter - 0
			self.inputFile = inputArg.inputFile
			self.currentPara = inputArg.currentPara
		
		if inputArg.__class__ is pfc.ProgramProcessingFile:
			self.inputFile = inputArg
			self.programCounter = 0

	def peekStatement(self,lineNo):
		return self.inputFile.procedureDivision[lineNo]
	
	def peekCurrentStatement(self):
		currentLine = self.processedLines[-1]
		return self.inputFile.procedureDivision[currentLine]
	
	def peekNextStatement(self):
		return self.inputFile.procedureDivision[self.programCounter]
	
	def incrementProgramCounter(self):
		self.paraReturn = False
		
		if self.processedLines and not self.paraCall:
			if self.processedLines[-1] in self.inputFile.paraEnd.keys():
				if self.inputFile.paraEnd[self.processedLines[-1]] in self.performEndStack:
					stackIndex = self.performEndStack.index(self.inputFile.paraEnd[self.processedLines[-1]])
					stackDepth = len(self.performEndStack) - stackIndex

					for i in range(stackDepth):
						self.performEndStack.pop()
						self.paraStack.pop()
						self.programCounter = self.performReturnStack.pop()
					self.paraReturn = True
		
		self.paraCall = False
		self.processedLines.append(self.programCounter)
		self.programCounter += 1
	
	def getNextStatement(self):
		self.incrementProgramCounter()
		return self.peekCurrentStatement()
	
	def pushStack(self,performStart,performEnd):
		#time.sleep(0.5)
		#fileaccess.writeLOG(";".join(self.paraStack))
		currentPara = self.currentPara
		self.paraStack.append(currentPara)
		self.performReturnStack.append(self.processedLines[-1])
		self.performEndStack.append(performEnd)
		
		self.jumpToPara(performStart)
		
	def jumpToPara(self,paraName):
		self.programCounter = self.inputFile.paraStart[paraName]
		self.paraCall = True
	
	
def createChart(PU,ignorePeriod=False):
	programObj = []
	tempObj = False
	global depthcount
	lineCount = 0
	depthcount += 1
	try:
		fileaccess.writeLOG("start:" + str(depthcount)+ "      " + str(PU.processedLines[-1])+ "      " + str(PU.inputFile.procedureDivision[PU.processedLines[-1]]))
	except IndexError:
		fileaccess.writeLOG("start:index error")
	
	while True:
		inputLine = PU.getNextStatement()
		lineDict = digestSentence(inputLine)
		fileaccess.writeLOG(str(PU.processedLines[-1]) + "    " + str(inputLine))
		if PU.paraReturn:
			break
		
		lineCount += 1
		
		
		#exec nodes
		if "exec" in lineDict:
			execBlock = [inputLine]
			tempPU = ProcessingUnit(PU)
			while "end-exec" not in inputLine:
				inputLine = PU.getNextStatement()
				execBlock.append(inputLine)
				
			execDict = digestExecBlock(execBlock)
			if "call" in execDict:
				lineDict["call"] = execDict["call"]
			if "goback" in execDict:
				lineDict["goback"] = execDict["goback"]
				
			if execDict["type"] == "sql":
				tempObj2 = nodes.ExecNode(tempPU,execDict["type"])
				if "cursor" in execDict:
					tempObj2.cursor = execDict["cursor"]
				if "table" in execDict:
					tempObj2.table = execDict["table"]
				if "query" in execDict:
					tempObj2.query = execDict["query"]
				programObj.append(tempObj2)
		
		
		#point node
		if "para" in lineDict:
			PU.currentPara = lineDict["para"]
			programObj.append(nodes.ParaNode(PU,lineDict["para"]))
		if "file" in lineDict:
			statement = lineDict["file"]
			programObj.append(nodes.FileNode(PU,statement,lineDict[statement]))
		if "call" in lineDict:
			calledProgram = getFieldValue(PU,lineDict["call"])
			if calledProgram == "'dfhei1'":
				if len(lineDict["using"])==1:
					lineDict["goback"] = True
					calledProgram = ""
				else:
					calledProgram = getFieldValue(PU,lineDict["using"][1])
			
			if calledProgram:
				programObj.append(nodes.CallNode(PU,calledProgram))
			
			
		#returnable statements
		if "goback" in lineDict:
			programObj.append(nodes.EndNode(PU,lineDict["goback"]))
		if "go to" in lineDict:
			tempObj = nodes.GoToBranch(PU,lineDict["go to"])
			if lineDict["go to"] not in (PU.paraStack + PU.performEndStack + [PU.currentPara]):
				goToPU = ProcessingUnit(PU)
				goToPU.jumpToPara(lineDict["go to"])
				subChart = createChart(goToPU,True)
				tempObj.branch = subChart
			programObj.append(tempObj)
			tempObj = False
			
		
		#check chart end
		if "return statement" in lineDict:
			if not (lineDict["return statement"] == "." and ignorePeriod):
				break	
		
		#perform nodes
		if "perform" in lineDict:
			if "until" in lineDict:
				tempObj = nodes.LoopBranch(PU,lineDict["until"])
			else:
				tempObj = nodes.NonLoopBranch(PU)
			
			paraAlreadyInPath = False
			if lineDict["perform"] is not True:
				ignorePeriodSub = True
				performStart = lineDict["perform"]
				performEnd = lineDict["perform"]
				if "thru" in lineDict:
					performEnd = lineDict["thru"]
				
				if performStart in PU.paraStack:
					paraAlreadyInPath = True
					tempObj = nodes.LoopBreakPointer(PU,performStart)
					programObj.append(tempObj)
					tempObj = False
				else:
					PU.pushStack(performStart,performEnd)
			else:
				ignorePeriodSub = False
				
			if not paraAlreadyInPath:
				subChart = createChart(PU,ignorePeriodSub)
				tempObj.branch = subChart
				programObj.append(tempObj)
				tempObj = False
				
				inputLine = PU.peekCurrentStatement()
				lineDict = digestSentence(inputLine)
				awkwardReturnFlag = False
				while ("go to" in lineDict or "goback" in lineDict) and ("." not in lineDict or ignorePeriodSub):
					awkwardReturnFlag = True
					createChart(PU,ignorePeriodSub)
					inputLine = PU.peekCurrentStatement()
					lineDict = digestSentence(inputLine)
				if not awkwardReturnFlag:
					while subChart and (subChart[-1].__class__ is nodes.LoopBranch or subChart[-1].__class__ is nodes.NonLoopBranch):
						subChart = subChart[-1].branch
					while subChart and (subChart[-1].__class__ is nodes.GoToBranch or subChart[-1].__class__ is nodes.EndNode):
						subChart = createChart(PU,ignorePeriodSub)
						while subChart and (subChart[-1].__class__ is nodes.LoopBranch or subChart[-1].__class__ is nodes.NonLoopBranch):
							subChart = subChart[-1].branch
			
			if "." in lineDict and not ignorePeriod:
				break
			continue
		
		
		#check chart end
		if "return statement" in lineDict:
			if not (lineDict["return statement"] == "." and ignorePeriod):
				break
		
		#branching statements
		while "if" in lineDict or "else" in lineDict:
			ifCondition = "if" in lineDict
			if ifCondition:
				tempObj = nodes.IfNode(PU,lineDict["if"])
			
			subChart = createChart(PU)
			
			tempObj2 = nodes.IfBranch(PU,ifCondition)
			tempObj2.branch = subChart
			tempObj.branch[ifCondition] = tempObj2
			
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			
			while ("go to" in lineDict or "goback" in lineDict) and ("." not in lineDict or ignorePeriod):
				createChart(PU)
				#createChart(PU,ignorePeriod)
				inputLine = PU.peekCurrentStatement()
				lineDict = digestSentence(inputLine)
				
			if lineDict["return statement"] in ["end-if","."]:
				programObj.append(tempObj)
				tempObj = False
				if "." in lineDict and not ignorePeriod:
					break
		if "." in lineDict and not ignorePeriod:
			break
			
		if "evaluate" in lineDict:
			tempObj = nodes.EvaluateNode(PU,lineDict["evaluate"])
			inputLine = PU.getNextStatement()
			lineDict = digestSentence(inputLine)
		
			while "when" in lineDict:
				tempObj2 = nodes.WhenBranch(PU,lineDict["when"])
				while "when" in digestSentence(PU.peekNextStatement()):
					inputLine = PU.getNextStatement()
					lineDict = digestSentence(inputLine)
					tempObj2.addCondition(lineDict["when"])
				
				subChart = createChart(PU)
				tempObj2.branch = subChart
				tempObj.whenList.append(tempObj2)
				
				inputLine = PU.peekCurrentStatement()
				lineDict = digestSentence(inputLine)
				while ("go to" in lineDict or "goback" in lineDict) and ("." not in lineDict or ignorePeriod):
					createChart(PU)
					#createChart(PU,ignorePeriod)
					inputLine = PU.peekCurrentStatement()
					lineDict = digestSentence(inputLine)
			
			#"other" branch always exists for evaluate
			otherBranch = False
			for whenbranch in tempObj.whenList:
				for cond in whenbranch.condition:
					if cond == "other":
						otherBranch = True
			if not otherBranch:
				tempObj2 = nodes.WhenBranch(PU,"other")
				tempObj.whenList.append(tempObj2)
			
			
			if lineDict["return statement"] in ["end-evaluate","."]:
				programObj.append(tempObj)
				tempObj = False
				if "." in lineDict and not ignorePeriod:
					break
		
	
	if tempObj:
		programObj.append(tempObj)
	
	emptyFlag = True
	for tempObj in programObj:
		if not tempObj.isEmpty():
			emptyFlag = False
	#if emptyFlag:
	#	programObj = []
	
	depthcount -= 1
	try:
		fileaccess.writeLOG("end:" + str(depthcount)+ "      " + str(PU.processedLines[-1])+ "      " + str(PU.inputFile.procedureDivision[PU.processedLines[-1]]))
	except IndexError:
		fileaccess.writeLOG("end:index error")
	
	
	return programObj
	
def getFieldValue(PU,field):
	if field[0] in ["'",'"'] or field.replace(".","").isdigit():
		return field
	i=0
	for lineNo in reversed(PU.processedLines):
		i+=1
		if i>500:
			break
		processedLine = PU.peekStatement(lineNo)
		if not processedLine.startswith("move "):
			continue
		processedDict = digestSentence(processedLine)
		if "move" in processedDict:
			if field in processedDict["to"]:
				i=0
				field = processedDict["move"]
				if field[0] in ["'",'"'] or field.replace(".","").isdigit():
					break
	#print i
	
	#get initial value(string in quotes,number) if not MOVE'd
	if field[0] in ["'",'"'] or field.replace(".","").isdigit():
		pass
	else:
		field = " " + field + " "
		
		for inputLine in PU.inputFile.dataDivision:
			if field in inputLine:
				if " value " in inputLine:
					valuePos = inputLine.find(" value ") + len(" value ")
					field = inputLine[valuePos:-1]
				break
				
		field = field.strip()

	return field
	
def digestSentence(inputLine):
	lineDict = {}
	words = inputLine.replace("."," .").split()
	
	#keyList = []
	#keyList.extend(["para","if","else","end-if",".","evaluate","when","end-evaluate","call","go to"])
	#keyList.extend(["perform","thru","until","end-perform","exec","end-exec","goback","return statement"])
	#keyList.extend(["using","move","to"])
	#for word in keyList:
	#	lineDict[word] = False
	
	lineDict[0] = words[0]
	lineDict[words[0]] = True
	if "." in words:
		lineDict["."] = True
		
	if inputLine[0] != " " and "." in lineDict:
		lineDict["para"] = words[0]	
	
	if "move" in lineDict:
		toPos = words.index("to")
		lineDict["move"] = words[toPos-1]
		lineDict["to"] = words[toPos+1:]
		
	if lineDict[0] in ["open","read","write","close","rewrite","delete","start"]:
		lineDict["file"] = lineDict[0]
		lineDict[lineDict[0]] = words[1]
		if words[0] == "open":
			lineDict[lineDict[0]] = words[2]
		if words[0] == "read" and words[1] == "next":
			lineDict[lineDict[0]] = words[2]
	
	if words[0] == "go" and words[1] == "to":
		lineDict["go to"] = words[2]
	
	if "call" in lineDict:
		lineDict["call"] = words[1]
		if "using" in words:
			usingPos = words.index("using")
			lineDict["using"] = []
			for word in words[usingPos+1:]:
				lineDict["using"].append(word)
	
	if "if" in lineDict:
		lineDict["if"] = " ".join(words[1:])
	
	if "evaluate" in lineDict:
		lineDict["evaluate"] = " ".join(words[1:])
	
	if "when" in lineDict:
		lineDict["when"] = " ".join(words[1:])
	
	if "perform" in lineDict:
		thruPos = varyingPos = untilPos = timesPos = False
		try:
			thruPos = words.index("thru")
		except ValueError:
			pass
		try:
			thruPos = words.index("through")
		except ValueError:
			pass
		try:
			varyingPos = words.index("varying")
		except ValueError:
			pass
		try:
			untilPos = words.index("until")
		except ValueError:
			pass
		try:
			timesPos = words.index("times")
		except ValueError:
			pass
		
		if not keywords.isKeyword(words[1]):
			lineDict["perform"] = words[1]
		if thruPos:
			lineDict["thru"] = words[thruPos+1]
		if timesPos:
			lineDict["until"] = words[timesPos-1] + "  " +  words[timesPos]
		if varyingPos:
			lineDict["until"] = " ".join(words[varyingPos+1:])
		if untilPos and not varyingPos:
			lineDict["until"] = " ".join(words[untilPos+1:])
	
	if words[0] == "stop" and words[1] == "run":
		lineDict["goback"] = True
	if words[0] == "exit" and words[1] == "program":
		lineDict["goback"] = True
	
	
	for word in ["end-if","end-evaluate","end-perform","when","else","go to","goback","."]:
		if word in lineDict:
			lineDict["return statement"] = word
			break
	
	return lineDict
	
def digestExecBlock(inputBlock):
	execDict = {}
	inputLine = " ".join(inputBlock)
	words = inputLine.split()
	
	#keyList = []
	#keyList.extend(["type","call","goback","cursor","query","table","."])
	#for dictKey in keyList:
	#	execDict[dictKey] = False

	execDict["type"] = words[1]
	
	if "." in words[-1]:
		execDict["."] = True
	
	if execDict["type"] == "cics":
		if "link" in words or "xctl" in words:
			progPos = words.index("program")
			execDict["call"] = words[progPos+1][1:-1]
		if "return" in words:
			execDict["goback"] = True
			
	
	if execDict["type"] == "sql":
		cursorPos = fromPos = intoPos = wherePos = False
		if "into" in words:
			execDict["table"] = words[words.index("into")+1]
		if "from" in words:
			execDict["table"] = words[words.index("from")+1]
		if "update" in words:
			execDict["table"] = words[words.index("update")+1]
		
		for cursorPreword in ["declare","open","close","fetch"]:
			if cursorPreword in words:
				cursorPos = words.index(cursorPreword) + 1
				break
		if "where" in words:
			wherePos = words.index("where")
			if words[wherePos+1] == "current" and words[wherePos+2] == "of":
				cursorPos = wherePos + 3
		if cursorPos:
			execDict["cursor"] = words[cursorPos]
		
		for queryWord in ["select","open","close","fetch","update","delete","insert"]:
			if queryWord in words:
				execDict["query"] = queryWord
				
	return execDict

def generateChart(file):
	fChart = []
	
	processingFile = pfc.ProgramProcessingFile(file)
	PU = ProcessingUnit(processingFile)
	sys.setrecursionlimit(4000)
	fChart = createChart(PU,True)
	sys.setrecursionlimit(1000)
	
	return PU, fChart
	
def getChart(component):
	fileaccess.openLib(fileaccess.PROCESSING)
	fileList = fileaccess.fileListLib(fileaccess.PROCESSING)
	fileaccess.writeDATA("log")
	file = fileaccess.loadFile(fileaccess.PROCESSING,component)
	#file = fileaccess.loadDATA("test")
	
	PU, fChart = generateChart(file)
	#fileaccess.writePickle(component,fChart)
	#f2 = fileaccess.loadPickle(component)
	
	fileaccess.closeLib(fileaccess.PROCESSING)
	
	return fChart
		
def getPU(component):
	fileaccess.openLib(fileaccess.PROCESSING)
	fileList = fileaccess.fileListLib(fileaccess.PROCESSING)
	fileaccess.writeDATA("log")
	file = fileaccess.loadFile(fileaccess.PROCESSING,component)
	#file = fileaccess.loadDATA("test")
	
	fChart = []
	
	processingFile = pfc.ProgramProcessingFile(file)
	PU = ProcessingUnit(processingFile)
	
	#fChart = createChart(PU,True)
	#fileaccess.writePickle(component,fChart)
	#f2 = fileaccess.loadPickle(component)
	
	fileaccess.closeLib(fileaccess.PROCESSING)
	
	return PU
	
def t1():
	return getChart("vib3248")
	
def t2():
	return getPU("aib018y")
	
#n=t1()