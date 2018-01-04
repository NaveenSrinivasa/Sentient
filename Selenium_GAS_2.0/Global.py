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

# dictionary of serial:deviceInfo
devices = {}

# track which devices are on ample and which are not
offDevs = []    # not on Ample
onDevs = []     # on Ample

# log
logPath = ''
info = ''
startLogPath = ''

driver = ''
xpaths = {}

