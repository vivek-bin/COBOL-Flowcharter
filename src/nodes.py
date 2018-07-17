

class Node:
	def __init__(self,performStack):
		self.performStack = performStack[:]
	
class Branch:
	def __init__(self):
		self.flow = []
	
class IfNode:
	def __init__(self):
		self.trueBranch = Branch()
		self.falseBranch = Branch()

class EvaluateNode:
	def __init__(self):
		self.branchList = []
	
class LoopNode:
	def __init__(self):
		self.loopFlow = Branch()
	
class NonLoopNode:
	def __init__(self):
		self.flow = Branch()
	
class CallNode:
	def __init__(self):
		self.moduleName = ""
	
class GoToNode:
	def __init__(self):
		self.link = ""
	
class EndNode:
	def __init__(self):
		self.errorEnd = 0
