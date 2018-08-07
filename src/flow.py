from Tkinter import Tk, Canvas, Frame, Button
from Tkinter import BOTH, W, NW, SUNKEN, TOP, X, FLAT, LEFT
from PIL import Image, ImageTk
import tooltip

class ButtonProperties:
	def __init__(self):
		self.button = False
		self.buttonWindow = False
		self.buttonTooltip = False

class Example(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		self.lines=[]
		self.initUI()

	def addButton(self,text,x,y,command,hoverMsg=False):
		newButton = ButtonProperties()
		
		newButton.button = Button(self.canvas, text = text, command = command,anchor = W)
		newButton.button.configure(image=self.img, compound="bottom", width = 90, activebackground = "#33B5E5",relief = FLAT)
		newButton.buttonWindow = self.canvas.create_window(x, y, anchor=NW, window=newButton.button)
		if hoverMsg:
			newButton.buttonTooltip = tooltip.CreateToolTip(newButton.button, hoverMsg)
		
		return newButton
		
		
	def createLine(self,x1,y1,x2,y2,fill="red",width=5):
		def f1(e):
			self.canvas.itemconfigure(self.canvas.find_withtag("current")[0],width=9)
		def f2(e):
			self.canvas.itemconfigure(self.canvas.find_withtag("current")[0],width=5)
		line = self.canvas.create_line(x1, y1, x2, y2, fill=fill,width=width)
		#self.canvas.tag_bind(line, '<ButtonPress-1>', f1)
		print self.canvas.tag_bind(line, '<Enter>', f1)
		print self.canvas.tag_bind(line, '<Leave>', f2)
		#self.lines.append(line)
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
		
def main():
	root = Tk()
	root.geometry('800x600+10+50')
	app = Example(root)
	app.mainloop()
	root.destroy()

main()