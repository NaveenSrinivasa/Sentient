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
from bs4 import BeautifulSoup as soup
from Ample_GroupTree import *
import re
import csv
import pandas as pd



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

def NoFiltersAtSiteLevelSelectionExistingSiteSelection(input_file_path):
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

        subStation = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SUBSTATION-name')]")
        JustClick(subStation)
        time.sleep(2)

        feeder = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'FEEDER-name')]")
        JustClick(feeder)
        time.sleep(2)

        site = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SITE-name')]")
        JustClick(site)
        time.sleep(4)

        fwversion = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
        if fwversion.is_enabled() and fwversion.is_displayed():
            testComment = 'TEST FAIL - FW Version Filter is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Version Filter is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        fwstatus = GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button")
        if fwstatus.is_enabled() and fwstatus.is_displayed():
            testComment = 'TEST FAIL - FW Upgrade Filter Status is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Upgrade Filter Status is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        nwgroup = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
        if nwgroup.is_enabled() and nwgroup.is_displayed():
            testComment = 'TEST FAIL - Network Group Filter is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Network Group Filter is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        serialnumber = GetElement(Global.driver, By.XPATH, "//input[@ng-model='deviceSearch']")
        if serialnumber.is_enabled() and serialnumber.is_displayed():
            testComment = 'TEST FAIL - Serial Number Filter is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Serial Number Filter is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        testComment = 'TEST PASS - Filters are NOT present when user is in site.'
        printFP(testComment)
        return Global.PASS, testComment

    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment



def NoFiltersAtSiteLevelSelectionSelectASiteWithoutData(mtf_full_path):
    if mtf_full_path == None:
        mtf_full_path = Global.mtfPath
    with open(mtf_full_path, 'r') as inmtf:
        with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            time.sleep(1)
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
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
        printFP("INFO - Going to Device Management screen")
        GoToDevman()
        time.sleep(2)
        printFP("INFO - Reached Manage Devices screen")
        
        rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
        if rootElement.get_attribute('collapsed') == 'true':
            rootElement.click()
            time.sleep(2)
        GetRootNode()
        time.sleep(2)
    
        region = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'REGION-name')]")
        JustClick(region)
        time.sleep(2)

        subStation = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SUBSTATION-name')]")
        JustClick(subStation)
        time.sleep(2)
        feeder = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'FEEDER-name')]")
        JustClick(feeder)
        time.sleep(2)

        site = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SITE-name')]")
        JustClick(site)
        time.sleep(4)

        selected_device = SelectDevice(device['serial'])
        try:
            delete_device = GetElement(Global.driver, By.XPATH, "//button[text()='Delete']").click()
            time.sleep(2)
            GetElement(Global.driver, By.XPATH, "//button[text()='Ok']").click()
            time.sleep(3)
        except:
            time.sleep(2)
            delete_device = GetElement(Global.driver, By.XPATH, "//button[text()='Delete']").click()
            time.sleep(2)
            GetElement(Global.driver, By.XPATH, "//button[text()='Ok']").click()
            time.sleep(3)

        printFP("INFO - Going to Firmware Upgrade tab")
        GoToDevmanUp()
        time.sleep(2)
        printFP("INFO - Reached Firmware Upgrade tab")


        fwversion = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
        if fwversion.is_enabled() and fwversion.is_displayed():
            testComment = 'TEST FAIL - FW Version Filter is present when user is in site without data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Version Filter is NOT present when user is in site without data.'
            printFP(testComment)
            result = Global.PASS, testComment

        fwstatus = GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button")
        if fwstatus.is_enabled() and fwstatus.is_displayed():
            testComment = 'TEST FAIL - FW Upgrade Status Filter is present when user is in site without data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Upgrade Status Filter is NOT present when user is in site without data.'
            printFP(testComment)
            result = Global.PASS, testComment

        nwgroup = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
        if nwgroup.is_enabled() and nwgroup.is_displayed():
            testComment = 'TEST FAIL - Network Group Filter is present when user is in site without data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Network Group Filter is NOT present when user is in site without data.'
            printFP(testComment)
            result = Global.PASS, testComment

        serialnumber = GetElement(Global.driver, By.XPATH, "//input[@ng-model='deviceSearch']")
        if serialnumber.is_enabled() and serialnumber.is_displayed():
            testComment = 'TEST FAIL - Serial Number Filter is present when user is in site without data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Serial Number Filter is NOT present when user is in site without data.'
            printFP(testComment)
            result = Global.PASS, testComment

       
        testComment = 'TEST PASS - Expected  Filters are NOT present when user is in site without data.'
        printFP(testComment)
        return Global.PASS, testComment

    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def NoFiltersAtSiteLevelSelectionSelectASiteWithData(input_file_path):
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

        subStation = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SUBSTATION-name')]")
        JustClick(subStation)
        time.sleep(2)

        feeder = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'FEEDER-name')]")
        JustClick(feeder)
        time.sleep(2)

        site = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'SITE-name')]")
        JustClick(site)
        time.sleep(4)

        fwversion = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
        if fwversion.is_enabled() and fwversion.is_displayed():
            testComment = 'TEST FAIL - FW Version Filter is present when user is in site and has some data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Version Filter is NOT present when user is in site and has some data.'
            printFP(testComment)
            result = testComment

        fwstatus = GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button")
        if fwstatus.is_enabled() and fwstatus.is_displayed():
            testComment = 'TEST FAIL - FW Upgrade Filter Status is present when user is in site and has some data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Upgrade Filter Status is NOT present when user is in site and has some data.'
            printFP(testComment)
            result = testComment

        nwgroup = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
        if nwgroup.is_enabled() and nwgroup.is_displayed():
            testComment = 'TEST FAIL - Network Group Filter is present when user is in site and has some data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Network Group Filter is NOT present when user is in site and has some data.'
            printFP(testComment)
            result = testComment

        serialnumber = GetElement(Global.driver, By.XPATH, "//input[@ng-model='deviceSearch']")
        if serialnumber.is_enabled() and serialnumber.is_displayed():
            testComment = 'TEST FAIL - Serial Number Filter is present when user is in site and has some data.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Serial Number Filter is NOT present when user is in site and has some data.'
            printFP(testComment)
            result = testComment

        testComment = 'TEST PASS - Filters are NOT present when user is in site and has some data.'
        printFP(testComment)
        return Global.PASS, testComment

    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def NoFiltersAtSiteLevelSelectionNewNodeCreationViaGroupTree(mtf_full_path):
    if mtf_full_path == None:
       mtf_full_path = Global.mtfPath
    with open(mtf_full_path, 'r') as inmtf:
       with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            time.sleep(1)
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
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
        printFP("INFO - Going to Device Management screen")
        GoToDevman()
        time.sleep(2)
        printFP("INFO - Reached Manage Devices screen")
        printFP("INFO - Going to Firmware Upgrade tab")
        GoToDevmanUp()
        time.sleep(2)
        printFP("INFO - Reached Firmware Upgrade tab")
        feeder = GetFeederFromTop(device['region'], device['substation'], device['feeder'])
        
        time.sleep(2)
        
        elementfeeder = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'FEEDER-name')]")
        JustClick(elementfeeder)
        time.sleep(2)
        RightClickElement(elementfeeder)
        time.sleep(2)
        SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Add Site')
        time.sleep(2)
        printFP('INFO - Adding Site via Group Tree')
        sitename = GetElement(Global.driver, By.XPATH, "//html/body/div[4]/div/div/div[2]/form/div[1]/div/input")
        time.sleep(1.5)
        testsite = 'TestTest'
        sitename.send_keys(testsite)
        ClickButton(Global.driver, By.XPATH, "//button[text()='Add']")
        time.sleep(3)

        GetSiteFromTop(device['region'], device['substation'], device['feeder'], testsite)

        fwversion = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
        if fwversion.is_enabled() and fwversion.is_displayed():
            testComment = 'TEST FAIL - FW Version Filter is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Version Filter is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        fwstatus = GetElement(Global.driver, By.XPATH, "//span[@options='fwUpgradeStatusSelection.list']/div/button")
        if fwstatus.is_enabled() and fwstatus.is_displayed():
            testComment = 'TEST FAIL - FW Upgrade Filter Status is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - FW Upgrade Filter Status is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        nwgroup = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
        if nwgroup.is_enabled() and nwgroup.is_displayed():
            testComment = 'TEST FAIL - Network Group Filter is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Network Group Filter is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        serialnumber = GetElement(Global.driver, By.XPATH, "//input[@ng-model='deviceSearch']")
        if serialnumber.is_enabled() and serialnumber.is_displayed():
            testComment = 'TEST FAIL - Serial Number Filter is present when user is in site.'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'TEST PASS - Serial Number Filter is NOT present when user is in site.'
            printFP(testComment)
            result = testComment

        testComment = 'TEST PASS - Filters are NOT present when user is in site.'
        printFP(testComment)
        return Global.PASS, testComment

    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def OrganizationNodeLevelDisplayAndServerSidePagination(input_file_path, mtf_full_path):
    if mtf_full_path == None:
       mtf_full_path = Global.mtfPath
    with open(mtf_full_path, 'r') as inmtf:
       with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            time.sleep(1)
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
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
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(20)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "The file has been uploaded successfully." in returnMessage:
    	time.sleep(4)
        result = NavigatePages(input_file_path, UpgradePage=True)
        if 'TEST PASS - All pages matched as we progressed through the navigation buttons.' in result:
        	testComment = 'TEST PASS - Pagination works fine'
        	printFP(testComment)
        	return Global.PASS, testComment
        else:
        	testComment = 'TEST FAIL - Pagination NOT works proper.'
        	printFP(testComment)
        	return Global.FAIL, testComment
    else:
    	testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def DeviceFiltersForUpgradePage(mtf_full_path, page='Upgrade'):
    '''if mtf_full_path == None:
       mtf_full_path = Global.mtfPath
    with open(mtf_full_path, 'r') as inmtf:
       with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            time.sleep(1)
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
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
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(20)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "The file has been uploaded successfully." in returnMessage:'''
    GoToDevMan()   
    if page == 'Upgrade':
        GoToDevUpgrade()
        time.sleep(2)
        swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
        time.sleep(1)
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
        	#FilterChoices = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='option in options | filter:getFilter(input.searchFilter)']")
            FilterChoices[n].click()
            if n>0:
            	swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button").click()
            	FilterChoices[n-1].click()
            time.sleep(2)
            GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
            time.sleep(5)
            FilterChoices = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='option in options | filter:getFilter(input.searchFilter)']").click()
            filterText = GetElement(FilterChoices[n], By.XPATH, 'a/span[2]/span').text
            print filterText
            nodata = NoDataAvailable('device-management-upgrade')
            if nodata == "No Data Available":
            	testComment = 'INFO - No data for selected FW version'
                printFP(testComment)
            else:
          	    displayedSW = GetElements(Global.driver, By.XPATH, '//td[5]/span')
	            print displayedSW

	            for m in range(len(displayedSW)):
	                if displayedSW[m].text != filterText:
	                    result = Global.FAIL
	                    printFP("INFO - A displayed SW version does not match the filter applied.")
	                    testComment = 'All filters are working.'
	                    printFP(testComment)
	                    return Global.FAIL, testComment
	                    time.sleep(5)
	            testComment = 'All filters are working.'
	            printFP(testComment)
	            return Global.PASS, testComment

	    #swFilterButton.click()
	    #time.sleep(2)
	    testComment = 'All filters are working.'
	    printFP(testComment)
	    return Global.PASS, testComment

def FirmwareUpgradeList(mtf_full_path, input_file_path):
    if mtf_full_path == None:
       mtf_full_path = Global.mtfPath
    with open(mtf_full_path, 'r') as inmtf:
       with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            time.sleep(1)
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
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
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(20)
    device_name = device['serial']
    sgw = device['commserver']
    network_group = device['networkgroupname']
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "The file has been uploaded successfully." in returnMessage:
    	result = OTAPCheckOfflineDeviceUpgrade(input_file_path, device_name, False, sgw, network_group)
    	if 1 in result:
    		testComment = 'Test Pass - FW Button is disabled for offline device.'
    		printFP(testComment)
    		return Global.PASS, testComment
    	else:
    		testComment = 'Test Fail - FW Button is NOT disabled for offline device'
    		printFP(testComment)
    		return Global.FAIL, testComment
    else:
    	testComment = 'Test Fail - MTF File Failed to upload'
    	printFP(testComment)
    	return Global.FAIL, testComment

def FirmwareUpgradeButtonDisabledWithoutDevicesSelected(mtf_full_path):
    if mtf_full_path == None:
       mtf_full_path = Global.mtfPath
    with open(mtf_full_path, 'r') as inmtf:
       with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            time.sleep(1)
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
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
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(20)
    device_name = device['serial']
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "The file has been uploaded successfully." in returnMessage:
    	printFP("INFO - Going to Manage Device screen")
    	GoToDevMan()
    	time.sleep(1)
    	printFP("INFO - Reached Manage Device screen")
    	printFP("INFO - Going to Firmware Upgrade screen")
    	GoToDevUpgrade()
    	time.sleep(2)
    	printFP("INFO - Reached Firmware Upgrade screen")
    	printFP("INFO - Clicking the node which has devices")
    	GetRootNode()
    	time.sleep(2)
    	printFP("INFO - Checking upgrade button..")
    	Upgrade_button = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_button'])
    	res = Upgrade_button.is_enabled()

    	if True:
    		if 'disabled' in Upgrade_button.get_attribute('class'):
    			testComment = 'TEST PASS - Firmware Upgrade button is disabled and not clickable when user has not selected any devices..'
    			printFP(testComment)
    			return Global.PASS, testComment
    		else:
    		   testComment = 'TEST FAIL - Firmware Upgrade button is NOT disabled  when user has not selected any devices..'
    		   printFP(testComment)
    		   return Global.FAIL, testComment
        testComment = 'TEST FAIL - Firmware Upgrade button is clickable when user has not selected any devices..'
        printFP(testComment)
        return Global.FAIL, testComment
    else:
    	testComment = 'TEST FAIL - MTF File failed to upload..'
    	printFP(testComment)
    	return Global.FAIL, testComment


























        











