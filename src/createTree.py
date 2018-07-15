import constants as CONST
import keywords
import processingfileclass as pfc

class ProgramSequence:
	def __init__(self):
		self.flow = []
	
class IfBranch:
	def __init__(self):
		self.trueBranch = ProgramSequence()
		self.falseBranch = ProgramSequence()

class EvaluateBranch:
	def __init__(self):
		self.branchList = []
	
class LoopSequence:
	def __init__(self):
		self.loopFlow = ProgramSequence()
	
class NonLoopSequence:
	def __init__(self):
		self.flow = ProgramSequence()
	
class CallNode:
	def __init__(self):
		self.moduleName = ""
	
class GoToLink:
	def __init__(self):
		self.link = ""
	
class EndNode:
	def __init__(self):
		self.errorEnd = 0

class Processing:
	def __init__(self,inputFile):
		self.performStartStack = []
		self.performEndStack = []
		self.inputFile = inputFile
		self.programCounter = 0
		self.statementStack = []
	
	def isPerformEnd(self,lineNo):
		if lineNo in self.performEndStack:
			return True
		else:
			return False
	
	def setPerformEnd(self,lineNo):
		if lineNo in self.performEndStack:
			stackIndex = self.performEndStack.index(lineNo)
			self.programCounter = self.performStartStack[stackIndex]
			
			stackDepth = len(self.performEndStack) - stackIndex
			for i in range(1,stackDepth):
				self.performEndStack.pop()
				self.performStartStack.pop()
			
			return True
		else:
			return False
	
	def performStackSize():
		return len(self.performStartStack)
	
def createChart(inputFile,lineNo):
	programObj = []
	tempObj = False
	lineNo = lineCount = 0
	while True:
		inputLine = inputFile[lineNo]
		words = inputLine.replace("."," .").split()
		keyWords = keywords.extractKeywords(inputLine)
		nonKeyWords = keywords.extractNonKeywords(inputLine)
		lineNo += 1
		lineCount += 1
		
		if blockEndStatement(inputLine):
			if tempObj:
				programObj.append(tempObj)
				tempObj = False
			break
		
		if keyWords[0] = 'if':
			tempObj = IfBranch()
			tempObj.trueBranch.flow = createChart(inputFile,lineNo)[:-1]
			continue
			
		if keyWords[0] = 'perform':
			thruFlag = False
			untilFlag = False
			
			if keyWords[1] = "thru":
				performStartStack.append(lineNo-1)
				lineNo = inputFile.paraStart[paraName]
				thruFlag = True
			if "until" in keyWords or "times" in keyWords:
				tempObj = LoopSequence()
				untilFlag = True
			
			if untilFlag:
				if thruFlag:
					tempObj.loopFlow.flow = createChart(inputFile,lineNo)[:-1]
				else:
					
			else:
			
			
			
			continue
		
		if keyWords[0] = 'else':
			tempObj.falseBranch.flow = createChart(inputFile,lineNo)[:-1]
			continue
		
		if keyWords[0] = 'evaluate':
			tempObj = EvaluateBranch()
			continue
		
		if keyWords[0] = 'when':
			tempObj.branchList.append(createChart(inputFile,lineNo)[:-1])
			continue
			
		
		temp = specialStatement(inputLine)
		if temp:
			programObj.append(temp)
			
	return programObj, lineNo
