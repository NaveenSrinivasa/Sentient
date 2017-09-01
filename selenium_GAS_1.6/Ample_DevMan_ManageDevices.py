import Global
import time
import pandas as pd
import csv
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
from Ample_DevMan import *
from Utilities_Framework import *
from Utilities_Ample import *


def SelectANodeToShowAllDevicesUnderTheNode(input_file_path):
	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(2)
		printFP("INFO - Reached Manage Devices screen")
		printFP("INFO - Clicking on the Root node")
		GetRootNode()
		time.sleep(1)
		table = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
		devtbody = GetElement(table, By.TAG_NAME, "tbody")
		deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
		devicenamesfromtable = []
		for row in deviceslist:
			devicedetails = GetElement(row, By.XPATH, 'td[2]')
			devicename = devicedetails.text
			devicenamesfromtable.append(devicename)
		print devicenamesfromtable

		#Reading the Serial Number from the MTF File
		column = pd.read_csv(input_file_path) 
		devicnamesfromcsv = list(column['Serial Number'])
		print devicnamesfromcsv

		#Validating the devices names both from UI and from the MTF File

		if all(str(x) in devicenamesfromtable for x in devicnamesfromcsv):
			testComment = 'TEST Pass - Device names matched'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST Fail - Device names NOT matched'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceSummaryData(input_file_path, wait_for_online=True):

	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to Sys Admin page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	#First line has to be online device.Reading the serial number of online device from the MTF File
	printFP('INFO - Reading the serial number of online device from csv')
	with open(input_file_path, 'rb') as f:
		rows = list(csv.reader(f))
		region_nameof_online_device = rows[1][0]
		substation_nameof_online_device = rows[1][1]
		feeder_nameof_online_device = rows[1][2]
		site_nameof_online_device = rows[1][3]
		device_nameof_online_device = rows[1][5]
		#printFP('INFO - Serial number of online device'), device_nameof_online_device

	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - MTF upload message: %s" % returnMessage)
	else:
		testComment = "MTF upload message: %s" % returnMessage
		printFP(testComment)
		return Global.FAIL, 'TEST FAIL - ' + testComment

	GoToDevMan()
	time.sleep(2)
	rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
	if rootElement.get_attribute('collapsed') == 'true':
		rootElement.click()
		time.sleep(2)
	GetRootNode()
	time.sleep(2)
	'''region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
	JustClick(region)
	time.sleep(1)'''

	GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
	time.sleep(1.5)
	region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
	JustClick(region)
	time.sleep(2)

	printFP('INFO - Checking for Online status')
	ping_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span[2]").click()
	time.sleep(2)
	initiate_ping = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Initiate Ping')]").click()
	time.sleep(2)
	close_button = GetElement(Global.driver, By.XPATH, "//button[contains(@class,'close')]").click()

	if wait_for_online:
		GoToDevMan()
		time.sleep(5)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(region_nameof_online_device, substation_nameof_online_device, feeder_nameof_online_device, site_nameof_online_device)
		if IsOnline(device_nameof_online_device):
			testComment = 'INFO - %s did come online and successfully uploaded'% device_nameof_online_device
			printFP(testComment)
		else:
			testComment = 'INFO - %s did not come online' % device_nameof_online_device
			printFP(testComment)

	#GoToDevMan()
	time.sleep(2)
	printFP('INFO - Clicking on the Root node')
	GetRootNode()
	time.sleep(1)
	printFP('INFO - Clicking on Device Summary Tab')
	#Click on Device Summary Tab
	devicesummary = GetElement(Global.driver, By.XPATH, "//li[@id='deviceSummary']").click()
	time.sleep(2)
	tabledevicesummary = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceSummary')]")
	devtbody = GetElement(tabledevicesummary, By.TAG_NAME, "tbody")
	deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
	#Empty Dictionary
	devicestatuscountfromtable = {}
	for row in deviceslist:
		devicestatus = GetElement(row, By.TAG_NAME, 'td').text
		if not 'Device' in devicestatus:
			devicecount = GetElement(row, By.XPATH, 'td[2]').text
			devicestatuscountfromtable[devicestatus] = devicecount
	print devicestatuscountfromtable

	printFP('INFO - Clicking on Device List Tab')
	deviceList = GetElement(Global.driver, By.XPATH, "//li[@id='deviceList']").click()
	time.sleep(1)
	tabledevicelist = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
	devtbody = GetElement(tabledevicelist, By.TAG_NAME, "tbody")
	deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
	countfromdevicelist = {}
	deviceoffline = 0
	deviceonline = 0
	for row in deviceslist:
		devicedetails = GetElement(row, By.XPATH, 'td[4]')
		status = GetElement(devicedetails, By.TAG_NAME, 'span')
		time.sleep(1)
		if 'ion-checkmark-circled' in status.get_attribute('class'):
			deviceonline += 1
		if 'ion-close-circled' in status.get_attribute('class'):
			deviceoffline += 1

	countfromdevicelist['ONLINE'] = deviceonline
	countfromdevicelist['OFFLINE'] = deviceoffline
	print countfromdevicelist

	printFP('INFO - Validating the status and count from device list and device summary')

	if all(int(devicestatuscountfromtable[x]) == int(countfromdevicelist[x]) for x in countfromdevicelist):
		testComment = 'TEST Pass - Device status and device count matched'
		printFP(testComment)
		return Global.PASS, testComment
	else:
		testComment = 'TEST Fail - Device status and device count NOT matched'
		printFP(testComment)
		return Global.FAIL, testComment


def AddDevicesViaActionButtonRegionLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(1)
		#GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		#time.sleep(0.5)
		printFP('INFO - Clicking on the Region to add the device via add button')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(1)
		printFP('INFO - Clicking on Add device button')
		Add_device = GetElement(Global.driver, By.XPATH, "//button[text()='Add Device']").click()
		time.sleep(2)
		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device encountered error at the Region level')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment


def AddDevicesViaActionButtonSubStationLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(1)
		#GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(0.5)
		printFP('INFO - Clicking on the SubStation to add the device via add button')
		sstation = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SUBSTATION-name')]")
		JustClick(sstation)
		time.sleep(2)
		printFP('INFO - Clicking on Add device button')
		Add_device = GetElement(Global.driver, By.XPATH, "//button[text()='Add Device']").click()
		time.sleep(2)
		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device encountered error at the Sub Station level')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def AddDevicesViaActionButtonFeederLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(2)
		'''GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(2)'''
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[3]").click()
		time.sleep(2)
		printFP('INFO - Clicking on the Feeder to add the device via add button')
		feeder = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'FEEDER-name')]")
		JustClick(feeder)
		time.sleep(2)
		printFP('INFO - Clicking on Add device button')
		Add_device = GetElement(Global.driver, By.XPATH, "//button[text()='Add Device']").click()
		time.sleep(2)
		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device encountered error at the Feeder level')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def AddDevicesViaActionButtonSiteLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(2)
		'''GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(2)'''
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[3]").click()
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[4]").click()
		time.sleep(2)
		printFP('INFO - Clicking on the Site to add the device via add button')
		site = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SITE-name')]")
		JustClick(site)
		time.sleep(2)
		printFP('INFO - Clicking on Add device button')
		Add_device = GetElement(Global.driver, By.XPATH, "//button[text()='Add Device']").click()
		time.sleep(2)
		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device encountered error at the Site level')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def AddDevicesContextMenuRegionLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(1)
		printFP('INFO - Clicking on the Region to add the device via context menu')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		printFP('INFO - Selecting Add device from the dropdown')
		RightClickElement(region)
		SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Add Device')
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device from the context menu encountered error at the Region level')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def AddDevicesContextMenuSubStationLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(1)
		#GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(0.5)
		printFP('INFO - Clicking on the SubStation to add the device via context menu')
		sstation = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SUBSTATION-name')]")
		JustClick(sstation)
		time.sleep(2)
		printFP('INFO - Selecting Add device from the dropdown')
		RightClickElement(sstation)
		SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Add Device')
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device encountered error at the Sub Station level from the context menu')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def AddDevicesContextMenuFeederLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(1)
		'''GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(2)'''
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[3]").click()
		time.sleep(2)
		printFP('INFO - Clicking on the Feeder to add the device via context menu')
		feeder = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'FEEDER-name')]")
		JustClick(feeder)
		time.sleep(2)
		printFP('INFO - Selecting Add device from the dropdown')
		RightClickElement(feeder)
		SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Add Device')
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device encountered error at the Feeder level')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def AddDevicesContextMenuSiteLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		#GetRootNode()
		time.sleep(1)
		'''GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(2)'''
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[3]").click()
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[4]").click()
		time.sleep(2)
		printFP('INFO - Clicking on the Site to add the device via add button')
		site = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SITE-name')]")
		JustClick(site)
		time.sleep(2)
		printFP('INFO - Selecting Add device from the dropdown')
		RightClickElement(site)
		SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Add Device')
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Filling out the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
		time.sleep(1.5)
		serialNumber.send_keys(deviceInfo["Serial Number"])

		productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
		productName.click()
		parentelement = GetElement(productName, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
		time.sleep(1.5)

		platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
		platform.click()
		parentelement = GetElement(platform, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
		macAddr.send_keys(deviceInfo["MAC Address"])

		sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
		sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

		sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
		sDNP.send_keys(deviceInfo["Sensor DNP Address"])

		dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
		ClearInput(dnpPort)
		dnpPort.send_keys(deviceInfo["DNP General Port"])

		swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
		swVer.click()
		parentelement = GetElement(swVer, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
		time.sleep(1.5)

		partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
		partNumber.send_keys(deviceInfo["SEI Part Number"])

		network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
		network.click()
		parentelement = GetElement(network, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
		time.sleep(1.5)

		commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
		commserver.click()
		parentelement = GetElement(commserver, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
		time.sleep(1.5)

		network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
		network_grp_name.click()
		parentelement = GetElement(network_grp_name, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
		time.sleep(5)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)


		if 'Device added successfully' in  msg:
			printFP('TEST PASS - Success message: '+ msg)
			return Global.PASS, 'TEST PASS - ' + msg

		else:
			testComment('TEST FAIL - Adding device encountered error at the Site level')
			printFP(testComment)
			return Global.FAIL , testComment

		
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def FieldNoteColumnToBeAddedToDeviceManagementMenuOptionList(input_file_path=None):
	if input_file_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	#returnMessage = 'The file has been uploaded successfully.'
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(1)
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
		time.sleep(2)

		fieldnote = GetElement(Global.driver, By.XPATH, "//span[text()='Field Notes']/preceding-sibling::input")
		if (fieldnote.is_selected()):
			printFP('INFO - Field note is already checked...Now unchecking')
			fieldnote.click()
			time.sleep(2)
		printFP('INFO - Field note is unchecked...Now checking')
		fieldnote.click()
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
		time.sleep(2)

		#Getting the Field Note value from the MTF File
		printFP('INFO - Reading the Field Note value from the Uploaded MTF File')
		column = pd.read_csv(input_file_path) 
		field_notes_from_csv = list(column['Field Notes'])
		print field_notes_from_csv

		#Getting the Field Note value from the table - UI
		printFP('INFO - Getting the Field note value from the UI')
		table = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
		devtbody = GetElement(table, By.TAG_NAME, "tbody")
		deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
		field_note_from_table = []
		for row in deviceslist:
			devicedetails = GetElement(row, By.XPATH, "//td[20]")
			field_notes = devicedetails.text
			field_note_from_table.append(field_notes)
		print field_note_from_table

		#Validating the field notes value both from UI and from the MTF File

		if all(str(x) in field_note_from_table for x in field_notes_from_csv):
			testComment = 'TEST Pass - Field Notes Value matched'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST Fail - Field Notes Value NOT matched'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def FieldNoteEmptyValue(input_file_path=None):
	if input_file_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	#returnMessage = 'The file has been uploaded successfully.'
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[1]").click()
		time.sleep(1)
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
		time.sleep(2)

		fieldnote = GetElement(Global.driver, By.XPATH, "//span[text()='Field Notes']/preceding-sibling::input")
		if (fieldnote.is_selected()):
			printFP('INFO - Field note is already checked...Now unchecking')
			fieldnote.click()
			time.sleep(2)
		printFP('INFO - Field note is unchecked...Now checking')
		fieldnote.click()
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
		time.sleep(2)

		#Getting the Field Note value from the MTF File
		printFP('INFO - Reading the Field Note value from the Uploaded MTF File')
		column = pd.read_csv(input_file_path)
		column = column.replace(np.nan, '', regex=True) 
		field_notes_from_csv = list(column['Field Notes'])
		print field_notes_from_csv


		#Getting the Field Note value from the table - UI
		printFP('INFO - Getting the Field note value from the UI')
		table = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
		devtbody = GetElement(table, By.TAG_NAME, "tbody")
		deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
		field_note_from_table = []
		for row in deviceslist:
			devicedetails = GetElement(row, By.XPATH, "//td[20]")
			field_notes = devicedetails.text
			field_note_from_table.append(field_notes)
		print field_note_from_table

		#Validating the field notes value both from UI and from the MTF File

		if all(str(x) in field_note_from_table for x in field_notes_from_csv):
			testComment = 'TEST Pass -Value of Field Notes is Empty - value same as in Uploaded MTF '
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST Fail - Value of Field Notes is NOT Empty -value is not same as Uploaded MTF '
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def FieldNoteLongValue(input_file_path=None):
	if input_file_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	#returnMessage = 'The file has been uploaded successfully.'
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[1]").click()
		time.sleep(1)
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
		time.sleep(2)

		fieldnote = GetElement(Global.driver, By.XPATH, "//span[text()='Field Notes']/preceding-sibling::input")
		if (fieldnote.is_selected()):
			printFP('INFO - Field note is already checked...Now unchecking')
			fieldnote.click()
			time.sleep(2)
		printFP('INFO - Field note is unchecked...Now checking')
		fieldnote.click()
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
		time.sleep(2)

		#Getting the Field Note value from the MTF File
		printFP('INFO - Reading the Field Note value from the Uploaded MTF File')
		column = pd.read_csv(input_file_path)
		#column = column.replace(np.nan, '', regex=True) 
		field_notes_from_csv = list(column['Field Notes'])
		print field_notes_from_csv

	

		#Getting the Field Note value from the table - UI
		printFP('INFO - Getting the Field note value from the UI')
		table = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
		devtbody = GetElement(table, By.TAG_NAME, "tbody")
		deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
		field_note_from_table = []
		for row in deviceslist:
			devicedetails = GetElement(row, By.XPATH, "//td[20]")
			field_notes = devicedetails.text
			field_note_from_table.append(field_notes)
		print field_note_from_table

		#Validating the field notes value both from UI and from the MTF File

		if all(str(x) in field_note_from_table for x in field_notes_from_csv):
			testComment = 'TEST Pass -Import MTF:Field Note can accept long values '
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST Fail -Import MTF:Field Note CANNOT accept long values'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def FieldNoteMaxCharacterValidation(input_file_path):
	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment
	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File")
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		errorpopup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		errormessage = GetElement(errorpopup, By.TAG_NAME,'p')
		errormessage.click()
		errormsg = errormessage.text.strip()
		errormsg = errormsg.replace('"','')
		errormsg = ''.join(errormsg.split('\n'))
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'Field Notes : Notes cannot exceed 255 characters in length' in errormsg:
			testComment = 'Test Pass - MTF Failed to Upload when Field note has more then 255 characters and proper error message is displayed on the UI'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'Test Fail - Expected error message is not displayed on the UI when filed note value has more then 255 characters'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceManagementManageDevicesEditDevice(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		rootElement.click()
		time.sleep(1)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(1)
		printFP('INFO - Clicking on the Region')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		edit_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span").click()
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Editing the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'phaseListSelection')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'editDevice_form')]/descendant::button")
		time.sleep(3)

		try:
			msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
			msg = GetElement(msgBox, By.XPATH, 'div/span').text
			if msgBox:
				if'Device details updated successfully' in  msg:
					printFP('TEST PASS - Success message: '+ msg)
					closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
					JustClick(closebutton)
					time.sleep(2)
					return Global.PASS, 'TEST PASS - ' + msg
				else:
					testComment('TEST FAIL - Failed to update the device details')
					printFP(testComment)
					return Global.FAIL , testComment
			else:
				testComment('TEST FAIL - Success message is not present in the pop up..something wrong')
				printFP(testComment)
				return Global.FAIL , testComment
		except:
			testComment = 'TEST FAIL - Success alert message is not present in the pop up..something wrong'
			closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
			JustClick(closebutton)
			time.sleep(2)
			printFP(testComment)
			return Global.FAIL , testComment

	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def AddDevicesViaActionButtonOrganizationNodeLevel(input_file_path=None, device_detail_path=None):
    if input_file_path == None or device_detail_path == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    printFP('INFO - Going to System Admin Page')
    GoToSysAdmin()
    time.sleep(2)
    printFP('INFO - Uploading the MTF File')
    UploadMTF(input_file_path)
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(2)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "The file has been uploaded successfully." in returnMessage:
        printFP("INFO - Going to Device Management screen")
        GoToDevman()
        time.sleep(1)
        rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
        rootElement.click()
        time.sleep(2)
        printFP('INFO - Clicking on the Organization node to add the device via add button')
        organization_node = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'ROOTNODE-name')]")
        JustClick(organization_node)
        time.sleep(1)
        printFP('INFO - Clicking on Add device button')
        Add_device = GetElement(Global.driver, By.XPATH, "//button[text()='Add Device']").click()
        time.sleep(2)
        deviceInfo = ParseJsonInputFile(device_detail_path)
        printFP('INFO - Filling out the device details')

        region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
        region.click()
        parentelement = GetElement(region, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
        time.sleep(1.5)

        subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
        subStation.click()
        parentelement = GetElement(subStation, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
        time.sleep(1.5)

        feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
        feeder.click()
        parentelement = GetElement(feeder, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
        time.sleep(1.5)

        site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
        site.click()
        parentelement = GetElement(site, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
        time.sleep(1.5)

        serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
        time.sleep(1.5)
        serialNumber.send_keys(deviceInfo["Serial Number"])

        productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
        productName.click()
        parentelement = GetElement(productName, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
        time.sleep(1.5)

        platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
        platform.click()
        parentelement = GetElement(platform, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
        time.sleep(1.5)

        phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
        phase.click()
        parentelement = GetElement(phase, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
        time.sleep(1.5)

        macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
        macAddr.send_keys(deviceInfo["MAC Address"])

        sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
        sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

        sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
        sDNP.send_keys(deviceInfo["Sensor DNP Address"])

        dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
        ClearInput(dnpPort)
        dnpPort.send_keys(deviceInfo["DNP General Port"])

        swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
        swVer.click()
        parentelement = GetElement(swVer, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
        time.sleep(1.5)

        partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
        partNumber.send_keys(deviceInfo["SEI Part Number"])

        network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
        network.click()
        parentelement = GetElement(network, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
        time.sleep(1.5)

        commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
        commserver.click()
        parentelement = GetElement(commserver, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
        time.sleep(1.5)

        network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
        network_grp_name.click()
        parentelement = GetElement(network_grp_name, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
        time.sleep(1.5)
        ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
        time.sleep(5)

        msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
        msg = GetElement(msgBox, By.XPATH, 'div/span').text

        closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
        JustClick(closebutton)
        time.sleep(2)
        if 'Device added successfully' in  msg:
            printFP('TEST PASS - Success message: '+ msg)
            return Global.PASS, 'TEST PASS - ' + msg

        else:
            testComment('TEST FAIL - Adding device encountered error at the organization node')
            printFP(testComment)
            return Global.FAIL , testComment
    else:
        testComment = 'TEST Fail - Failed to Upload MTF File'
        printFP(testComment)
        return Global.FAIL, testComment

def AddDevicesContextMenuOrganizationNodeLevel(input_file_path=None, device_detail_path=None):
    if input_file_path == None or device_detail_path == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    printFP('INFO - Going to System Admin Page')
    GoToSysAdmin()
    time.sleep(2)
    printFP('INFO - Uploading the MTF File')
    UploadMTF(input_file_path)
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(2)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "The file has been uploaded successfully." in returnMessage:
        printFP("INFO - Going to Device Management screen")
        GoToDevman()
        time.sleep(1)
        rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
        rootElement.click()
        time.sleep(2)
        printFP('INFO - Clicking on the Organization node to add the device via context menu')
        organization_node = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'ROOTNODE-name')]")
        JustClick(organization_node)
        time.sleep(2)
        printFP('INFO - Selecting Add device from the dropdown')
        RightClickElement(organization_node)
        SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Add Device')
        time.sleep(2)

        deviceInfo = ParseJsonInputFile(device_detail_path)
        printFP('INFO - Filling out the device details')

        region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
        region.click()
        parentelement = GetElement(region, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
        time.sleep(1.5)

        subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
        subStation.click()
        parentelement = GetElement(subStation, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
        time.sleep(1.5)

        feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
        feeder.click()
        parentelement = GetElement(feeder, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
        time.sleep(1.5)

        site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
        site.click()
        parentelement = GetElement(site, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
        time.sleep(1.5)

        serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
        time.sleep(1.5)
        serialNumber.send_keys(deviceInfo["Serial Number"])

        productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
        productName.click()
        parentelement = GetElement(productName, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
        time.sleep(1.5)

        platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
        platform.click()
        parentelement = GetElement(platform, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
        time.sleep(1.5)

        phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
        phase.click()
        parentelement = GetElement(phase, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
        time.sleep(1.5)

        macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
        macAddr.send_keys(deviceInfo["MAC Address"])

        sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
        sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

        sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
        sDNP.send_keys(deviceInfo["Sensor DNP Address"])

        dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
        ClearInput(dnpPort)
        dnpPort.send_keys(deviceInfo["DNP General Port"])

        swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
        swVer.click()
        parentelement = GetElement(swVer, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
        time.sleep(1.5)

        partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
        partNumber.send_keys(deviceInfo["SEI Part Number"])

        network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
        network.click()
        parentelement = GetElement(network, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
        time.sleep(1.5)

        commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
        commserver.click()
        parentelement = GetElement(commserver, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Sensor Gateway Name'])
        time.sleep(1.5)

        network_grp_name = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
        network_grp_name.click()
        parentelement = GetElement(network_grp_name, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])
        time.sleep(1.5)

        ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
        time.sleep(5)

        msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
        msg = GetElement(msgBox, By.XPATH, 'div/span').text

        closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
        JustClick(closebutton)
        time.sleep(2)


        if 'Device added successfully' in  msg:
            printFP('TEST PASS - Success message: '+ msg)
            return Global.PASS, 'TEST PASS - ' + msg

        else:
            testComment('TEST FAIL - Adding device from the context menu encountered error at the Organizational node level')
            printFP(testComment)
            return Global.FAIL , testComment

        
    else:
        testComment = 'TEST Fail - Failed to Upload MTF File'
        printFP(testComment)
        return Global.FAIL, testComment

def DeviceManagementManageDevicesEditDuplicatePhaseForAnyDeviceWhichAreOnAnyRegionSubstationFeederAndSite(input_file_path=None, device_detail_path=None,input_file_path1=None,):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	UploadMTF(input_file_path1)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		rootElement.click()
		time.sleep(1)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(1)
		printFP('INFO - Clicking on the Region')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		edit_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span").click()
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Editing the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'phaseListSelection')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'editDevice_form')]/descendant::button")
		time.sleep(3)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-danger')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text
		print msg

		if 'Device exist for this Phase.' in msg:
			printFP('TEST PASS - Success Message: ' + msg)
			closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
			JustClick(closebutton)
			time.sleep(2)
			return Global.PASS, 'TEST PASS - ' + msg
		else:
			testComment = 'TEST FAIL - Updated duplicate phase'
			printFP(testComment)
			closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
			JustClick(closebutton)
			time.sleep(2)
			return Global.FAIL , testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceStatusToolTipShowsTheCorrectDeviceStatus(input_file_path, wait_for_online=True):
	if input_file_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment
	printFP('INFO - Going to Sys Admin page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	with open(input_file_path, 'rb') as f:
		rows = list(csv.reader(f))
		region_nameof_online_device = rows[1][0]
		substation_nameof_online_device = rows[1][1]
		feeder_nameof_online_device = rows[1][2]
		site_nameof_online_device = rows[1][3]
		device_nameof_online_device = rows[1][5]
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - MTF upload message: %s" % returnMessage)
	else:
		testComment = "MTF upload message: %s" % returnMessage
		printFP(testComment)
		return Global.FAIL, 'TEST FAIL - ' + testComment

	#Checking for Offline device status
	printFP('INFO - Checking for Offline status')
	GoToDevman()
	time.sleep(2)
	printFP('INFO - Clicking on the Root node')
	GetRootNode()
	time.sleep(1)
	tabledevicelist = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
	devtbody = GetElement(tabledevicelist, By.TAG_NAME, "tbody")
	deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
	for row in deviceslist:
		devicedetails = GetElement(row, By.XPATH, 'td[4]')
		actions = ActionChains(Global.driver).move_to_element(devicedetails).perform()
		time.sleep(1)
		status = GetElement(devicedetails, By.TAG_NAME, 'span')
		status_value = status.get_attribute('tooltip')
	print status_value
	if 'Offline' in status_value:
		testComment = 'INFO - Device Status is Offline'
		printFP(testComment)
	else:
		testComment = 'INFO - Device Status is NOT Offline'
		printFP(testComment)

	#Checking for Online device status
	printFP('INFO - Checking for Online status')
	ping_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span[2]").click()
	time.sleep(2)
	initiate_ping = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Initiate Ping')]").click()
	time.sleep(2)
	close_button = GetElement(Global.driver, By.XPATH, "//button[contains(@class,'close')]").click()

	if wait_for_online:
		GoToDevMan()
		time.sleep(5)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(region_nameof_online_device, substation_nameof_online_device, feeder_nameof_online_device, site_nameof_online_device)
		if IsOnline(device_nameof_online_device):
			testComment = 'INFO - %s did come online and successfully uploaded'% device_nameof_online_device
			printFP(testComment)
			GoToDevman()
			time.sleep(2)
			printFP('INFO - Clicking on the Root node')
			GetRootNode()
			time.sleep(1)
			tabledevicelist = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
			devtbody = GetElement(tabledevicelist, By.TAG_NAME, "tbody")
			deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
			for row in deviceslist:
				devicedetails = GetElement(row, By.XPATH, 'td[4]')
				actions = ActionChains(Global.driver).move_to_element(devicedetails).perform()
				time.sleep(1)
				status = GetElement(devicedetails, By.TAG_NAME, 'span')
				status_value = status.get_attribute('tooltip')
			print status_value
			if 'Online' in status_value:
				testComment = 'TEST PASS - Device Status is Online'
				printFP(testComment)
				return Global.PASS, testComment
			else:
				testComment = 'TEST FAIL - Device Status is NOT Online'
				printFP(testComment)
				return Global.FAIL, testComment
		else:
			testComment = 'TEST FAIL - %s did not come online' % device_nameof_online_device
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'TEST FAIL - %s did not come online' % device_nameof_online_device
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceManagementManageDevicesEditAnyDeviceWithMissingMandatoryDetailsOnInDeviceManagementManageDeviceScreenOnOrganizationRegionSubstationFeederSiteLevel(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		rootElement.click()
		time.sleep(1)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(1)
		printFP('INFO - Clicking on the Region')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		edit_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span").click()
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Editing the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'phaseListSelection')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'editDevice_form')]/descendant::button")
		time.sleep(3)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-danger')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text
		print msg

		if 'Please fill all mandatory fields.' in msg:
			printFP('TEST PASS - Success Message: ' + msg)
			closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
			JustClick(closebutton)
			time.sleep(2)
			return Global.PASS, 'TEST PASS - ' + msg
		else:
			testComment = 'TEST FAIL - Without Mandatory details - Updated successfully'
			printFP(testComment)
			closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
			JustClick(closebutton)
			time.sleep(2)
			return Global.FAIL , testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceManagementManageDevicesMoveDeviceOnDifferentSiteWherePhaseABCDeviceAreThereOnInDeviceManagementManageDeviceScreenOnOrganizationRegionSubstationFeederSiteLevel(input_file_path=None, device_detail_path=None,input_file_path1=None,input_file_path2=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	UploadMTF(input_file_path1)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	UploadMTF(input_file_path2)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		rootElement.click()
		time.sleep(1)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(1)
		printFP('INFO - Clicking on the Region')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		rootElement.click()
		time.sleep(2)
		edit_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span").click()
		time.sleep(3)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Editing the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'phaseListSelection')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'editDevice_form')]/descendant::button")
		time.sleep(3)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-danger')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text
		print msg

		if 'Device exist for this Phase.' in msg:
			printFP('TEST PASS - Success Message: ' + msg)
			closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
			JustClick(closebutton)
			time.sleep(2)
			return Global.PASS, 'TEST PASS - ' + msg
		else:
			testComment = 'TEST FAIL - Updated with the duplicate phase'
			printFP(testComment)
			closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
			JustClick(closebutton)
			time.sleep(2)
			return Global.FAIL , testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def FlashLEDDeviceIsOffline(input_file_path=None):
	if input_file_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		rootElement.click()
		time.sleep(1)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(1)
		printFP('INFO - Clicking on the Region')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		rootElement.click()
		time.sleep(2)

		led_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span[3]").click()
		time.sleep(2)

		header = GetElement(Global.driver, By.XPATH, "//span[contains(text(),'LED Flash')]").click()
		time.sleep(2)

		device_info = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'modal-body')]")
		device_info_rows = GetElements(device_info, By.XPATH, "//div[contains(@ng-repeat, 'key in deviceInfoKeyOrder')]")
		deviceinfodict = {}
		for device_info_row in device_info_rows:
			deviceinfokey = GetElement(device_info_row, By.XPATH, "span[1]").text
			deviceinfovalue = GetElement(device_info_row, By.XPATH, "span[3]").text
			deviceinfodict[deviceinfokey] = deviceinfovalue
		print deviceinfodict

		column = pd.read_csv(input_file_path)
		devicnamefromcsv = list(column['Serial Number'])
		device_state = "Production"
		device_status = "OFFLINE"
		last_communication_type = "Unavailable"

		if devicnamefromcsv[0] in deviceinfodict['Serial Number'] and device_state in deviceinfodict['Device State'] and device_status in deviceinfodict['Device Status'] and last_communication_type in deviceinfodict['Last Communication Time']:
			testComment = 'INFO - Device info matched'
			printFP(testComment)
		else:
			testComment = 'INFO - Device info not matched'
			printFP(testComment)

		ClickButton(Global.driver, By.XPATH, xpaths['led_flash_initiate_button'])
		#initiate_flash = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'modal-body')]").click()
		time.sleep(2)
		title = GetElement(Global.driver, By.XPATH, "//h4[contains(@class,'modal-title')]").click()
		time.sleep(2)
		error_msg = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'modal-body')]/p").text
		print error_msg

		closebutton = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Close')]").click()
		time.sleep(2)
		cancel_button = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Cancel')]").click()

		if 'The device is not online to initiate the Flash request.' in error_msg:
			testComment = 'TEST PASS - Cannot Flash the Offline device and all the device info matched..'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST FAIL - Different message has displayed.Pls check...'
			printFP(testComment)
			return Global.FAIL, testComment

	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceManagementManageDevicesEditDescriptionFieldForAnyDeviceWhichAreOnAnyRegionSubstationFeederAndSite(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		rootElement.click()
		time.sleep(2)
		printFP('INFO - Clicking on the Organization node')
		organization_node = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'ROOTNODE-name')]")
		JustClick(organization_node)
		time.sleep(2)
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		edit_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span").click()
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Editing the device details')
		printFP('INFO - Editing the description')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'phaseListSelection')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		description = GetElement(Global.driver, By.XPATH, "//textarea[contains(@ng-model,'deviceDetail.description')]")
		time.sleep(1.5)
		description.send_keys(deviceInfo["Description"])

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'editDevice_form')]/descendant::button")
		time.sleep(3)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)

		if 'Device details updated successfully' in  msg:
			printFP('Success message: '+ msg)
			testComment = 'TEST PASS - Device details updated successfully upon editing the description'
			printFP(testComment)
			return Global.PASS, 'TEST PASS - ' + msg
		else:
			testComment('TEST FAIL - Device details was not able to update successfully when description is given')
			printFP(testComment)
			return Global.FAIL , testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceManagementManageDevicesEditDeviceStateOnSameRegionSubstationFeederAndSite(input_file_path=None, device_detail_path=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		rootElement.click()
		time.sleep(2)
		printFP('INFO - Clicking on the Organization node')
		organization_node = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'ROOTNODE-name')]")
		JustClick(organization_node)
		time.sleep(2)
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		edit_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span").click()
		time.sleep(2)

		params = deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Editing the device details')
		printFP('INFO - Changing the device state')
		state = params['Device State']

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'phaseListSelection')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		device_state = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'deviceStateSelection')]/descendant::button")
		device_state.click()
		parentelement = GetElement(device_state, By.XPATH, '..')
		new_devicestate = SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Device State'])
		time.sleep(1.5)

		description = GetElement(Global.driver, By.XPATH, "//textarea[contains(@ng-model,'deviceDetail.description')]")
		time.sleep(1.5)
		description.send_keys(deviceInfo["Description"])

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'editDevice_form')]/descendant::button")
		time.sleep(3)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)
		time.sleep(3)

		#Getting the Device State value from the table - UI
		printFP('INFO - Getting the Device state value from the UI')
		table = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
		devtbody = GetElement(table, By.TAG_NAME, "tbody")
		deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
		device_state_from_table = []
		for row in deviceslist:
			devicedetails = GetElement(row, By.XPATH, "//td[5]")
			device_state = devicedetails.text
			device_state_from_table.append(device_state)
		print device_state_from_table

		if state in device_state_from_table:
			printFP('INFO - Changed device state reflected on the Device list table')
		else:
			testComment = 'TEST FAIL - Changed device state NOT reflected on the Device list table'
			printFP(testComment)
			return Global.FAIL, testComment


		if 'Device details updated successfully' in  msg:
			printFP('Success message: '+ msg)
			testComment = 'TEST PASS - Device details updated successfully upon changing the device state'
			printFP(testComment)
			return Global.PASS, 'TEST PASS - ' + msg
		else:
			testComment('TEST FAIL - Device details was not able to update successfully when device state is changed')
			printFP(testComment)
			return Global.FAIL , testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceManagementManageDevicesMovingDeviceOnDifferentRegion(input_file_path=None, device_detail_path=None,input_file_path1=None):
	if input_file_path == None or device_detail_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	UploadMTF(input_file_path1)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - Going to Device Management screen")
		GoToDevman()
		time.sleep(1)
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		rootElement.click()
		time.sleep(1)
		GetElement(Global.driver, By.XPATH, "(//span[contains(@class,'node-icon-wrapper')]/a)[2]").click()
		time.sleep(1)
		printFP('INFO - Clicking on the Region')
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)
		edit_button = GetElement(Global.driver, By.XPATH, "//td[contains(@class,'action-column')]/div/span").click()
		time.sleep(2)

		deviceInfo = ParseJsonInputFile(device_detail_path)
		printFP('INFO - Editing the device details')

		region = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'regionSelection')]")
		region.click()
		parentelement = GetElement(region, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Region'])
		time.sleep(1.5)

		subStation = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'substationSelection')]")
		subStation.click()
		parentelement = GetElement(subStation, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Substation'])
		time.sleep(1.5)

		feeder = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'feederSelection')]")
		feeder.click()
		parentelement = GetElement(feeder, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Feeder'])
		time.sleep(1.5)

		site = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'siteSelection')]")
		site.click()
		parentelement = GetElement(site, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Site'])
		time.sleep(1.5)

		phase = GetElement(Global.driver, By.XPATH, "//div[contains(@options,'phaseListSelection')]/descendant::button")
		phase.click()
		parentelement = GetElement(phase, By.XPATH, '..')
		SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
		time.sleep(1.5)

		ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'editDevice_form')]/descendant::button")
		time.sleep(3)

		msgBox = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]")
		msg = GetElement(msgBox, By.XPATH, 'div/span').text
		print msg

		closebutton = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'glyphicon-remove-circle close-icon')]")
		JustClick(closebutton)
		time.sleep(2)

		if 'Device details updated successfully' in msg:
			printFP('TEST PASS - Success Message: ' + msg)
			return Global.PASS, 'TEST PASS - ' + msg
		else:
			testComment = 'TEST FAIL - Failed to update device details'
			printFP(testComment)
			return Global.FAIL , testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment











	






		







