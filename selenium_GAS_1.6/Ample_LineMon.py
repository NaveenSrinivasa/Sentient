import Global
import re
import calendar
import time
from bs4 import BeautifulSoup as soup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
from Utilities_Ample import *



def GetViewChartZoom():
    zoomField = GetElement(Global.driver, By.XPATH, xpaths['dnp3_view_chart_zoomfilter'])
    allZooms = zoomField.find_elements_by_class_name('btn-common-right')
    zooms = {}
    # 1D 1W 1M 3M 6M 1Y
    for zoom in allZooms:
        print zoom.text
        zooms[zoom.text] = zoom
    return zooms

def GetViewChartPhases():
    phaseField = GetElement(Global.driver, By.XPATH, xpaths['dnp3_view_chart_phasefilter'])
    allPhases = phaseField.find_elements_by_class_name('btn-common-right')
    phases = {}
    # A B C
    for phase in allPhases:
        print phase.text
        phases[phase.text] = phase
    return phases

def OpenViewChartMultiSelect():
    selectDropdown = GetButton(Global.driver, By.XPATH, xpaths['dnp3_view_chart_multiselect'])
    time.sleep(1)
    selectDropdown.click()

def GetViewChartMultiSelect():
    OpenViewChartMultiSelect()
    selectMenu = GetElement(Global.driver, By.XPATH, xpaths['dnp3_multiselect_menu'])
    allChoices = selectMenu.find_elements_by_class_name('ng-scope')
    choices = []
    # activeUpTime activePowerLowTime energyReserveVoltage cndIrms cndTemp
    for choice in allChoices:
        print choice.text
        choices.append(choice)
    return choices

def ViewChartDrawGraph():
    button = ClickButton(Global.driver, By.XPATH, xpaths['dnp3_view_chart_draw'])

def CloseChart():
    button = ClickButton(Global.driver, By.XPATH, xpaths['dnp3_close_chart'])
    print 'Close chart'

def CheckForActiveFaults(device):
    """Navigates to the dashboard and looks in the active faults box for
    device.
    Args:
      dic device - dictionary representing the device to look for
                   parameters of device needed for this method are:
                   device['feeder']
                   device['phase']
                   device['serial']"""

    # Check the fault events table on dashboard
    GoToDashboard()
    time.sleep(1)

    ## Immediately set to fail if no active faults in table
    # Check active faults 3 times maybe?
    for retry in range(10):
        Global.driver.refresh()
        time.sleep(10)
        activeFaultTable = GetElement(Global.driver, By.XPATH, xpaths['dash_active_fault_table'])
        rows = GetElements(activeFaultTable, By.TAG_NAME, 'tr')
        if len(rows) == 0:
            result = Global.FAIL
        else:
            for row in rows:
                result = Global.FAIL
                gotFeeder = False
                gotPhase = False
                fields = GetElements(row, By.TAG_NAME, 'div')
                for field in fields:
                    if field.text == device['feeder']:
                        gotFeeder = True
                        break

                for field in fields:
                    if field.text == device['phase']:
                        gotPhase = True
                        break
                if gotFeeder and gotPhase:
                    result = Global.PASS
                    break
        if result == Global.FAIL:
            printFP('Did not get active fault. Retrying . . .')
            time.sleep(60)
            continue
        else:
            break
    if result == Global.PASS:
        testComment = 'Successfully triggered an active fault for %s' % device['serial']
    else:
        testComment = 'Failed to trigger an active fault for %s' % device['serial']
    printFP(testComment)
    return result, testComment

def WaitForActiveFaultToClear(device, timeout=1200):
    """Navigates to dashboard and watches the active faults box. If device
    is no longer there, active fault is cleared and returns pass.
    Args:
      dic device - dictionary representing a device
                   parameters needed for this method are:
                   device['feeder']
                   device['phase']
                   device['serial']"""

    # Check the fault events table until the fault clears
    GoToDashboard()
    time.sleep(2)
    i = 0
    while i < timeout:
        printFP('Waiting for active fault to clear . . .')
        time.sleep(60)
        Global.driver.refresh()
        time.sleep(10)
        activeFaultTable = GetElement(Global.driver, By.XPATH, xpaths['dash_active_fault_table'])
        rows = GetElements(activeFaultTable, By.TAG_NAME, 'tr')

        # Immediately return pass if there are no faults in the table
        if len(rows) == 0:
            testComment = 'All faults cleared'
            printFP(testComment)
            return Global.PASS, testComment
        # Look through each row. If find a matching feeder and phase,
        # fault is still active. If did not find a matching Feeder
        # and phase, fault has cleared.
        for row in rows:
            gotFeeder = False
            gotPhase = False
            fields = GetElements(row, By.TAG_NAME, 'div')
            for field in fields:
                if field.text == device['feeder']:
                    gotFeeder = True
                    break
            # Dont check phase if no feeder matches
            if not gotFeeder:
                continue
            for field in fields:
                if field.text == device['phase']:
                    gotPhase = True
                    break
            # Found the device, so fault is still active
            if gotFeeder and gotPhase:
                break
        if gotFeeder and gotPhase:
            printFP('Active fault not cleared yet.')
            i += 60
            continue
        else:
            testComment = 'Cleared active fault for %s' % device['serial']
            printFP(testComment)
            return Global.PASS, testComment
    testComment = 'Active fault did not clear within %d seconds' % timeout
    printFP(testComment)
    return Global.FAIL, testComment

def FaultEventTest(low_threshold_profile_name, norm_threshold_profile_name):
    """Triggers a fault event by applying a profile that sets FciThreshLimit
    low. Navigates to the dashboard and checks that fault was triggered.
    Applies another profile to clear the fault. Checks dashboard for fault
    clear."""

    # Get parameters for test
    device = GetOnlineDevice()
    # Subscribe for email alert
    #driver.refresh()
    #time.sleep(1)
    #SubscribeToAlerts(driver, xpaths, [device['region']])
    #time.sleep(2)

    # Navigate to config page and try to apply low threshold profile
    retry = 0
    while (retry < 3):
        # Apply profile to turn on logI features
        printFP('Applying profile')
        result, testComment = ApplyProfile(device, low_threshold_profile_name)
        if result == Global.PASS:
            result, testComment = CheckAppliedParameters(device, expectedParameters=['FciThreshLimit'])
            if result == Global.PASS:
                # Config success and got the desired parameters
                break
            else:
                # Did not get the desired parameters. Retry.
                retry += 1
                continue
        else:
            # The config failed 3 times within ApplyProfile.
            break
    if result == Global.FAIL:
        printFP('Apply profile %s failed' % low_threshold_profile_name)
        return result, testComment
    else:
        printFP('Apply profile succeeded after %d attempts' % retry)

    # Check if active fault was triggered
    time.sleep(5)
    activeFault = False
    result, testComment = CheckForActiveFaults(device)
    if result == Global.PASS:
        activeFault = True

    # Navigate to config page and try to apply normal threshold profile to clear fault
    retry = 0
    while (retry < 3):
        # Apply profile to turn on logI features
        result, testComment = ApplyProfile(device, norm_threshold_profile_name)
        if result == Global.PASS:
            result, testComment = CheckAppliedParameters(device, expectedParameters=['FciThreshLimit'])
            if result == Global.PASS:
                break
            else:
                # Retry the entire config if did not get the desired parameters applied
                retry += 1
                printFP('Retrying apply profile')
                continue
        else:
            # The config failed 3 times within ApplyProfile
            break
    if result == Global.FAIL:
        # Still check to see if the fault clears, even if normThreshProfile fails
        printFP('Apply profile %s failed' % norm_threshold_profile_name)
    else:
        printFP('Apply profile succeeded after %d attempts' % retry)
    applyProfileResult = result

    # If an active fault was not triggered, return fail
    if not activeFault:
        return Global.FAIL, 'Did not trigger active fault'

    result, testComment = WaitForActiveFaultToClear(device)
    if result == Global.FAIL and applyProfileResult == Global.FAIL:
        testComment = 'Did not clear active fault because config profile to %s failed' % norm_threshold_profile_name
    return result, testComment

def LogITest(profile_name, time_to_wait_for_logi_data):
    """Applies a profile to enable Log-I logging, then navigates to Log-I page
    and waits for data to appear. Returns pass if it finds average
    current data."""

    device = GetOnlineDevice()
    # Navigate to config page and try to apply normal threshold profile to clear fault
    retry = 0
    while (retry < 3):
        # Apply profile to turn on logI features
        result, testComment = ApplyProfile(device, profile_name)
        if result == Global.PASS:
            result, testComment = CheckAppliedParameters(device)
            if result == Global.PASS:
                break
            else:
                retry += 1
                printFP('Retrying apply profile')
                continue
        else:
            break

    if result == Global.FAIL:
        printFP('Apply profile %s failed' % profile_name)
        return result, testComment
    else:
        printFP('Apply profile succeeded after %d attempts.' % retry)

    # Wait 30 minutes for some log i data to appear
    # Navigate to Line Monitoring to see Log I data
    time.sleep(1)
    GoToLineMon()
    time.sleep(1)
    GoToLineMonLogI()
    time.sleep(1)
    GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
    i = 0
    while(i < time_to_wait_for_logi_data):
        printFP('Polling every 3 minutes for logI data . . .')
        time.sleep(180)
        Global.driver.refresh()
        time.sleep(10)

        # Check table
        table = GetElement(Global.driver, By.XPATH, xpaths['line_mon_logi_table'])
        rows = GetElements(table, By.TAG_NAME, 'tr')
        for row in rows:
            field = GetElement(row, By.CLASS_NAME, 'text-left')
            printFP(field.text)
            if field.text in 'Avg Current Value':
                values = GetElements(row, By.TAG_NAME, 'td')
                break
        for value in values:
            printFP(value.text)
            try:
                value = float(value.text)
            except:
                continue
            if value > 0:
                testComment = 'Got LogI data for %s' % device['serial']
                printFP(testComment)
                return Global.PASS, testComment
        else:
            testComment = 'Did not get LogI data'
            printFP(testComment)
            i += 180
            continue
    return Global.FAIL, testComment

def Dnp3PointsEmptyData(input_file_path):

    printFP('Verifying Dnp3Points empty data')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(2)

    if getfeeder:
        nodataavailableFeeder = NoDataAvailable('line-monitoring')
        if nodataavailableFeeder == "No Data Available":
            testComment = 'Test Pass - Found "No Data Available" Text for Feeder'
            printFP(testComment)

            GetSiteFromTop(region, substation, feeder, site)
            nodataavailableSite = NoDataAvailable('line-monitoring')
            if nodataavailableSite == "No Data Available":
                testComment = 'Test Pass - Found "No Data Available" Text for Both Feeder and Site'
                printFP(testComment)
                return Global.PASS, testComment
            else:
                testComment = 'Test Fail - Not Found "No Data Available" Text for Site'
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = 'Test Fail - Not Found "No Data Available" Text for Feeder'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment


def Dnp3PointsExportButton(input_file_path):

    printFP('Verifying Dnp3Points Screen Export button')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(3)

    if getfeeder:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
        #Get export button elements
            exportbuttonelements = GetElements(Global.driver, By.CLASS_NAME, 'dropdown-toggle')

            # find export toggle dorpdown button
            for exportbuttonelement in exportbuttonelements:
                exportbuttonelementname = exportbuttonelement.text
                if 'Export' in exportbuttonelementname:
                    try:
                        isdisabled = exportbuttonelement.get_attribute('disabled')
                    except Exception as e:
                        print e.message

                    if isdisabled is None:
                        try:
                            time.sleep(2)
                            exportbuttonelement.click()
                        except Exception as e:
                            printFP(e.message)
                            printFP('Test Fail - Unable to click Export Button')
                            break
                    else:
                        testComment = "Test Fail - Export Button is not enabled. Please point to a feeder which has Dnp3 Points"
                        printFP(testComment)
                        return Global.FAIL, testComment

                    timerangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
                    time.sleep(1)
                    timerangefilters = GetElements(timerangeframe, By.TAG_NAME, 'label')
                    time.sleep(1)
                    n=0
                    for timerangefilter in timerangefilters:
                        timerangefiltername = timerangefilter.text
                        testtimerange =  timerangefiltername
                        if timerangefiltername in ('1D','1W','1M', '3M'):
                            buttonclassname = timerangefilter.get_attribute('class')
                            if "active" in buttonclassname:
                                printFP('"Selected Export Time Range '+ testtimerange +'" button is already selected by default')
                            elif not "active" in buttonclassname:
                                try:
                                    timerangefilter.click()
                                    time.sleep(5)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testtimerange +'" Export Time Range filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                timerangebuttonstatus = GetTimeRangeButtonStatus(testtimerange)
                                if timerangebuttonstatus:
                                    testComment = 'Test Pass - "Selected Export Time Range '+ testtimerange +'" button got activated when select Export Time Range filter "' + testtimerange + '"'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Export Time Range '+ testtimerange +'" button is still not activated when select Export Time Range filter "' + testtimerange + '"'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                            else:
                                printFP('Unable to find whether Export Time Range "' + testtimerange + '" button is enabled or not')
                        else:
                            testComment = 'Test Fail - Export Time Range filter "' + testtimerange + '" is not in the defined list'
                            printFP(testComment)
                            return Global.FAIL, testComment

                        exportdropdownframe = GetElement(Global.driver, By.CLASS_NAME, 'export-dialog')
                        exportdropdownframe2 = GetElement(exportdropdownframe, By.CLASS_NAME, 'format-wrap')
                        exportdropdownlists = GetElements(exportdropdownframe2, By.TAG_NAME, 'input')
                        for exportdropdownlist in exportdropdownlists:
                            formattype = exportdropdownlist.get_attribute('value')
                            printFP('formattype %s' %formattype)
                            if 'excel' in formattype:
                                try:
                                    JustClick(exportdropdownlist)
                                    time.sleep(1)
                                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_export_button'])
                                    time.sleep(5)

                                    testComment = 'Test Pass - Able to export Dnp3 points in excel format for selected Export Time Range "' + testtimerange + '"'
                                    printFP(testComment)
                                    excelStatus = True

                                except:
                                    testComment = 'Test Fail - Unable to click "Excel" export option in Dnp3 Points screen'
                                    return Global.FAIL, testComment

                            elif 'csv' in formattype:
                                try:
                                    JustClick(exportdropdownlist)
                                    time.sleep(1)
                                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_export_button'])
                                    time.sleep(5)

                                    testComment = 'Test Pass - Able to export Dnp3 points in csv format for selected Export Time Range "' + testtimerange + '"'
                                    printFP(testComment)
                                    excelStatus = True

                                except:
                                    testComment = 'Test Fail - Unable to click "csv" export option in Dnp3 Points screen'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                        n=n+1

                    testComment = "Test Pass - Able to export Dnp3 Points in both Excel and CSV formats successfully"
                    printFP(testComment)
                    return Global.PASS, testComment

            testComment = "Test Fail - Export Button element is not found"
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Given feeder doesn't have any Dnp3 points. Please point to a feeder which has Dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def CheckDnp3PointsDisplays(input_file_path, Phase=None):

    printFP('Verifying data available for given phase in Dnp3 Points tabular data')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    pagename = 'line-monitoring'

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points data")
            if Phase is not None:
                #Get all filter button elements
                phasebuttonelement = GetElement(Global.driver, By.TAG_NAME, 'phase-filter')
                time.sleep(1)
                phasefilters = GetElements(phasebuttonelement, By.TAG_NAME, 'label')
                time.sleep(2)
                for phasefilter in phasefilters:
                    phasefiltername = phasefilter.text
                    testphase =  phasefiltername
                    if phasefiltername == Phase:
                        buttonclassname = phasefilter.get_attribute('class')
                        if "active" in buttonclassname:
                            printFP('"Phase '+ testphase +'" button is already selected by default')
                            filteredphasedata = Dnp3FilteredDataFromTable(Phase)
                            if any(str(x) in filteredphasedata for x in range(999)):
                                testComment = 'Test Pass - Phase '+ testphase +' data are available for selected site'
                                printFP(testComment)
                                return Global.PASS, testComment
                            else:
                                testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed in Dnp3 Points data table'
                                printFP(testComment)
                                return Global.FAIL, testComment

                        elif not "active" in buttonclassname:
                            printFP('"Phase '+ testphase +'" button is not selected by default. so checking')
                            try:
                                JustClick(phasefilter)
                                time.sleep(3)
                            except:
                                testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            filteredphasedata = Dnp3FilteredDataFromTable(Phase)
                            if any(str(x) in filteredphasedata for x in range(999)):
                                testComment = 'Test Pass - Phase '+ testphase +' data are available for selected site'
                                printFP(testComment)
                                return Global.PASS, testComment
                            else:
                                testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed in Dnp3 Points data table'
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Unable to find whether Phase "' + testphase + '" button is enabled or not')

            testComment = 'Test Fail - Any of Phase filters are not matched with given Phase "' + Phase + '"'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            printFP("Test Fail - Given site doesn't have Dnp3 Points. Please point to a site which has Dnp3 Points")
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsPhaseFilters(input_file_path):

    printFP('Verifying Dnp3 Points Screen Phase Filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points data")

            #Get all filter button elements
            phasebuttonelement = GetElement(Global.driver, By.TAG_NAME, 'phase-filter')
            time.sleep(1)
            phasefilters = GetElements(phasebuttonelement, By.TAG_NAME, 'label')
            time.sleep(2)
            for phasefilter in phasefilters:
                phasefiltername = phasefilter.text
                testphase =  phasefiltername
                if testphase in ('A','B','C'):
                    buttonclassname = phasefilter.get_attribute('class')
                    filteredphasedata = Dnp3FilteredDataFromTable(testphase)
                    if any(str(x) in filteredphasedata for x in range(999)):
                        printFP('"Phase '+ testphase +'" data are available for selected site')
                        if "active" in buttonclassname:
                            printFP('"Phase '+ testphase +'" button is already selected by default')
                            getcurrentphasecolumnnames = GetPhaseRowColumnHeaders()
                            if testphase in getcurrentphasecolumnnames:
                                printFP('"Phase '+ testphase +'" data are displaying on Dnp3 Point table when selected by default')

                                try:
                                    JustClick(phasefilter)
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                getcurrentphasecolumnnames = GetPhaseRowColumnHeaders()
                                if not testphase in getcurrentphasecolumnnames:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are not displayed on Dnp3 Point table when unselect Phase filter "' + testphase + '"'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are still displaying on Dnp3 Point table when unselect Phase filter "' + testphase + '"'
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                                try:
                                    JustClick(phasefilter)
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                                getcurrentphasecolumnnames = GetPhaseRowColumnHeaders()
                                if not testphase in getcurrentphasecolumnnames:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed on Dnp3 Point table when select Phase filter "' + testphase + '" again'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are displayed on Dnp3 Point table when select Phase filter "' + testphase + '" again'
                                    printFP(testComment)
                            else:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" column is not enabled in Dnp3 Point table when selected by default'
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                        elif not "active" in buttonclassname:
                            printFP('"Phase '+ testphase +'" button is already selected by default')
                            getcurrentphasecolumnnames = GetPhaseRowColumnHeaders()
                            if not testphase in getcurrentphasecolumnnames:
                                printFP('"Phase '+ testphase +'" data are not displayed on Dnp3 Point table when unselected by default')

                                try:
                                    JustClick(phasefilter)
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                getcurrentphasecolumnnames = GetPhaseRowColumnHeaders()
                                if not testphase in getcurrentphasecolumnnames:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed on Dnp3 Point table when select Phase filter "' + testphase + '"'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are displayed on Dnp3 Point table when select Phase filter "' + testphase + '"'
                                    printFP(testComment)

                                try:
                                    JustClick(phasefilter)
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                getcurrentphasecolumnnames = GetPhaseRowColumnHeaders()
                                if not testphase in getcurrentphasecolumnnames:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are not displayed on Dnp3 Point table when unselect Phase filter "' + testphase + '" again'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are still displaying on Dnp3 Point table when unselect Phase filter "' + testphase + '" again'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                            else:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" column is enabled in Dnp3 Point table when unselected by default'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                        else:
                            printFP('Unable to find whether Phase "' + testphase + '" button is enabled or not')
                    else:
                        printFP('"Phase '+ testphase +'" data are not available for selected site')

                else:
                    testComment = 'Test Fail - Phase filter "' + testphase + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Verified Dnp3 Point phasefilters successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            printFP("Test Fail - Given site doesn't have Dnp3 Points. Please point to a site which has Dnp3 Points")
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def Dnp3TableColumnFilters(input_file_path):

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']
    GoToLineMon()
    GoToLineMonDNP3()
    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(1)
    if getsite:
        try:
            isdataavailable = NoDataAvailable('line-monitoring')
        except Exception as e:
            printFP(e.message)

        if isdataavailable == "No Data Available":
            testComment = 'Test Fail - No DNP3 Points data for selected site. Please provide DNP3 Points data available site'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            dropdownmenubutton = GetButton(Global.driver, By.XPATH, xpaths['dnp3_dropdown_menu_button'])
            time.sleep(2)
            dropdownmenubutton.click()
            time.sleep(1)

            # Get all filters name
            dnp3filterstmp = Global.driver.find_element_by_css_selector('.dropdown-menu.column-wrap')
            time.sleep(1)
            dnp3filters = dnp3filterstmp.find_elements_by_css_selector('.checkbox.column-label')

            for dnp3filter in dnp3filters:
                dnp3filterelement = GetElement(dnp3filter, By.CLASS_NAME, 'column-title')
                time.sleep(1)
                dnp3filterName = dnp3filterelement.text

                printFP("Current Test Dnp3 Filter Name : " + dnp3filterName)

                inputElement = GetElement(dnp3filter, By.TAG_NAME, 'input')
                inputType = inputElement.get_attribute('type')

                # 2 conditions : one is check and verify. Second one is uncheck and verify.
                i=0
                while i<2:
                    if i==0:
                        value = 'false'
                        if 'checkbox' in inputType:
                            SetCheckBox(inputElement, value)
                            Dnp3TableColumnNames = GetCurrentDnp3TableColumnNames()
                            printFP(Dnp3TableColumnNames)
                            if not dnp3filterName in Dnp3TableColumnNames:
                                testComment= "Test Fail - Unchecked dnp3filter " + dnp3filterName + "is still visible in DNP3 Points Table"
                                printFP(testComment)
                                result = Global.FAIL
                                return result, testComment

                            else:
                                testComment= "Test Pass - Unchecked dnp3filter " + dnp3filterName + "is not visible in DNP3 Points Table"
                                printFP(testComment)
                                result = Global.PASS

                        else:
                            printFP('Test Fail - Do not recognize this input type')

                    elif i==1:
                        value = 'true'
                        if 'checkbox' in inputType:
                            SetCheckBox(inputElement, value)
                            Dnp3TableColumnNames = GetCurrentDnp3TableColumnNames()
                            printFP(Dnp3TableColumnNames)
                            if not dnp3filterName in Dnp3TableColumnNames:
                                testComment= "Test Pass - checked dnp3filter " + dnp3filterName + "is visible in DNP3 Points Table"
                                printFP(testComment)
                                result = Global.PASS

                            else:
                                testComment= "Test Fail - checked dnp3filter " + dnp3filterName + "is not visible in DNP3 Points Table"
                                printFP(testComment)
                                result = Global.FAIL
                                return result, testComment

                        else:
                            printFP('Test Fail - Do not recognize this input type')
                    i = i+1

            testComment = 'Test Pass - All DNP3 Table column name filters are success'
            printFP(testComment)
            return result, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsPastDateWithEmptyData(input_file_path, date=None, month=None, year=None):

    printFP('Verifying whether Dnp3 Points are displayed when select past date')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    month = calendar.month_name[int(month)]
    print month

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
            time.sleep(1)
            datepickerbutton.click()
            time.sleep(1)
            findcurrentmonthandyear = GetDatePickerCurrentTitle()
            currentmonthandyear = findcurrentmonthandyear.text
            #print('currentmonthandyear_1: %s' %currentmonthandyear)
            selectyear = None
            selectmonth = None
            selectdate = None
            if not year in currentmonthandyear:
                selectyear = SelectYearMonthAndDateFromCalendar(year, month, date)
                #print('selectyear %s:' %selectyear)
            elif not month in currentmonthandyear:
                selectmonth = SelectMonthAndDateFromCalendar(month, date)
                #print('selectmonth %s:' %selectmonth)
            else:
                selectdate = SelectDateFromCalendar(date)
                #print('selectdate %s:' %selectdate)

            if selectyear or selectmonth or selectdate:
                nodataavailable = NoDataAvailable('line-monitoring')
                if nodataavailable == "No Data Available":
                    testComment = 'Test Pass - Found "No Data Available" text when selected past date from datepicker'
                    printFP(testComment)
                    return Global.PASS, testComment
                else:
                    testComment = 'Test Fail - Dnp3 Points table is still displayed when selected past date : %s %s %s' %(year, month, date)
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Fail - Unable select a given date : %s %s %s' %(year, month, date)
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsClickTodayInDatepicker(input_file_path, date=None, month=None, year=None):

    printFP('Verifying whether Dnp3 Points are displayed when select today date after selected past date')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    month = calendar.month_name[int(month)]

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
            time.sleep(3)
            datepickerbutton.click()
            time.sleep(3)
            findcurrentmonthandyear = GetDatePickerCurrentTitle()
            currentmonthandyear = findcurrentmonthandyear.text
            #print('currentmonthandyear_1: %s' %currentmonthandyear)
            selectyear = None
            selectmonth = None
            selectdate = None
            if not year in currentmonthandyear:
                selectyear = SelectYearMonthAndDateFromCalendar(year, month, date)
                #print('selectyear %s:' %selectyear)
            elif not month in currentmonthandyear:
                selectmonth = SelectMonthAndDateFromCalendar(month, date)
                #print('selectmonth %s:' %selectmonth)
            else:
                selectdate = SelectDateFromCalendar(date)
                #print('selectdate %s:' %selectdate)

            if selectyear or selectmonth or selectdate:
                nodataavailable = NoDataAvailable('line-monitoring')
                if nodataavailable == "No Data Available":
                    testComment = 'Test Pass - Found "No Data Available" text when selected past date from datepicker'
                    printFP(testComment)
                    datepickerbutton.click()
                    time.sleep(3)
                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_today_date'])
                    time.sleep(5)
                    nodataavailable = NoDataAvailable('line-monitoring')
                    if nodataavailable == "No Data Available":
                        testComment = 'Test Fail - Found "No Data Available" text when clicked today button in datepicker. Please point to a site which has dnp3 points for today s date'
                        printFP(testComment)
                        return Global.FAIL, testComment

                    else:
                        testComment = 'Test Pass - Dnp3 Points table is displayed again when clicked today button in datepicker'
                        printFP(testComment)
                        alltimestampssame = CheckAllTimeStampsForSelectedDate()
                        if alltimestampssame:
                            currenttimestamp = GetCurrentTimeStamp()
                            currenttime = datetime.now()
                            currenttime = currenttime.strftime('%m/%d/%Y %H:%M:%S')
                            currenttime = currenttime.split(' ')
                            if currenttime[0] == currenttimestamp:
                                testComment = 'Test Pass - Dnp3 Points table is displayed with today time stamp when clicked today button in datepicker'
                                printFP(testComment)
                                return Global.PASS, testComment
                            else:
                                testComment = 'Test Fail - Dnp3 Points table is not displayed with today time stamp when clicked today button in datepicker'
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'Test Fail - Dnp3 Points table is not displayed with today time stamps on all rows when clicked today button in datepicker'
                            printFP(testComment)
                            return Global.FAIL, testComment
                else:
                    testComment = 'Test Fail - Dnp3 Points table is still displayed when selected past date : %s %s %s' %(year, month, date)
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Fail - Unable select a given date : %s %s %s' %(year, month, date)
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsClickClearInDatepicker(input_file_path, date=None, month=None, year=None):

    printFP('Verifying date reset to default date and DNP3 Points refreshed when select Clear in date picker')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    month = calendar.month_name[int(month)]

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
            time.sleep(1)
            datepickerbutton.click()
            time.sleep(1)
            findcurrentmonthandyear = GetDatePickerCurrentTitle()
            currentmonthandyear = findcurrentmonthandyear.text
            defaultmonthandyear = findcurrentmonthandyear.text.strip().split(' ')
            defaultyear = defaultmonthandyear[1]
            defaultmonth = defaultmonthandyear[0]
            defaultmonth = list(calendar.month_name).index(defaultmonth)
            defaultdate = GetDatePickerCurrentDate()
            #print('currentmonthandyear_1: %s' %currentmonthandyear)
            selectyear = None
            selectmonth = None
            selectdate = None
            if not year in currentmonthandyear:
                selectyear = SelectYearMonthAndDateFromCalendar(year, month, date)
                #print('selectyear %s:' %selectyear)
            elif not month in currentmonthandyear:
                selectmonth = SelectMonthAndDateFromCalendar(month, date)
                #print('selectmonth %s:' %selectmonth)
            else:
                selectdate = SelectDateFromCalendar(date)
                #print('selectdate %s:' %selectdate)

            if selectyear or selectmonth or selectdate:
                nodataavailable = NoDataAvailable('line-monitoring')
                if nodataavailable == "No Data Available":
                    testComment = 'Test Pass - Found "No Data Available" text when selected past date from datepicker'
                    printFP(testComment)
                    datepickerbutton.click()
                    time.sleep(1)
                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_clear_date'])
                    time.sleep(5)
                    nodataavailable = NoDataAvailable('line-monitoring')
                    if nodataavailable == "No Data Available":
                        testComment = 'Test Fail - Found "No Data Available" text when clicked Clear button from datepicker'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Dnp3 Points table is displayed again when clicked Clear button in datepicker'
                        printFP(testComment)
                        alltimestampssame = CheckAllTimeStampsForSelectedDate()
                        if alltimestampssame:
                            currenttimestamp = GetCurrentTimeStamp()
                            defaulttimestamp = '%s/%s/%s' %(defaultmonth,defaultdate,defaultyear)
                            if defaulttimestamp == currenttimestamp:
                                testComment = 'Test Pass - Dnp3 Points table is displayed with default time stamp when clicked Clear button in datepicker'
                                printFP(testComment)
                                return Global.PASS, testComment
                            else:
                                testComment = 'Test Fail - Dnp3 Points table is not displayed with default time stamp when clicked Clear button in datepicker'
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'Test Fail - Dnp3 Points table is not displayed with today time stamps on all rows when clicked Clear button in datepicker'
                            printFP(testComment)
                            return Global.FAIL, testComment
                else:
                    testComment = 'Test Fail - Dnp3 Points table is still displayed when selected past date : %s %s %s' %(year, month, date)
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Fail - Unable select a given date : %s %s %s' %(year, month, date)
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsPreviousAndNextDayButtons(input_file_path, tdate=None, month=None, year=None):

    printFP('Verify Previous and Next Day Buttons Navigation')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    tmpmonth = month
    month = calendar.month_name[int(month)]

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
            time.sleep(1)
            datepickerbutton.click()
            time.sleep(1)
            findcurrentmonthandyear = GetDatePickerCurrentTitle()
            currentmonthandyear = findcurrentmonthandyear.text
            #print('currentmonthandyear_1: %s' %currentmonthandyear)
            selectyear = None
            selectmonth = None
            selectdate = None
            if not year in currentmonthandyear:
                selectyear = SelectYearMonthAndDateFromCalendar(year, month, tdate)
                #print('selectyear %s:' %selectyear)
            elif not month in currentmonthandyear:
                selectmonth = SelectMonthAndDateFromCalendar(month, tdate)
                #print('selectmonth %s:' %selectmonth)
            else:
                selectdate = SelectDateFromCalendar(tdate)
                #print('selectdate %s:' %selectdate)

            if selectyear or selectmonth or selectdate:
                nodataavailable = NoDataAvailable('line-monitoring')
                if nodataavailable == "No Data Available":
                    testComment = 'Test Fail - Found "No Data Available" text when select given date in datepicker. Please choose a site and date which has data for previous and Next day of given date'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    currenttimestamp = GetCurrentTimeStamp()
                    time.sleep(1)
                    givendate = '%s/%s/%s' %(tmpmonth,tdate,year)
                    time.sleep(1)
                    if givendate == currenttimestamp:
                        testComment = 'Test Pass - Dnp3 Points table is displayed with given date time stamp when selected given date in datepicker'
                        printFP(testComment)
                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_prevday_button'])
                        time.sleep(5)
                        nodataavailable = NoDataAvailable('line-monitoring')
                        if nodataavailable == "No Data Available":
                            testComment = 'Test Fail - Found "No Data Available" text when select previous date of today in datepicker. Please choose a site and date which has data for previous and Next day of given date '
                            printFP(testComment)
                            return Global.FAIL, testComment
                        else:
                            currenttimestamp = GetCurrentTimeStamp()
                            currenttimestamp = str(currenttimestamp).strip().replace('/','')
                            t=time.strptime(currenttimestamp,'%m%d%Y')
                            newdate = date(t.tm_year,t.tm_mon,t.tm_mday)+timedelta(1)
                            newdate = newdate.strftime('%m/%d/%Y %H:%M:%S')
                            newdate = newdate.split(' ')
                            givendate = '%s/%s/%s' %(tmpmonth,tdate,year)
                            if givendate == newdate[0]:
                                testComment = 'Test Pass - Dnp3 Points table is displayed with previous date of given date time stamp when selected previous day button in datepicker'
                                printFP(testComment)
                                ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_nextday_button'])
                                time.sleep(5)
                                ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_nextday_button'])
                                time.sleep(5)
                                nodataavailable = NoDataAvailable('line-monitoring')
                                if nodataavailable == "No Data Available":
                                    testComment = 'Test Fail - Found "No Data Available" text when select next date of today in datepicker. Please choose a site and date which has data for previous and Next day of given date '
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    currenttimestamp = GetCurrentTimeStamp()
                                    currenttimestamp = str(currenttimestamp).replace('/','')
                                    t=time.strptime(currenttimestamp,'%m%d%Y')
                                    newdate = date(t.tm_year,t.tm_mon,t.tm_mday)-timedelta(1)
                                    newdate = newdate.strftime('%m/%d/%Y %H:%M:%S')
                                    newdate = newdate.split(' ')
                                    givendate = '%s/%s/%s' %(tmpmonth,tdate,year)
                                    if givendate == newdate[0]:
                                        testComment = 'Test Pass - Dnp3 Points table is displayed with next date of given date time stamp when selected next day button in datepicker'
                                        printFP(testComment)
                                    else:
                                        testComment = 'Test Fail - Dnp3 Points table is not displayed with next date of given date time stamp when selected next day button in datepicker'
                                        printFP(testComment)
                                        return Global.FAIL, testComment
                            else:
                                testComment = 'Test Fail - Dnp3 Points table is not displayed with previous date of given date time stamp when selected next day button in datepicker'
                                printFP(testComment)
                                return Global.FAIL, testComment
                    else:
                        testComment = 'Test Fail - Dnp3 Points table is not displayed with given date time stamp when selected given date in datepicker'
                        printFP(testComment)
                        return Global.FAIL, testComment
            else:
                testComment = 'Test Fail - Unable select a given date : %s %s %s' %(year, month, date)
                printFP(testComment)
                return Global.FAIL, testComment

            testComment = 'Test Pass - Verified Dnp3 Points Prev and Next day buttons successfully. All test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def Dnp3PointsNextDayButtonForFutureDate(input_file_path):

    printFP('Verify Next Day Button State for Futre and Past date selection')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
            time.sleep(1)
            datepickerbutton.click()
            time.sleep(1)
            ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_today_date'])
            time.sleep(5)
            nodataavailable = NoDataAvailable('line-monitoring')
            if nodataavailable == "No Data Available":
                testComment = 'INFO - Found "No Data Available" text when selected today date in datepicker'
                printFP(testComment)
            else:
                testComment = 'Test Pass - Dnp3 Points table is displayed when selected today date'
                printFP(testComment)
                nextdaybutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_nextday_button'])
                time.sleep(2)
                classname = nextdaybutton.get_attribute('class')
                if not 'disabled' in classname:
                    testComment = 'Test Fail - Next Day button is not disabled when select today date in datepicker'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Next Day Button is disabled when select today date in datepicker'
                    printFP(testComment)

                    now = datetime.now()
                    todaydate = '%s/%s/%s' %(now.month,now.day,now.year)
                    todaydate = str(todaydate).strip().replace('/','')
                    t=time.strptime(todaydate,'%m%d%Y')
                    prevdate = date(t.tm_year,t.tm_mon,t.tm_mday)-timedelta(1)
                    month = str(calendar.month_name[prevdate.month])
                    year = str(prevdate.year)
                    tdate = str(prevdate.day)
                    datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
                    time.sleep(1)
                    datepickerbutton.click()
                    time.sleep(1)
                    findcurrentmonthandyear = GetDatePickerCurrentTitle()
                    currentmonthandyear = findcurrentmonthandyear.text
                    #print('currentmonthandyear_1: %s' %currentmonthandyear)
                    selectyear = None
                    selectmonth = None
                    selectdate = None
                    if not year in currentmonthandyear:
                        selectyear = SelectYearMonthAndDateFromCalendar(year, month, tdate)
                        #print('selectyear %s:' %selectyear)
                    elif not month in currentmonthandyear:
                        selectmonth = SelectMonthAndDateFromCalendar(month, tdate)
                        #print('selectmonth %s:' %selectmonth)
                    else:
                        selectdate = SelectDateFromCalendar(tdate)
                        #print('selectdate %s:' %selectdate)

                    if selectyear or selectmonth or selectdate:
                        nodataavailable = NoDataAvailable('line-monitoring')
                        if nodataavailable == "No Data Available":
                            testComment = 'INFO - Found "No Data Available" text when select previous date of today s date in datepicker'
                            printFP(testComment)
                        else:
                            testComment = 'Test Pass - Dnp3 Points table is displayed when selected previous date of today s date'
                            printFP(testComment)
                            nextdaybutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_nextday_button'])
                            time.sleep(2)
                            classname = nextdaybutton.get_attribute('class')
                            if 'disabled' in classname:
                                testComment = 'Test Fail - Next Day button is disabled when selected previous date of today s date'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Next Day Button is not disabled when selected previous date of today s date'
                                printFP(testComment)

            testComment = 'Test Pass - Verified Dnp3 Points Next Day button state for future and past date successfully. All test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsFeederTimeRangeSelection(input_file_path):

    printFP('Verify Dnp3 Points feeder level time range selection')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(3)
    if getfeeder:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has Dnp3 Points")
            datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
            time.sleep(1)
            datepickerbutton.click()
            time.sleep(1)
            ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_today_date'])
            time.sleep(5)
            nodataavailable = NoDataAvailable('line-monitoring')
            if nodataavailable == "No Data Available":
                testComment = 'Test Fail - Found "No Data Available" text when selected today date in datepicker. Please point to a Feeder which has dnp3 points for today s date'
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Dnp3 Points table is displayed when selected today date'
                printFP(testComment)
                currenttimerangeelement = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_feeder_timerange_button'])
                currenttimerange = currenttimerangeelement.text.replace('"','')
                currenttimerange = ''.join(currenttimerange.split())
                currenttimerange = currenttimerange.split('-')
                if '12:00AM' in currenttimerange[0]:
                    minrange = currenttimerange[0][:2].replace('12','00')
                    minrange = int(minrange)
                    maxrange = currenttimerange[1][:2]
                    maxrange = int(maxrange)
                    maxrange = maxrange + 1
                    minchange = True
                elif '01:00PM' in currenttimerange[1]:
                    minrange = currenttimerange[0][:2]
                    minrange = int(minrange)
                    maxrange = currenttimerange[1][:2].replace('01','13')
                    maxrange = int(maxrange)
                    maxrange = maxrange + 1
                    maxchange = True
                else:
                    minrange = currenttimerange[0][:2]
                    minrange = int(minrange)
                    maxrange = currenttimerange[1][:2]
                    maxrange = int(maxrange)
                    maxrange = maxrange + 1
                    minchange = False
                    maxchange = False
                alltimestampssame = CheckAllTimeStampsForSelectedDate()
                if alltimestampssame:
                    alltimeranges = GetCurrentAllTimeRanges(minchange, maxchange)
                    #selectedrange = range(minrange, maxrange)
                    #print('selectedrange: %s' %selectedrange)
                    if all(int(x) not in range(minrange, maxrange) for x in alltimeranges):
                        testComment = 'Test Fail - Dnp3 Points table is not displayed within the range of selected time range'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Dnp3 Points table is displayed within the range of selected time range'
                        printFP(testComment)
                        defaulttimerange = currenttimerangeelement.text.replace('"','')
                        defaulttimerange = ''.join(defaulttimerange.split())
                        printFP('defaulttimerange: %s' %defaulttimerange)
                        JustClick(currenttimerangeelement)
                        time.sleep(3)
                        parentelement = GetElement(currenttimerangeelement, By.XPATH, '..')
                        dropdownlist = GetElement(parentelement, By.TAG_NAME, 'ul')
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                        m=0
                        for option in dropdownoptions:
                            try:
                                filternameElement = GetElement(option, By.XPATH, 'a/span[2]/span')
                                filtername = filternameElement.text
                                filtername = ''.join(filtername.split())
                                #filtername = raw_filtername.replace(' ','').replace('"','')
                                print('filtername: %s' %filtername)
                                #print('defaulttimerange: %s' %defaulttimerange)
                                if filtername == defaulttimerange:
                                    currentposition = m
                                    #print('currentposition: %s' %currentposition)
                                    break
                                else:
                                    m=m+1
                            except:
                                pass
                        n=0
                        for option in dropdownoptions:
                            if n < currentposition:
                                filterelement = GetElement(option, By.TAG_NAME, 'a/span[2]/span')
                                filtername = filterelement.text.strip()
                                filtername = ''.join(filtername.split())
                                #filtername = raw_filtername.replace(' ','').replace('"','')
                                #print('filtername2: %s' %filtername)
                                ariaexpanded = currenttimerangeelement.get_attribute('aria-expanded')
                                #print('ariaexpanded: %s' %ariaexpanded)
                                if 'false' in ariaexpanded:
                                    JustClick(currenttimerangeelement)
                                JustClick(filterelement)
                                time.sleep(5)
                                currenttimerangeelement = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_feeder_timerange_button'])
                                currenttimerange = currenttimerangeelement.text.replace('"','')
                                currenttimerange = ''.join(currenttimerange.split())
                                rawcurrenttimerange = currenttimerange
                                currenttimerange = currenttimerange.split('-')
                                nodataavailable = NoDataAvailable('line-monitoring')
                                if not nodataavailable == "No Data Available":
                                    if '12:00AM' in currenttimerange[0]:
                                        minrange = currenttimerange[0][:2].replace('12','00')
                                        minrange = int(minrange)
                                        maxrange = currenttimerange[1][:2]
                                        maxrange = int(maxrange)
                                        maxrange = maxrange + 1
                                        minchange = True
                                        maxchange = False

                                    elif '01:00PM' in currenttimerange[1]:
                                        minrange = currenttimerange[0][:2]
                                        minrange = int(minrange)
                                        maxrange = currenttimerange[1][:2].replace('01','13')
                                        maxrange = int(maxrange)
                                        maxrange = maxrange + 1
                                        minchange = False
                                        maxchange = True
                                    else:
                                        minrange = currenttimerange[0][:2]
                                        minrange = int(minrange)
                                        maxrange = currenttimerange[1][:2]
                                        maxrange = int(maxrange)
                                        maxrange = maxrange + 1
                                        minchange = False
                                        maxchange = False
                                    alltimestampssame = CheckAllTimeStampsForSelectedDate()
                                    if alltimestampssame:
                                        alltimeranges = GetCurrentAllTimeRanges(minchange, maxchange)
                                        print alltimeranges
                                        #selectedrange = range(minrange, maxrange)
                                        #print('selectedrange: %s' %selectedrange)
                                        if all(int(x) not in range(minrange, maxrange) for x in alltimeranges):
                                            testComment = 'Test Fail - Dnp3 Points table is not displayed within the range of selected time range: %s' %filtername
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                        else:
                                            testComment = 'Test Pass - Dnp3 Points table is displayed within the range of selected time range'
                                            printFP(testComment)
                                    else:
                                        testComment = 'Test Fail - Dnp3 Points table is not displayed with same time stamps on all rows when selected time range: %s' %filtername
                                        printFP(testComment)
                                        return Global.FAIL, testComment
                                else:
                                    printFP('INFO - There is no Dnp3 Points for selected time range %s. Skipping test for this time range.' %rawcurrenttimerange)
                            n=n+1

                else:
                    testComment = 'Test Fail - Dnp3 Points table is not displayed with today time stamps on all rows when clicked today button in datepicker'
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Verified Dnp3 Points Feeder level time rage selection successfully. All test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Given Feeder doesn't have dnp3 points. Please point to a Feeder which has dnp3 points for today's date"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsCheckButtonsWithNoData(input_file_path):

    printFP('Export, Refresh, and View Chart Buttons are Disabled When No Data for Feeder and Site')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(2)

    if getfeeder:
        nodataavailableFeeder = NoDataAvailable('line-monitoring')
        if nodataavailableFeeder == "No Data Available":
            testComment = 'Test Pass - Found "No Data Available" Text for Feeder'
            printFP(testComment)
            exportbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_export_button'])
            viewchartbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_button'])
            refershbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_refresh_button'])
            time.sleep(2)
            classnameexport = exportbutton.get_attribute('class')
            classnameviewchart = viewchartbutton.get_attribute('class')
            classnamerefresh = refershbutton.get_attribute('class')
            if not 'ng-hide' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is not hidden for selected feeder %s' %feeder
                printFP(testComment)
                return Global.FAIL, testComment
            elif not 'disabled' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is not disabled for selected feeder %s' %feeder
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - View Chart button is hidden for selected feeder %s' %feeder
                printFP(testComment)
                if not 'disabled' in classnamerefresh:
                    testComment = 'Test Fail - Refresh button is not disabled for selected feeder %s' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Refresh button is disabled for selected feeder %s' %feeder
                    printFP(testComment)
                    if not 'disabled' in classnameexport:
                        testComment = 'Test Fail - Export button is not disabled for selected feeder %s' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Export button is disabled for selected feeder %s' %feeder
                        printFP(testComment)

            GetSiteFromTop(region, substation, feeder, site)
            nodataavailableSite = NoDataAvailable('line-monitoring')
            if nodataavailableSite == "No Data Available":
                testComment = 'Test Pass - Found "No Data Available" Text for Site'
                printFP(testComment)
                exportbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_export_button'])
                viewchartbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_button'])
                refershbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_refresh_button'])
                time.sleep(2)
                classnameexport = exportbutton.get_attribute('class')
                classnameviewchart = viewchartbutton.get_attribute('class')
                classnamerefresh = refershbutton.get_attribute('class')
                if 'ng-hide' in classnameviewchart:
                    testComment = 'Test Fail - View Chart button is hidden for selected site %s . It should be disabled.' %site
                    printFP(testComment)
                    return Global.FAIL, testComment
                elif not 'disabled' in classnameviewchart:
                    testComment = 'Test Fail - View Chart button is not disabled for selected site %s' %site
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - View Chart button is disabled for selected site %s' %site
                    printFP(testComment)
                    if not 'disabled' in classnamerefresh:
                        testComment = 'Test Fail - Refresh button is not disabled for selected site %s' %site
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Refresh button is disabled for selected site %s' %site
                        printFP(testComment)
                        if not 'disabled' in classnameexport:
                            testComment = 'Test Fail - Export button is not disabled for selected site %s' %site
                            printFP(testComment)
                            return Global.FAIL, testComment
                        else:
                            testComment = 'Test Pass - Export button is disabled for selected site %s' %site
                            printFP(testComment)
            else:
                testComment = 'Test Fail - Not Found "No Data Available" Text for Site'
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = 'Test Fail - Not Found "No Data Available" Text for Feeder'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment


def Dnp3PointsViewChart(input_file_path):

    printFP('Verifying date reset to today date and DNP3 Points refreshed when select Clear in date picker')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            viewchartbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_button'])
            time.sleep(2)
            classnameviewchart = viewchartbutton.get_attribute('class')
            if 'ng-hide' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is hidden for selected site %s . It should be disabled.' %site
                printFP(testComment)
                return Global.FAIL, testComment
            elif 'disabled' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is disabled for selected site %s' %site
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - View Chart button is not disabled for selected site %s' %site
                printFP(testComment)
                JustClick(viewchartbutton)
                time.sleep(1)
                viewchartdialog = GetElement(Global.driver, By.CLASS_NAME, 'modal-dialog')
                if viewchartdialog:
                    dnp3pointsbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_dnp3points_button'])
                    #JustClick(dnp3pointsbutton)
                    time.sleep(1)
                    parentelement = GetElement(dnp3pointsbutton, By.XPATH, '..')
                    dropdownmenu = GetElement(parentelement, By.TAG_NAME, 'ul')
                    dropdownlist = GetElements(dropdownmenu, By.TAG_NAME, 'li')
                    dropdownheader = dropdownlist[0].text
                    #print('dropdownheader1:%s' %dropdownheader)
                    n = 0
                    while n<5:
                        dnp3pointsbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_dnp3points_button'])
                        JustClick(dnp3pointsbutton)
                        time.sleep(1)
                        dropdownheader = 'Selected 0 of 3'

                        if n<3:
                            dropdownheadercondition = 'Selected 3 of 3'
                        elif n==3:
                            dropdownheadercondition = 'Selected 2 of 3'
                        elif n==4:
                            dropdownheadercondition = 'Selected 1 of 3'

                        selecteddnp3filternames = []
                        j=0
                        for option in dropdownlist:
                            classname = option.get_attribute('class')
                            if 'ng-scope' in classname:
                                #print('dropdownheadercondition:%s' %dropdownheadercondition)
                                #print('dropdownheader2:%s' %dropdownheader)
                                if not dropdownheadercondition in dropdownheader:
                                    dnp3filterName = option.text
                                    inputElement = GetElement(option, By.TAG_NAME, 'input')
                                    inputType = inputElement.get_attribute('type')

                                    if n==0:
                                        if j>=0 and j<3:
                                            value = 'true'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                selecteddnp3filternames.append(dnp3filterName)
                                                dropdownheaderelement = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-header')
                                                dropdownheader = dropdownheaderelement.text
                                                #print('dropdownheader3:%s' %dropdownheader)
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                        else:
                                            value = 'false'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Not Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                dropdownheader = 'Selected 0 of 3'
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')

                                    elif n==1:
                                        if j>=1 and j<4:
                                            value = 'true'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                selecteddnp3filternames.append(dnp3filterName)
                                                dropdownheaderelement = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-header')
                                                dropdownheader = dropdownheaderelement.text
                                                #print('dropdownheader4:%s' %dropdownheader)
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                        else:
                                            value = 'false'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Not Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                dropdownheader = 'Selected 0 of 3'
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                    elif n==2:
                                        if j>=2 and j<5:
                                            value = 'true'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                selecteddnp3filternames.append(dnp3filterName)
                                                dropdownheaderelement = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-header')
                                                dropdownheader = dropdownheaderelement.text
                                                #print('dropdownheader5:%s' %dropdownheader)
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                        else:
                                            value = 'false'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Not Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                dropdownheader = 'Selected 0 of 3'
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                    elif n==3:
                                        if j>=2 and j<4:
                                            value = 'true'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                selecteddnp3filternames.append(dnp3filterName)
                                                dropdownheaderelement = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-header')
                                                dropdownheader = dropdownheaderelement.text
                                                #print('dropdownheader6:%s' %dropdownheader)
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                        else:
                                            value = 'false'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Not Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                dropdownheader = 'Selected 0 of 3'

                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                    elif n==4:
                                        if j>=4 and j<5:
                                            value = 'true'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                selecteddnp3filternames.append(dnp3filterName)
                                                dropdownheaderelement = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-header')
                                                dropdownheader = dropdownheaderelement.text
                                                #print('dropdownheader7:%s' %dropdownheader)
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')
                                        else:
                                            value = 'false'
                                            if 'checkbox' in inputType:
                                                SetCheckBox(inputElement, value)
                                                j=j+1
                                                printFP("Not Selecting Dnp3 Filter Name : " + dnp3filterName)
                                                dropdownheader = 'Selected 0 of 3'
                                            else:
                                                printFP('Test Fail - Do not recognize this input type')

                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                        time.sleep(5)
                        dnp3pointchartnames = GetCurrentDnp3PointChartNames()
                        printFP(dnp3pointchartnames)
                        printFP(selecteddnp3filternames)
                        if all(x not in dnp3pointchartnames for x in selecteddnp3filternames):
                            testComment = "Test Fail - Selected dnp3 points graph is not displayed in View Chart"
                            printFP(testComment)
                            ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                            time.sleep(1)
                            return Global.FAIL, testComment
                        else:
                            testComment= "Test Pass - Selected dnp3 points graphs are displayed in View Chart"
                            printFP(testComment)
                        n=n+1

                else:
                    testComment = "Test Fail - View Chart dialog is not opened when click on View Chart button"
                    printFP(testComment)
                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                    time.sleep(1)
                    return Global.FAIL, testComment

            testComment = "Test Pass - Verified Dnp3 Points View Chart graph filters successfully. All test cases are PASS"
            printFP(testComment)
            ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
            time.sleep(1)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def Dnp3PointsViewChartPhaseFilters(input_file_path):

    printFP('Verify Dnp3 Points View Chart Phase filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            viewchartbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_button'])
            time.sleep(2)
            classnameviewchart = viewchartbutton.get_attribute('class')
            if 'ng-hide' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is hidden for selected site %s . It should be disabled.' %site
                printFP(testComment)
                return Global.FAIL, testComment
            elif 'disabled' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is disabled for selected site %s' %site
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - View Chart button is not disabled for selected site %s' %site
                printFP(testComment)
                JustClick(viewchartbutton)
                time.sleep(1)
                viewchartdialog = GetElement(Global.driver, By.CLASS_NAME, 'modal-dialog')
                if viewchartdialog:
                    dnp3pointsbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_dnp3points_button'])
                    #JustClick(dnp3pointsbutton)
                    time.sleep(1)
                    parentelement = GetElement(dnp3pointsbutton, By.XPATH, '..')
                    dropdownmenu = GetElement(parentelement, By.TAG_NAME, 'ul')
                    dropdownlist = GetElements(dropdownmenu, By.TAG_NAME, 'li')
                    dropdownheader = dropdownlist[0].text
                    #print('dropdownheader1:%s' %dropdownheader)
                    dnp3pointsbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_dnp3points_button'])
                    JustClick(dnp3pointsbutton)
                    time.sleep(1)
                    dropdownheadercondition = 'Selected 3 of 3'
                    selecteddnp3filternames = []
                    j=0
                    for option in dropdownlist:
                        classname = option.get_attribute('class')
                        if 'ng-scope' in classname:
                            #print('dropdownheadercondition:%s' %dropdownheadercondition)
                            #print('dropdownheader2:%s' %dropdownheader)
                            if not dropdownheadercondition in dropdownheader:
                                dnp3filterName = option.text
                                inputElement = GetElement(option, By.TAG_NAME, 'input')
                                inputType = inputElement.get_attribute('type')
                                if j>=2 and j<5:
                                    value = 'true'
                                    if 'checkbox' in inputType:
                                        SetCheckBox(inputElement, value)
                                        j=j+1
                                        printFP("Selecting Dnp3 Filter Name : " + dnp3filterName)
                                        selecteddnp3filternames.append(dnp3filterName)
                                        dropdownheaderelement = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-header')
                                        dropdownheader = dropdownheaderelement.text
                                        #print('dropdownheader5:%s' %dropdownheader)
                                    else:
                                        printFP('Test Fail - Do not recognize this input type')
                                else:
                                    value = 'false'
                                    if 'checkbox' in inputType:
                                        SetCheckBox(inputElement, value)
                                        j=j+1
                                        printFP("Not Selecting Dnp3 Filter Name : " + dnp3filterName)
                                        dropdownheader = 'Selected 0 of 3'
                                    else:
                                        printFP('Test Fail - Do not recognize this input type')

                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                    time.sleep(5)
                    dnp3pointchartnames = GetCurrentDnp3PointChartNames()
                    printFP(dnp3pointchartnames)
                    printFP(selecteddnp3filternames)
                    if all(x not in dnp3pointchartnames for x in selecteddnp3filternames):
                        testComment = "Test Fail - Selected dnp3 points graph is not displayed in View Chart"
                        printFP(testComment)
                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                        time.sleep(1)
                        return Global.FAIL, testComment
                    else:
                        testComment= "Test Pass - Selected dnp3 points graphs are displayed in View Chart"
                        printFP(testComment)
                        phasebuttonelement = GetElement(viewchartdialog, By.TAG_NAME, 'phase-filter')
                        time.sleep(1)
                        phasefilters = GetElements(phasebuttonelement, By.TAG_NAME, 'label')
                        time.sleep(2)
                        for phasefilter in phasefilters:
                            phasefiltername = phasefilter.text
                            testphase =  phasefiltername
                            if phasefiltername in ('A','B','C'):
                                buttonclassname = phasefilter.get_attribute('class')
                                if "active" in buttonclassname:
                                    try:
                                        phasefilter.click()
                                        time.sleep(1)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                                        time.sleep(5)
                                    except:
                                        testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                        printFP(testComment)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                        time.sleep(1)
                                        return Global.FAIL, testComment
                                    for dnp3pointchartname in dnp3pointchartnames:
                                        printFP('Dnp3 Point Chart Name "'+ dnp3pointchartname +'" and "Phase '+ testphase +'" ')
                                        chart = GetElement(viewchartdialog, By.CLASS_NAME, 'chart')
                                        dnp3charts = GetElements(chart, By.TAG_NAME, 'dnp3-chart')
                                        for dnp3chart in dnp3charts:
                                            yaxis = GetElement(dnp3chart, By.CLASS_NAME, 'highcharts-yaxis-title')
                                            title = yaxis.text.strip()
                                            if title in dnp3pointchartname:
                                                filteredphasedata = Dnp3PointsPhaseDataStatus(title, testphase)
                                                if filteredphasedata:
                                                    printFP('Test Pass - "Phase '+ testphase +'" data are available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    phasedisplaystatus = GetPhaseStatusOnDnp3ViewChartGraph(title, testphase)
                                                    if not phasedisplaystatus:
                                                        testComment = 'Test Pass - "Phase '+ testphase +'" data are not displayed for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when unselect Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                    else:
                                                        testComment = 'Test Fail - "Phase '+ testphase +'" data are still displaying for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when unselect Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                                        time.sleep(1)
                                                        return Global.FAIL, testComment
                                                else:
                                                    printFP('INFO - "Phase '+ testphase +'" data are not available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    break

                                    try:
                                        phasefilter.click()
                                        time.sleep(1)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                                        time.sleep(5)
                                    except:
                                        testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                        printFP(testComment)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                        time.sleep(1)
                                        return Global.FAIL, testComment
                                    for dnp3pointchartname in dnp3pointchartnames:
                                        printFP('Dnp3 Point Chart Name "'+ dnp3pointchartname +'" and "Phase '+ testphase +'" ')
                                        chart = GetElement(viewchartdialog, By.CLASS_NAME, 'chart')
                                        dnp3charts = GetElements(chart, By.TAG_NAME, 'dnp3-chart')
                                        for dnp3chart in dnp3charts:
                                            yaxis = GetElement(dnp3chart, By.CLASS_NAME, 'highcharts-yaxis-title')
                                            title = yaxis.text.strip()
                                            if title in dnp3pointchartname:
                                                filteredphasedata = Dnp3PointsPhaseDataStatus(title, testphase)
                                                if filteredphasedata:
                                                    printFP('Test Pass - "Phase '+ testphase +'" data are available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    phasedisplaystatus = GetPhaseStatusOnDnp3ViewChartGraph(title, testphase)
                                                    if not phasedisplaystatus:
                                                        testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when select Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                                        time.sleep(1)
                                                        return Global.FAIL, testComment
                                                    else:
                                                        testComment = 'Test Pass - "Phase '+ testphase +'" data are displayed for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when select Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                else:
                                                    printFP('INFO - "Phase '+ testphase +'" data are not available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    break

                                elif not "active" in buttonclassname:

                                    try:
                                        phasefilter.click()
                                        time.sleep(1)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                                        time.sleep(5)
                                    except:
                                        testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                        printFP(testComment)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                        time.sleep(1)
                                        return Global.FAIL, testComment
                                    for dnp3pointchartname in dnp3pointchartnames:
                                        printFP('Dnp3 Point Chart Name "'+ dnp3pointchartname +'" and "Phase '+ testphase +'" ')
                                        chart = GetElement(viewchartdialog, By.CLASS_NAME, 'chart')
                                        dnp3charts = GetElements(chart, By.TAG_NAME, 'dnp3-chart')
                                        for dnp3chart in dnp3charts:
                                            yaxis = GetElement(dnp3chart, By.CLASS_NAME, 'highcharts-yaxis-title')
                                            title = yaxis.text.strip()
                                            if title in dnp3pointchartname:
                                                filteredphasedata = Dnp3PointsPhaseDataStatus(title, testphase)
                                                if filteredphasedata:
                                                    printFP('Test Pass - "Phase '+ testphase +'" data are available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    phasedisplaystatus = GetPhaseStatusOnDnp3ViewChartGraph(title, testphase)
                                                    if not phasedisplaystatus:
                                                        testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when select Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                                        time.sleep(1)
                                                        return Global.FAIL, testComment
                                                    else:
                                                        testComment = 'Test Pass - "Phase '+ testphase +'" data are displayed for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when select Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                else:
                                                    printFP('INFO - "Phase '+ testphase +'" data are not available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    break

                                    try:
                                        phasefilter.click()
                                        time.sleep(1)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                                        time.sleep(5)
                                    except:
                                        testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                        printFP(testComment)
                                        return Global.FAIL, testComment
                                    for dnp3pointchartname in dnp3pointchartnames:
                                        printFP('Dnp3 Point Chart Name "'+ dnp3pointchartname +'" and "Phase '+ testphase +'" ')
                                        chart = GetElement(viewchartdialog, By.CLASS_NAME, 'chart')
                                        dnp3charts = GetElements(chart, By.TAG_NAME, 'dnp3-chart')
                                        for dnp3chart in dnp3charts:
                                            yaxis = GetElement(dnp3chart, By.CLASS_NAME, 'highcharts-yaxis-title')
                                            title = yaxis.text.strip()
                                            if title in dnp3pointchartname:
                                                filteredphasedata = Dnp3PointsPhaseDataStatus(title, testphase)
                                                if filteredphasedata:
                                                    printFP('Test Pass - "Phase '+ testphase +'" data are available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    phasedisplaystatus = GetPhaseStatusOnDnp3ViewChartGraph(title, testphase)
                                                    if not phasedisplaystatus:
                                                        testComment = 'Test Pass - "Phase '+ testphase +'" data are not displayed for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when unselect Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                    else:
                                                        testComment = 'Test Fail - "Phase '+ testphase +'" data are still displaying for Dnp3 Point Chart Name "'+ dnp3pointchartname +'" on Dnp3 View chart when unselect Phase filter "' + testphase + '"'
                                                        printFP(testComment)
                                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                                        time.sleep(1)
                                                        return Global.FAIL, testComment
                                                else:
                                                    printFP('INFO - "Phase '+ testphase +'" data are not available for Dnp3 Point Chart Name "'+ dnp3pointchartname +'"')
                                                    break
                                else:
                                    printFP('Unable to find whether Phase "' + testphase + '" button is enabled or not')

                            else:
                                testComment = 'Test Fail - Phase filter "' + testphase + '" is not in the defined list'
                                printFP(testComment)
                                ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                time.sleep(1)
                                return Global.FAIL, testComment
                else:
                    testComment = "Test Fail - View Chart dialog is not opened when click on View Chart button"
                    printFP(testComment)
                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                    time.sleep(1)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Verified Dnp3 Points View Chart phasefilters successfully and all test cases are PASS'
            printFP(testComment)
            ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
            time.sleep(1)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def Dnp3PointsViewChartTimeRangeSelection(input_file_path):

    printFP('Verify Dnp3 Points View Chart Time Range Selection')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonDNP3()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(3)
    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Site has Dnp3 Points")
            viewchartbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_button'])
            time.sleep(2)
            classnameviewchart = viewchartbutton.get_attribute('class')
            if 'ng-hide' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is hidden for selected site %s . It should be disabled.' %site
                printFP(testComment)
                return Global.FAIL, testComment
            elif 'disabled' in classnameviewchart:
                testComment = 'Test Fail - View Chart button is disabled for selected site %s' %site
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - View Chart button is not disabled for selected site %s' %site
                printFP(testComment)
                JustClick(viewchartbutton)
                time.sleep(1)
                viewchartdialog = GetElement(Global.driver, By.CLASS_NAME, 'modal-dialog')
                if viewchartdialog:
                    dnp3pointsbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_dnp3points_button'])
                    #JustClick(dnp3pointsbutton)
                    time.sleep(1)
                    parentelement = GetElement(dnp3pointsbutton, By.XPATH, '..')
                    dropdownmenu = GetElement(parentelement, By.TAG_NAME, 'ul')
                    dropdownlist = GetElements(dropdownmenu, By.TAG_NAME, 'li')
                    dropdownheader = dropdownlist[0].text
                    #print('dropdownheader1:%s' %dropdownheader)
                    dnp3pointsbutton = GetElement(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_dnp3points_button'])
                    JustClick(dnp3pointsbutton)
                    time.sleep(1)
                    dropdownheadercondition = 'Selected 3 of 3'
                    selecteddnp3filternames = []
                    j=0
                    for option in dropdownlist:
                        classname = option.get_attribute('class')
                        if 'ng-scope' in classname:
                            #print('dropdownheadercondition:%s' %dropdownheadercondition)
                            #print('dropdownheader2:%s' %dropdownheader)
                            if not dropdownheadercondition in dropdownheader:
                                dnp3filterName = option.text
                                inputElement = GetElement(option, By.TAG_NAME, 'input')
                                inputType = inputElement.get_attribute('type')
                                if j>=2 and j<5:
                                    value = 'true'
                                    if 'checkbox' in inputType:
                                        SetCheckBox(inputElement, value)
                                        j=j+1
                                        printFP("Selecting Dnp3 Filter Name : " + dnp3filterName)
                                        selecteddnp3filternames.append(dnp3filterName)
                                        dropdownheaderelement = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-header')
                                        dropdownheader = dropdownheaderelement.text
                                        #print('dropdownheader5:%s' %dropdownheader)
                                    else:
                                        printFP('Test Fail - Do not recognize this input type')
                                else:
                                    value = 'false'
                                    if 'checkbox' in inputType:
                                        SetCheckBox(inputElement, value)
                                        j=j+1
                                        printFP("Not Selecting Dnp3 Filter Name : " + dnp3filterName)
                                        dropdownheader = 'Selected 0 of 3'
                                    else:
                                        printFP('Test Fail - Do not recognize this input type')

                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                    time.sleep(5)
                    dnp3pointchartnames = GetCurrentDnp3PointChartNames()
                    printFP(dnp3pointchartnames)
                    printFP(selecteddnp3filternames)
                    if all(x not in dnp3pointchartnames for x in selecteddnp3filternames):
                        testComment = "Test Fail - Selected dnp3 points graph is not displayed in View Chart"
                        printFP(testComment)
                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                        time.sleep(1)
                        return Global.FAIL, testComment
                    else:
                        testComment= "Test Pass - Selected dnp3 points graphs are displayed in View Chart"
                        printFP(testComment)
                        timerangeframe = GetElement(viewchartdialog, By.TAG_NAME, 'zoom-filter')
                        time.sleep(1)
                        timerangefilters = GetElements(timerangeframe, By.TAG_NAME, 'label')
                        time.sleep(1)
                        n=0
                        for timerangefilter in timerangefilters:
                            timerangefiltername = timerangefilter.text
                            testtimerange =  timerangefiltername
                            if timerangefiltername in ('1D','1W','1M', '3M', '6M', '1Y'):
                                buttonclassname = timerangefilter.get_attribute('class')
                                if "active" in buttonclassname:
                                    printFP('"Time Range '+ testtimerange +'" button is already selected by default')
                                    rangeframe = GetElement(viewchartdialog, By.TAG_NAME, 'zoom-filter')
                                    rangefilters = GetElements(rangeframe, By.TAG_NAME, 'label')
                                    m=n
                                    m=m+1
                                    try:
                                        rangefilters[m].click()
                                        time.sleep(1)
                                        rangeframe = GetElement(viewchartdialog, By.TAG_NAME, 'zoom-filter')
                                        rangefilters = GetElements(rangeframe, By.TAG_NAME, 'label')
                                        rangefilters[n].click()
                                        time.sleep(1)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                                        time.sleep(5)
                                    except:
                                        testComment = 'Test Fail - Unable to click "'+ testtimerange +'" Time Range filter'
                                        printFP(testComment)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                        time.sleep(1)
                                        return Global.FAIL, testComment
                                    for dnp3pointchartname in dnp3pointchartnames:
                                        printFP('Dnp3 Point Chart Name "'+ dnp3pointchartname +'" and "Time Range '+ testtimerange +'" ')
                                        chart = GetElement(viewchartdialog, By.CLASS_NAME, 'chart')
                                        dnp3charts = GetElements(chart, By.TAG_NAME, 'dnp3-chart')
                                        for dnp3chart in dnp3charts:
                                            yaxis = GetElement(dnp3chart, By.CLASS_NAME, 'highcharts-yaxis-title')
                                            title = yaxis.text.strip()
                                            if title in dnp3pointchartname:
                                                timerangebuttonstatus = GetDnp3ViewChartTimeRangeButtonStatus(testtimerange, viewchartdialog)
                                                if timerangebuttonstatus:
                                                    testComment = 'Test Pass - "Selected Time Range '+ testtimerange +'" button got activated when select Time Range filter "' + testtimerange + '"'
                                                    printFP(testComment)
                                                else:
                                                    testComment = 'Test Fail - "Time Range '+ testtimerange +'" button is still not activated when select Time Range filter "' + testtimerange + '"'
                                                    printFP(testComment)
                                                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                                    time.sleep(1)
                                                    return Global.FAIL, testComment

                                elif not "active" in buttonclassname:
                                    try:
                                        rangeframe = GetElement(viewchartdialog, By.TAG_NAME, 'zoom-filter')
                                        rangefilters = GetElements(rangeframe, By.TAG_NAME, 'label')
                                        rangefilters[n].click()
                                        time.sleep(1)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_drawgraph_button'])
                                        time.sleep(5)
                                    except:
                                        testComment = 'Test Fail - Unable to click "'+ testtimerange +'" Time Range filter'
                                        printFP(testComment)
                                        ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                        time.sleep(1)
                                        return Global.FAIL, testComment
                                    for dnp3pointchartname in dnp3pointchartnames:
                                        printFP('Dnp3 Point Chart Name "'+ dnp3pointchartname +'" and "Time Range '+ testtimerange +'" ')
                                        chart = GetElement(viewchartdialog, By.CLASS_NAME, 'chart')
                                        dnp3charts = GetElements(chart, By.TAG_NAME, 'dnp3-chart')
                                        for dnp3chart in dnp3charts:
                                            yaxis = GetElement(dnp3chart, By.CLASS_NAME, 'highcharts-yaxis-title')
                                            title = yaxis.text.strip()
                                            if title in dnp3pointchartname:
                                                timerangebuttonstatus = GetDnp3ViewChartTimeRangeButtonStatus(testtimerange, viewchartdialog)
                                                if timerangebuttonstatus:
                                                    testComment = 'Test Pass - "Selected Time Range '+ testtimerange +'" button got activated when select Time Range filter "' + testtimerange + '"'
                                                    printFP(testComment)
                                                else:
                                                    testComment = 'Test Fail - "Time Range '+ testtimerange +'" button is still not activated when select Time Range filter "' + testtimerange + '"'
                                                    printFP(testComment)
                                                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                                    time.sleep(1)
                                                    return Global.FAIL, testComment
                                else:
                                    printFP('Unable to find whether Time Range "' + testtimerange + '" button is enabled or not')

                            else:
                                testComment = 'Test Fail - Time Range "' + testtimerange + '" is not in the defined list'
                                printFP(testComment)
                                ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                                time.sleep(1)
                                return Global.FAIL, testComment
                            n=n+1
                else:
                    testComment = "Test Fail - View Chart dialog is not opened when click on View Chart button"
                    printFP(testComment)
                    ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
                    time.sleep(1)
                    return Global.FAIL, testComment


            testComment = 'Test Pass - Verified Dnp3 Points Time Range filters successfully and all test cases are PASS'
            printFP(testComment)
            ClickButton(Global.driver, By.XPATH, xpaths['dnp3points_viewchart_close_button'])
            time.sleep(1)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Given site doesn't have dnp3 points. Please point to a site which has dnp3 points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def FaultEventsTableEmptyData(input_file_path):

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getregion = GetRegionFromTop(region)

    time.sleep(2)

    if getregion:
        nodataavailableFeeder = NoDataAvailable('line-monitoring')
        if nodataavailableFeeder == "No Data Available":
            testComment = 'Test Pass - Found "No Data Available" Text for Region'
            printFP(testComment)
            getsubstation = GetSubstationFromTop(region, substation)
            if getsubstation:
                nodataavailableSite = NoDataAvailable('line-monitoring')
                if nodataavailableSite == "No Data Available":
                    testComment = 'Test Pass - Found "No Data Available" Text for Substation'
                    printFP(testComment)
                    getfeeder = GetFeederFromTop(region, substation, feeder)
                    if getfeeder:
                        nodataavailableSite = NoDataAvailable('line-monitoring')
                        if nodataavailableSite == "No Data Available":
                            testComment = 'Test Pass - Found "No Data Available" Text for Feeder'
                            printFP(testComment)
                            getsite = GetSiteFromTop(region, substation, feeder, site)
                            if getsite:
                                nodataavailableSite = NoDataAvailable('line-monitoring')
                                if nodataavailableSite == "No Data Available":
                                    testComment = 'Test Pass - Found "No Data Available" Text for Region, Substation, Feeder and Site'
                                    printFP(testComment)
                                    return Global.PASS, testComment
                                else:
                                    testComment = 'Test Fail - Not Found "No Data Available" Text for Site'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                            else:
                                testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'Test Fail - Not Found "No Data Available" Text for Feeder'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    else:
                        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    testComment = 'Test Fail - Not Found "No Data Available" Text for Substation'
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Fail - Unable to locate Given Substation "%s"' %substation
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = 'Test Fail - Not Found "No Data Available" Text for Region'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def GetFaultEventsColumnOrder():

    columnnamesorder = {}

    html = Global.driver.page_source

    OrderElements = soup(html, "lxml")

    # find lineMonitoring Page view
    linemonitoringpage = OrderElements.find('div', class_=re.compile('line-monitoring'))

    if linemonitoringpage.find('table'):
        tabledata = linemonitoringpage.find('table')
        header = tabledata.find('thead')
        columnnames = header.find_all(class_=re.compile('ng-binding'))
        n=1
        for columnname in columnnames:
            name = columnname.text.strip()
            columnnamesorder[name] = n
            n = n+1
    return columnnamesorder


def FilterFromFaultEventsData(columnname):

    columnorder = GetFaultEventsColumnOrder()

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find lineMonitoring Page view
    linemonitoringpage = FilterElements.find('div', class_=re.compile('line-monitoring'))

    if linemonitoringpage.find('table'):
        tabledata = linemonitoringpage.find('table')
        # Get all rows
        rows = tabledata.find_all('tr', class_=re.compile('row'))
        for row in rows:
            n=1
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        columnnamevalueslist.append(value)
                    n = n+1

    print columnnamevalueslist
    return columnnamevalueslist

def FaultEventsExportButton(input_file_path, level=None):

    printFP('Verifying Fault Event %s Export button' %level)

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    if 'region' in level:
        getregion = GetRegionFromTop(region)
        getlevel = getregion

    elif 'substation' in level:
        getsubstation = GetSubstationFromTop(region, substation)
        getlevel = getsubstation
    elif 'feeder' in level:
        getfeeder= GetFeederFromTop(region, substation, feeder)
        getlevel = getfeeder
    elif 'site' in level:
        getsite = GetSiteFromTop(region, substation, feeder, site)
        getlevel = getsite

    if 'site' in level:
        xpathnameexcel = 'faultevents_site_export_excel_button'
        xpathnamecsv = 'faultevents_site_export_csv_button'
    else:
        xpathnameexcel = 'faultevents_export_excel_button'
        xpathnamecsv = 'faultevents_export_csv_button'

    time.sleep(5)

    if getlevel:
        #Get export button elements
        exportbuttonelements = GetElements(Global.driver, By.CLASS_NAME, 'dropdown-toggle')

        # find export toggle dorpdown button
        for exportbuttonelement in exportbuttonelements:
            exportbuttonelementname = exportbuttonelement.text
            if 'Export' in exportbuttonelementname:
                try:
                    isdisabled = exportbuttonelement.get_attribute('disabled')
                except Exception as e:
                    print e.message

                if isdisabled is None:
                    try:
                        time.sleep(2)
                        exportbuttonelement.click()
                    except Exception as e:
                        printFP(e.message)
                        testComment = 'Test Fail - Unable to click Export Button'
                        printFP(testComment)
                        return Global.FAIL, testComment

                    exportdropdownframe = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-menu-form')
                    exportdropdownlists = GetElements(exportdropdownframe, By.TAG_NAME, 'li')
                    excelStatus = False
                    for exportdropdownlist in exportdropdownlists:
                        if not excelStatus:
                            formattype = exportdropdownlist.text
                            printFP('formattype %s' %formattype)

                            if 'EXCEL' in formattype:
                                try:
                                    ClickButton(Global.driver, By.XPATH, xpaths[xpathnameexcel])
                                    time.sleep(5)

                                    try:
                                        Global.driver.switch_to_window(Global.driver.window_handles[-1])
                                        cancelbutton = Global.driver.find_element_by_xpath(u'//input[@value="Cancel"]')
                                        cancelbutton.click()
                                        time.sleep(1)
                                        Global.driver.switch_to_default_content()
                                    except Exception as e:
                                        printFP(e.message)

                                    testComment = 'Test Pass - Able to export faultevents %s tabluar data in excel format' %level
                                    printFP(testComment)
                                    excelStatus = True

                                except:
                                    testComment = 'Test Fail - Unable to click "Excel" export option in faultevents screen'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Fail - Export Button is not enabled. Please point to a %s which has faultevents' %level
                    printFP(testComment)
                    return Global.FAIL, testComment

                if isdisabled is None:
                    try:
                        time.sleep(2)
                        exportbuttonelement.click()
                    except Exception as e:
                        printFP(e.message)
                        testComment = 'Test Fail - Unable to click Export Button'
                        printFP(testComment)
                        return Global.FAIL, testComment

                    exportdropdownframe = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-menu-form')
                    exportdropdownlists = GetElements(exportdropdownframe, By.TAG_NAME, 'li')
                    csvStatus = False
                    for exportdropdownlist in exportdropdownlists:
                        if not csvStatus:
                            formattype = exportdropdownlist.text
                            printFP('formattype %s' %formattype)

                            if 'CSV' in formattype:
                                try:
                                    ClickButton(Global.driver, By.XPATH, xpaths[xpathnamecsv])
                                    time.sleep(5)

                                    try:
                                        Global.driver.switch_to_window(Global.driver.window_handles[-1])
                                        title = Global.driver.title
                                    except Exception as e:
                                        printFP(e.message)

                                    testComment = 'Test Pass - Able to export faultevents %s tabluar data in CSV format' %level
                                    printFP(testComment)
                                    csvStatus = True

                                except:
                                    testComment = 'Test Fail - Unable to click "CSV" export option in faultevents region screen'
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                    time.sleep(1)
                    testComment = 'Test Pass - Able to export faultevents %s tabluar data in both Excel and CSV formats successfully' %level
                    printFP(testComment)
                    return Global.PASS, testComment

                else:
                    testComment = 'Test Fail - Export Button is not enabled. Please point to a %s which has faultevents' %level
                    printFP(testComment)
                    return Global.FAIL, testComment

        testComment = "Test Fail - Export Button element is not found"
        printFP(testComment)
        return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given "%s"' %level
        printFP(testComment)
        return Global.FAIL, testComment



def FaultEventsCheckSubstationsWithoutEventsInRegionTable(input_file_path):

    printFP('Find which substation has no fault events and Check in region table')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getregion = GetRegionFromTop(region)
    subwithoutfaultevents = []

    time.sleep(5)

    if getregion:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Region has faultevents")
            getregionelement = GetRegion(region)
            allSubs = getregionelement.find_elements_by_class_name('SUBSTATION-name')
            for sub in allSubs:
                substationname = sub.text
                printFP('Found %s' % substationname)
                actions = ActionChains(Global.driver)
                actions.move_to_element(sub).click(sub).perform()
                time.sleep(3)
                UnCheckAllEventStates()
                UnCheckAllEventTypes()
                time.sleep(3)
                nodataavailable = NoDataAvailable('line-monitoring')
                if nodataavailable == "No Data Available":
                    subwithoutfaultevents.append(substationname)
            printFP(subwithoutfaultevents)
            if not subwithoutfaultevents:
                testComment = 'Test Fail - Please point to a Region which has at least one substation without faultevents'
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                getregion = GetRegionFromTop(region)
                subtationnames = FaultEventsRegionTableFilteredAllData('line-monitoring', 'Substation Name')
                if any(str(x) in subtationnames for x in subwithoutfaultevents):
                    testComment = 'Test Fail - substation with no faultevents present in region table'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - substation with no faultevents are not displayed in region table'
                    printFP(testComment)
                    return Global.PASS, testComment
        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a Region which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Region "%s"' %region
        printFP(testComment)
        return Global.FAIL, testComment


def FaultEventsCheckSubstationsWithEventsInRegionTable(input_file_path):

    printFP('Find which substation has fault events and Check in region table')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getregion = GetRegionFromTop(region)
    subwithfaultevents = []

    time.sleep(5)

    if getregion:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Region has faultevents")
            getregionelement = GetRegion(region)
            allSubs = getregionelement.find_elements_by_class_name('SUBSTATION-name')
            for sub in allSubs:
                substationname = sub.text
                printFP('Found %s' % substationname)
                actions = ActionChains(Global.driver)
                actions.move_to_element(sub).click(sub).perform()
                time.sleep(3)
                UnCheckAllEventStates()
                UnCheckAllEventTypes()
                time.sleep(3)
                nodataavailable = NoDataAvailable('line-monitoring')
                if not nodataavailable == "No Data Available":
                    subwithfaultevents.append(substationname)
            printFP(subwithfaultevents)
            if not subwithfaultevents:
                testComment = 'Test Fail - Please point to a Region which has at least one substation with faultevents'
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                getregion = GetRegionFromTop(region)
                subtationnames = FaultEventsRegionTableFilteredAllData('line-monitoring', 'Substation Name')
                if all(str(x) not in subtationnames for x in subwithfaultevents):
                    testComment = 'Test Fail - substation with faultevents is not present in region table'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - substation with faultevents are displayed in region table'
                    printFP(testComment)
                    return Global.PASS, testComment
        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a Region which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Region "%s"' %region
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsCheckSubEventTypesCountInRegionTable(input_file_path):

    printFP('Find which substation has fault events and check the count in region table')

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getregion = GetRegionFromTop(region)
    subwithfaultevents = []

    time.sleep(5)

    if getregion:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Region has faultevents")
            substationnames = FaultEventsRegionTableFilteredAllData('line-monitoring', 'Substation Name')
            for substationname in substationnames:
                faulteventtypes, faluteventslist, substation = FaultEventsGetSubstationFaultEventsCountInRegionTable(pagename, substationname)
                getsubstation = GetSubstationFromTop(region, substationname)
                if getsubstation:
                    time.sleep(5)
                    UnCheckAllEventStates()
                    UnCheckAllEventTypes()
                    for faulteventtype in faulteventtypes:
                        value = faluteventslist[faulteventtype]
                        print value
                        faulteventtype = faulteventtype.replace('Interruptions','Interruption').replace('Faults','Fault')
                        if int(value) > 0:
                            filtereddata, totaleventcount = FaultEventsTableFilteredSpecificData(pagename, 'Event Type', faulteventtype)
                            if int(totaleventcount) == int(value):
                                testComment = 'Test Pass - fault event count of region table is matched with substation table for substaion:  %s and event type: %s ' %(substationname, faulteventtype)
                                printFP(testComment)
                            else:
                                testComment = 'Test Fail - fault event count of region table is not matched with substation table for substaion:  %s and event type: %s ' %(substationname, faulteventtype)
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'INFO- There is no "%s" fault events for substation: %s' %(faulteventtype, substationname)
                            printFP(testComment)
                else:
                    testComment = 'Test Fail - Unable to locate filtered substation "%s"' %substationname
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = "Test Pass -  Verified all Fault Events count of region and substaion table successfully and all test cases are PASS"
            printFP(testComment)
            return Global.PASS, testComment

def FaultEventsCheckFeederEventsCountInSubstationTable(input_file_path):

    printFP('Find which feeder has fault events and Check in substation table')

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(5)

    if getfeeder:
        UnCheckAllEventStates()
        UnCheckAllEventTypes()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given feeder has faultevents")
            nodataavailable = NoDataAvailable(pagename)
            if not nodataavailable == "No Data Available":
                faulteventsvalueslist , feederfaulteventscount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
                if not feederfaulteventscount:
                    testComment = 'Test Fail - Please point to a Feeder which has at least one faultevents'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    getsubstation = GetSubstationFromTop(region, substation)
                    UnCheckAllEventStates()
                    UnCheckAllEventTypes()
                    feederfaulteventlist, feederfaulteventscountinsubstation= FaultEventsGetFeederFaultEventsCountInSubstationTable(pagename, 'Feeder', feeder)
                    if int(feederfaulteventscountinsubstation) == int(feederfaulteventscount):
                        testComment = 'Test Pass - fault event count of feeder table is matched with substation table for feeder:  %s ' %feeder
                        printFP(testComment)
                        return Global.PASS, testComment
                    else:
                        testComment = 'Test Fail - fault event count of feeder table is not matched with substation table for feeder:  %s ' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
            else:
                testComment = 'Test Fail- There is no fault events for substation: %s' %substation
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a Region which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsCheckFeederEventTypesCountInSubstationTable(input_file_path):

    printFP('Find which feeder has fault events and Check each type count in substation table')

    feedereventtypescountinsubtablelist = {}
    feedereventtypescountlist = {}
    faulteventtypes = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(5)

    if getfeeder:
        UnCheckAllEventStates()
        UnCheckAllEventTypes()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given feeder has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event Type: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event Type "%s" is selected successfully' %filtername)
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event Type "%s" is already selected by default' %filtername)

                        faulteventsvalueslist , feederfaulteventscount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
                        feedereventtypescountlist[filtername] = feederfaulteventscount
                        faulteventtypes.append(filtername)
                        UnselectEventType(filtername)
                    n=n+1

            getsubstation = GetSubstationFromTop(region, substation)
            time.sleep(2)
            UnCheckAllEventStates()
            UnCheckAllEventTypes()
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                m=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[m]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event Type: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event Type "%s" is selected successfully' %filtername)
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event Type "%s" is already selected by default' %filtername)

                        feederfaulteventlist , feederfaulteventscountinsubstation = FaultEventsGetFeederFaultEventsCountInSubstationTable(pagename, 'Feeder', feeder)
                        feedereventtypescountinsubtablelist[filtername] = feederfaulteventscountinsubstation
                        UnselectEventType(filtername)
                    m = m+1

            printFP(feedereventtypescountlist)
            printFP(feedereventtypescountinsubtablelist)
            printFP(faulteventtypes)

            if all(feedereventtypescountlist[faulteventtype] == feedereventtypescountinsubtablelist[faulteventtype] for faulteventtype in faulteventtypes):
                testComment = 'Test Pass - each fault event type count of feeder table is matched with substation table for feeder:  %s ' %feeder
                printFP(testComment)
                return Global.PASS, testComment
            else:
                testComment = 'Test Fail - fault event type count of feeder table is not matched with substation table for feeder:  %s ' %feeder
                printFP(testComment)
                return Global.FAIL, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a Region which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSubCheckEventType(input_file_path):

    printFP('Select all Event Type and validate for substation')

    faulteventtypes = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsub = GetSubstationFromTop(region, substation)

    time.sleep(5)

    if getsub:
        UnCheckAllEventStates()
        UnCheckAllEventTypes()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given substation has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event Type: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event Type "%s" is selected successfully' %filtername)
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event Type "%s" is already selected by default' %filtername)

                        subeventtypefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event Type')
                        faulteventtypes.append(filtername)
                        #printFP(subeventtypefilteredvalueslist)
                        printFP(faulteventtypes)
                        if subeventtypefilteredvalueslist:
                            if any(x != filtername for x in subeventtypefilteredvalueslist):
                                testComment = 'Test Fail - Other event types are listed in the filtered data when selected event type "%s" for substation "%s"' %(filtername,substation)
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Only selected event types are listed in the filtered data when selected event type "%s" for substation "%s"' %(filtername,substation)
                                printFP(testComment)
                        else:
                            testComment = 'INFO - There is no fault events with "%s" event type in the table so test is not executed for this event type for substation "%s"' %(filtername,substation)
                            printFP(testComment)
                        UnselectEventType(filtername)
                    n=n+1


            testComment = 'Test Pass - All fault event types are selected one by one and validated in filtered data table for substation:  %s ' %substation
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a substation which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given substation "%s"' %substation
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSubCheckEventState(input_file_path):

    printFP('Select all Event State and validate for substation')

    faulteventstate = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsub = GetSubstationFromTop(region, substation)

    time.sleep(5)

    if getsub:
        UnCheckAllEventStates()
        UnCheckAllEventTypes()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given substation has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event State drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event State drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event State: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event State "%s" is selected successfully' %filtername)
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event State "%s" is already selected by default' %filtername)

                        subeventstatefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event State')
                        faulteventstate.append(filtername)
                        #printFP(subeventstatefilteredvalueslist)
                        printFP(faulteventstate)
                        if subeventstatefilteredvalueslist:
                            if any(x != filtername for x in subeventstatefilteredvalueslist):
                                testComment = 'Test Fail - Other event state are listed in the filtered data when selected event state "%s" for substation "%s"' %(filtername,substation)
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Only selected event state are listed in the filtered data when selected event state "%s" for substation "%s"' %(filtername,substation)
                                printFP(testComment)
                        else:
                            testComment = 'INFO - There is no fault events with "%s" event state in the table so test is not executed for this event state for substation "%s"' %(filtername,substation)
                            printFP(testComment)
                        UnselectEventState(filtername)
                    n=n+1

            testComment = 'Test Pass - All fault event states are selected one by one and validated in filtered data table for substation:  %s ' %substation
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a substation which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given substation "%s"' %substation
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSubUnCheckAll(input_file_path):

    printFP('Select Event Type/Event State UncheckAll and validate')

    faulteventstate = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsub = GetSubstationFromTop(region, substation)

    time.sleep(5)

    if getsub:
        SelectAllEventTypes()
        SelectAllEventStates()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given substation has faultevents")
            UnselectEventType('Fault Without Interruption')
            UnselectEventState('Cleared')
            subeventtypefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event Type')
            subeventstatefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event State')
            #printFP(subeventtypefilteredvalueslist)
            #printFP(subeventstatefilteredvalueslist)
            if subeventtypefilteredvalueslist:
                if any(x == 'Fault Without Interruption' for x in subeventtypefilteredvalueslist):
                    testComment = 'Test Fail - Unselected event type is listed in the filtered data when unselected event type "Fault Without Interruption" for substation "%s"' %substation
                    printFP(testComment)
                    return Global.FAIL, testComment
            elif subeventtypefilteredvalueslist:
                if any(x == 'Cleared' for x in subeventstatefilteredvalueslist):
                    testComment = 'Test Fail - Unselected event state is listed in the filtered data when unselected event state "Cleared" for substation "%s"' %substation
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Unselected event type and state are not listed in the filtered data when unselected event type "Fault Without Interruption" and event state "Active" for substation "%s"' %substation
                printFP(testComment)
                UnCheckAllEventStates()
                UnCheckAllEventTypes()
                subeventtypefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event Type')
                subeventstatefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event State')
                #printFP(subeventtypefilteredvalueslist)
                #printFP(subeventstatefilteredvalueslist)
                if subeventtypefilteredvalueslist:
                    if any(x == 'Fault Without Interruption' for x in subeventtypefilteredvalueslist):
                        testComment = 'Test Pass - Unselected event type "Fault Without Interruption" is listed in the filtered data when selected "Uncheck All" of event type for substation "%s"' %substation
                        printFP(testComment)
                        if subeventstatefilteredvalueslist:
                            if any(x == 'Cleared' for x in subeventstatefilteredvalueslist):
                                testComment = 'Test Pass - Unselected event state "Cleared" is listed in the filtered data when selected "Uncheck All" of event state for substation "%s"' %substation
                                printFP(testComment)
                            else:
                                testComment = 'Test Fail - Unselected event state "Cleared" is not listed in the filtered data when selected "Uncheck All" for substation "%s"' %substation
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'Test Fail - Please point a substation which has all types and states of fault events'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    else:
                        testComment = 'Test Fail -Unselected event type "Fault Without Interruption" is not listed in the filtered data when selected "Uncheck All" for substation "%s"' %substation
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    testComment = 'Test Fail - Please point a substation which has all types and states of fault events'
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Unselected event type and state are listed in the filtered data when selected "Uncheck All" of both event type and event state for substation "%s"' %substation
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a substation which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given substation "%s"' %substation
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSubGroupTableEventCountValidation(input_file_path):

    printFP('Validating substation group table Total Event Count')

    pagename = 'line-monitoring'

    propertyname = 'Total Event Count'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsub = GetSubstationFromTop(region, substation)

    time.sleep(5)

    if getsub:
        UnCheckAllEventTypes()
        UnCheckAllEventStates()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given substation has faultevents")
            sustained = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', propertyname)
            momentary = FaultEventsGroupTableFilteredData(pagename, 'MOMENTARY', propertyname)
            active = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', propertyname)

            SelectEventState('Active')
            activevalueslist , subactivecount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
            UnselectEventState('Active')

            SelectEventType('Sustained Interruption')
            sustainedvalueslist , subsustainedcount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
            UnselectEventType('Sustained Interruption')

            SelectEventType('Momentary Interruption')
            momentaryvalueslist , submomentarycount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
            UnselectEventType('Momentary Interruption')

            if not int(active[0]) == int(subactivecount):
                testComment = 'Test Fail - Group Table ACTIVE total count is not matched with total no. of active fault events count for substation "%s" ' %substation
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Group Table ACTIVE total count is matched with total no. of active fault events count for substation "%s" ' %substation
                printFP(testComment)
                if int(active[0]) == 0:
                    if activevalueslist:
                        testComment = 'Test Fail - Group Table ACTIVE total count is "0" but active fault events list is not empty for substation "%s" ' %substation
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table ACTIVE total count is "0" and active fault events list is empty for substation "%s" ' %substation
                        printFP(testComment)


            if not int(sustained[0]) == int(subsustainedcount):
                testComment = 'Test Fail - Group Table SUSTAINED total count is not matched with total no. of sustained fault events count for substation "%s" ' %substation
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Group Table SUSTAINED total count is matched with total no. of sustained fault events count for substation "%s" ' %substation
                printFP(testComment)
                if int(sustained[0]) == 0:
                    if sustainedvalueslist:
                        testComment = 'Test Fail - Group Table SUSTAINED total count is "0" but sustained fault events list is not empty for substation "%s" ' %substation
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table SUSTAINED total count is "0" and sustained fault events list is empty for substation "%s" ' %substation
                        printFP(testComment)

            if not int(momentary[0]) == int(submomentarycount):
                testComment = 'Test Fail - Group Table MOMENTARY total count is not matched with total no. of momentary fault events count for substation "%s" ' %substation
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Group Table MOMENTARY total count is matched with total no. of momentary fault events count for substation "%s" ' %substation
                printFP(testComment)
                if int(momentary[0]) == 0:
                    if momentaryvalueslist:
                        testComment = 'Test Fail - Group Table MOMENTARY total count is "0" but momentary fault events list is not empty for substation "%s" ' %substation
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table MOMENTARY total count is "0" and momentary fault events list is empty for substation "%s" ' %substation
                        printFP(testComment)

            testComment = 'Test Pass - Validated substation group table Toal Event Count sucessfully for substation "%s"' %substation
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a substation which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given substation "%s"' %substation
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSubGroupTableDurationValidation(input_file_path):

    printFP('Validating substation group table Total Duration')

    pagename = 'line-monitoring'

    propertyname = 'Total Interruption Duration'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsub = GetSubstationFromTop(region, substation)

    time.sleep(5)

    if getsub:
        UnCheckAllEventTypes()
        UnCheckAllEventStates()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given substation has faultevents")

            sustainedcount = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', 'Total Event Count')
            momentarycount = FaultEventsGroupTableFilteredData(pagename, 'MOMENTARY', 'Total Event Count')
            activecount = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', 'Total Event Count')

            sustained = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', propertyname)
            momentary = FaultEventsGroupTableFilteredData(pagename, 'MOMENTARY', propertyname)
            active = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', propertyname)

            SelectEventState('Active')
            activevalueslist , subactivetotalduration = FaultEventsGetFaultEventsTotalDuration(pagename)
            UnselectEventState('Active')

            SelectEventType('Sustained Interruption')
            sustainedvalueslist , subsustainedtotalduration = FaultEventsGetFaultEventsTotalDuration(pagename)
            UnselectEventType('Sustained Interruption')

            SelectEventType('Momentary Interruption')
            momentaryvalueslist , submomentarytotalduration = FaultEventsGetFaultEventsTotalDuration(pagename)
            UnselectEventType('Momentary Interruption')

            if int(activecount[0]) == 0:
                if not str(active[0]) == 'N/A' and activevalueslist:
                    testComment = 'Test Fail - Group Table ACTIVE total count is "0" but Total duration is not having "N/A" or active fault events list is not empty for substation "%s" ' %substation
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table ACTIVE total count is "0" and Total duration is having "N/A" and active fault events list is empty for substation "%s" ' %substation
                    printFP(testComment)
            else:
                if subactivetotalduration == 0:
                    subactivetotalduration = 'N/A'
                    if not str(active[0]) == str(subactivetotalduration):
                        testComment = 'Test Fail - Group Table ACTIVE total duration is not matched with total duration of active fault events for substation "%s" ' %substation
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table ACTIVE total duration is matched with total duration of active fault events for substation "%s" ' %substation
                        printFP(testComment)

            if str(subsustainedtotalduration) == '0':
                if momentaryvalueslist:
                    testComment = 'Test Fail - Group Table SUSTAINED total duration is "0" but sustained fault events list is not empty for substation "%s" ' %substation
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table SUSTAINED total duration is "0" and sustained fault events list is empty for substation "%s" ' %substation
                    printFP(testComment)
            else:
                if not str(sustained[0]) == str(subsustainedtotalduration):
                    testComment = 'Test Fail - Group Table SUSTAINED total duration is not matched with total duration of sustained fault events for substation "%s" ' %substation
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table SUSTAINED total duration is matched with total duration of sustained fault events  for substation "%s" ' %substation
                    printFP(testComment)

            if str(submomentarytotalduration) == '0':
                if momentaryvalueslist:
                    testComment = 'Test Fail - Group Table MOMENTARY total duration is "0" but momentary fault events list is not empty for substation "%s" ' %substation
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table MOMENTARY total duration is "0" and momentary fault events list is empty for substation "%s" ' %substation
                    printFP(testComment)
            else:
                if not str(momentary[0]) == str(submomentarytotalduration):
                    testComment = 'Test Fail - Group Table MOMENTARY total duration is not matched with total duration of momentary fault events for substation "%s" ' %substation
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table MOMENTARY total duration is matched with total duration of momentary fault events  for substation "%s" ' %substation
                    printFP(testComment)


            testComment = 'Test Pass - Validated substation group table Toal Duration sucessfully for substation "%s"' %substation
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a substation which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given substation "%s"' %substation
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsFeederCheckEventType(input_file_path):

    printFP('Select all Event Type and validate for feeder')

    faulteventtypes = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(5)

    if getfeeder:
        UnCheckAllEventStates()
        UnCheckAllEventTypes()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given feeder has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event Type: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event Type "%s" is selected successfully' %filtername)
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event Type "%s" is already selected by default' %filtername)

                        feedereventtypefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event Type')
                        faulteventtypes.append(filtername)
                        #printFP(feedereventtypefilteredvalueslist)
                        printFP(faulteventtypes)
                        if feedereventtypefilteredvalueslist:
                            if any(x != filtername for x in feedereventtypefilteredvalueslist):
                                testComment = 'Test Fail - Other event types are listed in the filtered data when selected event type "%s" for feeder "%s"' %(filtername,feeder)
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Only selected event types are listed in the filtered data when selected event type "%s" for feeder "%s"' %(filtername,feeder)
                                printFP(testComment)
                        else:
                            testComment = 'INFO - There is no fault events with "%s" event type in the table so test is not executed for this event type for feeder "%s"' %(filtername,feeder)
                            printFP(testComment)
                        UnselectEventType(filtername)
                    n=n+1


            testComment = 'Test Pass - All fault event types are selected one by one and validated in filtered data table for feeder:  %s ' %feeder
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a feeder which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsFeederCheckEventState(input_file_path):

    printFP('Select all Event State and validate for feeder')

    faulteventstate = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region,substation, feeder)

    time.sleep(5)

    if getfeeder:
        UnCheckAllEventStates()
        UnCheckAllEventTypes()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given feeder has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event State drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event State drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event State: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event State "%s" is selected successfully' %filtername)
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event State "%s" is already selected by default' %filtername)

                        feedereventstatefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event State')
                        faulteventstate.append(filtername)
                        #printFP(feedereventstatefilteredvalueslist)
                        printFP(faulteventstate)
                        if feedereventstatefilteredvalueslist:
                            if any(x != filtername for x in feedereventstatefilteredvalueslist):
                                testComment = 'Test Fail - Other event state are listed in the filtered data when selected event state "%s" for feeder "%s"' %(filtername,feeder)
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Only selected event state are listed in the filtered data when selected event state "%s" for feeder "%s"' %(filtername,feeder)
                                printFP(testComment)
                        else:
                            testComment = 'INFO - There is no fault events with "%s" event state in the table so test is not executed for this event state for feeder "%s"' %(filtername,feeder)
                            printFP(testComment)
                        UnselectEventState(filtername)
                    n=n+1

            testComment = 'Test Pass - All fault event states are selected one by one and validated in filtered data table for feeder:  %s ' %feeder
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a feeder which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsFeederUnCheckAll(input_file_path):

    printFP('Select Event Type/Event State UncheckAll and validate')

    faulteventstate = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region,substation, feeder)

    time.sleep(5)

    if getfeeder:
        SelectAllEventTypes()
        SelectAllEventStates()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given feeder has faultevents")
            UnselectEventType('Fault Without Interruption')
            UnselectEventState('Cleared')
            feedereventtypefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event Type')
            feedereventstatefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event State')
            #printFP(feedereventtypefilteredvalueslist)
            #printFP(feedereventstatefilteredvalueslist)
            if feedereventtypefilteredvalueslist:
                if any(x == 'Fault Without Interruption' for x in feedereventtypefilteredvalueslist):
                    testComment = 'Test Fail - Unselected event type is listed in the filtered data when unselected event type "Fault Without Interruption" for feeder "%s"' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
            elif feedereventtypefilteredvalueslist:
                if any(x == 'Cleared' for x in feedereventstatefilteredvalueslist):
                    testComment = 'Test Fail - Unselected event state is listed in the filtered data when unselected event state "Cleared" for feeder "%s"' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Unselected event type and state are not listed in the filtered data when unselected event type "Fault Without Interruption" and event state "Active" for feeder "%s"' %feeder
                printFP(testComment)
                UnCheckAllEventStates()
                UnCheckAllEventTypes()
                feedereventtypefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event Type')
                feedereventstatefilteredvalueslist = FaultEventsTableFilteredAllData(pagename, 'Event State')
                #printFP(feedereventtypefilteredvalueslist)
                #printFP(feedereventstatefilteredvalueslist)
                if feedereventtypefilteredvalueslist:
                    if any(x == 'Fault Without Interruption' for x in feedereventtypefilteredvalueslist):
                        testComment = 'Test Pass - Unselected event type "Fault Without Interruption" is listed in the filtered data when selected "Uncheck All" of event type for feeder "%s"' %feeder
                        printFP(testComment)
                        if feedereventstatefilteredvalueslist:
                            if any(x == 'Cleared' for x in feedereventstatefilteredvalueslist):
                                testComment = 'Test Pass - Unselected event state "Cleared" is listed in the filtered data when selected "Uncheck All" of event state for feeder "%s"' %feeder
                                printFP(testComment)
                            else:
                                testComment = 'Test Fail - Unselected event state "Cleared" is not listed in the filtered data when selected "Uncheck All" for feeder "%s"' %feeder
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'Test Fail - Please point a feeder which has all types and states of fault events'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    else:
                        testComment = 'Test Fail -Unselected event type "Fault Without Interruption" is not listed in the filtered data when selected "Uncheck All" for feeder "%s"' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    testComment = 'Test Fail - Please point a feeder which has all types and states of fault events'
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Unselected event type and state are listed in the filtered data when selected "Uncheck All" of both event type and event state for feeder "%s"' %feeder
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a feeder which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsFeederGroupTableEventCountValidation(input_file_path):

    printFP('Validating feeder group table Total Event Count')

    pagename = 'line-monitoring'

    propertyname = 'Total Event Count'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(5)

    if getfeeder:
        UnCheckAllEventTypes()
        UnCheckAllEventStates()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given feeder has faultevents")
            sustained = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', propertyname)
            momentary = FaultEventsGroupTableFilteredData(pagename, 'MOMENTARY', propertyname)
            active = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', propertyname)

            SelectEventState('Active')
            activevalueslist , feederactivecount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
            UnselectEventState('Active')

            SelectEventType('Sustained Interruption')
            sustainedvalueslist , feedersustainedcount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
            UnselectEventType('Sustained Interruption')

            SelectEventType('Momentary Interruption')
            momentaryvalueslist , feedermomentarycount = FaultEventsGetFaultEventsCount(pagename, 'Event Type')
            UnselectEventType('Momentary Interruption')

            if not int(active[0]) == int(feederactivecount):
                testComment = 'Test Fail - Group Table ACTIVE total count is not matched with total no. of active fault events count for feeder "%s" ' %feeder
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Group Table ACTIVE total count is matched with total no. of active fault events count for feeder "%s" ' %feeder
                printFP(testComment)
                if int(active[0]) == 0:
                    if activevalueslist:
                        testComment = 'Test Fail - Group Table ACTIVE total count is "0" but active fault events list is not empty for feeder "%s" ' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table ACTIVE total count is "0" and active fault events list is empty for feeder "%s" ' %feeder
                        printFP(testComment)


            if not int(sustained[0]) == int(feedersustainedcount):
                testComment = 'Test Fail - Group Table SUSTAINED total count is not matched with total no. of sustained fault events count for feeder "%s" ' %feeder
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Group Table SUSTAINED total count is matched with total no. of sustained fault events count for feeder "%s" ' %feeder
                printFP(testComment)
                if int(sustained[0]) == 0:
                    if sustainedvalueslist:
                        testComment = 'Test Fail - Group Table SUSTAINED total count is "0" but sustained fault events list is not empty for feeder "%s" ' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table SUSTAINED total count is "0" and sustained fault events list is empty for feeder "%s" ' %feeder
                        printFP(testComment)

            if not int(momentary[0]) == int(feedermomentarycount):
                testComment = 'Test Fail - Group Table MOMENTARY total count is not matched with total no. of momentary fault events count for feeder "%s" ' %feeder
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Group Table MOMENTARY total count is matched with total no. of momentary fault events count for feeder "%s" ' %feeder
                printFP(testComment)
                if int(momentary[0]) == 0:
                    if momentaryvalueslist:
                        testComment = 'Test Fail - Group Table MOMENTARY total count is "0" but momentary fault events list is not empty for feeder "%s" ' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table MOMENTARY total count is "0" and momentary fault events list is empty for feeder "%s" ' %feeder
                        printFP(testComment)

            testComment = 'Test Pass - Validated feeder group table Toal Event Count sucessfully for feeder "%s"' %feeder
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a feeder which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsFeederGroupTableDurationValidation(input_file_path):

    printFP('Validating feeder group table Total Duration')

    pagename = 'line-monitoring'

    propertyname = 'Total Interruption Duration'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(5)

    if getfeeder:
        UnCheckAllEventTypes()
        UnCheckAllEventStates()
        time.sleep(3)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given feeder has faultevents")

            sustainedcount = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', 'Total Event Count')
            momentarycount = FaultEventsGroupTableFilteredData(pagename, 'MOMENTARY', 'Total Event Count')
            activecount = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', 'Total Event Count')

            sustained = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', propertyname)
            momentary = FaultEventsGroupTableFilteredData(pagename, 'MOMENTARY', propertyname)
            active = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', propertyname)

            SelectEventState('Active')
            activevalueslist , feederactivetotalduration = FaultEventsGetFaultEventsTotalDuration(pagename)
            UnselectEventState('Active')

            SelectEventType('Sustained Interruption')
            sustainedvalueslist , feedersustainedtotalduration = FaultEventsGetFaultEventsTotalDuration(pagename)
            UnselectEventType('Sustained Interruption')

            SelectEventType('Momentary Interruption')
            momentaryvalueslist , feedermomentarytotalduration = FaultEventsGetFaultEventsTotalDuration(pagename)
            UnselectEventType('Momentary Interruption')

            if int(activecount[0]) == 0:
                if not str(active[0]) == 'N/A' and activevalueslist:
                    testComment = 'Test Fail - Group Table ACTIVE total count is "0" but Total duration is not having "N/A" or active fault events list is not empty for feeder "%s" ' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table ACTIVE total count is "0" and Total duration is having "N/A" and active fault events list is empty for feeder "%s" ' %feeder
                    printFP(testComment)
            else:
                if feederactivetotalduration == 0:
                    feederactivetotalduration = 'N/A'
                    if not str(active[0]) == str(feederactivetotalduration):
                        testComment = 'Test Fail - Group Table ACTIVE total duration is not matched with total duration of active fault events for feeder "%s" ' %feeder
                        printFP(testComment)
                        return Global.FAIL, testComment
                    else:
                        testComment = 'Test Pass - Group Table ACTIVE total duration is matched with total duration of active fault events for feeder "%s" ' %feeder
                        printFP(testComment)

            if str(feedersustainedtotalduration) == '0':
                if sustainedvalueslist:
                    testComment = 'Test Fail - Group Table SUSTAINED total duration is "0" but sustained fault events list is not empty for feeder "%s" ' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table SUSTAINED total duration is "0" and sustained fault events list is empty for feeder "%s" ' %feeder
                    printFP(testComment)
            else:
                if not str(sustained[0]) == str(feedersustainedtotalduration):
                    testComment = 'Test Fail - Group Table SUSTAINED total duration is not matched with total duration of sustained fault events for feeder "%s" ' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table SUSTAINED total duration is matched with total duration of sustained fault events  for feeder "%s" ' %feeder
                    printFP(testComment)

            if str(feedermomentarytotalduration) == '0':
                if momentaryvalueslist:
                    testComment = 'Test Fail - Group Table MOMENTARY total duration is "0" but momentary fault events list is not empty for feeder "%s" ' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table MOMENTARY total duration is "0" and momentary fault events list is empty for feeder "%s" ' %feeder
                    printFP(testComment)
            else:
                if not str(momentary[0]) == str(feedermomentarytotalduration):
                    testComment = 'Test Fail - Group Table MOMENTARY total duration is not matched with total duration of momentary fault events for feeder "%s" ' %feeder
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Group Table MOMENTARY total duration is matched with total duration of momentary fault events  for feeder "%s" ' %feeder
                    printFP(testComment)


            testComment = 'Test Pass - Validated feeder group table Toal Duration sucessfully for feeder "%s"' %feeder
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a feeder which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSiteCheckEventType(input_file_path):

    printFP('Select all Event Type and validate for site')

    faulteventtypes = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        UnCheckAllEventStates()
        time.sleep(5)
        UnCheckAllEventTypes()
        time.sleep(5)
        UnCheckAllTriggeredDetectors()
        time.sleep(5)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given site has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event Type: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event Type "%s" is selected successfully' %filtername)
                                time.sleep(5)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event Type "%s" is already selected by default' %filtername)

                        siteeventtypefilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Event Type')
                        faulteventtypes.append(filtername)
                        #printFP(siteeventtypefilteredvalueslist)
                        printFP(faulteventtypes)
                        if siteeventtypefilteredvalueslist:
                            if any(x != filtername for x in siteeventtypefilteredvalueslist):
                                testComment = 'Test Fail - Other event types are listed in the filtered data when selected event type "%s" for site "%s"' %(filtername,site)
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Only selected event types are listed in the filtered data when selected event type "%s" for site "%s"' %(filtername,site)
                                printFP(testComment)
                        else:
                            testComment = 'INFO - There is no fault events with "%s" event type in the table so test is not executed for this event type for site "%s"' %(filtername,site)
                            printFP(testComment)
                        UnselectEventType(filtername)
                        time.sleep(5)
                    n=n+1


            testComment = 'Test Pass - All fault event types are selected one by one and validated in filtered data table for site:  %s ' %site
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a site which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSiteCheckEventState(input_file_path):

    printFP('Select all Event State and validate for site')

    faulteventstate = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsite = GetSiteFromTop(region,substation, feeder, site)

    time.sleep(5)

    if getsite:
        UnCheckAllEventStates()
        time.sleep(5)
        UnCheckAllEventTypes()
        time.sleep(5)
        UnCheckAllTriggeredDetectors()
        time.sleep(5)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given site has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Event State drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Event State drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Event State: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Event State "%s" is selected successfully' %filtername)
                                time.sleep(5)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Event State "%s" is already selected by default' %filtername)

                        siteeventstatefilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Event State')
                        faulteventstate.append(filtername)
                        #printFP(siteeventstatefilteredvalueslist)
                        printFP(faulteventstate)
                        if siteeventstatefilteredvalueslist:
                            if any(x != filtername for x in siteeventstatefilteredvalueslist):
                                testComment = 'Test Fail - Other event state are listed in the filtered data when selected event state "%s" for site "%s"' %(filtername,site)
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Only selected event state are listed in the filtered data when selected event state "%s" for site "%s"' %(filtername,site)
                                printFP(testComment)
                        else:
                            testComment = 'INFO - There is no fault events with "%s" event state in the table so test is not executed for this event state for site "%s"' %(filtername,site)
                            printFP(testComment)
                        UnselectEventState(filtername)
                        time.sleep(5)
                    n=n+1

            testComment = 'Test Pass - All fault event states are selected one by one and validated in filtered data table for site:  %s ' %site
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a site which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSiteCheckTriggeredDetector(input_file_path):

    printFP('Select all Triggered Detectors and validate for site')

    faulttriggereddetector = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsite = GetSiteFromTop(region,substation, feeder, site)

    time.sleep(5)

    if getsite:
        UnCheckAllEventStates()
        time.sleep(5)
        UnCheckAllEventTypes()
        time.sleep(5)
        UnCheckAllTriggeredDetectors()
        time.sleep(5)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given site has faultevents")
            dropdown = GetElement(Global.driver, By.CLASS_NAME, 'detector-select-list')
            dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
            try:
                dropdownbutton.click()
                time.sleep(2)
            except:
                testComment = 'Test Fail - Unable to click "Triggered Detector drop down button"'
                printFP(testComment)
                return Global.FAIL, testComment
            time.sleep(1)
            try:
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                #print dropdownlist
            except:
                dropdownbutton.click()
                time.sleep(1)
                dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

            if dropdownlist:
                dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                n=0
                for option in dropdownoptions:
                    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'detector-select-list')
                    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
                    try:
                        dropdownbutton.click()
                        time.sleep(2)
                    except:
                        testComment = 'Test Fail - Unable to click "Triggered Detector drop down button"'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    try:
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                        #print dropdownlist
                    except:
                        dropdownbutton.click()
                        time.sleep(1)
                        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
                    if dropdownlist:
                        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
                    option = dropdownoptions[n]
                    rawfiltername = option.text
                    filtername = rawfiltername.strip().replace('"','')
                    #filtername = ''.join(filtername.split())
                    if filtername and not 'Uncheck All' in filtername:
                        printFP('Selecting Triggered Detector: %s' %filtername)
                        currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                        classname = currentbuttonstatus.get_attribute('class')
                        if not "glyphicon-ok" in classname:
                            eventbutton = GetElement(option, By.TAG_NAME, 'a')
                            try:
                                eventbutton.click()
                                printFP('Triggered Detector "%s" is selected successfully' %filtername)
                                time.sleep(5)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" option' %filtername
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            printFP('Triggered Detector "%s" is already selected by default' %filtername)

                        sitetriggereddetectorfilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Triggered Detector')
                        faulttriggereddetector.append(filtername)
                        #printFP(sitetriggereddetectorfilteredvalueslist)
                        printFP(faulttriggereddetector)
                        if sitetriggereddetectorfilteredvalueslist:
                            if 'Blanks' in filtername:
                                if any(x != '' for x in sitetriggereddetectorfilteredvalueslist):
                                    testComment = 'Test Fail - Other Triggered Detector are listed in the filtered data when selected Triggered Detector "%s" for site "%s"' %(filtername,site)
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    testComment = 'Test Pass - Triggered Detector column is empty in the filtered data when selected Triggered Detector "%s" for site "%s"' %(filtername,site)
                                    printFP(testComment)
                                    pass
                            elif any(x != filtername for x in sitetriggereddetectorfilteredvalueslist):
                                testComment = 'Test Fail - Other Triggered Detector are listed in the filtered data when selected Triggered Detector "%s" for site "%s"' %(filtername,site)
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - Only selected Triggered Detector are listed in the filtered data when selected Triggered Detector "%s" for site "%s"' %(filtername,site)
                                printFP(testComment)
                        else:
                            testComment = 'INFO - There is no fault events with "%s" Triggered Detector in the table so test is not executed for this Triggered Detector for site "%s"' %(filtername,site)
                            printFP(testComment)
                        UnselectTriggeredDetector(filtername)
                        time.sleep(5)
                    n=n+1

            testComment = 'Test Pass - All fault Triggered Detectors are selected one by one and validated in filtered data table for site:  %s ' %site
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a site which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsSiteUnCheckAll(input_file_path):

    printFP('Select Event Type/Event State/Triggered Detectors UncheckAll and validate')

    faulteventstate = []

    pagename = 'line-monitoring'

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsite = GetSiteFromTop(region,substation, feeder, site)

    time.sleep(5)

    if getsite:
        SelectAllEventTypes()
        time.sleep(5)
        SelectAllEventStates()
        time.sleep(5)
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP("Given site has faultevents")
            UnselectEventType('Fault Without Interruption')
            time.sleep(5)
            UnselectEventState('Cleared')
            time.sleep(5)
            UnselectTriggeredDetector('Threshold')
            time.sleep(5)
            siteeventtypefilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Event Type')
            siteeventstatefilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Event State')
            sitetriggereddetectorfilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Triggered Detector')
            #printFP(siteeventtypefilteredvalueslist)
            #printFP(siteeventstatefilteredvalueslist)
            if siteeventtypefilteredvalueslist:
                if any(x == 'Fault Without Interruption' for x in siteeventtypefilteredvalueslist):
                    testComment = 'Test Fail - Unselected event type is listed in the filtered data when unselected event type "Fault Without Interruption" for site "%s"' %site
                    printFP(testComment)
                    return Global.FAIL, testComment
            elif siteeventtypefilteredvalueslist:
                if any(x == 'Cleared' for x in siteeventstatefilteredvalueslist):
                    testComment = 'Test Fail - Unselected event state is listed in the filtered data when unselected event state "Cleared" for site "%s"' %site
                    printFP(testComment)
                    return Global.FAIL, testComment
            elif sitetriggereddetectorfilteredvalueslist:
                if any(x == 'Threshold' for x in sitetriggereddetectorfilteredvalueslist):
                    testComment = 'Test Fail - Unselected triggered detector is listed in the filtered data when unselected triggered detector "Threshold" for site "%s"' %site
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Pass - Unselected event type, triggered detector and state are not listed in the filtered data when unselected event type "Fault Without Interruption" , event state "Active" and triggered detector "Threshold" for site "%s"' %site
                printFP(testComment)
                UnCheckAllEventStates()
                time.sleep(5)
                UnCheckAllEventTypes()
                time.sleep(5)
                UnCheckAllTriggeredDetectors()
                time.sleep(5)
                siteeventtypefilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Event Type')
                siteeventstatefilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Event State')
                sitetriggereddetectorfilteredvalueslist = FaultEventsSiteTableFilteredAllData(pagename, 'Triggered Detector')
                #printFP(siteeventtypefilteredvalueslist)
                #printFP(siteeventstatefilteredvalueslist)
                if siteeventtypefilteredvalueslist:
                    if any(x == 'Fault Without Interruption' for x in siteeventtypefilteredvalueslist):
                        testComment = 'Test Pass - Unselected event type "Fault Without Interruption" is listed in the filtered data when selected "Uncheck All" of event type for site "%s"' %site
                        printFP(testComment)
                        if siteeventstatefilteredvalueslist:
                            if any(x == 'Cleared' for x in siteeventstatefilteredvalueslist):
                                testComment = 'Test Pass - Unselected event state "Cleared" is listed in the filtered data when selected "Uncheck All" of event state for site "%s"' %site
                                printFP(testComment)
                                if sitetriggereddetectorfilteredvalueslist:
                                    if any(x == 'Threshold' for x in sitetriggereddetectorfilteredvalueslist):
                                        testComment = 'Test Pass - Unselected triggered detector "Threshold" is listed in the filtered data when selected "Uncheck All" of triggered detector for site "%s"' %site
                                        printFP(testComment)
                                    else:
                                        testComment = 'Test Fail - Unselected triggered detector "Threshold" is not listed in the filtered data when selected "Uncheck All" for site "%s"' %site
                                        printFP(testComment)
                                        return Global.FAIL, testComment
                                else:
                                    testComment = 'Test Fail - Please point to a site which has all types , triggered detectors and states of fault events'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                            else:
                                testComment = 'Test Fail - Unselected event state "Cleared" is not listed in the filtered data when selected "Uncheck All" for site "%s"' %site
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'Test Fail - Please point to a site which has all types , triggered detectors and states of fault events'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    else:
                        testComment = 'Test Fail -Unselected event type "Fault Without Interruption" is not listed in the filtered data when selected "Uncheck All" for site "%s"' %site
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    testComment = 'Test Fail - Please point to a site which has all types , triggered detectors and states of fault events'
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Unselected event type , triggered detector and state are listed in the filtered data when selected "Uncheck All" of event type, triggered detector and event state for site "%s"' %site
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any fault events. Please point to a site which has fault events"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

'''def FaultEventsDetectorButton(input_file_path):

    printFP('Verifying Fault Event Screen Detector button')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(1)

    if getfeeder:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has faultevents")

            finddetectordropdown = GetElements(Global.driver, By.CLASS_NAME, 'pull-left')
            for detectordropdown in finddetectordropdown:
                tmpdetectordropdown = GetElement(detectordropdown, By.TAG_NAME, 'span')
                detectorname = tmpdetectordropdown.text
                detectorname = detectorname.replace(' ','').replace(':','')
                if detectorname == "Detector":
                    detectordropdownbutton = GetElement(detectordropdown, By.TAG_NAME, 'button')
                    detectordropdowndisplay = detectordropdownbutton.text
                    try:
                        detectordropdownbutton.click()
                        time.sleep(1)
                    except:
                        testComment = 'Test Fail - Unable to click "detector drop down button" detector filter'
                        printFP(testComment)
                        return Global.FAIL, testComment
                    time.sleep(1)
                    detectordropdownlist = GetElement(detectordropdown, By.TAG_NAME, 'ul')
                    detectordropdownoptions = GetElements(detectordropdownlist, By.TAG_NAME, 'li')
                    for detectoroption in detectordropdownoptions:
                        detectorfiltername = detectoroption.text
                        detectorfiltername = detectorfiltername.replace(' ','').replace('"','')
                        detectorcolumnname = 'Detector'
                        printFP(detectorfiltername)
                        if detectorfiltername == "CheckAll":
                            try:
                                detectoroption.click()
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "CheckAll" detector filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            time.sleep(1)
                            detectordropdowndisplay = detectordropdownbutton.text
                            detectordropdowndisplay = detectordropdowndisplay.replace('"','')
                            if "3/3 Checked" in detectordropdowndisplay:
                                nodataavailable = NoDataAvailable('line-monitoring')
                                if nodataavailable == "No Data Available":
                                    testComment = 'Test Fail - Found "No Data Available" text when select Detector filter "' + detectorfiltername + '"'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                    if "cFCI Fault Indication Alert" in filtereddetectordata:
                                        printFP('"cFCI Fault Indication Alert" are available for selected feeder')
                                    else:
                                        printFP('"cFCI Fault Indication Alert" are not available for selected feeder')
                                    if "cFCI Led State" in filtereddetectordata:
                                        printFP('"cFCI Led State" are available for selected feeder')
                                    else:
                                        printFP('"cFCI Led State" are not available for selected feeder')
                                    if "cFCI Loss of Source" in filtereddetectordata:
                                        printFP('"cFCI Loss of Source" are available for selected feeder')
                                    else:
                                        printFP('"cFCI Loss of Source" are not available for selected feeder')
                            else:
                                testComment = '"CheckAll" detector filter was not working as expected'
                                return Global.FAIL, testComment

                        elif detectorfiltername == "UncheckAll":
                            try:
                                detectoroption.click()
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "UncheckAll" detector filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            time.sleep(1)
                            detectordropdowndisplay = detectordropdownbutton.text
                            detectordropdowndisplay = detectordropdowndisplay.replace('"','')
                            if "Select" in detectordropdowndisplay:
                                nodataavailable = NoDataAvailable('line-monitoring')
                                if nodataavailable == "No Data Available":
                                    testComment = 'Found "No Data Available" text when select Detector filter "' + detectorfiltername + '"'
                                    printFP(testComment)
                                else:
                                    filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                    if "cFCI Fault Indication Alert" in filtereddetectordata:
                                        printFP('"cFCI Fault Indication Alert" are available for selected feeder')
                                        testComment = 'Test Fail - Not Found "No Data Available" text when select Detector filter "' + detectorfiltername + '"'
                                        return Global.FAIL, testComment
                                    else:
                                        printFP('"cFCI Fault Indication Alert" are not available for selected feeder')
                                    if "cFCI Led State" in filtereddetectordata:
                                        printFP('"cFCI Led State" are available for selected feeder')
                                        testComment = 'Test Fail - Not Found "No Data Available" text when select Detector filter "' + detectorfiltername + '"'
                                        return Global.FAIL, testComment
                                    else:
                                        printFP('"cFCI Led State" are not available for selected feeder')
                                    if "cFCI Loss of Source" in filtereddetectordata:
                                        printFP('"cFCI Loss of Source" are available for selected feeder')
                                        testComment = 'Test Fail - Not Found "No Data Available" text when select Detector filter "' + detectorfiltername + '"'
                                        return Global.FAIL, testComment
                                    else:
                                        printFP('"cFCI Loss of Source" are not available for selected feeder')
                            else:
                                testComment = 'Test Fail - "UncheckAll" detector filter was not working as expected'
                                printFP(testComment)
                                return Global.FAIL, testComment

                        elif detectorfiltername == "cFCIFaultIndicationAlert":

                            currentbuttonstatus = GetElement(detectoroption, By.TAG_NAME, 'span')
                            classname = currentbuttonstatus.get_attribute('class')

                            if "glyphicon-ok" in classname:

                                filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                if "cFCI Fault Indication Alert" in filtereddetectordata:
                                    printFP('"cFCI Fault Indication Alert" are available for selected feeder')

                                    try:
                                        detectoroption.click()
                                        time.sleep(1)
                                    except:
                                        testComment = 'Test Fail - Unable to click "cFCI Fault Indication Alert" detector filter'
                                        printFP(testComment)
                                        return Global.FAIL, testComment

                                    nodataavailable = NoDataAvailable('line-monitoring')
                                    if nodataavailable == "No Data Available":
                                        testComment = 'Found "No Data Available" Text when unselect detector filter "cFCI Fault Indication Alert"- Test Pass'
                                        printFP(testComment)
                                    else:
                                        filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                        if not "cFCI Fault Indication Alert" in filtereddetectordata:
                                            testComment = 'Not Found "No Data Available" and "cFCI Fault Indication Alert" Text when unselect detector filter "' + detectorfiltername + '". Data is displayed for other filters - Test Pass'
                                            printFP(testComment)
                                        else:
                                            testComment = 'Test Fail - "cFCI Fault Indication Alert" are still displayed when unselect detector filter "' + detectorfiltername + '" - Test Fail'
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                    detectoroption.click()
                                    time.sleep(1)
                                else:
                                    printFP('"cFCI Fault Indication Alert" are not available for selected feeder')

                            else:
                                try:
                                    detectoroption.click()
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "cFCI Fault Indication Alert" detector filter'
                                    return Global.FAIL, testComment

                                filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                if "cFCI Fault Indication Alert" in filtereddetectordata:
                                    testComment = '"cFCI Fault Indication Alert" are displayed when select detector filter "' + detectorfiltername + '". - Test Pass'
                                    printFP(testComment)

                                    detectoroption.click()
                                    time.sleep(1)
                                    nodataavailable = NoDataAvailable('line-monitoring')
                                    if nodataavailable == "No Data Available":
                                        testComment = 'Found "No Data Available" Text when unselect detector filter "cFCI Fault Indication Alert" - Test Pass'
                                        printFP(testComment)
                                    else:
                                        filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                        if not "cFCI Fault Indication Alert" in filtereddetectordata:
                                            testComment = 'Not Found "cFCI Fault Indication Alert" Text when unselect detector filter "' + detectorfiltername + '". Data is displayed for other filters - Test Pass'
                                            printFP(testComment)
                                        else:
                                            testComment = 'Test Fail - "cFCI Fault Indication Alert" are still displayed when unselect detector filter "' + detectorfiltername + '" - Test Fail'
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                else:
                                    testComment = '"cFCI Fault Indication Alert" are not available for selected feeder'
                                    printFP(testComment)

                        elif detectorfiltername == "cFCILedState":

                            currentbuttonstatus = GetElement(detectoroption, By.TAG_NAME, 'span')
                            classname = currentbuttonstatus.get_attribute('class')

                            if "glyphicon-ok" in classname:
                                filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                if "cFCI Led State" in filtereddetectordata:
                                    printFP('"cFCI Led State" are available for selected feeder')

                                    try:
                                        detectoroption.click()
                                        time.sleep(1)
                                    except:
                                        testComment = 'Test Fail - Unable to click "cFCI Led State" detector filter'
                                        return Global.FAIL, testComment

                                    nodataavailable = NoDataAvailable('line-monitoring')
                                    if nodataavailable == "No Data Available":
                                        testComment = 'Found "No Data Available" Text when unselect detector filter "cFCI Led State"- Test Pass'
                                        printFP(testComment)
                                    else:
                                        filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                        if not "cFCI Led State" in filtereddetectordata:
                                            testComment = 'Not Found "No Data Available" and "cFCI Led State" Text when unselect detector filter "' + detectorfiltername + '". Data is displayed for other filters - Test Pass'
                                            printFP(testComment)
                                        else:
                                            testComment = 'Test Fail - "cFCI Led State" are still displayed when unselect detector filter "' + detectorfiltername + '" - Test Fail'
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                    detectoroption.click()
                                    time.sleep(1)
                                else:
                                    printFP('"cFCI Led State" are not available for selected feeder')

                            else:
                                try:
                                    detectoroption.click()
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "cFCI Led State" detector filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                                filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                if "cFCI Led State" in filtereddetectordata:
                                    testComment = '"cFCI Led State" are displayed when select detector filter "' + detectorfiltername + '". - Test Pass'
                                    printFP(testComment)

                                    detectoroption.click()
                                    time.sleep(1)
                                    nodataavailable = NoDataAvailable('line-monitoring')
                                    if nodataavailable == "No Data Available":
                                        testComment = 'Found "No Data Available" Text when unselect detector filter "cFCI Led State" - Test Pass'
                                        printFP(testComment)
                                    else:
                                        filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                        if not "cFCI Led State" in filtereddetectordata:
                                            testComment = 'Not Found "cFCI Led State" Text when unselect detector filter "' + detectorfiltername + '". Data is displayed for other filters - Test Pass'
                                            printFP(testComment)
                                        else:
                                            testComment = 'Test Fail - "cFCI Led State" are still displayed when unselect detector filter "' + detectorfiltername + '" - Test Fail'
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                else:
                                    testComment = '"cFCI Led State" are not available for selected feeder'
                                    printFP(testComment)

                        elif detectorfiltername == "cFCILossofSourceinProgress":

                            currentbuttonstatus = GetElement(detectoroption, By.TAG_NAME, 'span')
                            classname = currentbuttonstatus.get_attribute('class')

                            if "glyphicon-ok" in classname:
                                filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                if "cFCI Loss of Source" in filtereddetectordata:
                                    printFP('"cFCI Loss of Source" are available for selected feeder')

                                    try:
                                        detectoroption.click()
                                        time.sleep(1)
                                    except:
                                        testComment = 'Test Fail - Unable to click "cFCI Loss of Source" detector filter'
                                        printFP(testComment)
                                        return Global.FAIL, testComment

                                    nodataavailable = NoDataAvailable('line-monitoring')
                                    if nodataavailable == "No Data Available":
                                        testComment = 'Found "No Data Available" Text when unselect detector filter "cFCI Loss of Source"- Test Pass'
                                        printFP(testComment)
                                    else:
                                        filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                        if not "cFCI Loss of Source" in filtereddetectordata:
                                            testComment = 'Not Found "No Data Available" and "cFCI Loss of Source" Text when unselect detector filter "' + detectorfiltername + '". Data is displayed for other filters - Test Pass'
                                            printFP(testComment)
                                        else:
                                            testComment = 'Test Fail - "cFCI Loss of Source" are still displayed when unselect detector filter "' + detectorfiltername + '" - Test Fail'
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                    detectoroption.click()
                                    time.sleep(1)
                                else:
                                    printFP('"cFCI Loss of Source" are not available for selected feeder')

                            else:
                                try:
                                    detectoroption.click()
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "cFCI Loss of Source" detector filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                                filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                if "cFCI Loss of Source" in filtereddetectordata:
                                    testComment = '"cFCI Loss of Source" are displayed when select detector filter "' + detectorfiltername + '". - Test Pass'
                                    printFP(testComment)

                                    detectoroption.click()
                                    time.sleep(1)
                                    nodataavailable = NoDataAvailable('line-monitoring')
                                    if nodataavailable == "No Data Available":
                                        testComment = 'Found "No Data Available" Text when unselect detector filter "cFCI Loss of Source" - Test Pass'
                                        printFP(testComment)
                                    else:
                                        filtereddetectordata = FilterFromFaultEventsData(detectorcolumnname)
                                        if not "cFCI Loss of Source" in filtereddetectordata:
                                            testComment = 'Not Found "cFCI Loss of Source" Text when unselect detector filter "' + detectorfiltername + '". Data is displayed for other filters - Test Pass'
                                            printFP(testComment)
                                        else:
                                            testComment = 'Test Fail - "cFCI Loss of Source" are still displayed when unselect detector filter "' + detectorfiltername + '" - Test Fail'
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                else:
                                    testComment = '"cFCI Loss of Source" are not available for selected feeder'
                                    printFP(testComment)

                    testComment = 'Test Pass - Verified all Fault Events Detectors successfully and all test cases are PASS'
                    return Global.PASS, testComment
        else:
            printFP("Test Fail - Line Monitoring doesn't have any faultevents. Please point to a feeder which has faultevents")
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsPhaseFilters(input_file_path):

    printFP('Verifying Fault Event Screen Phase Filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(1)
    if getfeeder:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has faultevents")

            #Get all toggle button elements
            phasebuttonelement = GetElement(Global.driver, By.TAG_NAME, 'phase-filter')
            time.sleep(1)
            phasefilters = GetElements(phasebuttonelement, By.TAG_NAME, 'label')
            time.sleep(2)
            for phasefilter in phasefilters:

                phasefiltername = phasefilter.text
                print phasefiltername
                phasecolumnname = 'Phase'
                printFP(phasecolumnname)
                filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                print filteredphasedata

                if phasefiltername == "A":
                    exportbuttonclassname = phasefilter.get_attribute('class')
                    print exportbuttonclassname

                    if "active" in exportbuttonclassname:
                        if "A" in filteredphasedata:

                            printFP('"Phase A" data are available for selected feeder')

                            try:
                                phasefilter.click()
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "A" Phase filter'
                                printFP(testComment)
                                return Global.FAIL, testComment

                            nodataavailable = NoDataAvailable('line-monitoring')
                            if nodataavailable == "No Data Available":
                                testComment = 'Found "No Data Available" Text when unselect Phase filter "A" - Test Pass'
                                printFP(testComment)
                            else:
                                filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                                if not "A" in filteredphasedata:
                                    testComment = 'Not Found "No Data Available" and "Phase A" when unselect Phase filter "' + phasefiltername + '". Data is displayed only for other filters - Test Pass'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase A" data are still displayed when unselect Phase filter "' + phasefiltername + '" - Test Fail'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                            phasefilter.click()
                            time.sleep(1)
                        else:
                            printFP('"Phase A" data are not available for selected feeder')


                    elif not "active" in exportbuttonclassname:
                        try:
                            phasefilter.click()
                            time.sleep(1)
                        except:
                            testComment = 'Test Fail - Unable to click "Phase A" filter'
                            printFP(testComment)
                            return Global.FAIL, testComment

                        filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                        if "A" in filteredphasedata:
                            testComment = '"Phase A" data are displayed when select Phase filter "' + phasefiltername + '". - Test Pass'
                            printFP(testComment)

                            phasefilter.click()
                            time.sleep(1)
                            nodataavailable = NoDataAvailable('line-monitoring')
                            if nodataavailable == "No Data Available":
                                testComment = 'Found "No Data Available" Text when unselect Phase filter "A" - Test Pass'
                                printFP(testComment)
                            else:
                                filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                                if not "A" in filteredphasedata:
                                    testComment = 'Not Found "Phase A" when unselect Phase filter "' + phasefiltername + '". Data is displayed only for other filters - Test Pass'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase A" data are still displayed when unselect Phase filter "' + phasefiltername + '" - Test Fail'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                        else:
                            testComment = '"Phase A" data are not available for selected feeder'
                            printFP(testComment)

                    else:
                        printFP('Unable to find whether Phase "A" button is enabled or not')

                elif phasefiltername == "B":
                    exportbuttonclassname = phasefilter.get_attribute('class')
                    print exportbuttonclassname

                    if "active" in exportbuttonclassname:
                        if "B" in filteredphasedata:

                            printFP('"Phase B" data are available for selected feeder')

                            try:
                                phasefilter.click()
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "B" Phase filter'
                                printFP(testComment)
                                return Global.FAIL, testComment

                            nodataavailable = NoDataAvailable('line-monitoring')
                            if nodataavailable == "No Data Available":
                                testComment = 'Found "No Data Available" Text when unselect Phase filter "B" - Test Pass'
                                printFP(testComment)
                            else:
                                filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                                if not "B" in filteredphasedata:
                                    testComment = 'Not Found "No Data Available" and "Phase B" when unselect Phase filter "' + phasefiltername + '". Data is displayed only for other filters - Test Pass'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase B" data are still displayed when unselect Phase filter "' + phasefiltername + '" - Test Fail'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                            phasefilter.click()
                            time.sleep(1)
                        else:
                            printFP('"Phase B" data are not available for selected feeder')


                    elif not "active" in exportbuttonclassname:
                        try:
                            phasefilter.click()
                            time.sleep(1)
                        except:
                            testComment = 'Test Fail - Unable to click "Phase B" filter'
                            printFP(testComment)
                            return Global.FAIL, testComment

                        filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                        if "B" in filteredphasedata:
                            testComment = '"Phase B" data are displayed when select Phase filter "' + phasefiltername + '". - Test Pass'
                            printFP(testComment)

                            phasefilter.click()
                            time.sleep(1)
                            nodataavailable = NoDataAvailable('line-monitoring')
                            if nodataavailable == "No Data Available":
                                testComment = 'Found "No Data Available" Text when unselect Phase filter "B" - Test Pass'
                                printFP(testComment)
                            else:
                                filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                                if not "B" in filteredphasedata:
                                    testComment = 'Not Found "Phase B" when unselect Phase filter "' + phasefiltername + '". Data is displayed only for other filters - Test Pass'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase B" data are still displayed when unselect Phase filter "' + phasefiltername + '" - Test Fail'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                        else:
                            testComment = '"Phase B" data are not available for selected feeder'
                            printFP(testComment)

                    else:
                        printFP('Unable to find whether Phase "B" button is enabled or not')

                elif phasefiltername == "C":
                    exportbuttonclassname = phasefilter.get_attribute('class')
                    print exportbuttonclassname

                    if "active" in exportbuttonclassname:
                        if "C" in filteredphasedata:

                            printFP('"Phase C" data are available for selected feeder')

                            try:
                                phasefilter.click()
                                time.sleep(1)
                            except:
                                testComment = 'Test Fail - Unable to click "C" Phase filter'
                                printFP(testComment)
                                return Global.FAIL, testComment

                            nodataavailable = NoDataAvailable('line-monitoring')
                            if nodataavailable == "No Data Available":
                                testComment = 'Found "No Data Available" Text when unselect Phase filter "C" - Test Pass'
                                printFP(testComment)
                            else:
                                filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                                if not "C" in filteredphasedata:
                                    testComment = 'Not Found "No Data Available" and "Phase C" when unselect Phase filter "' + phasefiltername + '". Data is displayed only for other filters - Test Pass'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase C" data are still displayed when unselect Phase filter "' + phasefiltername + '" - Test Fail'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                            phasefilter.click()
                            time.sleep(1)
                        else:
                            printFP('"Phase C" data are not available for selected feeder')


                    elif not "active" in exportbuttonclassname:
                        try:
                            phasefilter.click()
                            time.sleep(1)
                        except:
                            testComment = 'Test Fail - Unable to click "Phase C" filter'
                            printFP(testComment)
                            return Global.FAIL, testComment

                        filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                        if "C" in filteredphasedata:
                            testComment = '"Phase C" data are displayed when select Phase filter "' + phasefiltername + '". - Test Pass'
                            printFP(testComment)

                            phasefilter.click()
                            time.sleep(1)
                            nodataavailable = NoDataAvailable('line-monitoring')
                            if nodataavailable == "No Data Available":
                                testComment = 'Found "No Data Available" Text when unselect Phase filter "C" - Test Pass'
                                printFP(testComment)
                            else:
                                filteredphasedata = FilterFromFaultEventsData(phasecolumnname)
                                if not "C" in filteredphasedata:
                                    testComment = 'Not Found "Phase C" when unselect Phase filter "' + phasefiltername + '". Data is displayed only for other filters - Test Pass'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase C" data are still displayed when unselect Phase filter "' + phasefiltername + '" - Test Fail'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                        else:
                            testComment = '"Phase C" data are not available for selected feeder'
                            printFP(testComment)

                    else:
                        printFP('Unable to find whether Phase "C" button is enabled or not')
                else:
                    testComment = 'Test Fail - Phase filter "' + phasefiltername + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Verified all Fault Events phasefilters successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            printFP("Test Fail - Line Monitoring doesn't have any faultevents. Please point to a feeder which has faultevents")
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsTimeRangeSelection(input_file_path):

    printFP('Verifying FaultEvents Screen timerange Filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    pagename = 'line-monitoring'

    GoToLineMon()
    GoToLineMonFaultEvents()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(10)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has FaultEvents data")

            #Get all time range button elements
            timerangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
            time.sleep(1)
            timerangefilters = GetElements(timerangeframe, By.TAG_NAME, 'label')
            time.sleep(1)
            n=0
            for timerangefilter in timerangefilters:
                timerangefiltername = timerangefilter.text
                testtimerange =  timerangefiltername
                if timerangefiltername in ('1D','1W','1M', '3M', '6M', '1Y'):
                    buttonclassname = timerangefilter.get_attribute('class')
                    if "active" in buttonclassname:
                        printFP('"Selected Time Range '+ testtimerange +'" button is already selected by default')
                        rangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
                        rangefilters = GetElements(rangeframe, By.TAG_NAME, 'label')
                        m=n
                        m=m+1
                        try:
                            rangefilters[m].click()
                            time.sleep(5)
                            rangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
                            rangefilters = GetElements(rangeframe, By.TAG_NAME, 'label')
                            rangefilters[n].click()
                            time.sleep(5)
                        except:
                            testComment = 'Test Fail - Unable to click "'+ testtimerange +'" Time Range filter'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        timerangebuttonstatus = GetTimeRangeButtonStatus(testtimerange)
                        if timerangebuttonstatus:
                            testComment = 'Test Pass - "Selected Time Range '+ testtimerange +'" button got activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                        else:
                            testComment = 'Test Fail - "Time Range '+ testtimerange +'" button is still not activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                            return Global.FAIL, testComment

                    elif not "active" in buttonclassname:
                        try:
                            timerangefilter.click()
                            time.sleep(5)
                        except:
                            testComment = 'Test Fail - Unable to click "'+ testtimerange +'" Time Range filter'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        timerangebuttonstatus = GetTimeRangeButtonStatus(testtimerange)
                        if timerangebuttonstatus:
                            testComment = 'Test Pass - "Selected Time Range '+ testtimerange +'" button got activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                        else:
                            testComment = 'Test Fail - "Time Range '+ testtimerange +'" button is still not activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    else:
                        printFP('Unable to find whether Time Range "' + testtimerange + '" button is enabled or not')
                else:
                    testComment = 'Test Fail - Time Range filter "' + testtimerange + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment
                n=n+1

            testComment = 'Test Pass - Verified FaultEvents Time Range filters successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            printFP("Test Fail - Given site doesn't have FaultEvents data. Please point to a site which has FaultEvents data")
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def FaultEventsWaveformLink(input_file_path):

    printFP('Verifying Fault Event Waveform link state and navigation')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    if getfeeder:
        time.sleep(2)
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has faultevents")
            faultstatecolumnname = 'Waveform Status'
            printFP(faultstatecolumnname)
            columnorder = GetFaultEventsColumnOrder()
            columnposition = columnorder[faultstatecolumnname]
            columnnamevalueslist = []

            linemonitoringpage = GetElements(Global.driver, By.CLASS_NAME, 'line-monitoring')
            for linemonitoring in linemonitoringpage:
                uiview = linemonitoring.get_attribute('ui-view')
                if "lineMonitoring" in uiview:
                    table = GetElement(linemonitoring, By.TAG_NAME, 'table')
                    time.sleep(1)
                    tbody = GetElement(table, By.TAG_NAME, 'tbody')
                    time.sleep(1)
                    rows = GetElements(tbody, By.TAG_NAME, 'tr')
                    for row in rows:
                        n=1
                        columns = GetElements(row, By.TAG_NAME, 'td')
                        time.sleep(1)
                        for column in columns:
                            if n == columnposition:
                                value = column.text.strip()
                                columnnamevalueslist.append(value)
                                print(columnnamevalueslist)
                                if value == "Waveform":
                                    waveformlink = GetElement(column, By.TAG_NAME, 'a')
                                    try:
                                        classname = waveformlink.get_attribute('class')
                                        print classname
                                    except Exception as e:
                                        classname = None
                                        print e.message

                                    if 'disabled' in classname:
                                            testComment = 'Waveform link is disabled for fault event'
                                            printFP(testComment)
                                    else:
                                        waveformlink.click()
                                        time.sleep(2)
                                        if WaitForTitle('waveforms'):
                                            testComment = 'Test Pass - Successfully navigated to fault events waveform tab'
                                            printFP(testComment)
                                            return Global.PASS, testComment
                                        else:
                                            testComment = 'Test Fail - Waveform link is not navigated to fault events Waveform tab'
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                            n = n+1

                    testComment = 'Test Fail - Waveform link is not enabled for any fault events'
                    printFP(testComment)
                    return Global.FAIL, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any faultevents. Please point to a feeder which has faultevents"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment'''

def WaveformPastDateWithEmptyData(input_file_path, date=None, month=None, year=None):

    printFP('Verifying Waveform graph is displayed when select past date')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonWaveforms()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has Waveform")
            datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
            time.sleep(1)
            datepickerbutton.click()
            time.sleep(1)
            findcurrentmonthandyear = GetDatePickerCurrentTitle()
            currentmonthandyear = findcurrentmonthandyear.text
            #print('currentmonthandyear_1: %s' %currentmonthandyear)
            selectyear = None
            selectmonth = None
            selectdate = None
            if not year in currentmonthandyear:
                selectyear = SelectYearMonthAndDateFromCalendar(year, month, date)
                #print('selectyear %s:' %selectyear)
            elif not month in currentmonthandyear:
                selectmonth = SelectMonthAndDateFromCalendar(month, date)
                #print('selectmonth %s:' %selectmonth)
            else:
                selectdate = SelectDateFromCalendar(date)
                #print('selectdate %s:' %selectdate)

            if selectyear or selectmonth or selectdate:
                time.sleep(2)
                nodataavailable = NoDataAvailable('line-monitoring')
                if nodataavailable == "No Data Available":
                    testComment = 'Test Pass - Found "No Data Available" text when selected past date from datepicker'
                    printFP(testComment)
                    return Global.PASS, testComment
                else:
                    testComment = 'Test Fail - Waveform is still displayed when selected past date : %s %s %s' %(year, month, date)
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'Test Fail - Unable select a given date : %s %s %s' %(year, month, date)
                printFP(testComment)
                return Global.FAIL, testComment


        else:
            testComment = "Test Fail - Line Monitoring doesn't have any waveforms. Please point to a Site which has waveforms"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment


def WaveformExportButton(input_file_path):

    printFP('Verifying Waveform Screen Export button')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonWaveforms()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has Waveform")
            time.sleep(5)
            #Get export button elements
            exportbuttonelements = GetElements(Global.driver, By.CLASS_NAME, 'dropdown-toggle')

            # find export toggle dorpdown button
            for exportbuttonelement in exportbuttonelements:
                exportbuttonelementname = exportbuttonelement.text
                print exportbuttonelementname
                if 'Export' in exportbuttonelementname:
                    try:
                        isdisabled = exportbuttonelement.get_attribute('disabled')
                    except Exception as e:
                        print e.message

                    if isdisabled is None:
                        try:
                            time.sleep(2)
                            exportbuttonelement.click()
                        except Exception as e:
                            printFP(e.message)
                            printFP('Test Fail - Unable to click waveform Export Button')
                            break

                        exportdropdownframe = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-menu-form')
                        exportdropdownlists = GetElements(exportdropdownframe, By.TAG_NAME, 'li')
                        excelStatus = False
                        for exportdropdownlist in exportdropdownlists:
                            if not excelStatus:
                                formattype = exportdropdownlist.text
                                printFP('formattype %s' %formattype)

                                if 'EXCEL' in formattype:
                                    try:
                                        ClickButton(Global.driver, By.XPATH, xpaths['waveform_export_excel_button'])
                                        time.sleep(5)

                                        try:
                                            Global.driver.switch_to_window(Global.driver.window_handles[-1])
                                            cancelbutton = Global.driver.find_element_by_xpath(u'//input[@value="Cancel"]')
                                            print cancelbutton
                                            cancelbutton.click()
                                            time.sleep(1)
                                            Global.driver.switch_to_default_content()
                                        except Exception as e:
                                            printFP(e.message)

                                        testComment = "Test Pass - Able to export waveform data in excel format"
                                        printFP(testComment)
                                        excelStatus = True

                                    except:
                                        testComment = 'Test Fail - Unable to click "Excel" export option in waveform screen'
                                        printFP(testComment)
                                        return Global.FAIL, testComment
                    else:
                        testComment = "Test Fail - Export Button is not enabled. Please point to a feeder which has waveforms"
                        printFP(testComment)
                        return Global.FAIL, testComment

                    if isdisabled is None:
                        try:
                            time.sleep(2)
                            exportbuttonelement.click()
                        except Exception as e:
                            printFP(e.message)
                            printFP('Test Fail - Unable to click waveform Export Button')
                            break

                        exportdropdownframe = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-menu-form')
                        exportdropdownlists = GetElements(exportdropdownframe, By.TAG_NAME, 'li')
                        csvStatus = False
                        for exportdropdownlist in exportdropdownlists:
                            if not csvStatus:
                                formattype = exportdropdownlist.text
                                printFP('formattype %s' %formattype)

                                if 'CSV' in formattype:
                                    try:
                                        ClickButton(Global.driver, By.XPATH, xpaths['waveform_export_csv_button'])
                                        time.sleep(5)

                                        try:
                                            Global.driver.switch_to_window(Global.driver.window_handles[-1])
                                            title = Global.driver.title
                                        except Exception as e:
                                            printFP(e.message)

                                        testComment = "Test Fail - Able to export waveform data in CSV format"
                                        printFP(testComment)
                                        csvStatus = True

                                    except:
                                        testComment = 'Test Fail - Unable to click "CSV" export option in waveform screen'
                                        printFP(testComment)
                                        return Global.FAIL, testComment

                        time.sleep(1)
                        testComment = "Test Pass - Able to export waveform data in both Excel and CSV formats successfully"
                        printFP(testComment)
                        return Global.PASS, testComment

                    else:
                        testComment = "Test Fail - Export Button is not enabled. Please point to a feeder which has waveform"
                        printFP(testComment)
                        return Global.FAIL, testComment

            testComment = "Test Fail - Export Button element is not found"
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Line Monitoring doesn't have any waveforms. Please point to a Site which has waveforms"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def CheckWaveformTableContent(input_file_path, tab_name=None, field_name=None, field_value=None):

    printFP('Verify Waveform table properties and its value')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonWaveforms()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has Waveform")

            if tab_name is not None and field_name is not None:
                filtereddata = WaveformFilteredDataFromTable(tab_name, field_name)
                if field_value is not None:
                    if field_value in filtereddata:
                        testComment = 'Test Pass - Given field name "%s" and field value "%s" are found successfully in Waveform Table' %(field_name,field_value)
                        printFP(testComment)
                        return Global.PASS, testComment
                    else:
                        testComment = 'Test Fail - Given field name "%s" (or) field value "%s" are not found in Waveform Table' %(field_name,field_value)
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    testComment = "Test Fail - Field value is None"
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = "Test Fail - Tab name (or) Field name is None"
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Line Monitoring doesn't have any waveforms. Please point to a site which has waveforms"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def ValidateMultipleWaveforms(input_file_path, tab_name=None, field_name=None):

    printFP('Verify multiple waveforms table properties by comparing')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonWaveforms()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has Waveform")

            if tab_name is not None and field_name is not None:
                try:
                    finddropdown = GetElement(Global.driver, By.TAG_NAME, 'single-select')
                except Exception as e:
                    print e.message
                    testComment = 'Test Fail - Unable to find multiple waveforms drop down box for given feeder'
                    printFP(testComment)
                    return Global.FAIL, testComment

                finddropdownbutton = GetElement(finddropdown, By.TAG_NAME, 'button')
                waveforms = GetElements(finddropdown, By.TAG_NAME, 'li')
                n=0
                for waveform in waveforms:
                    finddropdownbutton.click()
                    time.sleep(1)
                    selectwaveform = GetElement(waveform, By.TAG_NAME, 'span')
                    selectwaveform.click()
                    time.sleep(2)
                    filtereddata = WaveformFilteredDataFromTable(tab_name, field_name)
                    if n>0:
                        compare = cmp(tmp, filtereddata)
                        print compare
                        if compare == 0:
                            testComment = 'Test Fail - same value is displayed for given field name when select different waveforms'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    tmp = filtereddata
                    print('tmp: %s' %tmp)
                    n = n+1

                testComment = 'Test Pass - same value is not displayed for given field name when select different waveforms'
                printFP(testComment)
                return Global.PASS, testComment

            else:
                testComment = "Test Fail - Tab name (or) Field name is None"
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Line Monitoring doesn't have any waveforms. Please point to a site which has waveforms"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment


def SingleAndMultipleEventsCheck(input_file_path):

    printFP('Verify whether waveform displays based on user selection')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonWaveforms()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(7)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has Waveform")
            waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
            if waveformchartdisplaystatus == True:
                timelineframe = GetElement(Global.driver, By.CLASS_NAME, 'timeline-items')
                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                n=0
                a=0
                for findevent in findevents:
                    findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                    classname = findevents[n].get_attribute('class')

                    if not "dataitem1" in classname:
                        if "single" in classname:
                            if "active" in classname:
                                a=1
                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                JustClick(findevents[n])
                                time.sleep(5)

                        elif not "single" in classname:
                            parentelement = GetElement(findevents[n], By.XPATH, '..')
                            findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')
                            m=0
                            for findsubevent in findsubevents:
                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                parentelement = GetElement(findevents[n], By.XPATH, '..')
                                findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')
                                classname = findsubevents[m].get_attribute('class')

                                if "dataitem1" in classname:
                                    if "active" in classname:
                                        a=1
                                        JustClick(findevents[n])
                                        time.sleep(5)

                                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                        ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                        printFP('ariaexpanded when first click on event icon after closed the graph : %s' % ariaexpanded)
                                        parentelement = GetElement(findevents[n], By.XPATH, '..')
                                        findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')
                                        classname = findsubevents[m].get_attribute('class')

                                        if "dataitem1" in classname:
                                            if "active" in classname:
                                                # Need to remove double click event icon once issue is fixed AN-2347
                                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                                JustClick(findevents[n])
                                                time.sleep(2)

                                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                                parentelement = GetElement(findevents[n], By.XPATH, '..')
                                                findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')
                                                ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                                printFP('ariaexpanded after 2nd clicked event icon after closed the graph: %s' % ariaexpanded)
                                                JustClick(findsubevents[m])
                                                time.sleep(10)

                                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                        ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                        printFP('ariaexpanded after clicked subevent icon: %s' % ariaexpanded)
                                m=m+1
                        else:
                            testComment = "Test Fail - Unable to locate any single or multiple event icons from timelineframe"
                            printFP(testComment)
                            return Global.FAIL, testComment

                    n=n+1

                if a==0 or a==1:
                    printFP('Disabled all waveforms successfully')
                    x=0
                    y=0
                    x1=0
                    y1=0
                    findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                    n=0
                    for findevent in findevents:
                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                        classname = findevents[n].get_attribute('class')

                        if not "dataitem1" in classname:
                            if "single" in classname:
                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x,y).click().perform()
                                time.sleep(2)
                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                classname = findevents[n].get_attribute('class')
                                if 'active' in classname:
                                    time.sleep(10)
                                    waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                else:
                                    waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                    if waveformchartdisplaystatus == True:
                                        ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x,y).click().perform()
                                        time.sleep(2)
                                        waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                    x=15
                                    y=2
                                    ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x,y).click().perform()
                                    findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                    classname = findevents[n].get_attribute('class')
                                    if 'active' in classname:
                                        time.sleep(10)
                                        waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                    else:
                                        waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                        if waveformchartdisplaystatus == True:
                                            ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x,y).click().perform()
                                            time.sleep(2)
                                            waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                        x=1
                                        y=10
                                        ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x,y).click().perform()
                                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                        classname = findevents[n].get_attribute('class')
                                        if 'active' in classname:
                                            time.sleep(10)
                                            waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                        else:
                                            testComment = "Test Fail - Unable to click single event icon to select. Please try with other single event waveform"
                                            printFP(testComment)
                                            return Global.FAIL, testComment


                                if waveformchartdisplaystatus == False:
                                    testComment = "Test Fail - Waveform Chart is not displayed when select event icon"
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    testComment = "Test Pass - Waveform Chart is displayed when select event icon"
                                    printFP(testComment)

                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x,y).click().perform()
                                time.sleep(2)
                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                classname = findevents[n].get_attribute('class')
                                if not 'active' in classname:
                                    time.sleep(5)
                                    waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                else:
                                    testComment = "Test Fail - Unable to click single event icon to unselect"
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                                if waveformchartdisplaystatus == True:
                                    testComment = "Test Fail - Waveform Chart is still displaying when unselect event icon"
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    testComment = "Test Pass - Waveform Chart is not displayed when unselect event icon"
                                    printFP(testComment)

                            elif not "single" in classname:
                                parentelement = GetElement(findevents[n], By.XPATH, '..')
                                findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')
                                m=0
                                for findsubevent in findsubevents:
                                    findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                    parentelement = GetElement(findevents[n], By.XPATH, '..')
                                    findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')

                                    classname = findsubevents[m].get_attribute('class')

                                    if "dataitem1" in classname:

                                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                        ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                        printFP('ariaexpanded before click event icon: %s' % ariaexpanded)

                                        if 'false' in ariaexpanded:
                                            findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                            JustClick(findevents[n])
                                            time.sleep(2)
                                            findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                            ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                            printFP('ariaexpanded after first click event icon: %s' % ariaexpanded)
                                            if 'false' in ariaexpanded:
                                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                                #focusfindevents = GetElement(findevents[n], By.TAG_NAME, 'span')
                                                ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x1,y1).click().perform()
                                                #JustClick(focusfindevents)
                                                time.sleep(2)
                                                findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                                ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                                printFP('ariaexpanded after 2nd click on event icon: %s' % ariaexpanded)
                                                if 'false' in ariaexpanded:
                                                    waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                                    if waveformchartdisplaystatus == True:
                                                        ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x1,y1).click().perform()
                                                        time.sleep(2)
                                                        waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                                    x1=25
                                                    y1=1
                                                    findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                                    #focusfindevents = GetElement(findevents[n], By.TAG_NAME, 'span')
                                                    ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x1,y1).click().perform()
                                                    #JustClick(focusfindevents)
                                                    time.sleep(2)
                                                    findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                                    ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                                    printFP('ariaexpanded after 2nd click on event icon: %s' % ariaexpanded)

                                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                        parentelement = GetElement(findevents[n], By.XPATH, '..')
                                        findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')
                                        parentsubelement = GetElement(findsubevents[m], By.XPATH, '..')
                                        subelementname = parentsubelement.text.strip()
                                        printFP('subevent waveform name : %s' %subelementname)
                                        if 'true' in ariaexpanded:
                                            JustClick(findsubevents[m])
                                            time.sleep(5)
                                        else:
                                            testComment = 'Test Fail - Waveform event list is not opened to select an event from the list - %s after clicked on event icon' %subelementname
                                            printFP(testComment)
                                            return Global.FAIL, testComment

                                        waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                        if waveformchartdisplaystatus == False:
                                            testComment = "Test Fail - Waveform Chart is not displayed when select event icon from the dropdown list"
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                        else:
                                            testComment = "Test Pass - Waveform Chart is displayed when select event icon from the dropdown list"
                                            printFP(testComment)

                                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                        ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                        printFP('ariaexpanded after clicked subevent icon: %s' % ariaexpanded)

                                        if 'false' in ariaexpanded:
                                            findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                            #focusfindevents = GetElement(findevents[n], By.TAG_NAME, 'span')
                                            ActionChains(Global.driver).move_to_element_with_offset(findevents[n],x1,y1).click().perform()
                                            #JustClick(focusfindevents)
                                            time.sleep(2)
                                            findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                            ariaexpanded = findevents[n].get_attribute('aria-expanded')
                                            printFP('ariaexpanded after click on event icon to unselect: %s' % ariaexpanded)

                                        findevents = GetElements(timelineframe, By.CLASS_NAME, 'ion-alert-circled')
                                        parentelement = GetElement(findevents[n], By.XPATH, '..')
                                        findsubevents = GetElements(parentelement, By.CLASS_NAME, 'ion-alert-circled')
                                        if 'true' in ariaexpanded:
                                            JustClick(findsubevents[m])
                                            time.sleep(5)
                                        else:
                                            testComment = 'Test Fail - Waveform event list is not opened to unselect an event from the list - %s after clicked on event icon' %subelementname
                                            printFP(testComment)
                                            return Global.FAIL, testComment

                                        waveformchartdisplaystatus = GetWaveformChartDisplayStatus()
                                        if waveformchartdisplaystatus == True:
                                            testComment = "Test Fail - Waveform Chart is still displaying when unselect event icon from the dropdown list"
                                            printFP(testComment)
                                            return Global.FAIL, testComment
                                        else:
                                            testComment = "Test Pass - Waveform Chart is not displayed when unselect event icon from the dropdown list"
                                            printFP(testComment)
                                    m=m+1
                        n= n+1
                else:
                    testComment = "Test Fail - Unable to disable all showing waveforms"
                    printFP(testComment)
                    return Global.FAIL, testComment

            else:
                testComment = "Test Fail - Waveform Chart is not loaded by default. Please check it"
                printFP(testComment)
                return Global.FAIL, testComment

            testComment = "Test Pass - Waveform Chart displays based on user selection on close and event icons"
            printFP(testComment)
            return Global.PASS, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any waveforms. Please point to a site which has waveforms"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def WaveformDownloadButton(input_file_path, interval = None, timeout = None):

    printFP('Verify whether waveform is downloaded successfully when click on Download button')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonWaveforms()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has Waveform")
            downloadelement = GetElement(Global.driver, By.CLASS_NAME, 'noborder')
            downloadbutton = GetElement(downloadelement, By.TAG_NAME, 'button')
            classname = downloadbutton.get_attribute('class')
            if not 'hide' in classname:
                try:
                    ClickButton(Global.driver, By.XPATH, xpaths['waveform_download_button'])
                except Exception as e:
                    print e.message
                    testComment = "Test Fail - Unable to click waveform download button. Please check"
                    printFP(testComment)
                    return Global.FAIL, testComment

                try:
                    inprogress = GetElement(Global.driver, By.CLASS_NAME, 'noborder')
                    progresstext = inprogress.text.strip()
                    printFP(progresstext)
                except Exception as e:
                    progresstext = 'Unable to find waveform download progress message'
                    printFP(progresstext)
                    print e.message

                if not 'data download are in progress' in progresstext:
                    try:
                        errcheck = GetElement(Global.driver, By.CLASS_NAME, 'modal-dialog')
                        getheadertext = GetText(errcheck, By.TAG_NAME, 'h4')
                    except Exception as e:
                        print e.message
                        getheadertext = False
                    if getheadertext:
                        if 'Oops' in getheadertext or 'Request Failed' in getheadertext :
                            try:
                                errmessage = GetText(errcheck, By.TAG_NAME, 'p')
                            except Exception as e:
                                errmessage = 'Its blank dialog window'
                                print e.message
                            ClickButton(errcheck, By.TAG_NAME, 'button')
                            time.sleep(1)
                            testComment = 'Test Fail - Error dialog is displayed : %s' % errmessage
                            printFP(testComment)
                            return Global.FAIL, testComment

                if timeout and interval is not None:
                    elapsed = 0
                    printFP('Waiting for waveforms to get downloaded . . .')
                    while elapsed < timeout:
                        time.sleep(interval)
                        elapsed += interval
                        print elapsed
                        downloadelement = GetElement(Global.driver, By.CLASS_NAME, 'noborder')
                        downloadbutton = GetElement(downloadelement, By.TAG_NAME, 'button')
                        classname = downloadbutton.get_attribute('class')
                        if not 'hide' in classname:
                            printFP('Waveform is still downloading')
                        elif 'hide' in classname:
                            testComment = "Test Pass - Waveform Chart is downloaded successfully and displayed for given site"
                            printFP(testComment)
                            return Global.PASS, testComment
                        else:
                            testComment = "Test Fail - Unable to get Waveform display status"
                            printFP(testComment)
                            return Global.FAIL, testComment

                    testComment = "Test Fail - Waveform Chart is not downloaded within timeout range"
                    printFP(testComment)
                    return Global.FAIL, testComment

            else:
                testComment = "Test Fail - Waveform Chart is already downloaded for given site"
                printFP(testComment)
                return Global.FAIL, testComment

        else:
            testComment = "Test Fail - Line Monitoring doesn't have any waveforms. Please point to a site which has waveforms"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def WaveformChartLegendUnitfilters(input_file_path):

    printFP('Verifying Waveform Screen Unit Filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonWaveforms()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has Waveform data")


            Waveformchart = GetElement(Global.driver, By.CLASS_NAME, 'chart-container')
            legend = GetElement(Waveformchart, By.CLASS_NAME, 'highcharts-legend')
            legendunitfilters = GetElements(legend, By.CLASS_NAME, 'highcharts-legend-item')

            for filter in legendunitfilters:
                filtername = filter.text
                if 'Current' in filtername or 'E-field' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnWaveformGraph(testunit)
                    if unitdisplaystatus:
                            printFP('"%s" points are displaying on waveform chart' %testunit)
                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnWaveformGraph(testunit)
                            if unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are still displaying on waveform chart when unselect chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are not displayed on waveform chart when unselect chart legend unit filter'
                                printFP(testComment)

                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnWaveformGraph(testunit)
                            if not unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are not displayed on waveform chart when select chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are displayed on waveform chart when select chart legend unit filter'
                                printFP(testComment)

                    elif not unitdisplaystatus:
                            printFP('"%s" points are not displayed on waveform chart' %testunit)
                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnWaveformGraph(testunit)
                            if not unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are not displayed on waveform chart when select chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are displayed on waveform chart when select chart legend unit filter'
                                printFP(testComment)

                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnWaveformGraph(testunit)
                            if unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are still displaying on waveform chart when unselect chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are not displayed on waveform chart when unselect chart legend unit filter'
                                printFP(testComment)

                else:
                    testComment = 'Unit filter "' + testunit + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment

            for filter in legendunitfilters:
                filtername = filter.text
                if 'Current' in filtername or 'E-field' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnWaveformGraph(testunit)
                    if unitdisplaystatus:
                        printFP('"%s" points are displayed on waveform chart. so unchecking' %testunit)
                        try:
                            button = GetElement(filter, By.TAG_NAME, 'text')
                            JustClick(button)
                            time.sleep(2)
                        except:
                            testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                            printFP(testComment)
                            return Global.FAIL, testComment

            currentdisplaystatus = GetUnitStatusOnWaveformGraph('Current')
            efielddisplaystatus = GetUnitStatusOnWaveformGraph('E-field')

            if not currentdisplaystatus and not efielddisplaystatus:
                testComment = 'Test Pass - Both Current and E-field Values are not displayed on waveform chart when unselect both current and E-field chart legend unit filters'
                printFP(testComment)
            else:
                testComment = 'Test Fail - Both (or) Any one of - Current and E-field Values are still displaying on waveform chart when unselect both current and E-field chart legend unit filters'
                printFP(testComment)
                return Global.FAIL, testComment

            for filter in legendunitfilters:
                filtername = filter.text
                if 'Current' in filtername or 'E-field' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnWaveformGraph(testunit)
                    if not unitdisplaystatus:
                        printFP('"%s" points are not displayed on waveform chart. so enabling' %testunit)
                        try:
                            button = GetElement(filter, By.TAG_NAME, 'text')
                            JustClick(button)
                            time.sleep(2)
                        except:
                            testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                            printFP(testComment)
                            return Global.FAIL, testComment

            currentdisplaystatus = GetUnitStatusOnWaveformGraph('Current')
            efielddisplaystatus = GetUnitStatusOnWaveformGraph('E-field')

            if currentdisplaystatus and efielddisplaystatus:
                testComment = 'Test Pass - Both Current and E-field Values are displayed on waveform chart when select both current and E-field chart legend unit filters'
                printFP(testComment)
            else:
                testComment = 'Test Fail - Both (or) Any one of - Current and E-field Values are not displayed on waveform chart when select both current and E-field chart legend unit filters'
                printFP(testComment)
                return Global.FAIL, testComment

            testComment = 'Test Pass - Verified waveform chart legend unit filters Current and E-field successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = "Test Fail - Given site doesn't have any waveform data. Please point to a site which has waveform data points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def LogIEmptyData(input_file_path):

    printFP('Verifying LogI empty data')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonLogI()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(10)

    if getfeeder:
        nodataavailableFeeder = NoDataAvailable('line-monitoring')
        if nodataavailableFeeder == "No Data Available":
            testComment = 'Test Pass - Found "No Data Available" Text for Feeder'
            printFP(testComment)

            GetSiteFromTop(region, substation, feeder, site)
            nodataavailableSite = NoDataAvailable('line-monitoring')
            if nodataavailableSite == "No Data Available":
                testComment = 'Test Pass - Found "No Data Available" Text for Both Feeder and Site'
                printFP(testComment)
                return Global.PASS, testComment
            else:
                testComment = 'Test Fail - Not Found "No Data Available" Text for Site'
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = 'Test Fail - Not Found "No Data Available" Text for Feeder'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment


def LogIExportButton(input_file_path):

    printFP('Verifying LogI Screen Export button')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonLogI()

    getfeeder = GetFeederFromTop(region, substation, feeder)

    time.sleep(10)

    if getfeeder:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
        #Get export button elements
            exportbuttonelements = GetElements(Global.driver, By.CLASS_NAME, 'dropdown-toggle')

            # find export toggle dorpdown button
            for exportbuttonelement in exportbuttonelements:
                exportbuttonelementname = exportbuttonelement.text
                if 'Export' in exportbuttonelementname:
                    try:
                        isdisabled = exportbuttonelement.get_attribute('disabled')
                    except Exception as e:
                        print e.message

                    if isdisabled is None:
                        try:
                            time.sleep(2)
                            exportbuttonelement.click()
                        except Exception as e:
                            printFP(e.message)
                            printFP('Test Fail - Unable to click Export Button')
                            break

                        exportdropdownframe = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-menu-form')
                        exportdropdownlists = GetElements(exportdropdownframe, By.TAG_NAME, 'li')
                        excelStatus = False
                        for exportdropdownlist in exportdropdownlists:
                            if not excelStatus:
                                formattype = exportdropdownlist.text
                                printFP('formattype %s' %formattype)

                                if 'EXCEL' in formattype:
                                    try:
                                        ClickButton(Global.driver, By.XPATH, xpaths['logi_export_excel_button'])
                                        time.sleep(5)

                                        try:
                                            Global.driver.switch_to_window(Global.driver.window_handles[-1])
                                            cancelbutton = Global.driver.find_element_by_xpath(u'//input[@value="Cancel"]')
                                            cancelbutton.click()
                                            time.sleep(1)
                                            Global.driver.switch_to_default_content()
                                        except Exception as e:
                                            printFP(e.message)

                                        testComment = "Test Pass - Able to export logi data points in excel format"
                                        printFP(testComment)
                                        excelStatus = True

                                    except:
                                        testComment = 'Test Fail - Unable to click "Excel" export option in logi screen'
                                        return Global.FAIL, testComment
                    else:
                        printFP(testComment)
                        testComment = "Test Fail - Export Button is not enabled. Please point to a feeder which has logi data"
                        return Global.FAIL, testComment

                    if isdisabled is None:
                        try:
                            time.sleep(2)
                            exportbuttonelement.click()
                        except Exception as e:
                            printFP(e.message)
                            printFP('Test Fail - Unable to click Export Button')
                            break

                        exportdropdownframe = GetElement(Global.driver, By.CLASS_NAME, 'dropdown-menu-form')
                        exportdropdownlists = GetElements(exportdropdownframe, By.TAG_NAME, 'li')
                        csvStatus = False
                        for exportdropdownlist in exportdropdownlists:
                            if not csvStatus:
                                formattype = exportdropdownlist.text
                                printFP('formattype %s' %formattype)

                                if 'CSV' in formattype:
                                    try:
                                        ClickButton(Global.driver, By.XPATH, xpaths['logi_export_csv_button'])
                                        time.sleep(5)

                                        try:
                                            Global.driver.switch_to_window(Global.driver.window_handles[-1])
                                            title = Global.driver.title
                                        except Exception as e:
                                            printFP(e.message)

                                        testComment = "Test Pass - Able to export logi data points in CSV format"
                                        printFP(testComment)
                                        csvStatus = True

                                    except:
                                        testComment = 'Test Fail - Unable to click "CSV" export option in logi screen'
                                        printFP(testComment)
                                        return Global.FAIL, testComment

                        time.sleep(1)
                        testComment = "Test Pass - Able to export logi data points in both Excel and CSV formats successfully"
                        printFP(testComment)
                        return Global.PASS, testComment

                    else:
                        printFP(testComment)
                        testComment = "Test Fail - Export Button is not enabled. Please point to a feeder which has logi"
                        return Global.FAIL, testComment


            testComment = "Test Fail - Export Button element is not found"
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = "Test Fail - Given feeder doesn't have any logi data points. Please point to a feeder which has logi data points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment


def LogIUnitfilters(input_file_path):

    printFP('Verifying LogI Screen Unit Filters button')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonLogI()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(10)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has LogI data")

            #Get all unit filters button elements
            unitfilters = GetElement(Global.driver, By.TAG_NAME, 'unit-filter')
            filters = GetElements(unitfilters, By.TAG_NAME, 'label')
            for filter in filters:
                filtername = filter.text
                if 'Current' in filtername or 'Temperature' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                    if unitdisplaystatus:
                            printFP('"%s" points are displaying on LogI chart by default' %testunit)
                            try:
                                JustClick(filter)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are still displaying on LogI chart when unselect unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are not displayed on LogI chart when unselect unit filter'
                                printFP(testComment)

                            try:
                                JustClick(filter)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if not unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are not displayed on LogI chart when select unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are displayed on LogI chart when select unit filter'
                                printFP(testComment)

                    elif not unitdisplaystatus:
                            printFP('"%s" points are not displayed on LogI chart by default' %testunit)
                            try:
                                JustClick(filter)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if not unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are not displayed on LogI chart when select unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are displayed on LogI chart when select unit filter'
                                printFP(testComment)

                            try:
                                JustClick(filter)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are still displaying on LogI chart when unselect unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are not displayed on LogI chart when unselect unit filter'
                                printFP(testComment)

                else:
                    testComment = 'Unit filter "' + testunit + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment

            for filter in filters:
                filtername = filter.text
                if 'Current' in filtername or 'Temperature' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                    if unitdisplaystatus:
                        printFP('"%s" points are displayed on LogI chart by default. so unchecking' %testunit)
                        try:
                            JustClick(filter)
                            time.sleep(2)
                        except:
                            testComment = 'Test Fail - Unable to click "%s" unit filter' %testunit
                            printFP(testComment)
                            return Global.FAIL, testComment

            currentdisplaystatus = GetUnitStatusOnLogIGraph('Current')
            tempdisplaystatus = GetUnitStatusOnLogIGraph('Temperature')

            if not currentdisplaystatus and not tempdisplaystatus:
                testComment = 'Test Pass - Both Current and Temperature Values are not displayed on LogI chart when unselect both current and temperature unit filters'
                printFP(testComment)
            else:
                testComment = 'Test Fail - Both (or) Any one of - Current and Temperature Values are still displaying on LogI chart when unselect both current and temperature unit filters'
                printFP(testComment)
                return Global.FAIL, testComment

            for filter in filters:
                filtername = filter.text
                if 'Current' in filtername or 'Temperature' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                    if not unitdisplaystatus:
                        printFP('"%s" points are not displayed on LogI chart by default. so enabling' %testunit)
                        try:
                            JustClick(filter)
                            time.sleep(2)
                        except:
                            testComment = 'Test Fail - Unable to click "%s" unit filter' %testunit
                            printFP(testComment)
                            return Global.FAIL, testComment

            currentdisplaystatus = GetUnitStatusOnLogIGraph('Current')
            tempdisplaystatus = GetUnitStatusOnLogIGraph('Temperature')

            if currentdisplaystatus and tempdisplaystatus:
                testComment = 'Test Pass - Both Current and Temperature Values are displayed on LogI chart when select both current and temperature unit filters'
                printFP(testComment)
            else:
                testComment = 'Test Fail - Both (or) Any one of - Current and Temperature Values are not displayed on LogI chart when select both current and temperature unit filters'
                printFP(testComment)
                return Global.FAIL, testComment

            testComment = 'Test Pass - Verified logi unit filters Current and Temperature successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = "Test Fail - Given site doesn't have any logi data points. Please point to a site which has logi data points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment

def LogIChartLegendUnitfilters(input_file_path):

    printFP('Verifying LogI Screen Unit Filters button')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonLogI()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has LogI data")

            #Get all unit filters button elements
            unitfilters = GetElement(Global.driver, By.TAG_NAME, 'unit-filter')
            filters = GetElements(unitfilters, By.TAG_NAME, 'label')

            for filter in filters:
                filtername = filter.text
                if 'Current' in filtername or 'Temperature' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                    if not unitdisplaystatus:
                        printFP('"%s" points are not displayed on LogI chart by default. so enabling' %testunit)
                        try:
                            JustClick(filter)
                            time.sleep(2)
                        except:
                            testComment = 'Test Fail - Unable to click "%s" unit filter' %testunit
                            printFP(testComment)
                            return Global.FAIL, testComment

            currentdisplaystatus = GetUnitStatusOnLogIGraph('Current')
            tempdisplaystatus = GetUnitStatusOnLogIGraph('Temperature')

            if currentdisplaystatus and tempdisplaystatus:
                testComment = 'Test Pass - Both Current and Temperature Values are displayed on LogI chart when select both current and temperature unit filters'
                printFP(testComment)
            else:
                testComment = 'Test Fail - Both (or) Any one of - Current and Temperature Values are not displayed on LogI chart when select both current and temperature unit filters'
                printFP(testComment)
                return Global.FAIL, testComment

            logichart = GetElement(Global.driver, By.TAG_NAME, 'stock-chart')
            legend = GetElement(logichart, By.CLASS_NAME, 'highcharts-legend')
            legendunitfilters = GetElements(legend, By.CLASS_NAME, 'highcharts-legend-item')

            for filter in legendunitfilters:
                filtername = filter.text
                if 'Current' in filtername or 'Temperature' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                    if unitdisplaystatus:
                            printFP('"%s" points are displaying on LogI chart' %testunit)
                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are still displaying on LogI chart when unselect chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are not displayed on LogI chart when unselect chart legend unit filter'
                                printFP(testComment)

                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if not unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are not displayed on LogI chart when select chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are displayed on LogI chart when select chart legend unit filter'
                                printFP(testComment)

                    elif not unitdisplaystatus:
                            printFP('"%s" points are not displayed on LogI chart' %testunit)
                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if not unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are not displayed on LogI chart when select chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are displayed on LogI chart when select chart legend unit filter'
                                printFP(testComment)

                            try:
                                button = GetElement(filter, By.TAG_NAME, 'text')
                                JustClick(button)
                                time.sleep(2)
                            except:
                                testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                                printFP(testComment)
                                return Global.FAIL, testComment

                            unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                            if unitdisplaystatus:
                                testComment = 'Test Fail - '+ testunit +' Values are still displaying on LogI chart when unselect chart legend unit filter'
                                printFP(testComment)
                                return Global.FAIL, testComment
                            else:
                                testComment = 'Test Pass - '+ testunit +' Values are not displayed on LogI chart when unselect chart legend unit filter'
                                printFP(testComment)

                else:
                    testComment = 'Unit filter "' + testunit + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment

            for filter in legendunitfilters:
                filtername = filter.text
                if 'Current' in filtername or 'Temperature' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                    if unitdisplaystatus:
                        printFP('"%s" points are displayed on LogI chart. so unchecking' %testunit)
                        try:
                            button = GetElement(filter, By.TAG_NAME, 'text')
                            JustClick(button)
                            time.sleep(2)
                        except:
                            testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                            printFP(testComment)
                            return Global.FAIL, testComment

            currentdisplaystatus = GetUnitStatusOnLogIGraph('Current')
            tempdisplaystatus = GetUnitStatusOnLogIGraph('Temperature')

            if not currentdisplaystatus and not tempdisplaystatus:
                testComment = 'Test Pass - Both Current and Temperature Values are not displayed on LogI chart when unselect both current and temperature chart legend unit filters'
                printFP(testComment)
            else:
                testComment = 'Test Fail - Both (or) Any one of - Current and Temperature Values are still displaying on LogI chart when unselect both current and temperature chart legend unit filters'
                printFP(testComment)
                return Global.FAIL, testComment

            for filter in legendunitfilters:
                filtername = filter.text
                if 'Current' in filtername or 'Temperature' in filtername:
                    testunit = filtername
                    unitdisplaystatus = GetUnitStatusOnLogIGraph(testunit)
                    if not unitdisplaystatus:
                        printFP('"%s" points are not displayed on LogI chart. so enabling' %testunit)
                        try:
                            button = GetElement(filter, By.TAG_NAME, 'text')
                            JustClick(button)
                            time.sleep(2)
                        except:
                            testComment = 'Test Fail - Unable to click "%s" chart legend unit filter' %testunit
                            printFP(testComment)
                            return Global.FAIL, testComment

            currentdisplaystatus = GetUnitStatusOnLogIGraph('Current')
            tempdisplaystatus = GetUnitStatusOnLogIGraph('Temperature')

            if currentdisplaystatus and tempdisplaystatus:
                testComment = 'Test Pass - Both Current and Temperature Values are displayed on LogI chart when select both current and temperature chart legend unit filters'
                printFP(testComment)
            else:
                testComment = 'Test Fail - Both (or) Any one of - Current and Temperature Values are not displayed on LogI chart when select both current and temperature chart legend unit filters'
                printFP(testComment)
                return Global.FAIL, testComment

            testComment = 'Test Pass - Verified logi chart legend unit filters Current and Temperature successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = "Test Fail - Given site doesn't have any logi data points. Please point to a site which has logi data points"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def LogIPhaseDetailsCheck(input_file_path, phase=None, propertyname=None, propertyvalue=None):

    printFP('Verifying LogI Screen Phase Filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonLogI()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(5)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has logi data")
            if phase is not None and propertyname is not None:
                filtereddata = LogiFilteredDataFromTable('line-monitoring', phase, propertyname)
                if propertyvalue is not None:
                    if propertyvalue in filtereddata:
                        testComment = 'Test Pass - Given property name "%s" and property value "%s" are found successfully in logi Phase details table' %(propertyname,propertyvalue)
                        printFP(testComment)
                        return Global.PASS, testComment
                    else:
                        testComment = 'Test Fail - Given property name "%s" (or) property value "%s" are not found in logi Phase details table' %(propertyname,propertyvalue)
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    testComment = "Test Fail - Property value is None"
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = "Test Fail - phase (or) property name is None"
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


def LogIPhaseFilters(input_file_path):

    printFP('Verifying Logi Screen Phase Filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    pagename = 'line-monitoring'
    rowname = 'Type'

    GoToLineMon()
    GoToLineMonLogI()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(10)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given Feeder has Logi data")

            #Get all filter button elements
            phasebuttonelement = GetElement(Global.driver, By.TAG_NAME, 'phase-filter')
            time.sleep(1)
            phasefilters = GetElements(phasebuttonelement, By.TAG_NAME, 'label')
            time.sleep(2)
            for phasefilter in phasefilters:
                phasefiltername = phasefilter.text
                testphase =  phasefiltername
                if phasefiltername in ('A','B','C'):
                    buttonclassname = phasefilter.get_attribute('class')
                    filteredphasedata = LogiFilteredDataFromTable(pagename, testphase, rowname)
                    filteredphasedata = map(str, filteredphasedata)
                    if not filteredphasedata == [''] or filteredphasedata == []:
                        printFP('"Phase '+ testphase +'" data are available for selected site')
                        if "active" in buttonclassname:
                            phasedisplaystatus = GetPhaseStatusOnLogIGraph(testphase)
                            if phasedisplaystatus:
                                printFP('"Phase '+ testphase +'" data are displaying on Logi chart when selected by default')

                                try:
                                    phasefilter.click()
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                phasedisplaystatus = GetPhaseStatusOnLogIGraph(testphase)
                                if not phasedisplaystatus:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are not displayed on Logi chart when unselect Phase filter "' + testphase + '"'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are still displaying on Logi chart when unselect Phase filter "' + testphase + '"'
                                    printFP(testComment)
                                    return Global.FAIL, testComment

                                try:
                                    phasefilter.click()
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                phasedisplaystatus = GetPhaseStatusOnLogIGraph(testphase)
                                if not phasedisplaystatus:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed on Logi chart when select Phase filter "' + testphase + '" again'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are displayed on Logi chart when select Phase filter "' + testphase + '" again'
                                    printFP(testComment)

                        elif not "active" in buttonclassname:
                            phasedisplaystatus = GetPhaseStatusOnLogIGraph(testphase)
                            if phasedisplaystatus:
                                printFP('"Phase '+ testphase +'" data are not displayed on Logi chart when unselected by default')

                                try:
                                    phasefilter.click()
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                phasedisplaystatus = GetPhaseStatusOnLogIGraph(testphase)
                                if not phasedisplaystatus:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are not displayed on Logi chart when select Phase filter "' + testphase + '"'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                else:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are displayed on Logi chart when select Phase filter "' + testphase + '"'
                                    printFP(testComment)

                                try:
                                    phasefilter.click()
                                    time.sleep(1)
                                except:
                                    testComment = 'Test Fail - Unable to click "'+ testphase +'" Phase filter'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                                phasedisplaystatus = GetPhaseStatusOnLogIGraph(testphase)
                                if not phasedisplaystatus:
                                    testComment = 'Test Pass - "Phase '+ testphase +'" data are not displayed on Logi chart when unselect Phase filter "' + testphase + '" again'
                                    printFP(testComment)
                                else:
                                    testComment = 'Test Fail - "Phase '+ testphase +'" data are still displaying on Logi chart when unselect Phase filter "' + testphase + '" again'
                                    printFP(testComment)
                                    return Global.FAIL, testComment
                        else:
                            printFP('Unable to find whether Phase "' + testphase + '" button is enabled or not')
                    else:
                        printFP('"Phase '+ testphase +'" data are not available for selected site')

                else:
                    testComment = 'Test Fail - Phase filter "' + testphase + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment

            testComment = 'Test Pass - Verified LogI phasefilters successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            printFP("Test Fail - Given site doesn't have logi data. Please point to a site which has logi data")
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def LogITimeRangeSelection(input_file_path):

    printFP('Verifying Logi Screen timerange Filters')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    pagename = 'line-monitoring'

    GoToLineMon()
    GoToLineMonLogI()

    getsite = GetSiteFromTop(region, substation, feeder, site)

    time.sleep(10)

    if getsite:
        nodataavailable = NoDataAvailable('line-monitoring')
        if not nodataavailable == "No Data Available":
            printFP("Given site has Logi data")

            #Get all time range button elements
            timerangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
            time.sleep(1)
            timerangefilters = GetElements(timerangeframe, By.TAG_NAME, 'label')
            time.sleep(1)
            n=0
            for timerangefilter in timerangefilters:
                timerangefiltername = timerangefilter.text
                testtimerange =  timerangefiltername
                if timerangefiltername in ('1D','1W','1M', '3M', '6M', '1Y'):
                    buttonclassname = timerangefilter.get_attribute('class')
                    if "active" in buttonclassname:
                        printFP('"Selected Time Range '+ testtimerange +'" button is already selected by default')
                        rangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
                        rangefilters = GetElements(rangeframe, By.TAG_NAME, 'label')
                        m=n
                        m=m+1
                        try:
                            rangefilters[m].click()
                            time.sleep(5)
                            rangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
                            rangefilters = GetElements(rangeframe, By.TAG_NAME, 'label')
                            rangefilters[n].click()
                            time.sleep(5)
                        except:
                            testComment = 'Test Fail - Unable to click "'+ testtimerange +'" Time Range filter'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        timerangebuttonstatus = GetTimeRangeButtonStatus(testtimerange)
                        if timerangebuttonstatus:
                            testComment = 'Test Pass - "Selected Time Range '+ testtimerange +'" button got activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                        else:
                            testComment = 'Test Fail - "Time Range '+ testtimerange +'" button is still not activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                            return Global.FAIL, testComment

                    elif not "active" in buttonclassname:
                        try:
                            timerangefilter.click()
                            time.sleep(5)
                        except:
                            testComment = 'Test Fail - Unable to click "'+ testtimerange +'" Time Range filter'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        timerangebuttonstatus = GetTimeRangeButtonStatus(testtimerange)
                        if timerangebuttonstatus:
                            testComment = 'Test Pass - "Selected Time Range '+ testtimerange +'" button got activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                        else:
                            testComment = 'Test Fail - "Time Range '+ testtimerange +'" button is still not activated when select Time Range filter "' + testtimerange + '"'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    else:
                        printFP('Unable to find whether Time Range "' + testtimerange + '" button is enabled or not')
                else:
                    testComment = 'Test Fail - Time Range filter "' + testtimerange + '" is not in the defined list'
                    printFP(testComment)
                    return Global.FAIL, testComment
                n=n+1

            testComment = 'Test Pass - Verified LogI Time Range filters successfully and all test cases are PASS'
            printFP(testComment)
            return Global.PASS, testComment
        else:
            testComment = "Test Fail - Given site doesn't have logi data. Please point to a site which has logi data"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site "%s"' %site
        printFP(testComment)
        return Global.FAIL, testComment


def LogISiteSelection(input_file_path):

    printFP('Verifying Logi multiple site selection')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site1 = params['Site1']
    site2 = params['Site2']

    pagename = 'line-monitoring'

    GoToLineMon()
    GoToLineMonLogI()

    getsite1 = GetSiteFromTop(region, substation, feeder, site1)
    time.sleep(10)
    if getsite1:
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP('Given site 1 "%s" has logi data' %site1)
        else:
            testComment = "Test Fail - Given site 1 doesn't have logi data. Please point to a site which has logi data"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site 1 "%s"' %site1
        printFP(testComment)
        return Global.FAIL, testComment

    getsite2 = GetSiteFromTop(region, substation, feeder, site2)
    time.sleep(10)
    if getsite2:
        nodataavailable = NoDataAvailable(pagename)
        if not nodataavailable == "No Data Available":
            printFP('Given site 2 "%s" has logi data' %site2)
        else:
            testComment = "Test Fail - Given site 2 doesn't have logi data. Please point to a site which has logi data"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given site 2 "%s"' %site2
        printFP(testComment)
        return Global.FAIL, testComment

    getfeeder = GetFeederFromTop(region, substation, feeder)
    time.sleep(5)

    if getfeeder:
        finddropdown = GetElement(Global.driver, By.XPATH, '//span[contains(text(),"Selected sites")]/../span[2]/div')
        dropdownbutton = GetElement(finddropdown, By.TAG_NAME, 'button')
        dropdowndisplay = dropdownbutton.text
        try:
            dropdownbutton.click()
            time.sleep(1)
        except:
            testComment = 'Test Fail - Unable to click "site drop down button" - ' + dropdowndisplay
            printFP(testComment)
            return Global.FAIL, testComment
        time.sleep(1)
        dropdownlist = GetElement(finddropdown, By.TAG_NAME, 'ul')
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            raw_filtername = option.text
            filtername = raw_filtername.replace(' ','').replace('"','')
            printFP('filtername: %s' %filtername)
            if filtername == "CheckAll":
                try:
                    option.click()
                    time.sleep(1)
                except:
                    testComment = 'Test Fail - Unable to click "' + filtername + '" filter'
                    printFP(testComment)
                    return Global.FAIL, testComment
                time.sleep(1)
                headerofsite1chart = GetHeadersOfLogiCharts(site1)
                headerofsite2chart = GetHeadersOfLogiCharts(site2)
                if not headerofsite1chart:
                    testComment = 'Test Fail - "' + site1 + '" logi chart is not displayed when select "Check All" filter'
                    printFP(testComment)
                    return Global.FAIL, testComment
                elif not headerofsite2chart:
                    testComment = 'Test Fail - "' + site2 + '" logi chart is not displayed when select "Check All" filter'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Both "' + site1 + '" and "' + site2 + '" logi chart are displayed when select "Check All" filter'
                    printFP(testComment)

            elif filtername == "UncheckAll":
                try:
                    option.click()
                    time.sleep(1)
                except:
                    testComment = 'Test Fail - Unable to click "' + filtername + '" filter'
                    printFP(testComment)
                    return Global.FAIL, testComment
                time.sleep(1)
                headerofsite1chart = GetHeadersOfLogiCharts(site1)
                headerofsite2chart = GetHeadersOfLogiCharts(site2)
                if headerofsite1chart:
                    testComment = 'Test Fail - "' + site1 + '" logi chart is still displaying when select "Uncheck All" filter'
                    printFP(testComment)
                    return Global.FAIL, testComment
                elif headerofsite2chart:
                    testComment = 'Test Fail - "' + site2 + '" logi chart is still displaying when select "Uncheck All" filter'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    testComment = 'Test Pass - Both "' + site1 + '" and "' + site2 + '" logi chart are not displayed when select "Uncheck All" filter'
                    printFP(testComment)

            else:

                try:
                    currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                    classname = currentbuttonstatus.get_attribute('class')
                except Exception as e:
                    classname = None
                    print e.message

                print classname

                if classname is not None:
                    if "glyphicon-ok" in classname:
                        headerofchart = GetHeadersOfLogiCharts(raw_filtername)
                        if not headerofchart:
                            testComment = 'Test Fail - "' + raw_filtername + '" logi chart is not displayed when it selected by default'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        else:
                            testComment = 'Test Pass - "' + raw_filtername + '" logi chart is displayed when it selected by default'
                            printFP(testComment)

                        try:
                            option.click()
                            time.sleep(1)
                        except:
                            testComment = 'Test Fail - Unable to click "'+raw_filtername+'" filter'
                            printFP(testComment)
                            return Global.FAIL, testComment

                        headerofchart = GetHeadersOfLogiCharts(raw_filtername)
                        if headerofchart:
                            testComment = 'Test Fail - "' + raw_filtername + '" logi chart is still displaying when unselected'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        else:
                            testComment = 'Test Pass - "' + raw_filtername + '" logi chart is not displayed when unselected'
                            printFP(testComment)
                    else:
                        try:
                            option.click()
                            time.sleep(1)
                        except:
                            testComment = 'Test Fail - Unable to click "'+raw_filtername+'" filter'
                            printFP(testComment)
                            return Global.FAIL, testComment

                        headerofchart = GetHeadersOfLogiCharts(raw_filtername)
                        if not headerofchart:
                            testComment = 'Test Fail - "' + raw_filtername + '" logi chart is not displayed when selected'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        else:
                            testComment = 'Test Pass - "' + raw_filtername + '" logi chart is displayed when selected'
                            printFP(testComment)

                        try:
                            option.click()
                            time.sleep(1)
                        except:
                            testComment = 'Test Fail - Unable to click "'+raw_filtername+'" filter'
                            printFP(testComment)
                            return Global.FAIL, testComment

                        headerofchart = GetHeadersOfLogiCharts(raw_filtername)
                        if headerofchart:
                            testComment = 'Test Fail - "' + raw_filtername + '" logi chart is still displaying when unselected again'
                            printFP(testComment)
                            return Global.FAIL, testComment
                        else:
                            testComment = 'Test Pass - "' + raw_filtername + '" logi chart is not displayed when unselected again'
                            printFP(testComment)

        testComment = 'Test Pass - Verified LogI site selection filters successfully and all test cases are PASS'
        printFP(testComment)
        return Global.PASS, testComment

    else:
        testComment = 'Test Fail - Unable to locate Given feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment

def CustomGroupsMultipleEventTypeSelectionSupport():
    printFP('INFO - Going to Line Monitoring screen')
    GoToLineMon()
    time.sleep(2)
    printFP('INFO - Clicking on the custom group')
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-2"]')
    if rootElement.get_attribute('collapsed') == 'true':
        rootElement.click()
        time.sleep(2)

    feeder_with_fault = GetElement(Global.driver, By.XPATH, "//span[contains(@title,'Feeders with Faults')]")
    feeder_with_fault.click()
    time.sleep(2)


    fault_type = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'multiselect-parent btn-group dropdown-multiselect')]/button[1]")
    fault_type.click()
    time.sleep(2)
    #Selecting show all from the drop down
    show_all = GetElement(Global.driver, By.XPATH, "//*[@id='deselectAll']").click()
    #SelectFromMenu(Global.driver, By.CLASS_NAME, 'option', 'Fault Without Interruption')
    time.sleep(2)
    fault_type.click()
    time.sleep(2)

    table = GetElement(Global.driver, By.TAG_NAME, 'table')
    dev_head = GetElement(table, By.TAG_NAME, "thead")
    details = GetElements(dev_head, By.TAG_NAME, 'tr')

    column_header = GetTableColumnOrder('line-monitoring')
    print column_header

    if 'Fault Type' in column_header:
        printFP('INFO - Expected column present on the UI table')
    else:
        testComment = 'TEST FAIL - Expected column NOT present on the UI table'
        printFP(testComment)
        return Global.FAIL, testComment

    devtbody = GetElement(table, By.TAG_NAME, "tbody")
    deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
    fault_type_from_table = []
    for row in deviceslist:
        devicedetails = GetElement(row, By.XPATH, "//td[4]")
        fault_type_ui = devicedetails.text
        fault_type_from_table.append(fault_type_ui)
    print fault_type_from_table

    if 'Fault Without Interruption' in fault_type_from_table:
        testComment = 'TEST PASS - Expected fault event present in the table and Fault Type column present'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'TEST FAIL - Expected fault event Not present'
        printFP(testComment)
        return Global.FAIL, testComment

def CustomGroupsOrderingOfTableColumns():
    printFP('INFO - Going to Line Monitoring screen')
    GoToLineMon()
    time.sleep(2)
    printFP('INFO - Clicking on the custom group')
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-2"]')
    if rootElement.get_attribute('collapsed') == 'true':
        rootElement.click()
        time.sleep(2)
    printFP('INFO - Clicking on the Active Faults')
    active_faults = GetElement(Global.driver, By.XPATH, '//*[@id="node-2-Active_Faults"]/div[2]/span[3]').click()
    time.sleep(2)
    column_header = GetTableColumnOrder('line-monitoring')
    print column_header


    if column_header['Region'] == 1 and column_header['Substation'] == 2 and column_header['Feeder'] == 3 and column_header['Site'] == 4:
        testComment = 'TEST PASS - Ordering of table columns is as expected'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'TEST FAIL - Ordering of table columns is NOT as expected'
        printFP(testComment)
        return Global.FAIL, testComment

def ExportCustomGroupsTablesWithMultipleEventTypeSelection():
    printFP('INFO - Going to Line Monitoring screen')
    GoToLineMon()
    time.sleep(2)
    printFP('INFO - Clicking on the custom group')
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-2"]')
    if rootElement.get_attribute('collapsed') == 'true':
        rootElement.click()
        time.sleep(2)

    feeder_with_fault = GetElement(Global.driver, By.XPATH, "//span[contains(@title,'Feeders with Faults')]")
    feeder_with_fault.click()
    time.sleep(2)

    fault_type = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'multiselect-parent btn-group dropdown-multiselect')]/button[1]")
    fault_type.click()
    time.sleep(2)
    #Selecting show all from the drop down
    show_all = GetElement(Global.driver, By.XPATH, "//*[@id='deselectAll']").click()
    #SelectFromMenu(Global.driver, By.CLASS_NAME, 'option', 'Fault Without Interruption')
    time.sleep(2)
    fault_type.click()
    time.sleep(2)

    table = GetElement(Global.driver, By.TAG_NAME, 'table')
    devtbody = GetElement(table, By.TAG_NAME, "tbody")
    deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
    details_from_table = []
    for row in deviceslist:
        devicedetails = GetElements(row, By.XPATH, 'td')
        device_details_ui = devicedetails.text
        print device_details_ui
        details_from_table.append(device_details_ui)
    print details_from_table

    #Clicking on the Export button
    '''export_button = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'pull-right')]/div/span/div/button").click()
    time.sleep(1)
    excel = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'pull-right')]/div/span/div/ul/li[1]").click()
    time.sleep(2)
    export_button = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'pull-right')]/div/span/div/button").click()
    time.sleep(1)
    csv = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'pull-right')]/div/span/div/ul/li[2]").click()
    time.sleep(2)

    # Place where downloaded file exists
    location = downloadfolder + 'export.xls'
    #Opening the downloaded file and reading its content
    with open(location,'r') as f:
        content = f.read()
        downloaded_file = content.strip()
        downloaded_file = unicode(downloaded_file, "utf-8")
        downloaded_file = downloaded_file.strip('\n').replace('"','').replace(' ','')
        downloaded_file = ''.join(downloaded_file.split())
        downloaded_file = downloaded_file.strip()

    #After reading content of downloaded file, deleting the opened file
    try:
        os.remove(location)
    except OSError as e:
        printFP(e)
        return Global.FAIL, 'TEST FAIL - ' + e'''







