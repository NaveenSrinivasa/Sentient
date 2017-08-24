import Global
import json
import time
import csv
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from Utilities_Ample import *
from Utilities_Framework import *
from Ample_SysAdmin import *
from bs4 import BeautifulSoup as soup
from stripogram import html2text
import subprocess as sp
import filecmp
import unicodedata


def NumberOfErrorsSupportedForAFailedMTFUpload(input_file_path):
	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment

	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File with more than 50 devices details")
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

		#Scrolling the page to see complete error message details
		lines = GetElement(popup, By.TAG_NAME,'p')
		time.sleep(2)
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


def MTFErrorFormatToIndicateColumnHeadingInsteadOfColumnNumber(input_file_path):
	if input_file_path == None:
		testComment = 'Test Fail - Missing a mandatory parameter.'
		printFP(testComment)
		return Global.FAIL, testComment
	time.sleep(1)
	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File")
	UploadMTF(input_file_path)
	time.sleep(2)
	ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
	time.sleep(2)
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



def ExportFunctionalityForTheErrorMessagesRetrievedOnMTFFailure(input_file_path=None, downloadfolder=None, filetype=None):
	if input_file_path == None or downloadfolder == None or filetype == None:
		testComment = "Missing a mandatory parameter."
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
		errormsg = errormsgheader + errormsg
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
			errormsgfromfile = errormsgfromfile.strip()

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

		if len(errormsg) == len(errormsgfromfile) - 1:
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


def ASCIICharSetValidationForAllFieldsInMTF(input_file_path):
	if input_file_path == None:
		testComment = "Test Fail - Missing a mandatory parameter."
		printFP(testComment)
		return Global.FAIL, testComment
	
	printFP("INFO - Going to System Admin Page")
	GoToSysAdmin()
	time.sleep(2)
	printFP("INFO - Uploading the MTF File")
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









    

		
		


