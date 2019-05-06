import constants as CONST
import keywords
import processingfileclass as pfc
import nodes
import fileaccess
from processingunitclass import ProcessingUnit

import sys
import time

depthcount = 0
	
def createChart(PU,ignorePeriod=False):
	programObj = []
	tempObj = False
	global depthcount
	lineCount = 0
	depthcount += 1
	#try:
	#	fileaccess.writeLOG("start:" + str(depthcount)+ "      " + str(PU.processedLines[-1])+ "      " + str(PU.inputFile.procedureDivision[PU.processedLines[-1]]))
	#except IndexError:
	#	fileaccess.writeLOG("start:index error")
	
	while True:
		inputLine = PU.getNextStatement()
		lineDict = digestSentence(inputLine)
	#	fileaccess.writeLOG(str(PU.processedLines[-1]).ljust(8) + "    " + str(inputLine))
		if PU.paraReturn:
			break
			
		#;)
		#if depthcount > 15:
		#	break
		
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
				lineDict["return statement"] = "goback"
				
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
			PU.paraStack[-1] = lineDict["para"]
			programObj.append(nodes.ParaNode(PU,lineDict["para"]))
		if "file" in lineDict:
			statement = lineDict["file"]
			programObj.append(nodes.FileNode(PU,statement,lineDict[statement]))
		if "call" in lineDict:
			calledProgram = getFieldValue(PU,lineDict["call"])
			if calledProgram == "'dfhei1'":
				if len(lineDict["using"]) == 1:
					lineDict["goback"] = True
					calledProgram = ""
				else:
					calledProgram = getFieldValue(PU,lineDict["using"][1])
			
			if calledProgram:
				calledProgram = calledProgram[1:-1].strip().lower()
				if calledProgram not in CONST.IGNOREDMODULES:
					tempObj = nodes.CallNode(PU,calledProgram)
					if not isValue(lineDict["call"]) or lineDict["call"] == "'dfhei1'":
						tempObj.dynamicCall = True
					programObj.append(tempObj)
					tempObj = False
		
		#returnable statements
		if "goback" in lineDict:
			programObj.append(nodes.EndNode(PU,lineDict["goback"]))
		if "go to" in lineDict:
			if "depending" in lineDict:
				tempObj = nodes.EvaluateNode(PU,lineDict["depending"])
				tempObj.whenList.append(nodes.WhenBranch(PU,"other"))
				for i,goToPara in enumerate(lineDict["go to"]):
					tempObj2 = nodes.WhenBranch(PU,str(i+1))
					tempObj3 = nodes.GoToBranch(PU,goToPara)
					if goToPara not in (PU.paraStack + PU.performEndStack):
						goToPU = ProcessingUnit(PU)
						goToPU.jumpToPara(goToPara)
					#	subChart = createChart(goToPU,True)
					#	tempObj3.branch = subChart
					tempObj2.branch.append(tempObj3)
					tempObj.whenList.append(tempObj2)
			else:
				tempObj = nodes.GoToBranch(PU,lineDict["go to"])
				if lineDict["go to"] not in (PU.paraStack + PU.performEndStack):
					goToPU = ProcessingUnit(PU)
					goToPU.jumpToPara(lineDict["go to"])
				#	subChart = createChart(goToPU,True)
				#	tempObj.branch = subChart
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
			
			expandPara = True
			includePara = True
			ignorePeriodSub = True
			if lineDict["perform"] is not True:
				performEnd = performStart = lineDict["perform"]
				if "thru" in lineDict:
					performEnd = lineDict["thru"]
				
				if performStart in PU.paraStack:
					expandPara = False
					programObj.append(nodes.LoopBreakPointer(PU,performStart))
				elif performStart in CONST.IGNOREDPARAS:
					includePara = False
					programObj.append(nodes.PerformNode(PU,performStart))
					
			else:				#inline perform
				ignorePeriodSub = False
			
			if expandPara:
				fastforwardRequired = True
				if ignorePeriodSub:				#performing a PARA, so check if already created
					dictKey = (performStart,performEnd)
					if dictKey not in PU.paraBranches:
						PU.pushStack(performStart,performEnd)
						subChart = createChart(PU,ignorePeriodSub)
						if not containsDynamicCall(subChart):
							PU.paraBranches[dictKey] = subChart
					else:
						fastforwardRequired = False
						subChart = PU.paraBranches[dictKey]
				else:
					subChart = createChart(PU,ignorePeriodSub)
					
				if includePara:
					tempObj.branch = subChart
					programObj.append(tempObj)
				tempObj = False
				
				if not includePara:
					if isTerminatedBranch(subChart):
						programObj.append(isTerminatedBranch(subChart))
				
				if fastforwardRequired:
					while isTerminatedBranch(subChart):
						subChart = createChart(PU,ignorePeriodSub)
					
				if isTerminatedBranch(programObj):
					break
					
				inputLine = PU.peekCurrentStatement()
				lineDict = digestSentence(inputLine)
			
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
			
			tempObj2 = nodes.IfBranch(PU,ifCondition)
			subChart = createChart(PU)
			tempObj2.branch = subChart
			tempObj.branch[ifCondition] = tempObj2
			
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			
			while isTerminatedBranch(subChart) and ("." not in lineDict):
				subChart = createChart(PU)
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
				while isTerminatedBranch(subChart) and ("." not in lineDict):
					subChart = createChart(PU)
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
					
		if "search" in lineDict:
			createChart(PU)
			inputLine = PU.peekCurrentStatement()
			lineDict = digestSentence(inputLine)
			if "when" in lineDict:
				createChart(PU)
				inputLine = PU.peekCurrentStatement()
				lineDict = digestSentence(inputLine)
				
	
	if tempObj:
		programObj.append(tempObj)
	
	depthcount -= 1
	
	#try:
	#	fileaccess.writeLOG("end:" + str(depthcount)+ "      " + str(PU.processedLines[-1])+ "      " + str(PU.inputFile.procedureDivision[PU.processedLines[-1]]))
	#except IndexError:
	#	fileaccess.writeLOG("end:index error")
	
	
	return programObj
	
def getFieldValue(PU,field):
	if not isValue(field):
		field = getMovedFieldValue(PU,field)
	
	#get initial value(string in quotes,number) if not MOVE'd
	if not isValue(field):
		field = getDefinedValue(PU,field)

	return field
	
def getMovedFieldValue(PU,field):
	if not isValue(field):
		i=0
		for lineNo in reversed(PU.processedLines):
			i+=1
			if i>500:
				break
			processedLine = PU.peekStatement(lineNo)
			
			if not processedLine.strip().startswith("move "):
				continue
			processedDict = digestSentence(processedLine)
			if "move" in processedDict:
				if field in processedDict["to"]:
					i=0
					field = processedDict["move"]
					if isValue(field):
						break

	return field
	
def getDefinedValue(PU,field):		
	field = " " + field + " "
	fieldFound = False
	for inputLine in PU.inputFile.dataDivision:
		if field in inputLine:
			if " value " in inputLine:
				valuePos = inputLine.find(" value ") + len(" value ")
				field = inputLine[valuePos:-1].strip()
				fieldFound = True
			break
	
	if not fieldFound:
		print("field not found: "+field)
			
	return field

def isValue(field):
	numericField = field.replace(".","").replace("-","").replace("+","")
	return field[0] in ["'",'"'] or numericField.isdigit()
	
def isTerminatedBranch(branch):
	if not branch:
		return False
	
	node = branch[-1]
	
	if node.__class__ is nodes.GoToBranch or node.__class__ is nodes.EndNode:
		return node
		
	if node.__class__ is nodes.LoopBranch or node.__class__ is nodes.NonLoopBranch:
		return isTerminatedBranch(node.branch)
	
def containsDynamicCall(branch):
	for node in branch:
		if node.__class__ is nodes.CallNode and node.dynamicCall:
			return True
		
		if node.__class__ is nodes.IfNode:
			if containsDynamicCall(node.branch[True].branch):
				return True
			if containsDynamicCall(node.branch[False].branch):
				return True

		if node.__class__ is nodes.EvaluateNode:
			for whenBranch in node.whenList:
				if containsDynamicCall(whenBranch.branch):
					return True
		
		if node.__class__ is nodes.LoopBranch or node.__class__ is nodes.NonLoopBranch or node.__class__ is nodes.GoToBranch:
			if containsDynamicCall(node.branch):
				return True
	
	return False
	
def digestSentence(inputLine):
	lineDict = {}
	#dont split quoted text into strings
	if "'" in inputLine or '"' in inputLine:
		singleQuotePos = inputLine.find("'")
		doubleQuotePos = inputLine.find('"')
		if singleQuotePos == -1:
			quoteType = '"'
		elif doubleQuotePos == -1:
			quoteType = "'"
		elif doubleQuotePos > singleQuotePos:
			quoteType = "'"
		else:
			quoteType = '"'
		
		quotePos = [i for i,c in enumerate(inputLine) if c == quoteType]
		while quotePos:
			for i in range(quotePos[0],quotePos[1]):
				if inputLine[i] == " ":
					inputLine = inputLine[:i] + chr(0) + inputLine[i+1:]
			quotePos.pop()
			quotePos.pop()
		
	words = inputLine.replace("."," .").split()
	inputLine = inputLine.replace(chr(0)," ")
	words = [word.replace(chr(0)," ") for word in words]
	
	
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
		if "depending" in words:
			dependingPos = words.index("depending")
			lineDict["go to"] = words[2:dependingPos]
			lineDict["depending"] = words[-1]
		else:
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
	
	
	for word in ["end-if","end-evaluate","end-perform","end-search","else","when","go to","goback","."]:
		if word in lineDict:
			if not (word == "go to" and "depending" in lineDict):
				lineDict["return statement"] = word
				break
	
	return lineDict
	
def digestExecBlock(inputBlock):
	execDict = {}
	inputLine = " ".join(inputBlock)
	words = inputLine.split()

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
		if "from" in words:
			execDict["table"] = words[words.index("from")+1]
		elif "update" in words:
			execDict["table"] = words[words.index("update")+1]
		elif "insert" in words:
			execDict["table"] = words[words.index("into")+1]
		
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
				break
				
	return execDict

def generateChart(file):
	fChart = []
	
	processingFile = pfc.ProgramProcessingFile(file)
	PU = ProcessingUnit(processingFile)
	fChart = createChart(PU,True)
	
	return PU, fChart
	
def getChart(component):
	PU = False
	fChart = []
	
	fileaccess.openLib(fileaccess.PROCESSING)
	fileList = fileaccess.fileListLib(fileaccess.PROCESSING)
	fileaccess.writeDATA("log")
	file = fileaccess.loadFile(fileaccess.PROCESSING,component)
	#file = fileaccess.loadDATA("test")
	if file:
		PU, fChart = generateChart(file)
	#	fileaccess.writePickle(component,fChart)
	#fChart = fileaccess.loadPickle(component)
	
	fileaccess.closeLib(fileaccess.PROCESSING)
	
	return fChart
	
def writeAllCharts(start=0,end=99):
	startTime = time.time()
	
	fileaccess.openLib(fileaccess.PROCESSING)
	
	l = fileaccess.fileListLib(fileaccess.PROCESSING)
	processingList = l[start:end]
	
	for fileName in processingList:
		print(fileName)
		src = fileaccess.loadFile(fileaccess.PROCESSING,fileName)
		PU, fChart = generateChart(src)
		fileaccess.writePickle(fileName,fChart)
	
	fileaccess.closeLib(fileaccess.PROCESSING)


	print(time.time() - startTime)


if __name__ == "__main__":
	writeAllCharts()

	
	