import os
import constants as CONST

def renameLib(lib):
	li=os.listdir(lib)
	for l in li:
		os.rename(lib+l,lib+l[20:]+".txt")

def renameSRCELIB():
	renameLib(CONST.SRCELIB)
	
def renameCOPYLIB():
	renameLib(CONST.COPYLIB)
	
def renameINCLUDE():
	renameLib(CONST.INCLUDE)
	
def renameAll():
	renameSRCELIB()
	renameCOPYLIB()
	renameINCLUDE()