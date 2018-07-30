import constants as CONST
import keywords
import processingfileclass as pfc
import nodes

class ProcessingUnit:
	def __init__(self,inputArg=False):
		self.performReturnStack = []
		self.performEndStack = []
		self.paraStack = []
		self.processedLines = []		#list of all lines processed
		self.programCounter = 0			#points to next sentence to be executed
		self.inputFile = []
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

	def peekStatement(self,lineNo):
		return self.inputFile.inputFile[lineNo]
	
	def peekCurrentStatement(self):
		return self.inputFile.inputFile[self.processedLines[-1]]
	
	def peekNextStatement(self):
		return self.inputFile.inputFile[self.programCounter]
	
	def stackSize():
		return len(self.performEndStack)
	
	def incrementProgramCounter(self):
		self.paraReturn = False
		self.processedLines.append(self.programCounter)
		currentPara = self.inputFile.getCurrentPara(self.processedLines[-1])
		if self.inputFile.paraEnd[currentPara] == self.processedLines[-1] and currentPara in self.performEndStack:
			self.setPerformReturn(currentPara)
			self.paraReturn = True
		else:
			self.programCounter += 1
	
	def getNextStatement(self):
		self.incrementProgramCounter()
		return self.peekCurrentStatement()
	
	def pushStack(self,performStart,performEnd):
		currentPara = self.inputFile.getCurrentPara(self.processedLines[-1])
		self.paraStack.append(currentPara)
		self.performReturnStack.append(self.programCounter)
		self.performEndStack.append(performEnd)
		
		self.programCounter = self.inputFile.paraStart[performStart]

	def setPerformReturn(self,para):
		stackIndex = self.performEndStack.index(para)
		
		stackDepth = len(self.performEndStack) - stackIndex
		for i in range(1,stackDepth):
			self.performEndStack.pop()
			self.paraStack.pop()
			self.programCounter = self.performReturnStack.pop()
	
def createChart(PU,ignorePeriod=False):
	programObj = []
	tempObj = False
	
	lineCount = 0

	while True:
		inputLine = PU.getNextStatement()
		lineDict = digestSentence(inputLine)
		
		lineCount += 1
		
		#point nodes
		if lineDict["para"]:
			programObj.append(nodes.ParaNode(PU,lineDict["para"]))
		if lineDict["call"]:
			calledProgram = getFieldValue(PU,lineDict["call"])
			if calledProgram == "'dfhei1'":
				calledProgram = getFieldValue(PU,lineDict["using"][1])
			programObj.append(nodes.CallNode(PU,calledProgram))
		if lineDict["goback"]:
			programObj.append(nodes.EndNode(PU,lineDict["goback"]))
		if lineDict["go to"]:
			tempObj = nodes.GoToNode(PU,lineDict["go to"])
			if lineDict["go to"] not in PU.performEndStack:
				subChart = createChart(ProcessingUnit(PU),True)
			programObj.append(tempObj)
			tempObj = False
		
		#perform nodes
		if lineDict["perform"]:
			if lineDict["until"]:
				tempObj = nodes.LoopNode(PU,lineDict["until"])
			else:
				tempObj = nodes.NonLoopNode(PU)

			if type(lineDict["perform"]) is str:
				performStart = lineDict["perform"]
				performEnd = lineDict["perform"]
				if lineDict["thru"]:
					performEnd = lineDict["thru"]
				PU.pushStack(performStart,performEnd)
				ignorePeriod = True
			else:
				ignorePeriod = False
			
			subChart = createChart(PU,ignorePeriod)
			
			skipStatementsGotoGoback(PU,ignorePeriod)
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)

			if lineDict["return statement"]:
				programObj.append(tempObj)
				tempObj = False
				if lineDict["."] and not ignorePeriod:
					break
		
		#exec nodes
		if lineDict["exec"]:
			execBlock = [inputLine]
			while "end-exec" not in inputLine:
				inputLine = PU.getNextStatement()
				execBlock.append(inputLine)
				
			execDict = digestExecBlock(execBlock)
			#add the exec block node
			programObj.append(nodes.ExecNode(PU,lineDict["type"]))

		
		#check chart end
		if lineDict["return statement"]:
			if not (lineDict["."] and ignorePeriod):
				break
		
		#branching statement
		if lineDict["if"]:
			tempObj = nodes.IfNode(PU,lineDict["if"])
			
			subChart = createChart(PU)
			tempObj.trueBranch = subChart
			
			skipStatementsGotoGoback(PU)
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			
			if lineDict["return statement"] in ["end-if","."]:
				programObj.append(tempObj)
				tempObj = False
				if lineDict["."] and not ignorePeriod:
					break
			
			
		if lineDict["else"]:
			subChart = createChart(PU)
			tempObj.falseBranch = subChart
			
			skipStatementsGotoGoback(PU)
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			
			if lineDict["return statement"] in ["end-if","."]:
				programObj.append(tempObj)
				tempObj = False
				if lineDict["."] and not ignorePeriod:
					break
			
			
		if lineDict["evaluate"]:
			tempObj = nodes.EvaluateNode(PU,lineDict["evaluate"])
		
		while lineDict["when"]:
			tempObj2 = nodes.WhenNode(lineDict["when"])
			while digestSentence(PU.peekNextStatement())["when"]:
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
				if lineDict["."] and not ignorePeriod:
					break
			
		
		if PU.paraReturn:
			break
	
	if tempObj:
		programObj.append(tempObj)

	return programObj
	
def skipStatementsGotoGoback(PU,ignorePeriod=False):
	inputLine = PU.peekCurrentStatement()
	lineDict = digestSentence(inputLine)
	while (not lineDict["."] or ignorePeriod) and (lineDict["go to"] or lineDict["goback"]):
		createChart(PU)
		inputLine = PU.peekCurrentStatement()
		lineDict = digestSentence(inputLine)
	
def getFieldValue(PU,field):
	if field[0] in ["'",'"'] or field.replace(".","").isdigit():
		return field

	for lineNo in reversed(PU.processedLines):
		processedLine = PU.peekStatement(lineNo)
		processedDict = digestSentence(processedLine)
		if processedDict["move"]:
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
	
	keyList = []
	keyList.extend(["para","if","else","end-if",".","evaluate","when","end-evaluate","call","go to"])
	keyList.extend(["perform","thru","until","end-perform","exec","end-exec","goback","return statement"])
	keyList.extend(["using","move","to"])
	for word in keyList:
		lineDict[word] = False
	
	lineDict[0] = words[0]
	lineDict[words[0]] = True
	if "." in words:
		lineDict["."] = True
		
	if inputLine[0] != " " and lineDict["."]:
		lineDict["para"] = words[0]	
	
	if lineDict["move"]:
		toPos = words.index("to")
		lineDict["move"] = words[toPos-1]
		lineDict["to"] = words[toPos+1:]
	
	if words[0] == "go" and words[1] == "to":
		lineDict["go to"] = words[2]
	
	if lineDict["call"]:
		lineDict["call"] = words[1]
		if "using" in words:
			usingPos = words.index("using")
			lineDict["using"] = []
			for word in words[usingPos+1:]:
				lineDict["using"].append(word)
	
	if lineDict["if"]:
		lineDict["if"] = " ".join(words[1:])
	
	if lineDict["evaluate"]:
		lineDict["evaluate"] = " ".join(words[1:])
	
	if lineDict["when"]:
		lineDict["when"] = " ".join(words[1:])
	
	if lineDict["perform"]:
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
		if lineDict[word]:
			lineDict["return statement"] = word
			break
	
	return lineDict
	
def digestExecBlock(inputBlock):
	execDict = {}
	inputLine = " ".join(inputBlock)
	words = inputLine.split()
	
	keyList = []
	keyList.extend(["type","call","goback","cursor","query","table","."])
	for dictKey in keyList:
		execDict[dictKey] = False

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
				cursorPos = words.index[cursorPreword] + 1
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

