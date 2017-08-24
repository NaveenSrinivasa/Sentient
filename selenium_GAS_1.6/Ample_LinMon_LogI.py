import Global
import re
import calendar
import time
from bs4 import BeautifulSoup as soup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
from Utilities_Ample import *

def AddRMSToCurrentLabelsLineMonitoringLogI(input_file_path):
	printFP('Verifying LogI Screen Phase Filters')
	params = ParseJsonInputFile(input_file_path)
	region = params['Region']
	substation = params['Substation']
	feeder = params['Feeder']
	site = params['Site']
	printFP('INFO - Going to Line Monitoring - LogI screen')
	GoToLineMon()
	GoToLineMonLogI()
	getsite = GetSiteFromTop(region, substation, feeder, site)
	time.sleep(5)
	if getsite:
		nodataavailable = NoDataAvailable('line-monitoring')
		if not nodataavailable == "No Data Available":
			printFP("Given site has logi data")
			printFP('INFO - Getting the phase details')
			roworder = LogiGetTableRowOrder('line-monitoring')

			'''rms_current_label = GetElements(Global.driver, By.XPATH,  "//div[contains(@class,'chart-container')]")
			print rms_current_label
			if 'RMS Current(A)' in rms_current_label:
				printFP('INFO - Label is present')
			else:
				printFP('INFO - Label is not present')'''

			if 'Max RMS Current Value ( A)' in roworder and 'Min RMS Current Value ( A)' in roworder and 'Avg RMS Current Value ( A)' in roworder and 'Yday Max RMS Current ( A)' in roworder and 'High RMS Current Threshold ( A)' in roworder:
				printFP('INFO- Expected labels are present on the phase details section')
			else:
				testComment = 'TEST FAIL - Expected labels are NOT present on the phase device details section'
				printFP(testComment)
				return Global.FAIL, testComment
		else:
			testComment = "Test Fail - Given site doesn't have any logi data points. Please point to a feeder which has logi data points"
			printFP(testComment)
			return Global.FAIL, testComment
	else:
		testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
		printFP(testComment)
		return Global.FAIL, testComment