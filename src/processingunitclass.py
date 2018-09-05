import processingfileclass as pfc

class ProcessingUnit:
	def __init__(self,inputArg=False):
		self.performReturnStack = []
		self.performEndStack = []
		self.paraStack = [""]
		self.processedLines = []		#list of all lines processed
		self.programCounter = 0			#points to next sentence to be executed
		self.inputFile = []
		self.paraCall = False
		self.paraReturn = False
		self.paraBranches = {}

		if inputArg.__class__ is ProcessingUnit:
			self.performReturnStack = inputArg.performReturnStack[:]
			self.performEndStack = inputArg.performEndStack[:]
			self.paraStack = inputArg.paraStack[:]
			self.processedLines = inputArg.processedLines[:]
			self.programCounter = inputArg.programCounter - 0
			self.inputFile = inputArg.inputFile
			self.paraBranches = dict(inputArg.paraBranches)
		
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
				paraName = self.inputFile.paraEnd[self.processedLines[-1]]
				if paraName in self.performEndStack:
					poppedPara = False
					while poppedPara != paraName:
						poppedPara = self.performEndStack.pop()
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
		self.paraStack.append("")
		self.performReturnStack.append(self.processedLines[-1])
		self.performEndStack.append(performEnd)
		
		self.jumpToPara(performStart)
		
	def jumpToPara(self,paraName):
		self.programCounter = self.inputFile.paraStart[paraName]
		self.paraCall = True
	
	