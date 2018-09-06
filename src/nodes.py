import constants as CONST

class Node:
	iconWidth = 0
	iconHeight = 0
	iconName = False
	def __init__(self,PU):
		self.paraStack = PU.paraStack[:]
		self.lineNo = int(PU.inputFile.procedureDivisionLineNo[PU.processedLines[-1]]) + 1
		self.empty = False
		self.tags = ["ButtonIcon","JumpToLine","HasDetails"]
	
	def idleIcon(self):
		if self.iconName:
			return self.iconName + "-idle"
		else:
			return False
	
	def hoverIcon(self):
		if self.iconName:
			return self.iconName + "-hover"
		else:
			return False
	
	def clickIcon(self):
		if self.iconName:
			return self.iconName + "-click"
		else:
			return False
	
	def iconText(self):
		return ""
	
	def description(self):
		return ""
		
	def isEmpty(self):
		return self.empty
		
	def width(self):
		return self.iconWidth
		
	def height(self):
		return self.iconHeight
		
class Branch(Node):
	def __init__(self,PU):
		Node.__init__(self,PU)
		self.branch = []
		
	def isEmpty(self):
		flag = True
		for n in self.branch:
			if not n.isEmpty():
				flag = False
				break
		return flag
	
	def width(self):
		w = self.iconWidth
		for n in self.branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
		if w:
			return w + CONST.BRANCHSPACE/2
		else:
			return w
			
	def nodeHeight(self):
		return Node.height(self)
			
	def nodeWidth(self):
		return Node.width(self)
		
class IfNode(Node):
	iconName = "branch"
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.branch = {}
		self.branch[True] = IfBranch(PU,True)
		self.branch[False] = IfBranch(PU,False)
		
	def isEmpty(self):
		return self.branch[True].isEmpty() and self.branch[False].isEmpty()	
		
	def width(self):
		trueWidth = self.branch[True].width()
		falseWidth = self.branch[False].width()
		
		if Node.width(self) > trueWidth + falseWidth:
			return Node.width(self)
		else:
			return trueWidth + falseWidth
		
	def description(self):
		return "IF " + self.condition.upper()
		
class IfBranch(Branch):
	def __init__(self,PU,operand):
		Branch.__init__(self,PU)
		self.condition = operand
		
	def description(self):
		return str(self.condition).upper()
			
class EvaluateNode(Node):
	iconName = "branch"
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.whenList = []
		
	def isEmpty(self):
		flag = True
		for n in self.whenList:
			if not n.isEmpty():
				flag = False
				break
		return flag
		
	def width(self):
		finalWidth = 0
		for whenBranch in self.whenList:
			finalWidth += whenBranch.width()
		
		if Node.width(self) > finalWidth:
			return Node.width(self)
		else:
			return finalWidth
		
	def description(self):
		return "EVALUATE " + self.condition.upper()
	
class WhenBranch(Branch):
	def __init__(self,PU,operand):
		Branch.__init__(self,PU)
		self.condition = [operand]
		
	def addCondition(self,operand):
		self.condition.append(operand)
		
	def description(self):
		condition = self.condition[0]
		for c in self.condition[1:]:
			condition += "\n" + c
			
		return "WHEN " + condition.upper()
		
class LoopBranch(Branch):
	iconName = "loop"
	def __init__(self,PU,operand):
		Branch.__init__(self,PU)
		self.condition = operand
		
	def width(self):
		return Branch.width(self) + CONST.BRANCHSPACE
		
	def description(self):
		return self.condition.upper()
		
class NonLoopBranch(Branch):
	def __init__(self,PU):
		Branch.__init__(self,PU)
	
class PerformNode(Node):
	iconName = "process"
	def __init__(self,PU,operand,endingPara=False):
		Node.__init__(self,PU)
		self.empty = True
		self.para = operand
		self.endingPara = endingPara
		
	def iconText(self):
		return self.para.upper()
		
	def description(self):
		return "*COMMON PARA*"
	
class GoToBranch(Branch):
	iconName = "process"
	def __init__(self,PU,operand):
		Branch.__init__(self,PU)
		self.link = operand
		
	def description(self):
		return "GO TO " + self.link.upper()
	
class ParaNode(Node):
	iconName = "info"
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.empty = True
		self.paraName = operand
	
	def description(self):
		return self.paraName.upper() + "."
		
class CallNode(Node):
	iconName = "module"
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.tags.append("CalledProgram")
		self.moduleName = operand
		self.moduleNameVariable = operand
		self.dynamicCall = False
	
	def setCalledProgram(self,programName):
		self.moduleName = programName
	
	def iconText(self):
		return self.moduleName.upper()
		
	def description(self):
		return "double-click to open"
	
class ExecNode(Node):
	iconName = "db"
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.type = operand
		self.table = ""
		self.cursor = ""
		self.query = ""
	
	
	def iconText(self):
		if self.table:
			return self.table.upper()
		elif self.cursor:
			return self.cursor.upper()
		else:
			return"TABLE"
		
	def description(self):
		l = ""
		if self.table:
			l += "TABLE: " + self.table.upper() + "\n"
		if self.cursor:
			l += "CURSOR: " + self.cursor.upper() + "\n"
		if self.query:
			l += "QUERY: " + self.query.upper() + "\n"
		l = l[:-1]
		return l
	
class FileNode(Node):
	iconName = "file"
	def __init__(self,PU,statement,file):
		Node.__init__(self,PU)
		self.statement = statement
		self.file = file
	
	def iconText(self):
		return self.file.upper()
		
	def description(self):
		return self.statement.upper() + " " + self.file.upper()
	
class EndNode(Node):
	iconName = "start"
	def __init__(self,PU,operand=0):
		Node.__init__(self,PU)
		self.errorEnd = operand
		
	def iconText(self):
		return "STOP"
			
class LoopBreakPointer(Node):
	iconName = "info"
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.link = operand


