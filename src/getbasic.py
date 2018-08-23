import createTree
import nodes

def collectDetails(flow,calls,tables):
	for node in flow:
		if node.__class__ is nodes.CallNode:
			calls.append(node)
		if node.__class__ is nodes.ExecNode:
			if node.type == "sql":
				tables.append(node)
			
		if node.__class__ is nodes.NonLoopBranch or node.__class__ is nodes.LoopBranch or node.__class__ is nodes.GoToBranch:
			collectDetails(node.branch,calls,tables)
		
		if node.__class__ is nodes.IfNode:
			collectDetails(node.branch[True].branch,calls,tables)
			collectDetails(node.branch[False].branch,calls,tables)
			
		if node.__class__ is nodes.EvaluateNode:
			for whenbranch in node.whenList:
				collectDetails(whenbranch.branch,calls,tables)
	
	
def main():
	
	calls = []
	tables = []
	
	f = createTree.getChart("VIID246")
	collectDetails(f,calls,tables)
	
	return calls,tables
	
c,t = main()