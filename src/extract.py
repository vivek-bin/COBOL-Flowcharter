import fileaccess as FA

pd={}
vd={}

def loadFile(fName):
	f = FA.loadFile(FA.PROCESSING,fName)
	f = [l[8:] for l in f]
	return f

def extractParaNames(f):
	paras = []
	for i in range(len(f)):
		if f[i].startswith("procedure division"):
			break
	for j in range(i+1,len(f)):
		if f[j][0] != " ":
			paras.append(f[j])
	paras = [p[:-1] for p in paras]
	return paras
	
def extractVariableNames(f):
	vars = []
	for i in range(len(f)):
		if f[i].startswith("data division"):
			break
	for j in range(i+1,len(f)):
		l = f[j].strip()
		if l[:2].isdigit():
			try:
				vars.append(l.split()[1])
			except  IndexError:
				if l[2] != ".":
					raise IndexError
		if f[j].startswith("procedure division"):
			break

	for i in range(len(vars)):
		if vars[i][-1] == ".":
			vars[i] = vars[i][:-1]
	
	return vars

def appendDATA(inputFileName,inputList):
	try:
		iFile = open(FA.CONST.DATA+inputFileName+".txt","a")

		iFile.writelines(["%s\n" % item  for item in inputList])
		iFile.close()
		return False
	except IOError:
		return False
		
def getData(fn):
	f = loadFile(fn)
	p = extractParaNames(f)
	v = extractVariableNames(f)

	
	for a in p:
		pd[a] = True
	for a in v:
		vd[a] = True
	
	#appendDATA("paras",p)
	#appendDATA("vars",v)

		
def a(start,end):
	FA.openLib(FA.PROCESSING)
	l = FA.fileListLib(FA.PROCESSING)
	processingList = l[start:end]
		
	for fileName in processingList:
		getData(fileName)
	FA.closeLib(FA.PROCESSING)
	
	appendDATA("paras",pd.keys())
	appendDATA("vars",vd.keys())
	
a(0,632300)
