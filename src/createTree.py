import constants as CONST
import keywords
import processingfileclass as pfc
import nodes
import time

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

		if inputArg.__class__ is ProcessingUnit:
			self.performReturnStack = inputArg.performReturnStack[:]
			self.performEndStack = inputArg.performEndStack[:]
			self.paraStack = inputArg.paraStack[:]
			self.processedLines = inputArg.processedLines[:]
			self.programCounter = inputArg.programCounter - 0
			self.inputFile = inputArg.inputFile
		
		if inputArg.__class__ is pfc.ProgramProcessingFile:
			self.inputFile = inputArg
			self.programCounter = 0

	def peekStatement(self,lineNo):
		return self.inputFile.procedureDivision[lineNo]
	
	def peekCurrentStatement(self):
		return self.inputFile.procedureDivision[self.processedLines[-1]]
	
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
		currentPara = self.inputFile.getCurrentPara(self.processedLines[-1])
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
	
	lineCount = 0

	while True:
		inputLine = PU.getNextStatement()
		lineDict = digestSentence(inputLine)
		
		if PU.paraReturn:
			break
		
		lineCount += 1
		
		#exec nodes
		if "exec" in lineDict:
			execBlock = [inputLine]
			while "end-exec" not in inputLine:
				inputLine = PU.getNextStatement()
				execBlock.append(inputLine)
				
			execDict = digestExecBlock(execBlock)
			if "call" in execDict:
				lineDict["call"] = execDict["call"]
			if "goback" in execDict:
				lineDict["goback"] = execDict["goback"]
				
			programObj.append(nodes.ExecNode(PU,execDict["type"]))
		
		#returnable statements
		if "goback" in lineDict:
			programObj.append(nodes.EndNode(PU,lineDict["goback"]))
		if "go to" in lineDict:
			tempObj = nodes.GoToNode(PU,lineDict["go to"])
			if lineDict["go to"] not in PU.performEndStack:
				PU.jumpToPara(lineDict["go to"])
				subChart = createChart(ProcessingUnit(PU),True)
			programObj.append(tempObj)
			tempObj = False
		
		
		#point nodes
		if "para" in lineDict:
			programObj.append(nodes.ParaNode(PU,lineDict["para"]))
		if "call" in lineDict:
			calledProgram = getFieldValue(PU,lineDict["call"])
			if calledProgram == "'dfhei1'":
				calledProgram = getFieldValue(PU,lineDict["using"][1])
			programObj.append(nodes.CallNode(PU,calledProgram))
		
		#perform nodes
		if "perform" in lineDict:
			if "until" in lineDict:
				tempObj = nodes.LoopNode(PU,lineDict["until"])
			else:
				tempObj = nodes.NonLoopNode(PU)

			if lineDict["perform"] is not True:
				performStart = lineDict["perform"]
				performEnd = lineDict["perform"]
				if "thru" in lineDict:
					performEnd = lineDict["thru"]
				PU.pushStack(performStart,performEnd)
				ignorePeriod = True
			else:
				ignorePeriod = False
			
			subChart = createChart(PU,ignorePeriod)
			tempObj.branch = subChart
			programObj.append(tempObj)
			tempObj = False
			
			skipStatementsGotoGoback(PU,ignorePeriod)
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			#print PU.programCounter 
		
		
		#check chart end
		if "return statement" in lineDict:
			if not (lineDict["return statement"] == "." and ignorePeriod):
				break
		
		#branching statements
		if "if" in lineDict or "else" in lineDict:
			ifFlag = "if" in lineDict
			if ifFlag:
				tempObj = nodes.IfNode(PU,lineDict["if"])
			subChart = createChart(PU)
			if ifFlag:
				tempObj.trueBranch = subChart
			else:
				tempObj.falseBranch = subChart
			
			skipStatementsGotoGoback(PU)
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			
			if lineDict["return statement"] in ["end-if","."]:
				programObj.append(tempObj)
				tempObj = False
				if "." in lineDict and not ignorePeriod:
					break
	
			
		if "evaluate" in lineDict:
			tempObj = nodes.EvaluateNode(PU,lineDict["evaluate"])
			inputLine = PU.getNextStatement()
			lineDict = digestSentence(inputLine)
		
			while "when" in lineDict:
				tempObj2 = nodes.WhenNode(PU,lineDict["when"])
				while "when" in digestSentence(PU.peekNextStatement()):
					inputLine = PU.getNextStatement()
					lineDict = digestSentence(inputLine)
					tempObj2.addCondition(lineDict["when"])
				
				subChart = createChart(PU)
				tempObj2.branch = subChart
				tempObj.whenList.append(tempObj2)
				
				skipStatementsGotoGoback(PU)
				inputLine = PU.peekCurrentStatement()
				lineDict = digestSentence(inputLine)
					
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
	
	return programObj
	
def skipStatementsGotoGoback(PU,ignorePeriod=False):
	inputLine = PU.peekCurrentStatement()
	lineDict = digestSentence(inputLine)
	while ("." not in lineDict or ignorePeriod) and ("go to" in lineDict or "goback" in lineDict):
		createChart(PU)
		inputLine = PU.peekCurrentStatement()
		lineDict = digestSentence(inputLine)
	
def getFieldValue(PU,field):
	if field[0] in ["'",'"'] or field.replace(".","").isdigit():
		return field

	for lineNo in reversed(PU.processedLines):
		processedLine = PU.peekStatement(lineNo)
		processedDict = digestSentence(processedLine)
		if "move" in processedDict:
			if field in processedDict["to"]:
				field = processedDict["move"]
				if field[0] in ["'",'"'] or field.replace(".","").isdigit():
					break
	
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

