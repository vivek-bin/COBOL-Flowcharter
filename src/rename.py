import os
path  = "D:\\Profiles\\vbindal\\Documents\\MTP\\"
SRCELIB  = path+"SRCELIB\\"
COPYLIB  = path+"COPYLIB\\"
INCLUDE  = path+"INCLUDE\\"
li=os.listdir(SRCELIB)
for l in li:
	os.rename(SRCELIB+l,SRCELIB+l[20:]+".txt")
li=os.listdir(COPYLIB)
for l in li:
	os.rename(COPYLIB+l,COPYLIB+l[20:]+".txt")
li=os.listdir(INCLUDE)
for l in li:
	os.rename(INCLUDE+l,INCLUDE+l[20:]+".txt")