import constants as CONST
import os
import subprocess
import Tkinter
import nodes
import createTree
import fileaccess
import textwrap
import sys
import inspect
import time
from PIL import Image,ImageTk

class ChartWindow(Tkinter.Frame):
	def __init__(self, parent,component):
		Tkinter.Frame.__init__(self, parent)
		self.parent = parent
		self.nodeDict = {}
		self.component = component
		self.initUI()
		self.loadIcons()
		self.toolTip = []
		self.zoomScale = 1.0
	
	def initUI(self):
		self.scrollbarV = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL)
		self.scrollbarV.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
		self.scrollbarH = Tkinter.Scrollbar(self,orient=Tkinter.HORIZONTAL)
		self.scrollbarH.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
		
		self.parent.title(self.component.upper())
		self.config(bg = '#F0F0F0')
		self.pack(fill = Tkinter.BOTH, expand = 1)
		#create canvas
		self.canvas = Tkinter.Canvas(self, relief = Tkinter.FLAT, background = "#D2D2D2",width = 800, height = 600)
		self.canvas.pack(side = Tkinter.LEFT, anchor = Tkinter.NW, expand=True, fill=Tkinter.BOTH, padx = 10, pady = 10)
		self.canvas.bind_all("<Key>",self.zoom)
		self.canvas.tag_bind("ButtonIcon", "<ButtonPress-1>", self.setPressedIcon)
		self.canvas.tag_bind("ButtonIcon", "<ButtonRelease-1>", self.resetPressedIcon)
		self.canvas.tag_bind("JumpToLine", "<ButtonRelease-1>", self.openExpandedCode)
		self.canvas.tag_bind("HasDetails", "<Enter>", self.showToolTip)
		self.canvas.tag_bind("HasDetails", "<Leave>", self.hideToolTip)
		self.canvas.tag_bind("CalledProgram", "<Double-Button-1>", self.createNewWindow)
		
		self.canvas.configure(xscrollcommand=self.scrollbarH.set,yscrollcommand=self.scrollbarV.set)
		self.scrollbarV.config(command=self.canvas.yview)
		self.scrollbarH.config(command=self.canvas.xview)
		
		self.canvas.bind_all("<MouseWheel>", self.mouseWheelScroll)
		
	def zoom(self,event):
		canvas = event.widget
		key = event.char
		redrawFlag = False
		if key == "+" and self.zoomScale < 1.0:
			self.zoomScale *= 1.1
			redrawFlag = True
			if self.zoomScale > 1.0:
				self.zoomScale = 1.0
		
		if key == "-" and self.zoomScale > 0.05:
			self.zoomScale /= 1.1
			redrawFlag = True
			if self.zoomScale < 0.05:
				self.zoomScale = 0.05
		if redrawFlag:
			canvas.scale("all",0,0,self.zoomScale,self.zoomScale)
		
		
		
	
	def mouseWheelScroll(self, event):
		self.canvas.yview_scroll(-1*(event.delta/120), "units")
		
	def loadIcons(self):
		self.icons = {}
		for iType in ["branch","db","file","info","module","process","start"]:
			for state in ["idle","hover","click"]:
				imgName = iType + "-" + state
				img = Image.open(CONST.ICONS + imgName +".png")
				imgResize = (int(i*CONST.ZOOM) for i in img.size)
				img = img.resize(imgResize, Image.ANTIALIAS)
				self.icons[imgName] = ImageTk.PhotoImage(img)
		
		allNodeClasses = inspect.getmembers(nodes, inspect.isclass)
		for nodeClass in allNodeClasses:
			nodeClass = nodeClass[1]
			if nodeClass.iconName:
				nodeClass.iconWidth = self.icons[nodeClass.iconName+"-"+state].width()
				nodeClass.iconHeight = self.icons[nodeClass.iconName+"-"+state].height()
				
	def newBlock(self,node,x,y):
		tags = ("ButtonIcon","JumpToLine","HasDetails")
		if node.__class__ is nodes.CallNode:
			tags = tags + ("CalledProgram",)
		objId = self.canvas.create_image(x,y,image=self.icons[node.idleIcon()],activeimage=self.icons[node.hoverIcon()],tags=tags)
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
		
		if len(linePoints) == 5:
			prevX,prevY,curX,curY,outX = linePoints
			if bend == "C":
				linePoints = (prevX,prevY,prevX-outX,prevY,curX-outX,curY,curX,curY)
			elif bend == "-C":
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
		canvas.itemconfig(objId,activeimage=self.icons[node.clickIcon()])
		
	def resetPressedIcon(self,event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		node = self.nodeDict[objId]
		canvas.itemconfig(objId,activeimage=self.icons[node.hoverIcon()])
		
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
		#x = (points[0] + points[2])/2
		#y = (points[1] + points[3])/2
		x = canvas.canvasx(event.x)
		y = canvas.canvasy(event.y)
		
		node = self.nodeDict[objId]
		text = node.description()		
		if text:
			lines = text.split("\n")
			lines = [textwrap.fill(line,CONST.TOOLTIPSIZE) for line in lines]
			text = "\n".join(lines)
			textLabel = self.canvas.create_text(x,y,text=text,anchor="nw",font=CONST.TOOLTIPFONT,fill="#000000",tags="ToolTip",state=Tkinter.DISABLED)
			textBg = self.canvas.create_rectangle(self.canvas.bbox(textLabel),fill="white",tags="ToolTip",state=Tkinter.DISABLED)
			self.canvas.tag_lower(textBg,textLabel)
		
	def hideToolTip(self,event):
		canvas = event.widget
		objIds = canvas.find_withtag("ToolTip")
		
		self.toolTip = []
		
		for objId in objIds:
			canvas.delete(objId)
			
	def createNewWindow(self,event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		node = self.nodeDict[objId]
		newComponent = node.moduleName
		global createWindow
		createWindow(newComponent)
		print newComponent
	
	
def createFlowChart(chartWindow,nodeList,curX,curY):
	prevHeight = 0
	currentHeight = 0
	joiningLineLength = prevHeight + currentHeight
	for node in nodeList:
		prevHeight = currentHeight
		currentHeight = node.height()
		joiningLineLength = prevHeight + currentHeight
		
		if node.__class__ is nodes.ParaNode:
			pass#continue
		if node.isEmpty():
			continue
		
		if node.__class__ is nodes.NonLoopBranch:
			curX, curY = createFlowChart(chartWindow,node.branch,curX,curY)
		else:
			prevX, prevY = curX, curY
			curY += joiningLineLength/2
			linePoints = (prevX,prevY,curX,curY)
			chartWindow.joiningLine(linePoints)
			chartWindow.newBlock(node,curX,curY)
		
		if node.__class__ is nodes.LoopBranch:
			prevX, prevY = curX, curY
			curY += joiningLineLength/2
			linePoints = (prevX,prevY,curX,curY)
			chartWindow.joiningLine(linePoints)
			retX, retY = createFlowChart(chartWindow,node.branch,curX,curY)
			linePoints = (curX,curY-joiningLineLength/2,retX,retY,node.width()/2+node.nodeWidth()/8)
			chartWindow.joiningLine(linePoints,"-C",node=node)
			
			curY = retY
		
		
		if node.__class__ is nodes.IfNode:
			prevX, prevY = curX, curY
			curY += joiningLineLength/2
			
			tempX = {}
			tempY = {}
			terminatedBranch = {}
			tempX[True] = curX - node.branch[False].width()/2		#proper positioning(use opposite branch width)
			tempX[False] = curX + node.branch[True].width()/2		#proper positioning(use opposite branch width)
			
			for branch in [True,False]:
				branchNode = node.branch[branch]
				linePoints = (prevX,prevY,tempX[branch],curY)
				chartWindow.joiningLine(linePoints,bend="7",node=branchNode)
				tempX[branch], tempY[branch] = createFlowChart(chartWindow,branchNode.branch,tempX[branch],curY)
				terminatedBranch[branch] = isTerminatedBranch(branchNode.branch)
			
			if tempY[True] < tempY[False]:
				extX, extY = tempX[True], tempY[False]
			else:
				extX, extY = tempX[False], tempY[True]
			
			for branch in [True,False]:
				if not terminatedBranch[branch]:
					if tempY[branch] != extY:
						linePoints = (tempX[branch],tempY[branch],tempX[branch],extY)
						chartWindow.joiningLine(linePoints)
					linePoints = (tempX[branch],extY,curX,extY)
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
			ySeparation = (joiningLineLength/2)/len(oddWhen)
			
			if len(oddWhen) != len(evenWhen):
				newNodeWidth = evenWhen.pop().width()
				branchStartX.append(curX)
				branchStartY.append(curY + joiningLineLength/2)
				negWidth = posWidth = newNodeWidth/2
				
			while evenWhen:
				newNodeWidth = evenWhen.pop().width()
				branchStartX.insert(0, curX - newNodeWidth/2 - negWidth)
				branchStartY.insert(0, curY + joiningLineLength/2 - ySeparation)
					
				negWidth += newNodeWidth
				
			while oddWhen:
				newNodeWidth = oddWhen.pop().width()
				branchStartX.append(curX + newNodeWidth/2 + posWidth)
				branchStartY.append(curY + joiningLineLength/2 - ySeparation)
				posWidth += newNodeWidth
				
				
			prevX, prevY = curX, curY
			curY += joiningLineLength
				
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
		
		prevX, prevY = curX, curY
		curY += joiningLineLength/2
		if node.__class__ is not nodes.EndNode:
			linePoints = (prevX,prevY,curX,curY)
			chartWindow.joiningLine(linePoints)
				
	#prevX, prevY = curX, curY
	#curY += joiningLineLength/2
	#if not isTerminatedBranch(nodeList):
	#	linePoints = (prevX,prevY,curX,curY)
	#	chartWindow.joiningLine(linePoints)
	
	return curX, curY

	
def isTerminatedBranch(branch):
	if not branch:
		return False
	
	node = branch[-1]
	
	if node.__class__ is nodes.GoToBranch or node.__class__ is nodes.EndNode:
		return True
		
	if node.__class__ is nodes.LoopBranch or node.__class__ is nodes.NonLoopBranch:
		return isTerminatedBranch(node.branch)
	
	
def createNewChart(app,nodes):
	app.canvas.delete("all")
	createFlowChart(app,nodes,int(app.winfo_screenwidth()*0.25),20)
	chartBox = app.canvas.bbox("all")
	chartBorder = 50
	chartBox = (chartBox[0]-chartBorder,chartBox[1]-chartBorder,chartBox[2]+chartBorder,chartBox[3]+chartBorder)
	app.canvas.configure(scrollregion = chartBox)

def createWindow(component="VIID246"):
	startTime = time.time()
	
	root = Tkinter.Tk()
	RWidth = int(root.winfo_screenwidth()*0.5)
	RHeight = int(root.winfo_screenheight()*0.95)
	root.geometry(("%dx%d")%(RWidth,RHeight))
	
	nodes = createTree.getChart(component)
	print time.time() - startTime
	startTime = time.time()
	
	app = ChartWindow(root,component)
	createNewChart(app,nodes)
	
	print time.time() - startTime
	root.mainloop()
	
	return nodes
	
#n=createWindow()
#n=createWindow("VIBRE016")
#n=createWindow("vcc1060")
n=createWindow("vib3248")
#n=createWindow("vib3365")
