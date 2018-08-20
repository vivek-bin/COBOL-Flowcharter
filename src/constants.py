
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

ZEROPAD = 8

FONT = ("League Gothic",3,"bold")
TOOLTIPFONT = ("Times New Roman",7,"normal")
NPLOCATION = "C:\\Program Files\\Notepad++\\notepad++.exe"

TOOLTIPSIZE = 50

ZOOM = 0.3
BRANCHSPACE = 10*ZOOM
BLOCKSPACE = 0*ZOOM

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
IGNOREDMODULES = [i.lower() for i in IGNOREDMODULES]
IGNOREDPARAS = loadCustomization("ignore-para")
IGNOREDPARAS = [i.lower() for i in IGNOREDPARAS]
