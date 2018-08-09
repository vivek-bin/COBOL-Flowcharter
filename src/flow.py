import constants as CONST
import os
import Tkinter

class ChartWindow(Tkinter.Frame):
	def __init__(self, parent,component):
		Tkinter.Frame.__init__(self, parent)
		self.parent = parent
		self.nodeDict = {}
		self.component = component
		self.initUI()
	
	def initUI(self):
		self.parent.title(component.upper())
		self.config(bg = '#F0F0F0')
		self.pack(fill = Tkinter.BOTH, expand = 1)
		#create canvas
		self.canvas = Tkinter.Canvas(self, relief = Tkinter.FLAT, background = "#D2D2D2",width = 180, height = 500)
		self.canvas.pack(side = Tkinter.TOP, anchor = Tkinter.NW, padx = 10, pady = 10)
		self.canvas.tag_bind("JumpToLine", "<ButtonPress-1>", self.openExpandedCode)
		self.canvas.tag_bind("HasDetails", "<Enter>", self.showToolTip)
		self.canvas.tag_bind("HasDetails", "<Leave>", self.hideToolTip)
		
	def newBlock(self,node,x,y):
		tags = ("JumpToLine","HasDetails")
		
		objIds = self.canvas.create_image(x,y,image=node.idleIcon,tags=tags)
		textId = self.canvas.create_text(x,y,text=node.iconText(),font=CONST.FONT,fill="#000000",tags=tags)
			
		self.nodeDict[objId] = node
		self.nodeDict[textId] = node
		
	def joiningLine(self,prevX,prevY,curX,curY):
		return self.canvas.create_line(prevX,prevY,curX,curY,fill="#000000")
	
	def openExpandedCode(event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		node = self.nodeDict[objId]
		componentLocation = '"' + fileaccess.extractExpandedFile(self.component) + '"'
		lineNo = "-n" + str(node.lineNo)
		command = CONST.NPLOCATION + " " +  componentLocation + " " + lineNo
		os.system(command)
	
	def showToolTip(event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		points = canvas.bbox(objId)
		node = self.nodeDict[objId]
		
		text = node.description()		
		x = (points[0] + points[2])/2
		y = (points[1] + points[3])/2
		
		textLabel = self.canvas.create_text(x,y,text=text,anchor="NW",font=CONST.FONT,fill="#000000",tags="ToolTip")
		textBg = self.canvas.create_rectangle(self.canvas.bbox(textLabel),fill="white",tags="ToolTip")
		self.canvas.tag_lower(textBg,textLabel)
		
		return (textLabel,textBg)
	
	def hideToolTip(event):
		canvas = event.widget
		objIds = canvas.find_withtag("ToolTip")
		
		for objId in objIds:
			canvas.delete(objId)
	
	
	
def createFlowChart(chartWindow,nodes,prevX,prevY,curX,curY):
	for node in nodes:
		chartWindow.joiningLine(prevX,prevY,curX,curY)
		prevX, prevY = curX, curY
		curY += 30
		
		if node.__class__ is nodes.LoopNode:
			createFlowChart(chartWindow,node.branch,prevX,prevY,curX,curY)
		elif node.__class__ is nodes.NonLoopNode:
			createFlowChart(chartWindow,node.branch,prevX,prevY,curX,curY)
		else:
			chartWindow.newBlock(node,curX,curY)
		
		
		if node.__class__ is nodes.IfNode:
			createFlowChart(chartWindow,node.branch[True],prevX-0,prevY-0,curX-0,curY-node.trueWidth()/2)
			createFlowChart(chartWindow,node.branch[False],prevX-0,prevY-0,curX-0,curY+node.falseWidth()/2)
		
		if node.__class__ is nodes.EvaluateNode:
			width = node.width()
			whenCount = len(node.whenList)
			for i,branch in enumerate(node.whenList):
				createFlowChart(chartWindow,node.branch[True],prevX-0,prevY-0,curX-0,curY-100+(200/whenCount)*i)
			

			
			
def main(component="VIID246"):
	root = Tkinter.Tk()
	root.geometry('800x600+10+50')
	app = ChartWindow(root,component)
	app.mainloop()
	root.destroy()

main()
