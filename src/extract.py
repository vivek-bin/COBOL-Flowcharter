import fileaccess as FA
import filemod

pd={}
vd={}

def loadFile(fName):
	f = FA.loadFile(FA.EXPANDED,fName)
	f = filemod.processingFile(f)
	f = filemod.processingFileClean(f)
	
	f = [l[8:] for l in f]
	return f

def extractParaNames(f):
	paras = []
	for i in range(len(f)):
		if f[i].startswith("procedure division"):
			break
	for j in range(i+1,len(f)):
		if f[j][0] != " " and f[j].find(" ") == -1:
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
	p = []
	v = []
	f = loadFile(fn)
	p = extractParaNames(f)
	#v = extractVariableNames(f)

	
	for a in p:
		pd[a] = True
	for a in v:
		vd[a] = True
	

		
def a(start,end):
	FA.openLib(FA.EXPANDED)
	l = FA.fileListLib(FA.EXPANDED)
	processingList = l[start:end]
		
	for fileName in processingList:
		getData(fileName)
	FA.closeLib(FA.EXPANDED)
	
	appendDATA("paras",pd.keys())
	appendDATA("vars",vd.keys())
	
#a(0,632300)

def getBases():
	path = "D:\\CAI auto\\New folder\\data\\"
	v = open(path + "v.txt")
	vl = [e.rstrip().lower() for e in v]
	v.close()
	p = open(path + "p.txt")
	pl = [e.rstrip().lower() for e in p]
	p.close()
	ew = open(path + "ew.txt")
	ewl = [e.rstrip().lower() for e in ew]
	ew.close()
	fw = open(path + "fw.txt")
	fwl = [e.rstrip().lower() for e in fw]
	fw.close()


	ch = {}


	for ele in vl:
		for chr in ele:
			ch[chr] = True
			
	for ele in pl:
		for chr in ele:
			ch[chr] = True
			
	for ele in ewl:
		for chr in ele:
			ch[chr] = True
			
	for ele in fwl:
		for chr in ele:
			ch[chr] = True
			
			
			
	allChars = ch.keys()

	print(len(allChars))
	
	return allChars
	
getBases()