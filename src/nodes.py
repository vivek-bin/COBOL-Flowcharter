import Tkinter
import constants as CONST

class Node:
	def __init__(self,PU,iconName=False):
		self.paraStack = PU.paraStack[:]
		self.lineNo = int(PU.inputFile.procedureDivisionLineNo[PU.processedLines[-1]]) + 1
		
		self.idleIcon = self.hoverIcon = self.clickIcon = False
		if iconName:
			if not self.idleIcon:
				self.idleIcon = iconName + "-idle"
			if not self.hoverIcon:
				self.hoverIcon = iconName + "-hover"
			if not self.clickIcon:
				self.clickIcon = iconName + "-click"
	
	def iconText(self):
		return ""
	
	def description(self):
		return ""
		
	def isEmpty(self):
		return False
		
	def width(self):
		return CONST.BRANCHWIDTH
		
class Branch(Node):
	def __init__(self,PU,iconName=False):
		Node.__init__(self,PU,iconName)
		self.branch = []
		
	def isEmpty(self):
		flag = True
		for n in self.branch:
			if not n.isEmpty():
				flag = False
				break
		return flag
	
	def width(self):
		w = 0
		for n in self.branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
		return w
		
class IfNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"branch")
		self.condition = operand
		self.branch = {}
		self.branch[True] = IfBranch(PU,True)
		self.branch[False] = IfBranch(PU,False)
		
	def isEmpty(self):
		return self.branch[True].isEmpty() or self.branch[False].isEmpty()	
		
	def width(self):
		return self.branch[True].width() + self.branch[False].width()
		
	def description(self):
		return "IF " + self.condition.upper()
		
class IfBranch(Branch):
	def __init__(self,PU,operand):
		Branch.__init__(self,PU,"info")
		self.condition = operand
		
	def description(self):
		return str(self.condition).upper()
			
	def width(self):
		w = Branch.width(self)
		if w > CONST.ICONWIDTH:
			return w
		else:
			return CONST.ICONWIDTH
	
class EvaluateNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"multi")
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
			
		return finalWidth
		
	def description(self):
		return "EVALUATE " + self.condition.upper()
	
class WhenBranch(Branch):
	def __init__(self,PU,operand):
		Branch.__init__(self,PU,"info")
		self.condition = [operand]
		
	def addCondition(self,operand):
		self.condition.append(operand)
		
	def description(self):
		condition = self.condition[0]
		for c in self.condition[1:]:
			condition += "\n" + c
			
		return "WHEN " + condition.upper()
		
	def width(self):
		w = Branch.width(self)
		if w > CONST.ICONWIDTH:
			return w
		else:
			return CONST.ICONWIDTH
	
class LoopBranch(Branch):
	def __init__(self,PU,operand):
		Branch.__init__(self,PU,"info")
		self.condition = operand
		
	def description(self):
		return self.condition.upper()
		
class NonLoopBranch(Branch):
	def __init__(self,PU):
		Branch.__init__(self,PU)
		
class GoToBranch(Branch):
	def __init__(self,PU,operand):
		Branch.__init__(self,PU,"process")
		self.link = operand
		
	def description(self):
		return "GO TO " + self.link.upper()
	
class ParaNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"info")
		self.paraName = operand
		
	def isEmpty(self):
		return True
		
	def description(self):
		return "PARA " + self.paraName.upper()
		
class CallNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"module")
		self.moduleName = operand
		self.moduleNameVariable = operand
	
	def iconText(self):
		return self.moduleName.upper()
		
	def description(self):
		return "double-click to open"
	
class ExecNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"db")
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
	
class EndNode(Node):
	def __init__(self,PU,operand=0):
		Node.__init__(self,PU,"start")
		self.errorEnd = operand
		
	def iconText(self):
		return "STOP"
			
class LoopBreakPointer(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"info")
		self.link = operand


