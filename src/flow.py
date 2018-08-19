import constants as CONST
import os
import subprocess
import Tkinter
import nodes
import createTree
import fileaccess
import textwrap
from PIL import ImageTk

class ChartWindow(Tkinter.Frame):
	def __init__(self, parent,component):
		Tkinter.Frame.__init__(self, parent)
		self.parent = parent
		self.nodeDict = {}
		self.component = component
		self.initUI()
		self.loadIcons()
		self.toolTip = []
	
	def initUI(self):
		self.scrollbarV = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL)
		self.scrollbarV.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
		self.scrollbarH = Tkinter.Scrollbar(self,orient=Tkinter.HORIZONTAL)
		self.scrollbarH.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
		
		self.parent.title(self.component.upper())
		self.config(bg = '#F0F0F0')
		self.pack(fill = Tkinter.BOTH, expand = 1)
		#create canvas
		self.canvas = Tkinter.Canvas(self, relief = Tkinter.FLAT, background = "#D2D2D2",width = 800, height = 600)#,scrollregion=(0,0,1500,15000))
		self.canvas.pack(side = Tkinter.LEFT, anchor = Tkinter.NW, fill=Tkinter.BOTH, padx = 10, pady = 10)
		self.canvas.tag_bind("ButtonIcon", "<ButtonPress-1>", self.setPressedIcon)
		self.canvas.tag_bind("ButtonIcon", "<ButtonRelease-1>", self.resetPressedIcon)
		self.canvas.tag_bind("JumpToLine", "<ButtonRelease-1>", self.openExpandedCode)
		self.canvas.tag_bind("HasDetails", "<Enter>", self.showToolTip)
		self.canvas.tag_bind("HasDetails", "<Leave>", self.hideToolTip)
		
		self.scrollbarV.config(command=self.canvas.yview)
		self.scrollbarH.config(command=self.canvas.xview)
		
		self.canvas.bind_all("<MouseWheel>", self.mouseWheelScroll)
		
	def mouseWheelScroll(self, event):
		self.canvas.yview_scroll(-1*(event.delta/120), "units")
		
		
		
	def loadIcons(self):
		self.icons = {}
		for iType in ["branch","db","file","info","module","process","start"]:
			for state in ["idle","hover","click"]:
				self.icons[iType+"-"+state] = ImageTk.PhotoImage(file=CONST.ICONS + iType + "-" + state +".png")
				
	def newBlock(self,node,x,y):
		tags = ("ButtonIcon","JumpToLine","HasDetails")
		
		objId = self.canvas.create_image(x,y,image=self.icons[node.idleIcon],activeimage=self.icons[node.hoverIcon],tags=tags)
		textId = self.canvas.create_text(x,y,text=node.iconText(),font=CONST.FONT,fill="#000000",state=Tkinter.DISABLED)
		
		self.nodeDict[objId] = node
		
	def joiningLine(self,linePoints,bend=False,node=False):

		if len(linePoints) == 4:
			prevX,prevY,curX,curY = linePoints
			
			if bend == "N":
				midY = (prevY + curY)/2
				linePoints = (prevX,prevY,prevX,midY,curX,midY,curX,curY)
			elif bend == "7":
				linePoints = (prevX,prevY,curX,prevY,curX,curY)
			elif bend == "C":
				outX = CONST.BRANCHWIDTH/2 - CONST.BRANCHSPACE/2
				linePoints = (prevX,prevY,prevX-outX,prevY,curX-outX,curY,curX,curY)
			elif bend == "-C":
				outX = CONST.BRANCHWIDTH/2 - CONST.BRANCHSPACE/2
				linePoints = (prevX,prevY,prevX+outX,prevY,curX+outX,curY,curX,curY)
		
		if node:
			tags = ("Lines","JumpToLine","HasDetails")
			lineId = self.canvas.create_line(linePoints,fill="#000000",tags=tags,width=2,activewidth=4)
			self.nodeDict[lineId] = node
		else:
			tags = ("Lines")
			self.canvas.create_line(linePoints,fill="#000000",tags=tags,width=1)
			
		self.canvas.tag_lower(tags[0])
	
	def setPressedIcon(self,event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		node = self.nodeDict[objId]
		canvas.itemconfig(objId,activeimage=self.icons[node.clickIcon])
		
	def resetPressedIcon(self,event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		node = self.nodeDict[objId]
		canvas.itemconfig(objId,activeimage=self.icons[node.hoverIcon])
		
	def openExpandedCode(self,event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		node = self.nodeDict[objId]
		
		componentLocation = '"' + fileaccess.extractExpandedFile(self.component) + '"'
		lineNo = "-n" + str(node.lineNo)
		command = "\"" + CONST.NPLOCATION + "\"" +  " " +  componentLocation + " " + lineNo
		
		subprocess.call(command)
	
	def showToolTip(self,event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		if objId in self.toolTip:
			return
		
		self.toolTip.append(objId)
		
		points = canvas.bbox(objId)
		x = (points[0] + points[2])/2
		y = (points[1] + points[3])/2
		
		node = self.nodeDict[objId]
		text = node.description()		
		if text:
			lines = text.split("\n")
			lines = [textwrap.fill(line,CONST.TOOLTIPSIZE) for line in lines]
			text = "\n".join(lines)
			textLabel = self.canvas.create_text(x,y,text=text,anchor="nw",font=CONST.FONT,fill="#000000",tags="ToolTip",state=Tkinter.DISABLED)
			textBg = self.canvas.create_rectangle(self.canvas.bbox(textLabel),fill="white",tags="ToolTip",state=Tkinter.DISABLED)
			self.canvas.tag_lower(textBg,textLabel)
		
	def hideToolTip(self,event):
		canvas = event.widget
		objIds = canvas.find_withtag("ToolTip")
		
		self.toolTip = []
		
		for objId in objIds:
			canvas.delete(objId)
	
	
def createFlowChart(chartWindow,nodeList,curX,curY):
	#firstNodeFlag = True
	for node in nodeList:
		if node.__class__ is nodes.ParaNode:
			pass#continue
		if node.isEmpty():
			continue
		
		if node.__class__ is nodes.NonLoopBranch:
			curX, curY = createFlowChart(chartWindow,node.branch,curX,curY)
		else:
			#if not firstNodeFlag:
			prevX, prevY = curX, curY
			curY += CONST.BLOCKHEIGHT/2
			linePoints = (prevX,prevY,curX,curY)
			chartWindow.joiningLine(linePoints)
			chartWindow.newBlock(node,curX,curY)
			#firstNodeFlag = False
		
		if node.__class__ is nodes.LoopBranch:
			prevX, prevY = curX, curY
			curY += CONST.BLOCKHEIGHT/2
			linePoints = (prevX,prevY,curX,curY)
			chartWindow.joiningLine(linePoints)
			retX, retY = createFlowChart(chartWindow,node.branch,curX,curY)
			linePoints = (curX,curY - CONST.BLOCKHEIGHT/2,retX,retY)
			chartWindow.joiningLine(linePoints,"-C")
			
			curY = retY
		
		
		if node.__class__ is nodes.IfNode:
			prevX, prevY = curX, curY
			curY += CONST.BLOCKHEIGHT/2
			
			curXT = curX - node.branch[True].width()/2
			linePoints = (prevX,prevY,curXT,curY)
			chartWindow.joiningLine(linePoints,bend="7",node=node.branch[True])
			curXT, curYT = createFlowChart(chartWindow,node.branch[True].branch,curXT,curY)
			
			
			curXF = curX + node.branch[False].width()/2
			linePoints = (prevX,prevY,curXF,curY)
			chartWindow.joiningLine(linePoints,bend="7",node=node.branch[False])
			curXF, curYF = createFlowChart(chartWindow,node.branch[False].branch,curXF,curY)
			
			if curYT < curYF:
				extX, extY = curXT, curYF
			else:
				extX, extY = curXF, curYT
			
			if curYT != curYF:
				linePoints = (extX,curYT,extX,curYF)
				chartWindow.joiningLine(linePoints)
			linePoints = (curXF,extY,curXT,extY)
			chartWindow.joiningLine(linePoints)
			curY = extY
			
			
		
		if node.__class__ is nodes.EvaluateNode:
			arrangedWhen = []
			for i,branch in enumerate(node.whenList):
				breakFlag = False
				for j,branch2 in enumerate(arrangedWhen):
					if branch2.width() > branch.width():
						arrangedWhen.insert(j,branch)
						breakFlag = True
						break
				if not breakFlag:
					arrangedWhen.append(branch)
			
			
			branchStartX = []
			branchStartY = []
			branchStartNum = list(range(0,len(arrangedWhen),2)) + list(range(1,len(arrangedWhen),2))
			
			oddWhen = [b for i,b in enumerate(arrangedWhen) if i%2 == 0]
			evenWhen = [b for i,b in enumerate(arrangedWhen) if i%2 == 1]
			negWidth = posWidth = 0
			ySeparation = (CONST.BLOCKHEIGHT/2)/len(oddWhen)
			
			if len(oddWhen) != len(evenWhen):
				newNodeWidth = evenWhen.pop().width()
				branchStartX.append(curX)
				branchStartY.append(curY + CONST.BLOCKHEIGHT/2)
				negWidth = posWidth = newNodeWidth/2
				
			while evenWhen:
				newNodeWidth = evenWhen.pop().width()
				branchStartX.insert(0, curX - newNodeWidth/2 - negWidth)
				branchStartY.insert(0, curY + CONST.BLOCKHEIGHT/2 - ySeparation)
					
				negWidth += newNodeWidth
				
			while oddWhen:
				newNodeWidth = oddWhen.pop().width()
				branchStartX.append(curX + newNodeWidth/2 + posWidth)
				branchStartY.append(curY + CONST.BLOCKHEIGHT/2 - ySeparation)
				posWidth += newNodeWidth
				
				
			prevX, prevY = curX, curY
			curY += CONST.BLOCKHEIGHT
				
			branchEndPoints = []
			
			for i,branchNum in enumerate(branchStartNum):
				newNode = arrangedWhen[branchNum]
				linePoints = (prevX,prevY,branchStartX[i],branchStartY[i],branchStartX[i],curY)
				chartWindow.joiningLine(linePoints,node=newNode)
				endPoints = createFlowChart(chartWindow,newNode.branch,branchStartX[i],curY)
				branchEndPoints.append(endPoints)
			
			
			minX = branchStartX[0]
			maxX = branchStartX[-1]
			maxY = -1
			for point in branchEndPoints:
				if point[1] > maxY:
					maxY = point[1]
			
			for point in branchEndPoints:
				if point[1] != maxY:
					linePoints = (point[0],point[1],point[0],maxY)
					chartWindow.joiningLine(linePoints)
			linePoints = (minX,maxY,maxX,maxY)
			chartWindow.joiningLine(linePoints)
			
			curY = maxY
		
		if node.__class__ is not nodes.EndNode:
			prevX, prevY = curX, curY
			curY += CONST.BLOCKHEIGHT/2
			linePoints = (prevX,prevY,curX,curY)
			chartWindow.joiningLine(linePoints)
				
	
	return curX, curY

	

def main(component="VIID246"):
	nodes = createTree.getChart(component)
	root = Tkinter.Tk()
	root.geometry('500x600+10+50')
	app = ChartWindow(root,component)
	createFlowChart(app,nodes[:14],200,20)
	app.mainloop()
	#root.destroy()
	
	return nodes

#n=main()
#n=main("VIBRE016")
#n=main("VIB3N99")
n=main("aib018y")
