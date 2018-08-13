import constants as CONST
import os
import subprocess
import Tkinter
import nodes
import createTree
import fileaccess
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
		self.parent.title(self.component.upper())
		self.config(bg = '#F0F0F0')
		self.pack(fill = Tkinter.BOTH, expand = 1)
		#create canvas
		self.canvas = Tkinter.Canvas(self, relief = Tkinter.FLAT, background = "#D2D2D2",width = 800, height = 10000)
		self.canvas.pack(side = Tkinter.TOP, anchor = Tkinter.NW, padx = 10, pady = 10)
		self.canvas.tag_bind("JumpToLine", "<ButtonPress-1>", self.openExpandedCode)
		self.canvas.tag_bind("HasDetails", "<Enter>", self.showToolTip)
		self.canvas.tag_bind("HasDetails", "<Leave>", self.hideToolTip)
		
	def loadIcons(self):
		self.icons = {}
		for iType in ["branch","db","info","module","multi","process","start"]:
			for state in ["idle","hover","click"]:
				self.icons[iType+"-"+state] = ImageTk.PhotoImage(file=CONST.ICONS + iType + "-" + state +".png")
				
	def newBlock(self,node,x,y):
		tags = ("JumpToLine","HasDetails")
		
		objId = self.canvas.create_image(x,y,image=self.icons[node.idleIcon],activeimage=self.icons[node.hoverIcon],tags=tags)
		textId = self.canvas.create_text(x,y,text=node.iconText(),font=CONST.FONT,fill="#000000",state=Tkinter.DISABLED)
		
		self.nodeDict[objId] = node
		
	def joiningLine(self,prevX,prevY,curX,curY,bend=False):
		tags = "Lines"
		lineId = False
		if bend == "N":
			midY = (prevY + curY)/2
			lineId = self.canvas.create_line(prevX,prevY,prevX,midY,curX,midY,curX,curY,fill="#000000",tags=tags)
		elif bend == "7":
			lineId = self.canvas.create_line(prevX,prevY,curX,prevY,curX,curY,fill="#000000",tags=tags)
		elif bend == "C":
			outX = CONST.BRANCHWIDTH/2 - CONST.BRANCHSPACE/2
			lineId = self.canvas.create_line(prevX,prevY,prevX-outX,prevY,curX-outX,curY,curX,curY,fill="#000000",tags=tags)
		elif bend == "-C":
			outX = CONST.BRANCHWIDTH/2 - CONST.BRANCHSPACE/2
			lineId = self.canvas.create_line(prevX,prevY,prevX+outX,prevY,curX+outX,curY,curX,curY,fill="#000000",tags=tags)
		else:
			lineId = self.canvas.create_line(prevX,prevY,curX,curY,fill="#000000",tags=tags)
			
		self.canvas.tag_lower(tags)
		return lineId
	
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
	for node in nodeList:
		if node.__class__ is nodes.ParaNode:
			continue
		
		
		if node.__class__ is nodes.NonLoopBranch:
			curX, curY = createFlowChart(chartWindow,node.branch,curX,curY)
		else:
			prevX, prevY = curX, curY
			curY += CONST.BLOCKHEIGHT
			chartWindow.joiningLine(prevX,prevY,curX,curY)
			chartWindow.newBlock(node,curX,curY)
		
		if node.__class__ is nodes.LoopBranch:
			retX, retY = createFlowChart(chartWindow,node.branch,curX,curY)
			chartWindow.joiningLine(curX,curY,retX,retY,"-C")
			
			curY = retY
		
		
		if node.__class__ is nodes.IfNode:
			prevX, prevY = curX, curY
			
			curXT = curX - node.branch[True].width()/2
			curYT = curY + CONST.BLOCKHEIGHT
			chartWindow.joiningLine(prevX,prevY,curXT,curYT,"7")
			chartWindow.newBlock(node.branch[True],curXT,curYT)
			curXT, curYT = createFlowChart(chartWindow,node.branch[True].branch,curXT,curYT)
			
			
			curXF = curX + node.branch[False].width()/2
			curYF = curY + CONST.BLOCKHEIGHT
			chartWindow.joiningLine(prevX,prevY,curXF,curYF,"7")
			chartWindow.newBlock(node.branch[False],curXF,curYF)
			curXF, curYF = createFlowChart(chartWindow,node.branch[False].branch,curXF,curYF)
			
			if curYT < curYF:
				chartWindow.joiningLine(curXT,curYT,curXT,curYF)
			elif curYF < curYT:
				chartWindow.joiningLine(curXF,curYT,curXF,curYF)
			chartWindow.joiningLine(curXF,curYF,curXT,curYT)
			
			curY = curYT
			
		
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
			
			prevX, prevY = curX, curY
			branchEndPoints = []
			
			if len(arrangedWhen) % 2 == 1:
				newNode = arrangedWhen.pop()
				curXT = curX - 0
				curYT = curY + CONST.BLOCKHEIGHT
				chartWindow.joiningLine(prevX,prevY,curXT,curYT)
				chartWindow.newBlock(newNode,curXT,curYT)
				endPoints = createFlowChart(chartWindow,newNode.branch,curXT,curYT)
				branchEndPoints.append(endPoints)
			
			width = node.width()
			if len(arrangedWhen):
				reduceWidth = 0
				
				newNode = arrangedWhen.pop(0)
				branchWidth = newNode.width()
				reduceWidth += branchWidth
				curXT = curX - width/2 + branchWidth/2
				curYT = curY + CONST.BLOCKHEIGHT
				chartWindow.joiningLine(prevX,prevY,curXT,curYT,"7")
				chartWindow.newBlock(newNode,curXT,curYT)
				endPoints = createFlowChart(chartWindow,newNode.branch,curXT,curYT)
				branchEndPoints.append(endPoints)
				
				
				newNode = arrangedWhen.pop(0)
				branchWidth = newNode.width()
				reduceWidth += branchWidth
				curXT = curX + width/2 - branchWidth/2
				curYT = curY + CONST.BLOCKHEIGHT
				chartWindow.joiningLine(prevX,prevY,curXT,curYT,"7")
				chartWindow.newBlock(newNode,curXT,curYT)
				endPoints = createFlowChart(chartWindow,newNode.branch,curXT,curYT)
				branchEndPoints.append(endPoints)
				
				
				width -= reduceWidth
			
			if len(arrangedWhen):
				whenSpacing = (CONST.ICONWIDTH / 2)/(len(arrangedWhen) - 1 + (len(node.whenList) % 2))
				whenSpacingStart = CONST.ICONWIDTH / 2
			while len(arrangedWhen):
				reduceWidth = 0
				
				newNode = arrangedWhen.pop(0)
				branchWidth = newNode.width()
				reduceWidth += branchWidth
				curXT = curX - width/2 + branchWidth/2 - CONST.BRANCHWIDTH
				curYT = curY + CONST.BLOCKHEIGHT
				chartWindow.joiningLine(prevX - whenSpacingStart,prevY,curXT,curYT,"N")
				chartWindow.newBlock(newNode,curXT,curYT)
				endPoints = createFlowChart(chartWindow,newNode.branch,curXT,curYT)
				branchEndPoints.append(endPoints)
				
				newNode = arrangedWhen.pop(0)
				branchWidth = newNode.width()
				reduceWidth += branchWidth
				curXT = curX + width/2 - branchWidth/2 + CONST.BRANCHWIDTH
				curYT = curY + CONST.BLOCKHEIGHT
				chartWindow.joiningLine(prevX + whenSpacingStart,prevY,curXT,curYT,"N")
				chartWindow.newBlock(newNode,curXT,curYT)
				endPoints = createFlowChart(chartWindow,newNode.branch,curXT,curYT)
				branchEndPoints.append(endPoints)
				
				width -= reduceWidth
				whenSpacingStart -= whenSpacing
				
			minX =  99999999
			maxX = maxY = -1
			for point in branchEndPoints:
				if point[0] < minX:
					minX = point[0]
			for point in branchEndPoints:
				if point[0] > maxX:
					maxX = point[0]
			for point in branchEndPoints:
				if point[1] > maxY:
					maxY = point[1]
			
			for point in branchEndPoints:
				if point[1] != maxY:
					chartWindow.joiningLine(point[0],point[1],point[0],maxY)
			chartWindow.joiningLine(minX,maxY,maxX,maxY)
			
			curY = maxY
				
	
	return curX, curY


def main(component="VIID246"):
	nodes = createTree.getChart(component)
	root = Tkinter.Tk()
	#root.geometry('800x600+10+50')
	app = ChartWindow(root,component)
	createFlowChart(app,nodes,300,20)
	app.mainloop()
	#root.destroy()
	
	return nodes

n=main()
