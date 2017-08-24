# test result status
FAIL = 0
PASS = 1
SKIP = 2
NA = 3

# path to the mtf file where device information is held
mtfPath = ''

# dictionary of serial:deviceInfo
devices = {}

# track which devices are on ample and which are not
offDevs = []    # not on Ample
onDevs = []     # on Ample

# log
logPath = ''
loglevel = ''
startLogPath = ''

gusername = ''

# pexpect shells
pxChild = {}

# path to the tmp file
tmpPath = ''

# screen shot folder path
screenshots_path = ''

# current test cases name
currenttest_name = ''

# path to newly created profiles name file
tmpnewprofilesPath = ''

driver = ''
xpaths = {}

#userprofile
Li_User_Profile = '/home/balachander'
Wi_User_Profile = 'C:/Users/bbas0001'

