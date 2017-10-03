import json
import random
import os
import csv
from bs4 import BeautifulSoup as soup
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Utilities_Ample import *
from Ample_UserMan import *
from Ample_DevMan import *

def ViewOnlyRoleCapabilitiesExportData(input_file_path=None, downloadfolder=None):
    if input_file_path == None or downloadfolder == None:
        testComment = "Missing a mandatory parameter"
        printFP(testComment)
        return Global.FAIL, testComment

    """Must be logged in as a User"""
    params = ParseJsonInputFile(input_file_path)

    linemon = [xpaths['line_mon_disturbances'], xpaths['line_mon_waveforms'], xpaths['line_mon_logi']]
    devman = [xpaths['dev_man_manage_dev'], xpaths['dev_man_config'], xpaths['dev_man_inactive_dev'], xpaths['dev_man_phaseid']]

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = 'Provided input values are not valid.'
        printFP(testComment)
        return Global.FAIL, testComment
    time.sleep(5)
    GoToDevman()
    for i in range(len(devman)):
        GetElement(Global.driver, By.XPATH, devman[i]).click()
        nodataavailable = NoDataAvailable('device-management')
        if not nodataavailable == "No Data Available":
            try:
                exportbutton = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Export')]")
                exportbutton.click()
            except:
                testComment = 'TEST FAIL - User is not able to access export button in Dev Management Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment

            parentelement = GetElement(exportbutton, By.XPATH, "..")
            try:
                ClickButton(parentelement, By.XPATH, "//span[text()='CSV']")
            except:
                testComment = 'TEST FAIL - User is not able to access csv export button in Dev Management Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            csvlocation = downloadfolder + "export.csv"
            ClickButton(Global.driver, By.XPATH, "//button[contains(text(),'Export')]")
            try:
                ClickButton(parentelement, By.XPATH, "//span[text()='EXCEL']")
            except:
                testComment = 'TEST FAIL - User is not able to access excel export button in Dev Management Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            excellocation = downloadfolder + "export.xls"
            time.sleep(5) # must keep this sleep for export download time (bigger file will require you to change it)
            try:
                os.remove(csvlocation)
                time.sleep(1)
                os.remove(excellocation)
            except OSError as e:
                printFP(e)
                return Global.FAIL, 'TEST FAIL - ' + e

            testComment = "Successfully deleted exported files from download folder"
            printFP('INFO - ' + testComment)

    testComment = "Successfully exported files from device management pages with View Only Role Permission"
    printFP('INFO - ' + testComment)

    GoToLineMonitoring()
    time.sleep(1)

    for i in range(len(linemon)):
        GetElement(Global.driver, By.XPATH, linemon[i]).click()
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            try:
                exportbutton = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Export')]")
                exportbutton.click()
            except:
                testComment = 'TEST FAIL - User is not able to access export button in Line Monitoring Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment

            parentelement = GetElement(exportbutton, By.XPATH, "..")
            try:
                ClickButton(parentelement, By.XPATH, "//span[text()='CSV']")
            except:
                testComment = 'TEST FAIL - User is not able to access csv export button in Line Monitoring Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            csvlocation = downloadfolder + "export.csv"
            ClickButton(Global.driver, By.XPATH, "//button[contains(text(),'Export')]")
            try:
                ClickButton(parentelement, By.XPATH, "//span[text()='EXCEL']")
            except:
                testComment = 'TEST FAIL - User is not able to access excel export button in Line Monitoring Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            excellocation = downloadfolder + "export.xls"
            time.sleep(5) # must keep this sleep for export download time (bigger file will require you to change it)
            try:
                os.remove(csvlocation)
                time.sleep(1)
                os.remove(excellocation)
            except OSError as e:
                printFP(e)
                return Global.FAIL, 'TEST FAIL - ' + e

            testComment = "Successfully deleted exported files from download folder"
            printFP('INFO - ' + testComment)

    testComment = "Successfully exported files from both device management and line-monitoring pages with View Only Role Permission"
    printFP('INFO - ' + testComment)
    return Global.PASS, 'TEST PASS - ' + testComment


def ViewOnlyRoleCapabilitiesDownloadWaveforms(input_file_path=None):
    if not input_file_path:
        testComment = 'Test is missing mandatory parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    """Must be logged in as a User"""
    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']
    phase = params['Phase']

    GoToLineMonitoring()
    GoToLineMonFaultEvents()
    getsite = GetSiteFromTop(region, substation, feeder, site)
    time.sleep(5)
    if getsite:
        SelectAllEventStates()
        time.sleep(1)
        SelectAllEventTypes()
        time.sleep(1)
        SelectAllTriggeredDetectors()
        time.sleep(2)
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has faultevents")
            siterows = GetElements(Global.driver, By.XPATH, "//span[text()='" + site + "']")
            for row in siterows:
                try:
                    parentelement = GetElement(row, By.XPATH, "..")
                    deviceevent = GetElement(parentelement, By.XPATH, "//span[text()='" + phase + "']")
                except:
                    pass
            deviceevent.click()
            time.sleep(2)
            downloadbutton = GetElement(Global.driver, By.XPATH, "//button[text()='Download']")
            if 'disabled' in downloadbutton.get_attribute('class'):
                time.sleep(1)
                GoToLineMonWaveforms()
                time.sleep(1)
                downloadbutton = GetElement(Global.driver, By.XPATH, "//button[text()='Download']")
                if 'disabled' in downloadbutton.get_attribute('class'):
                    time.sleep(1)
                    testComment = 'TEST PASS - Unable to download waveforms with View Only User Role permission in both Waveforms and Fault Events screens'
                    printFP(testComment)
                    return Global.PASS, testComment
                else:
                    link.click()
                    testComment = 'TEST FAIL - Waveform Download button is not disabled in Line Monitoring Waveforms Page for View Only User Role'
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                link.click()
                testComment = 'TEST FAIL - Waveform Download button is not disabled in Line Monitoring Fault Events Page for View Only User Role'
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a site which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment
