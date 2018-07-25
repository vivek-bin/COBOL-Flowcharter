
class Node:
	def __init__(self,PU):
		self.paraStack = PU.paraStack[:]
		self.lineNo = PU.programCounter
		
class IfNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.trueBranch = []
		self.falseBranch = []

class EvaluateNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.whenList = []
	
class WhenNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = [operand]
		self.branch = []
		
	def addCondition(self,operand):
		self.condition.append(operand)
	
class LoopNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.condition = operand
		self.branch = []
	
class NonLoopNode(Node):
	def __init__(self,PU):
		Node.__init__(self,PU)
		self.branch = []
	
class CallNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.moduleName = operand
		self.moduleNameVariable = operand
	
class ExecNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.type = operand
	
class GoToNode(Node):
	def __init__(self,PU,operand):
		Node.__init__(self,PU)
		self.link = operand
	
class EndNode(Node):
	def __init__(self,PU,operand=0):
		Node.__init__(self,PU)
		self.errorEnd = operand

