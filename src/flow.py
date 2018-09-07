import constants as CONST
import os
import subprocess
import nodes
import createTree
import fileaccess
import textwrap
import sys
import inspect
import time
try:
	import Tkinter
except ImportError:
	import tkinter as Tkinter
from PIL import Image,ImageTk


class ChartFrame(Tkinter.Frame):
	def __init__(self, parent,component):
		Tkinter.Frame.__init__(self, parent)
		self.parent = parent
		self.nodeDict = {}
		self.component = component
		self.toolTip = []
		self.zoomScale = 1.0
		self.icons = {}
		self.iconImages = {}
		self.initUI()
		self.loadIcons()
	
	def initUI(self):
		self.scrollbarV = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL)
		self.scrollbarV.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
		self.scrollbarH = Tkinter.Scrollbar(self,orient=Tkinter.HORIZONTAL)
		self.scrollbarH.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
		
		self.parent.title(self.component.upper())
		self.config(bg = "#F0F0F0")
		self.pack(fill = Tkinter.BOTH, expand = 1)
		#create canvas
		self.canvas = Tkinter.Canvas(self, relief = Tkinter.FLAT, background = "#D2D2D2",width = 800, height = 600,state=Tkinter.NORMAL)
		self.canvas.pack(side = Tkinter.LEFT, anchor = Tkinter.NW, expand=True, fill=Tkinter.BOTH, padx = 10, pady = 10)
		
		self.canvas.tag_bind("ButtonIcon", "<ButtonPress-1>", self.setPressedIcon)
		self.canvas.tag_bind("ButtonIcon", "<ButtonRelease-1>", self.resetPressedIcon)
		self.canvas.tag_bind("JumpToLine", "<ButtonRelease-1>", self.openExpandedCode)
		self.canvas.tag_bind("HasDetails", "<Enter>", self.showToolTip)
		self.canvas.tag_bind("HasDetails", "<Leave>", self.hideToolTip)
		self.canvas.tag_bind("CalledProgram", "<Double-Button-1>", self.createNewWindow)
		
		self.canvas.configure(xscrollcommand=self.scrollbarH.set,yscrollcommand=self.scrollbarV.set)
		self.scrollbarV.config(command=self.canvas.yview)
		self.scrollbarH.config(command=self.canvas.xview)
		
	def zoom(self, key):
		redrawFlag = False
		zoomAmount = 1.0
		if key == "+" and self.zoomScale < 1.0:
			zoomAmount = 1.1
			redrawFlag = True
		
		if key == "-" and self.zoomScale > 0.1:
			zoomAmount = 1.0/1.1
			redrawFlag = True
		
		if redrawFlag:
			self.zoomScale *= zoomAmount
			self.canvas.scale("all",0,0,zoomAmount,zoomAmount)
		
			for iconName in self.iconImages.keys():
				img = self.iconImages[iconName]
				imgResize = (int(i*self.zoomScale) for i in img.size)
				img = img.resize(imgResize, Image.ANTIALIAS)
				self.icons[iconName] = ImageTk.PhotoImage(img)
				
			buttons = self.canvas.find_withtag("ButtonIcon")
			for button in buttons:
				node = self.nodeDict[button]
				self.canvas.itemconfig(button,image=self.icons[node.idleIcon()],activeimage=self.icons[node.hoverIcon()])
			
			buttons = self.canvas.find_withtag("ButtonText")
			newFont = (CONST.FONT[0],1+int(CONST.FONT[1]*self.zoomScale*0.9),CONST.FONT[2])
			for button in buttons:
				self.canvas.itemconfig(button,font=newFont)
				
			chartBox = self.canvas.bbox("all")
			chartBorder = 50
			chartBox = (chartBox[0]-chartBorder,chartBox[1]-chartBorder,chartBox[2]+chartBorder,chartBox[3]+chartBorder)
			self.canvas.configure(scrollregion = chartBox)
		
	def mouseWheelScroll(self, event):
		scroll = -1 * int(event.delta / 120)
		ctrlPressed = event.state & (1 << 2)
		
		if ctrlPressed:
			if scroll < 0:
				self.zoom("+")
			else:
				self.zoom("-")
		else:
			self.canvas.yview_scroll(scroll, "units")
	
	def loadIcons(self):
		for iType in ["branch","db","file","info","module","process","start","loop"]:
			for state in ["idle","hover","click"]:
				imgName = iType + "-" + state
				img = Image.open(CONST.ICONS + imgName +".png")
				self.iconImages[imgName] = img
				self.icons[imgName] = ImageTk.PhotoImage(img)
		
		allNodeClasses = inspect.getmembers(nodes, inspect.isclass)
		for nodeClass in allNodeClasses:
			nodeClass = nodeClass[1]
			if nodeClass.iconName:
				nodeClass.iconWidth = self.icons[nodeClass.iconName+"-"+state].width()
				nodeClass.iconHeight = self.icons[nodeClass.iconName+"-"+state].height()
	
	def newBlock(self,node,x,y):
		objId = self.canvas.create_image(x,y,image=self.icons[node.idleIcon()],activeimage=self.icons[node.hoverIcon()],tags=node.tags)
		textId = self.canvas.create_text(x,y,text=node.iconText(),font=CONST.FONT,fill="#000000",state=Tkinter.DISABLED,tags="ButtonText")
		
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
			
		self.canvas.tag_lower("Lines")
	
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
		createNewWindow(newComponent)
	
	
class ChartWindow(Tkinter.Toplevel):
	charts = {}
	def __init__(self,component):
		Tkinter.Toplevel.__init__(self)
		component = component.upper()
		
		self.chartFrame  = False
		self.component = component
		self.protocol("WM_DELETE_WINDOW", self.eraseChart)
		
		self.createWindow()
	
	def eraseChart(self):
		try:
			del ChartWindow.charts[self.component]
		except KeyError:
			pass
		self.destroy()
	
	def drawFlowChart(self,nodeList,curX,curY):
		prevHeight = 0
		currentHeight = 0
		joiningLineLength = prevHeight + currentHeight
		for node in nodeList:
			prevHeight = currentHeight
			currentHeight = node.height()
			joiningLineLength = prevHeight + currentHeight
			
			if node.isEmpty():
				continue
			
			if node.__class__ is nodes.NonLoopBranch:
				curX, curY = self.drawFlowChart(node.branch,curX,curY)
			else:
				prevX, prevY = curX, curY
				curY += joiningLineLength/2
				linePoints = (prevX,prevY,curX,curY)
				self.chartFrame.joiningLine(linePoints)
				self.chartFrame.newBlock(node,curX,curY)
			
			if node.__class__ is nodes.LoopBranch:
				prevX, prevY = curX, curY
				curY += joiningLineLength/2
				linePoints = (prevX,prevY,curX,curY)
				self.chartFrame.joiningLine(linePoints)
				retX, retY = self.drawFlowChart(node.branch,curX,curY)
				linePoints = (curX,curY-joiningLineLength/2,retX,retY,node.width()/2+node.nodeWidth()/8)
				self.chartFrame.joiningLine(linePoints,"-C",node=node)
				
				curY = retY
			
			
			if node.__class__ is nodes.IfNode:
				prevX, prevY = curX, curY
				curY += joiningLineLength/2
				
				tempX = {}
				tempY = {}
				terminatedBranch = {}
				tempX[True] = curX - node.branch[False].width()/2		#use opposite branch width
				tempX[False] = curX + node.branch[True].width()/2		#use opposite branch width
				
				for branch in [True,False]:
					branchNode = node.branch[branch]
					linePoints = (prevX,prevY,tempX[branch],curY)
					self.chartFrame.joiningLine(linePoints,bend="7",node=branchNode)
					tempX[branch], tempY[branch] = self.drawFlowChart(branchNode.branch,tempX[branch],curY)
					terminatedBranch[branch] = self.isTerminatedBranch(branchNode.branch)
				
				if tempY[True] < tempY[False]:
					extX, extY = tempX[True], tempY[False]
				else:
					extX, extY = tempX[False], tempY[True]
				
				for branch in [True,False]:
					if not terminatedBranch[branch]:
						if tempY[branch] != extY:
							linePoints = (tempX[branch],tempY[branch],tempX[branch],extY)
							self.chartFrame.joiningLine(linePoints)
						linePoints = (tempX[branch],extY,curX,extY)
						self.chartFrame.joiningLine(linePoints)
				
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
				
				totalWidth = 0
				for branch in arrangedWhen:
					totalWidth += branch.width()

				prevX, prevY = curX, curY
				curY += joiningLineLength
					
				branchEndPoints = []
				
				evenWidth = 0
				oddWidth = 0
				for i,newNode in enumerate(arrangedWhen):
					newNodeWidth = newNode.width()
					if i % 2:
						newX = curX + evenWidth + newNodeWidth/2 - totalWidth/2
						evenWidth += newNodeWidth
					else:
						newX = curX - oddWidth - newNodeWidth/2 + totalWidth/2
						oddWidth += newNodeWidth
					
					linePoints = (prevX,prevY,newX,curY - joiningLineLength/2,newX,curY)
					self.chartFrame.joiningLine(linePoints,node=newNode)
					endPoints = self.drawFlowChart(newNode.branch,newX,curY)
					branchEndPoints.append(endPoints)
				
				
				maxY = -1
				for point in branchEndPoints:
					if point[1] > maxY:
						maxY = point[1]
				curY = maxY
				
				prevX, prevY = curX, curY
				curY += joiningLineLength
				
				
				minX = branchEndPoints[0][0]
				try:
					maxX = branchEndPoints[1][0]
				except IndexError:
					maxX = minX
				
				for i,point in enumerate(branchEndPoints):
					if not self.isTerminatedBranch(arrangedWhen[i].branch):
						if point[1] != maxY:
							linePoints = (point[0],point[1],point[0],maxY)
							self.chartFrame.joiningLine(linePoints)
						linePoints = (point[0],maxY,curX,curY)
						self.chartFrame.joiningLine(linePoints,bend="N")
				
			
			prevX, prevY = curX, curY
			curY += joiningLineLength/2
			if node.__class__ is not nodes.EndNode:
				linePoints = (prevX,prevY,curX,curY)
				self.chartFrame.joiningLine(linePoints)
		
		
		return curX, curY
		
	def isTerminatedBranch(self,branch):
		if not branch:
			return False
		
		node = branch[-1]
		
		if node.__class__ is nodes.GoToBranch or node.__class__ is nodes.EndNode:
			return True
			
		if node.__class__ is nodes.LoopBranch or node.__class__ is nodes.NonLoopBranch:
			return self.isTerminatedBranch(node.branch)
	
	def alreadyExists(self,component):
		if component in ChartWindow.charts:
			ChartWindow.charts[component].focus_set()
			return True
		else:
			return False
	
	def createWindow(self):
		startTime = time.time()
		
		nodes = createTree.getChart(self.component)

		RWidth = int(self.winfo_screenwidth()*0.5)
		RHeight = int(self.winfo_screenheight()*0.95)
		self.geometry(("%dx%d")%(RWidth,RHeight))
		
		self.chartFrame = ChartFrame(self,self.component)
		self.drawFlowChart(nodes,int(self.chartFrame.winfo_screenwidth()*0.25),20)
		chartBox = self.chartFrame.canvas.bbox("all")
		chartBorder = 50
		chartBox = (chartBox[0]-chartBorder,chartBox[1]-chartBorder,chartBox[2]+chartBorder,chartBox[3]+chartBorder)
		self.chartFrame.canvas.configure(scrollregion = chartBox)
		
		self.bind("<MouseWheel>",self.chartFrame.mouseWheelScroll)
		
		print(time.time() - startTime)


def createNewWindow(component):
	component = component.upper()
	if fileaccess.validComponentName(component):
		if component in ChartWindow.charts:
			ChartWindow.charts[component].focus_set()
		else:
			ChartWindow.charts[component] = ChartWindow(component)
	
	
	
def main():
	root = Tkinter.Tk()
	
	inputBox = Tkinter.Entry(root)
	inputBox.pack()
	inputBox.insert(0,"vib3248")
	inputBoxButton = Tkinter.Button(root,text="OPEN",command=lambda:createNewWindow(inputBox.get()))
	inputBox.bind("<Return>",lambda e:createNewWindow(inputBox.get()))
	inputBoxButton.pack()
	
	root.mainloop()

if __name__ == "__main__":
	main()
