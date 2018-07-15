import constants as CONST
allKeyWords = []
mainVerbs = []

def loadDATA(inputFileName):
	f = []
	try:
		iFile = open(CONST.DATA+inputFileName+".txt")

		f = [l.rstrip() for l in iFile]
		iFile.close()
	except IOError:
		f = []
	return f

def extractKeywords(inputLine):
	if inputLine[-1] == ".":
		inputLine = inputLine[:-1]
	words = inputLine.split()
	keyWords = [w for w in words if w in allKeyWords]
	return keyWords
	
def extractNonKeywords(inputLine):
	if inputLine[-1] == ".":
		inputLine = inputLine[:-1]
	words = inputLine.split()
	nonKeyWords = [w for w in words if w not in allKeyWords]
	return nonKeyWords
	
def isKeyword(word):
	if word in allKeyWords:
		return True
	else:
		return False
		
def isMainVerb(word):
	if word in mainVerbs:
		return True
	else:
		return False

allKeyWords = loadDATA("Keywords")
mainVerbs = loadDATA("MainKeywords")
