PATH = "D:\\Profiles\\vbindal\\Documents\\CAAGIS flow track\\"
PROCESSING = PATH + "MTP\\PROCESSING\\"
DATA = PATH + "data\\"

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
	
class KeyWords:
	cobolKeyWords = getCobolKeywords()
	#cobolEndKeyWords = getCobolEndKeywords()
	additionalEndLines = []
	
	def loadDATA(self,inputFileName):
		f = []
		try:
			iFile = open(DATA+inputFileName+".txt")

			f = [l[:72].rstrip() for l in iFile]
			iFile.close()
		except IOError:
			f = []
		return f
	
	def getCobolKeywords(self):
		return loadDATA("Keywords")
		
	def getCobolEndKeywords(self):
		return loadDATA("EndKeywords")
	
	def extractKeywords(self,inputLine):
		if inputLine[-1] == ".":
			inputLine = inputLine[:-1]
		words = inputLine.split()
		keyWords = [w for w in words if w in KeyWords.cobolKeywords]
		return keyWords
		
	def extractNonKeywords(self,inputLine):
		if inputLine[-1] == ".":
			inputLine = inputLine[:-1]
		words = inputLine.split()
		keyWords = [w for w in words if w not in KeyWords.cobolKeywords]
		return keyWords
		
	def isKeyword(self,word):
		if word in KeyWords.cobolKeywords:
			return True
		else:
			return False

class InputFile:
	def loadFile(self,inputFileName,lib):
		try:
			iFile = open(lib+inputFileName+".txt")
			if lib not in (PROCESSING,DATA):
				self.inputFile = [l[:72].rstrip() for l in iFile]
			else
				self.inputFile = [l.rstrip() for l in iFile]
			
			iFile.close()
		except IOError:
			self.inputFile = []

	def writeFile(self,outputFileName,lib):
		try:
			oFile = open(lib+outputFileName+".txt","w")
			oFile.writelines( "%s\n" % row for row in self.inputFile)
			oFile.close()
		except IOError:
			print ("couldnt write file")
		
	def searchFile(self,search):
		i = 0
		for inputLine in self.inputFile:
			if inputLine.find(search) != -1:
				return i
			i += 1
		return -1
		
	def searchAllFile(self,search):
		i = 0
		li = []
		for inputLine in self.inputFile:
			if inputLine.find(search) != -1:
				li.append(i)
			i += 1
		return li

	def setIdentificationDivision(self):
		j = self.searchFile("environment division")
		if j == -1:
			j = self.searchFile("data division")
		self.identificationDivision = self.inputFile[1:j]
		
	def setEnvironmentDivision(self):
		i = self.searchFile("environment division")
		if i == -1:
			self.environmentDivision = []
		j = self.searchFile("data division")
		self.environmentDivision = self.inputFile[i+1:j]
		
	def setDataDivision(self):
		i = self.searchFile("data division")
		j = self.searchFile("procedure division")
		self.dataDivision = self.inputFile[i+1:j]
		
	def setProcedureDivision(self):
		i = self.searchFile("procedure division")
		self.procedureDivision = self.inputFile[i+1:]
	
	def setDivisions(self):
		self.setIdentificationDivision()
		self.setEnvironmentDivision()
		self.setDataDivision()
		self.setProcedureDivision()
	
	def setParaDictionary(self):
		for i, inputLine in enumerate(self.procedureDivision):
			if inputLine[0] != " ":
				self.paraStart[inputLine.replace(".","")] = i
				
		paraDeclarations = {v:k for k,v in self.paraPosition.items()}
		
		temp = sorted(paraDeclarations.keys)
		prevLineNo = temp[0]
		for lineNo in temp[1:]:
			self.paraEnd[paraDeclarations[prevLineNo]] = lineNo - 1
			prevLineNo = lineNo
		self.paraEnd[paraDeclarations[prevLineNo]] = len(self.procedureDivision) - 1
		
	def getCurrentPara(self,lineNo):
		paraDeclarations = {v:k for k,v in self.paraPosition.items()}
		
		for i in sorted(paraDeclarations.keys(),reverse=True):
			if i <= lineNo:
				return paraDeclarations[i]
		return ""
	
	def __init__(self,inputFile,lib=""):
		self.inputFile = []
		self.identificationDivision = []
		self.environmentDivision = []
		self.dataDivision = []
		self.procedureDivision = []
		self.paraStart = {}
		self.paraEnd = {}
		
		self.lib = lib
		if lib:
			self.loadFile(inputFile,lib)
		else:
			self.inputFile = inputFile 
			
		self.setDivisions()
		self.setParaDictionary()
	
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
	lineCount = 0
	while True:
		inputLine = inputFile[lineNo]
		lineNo += 1
		lineCount += 1
		keyWords = extractKeywords(inputLine)
		nonKeyWords = extractNonKeywords(inputLine)
		if blockEndStatement(inputLine):
			if tempObj:
				programObj.append(tempObj)
				tempObj = False
			else:
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
			if "until" in keyWords:
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
			
	return programObj + [lineNo]
			
	
def t1():
	import os
	import time
	startTime = time.time()
	l=os.listdir(PROCESSING)
	l1=[li.rstrip(".txt") for li in l] 
	l2=l1[:1000]
	foundKeywords = {}
	for component in l1:
		inputFile = getProcedureDivision(loadFile(component,PROCESSING))
		for inputLine in inputFile:
			kywrds = extractKeywords(inputLine)
			for w in kywrds:
				try:
					foundKeywords[w] += 1
				except:
					foundKeywords[w] = 1
	writeFile("found_kywrds",PATH,foundKeywords.keys())
	print (time.time() - startTime)

cobolKeywords = getCobolKeywords()
t1()