import tkinter
import constants as CONST

class Node:
	idleIcon = False
	hoverIcon = False
	clickIcon = False
	def __init__(self,PU,iconName=False):
		self.paraStack = PU.paraStack[:]
		self.lineNo = PU.programCounter
		if iconName:
			self.loadIcons(iconName)
	
	def loadIcons(self,iconName):
		if not idleIcon:
			idleIcon = tkinter.PhotoImage(file=CONST.ICONS + iconName +"-idle.png")
		if not hoverIcon:
			hoverIcon = tkinter.PhotoImage(file=CONST.ICONS + iconName +"-hover.png")
		if not clickIcon:
			clickIcon = tkinter.PhotoImage(file=CONST.ICONS + iconName +"-click.png")
	
	def iconText(self):
		return ""
	
	def description(self):
		return ""
		
	def isEmpty(self):
		return False
		
	def width(self):
		return CONST.BRANCHWIDTH
		
class IfNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"branch")
		self.condition = operand
		self.branch = {}
		self.branch[True] = []
		self.branch[False] = []
		
	def isEmpty(self):
		flag = True
		for n in self.branch[True]:
			if not n.isEmpty():
				flag = False
		for n in self.branch[False]:
			if not n.isEmpty():
				flag = False
		return flag	
		
	def trueWidth(self):
		width = 0
		for n in branch[True]:
			tempWidth = n.width()
			if tempWidth > width:
				width = tempWidth
		
		return width
		
	def falseWidth(self):
		width = 0
		for n in branch[False]:
			tempWidth = n.width()
			if tempWidth > width:
				width = tempWidth
		
		return width
		
	def width(self):
		return trueWidth(self) + falseWidth(self)

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
		return flag
		
	def width(self):
		finalWidth = 0
		for whenBranch in whenList:
			finalWidth += whenBranch.width()
			
		return finalWidth
	
class WhenNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"info")
		self.condition = [operand]
		self.branch = []
		
	def addCondition(self,operand):
		self.condition.append(operand)
		
	def isEmpty(self):
		flag = True
		for n in self.branch:
			if not n.isEmpty():
				flag = False
		return flag
	
	def width(self):
		w = 0
		for n in branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
		return w
	
class LoopNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.branch = []
		
	def isEmpty(self):
		flag = True
		for n in self.branch:
			if not n.isEmpty():
				flag = False
		return flag
		
	
	def width(self):
		w = 0
		for n in branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
		return w + 20
		
class NonLoopNode(Node):
	def __init__(self,PU):
		Node.__init__(self,PU)
		self.branch = []
		
	def isEmpty(self):
		flag = True
		for n in self.branch:
			if not n.isEmpty():
				flag = False
		return flag
	
	def width(self):
		w = 0
		for n in branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
		return w
		
class GoToNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"process")
		self.link = operand
		self.branch = []
	
	def width(self):
		w = 0
		for n in branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
	
		return w + Node.width(self)
	
class ParaNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"info")
		self.paraName = operand
		
	def isEmpty(self):
		return True
		
class CallNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"module")
		self.moduleName = operand
		self.moduleNameVariable = operand
	
	def iconText(self):
		return self.moduleName.upper()
	
class ExecNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU,"db")
		self.type = operand
	
	def iconText(self):
		return "TABLE"
	
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


