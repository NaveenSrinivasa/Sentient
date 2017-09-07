import json
import os
from time import strftime, strptime
import datetime
from selenium.webdriver.common.keys import Keys
from Utilities_Ample import *
from Utilities_Framework import *
from Ample_SysAdmin import *
from Ample_SysAdmin_MTF_0 import *

def ImportMTFNoGPSCoordinates(mtf_full_path=None, wait_for_online=True):
	"""Navigates to the System admin page and uploads MTF to Ample.
	Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
	If you do not specify an mtf_path, it will use the Global.MTF"""

	# Generate a temporary mtf with only 1 device
	if mtf_full_path == None:
		mtf_full_path = Global.mtfPath
	with open(mtf_full_path, 'r') as inmtf:
		with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
			time.sleep(1)
			header = inmtf.readline()
			outmtf.write(header)
			for line in inmtf:
			#line = inmtf.readline()
				outmtf.write(line)
				devInfo = line.strip('\n').split(',')
				#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
				try:
					device = CreateDeviceDictionary(devInfo)
					time.sleep(3)
				except:
					pass
	GoToSysAdmin()
	time.sleep(2)
	UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - MTF upload message: %s" % returnMessage)
		overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
		if not overridegpsstatus:
			testComment = 'Test Pass - Override GPS switch is OFF when uploaded mtf without GPS coordinates'
			printFP(testComment)
			result = Global.PASS
			if wait_for_online:
				GoToDevMan()
				time.sleep(3)
				Global.driver.refresh()
				time.sleep(10)
				GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
				if IsOnline(device['serial']):
					testComment = 'TEST PASS - %s did come online and successfully uploaded'% device['serial']
					printFP(testComment)
					result = Global.PASS
					overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
					if not overridegpsstatus:
						testComment = 'Test Pass - Override GPS switch is still OFF after device come online when uploaded mtf without GPS coordinates'
						printFP(testComment)
						return Global.PASS, testComment
					else:
						testComment = 'Test Fail - Override GPS is switched on after device come online when uploaded mtf without GPS coordinates'
						printFP(testComment)
						return Global.FAIL, testComment
				else:
					testComment = 'TEST FAIL - %s did not come online' % device['serial']
					printFP(testComment)
					result = Global.FAIL
			else:
				return result, testComment
		else:
			testComment = 'Test Fail - Override GPS switch is ON when uploaded mtf without GPS coordinates'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		try:
			GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
			time.sleep(1)
			popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			message = GetElement(popup,By.TAG_NAME,'p').text
			GetElement(popup, By.TAG_NAME, 'a').click()
			testComment = message.replace('\n', '')
		except:
			testComment = "MTF upload message: %s" % returnMessage
		printFP('INFO - ' + testComment)
		return Global.FAIL, 'TEST FAIL - ' + testComment


def ImportMTFContainsGPSCoordinates(mtf_full_path=None, wait_for_online=True):
	"""Navigates to the System admin page and uploads MTF to Ample.
	Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
	If you do not specify an mtf_path, it will use the Global.MTF"""

	# Generate a temporary mtf with only 1 device
	if mtf_full_path == None:
		mtf_full_path = Global.mtfPath
	with open(mtf_full_path, 'r') as inmtf:
		with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
			time.sleep(1)
			header = inmtf.readline()
			outmtf.write(header)
			for line in inmtf:
			#line = inmtf.readline()
				outmtf.write(line)
				devInfo = line.strip('\n').split(',')
				#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
				try:
					device = CreateDeviceDictionary(devInfo)
					time.sleep(3)
				except:
					pass
	GoToSysAdmin()
	time.sleep(2)
	UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - MTF upload message: %s" % returnMessage)
		overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
		if overridegpsstatus:
			testComment = 'Test Pass - Override GPS switch is ON when uploaded mtf with GPS coordinates'
			printFP(testComment)
			sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(device['region'], device['substation'], device['feeder'], device['site'])
			if str(sitelatitude) == str(device['lat']) and str(sitelongitude) == str(device['lon']):
				testComment = 'Test Pass - site longitude and latitude values are matched with MTF latitude and longitude'
				printFP(testComment)
				result = Global.PASS
				if wait_for_online:
					GoToDevMan()
					time.sleep(3)
					Global.driver.refresh()
					time.sleep(10)
					GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
					if IsOnline(device['serial']):
						testComment = 'TEST PASS - %s did come online and successfully uploaded'% device['serial']
						printFP(testComment)
						result = Global.PASS
						overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
						if overridegpsstatus:
							testComment = 'Test Pass - Override GPS switch is still ON after device come online when uploaded mtf with GPS coordinates'
							printFP(testComment)
							sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(device['region'], device['substation'], device['feeder'], device['site'])
							if str(sitelatitude) == str(device['lat']) and str(sitelongitude) == str(device['lon']):
								testComment = 'Test Pass - site longitude and latitude values are matched with MTF latitude and longitude after device come online'
								printFP(testComment)
								return Global.PASS, testComment
							else:
								testComment = 'Test Fail - site longitude and latitude values are not matched with MTF latitude and longitude after device come online'
								printFP(testComment)
								return Global.FAIL, testComment
						else:
							testComment = 'Test Fail - Override GPS switch changed to OFF state after device come online when uploaded mtf with GPS coordinates'
							printFP(testComment)
							return Global.FAIL, testComment
					else:
						testComment = 'TEST FAIL - %s did not come online' % device['serial']
						printFP(testComment)
						result = Global.FAIL
				else:
					return result, testComment
			else:
				testComment = 'Test Fail - site longitude and latitude values are not matched with MTF latitude and longitude'
				printFP(testComment)
				return Global.FAIL, testComment
		else:
			testComment = 'Test Fail - Override GPS switch is OFF when uploaded mtf with GPS coordinates'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		try:
			GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
			time.sleep(1)
			popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			message = GetElement(popup,By.TAG_NAME,'p').text
			GetElement(popup, By.TAG_NAME, 'a').click()
			testComment = message.replace('\n', '')
		except:
			testComment = "MTF upload message: %s" % returnMessage
		printFP('INFO - ' + testComment)
		return Global.FAIL, 'TEST FAIL - ' + testComment


def ImportMTFEmptyDeviceStateColumn(mtf_full_path=None, wait_for_online=True):
	"""Navigates to the System admin page and uploads MTF to Ample.
	Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
	If you do not specify an mtf_path, it will use the Global.MTF"""

	# Generate a temporary mtf with only 1 device
	if mtf_full_path == None:
		mtf_full_path = Global.mtfPath
	with open(mtf_full_path, 'r') as inmtf:
		with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
			time.sleep(1)
			header = inmtf.readline()
			outmtf.write(header)
			for line in inmtf:
			#line = inmtf.readline()
				outmtf.write(line)
				devInfo = line.strip('\n').split(',')
				#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
				try:
					device = CreateDeviceDictionary(devInfo)
				except:
					pass
	GoToSysAdmin()
	time.sleep(2)
	UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	printFP("INFO - MTF upload message: %s" % returnMessage)
	if "The file has been uploaded successfully." in returnMessage:
		GoToDevMan()
		time.sleep(5)
		GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
		getdevicestates = FilteredDataFromTable('Device State', 'device-management')
		printFP(getdevicestates)
		if 'Production' in getdevicestates:
			testComment = 'Test Pass - MTF File with empty device column uploaded successfully and device state has default value "Production"'
			printFP(testComment)
			result = Global.PASS
		else:
			testComment = 'Test Fail - MTF File with empty device column uploaded successfully but device state is not having default value "Production"'
			printFP(testComment)
			result = Global.FAIL
	else:
		try:
			GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
			time.sleep(1)
			popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			message = GetElement(popup,By.TAG_NAME,'p').text
			GetElement(popup, By.TAG_NAME, 'a').click()
			message = message.replace('\n', '')
		except:
			message = "MTF upload message: %s" % returnMessage
		testComment = 'Test Fail - MTF File with empty device column upload is failed'
		printFP(message)
		printFP(testComment)
		return Global.FAIL, testComment

	if wait_for_online:
		GoToDevMan()
		time.sleep(3)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
		if IsOnline(device['serial']):
			testComment = 'TEST PASS - %s did come online when MTF File with empty device column uploaded successfully and device state has default value "Production"' % device['serial']
			result = Global.PASS
		else:
			testComment = 'TEST FAIL - %s did not come online when MTF File with empty device column uploaded successfully and device state has default value "Production"' % device['serial']
			result = Global.FAIL
	else:
		result = Global.PASS
		testComment = 'TEST PASS - Successfully uploaded MTF file to Ample.'

	return result, testComment

def ImportMTFValidDeviceStateinDeviceStateColumn(mtf_full_path=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""
    deviceandstatemapping = {}
    # Generate a temporary mtf with only 1 device
    if mtf_full_path == None:
        mtf_full_path = Global.mtfPath
    with open(mtf_full_path, 'r') as inmtf:
        with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            time.sleep(1)
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
            #line = inmtf.readline()
                outmtf.write(line)
                devInfo = line.strip('\n').split(',')
                #If this doesn't work, then that means that the upload file is bad. Will error out later through upload
                try:
                    device = CreateDeviceDictionary(devInfo)
                    deviceandstatemapping[device['serial']] = device['devicestate']
                except:
                    pass
    printFP(deviceandstatemapping)
    GoToSysAdmin()
    time.sleep(2)
    UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(1)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    printFP("INFO - MTF upload message: %s" % returnMessage)
    if "The file has been uploaded successfully." in returnMessage:
        GoToDevMan()
        time.sleep(5)
        GetRegionFromTop(device['region'])
        getdevicestates = FilteredDataFromTableMapping('Serial Number', 'Device State', 'device-management')
        printFP(getdevicestates)
        if all(str(deviceandstatemapping[x]) == str(getdevicestates[x]) for x in deviceandstatemapping):
            testComment = 'Test Pass - MTF File with all type of device states uploaded successfully and device states are matched with GUI'
            printFP(testComment)
            result = Global.PASS
        else:
            testComment = 'Test Fail - MTF File with all type of device states uploaded successfully but device states are not matched with GUI'
            printFP(testComment)
            result = Global.FAIL
    else:
        try:
            GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
            time.sleep(1)
            popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
            message = GetElement(popup,By.TAG_NAME,'p').text
            GetElement(popup, By.TAG_NAME, 'a').click()
            message = message.replace('\n', '')
        except:
            message = "MTF upload message: %s" % returnMessage
        testComment = 'Test Fail - MTF File with all type of device states upload is failed'
        printFP(message)
        printFP(testComment)
        return Global.FAIL, testComment

    if wait_for_online:
        GoToDevMan()
        time.sleep(3)
        Global.driver.refresh()
        time.sleep(10)
        GetRegionFromTop(device['region'], device['substation'], device['feeder'], device['site'])
        if IsOnline(device['serial']):
            testComment = 'TEST PASS - %s did come online when MTF File with all type of device states uploaded successfully and device states are matched with GUI' % device['serial']
            result = Global.PASS
        else:
            testComment = 'TEST FAIL - %s did not come online when MTF File with all type of device states uploaded successfully and device states are matched with GUI' % device['serial']
            result = Global.FAIL
    else:
        result = Global.PASS
        testComment = 'TEST PASS - Successfully uploaded MTF file to Ample.'

    return result, testComment

def ImportMTFMM3SoftwareVersionNotImported(mtf_full_path=None):
	"""Navigates to the System admin page and uploads MTF to Ample.
	Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
	If you do not specify an mtf_path, it will use the Global.MTF"""

	# Generate a temporary mtf with only 1 device
	if mtf_full_path == None:
		mtf_full_path = Global.mtfPath
	with open(mtf_full_path, 'r') as inmtf:
		with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
			time.sleep(1)
			header = inmtf.readline()
			outmtf.write(header)
			for line in inmtf:
			#line = inmtf.readline()
				outmtf.write(line)
				devInfo = line.strip('\n').split(',')
				#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
				try:
					device = CreateDeviceDictionary(devInfo)
				except:
					pass
	GoToSysAdmin()
	time.sleep(2)
	UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		printFP("INFO - MTF upload message: %s" % returnMessage)
	else:
		try:
			GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
			time.sleep(1)
			popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			message = GetElement(popup,By.TAG_NAME,'p').text
			GetElement(popup, By.TAG_NAME, 'a').click()
			message = message.replace('\n', '')
		except:
			message = "MTF upload message: %s" % returnMessage
		if 'Product Name, Software Release, and Platform : The Product Name, Software Release, and Platform combination is invalid or wrongly entered' in message:
			testComment = 'Test Pass - MTF file with not imported software version is not uploaded'
			printFP(testComment)
			return Global.FAIL, testComment
		else:
			testComment = 'Test Fail - MTF file with not imported software version is uploaded successfully'
			printFP(testComment)
			printFP(message)
			return Global.PASS, testComment

def ImportMTFSameSiteDiffGPSUploadDevicesSingleUpload(mtf_full_path=None):
	"""Navigates to the System admin page and uploads MTF to Ample.
	Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
	If you do not specify an mtf_path, it will use the Global.MTF"""

	# Generate a temporary mtf with only 1 device
	if mtf_full_path == None:
		mtf_full_path = Global.mtfPath
	with open(mtf_full_path, 'r') as inmtf:
		with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
			time.sleep(1)
			header = inmtf.readline()
			outmtf.write(header)
			for line in inmtf:
			#line = inmtf.readline()
				outmtf.write(line)
				devInfo = line.strip('\n').split(',')
				#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
				try:
					device = CreateDeviceDictionary(devInfo)
				except:
					pass
	GoToSysAdmin()
	time.sleep(2)
	UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	printFP("INFO - MTF upload message: %s" % returnMessage)
	if "The file has been uploaded successfully." in returnMessage:
		testComment = 'Test Fail - MTF file is uploaded successfully when uploaded 2 devices with different GPS coordinates for the same site'
		printFP(testComment)
		return Global.PASS, testComment
	else:
		try:
			GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
			time.sleep(1)
			popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			message = GetElement(popup,By.TAG_NAME,'p').text
			printFP(message)
			GetElement(popup, By.TAG_NAME, 'a').click()
			time.sleep(1)
		except:
			testComment = "MTF upload message: %s" % returnMessage
			message = returnMessage

		if 'Invalid Latitude and Longitude Combination : The Latitude and Longitude Combination has to be same for all the Phases in a Feeder Site' in message:
			testComment = 'Test Pass - MTF file is not uploaded and error message is matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site'
			printFP(testComment)
			if 'Invalid Latitude and Longitude Entry for a Site : Latitude and Longitude combination should either be empty for all the phases in a site or should have valid values' in message:
				testComment = 'Test Pass - MTF file is not uploaded and error message is matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site'
				printFP(testComment)
				return Global.FAIL, testComment
			else:
				testComment = 'Test Fail - MTF file is not uploaded but error message is not matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site'
				printFP(testComment)
				printFP(message)
				return Global.PASS, testComment
		else:
			testComment = 'Test Fail - MTF file is not uploaded but error message is not matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site'
			printFP(testComment)
			printFP(message)
			return Global.PASS, testComment

def ImportMTFSameSiteDiffGPSUploadDevicesOneAfterOther(mtf_full_path_1=None, mtf_full_path_2=None):
	"""Navigates to the System admin page and uploads MTF to Ample.
	Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
	If you do not specify an mtf_path, it will use the Global.MTF"""

	# Generate a temporary mtf with only 1 device
	if mtf_full_path_1 == None:
		mtf_full_path = Global.mtfPath
	else:
		mtf_full_path = mtf_full_path_1
	with open(mtf_full_path, 'r') as inmtf:
		with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
			time.sleep(1)
			header = inmtf.readline()
			outmtf.write(header)
			for line in inmtf:
			#line = inmtf.readline()
				outmtf.write(line)
				devInfo = line.strip('\n').split(',')
				#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
				try:
					device = CreateDeviceDictionary(devInfo)
				except:
					pass
	GoToSysAdmin()
	time.sleep(2)
	UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		testComment = 'INFO - MTF file 1 with GPS is uploaded successfully when uploaded 2 devices with different GPS coordinates for the same site one after the other'
		printFP(testComment)
		if mtf_full_path_2 == None:
			mtf_full_path = Global.mtfPath
		else:
			mtf_full_path = mtf_full_path_2
		with open(mtf_full_path, 'r') as inmtf:
			with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
				time.sleep(1)
				header = inmtf.readline()
				outmtf.write(header)
				for line in inmtf:
				#line = inmtf.readline()
					outmtf.write(line)
					devInfo = line.strip('\n').split(',')
					#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
					try:
						device = CreateDeviceDictionary(devInfo)
					except:
						pass
		GoToSysAdmin()
		time.sleep(2)
		UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
		time.sleep(1)
		ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
		time.sleep(1)
		returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
		if "The file has been uploaded successfully." in returnMessage:
			printFP("INFO - MTF upload message: %s" % returnMessage)
			testComment = 'Test Fail - MTF file 2 with GPS is uploaded successfully when uploaded 2 devices with different GPS coordinates for the same site one after the other'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			try:
				GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
				time.sleep(1)
				popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
				message = GetElement(popup,By.TAG_NAME,'p').text
				GetElement(popup, By.TAG_NAME, 'a').click()
				message = message.replace('\n', '')
			except:
				message = "MTF upload message: %s" % returnMessage
			if 'Invalid Latitude and Longitude Combination : The Latitude and Longitude Combination has to be same for all the Phases in a Feeder Site' in message:
				testComment = 'Test Pass - MTF file 2 with GPS is not uploaded and error message is matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site one after the other'
				printFP(testComment)
				if 'Invalid Latitude and Longitude Entry for a Site : Latitude and Longitude combination should either be empty for all the phases in a site or should have valid values' in message:
					testComment = 'Test Pass - MTF file 2 with GPS is not uploaded and error message is matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site one after the other'
					printFP(testComment)
					return Global.FAIL, testComment
				else:
					testComment = 'Test Fail - MTF file 2 with GPS is not uploaded but error message is not matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site one after the other'
					printFP(testComment)
					printFP(message)
					return Global.PASS, testComment
			else:
				testComment = 'Test Fail - MTF file 2 with GPS is not uploaded but error message is not matched with the expected result when uploaded 2 devices with different GPS coordinates for the same site one after the other'
				printFP(testComment)
				printFP(message)
				return Global.PASS, testComment
	else:
		try:
			GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
			time.sleep(1)
			popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			message = GetElement(popup,By.TAG_NAME,'p').text
			GetElement(popup, By.TAG_NAME, 'a').click()
			message = message.replace('\n', '')
		except:
			message = "MTF upload message: %s" % returnMessage

		testComment = 'Test Fail - MTF file 1 with GPS is not uploaded successfully when uploaded 2 devices with different GPS coordinates for the same site one after the other'
		printFP(message)
		printFP(testComment)
		return Global.PASS, testComment



def ImportMTFSameSiteFirstWithGPSSecondWithoutGPS(mtf_full_path_1=None, mtf_full_path_2=None, wait_for_online=True):
	"""Navigates to the System admin page and uploads MTF to Ample.
	Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
	If you do not specify an mtf_path, it will use the Global.MTF"""

	# Generate a temporary mtf with only 1 device
	if mtf_full_path_1 == None:
		mtf_full_path = Global.mtfPath
	else:
		mtf_full_path = mtf_full_path_1
	with open(mtf_full_path, 'r') as inmtf:
		with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
			time.sleep(1)
			header = inmtf.readline()
			outmtf.write(header)
			for line in inmtf:
			#line = inmtf.readline()
				outmtf.write(line)
				devInfo = line.strip('\n').split(',')
				#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
				try:
					device = CreateDeviceDictionary(devInfo)
				except:
					pass
	GoToSysAdmin()
	time.sleep(2)
	UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		testComment = 'INFO - MTF file 1 without GPS is uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
		printFP(testComment)
		if mtf_full_path_2 == None:
			mtf_full_path = Global.mtfPath
		else:
			mtf_full_path = mtf_full_path_2
		with open(mtf_full_path, 'r') as inmtf:
			with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
				time.sleep(1)
				header = inmtf.readline()
				outmtf.write(header)
				for line in inmtf:
				#line = inmtf.readline()
					outmtf.write(line)
					devInfo = line.strip('\n').split(',')
					#If this doesn't work, then that means that the upload file is bad. Will error out later through upload
					try:
						device = CreateDeviceDictionary(devInfo)
					except:
						pass
		GoToSysAdmin()
		time.sleep(2)
		UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
		time.sleep(1)
		ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
		time.sleep(1)
		returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
		printFP("INFO - MTF upload message: %s" % returnMessage)
		if "The file has been uploaded successfully." in returnMessage:
			testComment = 'INFO - MTF file 2 with GPS is uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
			printFP(testComment)
			overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
			if overridegpsstatus:
				testComment = 'Test Pass - Override GPS switch is ON when uploaded mtf with GPS coordinates'
				printFP(testComment)
				sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(device['region'], device['substation'], device['feeder'], device['site'])
				if str(sitelatitude) == str(device['lat']) and str(sitelongitude) == str(device['lon']):
					testComment = 'Test Pass - site longitude and latitude values are matched with MTF latitude and longitude'
					printFP(testComment)
					result = Global.PASS
			else:
				testComment = 'Test Fail - Override GPS switch is OFF when uploaded mtf file 2 with GPS coordinates'
				printFP(testComment)
				return Global.FAIL, testComment
		else:
			try:
				GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
				time.sleep(1)
				popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
				message = GetElement(popup,By.TAG_NAME,'p').text
				GetElement(popup, By.TAG_NAME, 'a').click()
				message = message.replace('\n', '')
			except:
				message = "MTF upload message: %s" % returnMessage

			testComment = 'Test Fail - MTF file 2 with GPS is not uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
			printFP(message)
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		try:
			GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
			time.sleep(1)
			popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			message = GetElement(popup,By.TAG_NAME,'p').text
			GetElement(popup, By.TAG_NAME, 'a').click()
			message = message.replace('\n', '')
		except:
			message = "MTF upload message: %s" % returnMessage

		testComment = 'Test Fail - MTF file 1 without GPS is not uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
		printFP(message)
		printFP(testComment)
		return Global.FAIL, testComment

	if wait_for_online:
		GoToDevMan()
		time.sleep(3)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
		if IsOnline(device['serial']):
			testComment = 'TEST PASS - %s did come online when uploaded 2 devices with and without GPS coordinates for the same site one after the other'% device['serial']
			result = Global.PASS
		else:
			testComment = 'TEST FAIL - %s did not come online when uploaded 2 devices with and without GPS coordinates for the same site one after the other' % device['serial']
			result = Global.FAIL

	return result, testComment
