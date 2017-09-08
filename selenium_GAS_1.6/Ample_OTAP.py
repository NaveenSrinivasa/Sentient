import Global
import os
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Utilities_Ample import *
from Utilities_Device import *
from Ample_SysAdmin import *
from Ample_ManageProfile import *
from Ample_LineMon import *
from Ample_DevMan import *
from bs4 import BeautifulSoup



def RemoveActionsColumnFromUpgradeTable(input_file_path):
	if input_file_path == None:
		testComment = 'Missing mandatory input file'
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
		printFP("INFO - Going to Firmware Upgrade tab")
		GoToDevmanUp()
		time.sleep(2)
		printFP("INFO - Reached Firmware Upgrade tab")
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		GetRootNode()
		time.sleep(2)
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		printFP('Getting Initial Load column names')
		columnlist = GetCurrentTableDisplayedColumnNames()
		print 'Initial Load column names are :', columnlist
		#Selecting few more columns from the dropdown
		filters_list = ["Site","Feeder","Substation","Region"]
		value = True
		time.sleep(1)
		#method to set the above filters from the dropdown menu
		SelectFromTableColumnFilters(filters_list, value)
		#Getting the entire column names from the table
		columnlist = GetCurrentTableDisplayedColumnNames()
		print 'Selected columns along with Initial Load column names are :', columnlist

		if not 'Actions' in columnlist:
			testComment = 'TEST PASS - Actions Column is not present in the Firmware Upgrade page.'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'TEST FAIL - Actions Column is  present in the Firmware Upgrade page.'
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'TEST FAIL - MTF Failed to Upload.'
		printFP(testComment)
		return Global.FAIL, testComment

def DeviceFiltersForUpgradePage(input_file_path=None, page=None):
	if not (input_file_path and page):
		testComment = 'Test is missing an input parameter value for this test'
		printFP(testComment)
		return Global.FAIL, testComment

	params = ParseJsonInputFile(input_file_path)
	GoToDevMan()

	#Go to location specified in input_file_path
	if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
		testComment = "Unable to locate site based on input file"
		printFP(testComment)
		return Global.FAIL, testComment

	if page == 'Upgrade':
		GoToDevUpgrade()
		time.sleep(2)
		swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
		time.sleep(2)
		swFilterButton.click()
		time.sleep(2)

		GetElement(Global.driver, By.ID, 'deselectAll').click()
		time.sleep(3)
		GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button").click()
		time.sleep(3)

		#Clicking the apply button
		GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
		time.sleep(5)

		if not ('Select' in GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button").text):
			result = Global.FAIL
			printFP("INFO - Filter SW does not display the text Select when user selects Show All filter from the dropdown")
		printFP("INFO - Filter SW displayed the text Select when user selects Show All filter from the dropdown")

		swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
		swFilterButton.click()
		time.sleep(2)

		FilterChoices = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='option in options | filter:getFilter(input.searchFilter)']")
		for n in range(len(FilterChoices)):
			FilterChoices[n].click()
			time.sleep(2)
			'''GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
			time.sleep(5)'''
			filterText = GetElement(FilterChoices[n], By.XPATH, 'a/span[2]/span').text
			print filterText
			displayedSW = GetElements(Global.driver, By.XPATH, '//td[5]/span')
			print displayedSW
			for m in range(len(displayedSW)):
				if displayedSW[m].text != filterText:
					result = Global.FAIL
					printFP("INFO - A displayed SW version does not match the filter applied.")
					time.sleep(5)
			FilterChoices[n].click()
			time.sleep(2)
		swFilterButton.click()
		time.sleep(2)

		#Check Firmware Upgrade Status Filter
		fwStatusButton = GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button")
		fwStatusButton.click()
		GetElement(Global.driver, By.ID, 'deselectAll').click()
		GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button").click()

		GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
		time.sleep(5)

		if not ('Select' in GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button").text):
			result = Global.FAIL
			printFP("INFO - Filter SW does not display the text Select when user selects Show All filter from the dropdown")

		fwStatusButton = GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button")
		fwStatusButton.click()
		time.sleep(1)

		FilterChoices = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='option in options | filter:getFilter(input.searchFilter)']")
		for n in range(len(FilterChoices)):
			FilterChoices[n].click()
			filterText = GetElement(FilterChoices[n], By.XPATH, 'a/span[2]/span').text
			displayedSW = GetElements(Global.driver, By.XPATH, '//td[15]/span' if page == 'Upgrade' else '//td[16]/span')
			for m in range(len(displayedSW)):
				if displayedSW[m].text != filterText:
					result = Global.FAIL
					printFP("INFO - A displayed Communication Type version does not match the filter applied.")
					time.sleep(5)
			FilterChoices[n].click()
		fwStatusButton.click()

		# Check Network Group Filter
		netwotkgroupFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
		netwotkgroupFilterButton.click()
		time.sleep(2)

		GetElement(Global.driver, By.ID, 'deselectAll').click()
		time.sleep(2)
		GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button").click()
		time.sleep(2)
		#Clicking the apply button
		GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
		time.sleep(5)
		if not ('Select' in GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button").text):
			result = Global.FAIL
			printFP("INFO - Filter SW does not display the text Select when user selects Show All from the dropdown.")

		netwotkgroupFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
		netwotkgroupFilterButton.click()
		time.sleep(2)


		FilterChoices = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='option in options | filter:getFilter(input.searchFilter)']")
		for n in range(len(FilterChoices)):
			FilterChoices[n].click()
			time.sleep(2)
			filterText = GetElement(FilterChoices[n], By.XPATH, 'a/span[2]/span').text
			displayedSW = GetElements(Global.driver, By.XPATH, '//td[17]/span')
			for m in range(len(displayedSW)):
				if (displayedSW[m].text != filterText) or (filterText == '(BLANKS)' and displayedSW[m].text == ''):
					result = Global.FAIL
				printFP("INFO - A displayed Network Group does not match the filter applied.")
				time.sleep(5)
			FilterChoices[n].click()
			time.sleep(2)

		netwotkgroupFilterButton.click()
		time.sleep(2)

		#Serial Number
		devicenameInputBox = GetElement(Global.driver, By.XPATH, "(//input[@type='text'])[2]").click()
		time.sleep(1)
		SendKeys(devicenameInputBox, "at-")

		GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
		time.sleep(5)

		# Check if any filter checks failed.
		if result == Global.FAIL:
			testComment = 'One or more filters are not working.'
			printFP(testComment)
			return Global.FAIL, testComment
		else:
			testComment = 'All filters are working.'
			printFP(testComment)
			return Global.PASS, testComment

		printFP("INFO - " + testComment)
		return result, 'TEST PASS - ' + testComment if result == Global.PASS else 'TEST FAIL - ' + testComment

def ColumnListChanges(input_file_path):
	if input_file_path == None:
		testComment = 'Missing mandatory input file'
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
		printFP("INFO - Going to Firmware Upgrade tab")
		GoToDevmanUp()
		time.sleep(2)
		printFP("INFO - Reached Firmware Upgrade tab")
		rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
		if rootElement.get_attribute('collapsed') == 'true':
			rootElement.click()
			time.sleep(2)
		GetRootNode()
		time.sleep(2)
		region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
		JustClick(region)
		time.sleep(2)

		#Getting column names - Initial load
		columnlist = GetCurrentTableDisplayedColumnNames()
		print 'Initial Load column names are : ', columnlist

		if 'Serial Number' in columnlist and 'Phase' in columnlist and 'Device Status' in columnlist and 'FW Version' in columnlist and 'FW Upgrade Status' in columnlist and 'Network Group' in columnlist and 'Sensor Gateway' in columnlist:
			testComment = 'Test Pass - Initial Load column names matched'
			printFP(testComment)
			result = Global.PASS, testComment
		else:
			testComment = 'Test Fail - Initial Load column names NOT matched'
			printFP(testComment)
			result = Global.FAIL, testComment


		filters_list = ["Site","Feeder","Substation","Region"]
		value = True
		time.sleep(1)
		#method to set the above filters from the dropdown menu
		SelectFromTableColumnFilters(filters_list, value)
		#Getting the entire column names from the table
		columnlist = GetCurrentTableDisplayedColumnNames()
		print 'All column names after selecting from the dropdown', columnlist

		if 'Serial Number' in columnlist and 'Phase' in columnlist and 'Device Status' in columnlist and 'FW Version' in columnlist and 'FW Upgrade Status' in columnlist and 'Network Group' in columnlist and 'Sensor Gateway' in columnlist and 'Site' in columnlist and 'Feeder' in columnlist and 'Substation' in columnlist and 'Region' in columnlist:
			testComment = 'Test Pass - Initial Load column names and selected columns matched'
			printFP(testComment)
			return Global.PASS, testComment
		else:
			testComment = 'Test Fail - Initial Load column names and selected columns NOT matched'
			printFP(testComment)
			return Global.FAIL, testComment
	
	else:
		testComment = 'TEST FAIL - MTF Failed to Upload.'
		printFP(testComment)
		return Global.FAIL, testComment












