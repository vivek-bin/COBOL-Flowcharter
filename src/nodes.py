
class Node:
	def __init__(self,PU):
		self.paraStack = PU.paraStack[:]
		self.lineNo = PU.programCounter
		
	def isEmpty(self):
		return False
		
class IfNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.trueBranch = []
		self.falseBranch = []
		
	def isEmpty(self):
		flag = True
		for n in self.trueBranch:
			if not n.isEmpty():
				flag = False
		for n in self.falseBranch:
			if not n.isEmpty():
				flag = False
		return flag	

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
	
class GoToNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.link = operand
		self.branch = []
	
class ParaNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.paraName = operand
		
	def isEmpty(self):
		return True
		
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

