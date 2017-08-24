from Utilities_Ample import *
from Utilities_Framework import *


def CheckDefaultTableColumns():
	LineMonitoringFault = ['Timestamp', 'Detector', 'Phase', 'Fault State', 'Type', 'Sub Type', 'Waveform Status']
	LineMonitoringDNP3 = ['TimeStamp', 'cndIrms', 'cndTemp', 'activeUpTime', 'activePowerLowTime', 'energyReserveVoltage']
	DeviceManConfig = ['Serial #', 'Phase', 'Device Status', 'Profile Name', 'SW Ver', 'Actions']
	DeviceManUpgrade = ['Serial #', 'Phase', 'Status', 'SW Ver', 'OTAP Status' 'Actions']
	CurrentJobsConfig = ["Site ID", "Serial No", "Status", 'SW Version', 'Job Status']


def CheckSearchTextBoxes(input_file_path=None):
	if not input_file_path:
		testComment = 'Test is missing mandatory parameter(s).'
		printFP('INFO - ' + testComment)
		return Global.FAIL, 'TEST FAIL - ' + testComment

	printFP("INFO - Starting check on Device Management Config Page")

	GoToDevMan()


