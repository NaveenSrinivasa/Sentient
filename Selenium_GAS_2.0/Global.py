# test result status
FAIL = 0
PASS = 1
SKIP = 2
NA = 3
EXCEPTION = 4

# path to the mtf file where device information is held
mtfPath = ''
reportPath = ''
testResourcePath = ''
deviceFolderPath = ''
downloadFolder = ''

# dictionary of serial:deviceInfo
deviceList = []
deviceInfo = {}

# track which devices are on ample and which are not
offDevs = []    # not on Ample
onDevs = []     # on Ample

driver = ''
xpaths = {}

#SGW and Network Group Dictionary
sgw = []

