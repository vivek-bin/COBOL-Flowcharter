import constants as CONST

class ProgramProcessingFile:
	def loadFile(self,inputFileName):
		try:
			iFile = open(CONST.PROCESSING+inputFileName+".txt")
			self.inputFile = [l.rstrip() for l in iFile]
			iFile.close()
		except IOError:
			self.inputFile = []

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
				
		paraDeclarations = {v:k for k,v in self.paraStart.items()}
		
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
	
	def __init__(self,inputFile=[]):
		self.inputFile = []
		self.identificationDivision = []
		self.environmentDivision = []
		self.dataDivision = []
		self.procedureDivision = []
		self.paraStart = {}
		self.paraEnd = {}
		
		if type(inputFile) == type(""):
			self.loadFile(inputFile)
		else:
			self.inputFile = inputFile 
			
		self.setDivisions()
		self.setParaDictionary()
	