
#paths
PATH = "D:\\CAAGIS flow tracker\\"

MTP = PATH + "MTP\\"
MTPZIP = PATH + "MTP ZIP\\"
PROJECT = PATH + "PROJECT\\"

SRCELIB = MTP + "SRCELIB\\"
COPYLIB = MTP + "COPYLIB\\"
INCLUDE = MTP + "INCLUDE\\"
EXPANDED = MTP + "EXPANDED\\"
PROCESSING = MTP + "PROCESSING\\"
TREES = MTP + "TREES\\"

SRCEZIP = MTPZIP + "SRCELIB.zip"
COPYZIP = MTPZIP + "COPYLIB.zip"
INCZIP = MTPZIP + "INCLUDE.zip"
EXPANDEDZIP = MTPZIP + "EXPANDED.zip"
PROCESSINGZIP = MTPZIP + "PROCESSING.zip"
TREESZIP = MTPZIP + "TREES.zip"

DATA = PROJECT + "DATA\\"

#line number tracking
ZEROPAD = 8


#flowchart values
TOOLTIPSIZE = 50

NPLOCATION = "C:\\Program Files\\Notepad++\\notepad++.exe"


ZOOM = 1
BRANCHSPACE = 30

FONT = ("League Gothic",9,"bold")
TOOLTIPFONT = ("Times New Roman",7,"normal")

ICONS = PROJECT + "icons\\"


FLOWCUSTOM = DATA + "flowchart-customize\\"
def loadCustomization(inputFileName):
	f = []
	try:
		iFile = open(FLOWCUSTOM+inputFileName+".txt")

		f = [l.rstrip() for l in iFile]
		iFile.close()
	except IOError:
		f = []
	return f

IGNOREDMODULES = loadCustomization("ignore-program")
IGNOREDMODULES = [i.strip().lower() for i in IGNOREDMODULES]
IGNOREDPARAS = loadCustomization("ignore-para")
IGNOREDPARAS = [i.strip().lower() for i in IGNOREDPARAS]
