import constants as CONST
import keywords
import processingfileclass as pfc
import nodes

class ProcessingUnit:
	def __init__(self,inputArg=False):
		self.performReturnStack = []
		self.performEndStack = []
		self.paraStack = []
		self.currentCounter = -1		#points to current sentence
		self.programCounter = 0			#points to next sentence to be executed
		self.inputFile = []
		self.paraReturn = False

		if type(inputArg) is ProcessingUnit:
			self.performReturnStack = inputArg.performReturnStack[:]
			self.performEndStack = inputArg.performEndStack[:]
			self.programCounter = inputArg.programCounter
			self.inputFile = inputArg.inputFile
		
		if type(inputArg) is ProgramProcessingFile:
			self.inputFile = inputArg

	def peekCurrentStatement(self):
		return self.inputFile[self.currentCounter]
	
	def peekNextStatement(self):
		return self.inputFile[self.programCounter]
	
	def incrementProgramCounter(self):
		self.paraReturn = False
		self.currentCounter = self.programCounter
		currentPara = self.inputFile.getCurrentPara(self.currentCounter)
		if self.inputFile.paraEnd[currentPara] == self.currentCounter and currentPara in self.performEndStack:
			self.setPerformReturn(currentPara)
			self.paraReturn = True
		else:
			self.programCounter += 1
	
	def getNextStatement(self):
		self.incrementProgramCounter()
		return self.peekCurrentStatement()
	
	def pushStack(self,performStart,performEnd):
		currentPara = self.inputFile.getCurrentPara(self.currentCounter)
		self.paraStack.append(self.currentPara)
		self.performReturnStack.append(self.programCounter)
		self.performEndStack.append(performEnd)
		
		self.programCounter = performStart

	def setPerformReturn(self,para):
		stackIndex = self.performEndStack.index(para)
		
		stackDepth = len(self.performEndStack) - stackIndex
		for i in range(1,stackDepth):
			self.performEndStack.pop()
			self.paraStack.pop()
			self.programCounter = self.performReturnStack.pop()

	
	def stackSize():
		return len(self.performEndStack)
	
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
			programObj.append(ParaNode(PU,lineDict["para"]))
		if lineDict["call"]:
			programObj.append(CallNode(PU,lineDict["call"]))
		if lineDict["goback"]:
			programObj.append(EndNode(PU,lineDict["goback"]))
		if lineDict["go to"]:
			programObj.append(GoToNode(PU,lineDict["go to"]))
		
		#perform nodes
		if lineDict["perform"]:
			if lineDict["until"]:
				tempObj = LoopNode(PU,lineDict["until"])
			else:
				tempObj = NonLoopNode(PU)
			
			if type(lineDict["perform"]) is str:
				performStart = lineDict["perform"]
				performEnd = lineDict["perform"]
				if lineDict["thru"]:
					performEnd = lineDict["thru"]
				PU.pushStack(performStart,performEnd)
				subChart = createChart(PU,True)
			else:
				subChart = createChart(PU)
			programObj.append(tempObj)
			tempObj = False
		
		#exec nodes
		if lineDict["exec"]:
			execBlock = [inputLine]
			while inputLine.find("end-exec") == -1:
				inputLine = PU.getNextStatement()
				execBlock.append(inputLine)
				
			execDict = digestExecBlock(execBlock)
			#add the exec block node
			programObj.append(ExecNode(PU,lineDict["type"]))

		
		#check chart end
		if lineDict["return statement"]:
			if lineDict["return statement"] != "." or not ignorePeriod:
				break
		
		#branching statement
		if lineDict["if"]:
			tempObj = IfNode(PU,lineDict["if"])
			
			subChart = createChart(PU)
			tempObj.trueBranch = subChart
			
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			while lineDict["return statement"] in ["go to","goback"]:
				createChart(PU)
			if lineDict["return statement"] in ["end-if","."]:
				programObj.append(tempObj)
				tempObj = False
			
			
		if lineDict["else"]:
			subChart = createChart(PU)
			tempObj.falseBranch = subChart
			
			returnLineDict = digestSentence(PU.peekCurrentStatement())
			programObj.append(tempObj)
			tempObj = False
			
			
		if lineDict["evaluate"]:
			tempObj = EvaluateNode(PU,lineDict["evaluate"])
			
		
		if lineDict["when"]:
			tempObj2 = WhenNode(lineDict["when"])
			while digestSentence(PU.peekNextStatement())["when"]:
				inputLine = PU.getNextStatement()
				lineDict = digestSentence(inputLine)
				tempObj2.addCondition(lineDict["when"])
			
			subChart = createChart(PU)
			tempObj2.branch = subChart
			tempObj.whenList.append(tempObj2)
			
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			if lineDict["return statement"] in ["end-evaluate","."]:
				programObj.append(tempObj)
				tempObj = False
			
		
		if PU.paraReturn:
			break
	
	if tempObj:
		programObj.append(tempObj)

	return programObj
	
def digestSentence(inputLine):
	lineDict = {}
	words = inputLine.replace("."," .").split()
	
	keyList = []
	keyList.extends(["para","if","else","end-if",".","evaluate","when","end-evaluate","call","go to"])
	keyList.extends(["perform","thru","until","end-perform","exec","end-exec","goback","return statement"])
	for dictKey in keyList:
		lineDict[dictKey] = False
	
	lineDict[0] = words[0]
	lineDict[words[0]] = True
	if "." in words:
		lineDict["."] = True
		
	if inputLine[0] != " " and lineDict["."]:
		lineDict["para"] = words[0]	
	
	if words[0] = "go" and words[1] = "to":
		lineDict["go to"] = words[2]
	
	if lineDict["call"]:
		lineDict["call"] = words[1]
	
	
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
	
	if words[0] = "stop" and words[1] = "run":
		lineDict["goback"] = True
	if words[0] = "exit" and words[1] = "program":
		lineDict["goback"] = True
	
	for word in ["end-if","end-evaluate","end-perform","when","else","go to",".","goback"]:
		if lineDict[word]:
			lineDict["return statement"] = word
			break
	
	return lineDict
	
def digestExecBlock(inputBlock):
	execDict = {}
	inputLine = " ".join(inputBlock)
	words = inputLine.split()
	
	keyList = []
	keyList.extends(["type","call","goback","cursor","query","table"])
	for dictKey in keyList:
		execDict[dictKey] = False

	execDict["type"] = words[1]
	
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
				cursorPos = words.index[declare] + 1
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

