import constants as CONST

class ProgramProcessingFile:
	def searchFile(self,search,fromPos=0):
		i = fromPos
		for inputLine in self.inputFile[fromPos:]:
			if search in inputLine:
				return i
			i += 1
		return -1
		
	def searchAllFile(self,search):
		i = 0
		li = []
		for inputLine in self.inputFile:
			if search in inputLine:
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
		else:
			j = self.searchFile("data division")
			self.environmentDivision = self.inputFile[i+1:j]
		
	def setDataDivision(self):
		i = self.searchFile("data division")
		j = self.searchFile("procedure division")
		self.dataDivision = self.inputFile[i+1:j]
		
	def setProcedureDivision(self):
		i = self.searchFile("procedure division")
		j = self.searchFile("id division",i)
		if j == -1:
			j = self.searchFile("identification division",i)
		
		if j == -1:		
			self.procedureDivision = self.inputFile[i+1:]
			self.procedureDivisionLineNo = self.inputFileLineNo[i+1:]
		else:
			self.procedureDivision = self.inputFile[i+1:j]
			self.procedureDivisionLineNo = self.inputFileLineNo[i+1:j]
			
			eraseLines = []
			lineNo = j
			while lineNo < len(self.inputFile):
				subProg = []
				while lineNo < len(self.inputFile):
					eraseLines.append(lineNo)
					subProg.append(self.inputFileLineNo[lineNo] + self.inputFile[lineNo])
					lineNo += 1
					if self.inputFile[lineNo-1].startswith("end program"):
						break
				self.subProgram.append(ProgramProcessingFile(subProg))
				
				while lineNo < len(self.inputFile):
					if self.inputFile[lineNo].startswith("id division") or self.inputFile[lineNo].startswith("identification division"):
						break
					self.procedureDivision.append(self.inputFile[lineNo])
					self.procedureDivisionLineNo.append(self.inputFileLineNo[lineNo])
					lineNo += 1
					
			for lineNo in eraseLines[::-1]:
				del self.inputFile[lineNo]
				del self.inputFileLineNo[lineNo]
	
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
		
		temp = sorted(paraDeclarations.keys())
		prevLineNo = temp[0]
		for lineNo in temp[1:]:
			self.paraEnd[paraDeclarations[prevLineNo]] = lineNo - 1
			prevLineNo = lineNo
		self.paraEnd[paraDeclarations[prevLineNo]] = len(self.procedureDivision) - 1
		
		self.paraEnd = {v:k for k,v in self.paraEnd.items()}
		
	def getCurrentPara(self,lineNo):
		paraDeclarations = {v:k for k,v in self.paraStart.items()}
		
		for i in sorted(paraDeclarations.keys(),reverse=True):
			if i <= lineNo:
				return paraDeclarations[i]
		return ""
	
	def __init__(self,inputFile):
		self.inputFile = []
		self.inputFileLineNo = []
		self.identificationDivision = []
		self.environmentDivision = []
		self.dataDivision = []
		self.procedureDivision = []
		self.procedureDivisionLineNo = []
		self.paraStart = {}
		self.paraEnd = {}
		self.subProgram = []
		
		if inputFile:
			self.inputFile = inputFile 
		
			self.inputFileLineNo = [inputLine[:CONST.ZEROPAD] for inputLine in self.inputFile]
			self.inputFile = [inputLine[CONST.ZEROPAD:] for inputLine in self.inputFile]
			
			self.setDivisions()
			self.setParaDictionary()
	