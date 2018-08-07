import constants as CONST
import os
from Tkinter import Tk, Canvas, Frame, Button
from Tkinter import BOTH, W, NW, SUNKEN, TOP, X, FLAT, LEFT
from PIL import Image, ImageTk
import tooltip

class Chart:
	def __init__(self,component,canvas):
		self.lineNumbers = {}
		self.details = {}
		self.component = component
		canvas.tag_bind("JumpToLine", "<ButtonPress-1>", self.openExpandedCode)
		
	def startButton(self,canvas,x,y):
		recX1 = x-20
		recX2 = x+20
		recY1 = y-7
		recY2 = y+7
		return canvas.create_oval(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")
		#self.lineNumbers[oval] = lineNo

	def processButton(self,canvas,x,y):
		recX1 = x-20
		recX2 = x+20
		recY1 = y-7
		recY2 = y+7
		return canvas.create_rectangle(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def infoButton(self,canvas,x,y):
		recX1 = x-7
		recX2 = x+7
		recY1 = y-7
		recY2 = y+7
		return canvas.create_oval(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def multiBranchButton(self,canvas,x,y):
		recX1 = x-20
		recX2 = x-7
		recX3 = x+7
		recX4 = x+20
		recY1 = y-7
		recY2 = y+7
		points = [recX1,y,recX2,recY1,recX3,recY1,recX4,y,recX3,recY2,recX2,recY2]
		return canvas.create_polygon(points,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def branchButton(self,canvas,x,y):
		recX1 = x-7
		recX2 = x+7
		recY1 = y-7
		recY2 = y+7
		points = [x,recY1,recX2,y,x,recY2,recX1,y]
		return canvas.create_polygon(points,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def moduleButton(self,canvas,x,y):
		recX1 = x-20
		recX2 = x+20
		recY1 = y-7
		recY2 = y+7
		canvas.create_rectangle(recX1,recY1,recX2,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")
		return canvas.create_rectangle(recX1+3,recY1,recX2-3,recY2,outline="#cc6666",fill="#cc6666",activefill="#993333",tags="JumpToLine")

	def openExpandedCode(event):
		canvas = event.widget
		objId = canvas.find_withtag("current")[0]
		
		lineNo = self.lineNumbers[objId]
		componentLocation = '"' + fileaccess.extractExpandedFile(self.component) + '"'
		lineNo = "-n" + str(lineNo)
		command = CONST.NPLOCATION + " " +  componentLocation + " " + lineNo
		os.system(command)
		
class ChartCanvas(Canvas):
	def __init(self):
		Canvas.__init__(self)
		
class ChartWindow(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		self.initUI()
	
	def createLine(self,x1,y1,x2,y2,fill="red",width=5):
		def f1(e):
			self.canvas.itemconfigure(self.canvas.find_withtag("current")[0],width=9)
		def f2(e):
			self.canvas.itemconfigure(self.canvas.find_withtag("current")[0],width=5)
		line = self.canvas.create_line(x1, y1, x2, y2, fill=fill,width=width)
		#self.canvas.tag_bind(line, '<ButtonPress-1>', f1)
		print self.canvas.tag_bind(line, '<Enter>', f1)
		print self.canvas.tag_bind(line, '<Leave>', f2)
		#tooltip.CreateToolTip(line, "sgvgwegrwergwre")
	
	def initUI(self):
		self.parent.title("Layout Test")
		self.config(bg = '#F0F0F0')
		self.pack(fill = BOTH, expand = 1)
		#create canvas
		self.canvas = Canvas(self, relief = FLAT, background = "#D2D2D2",width = 180, height = 500)
		self.canvas.pack(side = TOP, anchor = NW, padx = 10, pady = 10)
		
		self.img = ImageTk.PhotoImage(Image.open("D:\\Profiles\\vbindal\\Downloads\\io-flow.png"))
		
		#add quit button
		
		self.createLine(0,100,100,0)
		self.createLine(0,0,200,200)
		#self.addButton("quit",10,10,self.quit,"rhnrhsreth")
		self.addButton("quit",10,90,self.quit)
		
def main(component="VIID246"):
	root = Tk()
	root.geometry('800x600+10+50')
	app = Example(root,component)
	app.mainloop()
	root.destroy()

main()