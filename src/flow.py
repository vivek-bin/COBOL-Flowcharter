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
		self.canvas.tag_bind("ShowDetails", "<Enter>", self.showToolTip)
		self.canvas.tag_bind("HideDetails", "<Leave>", self.hideToolTip)
		
	
	def newNode(self,node,x,y):
		if node.__class__ is nodes.ParaNode:
			objId = self.infoButton(x,y)
			
		self.nodeDict[objId] = node
			
		
	
	def startStopButton(self,x,y,text="STOP"):
		recX1 = x-20/2
		recX2 = x+20/2
		recY1 = y-7/2
		recY2 = y+7/2
		
		oval = self.canvas.create_oval(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")
		textLabel = self.canvas.create_text(x,y,text=text,font=CONST.FONT,fill="#000000")
		textBg = self.canvas.create_rectangle(self.canvas.bbox(textLabel),fill="white")
		self.canvas.tag_lower(textBg,textLabel)
		
	def processButton(self,x,y):
		recX1 = x-20
		recX2 = x+20
		recY1 = y-7
		recY2 = y+7
		return self.canvas.create_rectangle(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def infoButton(self,x,y):
		recX1 = x-7
		recX2 = x+7
		recY1 = y-7
		recY2 = y+7
		return self.canvas.create_oval(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def multiBranchButton(self,x,y):
		recX1 = x-20
		recX2 = x-7
		recX3 = x+7
		recX4 = x+20
		recY1 = y-7
		recY2 = y+7
		points = [recX1,y,recX2,recY1,recX3,recY1,recX4,y,recX3,recY2,recX2,recY2]
		return self.canvas.create_polygon(points,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def branchButton(self,x,y):
		recX1 = x-7
		recX2 = x+7
		recY1 = y-7
		recY2 = y+7
		points = [x,recY1,recX2,y,x,recY2,recX1,y]
		return self.canvas.create_polygon(points,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def moduleButton(self,x,y):
		recX1 = x-20
		recX2 = x+20
		recY1 = y-7
		recY2 = y+7
		self.canvas.create_rectangle(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")
		return self.canvas.create_rectangle(recX1+3,recY1,recX2-3,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

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
	
	
	
def main(component="VIID246"):
	root = Tkinter.Tk()
	root.geometry('800x600+10+50')
	app = ChartWindow(root,component)
	app.mainloop()
	root.destroy()

main()