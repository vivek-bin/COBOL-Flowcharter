import constants as CONST
import keywords
import processingfileclass as pfc
import nodes

class ProcessingUnit:
	def __init__(self,inputArg=False):
		self.performStartStack = []
		self.performEndStack = []
		self.programCounter = 0			#points to next sentence to be executed
		self.inputFile = []

		if type(inputArg) is ProcessingUnit:
			self.performStartStack = inputArg.performStartStack[:]
			self.performEndStack = inputArg.performEndStack[:]
			self.programCounter = inputArg.programCounter
			self.inputFile = inputArg.inputFile
		
		if type(inputArg) is ProgramProcessingFile:
			self.inputFile = inputArg

	def peekPreviousStatement(self):
		return self.inputFile[self.programCounter-2]
	
	def peekCurrentStatement(self):
		return self.inputFile[self.programCounter-1]
	
	def peekNextStatement(self):
		return self.inputFile[self.programCounter]
	
	def incrementProgramCounter(self):
		self.programCounter += 1
	
	def getNextStatement(self):
		self.incrementProgramCounter()
		return self.peekCurrentStatement()
	
	def pushStack(self,performStart,performEnd):
		self.performEndStack.append(performStart)
		self.performStartStack.append(performEnd)
	
	def atPerformReturn(self):
		#return self.programCounter in self.performEndStack:
	
	def isReturnPara(self,para):
		return para in self.performEndStack:
	
	def setPerformReturn(self):
		if self.atPerformReturn():
			#stackIndex = self.performEndStack.index(self.programCounter)
			#self.programCounter = self.performStartStack[stackIndex]
			
			stackDepth = len(self.performEndStack) - stackIndex
			for i in range(1,stackDepth):
				self.performEndStack.pop()
				self.performStartStack.pop()
			
			return True
		else:
			return False
	
	def stackSize():
		return len(self.performStartStack)
	
def createChart(PU):
	programObj = []
	tempObj = False
	
	lineCount = 0

	while True:
		inputLine = PU.getNextStatement()
		lineDict = digestSentence(inputLine)
		
		lineCount += 1
		
		
		if lineDict["exec"]:
			execBlock = [inputLine]
			while inputLine.find("end-exec") == -1:
				inputLine = PU.getNextStatement()
				execBlock.append(inputLine)
				
			execDict = digestExecBlock(execBlock)
			#add the exec block node
			continue

		
		if blockEndStatement(inputLine):
			if tempObj:
				programObj.append(tempObj)
				tempObj = False
			break
		
		if lineDict["if"]:
			tempObj = IfNode()
			
			subChart = createChart(PU)
			tempObj.trueBranch = subChart
			
			returnLineDict = digestSentence(PU.peekCurrentStatement())
			continue
			
		if lineDict["else"]:
			subChart = createChart(PU)
			continue
			
		if lineDict["evaluate"]:
			tempObj = EvaluateNode()
			continue
		
		if lineDict["when"]:
			subChart = createChart(PU)
			continue
			 
		if lineDict["perform"]:
			if lineDict["until"]:
				tempObj = LoopNode(lineDict["until"])
			else:
				tempObj = NonLoopNode()
			
			if type(lineDict["perform"]) is str:
				performStart = lineDict["perform"]
				performEnd = lineDict["perform"]
				if lineDict["thru"]:
					performEnd = lineDict["thru"]
				PU.pushStack(performStart,performEnd)
				
			subChart = createChart(PU)
				
			continue
		
			
	return programObj

	
def digestSentence(inputLine):
	lineDict = {}
	words = inputLine.replace("."," .").split()
	
	keyList = []
	keyList.extends(["if","else","end-if",".","evaluate","when","end-evaluate","call","go to"])
	keyList.extends(["perform","thru","until","end-perform","exec","end-exec","goback"])
	for dictKey in keyList:
		lineDict[dictKey] = False
	
	lineDict[0] = words[0]
	lineDict[words[0]] = True
	if "." in words:
		lineDict["."] = True
	
	
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
		if "thru" in words:
			thruPos = words.index("thru")
		if "through" in words:
			thruPos = words.index("through")
		if "varying" in words:
			varyingPos = words.index("varying")
		if "until" in words:
			untilPos = words.index("until")
		if "times" in words:
			timesPos = words.index("times")
		
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
	
	