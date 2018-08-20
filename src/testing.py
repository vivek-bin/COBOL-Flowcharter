import createTree
import fileaccess as fa
import os
import time
import tooltip
import constants as CONST
	
def t9(component="VIID246"):
	startTime = time.time()
	
	log = fa.loadDATA("log")
	log = [l[8:] for l in log]
	
	for i in range(len(log)):
		l = log[i]
		if l.strip() == "exit.":
			ln = log[i+1]
			if ln[4] != " ":
				print i 
				break
	
	print (time.time() - startTime)
	
	
class c1:
	a=2
	def __init__(self):
		print self.a
		self.a+=3
		print self.a
		
class c2(c1):
	a=22
	def __init__(self):
		c1.__init__(self)
		

def t2():
	b=c1()
	print b.a
	b.a=4
	print b.a
	
	b=c2()
	print b.a
	b.a=44
	print b.a
	
	b=c1()
	print b.a
	b.a=4
	print b.a
	
t2()