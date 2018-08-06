
class Node:
	def __init__(self,PU):
		self.paraStack = PU.paraStack[:]
		self.lineNo = PU.programCounter
		
	def isEmpty(self):
		return False
		
	def width():
		return 20
		
class IfNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
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
		
	def width():
		trueWidth = falseWidth = 0
		for n in branch[True]:
			tempWidth = n.width()
			if tempWidth > trueWidth:
				trueWidth = tempWidth
		
		for n in branch[False]:
			tempWidth = n.width()
			if tempWidth > falseWidth:
				falseWidth = tempWidth
		
		return trueWidth + falseWidth

class EvaluateNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.whenList = []
		
	def isEmpty(self):
		flag = True
		for n in self.whenList:
			if not n.isEmpty():
				flag = False
		return flag
		
	def width():
		finalWidth = 0
		for whenBranch in whenList:
			finalWidth += whenBranch.width()
			
		return finalWidth
	
class WhenNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
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
	
	def width():
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
		
	
	def width():
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
	
	
	def width():
		w = 0
		for n in branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
		return w
		
class GoToNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.link = operand
		self.branch = []
	
	def width():
		w = 0
		for n in branch:
			tempWidth = n.width()
			if tempWidth > w:
				w = tempWidth
	
		return w + 20
	
class ParaNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.paraName = operand
		
	def isEmpty(self):
		return True
		
	def width():
		return 10
		
class CallNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.moduleName = operand
		self.moduleNameVariable = operand
	
class ExecNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.type = operand
	
class EndNode(Node):
	def __init__(self,PU,operand=0):
		Node.__init__(self,PU)
		self.errorEnd = operand

class LoopBreakPointer(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.link = operand
	
	def width():
		return 20 + 20
		
