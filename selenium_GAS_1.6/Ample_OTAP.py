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

    result, msg = UploadMTFTest(input_file_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
        printFP("INFO - Going to Firmware Upgrade tab")
        GoToDevUpgrade()
        GoToRootNodeAndClickOnRegion()
        printFP('Getting Initial Load column names')
        columnlist = GetCurrentTableDisplayedColumnNames()
        printFP('Initial Load column names are : {}' .format(columnlist))
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

    result, msg = UploadMTFTest(input_file_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
        printFP("INFO - Going to Firmware Upgrade tab")
        GoToDevUpgrade()
        GoToRootNodeAndClickOnRegion()

        #Getting column names - Initial load
        columnlist = GetCurrentTableDisplayedColumnNames()
        print 'Initial Load column names are : ', columnlist
        initial_load_column_names_list = ['Serial Number', 'Phase', 'Device Status', 'FW Version', 'FW Upgrade Status', 'Network Group', 'Sensor Gateway']
        if all(str(x) in initial_load_column_names_list for x in columnlist):
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
        all_column_names_list = ['Serial Number', 'Phase', 'Device Status', 'FW Version', 'FW Upgrade Status', 'Network Group', 'Sensor Gateway', 'Site', 'Feeder', 'Substation', 'Region']
        if all(str(x) in all_column_names_list for x in columnlist):
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

def NoFiltersAtSiteLevelSelectionExistingSiteSelection(input_file_path, input_file_path1):
    if input_file_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path1)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    result,  msg = UploadMTFTest(input_file_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
        printFP("INFO - Going to Firmware Upgrade tab")
        GoToDevUpgrade()
        GetLocationFromInput(region, sub, feeder, site)
        result, msg = CheckFiltersInSite()
        if 'TEST PASS' in msg:
            testComment = 'TEST PASS - NO Filters at the Site location'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Some Filters exists at the Site location'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def NoFiltersAtSiteLevelSelectionSelectASiteWithoutData(input_file_path, input_file_path1):
    if input_file_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path1)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    result, msg = UploadMTFTest(input_file_path, wait_for_online=False)
    with open(input_file_path, 'r') as inmtf:
        time.sleep(1)
        header = inmtf.readline()
        for line in inmtf:
            devInfo = line.strip('\n').split(',')
            device = CreateDeviceDictionary(devInfo)
    time.sleep(1)
    if 'TEST PASS' in msg:
        GoToDevman()
        GetLocationFromInput(region, sub, feeder, site)
        selected_device = SelectDevice(device['serial'])
        delete_device = GetElement(Global.driver, By.XPATH, "//button[text()='Delete']").click()
        time.sleep(2)
        GetElement(Global.driver, By.XPATH, "//button[text()='Ok']").click()
        time.sleep(2)
        GoToDevUpgrade()
        time.sleep(2)
        result, msg = CheckFiltersInSite()
        if 'TEST PASS' in msg:
            testComment = 'TEST PASS - NO Filters are present when User is in site location without any data.'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Some Filters exists when User is in site location without any data.'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def NoFiltersAtSiteLevelSelectionSelectASiteWithData(input_file_path, input_file_path1):
    if input_file_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path1)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    result, msg = UploadMTFTest(input_file_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
        printFP("INFO - Going to Firmware Upgrade tab")
        GoToDevUpgrade()
        GetLocationFromInput(region, sub, feeder, site)
        result, msg = CheckFiltersInSite()
        if 'TEST PASS' in msg:
            testComment = 'TEST PASS - NO Filters when User is in site location with data.'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Some Filters exists when User is in site location with data.'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment


def NoFiltersAtSiteLevelSelectionNewNodeCreationViaGroupTree(input_file_path, input_file_path1):
    if input_file_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path1)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    result, msg = UploadMTFTest(input_file_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
        printFP("INFO - Going to Firmware Upgrade tab")
        GoToDevUpgrade()
        time.sleep(2)
        printFP("INFO - Reached Firmware Upgrade tab")
        GetLocationFromInput(region, sub, feeder, 'none')
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
        time.sleep(2)
        GetLocationFromInput(region, sub, feeder, testsite)

        result, msg = CheckFiltersInSite()
        if 'TEST PASS' in msg:
            testComment = 'TEST PASS - NO Filters at the site location when added via Group Tree'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Some Filters exists at the site location when added via Group Tree'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - MTF Failed to Upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def OrganizationNodeLevelDisplayAndServerSidePagination(input_file_path, input_file_path1):
    if input_file_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    result, msg = UploadMTFTest(input_file_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
    	time.sleep(2)
        GoToDevUpgrade()
        result = NavigatePages(input_file_path1, UpgradePage=True)
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

def DeviceFiltersForUpgradePage(mtf_full_path, fw_list, fw_status_list, network_group_list, serial_number, page='Upgrade'):
    if mtf_full_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    result, msg = UploadMTFTest(mtf_full_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
        GoToDevUpgrade()
        GetRootNode()
        time.sleep(1)
        #Selecting show all from the FW version dropdown and it should display Select
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
        time.sleep(4)
        #Validating select is displayed or not when show all is selected
        if not ('Select' in GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button").text):
            result = Global.FAIL
            printFP("INFO - Filter SW does not display the text Select when user selects Show All filter from the dropdown")
        printFP("INFO - Filter SW displayed the text Select when user selects Show All filter from the dropdown")

        #Selecting some FW version from the dropdown
        selectFiltersByFirmware(fw_list)
        lis_fw = ', '.join(fw_list)

        #Checking whether selected version has data or not
        nodata = NoDataAvailable('device-management-upgrade')
        if nodata == "No Data Available":
            testComment = 'TEST FAIL - No data for selected FW version, select FW version which is available and try searching...'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            displayedSW = GetElements(Global.driver, By.XPATH, '//td[5]/span')
            for m in range(len(displayedSW)):
                if displayedSW[m].text != lis_fw:
                    testComment = "TEST FAIL - A displayed SW version does not match the filter applied."
                    printFP(testComment)
                    result = Global.FAIL
                testComment = 'TEST PASS - A displayed SW version  matched the filter applied.'
                printFP(testComment)
                result = Global.PASS

        #Selecting some FW Upgrade Status from the dropdown
        selectFiltersByUpgradeStatus(fw_status_list)
        status_list = ', '.join(fw_status_list)
        #Checking whether selected FWversion Status has data or not
        nodata = NoDataAvailable('device-management-upgrade')
        if nodata == "No Data Available":
            testComment = 'TEST FAIL - No data for selected FW status, select FW Upgrade Status which is available and try searching...'
            printFP(testComment)
            return Global.FAIL, testComment
        
        if fw_status_list:
            fw_statuses = GetElements(Global.driver, By.XPATH, "//tbody/tr[@ng-repeat='item in $data']/td[6]/span")
            for i in range(len(fw_statuses)):
                print fw_statuses[i].text
                if fw_statuses[i].text=='' and not('(BLANKS)' in status_list):
                    testComment = 'TEST FAIL - Displayed FW Version Status not matched'
                    printFP(testComment)
                    result = Global.FAIL
                elif fw_statuses[i].text in status_list:
                    testComment = 'TEST PASS - Displayed FW Version Status matched'
                    printFP(testComment)
                    result = Global.PASS
                else:
                    if fw_statuses[i].text not in status_list:
                        testComment = 'TEST FAIL - Displayed FW Version Status NOT matched'
                        printFP(testComment)
                        result = Global.FAIL
        #Selecting Network Group from the dropdown
        selectFiltersByNetworkGroup(network_group_list)
        nw_list = ', '.join(network_group_list)
        print nw_list

        if nodata == "No Data Available":
            testComment = 'TEST FAIL - No data for selected FW version, select FW version which is available and try searching...'
            printFP(testComment)
            return Global.FAIL, testComment
        #Checking whether selected Network Group has data or not
        nodata = NoDataAvailable('device-management-upgrade')
        if nodata == "No Data Available":
            testComment = 'TEST FAIL - No data for selected FW version, select FW version which is available and try searching...'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            displayedNG = GetElements(Global.driver, By.XPATH, '//td[7]/span')
            for m in range(len(displayedNG)):
                if displayedNG[m].text != nw_list:
                    testComment = "TEST FAIL - A displayed Network Group name does not match the filter applied."
                    printFP(testComment)
                    result = Global.FAIL
                testComment = 'TEST PASS - A displayed Network Group name  matched the filter applied.'
                printFP(testComment)
                result = Global.PASS

        #Entering Device name in serial number input box
        selectFiltersBySerialNumber(serial_number)
        print serial_number

        #Checking whether selected Network Group has data or not
        nodata = NoDataAvailable('device-management-upgrade')
        if nodata == "No Data Available":
            testComment = 'TEST FAIL - No data for selected FW version, select FW version which is available and try searching...'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            displayedDeviceName = GetElements(Global.driver, By.XPATH, '//td[2]/span')
            for m in range(len(displayedDeviceName)):
                if displayedDeviceName[m].text != serial_number:
                    testComment = "TEST FAIL - A displayed serial number does not match the filter applied."
                    printFP(testComment)
                    result = Global.FAIL
                testComment = 'TEST PASS - A displayed serial number matched the filter applied.'
                printFP(testComment)
                result = Global.PASS

        if result == Global.PASS:
            testComment = 'TEST PASS - Device Filters are working..'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL -Some Device Filters not working..'
            printFP(testComment)
            return Global.FAIL, testComment

    testComment = 'Test Fail - MTF File failed to Upload..'
    printFP(testComment)
    return Global.FAIL, testComment

def FirmwareUpgradeList(mtf_full_path, input_file_path, onlinedev, offlinedev):
    if mtf_full_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)

    #result, msg = UploadMTFTest(mtf_full_path, wait_for_online=False)
    #if 'TEST PASS' in msg:
    GoToDevman()
    GetRootNode()
    GoToDevUpgrade()

    if not GetLocationFromInput('dummyregion', 'dummysub', 'dummyfeeder', 'dummysite'):
        testComment = "Unable to locate locations based off input file in Upgrade Page"
        printFP(testComment)
        return Global.FAIL, testComment

    SelectDevice(offlinedev)
    result, testComment = CheckPageButtonLinkAccessibility("//button[text()='Firmware Upgrade']", 'disabled')
    print result
    print testComment
    if not result:
        printFP(testComment)
        return Global.FAIL, testComment
    else:
        printFP('INFO - Firmware upgrade button is disabled offline device')

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate locations based off input file in Upgrade Page"
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevman()

    if IsOnline(onlinedev):
        GoToDevUpgrade()
        testComment = 'INFO - %s did come online and successfully uploaded' %onlinedev
        SelectDevice(onlinedev)
        result, testComment = CheckPageButtonLinkAccessibility("//button[text()='Firmware Upgrade']", 'enabled')
        print result, testComment
        if not result:
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            printFP('INFO - Firmware upgrade button is enabled for online device')
    else:
        testComment = 'TEST FAIL - %s did not come online' % onlinedev
        result = Global.FAIL

    testComment = 'TEST PASS - Firmware upgrade button is enabled for online device and disabled for offline device'
    printFP(testComment)
    return Global.PASS, testComment

    '''else:
    	testComment = 'Test Fail - MTF File Failed to upload'
    	printFP(testComment)
    	return Global.FAIL, testComment'''

def FirmwareUpgradeButtonDisabledWithoutDevicesSelected(mtf_full_path):
    if mtf_full_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    result, msg = UploadMTFTest(mtf_full_path, wait_for_online=False)
    if 'TEST PASS' in msg:
        GoToDevman()
    	printFP("INFO - Going to Firmware Upgrade screen")
    	GoToDevUpgrade()
    	time.sleep(2)
    	printFP("INFO - Reached Firmware Upgrade screen")
    	GetRootNode()
    	time.sleep(2)
    	printFP("INFO - Checking upgrade button..")
    	Upgrade_button = GetElement(Global.driver, By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/div/span/div/button[1]").get_attribute('class')
        if 'disabled' in Upgrade_button:
            testComment = 'TEST PASS - Firmware Upgrade button is disabled and not clickable when user has not selected any devices..'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Firmware Upgrade button is NOT disabled  when user has not selected any devices..'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - MTF File failed to upload..'
        printFP(testComment)
        return Global.FAIL, testComment

def SetUpgradeRetries():
    printFP('INFO - Going to Firmware Upgrade Settings')
    GoToFWUpgradeSettings()
    printFP('INFO - Reached Firmware Upgrade Settings screen')
    ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_num_retries'])
    menuElement = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_num_retries_menu'])
    num_of_retry = GetElement(menuElement, By.XPATH, 'li[1]').click()
    time.sleep(1)
    retry_selected = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_num_retries']).text
    
    ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_settings_save'])
    time.sleep(2)

    GoToFWUpgradeSettings()

    retries_displayed_in_ui = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_num_retries']).text
    GetElement(Global.driver, By.XPATH, "//a[contains(@class,'remove-circle close-icon')]").click()
    time.sleep(1)

    if retries_displayed_in_ui == retry_selected:
        testComment = 'TEST PASS - Number of retries matched with saved retry number'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'TEST FAIL - Number of retries did not matched with saved retry number'
        printFP(testComment)
        return Global.FAIL, testComment

def SearchForSerialNumber(mtf_full_path):
    if mtf_full_path == None:
        testComment = 'Missing mandatory input file'
        printFP(testComment)
        return Global.FAIL, testComment

    result, msg = UploadMTFTest(mtf_full_path, wait_for_online=False)
    with open(mtf_full_path, 'r') as inmtf:
        time.sleep(1)
        header = inmtf.readline()
        for line in inmtf:
            devInfo = line.strip('\n').split(',')
            device = CreateDeviceDictionary(devInfo)
        device_name = device['serial']
    time.sleep(1)
    if 'TEST PASS' in msg:
        GoToDevman()
        printFP('INFO - Going to Firmware Upgrade page')
        GoToDevUpgrade()
        printFP('INFO - Reached Firmware Upgrade page')
        GetRootNode()

        printFP('INFO - Inputting Serial number in search tab')
        serial_number = GetElement(Global.driver, By.XPATH, "//input[@ng-model='deviceSearch']")
        ClearInput(serial_number)
        serial_number.send_keys(device['serial'])

        GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
        time.sleep(3)

        displayed_Serial_number = GetElement(Global.driver, By.XPATH, '//td[2]/span').text
        if device_name == displayed_Serial_number:
            testComment = 'TEST PASS - Entered/Searched device name is displayed in the UI'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Entered/Searched device name is NOT displayed in the UI'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - MTF File failed to upload'
        printFP(testComment)
        return Global.FAIL, testComment

def ConfigureFwUpgradeSettingsStartTimeLaterThanEndTime():
    printFP('INFO - Going to Firmware Upgrade Settings')
    GoToFWUpgradeSettings()
    printFP('INFO - Reached Firmware Upgrade Settings screen')

    frm_hr = GetElement(Global.driver, By.XPATH, "(//input[@ng-model='hours'])[1]")
    ClearInput(frm_hr)
    frm_time = "5"
    frm_hr.send_keys(frm_time)

    frm_sec = GetElement(Global.driver, By.XPATH, "(//input[@ng-model='minutes'])[1]")
    ClearInput(frm_sec)
    sec_time = "50"
    frm_sec.send_keys(sec_time)

    tog = GetElement(Global.driver, By.XPATH, "(//button[contains(@ng-click,'toggleMeridian')])[1]")
    if 'AM' in tog.text:
        print 'AM time'
    else:
        JustClick(tog)

    to_hr = GetElement(Global.driver, By.XPATH, "(//input[@ng-model='hours'])[2]")
    ClearInput(to_hr)
    to_time = "5"
    to_hr.send_keys(to_time)

    to_sec = GetElement(Global.driver, By.XPATH, "(//input[@ng-model='minutes'])[2]")
    ClearInput(to_sec)
    sec = "45"
    to_sec.send_keys(sec)

    tog1 = GetElement(Global.driver, By.XPATH, "(//button[contains(@ng-click,'toggleMeridian')])[2]")
    if 'AM' in tog1.text:
        print 'AM time'
    else:
        JustClick(tog1)

    save_button = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Save')]").click()
    time.sleep(3)
    msg = GetText(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[2]/div[2]/div/div/span", visible=True)
    print msg
    close_button = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'remove-circle close-icon')]").click()
    time.sleep(1)

    if "Start time must be earlier than end time." in msg:
        testComment = 'TEST PASS - Expected error msg is displayed when Start time is greater then the end time..'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'TEST FAIL - Expected error msg is NOT displayed when Start time is greater then the end time..'
        printFP(testComment)
        return Global.FAIL, testComment

def UpgradeMultipleDeviceswithDifferentSoftwareVersions(mtf_file_path1, mtf_file_path2, wait_for_online1, wait_for_online2):
    if mtf_file_path1 == None and mtf_file_path2 == None:
        testComment = "Test Fail - Missing a mandatory parameter."
        printFP(testComment)
        return Global.FAIL, testComment

    result, msg = UploadMTFTest(mtf_file_path1, wait_for_online1)
    result, msg = UploadMTFTest(mtf_file_path2, wait_for_online2)
    if 'TEST PASS' in msg:
        GoToDevUpgrade()
        GetRootNode()
        time.sleep(1)
        selectAll = GetElement(Global.driver, By.XPATH, "//input[@ng-model='selection.checkAll']")
        SetCheckBox(selectAll, 'true')
        time.sleep(1)
        upgrade_button = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Firmware Upgrade')]").click()
        time.sleep(2)
        msg = GetText(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[2]/div[2]/div/div/span", visible=True)
        close_button = GetElement(Global.driver, By.XPATH, "//a[contains(@class,'remove-circle close-icon')]").click()
        if 'Selection contains different From Software Versions' in msg:
            testComment = 'TEST PASS - Expected error message is displayed when multiple devices are selected for firmware upgrade with different FW version.'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Expected error message is NOT displayed when multiple devices are selected for firmware upgrade with different FW version.'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - Unexpected error/Failed to upload MTF file..'
        printFP(testComment)
        return Global.FAIL, testComment

def DeleteDeviceWhileUpgradeInProgress(mtf_file_path, input_file_path,  wait_for_online):
    if mtf_file_path == None:
        testComment = "Test Fail - Missing a mandatory parameter."
        printFP(testComment)
        return Global.FAIL, testComment
    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    result, msg = UploadMTFTest(mtf_file_path, wait_for_online)
    with open(mtf_file_path, 'r') as inmtf:
        time.sleep(1)
        header = inmtf.readline()
        for line in inmtf:
            devInfo = line.strip('\n').split(',')
            device = CreateDeviceDictionary(devInfo)
    time.sleep(1)
    serial_name = device['serial']
    serial_name_list = [serial_name]
    if 'TEST PASS' in msg:
        GetRootNode()
        chk = False
        ver = "2.6.0"
        result, msg = OTAPUpgrade(input_file_path, serial_name_list, ver, chk, 1200)
        if 'TEST PASS'in msg:
            testComment = 'INFO - Firmware Upgrade started for selected device.'
            printFP(testComment)
        else:
            testComment = 'TEST FAIL - Firmware Upgrade NOT started for selected device.'
            printFP(testComment)
            return Global.FAIL, testComment

        GoToDevman()
        
        result, msg= deleteDevice(input_file_path, serial_name_list, chk)
        if 'TEST PASS' in msg:
            GoToCurrentJobsUpgrade()
            nodata = NoDataAvailable('currentJobs')
            printFP(nodata)

            if nodata == 'No Data Available':
                testComment = 'TEST PASS - Selected device is deleted successfully When Firmware upgrade is in progress and job is not shown in Current job page..'
                printFP(testComment)
                return Global.PASS, testComment
            else:
                tab = GetElement(Global.driver, By.TAG_NAME, 'table')
                devtbody = GetElement(tab, By.TAG_NAME, "tbody")
                deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
                serial_name_from_table = []
                for row in deviceslist:
                    serial_num = GetElement(row, By.XPATH, "//td[3]/span").text
                    serial_name_from_table.append(serial_num)
                printFP(serial_name_from_table)
        
            if all(str(x) in serial_name_list for x in serial_name_from_table):
                testComment = 'TEST FAIL - Selected device is NOT deleted successfully When Firmware upgrade is in progress and job is shown in Current job page..'
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'TEST PASS - Selected device is deleted successfully When Firmware upgrade is in progress and job is not shown in Current job page..'
                printFP(testComment)
                return Global.PASS, testComment
        else:
            testComment = 'TEST FAIL - Device is not deleted.'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'TEST FAIL - MTF file failed to upload.'
        printFP(testComment)
        return Global.FAIL, testComment

def VerifyNumberOfDevicesSelectedForUpgrade(mtf_file_path, wait_for_online):
    if mtf_file_path == None:
        testComment = "Test Fail - Missing a mandatory parameter."
        printFP(testComment)
        return Global.FAIL, testComment

    result, msg = UploadMTFTest(mtf_file_path, wait_for_online)
    if 'TEST PASS' in msg:
        GoToDevUpgrade()
        GetRootNode()
        selectAll = GetElement(Global.driver, By.XPATH, "//input[@ng-model='selection.checkAll']")
        SetCheckBox(selectAll, 'true')
        time.sleep(1)

        device_table = GetElement(Global.driver, By.TAG_NAME, 'table')
        devtbody = GetElement(device_table, By.TAG_NAME, "tbody")
        deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
        chk_count = 0
        for row in deviceslist:
            chk_box = GetElement(row, By.XPATH, "//td[1]")
            chk_box.is_selected()
            chk_count += 1
        print 'Number of devices ', chk_count

        upgrade_button = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Firmware Upgrade')]").click()
        time.sleep(2)

        upgradeTitle = GetElement(Global.driver, By.XPATH, "//span[contains(@class, 'modal-title')]").text
        printFP("INFO - Upgrade Title: %s" %upgradeTitle)
        time.sleep(1)

        closeButton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
        closeButton.click()

        if str(chk_count) + ' Device' in upgradeTitle:
            testComment = "TEST PASS - Number of Devices Selected Matches the Amount of devices to be Upgraded."
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = "TEST FAIL -Number of Devices Selected NOT Matches the Amount of devices to be Upgraded."
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = "TEST FAIL - MTF File failed to upload..."
        printFP(testComment)
        return Global.FAIL, testComment