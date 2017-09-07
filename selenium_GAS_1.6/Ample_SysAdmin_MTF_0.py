import Global
import json
import time
import csv
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from Utilities_Ample import *
from Utilities_Framework import *
from Ample_SysAdmin import *
from Ample_DevMan import *
from Ample_DevMan_ManageDevices import *
from bs4 import BeautifulSoup as soup
from stripogram import html2text
import subprocess as sp
import filecmp
import unicodedata

'''This Method will check number of error lines in MTF file is greater then 50 lines,
number of error lines shouldn't be restricted to any number!'''

def NumberOfErrorsSupportedForAFailedMTFUpload(input_file_path):
	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File with more than 50 error devices details")
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		line_count = 0
		for line in GetElements(lines, By.TAG_NAME,'br'):
			line_count += 1
		if line_count <= 50:
			testComment = 'Test Fail - Please upload MTF which has more then 50 error message lines'
			printFP(testComment)
			return Global.FAIL, testComment
		elif line_count > 50:
			testComment='Test Pass - MTF file upload has more then 50 error message lines'
			printFP(testComment)

		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(2)
		#Global.driver.execute_script("window.scrollTo(0,0/6)")
		last_height = Global.driver.execute_script("return document.body.scrollHeight")
		match = False

		while True:
		    # Scroll down to bottom
		    Global.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		    # Wait page to load
		    time.sleep(0.5)
		    # Calculate new scroll height and compare with last scroll height
		    new_height = Global.driver.execute_script("return document.body.scrollHeight")
		    if new_height == last_height:
		    	match = True
		        break
		    last_height = new_height
		# Scrolling back to top of the page.
	   	Global.driver.execute_script("window.scrollTo(0,0)")

	   	#Closing the pop up window
		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if not match:
			testComment = 'Test Fail - Unable to scroll when MTF file upload has more than 50 error messages'
			printFP(testComment)
			return Global.FAIL, testComment
		else:
			testComment='Test Pass - Able to scroll when MTF file upload has more then 50 error message lines'
			printFP(testComment)
			return Global.PASS, testComment
	else:
		testComment = 'Test Fail - MTF File Uploaded Successfully'
		printFP(testComment)
		return Global.FAIL, testComment

'''This method is to Indicate Column heading instead of column number,
when there are errors in MTF file'''

def MTFErrorFormatToIndicateColumnHeadingInsteadOfColumnNumber(input_file_path):
	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment
	time.sleep(1)
	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	Global.driver.refresh()
	time.sleep(10)
	printFP("INFO - Uploading the MTF File with Bad value")
	UploadMTF(input_file_path)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2.5)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:

		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2.5)
		errorpopup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		errormessage = GetElement(errorpopup, By.TAG_NAME,'p')
		errormessage.click()
		errormsg = errormessage.text.strip()
		errormsg = errormsg.replace('"','')
		errormsg = ''.join(errormsg.split('\n'))
		errormsg = errormsg.split('Line')

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		#Reading the column header of the MTF file to check whether column which has error has displayed or not
		with open(input_file_path, 'rb') as f:
			reader=csv.reader(f)
			header = reader.next()

			#Checking whether below mentioned coulmn name present in the error message body
			tmpheaders = [header[6], header[7], header[8],header[9],header[10],header[16], header[20]]
			n=0
			for line in errormsg:
				if n > 0:
					if any(x in line for x in tmpheaders):
						testComment = 'INFO - Error message in line: %s' % line
						printFP(testComment)
					else:
						testComment = 'Test Fail - Expected Column names are not present in line: %s' % line
						printFP(testComment)
						return Global.FAIL, testComment
				n = n + 1

		testComment = 'Test Pass - MTF error messages displayed with the column heading instead of column number'
		printFP(testComment)
		return Global.PASS, testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.FAIL, testComment


#This method is to export the error messages of MTF file to text file.

def ExportErrorLogForFailedMTF(input_file_path=None, downloadfolder=None, filetype=None):
	if input_file_path == None or downloadfolder == None or filetype == None:
		testComment = "Missing a mandatory parameter."
		printFP(testComment)
		return Global.FAIL, testComment

	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)

	printFP("INFO - Uploading the MTF File with Bad values to export the error messages")
	UploadMTF(input_file_path)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:

		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2.5)
		header = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-header')
		header.click()
		errormsgheader = header.text.strip()
		errormsgheader = errormsgheader.replace('"','').replace(' ','')
		errormsgheader = ''.join(errormsgheader.split())
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		errormsg = lines.text.strip()
		errormsg = errormsg.strip('\n').replace('"','').replace(' ','')
		errormsg = ''.join(errormsg.split('\n'))
		errormsg = errormsg.strip()
		#print len(errormsg)
		try:
			downloadbutton=GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[3]/button").click()
			printFP('INFO - Clicked download button')
			time.sleep(3)
		except:
			testComment = 'Test Fail - Unable to find download button'
			printFP(testComment)
			Global.FAIL , testComment
		# Place where downloaded file exists
		location = downloadfolder + 'error_messages.txt'
		#Opening the downloaded file and reading its content
		with open(location,'r') as f:
			content = f.read()
			errormsgfromfile = content.strip()
			errormsgfromfile = unicode(errormsgfromfile, "utf-8")
			errormsgfromfile = errormsgfromfile.strip('\n').replace('"','').replace(' ','')
			errormsgfromfile = ''.join(errormsgfromfile.split())
			errormsgfromfile = errormsgfromfile.strip().split('Themastertracker')
			#print len(errormsgfromfile[1])

		#After reading content of downloaded file, deleting the opened file
		try:
			os.remove(location)
		except OSError as e:
			printFP(e)
			return Global.FAIL, 'TEST FAIL - ' + e

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		#Validating the content of downloaded file and the content of error message shown on UI

		if len(errormsg) == (len('Themastertracker') + len(errormsgfromfile[1])):
			testComment = 'Test Pass - Successfully deleted file from download folder and content matched in the downloaded file'
			printFP(testComment)
			return Global.PASS, 'TEST PASS ' + testComment
		else:
			testComment = 'Test Fail - Both the contents NOT matched'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.FAIL, testComment

'''This method will check non- ascii character for all the fields in MTF file and
if exists it will throw an error message.'''

def ASCIICharSetValidationForAllFieldsInMTF(input_file_path):
	if input_file_path == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.FAIL, testComment

	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File with Non-Ascii character for columns")
	UploadMTF(input_file_path)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2.5)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		errormsg = errormsg.strip('\n').replace('"','').replace(' ','')
		errormsg = ''.join(errormsg.split('\n'))
		errormsg = errormsg.strip()
		#Getting the Non Ascii character from the error message
		nonascii =  re.sub('[ -~]', '', errormsg)

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if len(nonascii) > 0:
			testComment = 'Test Pass- MTF File failed to upload with Non-ASCII characters in the MTF file'
			printFP(testComment)
			return Global.PASS , testComment
		else:
			testComment = 'Test Fail - MTF File upload successful with Non-ASCII characters in the MTF file'
			printFP(testComment)
			return Global.FAIL , testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.FAIL, testComment

'''This method is to check whether MTF is uploaded with Missing column header,
as column header is mandatory, if its not exist it will give error message'''

def UploadMTFWithMissingColumnHeader(input_file_path):
	if input_file_path == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.FAIL, testComment

	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File With missing column header")
	UploadMTF(input_file_path)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'Column format mismatch.' in errormsg:
			testComment = 'Test Pass- MTF File failed to upload missing column header in the MTF'
			printFP(testComment)
			return Global.PASS , testComment
		else:
			testComment = 'Test Fail - MTF File upload successful with missing column header in the MTF file'
			printFP(testComment)
			return Global.FAIL , testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.FAIL, testComment

'''This method will check whether multiple devices are uploaded with same DNP address'''

def TwoDevicesWithSameSensorAddress(input_file_path):
	if input_file_path == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.PASS, testComment

	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File with Two devices having same sensor DNP address")
	UploadMTF(input_file_path)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'Duplicate Sensor (Device) DNP Address' in errormsg:
			testComment = 'Test Pass- MTF File failed to upload with same sensor DNP address for two devices. . .'
			printFP(testComment)
			return Global.FAIL , testComment
		else:
			testComment = 'Test Fail - MTF File upload successful with same sensor DNP address for two devices. . .'
			printFP(testComment)
			return Global.PASS , testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.PASS, testComment

'''This method will check two devices having same DNP address but Unique IP address'''

def DevicesWithSameSensorAddressButUniqueIPAddress(mtf_file_path1, mtf_file_path2, wait_for_online=True):
	if mtf_file_path1 == None and mtf_file_path2 == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.PASS, testComment

	if mtf_file_path1 == None:
		mtf_full_path = Global.mtfPath
	else:
		mtf_full_path = mtf_file_path1
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
	else:
		testComment = "MTF upload message: %s" % returnMessage
		printFP(testComment)
		return Global.PASS, 'TEST FAIL - ' + testComment
	if wait_for_online:
		GoToDevMan()
		time.sleep(3)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
		if IsOnline(device['serial']):
			testComment = 'INFO - %s did come online' % device['serial']
			result = Global.PASS
		else:
			testComment = 'INFO - %s did not come online' % device['serial']
			result = Global.FAIL

	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File with Unique Ip address but Same DNP address as of device 1")
	UploadMTF(mtf_file_path2)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'Duplicate Sensor (Device) DNP Address' in errormsg:
			testComment = 'Test Pass- MTF File failed to upload with same sensor DNP address of device 1 which is uploaded successfully. . .'
			printFP(testComment)
			return Global.FAIL , testComment
		else:
			testComment = 'Test Fail - MTF File upload successful with same sensor DNP address of device 1 which is uploaded successfully. . .'
			printFP(testComment)
			return Global.PASS , testComment
	else:
		testComment = 'Test Fail - MTF File upload successful with same sensor DNP address of device 1 which is uploaded successfully. . .'
		printFP(testComment)
		return Global.PASS, testComment

'''This method will check if user is trying to upload Duplicate devices,
it will return error message'''

def ImportMTFDuplicateDevices(input_file_path1,input_file_path2):
	if input_file_path1 == None and input_file_path2 == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.PASS, testComment

	printFP('INFO - Going to Sys Admin page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('Uploading the MTF File with duplicate device details without capitalization')
	UploadMTF(input_file_path1)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'An Element with the same Region, Sub Station, Feeder, Feeder Site, and Phase combination is already available.' in errormsg:
			testComment = 'INFO- MTF File failed to upload with Duplicate device details. . .'
			printFP(testComment)
		else:
			testComment = 'Test Fail - MTF File upload successful with Duplicate device details. . .'
			printFP(testComment)
			return Global.PASS , testComment


	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File with duplicate device details with capitalization")
	UploadMTF(input_file_path2)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'An Element with the same Region, Sub Station, Feeder, Feeder Site, and Phase combination is already available.' in errormsg:
			testComment = 'Test Pass- MTF File failed to upload with Duplicate device details for both capitalization & non -capitalization letters. . .'
			printFP(testComment)
			return Global.FAIL , testComment
		else:
			testComment = 'Test Fail - MTF File upload successful with Duplicate device details for both capitalization & non -capitalization letters. . .'
			printFP(testComment)
			return Global.PASS , testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.PASS, testComment

def ImportMTFValidFieldNotes(input_file_path=None):
	if input_file_path == None:
		testComment = 'Missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File with Valid Field Note value')
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
		field_notes_from_csv = list(column['Field Notes'])
		print field_notes_from_csv

		#Getting the Field Note value from the table - UI
		printFP('INFO - Getting the Field note value from the UI')
		table = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'deviceList')]")
		devtbody = GetElement(table, By.TAG_NAME, "tbody")
		deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
		field_note_from_table = []
		for row in deviceslist:
			field_note_column = GetElement(row, By.XPATH, "//td[20]").click()
			time.sleep(2)
			fieldnote_popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
			fieldnote_lines = GetElement(fieldnote_popup, By.TAG_NAME,'p')
			fieldnote_lines.click()
			time.sleep(1)
			Fieldnote_value = fieldnote_lines.text.strip()
			field_note_from_table.append(Fieldnote_value)
		print field_note_from_table

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span/span/a")
		closebutton.click()
		time.sleep(1)

		#Validating the field notes value both from UI and from the MTF File

		if all(str(x) in field_note_from_table for x in field_notes_from_csv):
			testComment = 'TEST Pass -Import MTF with long Field Note value is accepted... '
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST Fail - Field Note CANNOT accept long values'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'TEST Fail - Failed to Upload MTF File'
		printFP(testComment)
		return Global.FAIL, testComment

def ImportMTFInValidFieldNotes(input_file_path):
	if input_file_path == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.PASS, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File with Maximum characters for Field notes')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'Notes cannot exceed 255 characters in length.' in errormsg:
			testComment = 'Test Pass- MTF File failed to upload with more than 255 characters for field notes..'
			printFP(testComment)
			return Global.FAIL , testComment
		else:
			testComment = 'Test Fail - MTF File upload successful with more than 255 characters for field notes. . .'
			printFP(testComment)
			return Global.PASS , testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.PASS, testComment

def UploadMTFWithIncorrectNetworkType(mtf_file_path1, mtf_file_path2, wait_for_online1=True, wait_for_online2=True):
	if mtf_file_path1 == None and mtf_file_path2 == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.FAIL, testComment

	# Generate a temporary mtf with only 1 device
	if mtf_file_path1 == None:
		mtf_full_path = Global.mtfPath
	else:
		mtf_full_path = mtf_file_path1
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
		testComment = "MTF upload message: %s" % returnMessage
		printFP(testComment)
		return Global.FAIL, 'TEST FAIL - ' + testComment
	if wait_for_online1:
		GoToDevMan()
		time.sleep(3)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
		if IsOnline(device['serial']):
			testComment = 'INFO - %s did come online and successfully uploaded when uploaded ssn device with cellular network type'% device['serial']
			printFP(testComment)
		else:
			testComment = 'TEST FAIL - %s did not come online when uploaded cellular device with ssn network type' % device['serial']
			printFP(testComment)

	if mtf_file_path2 == None:
		mtf_full_path = Global.mtfPath
	else:
		mtf_full_path = mtf_file_path2
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
					device2 = CreateDeviceDictionary(devInfo)
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
		testComment = "MTF upload message: %s" % returnMessage
		printFP(testComment)
		return Global.FAIL, 'TEST FAIL - ' + testComment
	if wait_for_online2:
		GoToDevMan()
		time.sleep(3)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(device2['region'], device2['substation'], device2['feeder'], device2['site'])
		if IsOnline(device2['serial']):
			testComment = 'TEST PASS - Both devices did come online when uploaded cellular device with ssn and ssn with cellular network type after poll interval'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST FAIL - %s did not come online when uploaded cellular device with ssn network type' % device2['serial']
			printFP(testComment)
			return Global.FAIL, testComment

	else:
		testComment = 'Test Fail - MTF Failed to Upload Successfully'
		printFP(testComment)
		return Global.FAIL, testComment

def UploadMTFWithDifferentFirmwareVersion(mtf_full_path, wait_for_online=True):
	firmware_version_mapping = {}

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
				firmware_version_mapping[device['serial']] = device['swversion']
			except:
				pass
	printFP(firmware_version_mapping)
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
		getfirmwareversion = FilteredDataFromTableMapping('Serial Number', 'FW Version', 'device-management')
		#printFP(getfirmwareversion)
		if all(str(firmware_version_mapping[x]) != str(getfirmwareversion[x]) for x in firmware_version_mapping):
			testComment = 'Test Pass - Actual and uploaded firmware version did not matched'
			printFP(testComment)
			result = Global.PASS
		else:
			testComment = 'Test Fail - Actual and uploaded firmware version matched'
			printFP(testComment)
			result = Global.FAIL
	if wait_for_online:
		GoToDevMan()
		time.sleep(3)
		Global.driver.refresh()
		time.sleep(10)
		GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
		if IsOnline(device['serial']):
			testComment = 'TEST PASS - %s did come online when different firmware version is uploaded than the actual version on the device' % device['serial']
			printFP(testComment)
			result = Global.PASS
		else:
			testComment = 'TEST FAIL - %s did not come online when different firmware version is uploaded than the actual version on the device' % device['serial']
			printFP(testComment)
			result = Global.FAIL
	else:
		result = Global.FAIL
		testComment = 'TEST FAIL - MTF File failed to upload successfully..'
		printFP(testComment)
	return result, testComment


def VerifyNumberOfErrorsOnMTFFile(input_file_path):
	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File with 151 error lines in MTF file")
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(1)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		errormsg = lines.text.strip()
		errormsg = errormsg.replace('"','')
		errormsg = ''.join(errormsg.split('\n'))
		errormsg = errormsg.split('Line')
		line_count = 0
		for line in GetElements(lines, By.TAG_NAME,'br'):
			line_count += 1
		print line_count

		#Scrolling the page to see complete error message details
		lines = GetElement(popup, By.TAG_NAME,'p')
		time.sleep(2)
		Global.driver.execute_script("window.scrollTo(0,0/6)")

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)
		Global.driver.execute_script("window.scrollTo(0,0)")

		if line_count == 151:
			testComment = 'Test Pass - The number of errors listed is equal to the number of errors we created on the bad MTF file'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment='Test Fail - The number of errors listed is NOT equal to the number of errors we created on the bad MTF file'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'Test Fail - MTF File Uploaded Successfully'
		printFP(testComment)
		return Global.FAIL, testComment

def ImportMTFUploadingDuplicateDevices(input_file_path1,input_file_path2):
	if input_file_path1 == None and input_file_path2 == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.PASS, testComment

	printFP('INFO - Going to Sys Admin page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('Uploading the MTF File with valid device details')
	UploadMTF(input_file_path1)
	time.sleep(1)

	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "The file has been uploaded successfully." in returnMessage:
		testComment = 'Test Pass - Device 1 is uploaded successfully...'
		printFP(testComment)
	else:
		testComment = "MTF upload message: %s" % returnMessage
		printFP(testComment)
		return Global.PASS, 'TEST FAIL - ' + testComment

	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File")
	UploadMTF(input_file_path2)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'An Element with the same Region, Sub Station, Feeder, Feeder Site, and Phase combination is already available.' in errormsg:
			testComment = 'Test Pass- MTF File of device 2 failed to upload with different Sensor gateway and network group of device 1 which is uploaded successfully. . .'
			printFP(testComment)
			return Global.FAIL , testComment
		else:
			testComment = 'Test Fail - MTF File of device 2 upload successful with different Sensor gateway and network group of device 1 which is uploaded successfully. . .'
			printFP(testComment)
			return Global.PASS , testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.PASS, testComment

def ImportMTFMismatchedSensorGatewayAndNetworkGroup(input_file_path):
	if input_file_path == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.PASS, testComment

	printFP('INFO - Going to System Admin Page')
	GoToSysAdmin()
	time.sleep(2)
	printFP('INFO - Uploading the MTF File with Different Sensor GW and Network group present on the ample')
	UploadMTF(input_file_path)
	time.sleep(1)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
	returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
	if "Failed to upload" in returnMessage:
		GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
		time.sleep(2)
		popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
		lines = GetElement(popup, By.TAG_NAME,'p')
		lines.click()
		time.sleep(1)
		errormsg = lines.text.strip()
		print errormsg

		closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
		closebutton.click()
		time.sleep(1)

		if 'Network Group Name : Bad value.' in errormsg:
			testComment = 'Test Pass- MTF File failed to upload with different network group of different sensor gateway on the ample..'
			printFP(testComment)
			return Global.FAIL , testComment
		else:
			testComment = 'Test Fail - MTF File upload successful with different network group of different sensor gateway on the ample. . .'
			printFP(testComment)
			return Global.PASS , testComment
	else:
		testComment = 'Test Fail - MTF Uploaded Successfully'
		printFP(testComment)
		return Global.PASS, testComment















