import Global
import os
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Utilities_Ample import *

def DeviceFilters(input_file_path=None, page=None):
    if not (input_file_path and page):
        testComment = 'Test is missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)

    # check if we should be verifying Upgrade Page or Configure page
    GoToDevMan()
    if page == 'Upgrade':
        GoToDevUpgrade()

    # Go to location specified in input_file_path
    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    # Both pages have at least these two; Upgrade has SW version as well
    #FilterNames = ["Network Group"]
    GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
    time.sleep(2)
    #for i in range(len(FilterNames)):
    GetElement(Global.driver, By.XPATH, "//span[text()='Network Group']/preceding-sibling::input").click()
    time.sleep(2)
    #GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]").click()
    #time.sleep(2)
    result = Global.PASS
    # if the page is Upgrade then it will check the SW filter button
    if page == 'Upgrade':
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
            printFP("INFO - Filter SW does not display the text Select if unselect everything.")

        swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='fwVersionSelection.list']/div/button")
        swFilterButton.click()
        time.sleep(2)


        FilterChoices = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='option in options | filter:getFilter(input.searchFilter)']")
        for n in range(len(FilterChoices)):
            FilterChoices[n].click()
            time.sleep(2)
            filterText = GetElement(FilterChoices[n], By.XPATH, 'a/span[2]/span').text
            displayedSW = GetElements(Global.driver, By.XPATH, '//td[5]/span')
            for m in range(len(displayedSW)):
                if displayedSW[m].text != filterText:
                    result = Global.FAIL
                    printFP("INFO - A displayed SW version does not match the filter applied.")
                time.sleep(5)
            FilterChoices[n].click()
            time.sleep(2)
        swFilterButton.click()
        time.sleep(2)


    # Check Comm Type Filter
    '''swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='communicationTypeSettings.list']/div/button")
    swFilterButton.click()

    GetElement(Global.driver, By.ID, 'deselectAll').click()
    GetElement(Global.driver, By.XPATH, "//span[@options='communicationTypeSettings.list']/div/button").click()
    if not ('Select' in GetElement(Global.driver, By.XPATH, "//span[@options='communicationTypeSettings.list']/div/button").text):
        result = Global.FAIL
        printFP("INFO - Filter SW does not display the text Select if unselect everything.")

    swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='communicationTypeSettings.list']/div/button")
    swFilterButton.click()
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

    swFilterButton.click()'''

    # Check Network Group Filter
    swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
    swFilterButton.click()
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
        printFP("INFO - Filter SW does not display the text Select if unselect everything.")

    swFilterButton = GetElement(Global.driver, By.XPATH, "//span[@options='networkGroupSelection.list']/div/button")
    swFilterButton.click()
    time.sleep(2)


    FilterChoices = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='option in options | filter:getFilter(input.searchFilter)']")
    for n in range(len(FilterChoices)):
        FilterChoices[n].click()
        time.sleep(2)
        filterText = GetElement(FilterChoices[n], By.XPATH, 'a/span[2]/span').text
        displayedSW = GetElements(Global.driver, By.XPATH, '//td[17]/span')
        for m in range(len(displayedSW)):
            if (displayedSW[m].text != filterText) or (filterText == '(Blanks)' and displayedSW[m].text == ''):
                result = Global.FAIL
                printFP("INFO - A displayed Network Group does not match the filter applied.")
            time.sleep(5)
        FilterChoices[n].click()
        time.sleep(2)

    swFilterButton.click()
    time.sleep(2)

    # Check if any filter checks failed.
    if result == Global.FAIL:
        testComment = 'One or more filters are not working.'
    else:
        testComment = 'All filters are working.'

    printFP("INFO - " + testComment)
    return result, 'TEST PASS - ' + testComment if result == Global.PASS else 'TEST FAIL - ' + testComment


def NavigatePages(input_file_path=None, UpgradePage=True):
    if not (input_file_path):
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)

    GoToDevMan()
    if UpgradePage:
        GoToDevUpgrade()

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    result = Global.PASS
    # Checks if there are pages to navigate
    Links = ['Next', 'Prev', 'First', 'Last']
    try:
        for i in range(len(Links)):
            GetElement(Global.driver, By.PARTIAL_LINK_TEXT, Links[i])
    except:
        maxRow = GetElement(Global.driver, By.XPATH, "//span[text()='Rows per Page']/../single-select/div/button").text
        numberOfRowsText = GetElement(Global.driver, By.XPATH, "//span[text()='Rows per Page']/../span[2]").text
        if findLargestNumber(numberOfRowsText) <= maxRow:
            testComment = "This level does not have pages to navigate through, but has an allowed amount of devices shown."
        else:
            testComment = "This level does not have pages to navigate through, but has more than the allowed number of devices."
            result = Global.FAIL

    # Gets all devices within the page and puts it in each element of page list
    page = []
    while True:
        page.append(GrabDeviceNamesOnPage())
        if 'disabled' not in GetElement(Global.driver, By.XPATH, "//div[contains(@class,'next')]").get_attribute('class'):
            GetElement(Global.driver, By.LINK_TEXT, 'Next >').click()
        else:
            break

    # Go use previous button and check if all devices match the order they were originally when passing through using next button
    for i in range(len(page) - 1, -1, -1):
        if GrabDeviceNamesOnPage() == page[i]:
            printFP("INFO - This page matches.")
        else:
            printFP("INFO - This page does not match after clicking previous.")
            result = Global.FAIL
        if not ('disabled' in GetElement(Global.driver, By.XPATH, "//div[contains(@class,'previous')]").get_attribute('class')):
            GetElement(Global.driver, By.LINK_TEXT, '< Prev').click()

    # Checks if the last button gets us to the last page by comparing the list to the last element in page
    GetElement(Global.driver, By.PARTIAL_LINK_TEXT, 'Last').click()
    if GrabDeviceNamesOnPage() == page[len(page) - 1]:
        printFP("INFO - Clicking Last Button gets us to the last page.")
    else:
        printFP("INFO - Clicking on the Last Button does not get us to the last page.")
        result = Global.FAIL

    # Checks if the first button gets us to hte first page by comparing the list to the first element in page
    GetElement(Global.driver, By.PARTIAL_LINK_TEXT, 'First').click()
    if GrabDeviceNamesOnPage() == page[0]:
        printFP("INFO - Clicking First Button gets us to the first page.")
    else:
        printFP("INFO - Clicking on the First Button does not get us to the first page.")
        result = Global.FAIL

    if result == Global.FAIL:
        testComment = 'One of the pages did not match as we verified the navigation buttons. Please refer to log file for more information'
    else:
        testComment = 'All pages matched as we progressed through the navigation buttons.'
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)


def ChangeNumberofDevicesPerPage(input_file_path=None, rows_per_page=None, UpgradePage=False):
    if not (input_file_path and rows_per_page):
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    # Goes to page and finds group tree location
    params = ParseJsonInputFile(input_file_path)
    GoToDevMan()
    if UpgradePage:
        GoToDevUpgrade()

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    # Clicks the Row per page button and tries to change the rows per page
    try:
        GetElement(Global.driver, By.XPATH, "//span[text()='Rows per Page']/../single-select/div/button").click()
        time.sleep(1)
        GetElement(Global.driver, By.XPATH, "//span[text()='" + str(rows_per_page) + "']").click()
    except:
        testComment = 'Exception error when trying to change the number of rows'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    """Checks page and sees that the number of devices is less or equal to the rows per page value
        it will continously check as long as it can click next. When next is disabled then it will break
        since it will be the last page"""
    result = Global.PASS
    while True:
        length = len(GetElements(Global.driver, By.XPATH, "//td[2]/span"))
        if length <= rows_per_page:
            printFP("Current Page displays less than or equal to the amount of devices allowed.")
        else:
            printFP("Current Page displays more than the amount of devices allowed in one page.")
            result = Global.FAIL
        try:
            nextButton = GetElement(Global.driver, By.LINK_TEXT, 'Next >')
            if 'disabled' in GetElement(nextButton, By.XPATH, '..').get_attribute('class'):
                break
            else:
                nextButton.click()
        except:
            break

    if result == Global.PASS:
        testComment = "All pages contained less than or equal to the amount of devices allowed in one page."
    else:
        testComment = "Some pages contained more than the amount of devices allowed."
    printFP("INFO - " + testComment)
    return result, ("TEST PASS - " + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment + 'Please refer to Log file for more information')


def EditProfileName(input_file_path=None, device_names=None, profileName=None, newprofileName=None,  description=None):
    if not (input_file_path and device_names and profileName and (newprofileName or description)):
        testComment = 'Missing a mandatory input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    # Go to manage profile and find the profile that matches profileName
    GoToManageProfile()
    try:
        profile = GetElement(Global.driver, By.XPATH, "//li[@ng-repeat='profile in profileList']/span[text()='"+profileName+"']")
        profile.click()
    except:
        testComment = 'Test could not locate profile %s.' %profileName
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    # Changes either/both profile name and description
    tabcontentDiv = GetElement(Global.driver, By.CSS_SELECTOR, 'div.info.tabs.ng-scope')
    try:
        if newprofileName:
            nameElement = GetElement(tabcontentDiv, By.TAG_NAME, 'input')
            ClearInput(nameElement)
            nameElement.send_keys(newprofileName)

        if description:
            descriptionElement = GetElement(tabcontentDiv, By.TAG_NAME, 'textarea')
            ClearInput(descriptionElement)
            descriptionElement.send_keys(description)
    except:
        testComment = 'Exception occurred when trying to fill out one of the text areas.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    # Saves it
    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_save'])

    # Checks if you can find any of the devices and if they are found check if they are in progress
    GoToCurrentJobsConfig()
    try:
        Jobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
    except:
        printFP("INFO - Test could not find any jobs in the Current Jobs - Configure page. Ending Test.")
        return Global.FAIL, 'TEST FAIL - Test could nto find any jobs in the Current Jobs  Configure Page'
    for job in Jobs:
        if not ('item-active' in job.get_attribute('class')):
            job.click()

        time.sleep(1)
        devicesFound = 0
        try:
            JobTbody = GetElement(Global.driver, By.XPATH, "//table[contains(@class,'jobs-list-table')]/tbody")
            for i in range(len(device_names)):
                try:
                    deviceRow = GetElement(Global.driver, By.XPATH, "//span[text()='" + device_names[i] + "']")
                    devicesFound += 1
                except:
                    printFP("INFO - Test was unable to find device in this job. Trying different job.")
                    break

                try:
                    deviceStatus = GetElement(Global.driver, By.XPATH, "//span[text()='" + device_names[i] + "']/../../td[6]/span").text
                    printFP('INFO - Job Status of device after either name and or description: %s' % deviceStatus)
                except:
                    printFP("INFO - Test could not locate job status of device.")

                if deviceStatus == 'INPROGRESS':
                    testComment = 'Either Name or Description text change caused an internal configuration'
                    printFP(testComment)
                    return Global.FAIL, testComment

            if devicesFound == len(device_names):
                break
        except:
            printFP("Error in trying to locate device and it's job status")

    # If there is a new profile name then you need to check if the profile name has change
    if newprofileName:
        params = ParseJsonInputFile(input_file_path)
        GoToDevMan()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "Could not locate node from input file"
            printFP(testComment)
            return Global.FAIL, testComment

        for i in range(len(device_names)):
            DeviceRow = GetDevice(device_names[i])
            profile = GetElement(DeviceRow, By.XPATH, "td[5]/span").text
            if not (profile == newprofileName):
                testComment = 'Device {} had profile name of {} instead of the new profile name {}' .format(device_names[i], profile, newprofileName)
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                printFP('Device {} updated the profile name to {}'.format(device_names[i], newprofileName))

    return Global.PASS, 'TEST PASS - Changing the profile name or adding a description does not trigger changes.'

def EditProfileDNP(device_name=None, profileName=None, tabs=None, fields=None, parameterTable=None):
    if not (device_name and profileName and fields and tabs):
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    # Goes to manage profile tab and then finds the profile name
    GoToManageProfile()
    try:
        profile = GetElement(Global.driver, By.XPATH, "//li[@ng-repeat='profile in profileList']/span[text()='"+profileName+"']")
        profile.click()
        printFP("Found profile %s" %profileName)
    except:
        testComment = 'Test could not locate profile.'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    # for each tab try to fill out any fields that want to be changed
    for tab in tabs:
        print "Filling out %s" % tab
        FillInProfileFields(tab, fields[tab])

    # tries to save and ensure that the profile did save successfully
    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_save'])
    try:
        GetElement(Global.driver, By.XPATH, "//span[contains(text(),'Profile saved successfully.')]")
        printFP("INFO - Profile saved successfully.")
    except:
        printFP("INFO - Profile did not save successfully.")
        return Global.FAIL, 'TEST FAIL - Profile did not save successfully.'

    # goes to current jobs config and tries to find the job that is changing the DNP points
    GoToCurrentJobsConfig()
    while True:
        try:
            Jobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
        except:
            printFP("INFO - Test could not locate any elements in the Job List. Exiting Test.")
            return Global.FAIL, 'TEST FAIL - Test could not locate any elements in the job list.'

        for t in range(len(Jobs)):
            if not ('item-active' in Jobs[t].get_attribute('class')):
                Jobs[t].click()
            if SearchJobLink(device_name):
                break
            elif t == (len(allJobs) - 1):
                printFP("INFO - Test could not locate job with all devices listed.")
                return Global.FAIL, "TEST FAIL - Test could not locate job with all devices listed."
        # Checks if all the devices are being configured and in progress
        devicesConfigured = 0
        for i in range(len(device_name)):
            count = 0
            DeviceRow = GetElement(Global.driver, By.XPATH, "//span[text()='" + str(device_name[i]) + "']/../..")
            if DeviceRow is not None:
                try:
                    WebDriverWait(DeviceRow, 10).until(EC.text_to_be_present_in_element((By.XPATH, 'td[6]/span'), 'SUCCESS'))
                    printFP("INFO - Device %s successfully configured." % device_name[i])
                    devicesConfigured += 1
                except:
                    printFP("INFO - Device %s did not successfully configure." % device_name[i])

        if devicesConfigured != len(device_name):
            time.sleep(60)
            Global.driver.refresh()
        else:
            break

    # puts all changes into device Parameter
    result = Global.PASS
    deviceParamDict = {}
    for n in range(len(device_name)):
        GetElement(Global.driver, By.XPATH, "//span[text()='" + str(device_name[n]) + "']/../..").click()
        time.sleep(1)
        deviceParams = GetElements(Global.driver, By.XPATH, "//tr[@ng-repeat='deviceParam in deviceParameters']")
        if len(deviceParams) > 0:
            deviceParamDict[device_name[n]] = {}
        else:
            printFP("INFO - Device %s did not contain any changes." % device_name[n])
            return Global.FAIL, "TEST FAIL - Device %s did not contain any changes." % device_name[n]

        for m in range(len(deviceParams)):
            key = GetElement(deviceParams[m], By.XPATH, "td[2]/span").text
            value = GetElement(deviceParams[m], By.XPATH, "td[3]").text
            deviceParamDict[device_name[n]][key] = value

    # checks that the DNP points that were changed matches the values that were given
    for j in range(len(device_name)):
        printFP("Verifying Device %s" % device_name[j])
        for tab in tabs:
            allkeys = parameterTable[tab].keys()
            for key in allkeys:
                printFP("Testing DNP Point %s. Ample Value: %s. JSON Value: %s" % (key, value, parameterTable[tab][key]))
                try:
                    if deviceParamDict[device_name[j]][key] == 'true' and parameterTable[tab][key] == 1:
                        del deviceParamDict[device_name[j]][key]
                    elif deviceParamDict[device_name[j]][key] == 'false' and parameterTable[tab][key] == 0:
                        del deviceParamDict[device_name[j]][key]
                    elif int(deviceParamDict[device_name[j]][key]) == parameterTable[tab][key]:
                        del deviceParamDict[device_name[j]][key]
                    else:
                        printFP('INFO - DNP Point %s was incorrect. Ample Value: %s. JSON Value: %s' % (key, value, parameterTable[tab][key]))
                        result = Global.FAIL
                except KeyError:
                    printFP('INFO - DNP Point %s was not found in the parameters table after editting.' % key)
                    result = Global.FAIL

        if deviceParamDict[device_name[j]]:
            result = Global.FAIL
            printFP("INFO - Ample table shows more values than the amount the test editted for device %s." % device_name[i])

    if result == Global.FAIL:
        testComment = 'Ample encountered an issue after editting DNP points to profiles already applied.'
    else:
        testComment = 'Ample changed the values of devices with the profile that was editted.'
    printFP("INFO - " + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)


def VerifyDNPChanges(input_file_path=None, device_name=None, polltime=0):
    if input_file_path is None or device_name is None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToCurrentJobsConfig()
    search = True
    changedDNPdict = {}

    """Searches the jobs list and finds the job that contains the devices; if they are not successful,
    then either retry (if FAIL) else sleep and wait 60s and try it again. If successful, it will store the DNP point changes
    for the device inside a dictionary"""
    while search:
        count = 0
        countFailure = 0
        time.sleep(2)
        for i in range(len(device_name)):
            time.sleep(2)
            JobTable = GetElement(Global.driver, By.CLASS_NAME, 'jobs-list-table')
            JobTbody = GetElement(JobTable, By.TAG_NAME, 'tbody')
            DeviceRow = FindRowInTable(JobTbody, device_name[i])
            if DeviceRow == None:
                testComment = 'Could not locate device %s on Config Job List' %device_name[i]
                printFP(testComment)
                return Global.FAIL, testComment
            textVal = GetElement(DeviceRow, By.XPATH, 'td[6]/span').text

            while textVal == 'FAILURE':
                if countFailure == 3:
                    testComment = 'Issue with device %s. Cannot configure after 3 retries.' %device_name[i]
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    countFailure += 1
                    rowButton = GetElement(DeviceRow, By.TAG_NAME, 'input')
                    if not 'disabled' in rowButton.get_attribute('class'):
                        rowButton.click()
                    GetElement(Global.driver, By.XPATH, "//button[contains(.,'Retry')]").click()
                    time.sleep(2)
                    JobTable = GetElement(Global.driver, By.CLASS_NAME, 'jobs-list-table')
                    JobTbody = GetElement(JobTable, By.TAG_NAME, 'tbody')
                    DeviceRow = FindRowInTable(JobTbody, device_name[i])
                    textVal = GetElement(DeviceRow, By.XPATH, 'td[6]/span').text

            if textVal == 'SUCCESS':
                DeviceRow.click()
                time.sleep(2)
                count += 1
                changedDNPdict[device_name[i]] = {}
                try:
                    parametersRows = GetElements(Global.driver, By.XPATH, "//tr[@ng-repeat='deviceParam in deviceParameters']")
                    for n in range(len(parametersRows)):
                        key = GetElement(parametersRows[n], By.XPATH, 'td[2]/span').text
                        value = GetElement(parametersRows[n], By.XPATH, 'td[3]').text
                        changedDNPdict[device_name[i]][key]=value
                except:
                    printFP("INFO - No parameter changes were found.")
                time.sleep(1)
            else:
                printFP('Device %s did not successfully configure yet.'%device_name[i])

        if count == len(device_name):
            search = False
        else:
            time.sleep(60)
            Global.driver.refresh()

    """Go to device management and goes to group tree that contains the devices"""
    GoToDevMan()
    #GoToDevConfig()
    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    """Finds the devices and checks if their details are updated within the polltime"""
    elapsedtime = 0
    while elapsedtime < polltime:
        deviceCorrect = 0
        for i in range(len(device_name)):
            TableBody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
            time.sleep(2)
            row = FindRowInTable(TableBody, device_name[i])
            if row == None:
                testComment = "Device Name %s could not be located" % device_name[i]
                printFP(testComment)
                return Global.FAIL, testComment

            time.sleep(2)
            DetailButton = GetElement(row, By.XPATH, "td[2]/span/a")
            time.sleep(2)
            ActionChains(Global.driver).click(DetailButton).perform()
            time.sleep(1)

            count = 0
            IDs = ["cfci","summary", "nonCfci", "logi"]
            for n in range(len(IDs)):
                tab = GetElement(Global.driver, By.ID, IDs[n])
                if not 'active' in tab.get_attribute('class'):
                    tab.click()
                time.sleep(1)
                active = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']")
                divElements = GetElements(active, By.XPATH, "//div[contains(@class, 'section-wrap')]")

                """Checks if the values match via dictionary for that device"""
                for x in divElements:
                    key = GetElement(x, By.XPATH, 'span[1]/span').get_attribute('tooltip')
                    value = GetElement(x, By.XPATH, 'span[2]').text
                    if changedDNPdict[device_name[i]].get(key):
                        if not changedDNPdict[device_name[i]][key] == value:
                            printFP('Values for given key %s did not match' % key)
                        else:
                            count +=1
                            print "Matched Parameter {} with Value of {} on Detail Window".format(key, value)
            ClickButton(Global.driver, By.XPATH, xpaths['dev_man_detail_close'])

            if count == len(changedDNPdict[device_name[i]].keys()):
                deviceCorrect += 1

        if deviceCorrect == len(device_name):
            testComment = 'All Device Details Matched'
            printFP('INFO - ' + testComment)
            Global.driver.refresh()
            return Global.PASS, 'TEST PASS - ' + testComment
        else:
            elapsedtime += 60
            time.sleep(60)
            Global.driver.refresh()

    """If it times out then it did not configure within the time allowed."""
    testComment = 'Test could not find one or more of the keys in the Configuration Page.'
    printFP(testComment)
    return Global.FAIL, testComment

def ApplyProfileByTree(input_file_path=None, treePortion=None, config=None):
    if input_file_path == None or treePortion == None or config == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']
    """Goes to device management configure and finds group tree location for applying configure"""
    GoToDevMan()
    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    """gets the group tree element to apply a configure through the group tree"""
    if treePortion == 'site':
        element = GetSite(site)
    elif treePortion == 'feeder':
        element = GetFeeder(feeder)
    elif treePortion == 'substation':
        element = GetSubstation(sub)
    else:
        testComment = 'Invalid value passed in treePortion parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    """Right clicks the group tree element and tries to select Configure"""
    RightClickElement(element)
    try:
        SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Configure')
    except:
        printFP("INFO - Ran into issue trying to click configure.")
        return Global.FAIL, 'TEST FAIL - Test ran into issue while trying to click configure.'
    try:
        profilebutton = GetElement(Global.driver, By.XPATH, "//button[contains(@class,'applyprofile-dropdown-btn-class')]")
        profilebutton.click()

        """Selects the profile you want to use"""
        profile = GetElement(Global.driver, By.XPATH, "//li[@ng-repeat='option in options']/a/span[text()='"+config+"']")
        profile.click()

        applyButton = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'device-form-action')]/button[contains(text(),'Apply')]")
        applyButton.click()
    except:
        printFP("INFO - Test ran into exception while trying to select profile. Refreshing and ending test.")
        Global.driver.refresh()
        return Global.FAIL, 'TEST FAIL - Test ran into exception while trying to select profile.'

    try:
        confirmTitle = GetElement(Global.driver, By.XPATH, "//div[@class='modal-header ng-scope']/span[contains(text(),'Apply')]")
        confirmButton = GetElement(Global.driver, By.XPATH, "//button[text()='Ok']")
        confirmButton.click()
    except:
        printFP("INFO - Test ran into issue while trying to click Ok. Refreshing and ending test.")
        Global.driver.refresh()
        return Global.FAIL, 'TEST FAIL - Test ran into issue while trying to click Ok.'

    returnMessage = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]/div/span")
    printFP("INFO - Return message: %s" % returnMessage.text)
    if 'Successfully' in returnMessage.text:
        pass
    else:
        printFP("INFO - Invalid return message. Possibly error.")
    GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()

    return Global.PASS, 'TEST PASS - Successfully configured through tree'

def CheckDeviceDetails(input_file_path=None, device_names=None):
    if input_file_path == None or device_names == None:
        testComment = "One of the parameters is missing."
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    GoToDevMan()

    """Goes to group tree location for device"""
    out = GetLocationFromInput(params['Region'],params['Substation'],params['Feeder'],params['Site'])
    if out == False:
        testComment = 'Provided site does not exist'
        printFP(testComment)
        return Global.FAIL, testComment

    """Check if we can reach device details for each device"""
    TableBody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
    for n in range(len(device_names)):
        row = FindRowInTable(TableBody, device_names[n])
        if row == None:
            testComment = "Device Name %s could not be located" % device_names[n]
            printFP(testComment)
            return Global.FAIL, testComment
        detail = GetElement(row, By.XPATH, 'td[22]/div/span[1]')
        ActionChains(Global.driver).click(detail).perform()
        time.sleep(2)
        if GetElement(Global.driver, By.CLASS_NAME, "modal-content") == None:
            testComment = "Details for Device %s did not display" % device_names[n]
            printFP(testComment)
            return Global.FAIL, testComment
        ClickButton(Global.driver, By.XPATH, xpaths['dev_man_detail_close'])
    return Global.PASS, ''


def SelectProfile(config=None):
    """Private function that is to select profile after you get to the screen"""
    try:
        time.sleep(1)
        ClickButton(Global.driver, By.XPATH, xpaths['dev_man_configure_dropdown'])
        time.sleep(1)
        GetElement(Global.driver, By.XPATH, "//li[@ng-repeat='option in options']/a[span='"+config+"']").click()
        time.sleep(3)
        GetElement(Global.driver, By.XPATH, xpaths['dev_man_configure_apply']).click()
        time.sleep(2)
        msg = GetText(Global.driver, By.XPATH, xpaths['dev_man_configure_error'])
        ClickButton(Global.driver, By.XPATH, xpaths['dev_man_configure_close'])
        if not 'Successfully' in msg:
            return False
        else:
            return True
    except:
        printFP("INFO - Selecting profile encountered an issue.")
        return False

def configureDevice(input_file_path=None, device_name=None, config=None, actionButton=False, waitforconfiguration=False):
    #this test simply tests the configuration button to see
    #site_name = site that the device is located on
    #device_name = list of device names that will be configured
    #config = name of the profile to be applied

    if input_file_path == None and device_name == None and config == None:
        testComment = 'One or more mandatory parameter is missing.'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(Global.testResourcePath + input_file_path)
    GoToDevMan()
    GoToDevConfig()

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = 'Provided input values are not valid.'
        printFP(testComment)
        return Global.FAIL, testComment
    time.sleep(1)

    if actionButton:
        for i in range(len(device_name)):
            row = GetDevice(device_name[i])
            button = GetElement(row, By.TAG_NAME, 'input')
            SetCheckBox(button, "true")
            time.sleep(2)
            configAction = GetElement(Global.driver, By.XPATH, xpaths['dev_man_configure'])
            time.sleep(2)
            if 'disabled' in configAction.get_attribute('class'):
                testComment = 'Unable to click configure button for this device %s' %device_name[i]
                printFP(testComment)
                return Global.FAIL, testComment
            configAction.click()
            if not SelectProfile(config):
                testComment = 'An error occurred while trying to configure the devices.'
                printFP(testComment)
                return Global.FAIL, testComment
    else:
        TableBody = GetElement(Global.driver, By.TAG_NAME, "tbody")
        for x in range(len(device_name)):
            row = FindRowInTable(TableBody, device_name[x])
            if row == None:
                testComment = "Test Could not find device named %s" % device_name[x]
                printFP('INFO - ' + testComment)
                return Global.FAIL, 'TEST FAIL ' + testComment
            button = GetElement(row, By.TAG_NAME, 'input')
            SetCheckBox(button, "true")

        classText = GetElement(Global.driver, By.XPATH, xpaths['dev_man_configure']).get_attribute('class')
        if 'disabled' in classText:
            testComment = 'Configure Button is disabled currently'
            printFP(testComment)
            return Global.FAIL, testComment

        if ClickButton(Global.driver, By.XPATH, xpaths['dev_man_configure']):
            if not SelectProfile(config):
                testComment = 'An error occured while trying to configure the devices.'
                printFP(testComment)
                return Global.FAIL, testComment

    result = Global.PASS
    for x in range(len(device_name)):
        TableBody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
        row = FindRowInTable(TableBody, device_name[x])
        if row == None:
            testComment = "Device named %s could not be located." % device_name[x]
            printFP(testComment)
            return Global.FAIL, testComment

        pName = GetElement(row, By.XPATH, 'td[5]/span').text
        if config == pName:
            printFP("New profile was applied successfully for device %s." % device_name[x])
        else:
            testComment="Profile was not applied successfully for device %s."% device_name[x]
            printFP(testComment)
            result = Global.FAIL

    if result == Global.FAIL:
        return result, "TEST FAIL - Profile was not applied succesfully to all devices"
    else:
        return result, "TEST PASS - Profile was applied successfully to all devices"

def UnregisterWhileConfigTest(device_names=None):
    """ Helper function that determines whether the Unregister Button is valid
        WHILE configuring. This is not an individual/independent test"""

    if device_names == None:
        testComment = 'No device(s) names were given to verify.'
        printFP(testComment)
        return Global.FAIL, testComment

    ClickButton(Global.driver, By.XPATH, xpaths['dev_config_col_btn'])
    FieldBox = GetElement(Global.driver, By.XPATH, xpaths['dev_config_cols'])
    ColumnOptions = GetElements(FieldBox, By.TAG_NAME, 'span')
    for option in ColumnOptions:
        if option.text == "Profile Status":
            parentofOption = option.find_element_by_xpath("..")
            inputElement = GetElement(parentofOption, By.TAG_NAME, "input")
            SetCheckBox(inputElement,"true")
            ClickButton(Global.driver, By.XPATH, xpaths['dev_config_col_btn'])
            break

    TableBody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
    row = FindRowInTable(TableBody, device_names)
    if row == None:
        testComment = "Device named %s could not be located." % device_names
        printFP(testComment)
        return Global.FAIL, testComment
    checkBox = GetElement(row, By.TAG_NAME, 'input')
    SetCheckBox(checkBox,'true')

    cols = GetElements(row, By.TAG_NAME, 'span')
    count = 0
    for col in cols:
        count += 1
        if count == 6 and col.get_attribute('class') == "icon ion-loading-a":
            if 'disabled' in GetElement(Global.driver,By.XPATH, xpaths['dev_man_unregister']).get_attribute('class'):
                printFP("Unable to click - Waiting for the profile to finish loading now")
                time.sleep(120)
                result, testComment = Global.PASS, ''
            else:
                ClickButton(Global.driver, By.XPATH, xpaths['dev_man_unregister_close'])
                testComment = 'Error -- should not be able to click Unregister while loading'
                printFP(testComment)
                result,testComment = Global.FAIL, testComment
        elif count == 6 and not col.get_attribute('class') == "icon ion-loading-a":
            testComment = "Device is not configuring a profile currently"
            printFP(testComment)
            result,testComment = Global.FAIL, testComment
    return result, testComment

def configureThenDelete(input_file_path=None, device_name=None, config=None):
    try:
        result, message = configureDevice(input_file_path, device_name, config)
    except:
        printFP("INFO - Test ran into exception while configuring device")
        return Global.FAIL, 'TEST FAIL - Test ran into exception while configuring device'

    if result == Global.FAIL:
        return result, message

    try:
        result, message = deleteDevice(input_file_path, device_name, False)
    except:
        printFP("INFO - Test ran into an exception while deleting device.")
        return Global.FAIL, 'TEST FAIL - Test ran into except while deleting device'

    GoToCurrentJobsConfig()

    if not 'ng-hide' in GetElement(Global.driver, By.XPATH, '//div[@class="section-filters grouping-data margin-0"]/div[1]').get_attribute('class'):
        printFP("INFO - Test does not find any jobs in Current Jobs - Config.")
        return Global.PASS, 'TEST PASS - Test could not find any jobs in Current Jobs - Config'
    else:
        jobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
        for i in range(len(jobs)):
            jobs[i].click()
        if SearchJobLink(device_name):
            printFP("INFO - Found a job that contains the deleted device.")
            return Global.FAIL, 'TEST FAIL - Test found a job that contains a deleted device'

    return Global.PASS, 'TEST PASS - Test did not find a job that contains a deleted device'

def deleteDevice(input_file_path=None, device_name=None, actionButton=False):
    #site_name - site name where the device you wish to delete from
    #device_name - name to search for to delete

    if input_file_path == None or device_name == None:
        testComment = 'Test is missing mandatory parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(Global.testResourcePath + input_file_path)
    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    """Goes to Device Management Configure and go to group tree location for device"""
    GoToDevMan()
    if not GetLocationFromInput(region, substation, feeder, site):
        testComment = "Unable to locate locations based off input file"
        printFP(testComment)
        return Global.FAIL, testComment

    """If it is action button it will click each delete button for each device.
    Otherwise, will check every device and then click the Delete button at the top"""
    if actionButton:
        for i in range(len(device_name)):
            row = GetDevice(device_name[i])
            GetElement(row, By.XPATH, 'td[22]/div/span[5]').click()
            confirmDelete = GetElement(Global.driver, By.XPATH, "//button[text()='Ok']")
            confirmDelete.click()
            if not CheckIfStaleElement(confirmDelete):
                printFP("Confirm Delete pop up has not disappeared.")
    else:
        for i in range(len(device_name)):
            TableBody = GetElement(Global.driver, By.TAG_NAME, "tbody")
            row = FindRowInTable(TableBody, device_name[i])
            if row is None:
                testComment = 'Test could not find %s to delete' % device_name[i]
                printFP('INFO - ' + testComment)
                return Global.FAIL, 'TEST FAIL - ' + testComment
            element = GetElement(row, By.TAG_NAME, 'input')
            SetCheckBox(element, 'true')
            time.sleep(1)

        if ClickButton(Global.driver, By.XPATH, xpaths['dev_man_delete']):
            confirmButton = GetElement(Global.driver, By.XPATH, "//button[text()='Ok']")
            confirmButton.click()
            if not CheckIfStaleElement(confirmButton):
                printFP("Confirm Delete pop up has not disappeared.")

    Global.driver.refresh()
    """Tries to find every device in the list; if it exists, then delete did not work"""
    found = False
    for i in range(len(device_name)):
        try:
            text = GetElement(Global.driver, By.XPATH, '//span[text()="'+str(device_name[i])+'"]').text
            if text == device_name[i]:
                found = True
                printFP("INFO - Device %s is still on the table." % device_name[i])
        except:
            pass

    if not found:
        return Global.PASS, 'TEST PASS - Test successfully deleted all devices specified.'
    else:
        testComment = 'Deleted device: %s is still exist in the table' % device_name[i]
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

def OTAPCheckOfflineDeviceUpgrade(input_file_path=None, device_name=None, waitOnline=False, commserver=None, networkgroup=None):
    if input_file_path == None or device_name == None:
        testComment = 'Test is missing mandatory parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)

    GoToDevMan()
    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate locations based off input file -- Config"
        printFP(testComment)
        return Global.FAIL, testComment

    TableBody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
    row = FindRowInTable(TableBody, device_name)
    if row == None:
        testComment = 'Could not locate device named %s' % device_name
        printFP(testComment)
        return Global.FAIL, testComment

    status = GetElement(row, By.XPATH, 'td[4]/span')
    if status.get_attribute('class') == 'icon ion-checkmark-circled':
        printFP("Device is currently in Online State..Changing it to Offline")
        UnregisterTest(input_file_path, device_name, False, False)
        RegisterDevice(input_file_path, commserver, networkgroup, device_name, False)
    elif status.get_attribute('class') == 'icon glyphicon glyphicon-transfer':
        printFP("Device is currently in Unregistered State.. Changing it to Offline")
        RegisterDevice(input_file_path, commserver, networkgroup, device_name, False)

    GoToDevUpgrade()
    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Information provided by input file is invalid -- Upgrade"
        printFP(testComment)
        return Global.FAIL, testComment

    row = GetDevice(device_name)
    deviceStatus = GetElement(row, By.XPATH, 'td[4]/span')
    if deviceStatus.get_attribute('class') == 'icon ion-close-circled':
        # CheckBox = GetElement(row, By.TAG_NAME, 'input')
        deviceSelect = GetElement(row, By.TAG_NAME, 'input')
        SetCheckBox(deviceSelect, 'true')
        try:
            upgradeButton = WebDriverWait(Global.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpaths['dev_upgrade_button'])))
            upgradeButton.click()
            if 'disabled' in upgradeButton.get_attribute('class'):
                pass
            else:
                testComment = 'Upgrade button was not disabled for an offline device %s' %device_name
                printFP(testComment)
                return Global.FAIL, testComment
        except:
            pass
        printFP('Upgrade Button was disabled for an offline device %s' %device_name)
        return Global.PASS, ''
    else:
        testComment = 'Device was not offline after running unregister and register'
        printFP(testComment)
        return Global.FAIL, testComment

def DeleteSubStation(input_file_path=None, region_name=None, substation_name=None):
    if region_name and substation_name:
        sub_name = substation_name
        GoToDevMan()
        if not GetLocationFromInput(region_name, substation_name, None, None):
            testComment = "Unable to locate locations based off input file -- Config"
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        if input_file_path == None:
            testComment = 'Test is missing mandatory parameter'
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            params = ParseJsonInputFile(input_file_path)
            sub_name = params['Substation']
            GoToDevMan()
            if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
                testComment = "Unable to locate locations based off input file -- Config"
                printFP(testComment)
                return Global.FAIL, testComment

    sub = GetSubstation(sub_name)
    if sub == None:
        testComment = "Unable to find feeder named %s" % sub_name
        printFP(testComment)
        return Global.FAIL, testComment

    RightClickElement(sub)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Delete')
    confirmDelete = GetElement(Global.driver, By.XPATH, "//div[@class='modal-footer ng-scope']/button[text()='Delete']")
    confirmDelete.click()
    if not CheckIfStaleElement(confirmDelete):
        printFP("Delete confirmation screen has not disappeared.")

    Global.driver.refresh()
    if GetSubstation(sub_name) == None:
        printFP("Substation %s deleted." % params['Substation'])
        return Global.PASS,""
    else:
        testComment = 'Failed to delete substation %s' % params['Substation']
        printFP(testComment)
        return Global.FAIL,testComment

def DeleteFeeder(input_file_path=None):
    if input_file_path == None:
        testComment = 'Test is missing mandatory parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)

    GoToDevMan()
    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate locations based off input file -- Config"
        printFP(testComment)
        return Global.FAIL, testComment

    feederElement = GetFeeder(params['Feeder'])
    if feederElement == None:
        testComment = "Unable to find feeder named %s" %params['Feeder']
        printFP(testComment)
        return Global.FAIL, testComment

    RightClickElement(feederElement)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Delete')
    confirmDelete = GetElement(Global.driver, By.XPATH, "//div[@class='modal-footer ng-scope']/button[text()='Delete']")
    confirmDelete.click()
    if not CheckIfStaleElement(confirmDelete):
        printFP("Delete confirmation screen has not disappeared.")

    Global.driver.refresh()
    if GetFeeder(params['Feeder']) == None:
        printFP("Feeder %s deleted." %params['Feeder'])
        return Global.PASS,""
    else:
        testComment = 'Failed to delete Feeder %s' % params['Feeder']
        printFP(testComment)
        return Global.FAIL, testComment

def DeleteSite(input_file_path=None, site_name=None):
    #This test deletes a site -- will return pass only if it was able to find the site and successfully delete it
    #use_global_test_device: parameter to use the global test Device's site_name rather than inputting your own site_name;
    #must be set to FALSE if you wish to use a site_name
    #site_name: site to find and attempt to delete

    if input_file_path == None:
        testComment = 'Test is missing mandatory parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)

    GoToDevMan()
    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate locations based off input file -- Config"
        printFP(testComment)
        return Global.FAIL, testComment

    if not site_name:
        site_name = params['Site']

    siteElement = GetSite(site_name)
    if siteElement == None:
        testComment = "Unable to find site named %s" % site_name
        printFP(testComment)
        return Global.FAIL, testComment

    RightClickElement(siteElement)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Delete')
    confirmDelete = GetElement(Global.driver, By.XPATH, "//div[@class='modal-footer ng-scope']/button[text()='Delete']")
    confirmDelete.click()
    if not CheckIfStaleElement(confirmDelete):
        printFP("Delete confirmation screen has not disappeared.")

    Global.driver.refresh()
    if GetSite(site_name) == None:
        printFP("Site %s deleted." % site_name)
        return Global.PASS,""
    else:
        testComment = 'Failed to delete Site %s' % site_name
        printFP(testComment)
        return Global.FAIL,testComment

def UnregisterTest(input_file_path=None, unregDev=None, checkRegisterButton=True, actionButton=False):
    if input_file_path == None or unregDev == None:
        testComment = 'Missing a mandatory input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToDevMan()
    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Unable to locate locations based off input file"
        printFP(testComment)
        return Global.FAIL, testComment

    if actionButton:
        for i in range(len(unregDev)):
            row = GetDevice(unregDev[i])
            action = GetElement(row, By.XPATH, 'td[22]/div/span[4]/span')
            ActionChains(Global.driver).click(action).perform()
            confirmUnregister = GetElement(Global.driver, By.XPATH, "//button[text()='Ok']")
            confirmUnregister.click()
            time.sleep(2)
            if not CheckIfStaleElement(confirmUnregister):
                printFP("INFO - Unregister pop up did not disappear.")
    else:
        try:
            TableBody = GetElement(Global.driver, By.TAG_NAME, "tbody")
        except:
            printFP("INFO - No Table was available. Ending Test.")
            return Global.FAIL, 'TEST FAIL - No Table was displayed'

        for i in range(len(unregDev)):
            row = FindRowInTable(TableBody, unregDev[i])
            button = GetElement(row, By.TAG_NAME, 'input')
            SetCheckBox(button, "true")
            time.sleep(1)

        if checkRegisterButton:
            try:
                GetElement(Global.driver,By.XPATH, xpaths['dev_man_register']).click()
                testComment = "Registered option available for registered device"
                printFP(testComment)
                return Global.FAIL, testComment
            except:
                printFP("Register option only available for unregistered device" )

        # Clicks Unregister Button
        try:
            unregButton = GetElement(Global.driver,By.XPATH, xpaths['dev_man_unregister'])
            if 'disabled' in unregButton.get_attribute('class'):
                testComment = 'Unregister Button is currently disabled.'
                printFP('INFO - ' + testComment)
                return Global.FAIL, 'TEST FAIL - ' + testComment
            unregButton.click()
        except:
            testComment = "Test was unable to click Unregister Button"
            printFP(testComment)
            return Global.FAIL, testComment
        time.sleep(1)
        confirmUnregister = GetElement(Global.driver, By.XPATH, "//div[@class='modal-footer ng-scope']/button[text()='Ok']")
        confirmUnregister.click()
        time.sleep(2)
        if not CheckIfStaleElement(confirmUnregister):
            printFP("INFO - Unregister pop up did not disappear.")

    #check if Unregistered
    result = Global.PASS
    Global.driver.refresh()
    time.sleep(10)
    for i in range(len(unregDev)):
        row = GetDevice(unregDev[i])
        icon = GetElement(row, By.XPATH, "td[4]/span")
        if not (icon.get_attribute('class') ==  "glyphicon glyphicon-transfer"):
            printFP("Device {} does not  displays Unregistered Icon." .format(unregDev[i]))
            result = Global.FAIL

    if result == Global.PASS:
        testComment = 'All Devices successfully unregistered and displays unregister icon'
    else:
        testComment = 'Test did not succesfully unregister all devices. Refer to Log File to see which devices failed.'

    printFP(testComment)
    return result, testComment

def RegisterDevice(input_file_path=None, commserver=None, sgw_group_name=None, regDev=None, wait_for_online=True):

    params = ParseJsonInputFile(input_file_path)
    GoToDevMan()

    if not GetLocationFromInput(params['Region'],params['Substation'],params['Feeder'],params['Site']):
        testComment = "Unable to locate locations based off input file"
        printFP(testComment)
        return Global.FAIL, testComment

    if not (commserver == None and sgw_group_name == None and regDev == None):
        TableBody = GetElement(Global.driver, By.TAG_NAME, "tbody")
        row = FindRowInTable(TableBody, regDev)
        GetElement(row, By.TAG_NAME, 'input').click()
        try:
            RegisterButton = GetElement(Global.driver, By.XPATH, xpaths['dev_man_register'])
            if 'ng-hide' in RegisterButton.get_attribute('class'):
                printFP("INFO - Register Button is currently hidden. Test is ending.")
                return Global.FAIL, 'TEST FAIL - Register Button is currently hidden.'
            RegisterButton.click()
            printFP("INFO - Register Button click was good.")
        except:
            printFP("INFO - Test could not click register")
            return Global.FAIL, 'TEST FAIL - Test could not click register button.'
        try:
            sensorgatewayOptions = GetElement(Global.driver, By.XPATH, "//single-select[@options='commServerSelection.list']/div/button")
            sensorgatewayOptions.click()
            time.sleep(2)
            sensorgateway = GetElement(Global.driver, By.XPATH, "//li[@ng-repeat='option in options']/a/span[text()='"+commserver+"']")
            sensorgateway.click()
            time.sleep(2)
        except:
            printFP("INFO - Test ran into exception while trying to click on SGW. Refreshing page and ending test.")
            Global.driver.refresh()
            return Global.FAIL, 'TEST FAIL - Test ran into exception while trying to click on SGW.'

        if not sgw_group_name == "":
            try:
                networkGroupButton = GetElement(Global.driver, By.XPATH, "//single-select[@options='groupNameSelection.list']/div/button")
                networkGroupButton.click()
                time.sleep(2)
                networkGroupElement = GetElement(Global.driver, By.XPATH, "//li[@ng-repeat='option in options']/a/span[text()='"+sgw_group_name+"']")
                networkGroupElement.click()
                time.sleep(2)
            except:
                printFP("INFO - Test ran into exception while trying to click on Network Group. Refreshing page and ending test.")
                Global.driver.refresh()
                return Global.FAIL, 'TEST FAIL - Test ran into exception while trying to click on Network Group.'

        button = GetElement(Global.driver, By.XPATH, "//button[text()='Ok']")
        button.click()
        time.sleep(2)
        if WebDriverWait(Global.driver, 10).until(EC.staleness_of(button)):
            printFP("INFO - Clicked OK for register")
        else:
            printFP("INFO - Did not click OK for register")
        returnMessage = GetElement(Global.driver, By.XPATH, xpaths['reg_site_msg']).text
        printFP('Return message: %s' % returnMessage)
        closeButton = GetElement(Global.driver,By.XPATH, xpaths['reg_site_msg_close'])
        closeButton.click()
        time.sleep(1)
        if 'Device have been registered successfully' in returnMessage:
            TableBody = GetElement(Global.driver, By.TAG_NAME, "tbody")
            row = FindRowInTable(TableBody, regDev)
            status = GetElement(row, By.XPATH, 'td[4]/span')
            classtype = status.get_attribute('class')
            if classtype == "glyphicon glyphicon-transfer":
                testComment = "Register Site Did not Register Correctly. Unregistered Icon is still displayed."
                printFP(testComment)
                return Global.FAIL, testComment
            if wait_for_online:
                if IsOnline(regDev):
                    return Global.PASS, ""
                else:
                    testComment = '%s did not come online and timed out.' % regDev
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                return Global.PASS, ""
        else:
            printFP('INFO - ' + returnMessage.text)
            return Global.FAIL, 'TEST FAIL - ' + returnMessage.text
    else:
        testComment = "Comm Server or Network Group Name or Device Name to register was not specified."
        printFP(testComment)
        return Global.FAIL, testComment

def Search(searchstr, val):
    """ Helper function to be called when Using the search bar """
    if val == 0:
        searchtextbox = GetElement(Global.driver,By.CLASS_NAME, "node-search")
        SendKeys(searchtextbox, searchstr)
        time.sleep(1)
        parentelementSearchtextbox = searchtextbox.find_element_by_xpath("..")
        time.sleep(1)
        #attr = re.compile(r'\bnode-search\b')
        DropDown = GetElement(Global.driver,By.XPATH, xpaths['tree_search'])
        try:
            DropDownlists = GetElements(DropDown,By.TAG_NAME, "a")
        except:
            DropDownlists = []
        if len(DropDownlists) == 0:
            return False

        for x in DropDownlists:
            result = GetElement(DropDown,By.CLASS_NAME, "node-name")
            resultname = result.text
            if searchstr in resultname:
                return True
            else:
                return False

    elif val == 1:
        searchtextbox = GetElement(Global.driver,By.CLASS_NAME, "device-search")
        time.sleep(2)
        SendKeys(searchtextbox, searchstr)
        time.sleep(2)
        searchclassname = searchtextbox.get_attribute('class')
        time.sleep(2)
        if not "placeholder" in searchclassname:
            Table = GetElement(Global.driver, By.TAG_NAME, "table")
            tableclassname = Table.get_attribute('class')
            time.sleep(1)
            if not "hide" in tableclassname:
                return True
            else:
                return False
        else:
            return False

    elif val == 2:
        searchtextbox = GetElement(Global.driver,By.CLASS_NAME, "fault-search")
        time.sleep(2)
        SendKeys(searchtextbox, searchstr)
        time.sleep(5)
        searchclassname = searchtextbox.get_attribute('class')
        time.sleep(2)
        if not "placeholder" in searchclassname:
            Table = GetElement(Global.driver, By.TAG_NAME, "table")
            tableclassname = Table.get_attribute('class')
            time.sleep(1)
            if not "hide" in tableclassname:
                return True
            else:
                return False
        else:
            return False

def SearchBarTestUpgrade(searchKeyword=None, region_name=None):
    """ Performs an negative test search to determine if Search Bar is functioning
        correctly in DeviceUtilities.pycgrade Page"""
    if region_name==None or searchKeyword==None:
        testComment = "One of the parameters is missing."
        printFP(testComment)
        return Global.FAIL, testComment

    Global.driver.refresh()
    GoToDevMan()
    GoToDevUpgrade()

    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()
    region = GetRegion(region_name)
    if region == None:
        testComment = 'region name %s is not found' % region_name
        printFP(testComment)
        return Global.FAIL, testComment
    time.sleep(3)
    printFP('Searching given keyword: %s in Upgraded Device Table' % searchKeyword)
    if Search(searchKeyword, 2):
        testComment = 'Search was succesful for finding keyword in Upgrade Page.'
        printFP(testComment)
        return Global.PASS, testComment

    else:
        testComment = 'Searching Upgrade Page with Input %s returns nothing.' % searchKeyword
        printFP(testComment)
        return Global.FAIL, testComment

def SearchBarTestConfig(searchKeyword=None, region_name=None):
    if searchKeyword == None or region_name==None:
        testComment = "No string was provided to search for in this test"
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()

    region = GetRegion(region_name)
    if region == None:
        testComment = 'region name %s is not found' % region_name
        printFP(testComment)
        return Global.FAIL, testComment
    printFP('Searching given keyword: %s in Device Table' % searchKeyword)
    if Search(searchKeyword, 1):
        testComment = 'Search was succesful for finding keyword in Config Page.'
        Global.driver.refresh()
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'Searching Configuration Page with Input %s returns nothing' % searchKeyword
        Global.driver.refresh()
        printFP(testComment)
        return Global.FAIL, testComment

def DeviceConfigExportTest(input_file_path=None, downloadfolder=None, filetype=None):
    """ Exporting the Device Management Data via Export Button into a CSV file
    and calls function to compare the exported file against the real values on
    Ample to ensure correct functionality """

    if input_file_path == None or downloadfolder == None or filetype == None:
        testComment = "Missing a mandatory parameter. Please fix"
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToDevMan()
    if not GetLocationFromInput(region, sub, feeder, site):
        testComment = "Invalid locations passed to parameter input_file_path"
        printFP(testComment)
        return Global.FAIL, testComment

    if ClickButton(Global.driver, By.XPATH, xpaths['dev_config_export_btn']):
        if filetype == 'CSV':
            ClickButton(Global.driver, By.XPATH, xpaths['configuration_export_csv_button'])
            location = downloadfolder + "export.csv"
        elif filetype == 'EXCEL':
            ClickButton(Global.driver, By.XPATH, xpaths['configuration_export_excel_button'])
            location = downloadfolder + "export.xls"
        else:
            ClickButton(Global.driver, By.XPATH, xpaths['dev_config_export_btn'])
            testComment = 'Invalid value for filetype parameter'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = "Unable to click Export Button"
        printFP('TEST INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    # must keep this sleep for export download time (bigger file will require you to change it)
    time.sleep(10)

    try:
        os.remove(location)
    except OSError as e:
        printFP(e)
        return Global.FAIL, 'TEST FAIL - ' + e

    testComment = "Successfully deleted file from download folder"
    printFP('INFO - ' + testComment)
    return Global.PASS, 'TEST PASS ' + testComment

def DeleteRegion(use_global_test_device=True, region_name=None):
    """This test finds the given region in the group tree and deletes the node.
    Args:
      bool useFP - if True, will read the region from fp"""

    if use_global_test_device:
        try:
            device = GetOnlineDevice()
            region_name = device['region']
        except Exception as e:
            printFP(e.message)
    elif region_name == None:
        testComment = 'No region name specified.'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()
        time.sleep(5)

    region = GetRegion(region_name)
    if region == None:
        testComment = "Region %s could not be found." % region_name
        printFP(testComment)
        return Global.FAIL, testComment

    RightClickElement(region)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Delete')
    ClickButton(Global.driver, By.XPATH, xpaths['tree_add_node_submit']) # confirm delete

    #Check if region is deleted
    Global.driver.refresh()
    if GetRegion(region_name) == None:
        printFP('Region %s deleted' % region_name)
        if use_global_test_device:
            try:
                MoveDeviceToOffline(device['serial'])
            except Exception as e:
                printFP(e.message)
        return Global.PASS, 'TEST PASS - '
    else:
        testComment = 'Failed to delete region %s' % region_name
        printFP(testComment)
        return Global.FAIL, testComment


#######################################################################################################
"""                             DEVICE UPGRADE FUNCTIONS                                            """
#######################################################################################################

def CheckDefaultUpgradePage(input_file_path=None, device_list=None):
    if input_file_path == None or device_list == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToDevMan()
    GoToDevUpgrade()

    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Unable to locate locations based off input file"
        printFP(testComment)
        return Global.FAIL, testComment

    #determine if OTAP Status Col + device
    TableBody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
    for i in range(len(device_list)):
        if FindRowInTable(TableBody, device_list[i]) == None:
            testComment = 'Could not locate Device %s in Upgrade Page' % device_list[i]
            printFP(testComment)
            return Global.FAIL, testComment

    #determine if Upgrade button is disabled by default
    try:
        upgradeButton = WebDriverWait(Global.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpaths['dev_upgrade_button'])))
        upgradeButton.click()
        if 'disabled' in upgradeButton.get_attribute('class'):
            printFP('Upgrade Button was disabled by default')
        else:
            testComment = 'Upgrade button was not disabled by default'
            printFP(testComment)
            return Global.FAIL, testComment
    except:
        printFP('Upgrade Button was disabled by default')

    testComment = 'Default Upgrade Page had no issues.'
    printFP('INFO - ' + testComment)
    return Global.PASS, 'TEST PASS - ' + testComment

def ValidDay(dayString):
    validDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return dayString in validDays

def ConfigureTime(timeBoxElement, timeSettings):
    allTimeElements = GetElements(timeBoxElement, By.TAG_NAME, 'td')
    printFP('Number of fields: %d' % len(allTimeElements))
    hourField = GetElement(allTimeElements[0], By.TAG_NAME, 'input')
    minuteField = GetElement(allTimeElements[2], By.TAG_NAME, 'input')
    periodButton = GetElement(allTimeElements[3], By.TAG_NAME, 'button')

    # Fill in time
    ClearInput(hourField)
    SendKeys(hourField, timeSettings['hour'])
    ClearInput(minuteField)
    SendKeys(minuteField, timeSettings['minute'])
    if periodButton.text == timeSettings['period']:
        # do nothing, setting is correct
        pass
    else:
        periodButton.click()
    return

def ChangeUpgradeSettings(upgrade_settings):
    """Configures the Upgrade Settings.
    Args:
      dic upgradeSettings - dictionary with the below parameters"""
    # upgradeSettings['days']
    #   days = Monday, Tuesday, etc. or All
    # upgradeSettings['from_time']
    #   from_time[hour,minute,am/pm]
    # upgradeSettings['to_time']
    #   to_time[hour,minute,am/pm]
    # upgradeSettings['numRetries']
    #   2 to 5
    

    # Select day
    if ValidDay(upgrade_settings['day']):
        ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_settings_days'])
        menuElement = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_days_menu'])
        SelectFromMenu(menuElement, By.TAG_NAME, 'li', upgrade_settings['day'])
        everydayCheckbox = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_everyday_checkbox'])
        SetCheckBox(everydayCheckbox, "False")
    else:
        everydayCheckbox = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_everyday_checkbox'])
        SetCheckbox(everydayCheckbox, "true")

    # Select time
    fromElement = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_settings_from'])
    toElement = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_settings_to'])
    ConfigureTime(fromElement, upgrade_settings['from_time'])
    ConfigureTime(toElement, upgrade_settings['to_time'])

    # Select retries
    ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_num_retries'])
    menuElement = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_num_retries_menu'])
    SelectFromMenu(menuElement, By.TAG_NAME, 'li', str(upgrade_settings['num_retries']))

    # Submit
    ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_settings_save'])
    time.sleep(1)
    try:
        msg = GetText(Global.driver, By.XPATH, xpaths['settings_upgrade_setting_errmsg'])
        if 'Start time must be earlier than end time.' in msg:
            ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_fail_close'])
            printFP(msg)
            return Global.FAIL, msg
    except:
        pass
    return Global.PASS, ''


def ParseTime(line):
    parsedTime = {}
    if 'AM' in line:
        parsedTime['period'] = 'AM'
        line = line.strip('AM')
    elif 'PM' in line:
        parsedTime['period'] = 'PM'
        line = line.strip('PM')
    else:
        return None
    line = line.split(':')
    parsedTime['hour'] = line[0]
    parsedTime['minute'] = line[1]
    return parsedTime


def UpgradeSettingsTest(upgrade_settings):
    """Change the upgrade settings in Ample. Reads input from inputFP to
    generate a dictionary representing the desired upgrade settings and
    executes the appropriate actions on the gui to configure those settings."""

    # configure upgrade settings
    # upgrade_setings['day'] Monday, Tuesday, etc.
    # upgrade_settings['from_time'] 9:00AM
    # upgrade_settings['to_time'] 10:00PM
    # upgrade_settings['num_retries'] 2-5

    upgrade_settings['from_time'] = ParseTime(upgrade_settings['from_time'])
    if upgrade_settings['from_time'] is None:
        testComment = 'Do not recognize this time format'
        printFP(testComment)
        return Global.FAIL, testComment
    # set end time
    upgrade_settings['to_time'] = ParseTime(upgrade_settings['to_time'])
    if upgrade_settings['to_time'] is None:
        testComment = 'Do not recognize this time format'
        printFP(testComment)
        return Global.FAIL, testComment
    # set num retries
    if upgrade_settings['num_retries'] > 5 or upgrade_settings['num_retries'] < 2:
        testComment = 'num_retries is out of range - value: %d' % upgrade_settings['num_retries']
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()
    GoToDevUpgrade()
    return ChangeUpgradeSettings(upgrade_settings)


def FlashDevice(path_to_rsa_key=None, target_version=None, ipaddr=None, portNumber=None, networktype=None):
    """This test will ssh to the device and flash it to the target version
    using the ssd. The device must have an ssd. Currently only works with
    Sierra 7354 cell units.

    The 1st parameter is to get a device from ample or off ample.
    2nd parameter is the path to the sentient id_rsa key for ssh
    3rd parameter is the software version to upgrade to."""

    if path_to_rsa_key == None or target_version == None or ipaddr == None or portNumber == None or networktype == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    # Start the flash
    flashstatus = FlashUnitFromSSD(ipaddr, path_to_rsa_key, target_version, portNumber, networktype)
    if not(flashstatus):
        printFP("INFO - Device did not Flash from ssh")
        return Global.FAIL, 'Device could not flash unit from SSH'

    # Wait for the device to finish rebooting
    flash_complete = CheckIfFlashComplete(ipaddr, path_to_rsa_key, target_version, portNumber, networktype)
    if flash_complete:
        return Global.PASS, 'Device flashed successfully'
    else:
        return Global.FAIL, 'Device was not flashed successfully'


def OTAPWrongUpdateSetting(input_file_path=None, device_name=None, target_version=None,actionButton=False,timeout=1200, time_or_day=None):
    if not (input_file_path and device_name and target_version and time_or_day):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    if time_or_day == 'Day':
        Dates = ["Saturday", "Sunday", "Monday","Tuesday", "Wednesday", "Thursday", "Friday"]
        i = datetime.datetime.today().weekday()
        print i
        #print datetime.datetime.today().weekday()
        #print Dates[i]

        upgrade_settings = {
            "day": Dates[datetime.datetime.today().weekday()],
            "from_time":"12:30AM",
            "to_time":"11:59PM",
            "num_retries": 3
        }

    if time_or_day == 'Time':
        Dates = ["Monday","Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        #print Dates[datetime.datetime.today().weekday()]

        upgrade_settings = {
            "day": Dates[datetime.datetime.today().weekday()],
            "from_time":"11:57PM",
            "to_time":"11:58PM",
            "num_retries": 3
        }

    try:
        UpgradeSettingsTest(upgrade_settings)
    except:
        testComment = 'OTAP on Wrong Day did not complete because Upgrade Setting Failed.'
        printFP(testComment)
        return Global.FAIL, testComment

    printFP("Changed Upgrade Settings.. Attempting to OTAP Upgrade")
    try:
        result, comment = OTAPUpgrade(input_file_path, device_name, target_version, actionButton, timeout)
    except:
        testComment = 'OTAP on Wrong Day did not complete because OTAPUpgrade caused an exception'
        printFP(testComment)
        return Global.FAIL, testComment

    if result == Global.FAIL:
        testComment = 'OTAP was not able to perform due to invalid upgrade settings.'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'OTAP was able to perform due to invalid upgrade settings.'
        printFP(testComment)
        return Global.FAIL, testComment

def OTAPPostCheckVersion(input_file_path=None, device_names=None, target_version=None):
    if input_file_path == None or device_names==None or target_version == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToDevMan()
    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Unable to locate locations based off input file"
        printFP(testComment)
        return Global.FAIL, testComment

    for i in range(len(device_names)):
        row = GetDevice(device_names[i])
        swVerText = GetElement(row, By.XPATH, 'td[6]/span').text
        if not swVerText == target_version:
            testComment = '%s does not match target version %s' % (device_names, target_version)
            printFP(testComment)
            return Global.FAIL, testComment

    Global.driver.refresh()

    GoToDevUpgrade()

    if not GetLocationFromInput(region, sub, feeder, site):
        testComment = 'Could not find the device location'
        printFP(testComment)
        return Global.FAIL, testComment

    for i in range(len(device_names)):
        row = GetDevice(device_names[i])
        swVerText = GetElement(row, By.XPATH, 'td[5]/span').text
        if not swVerText == target_version:
            testComment = '%s does not match target version %s' % (device_names, target_version)
            printFP(testComment)
            return Global.FAIL, testComment

    return Global.PASS, ''


def OTAPPollCurrentJobs(device_name=None, polltime = 20, target_version =None, desiredJobStatus=None, desiredOtapStatus=None):
    if device_name is None or target_version is None or desiredJobStatus is None or desiredOtapStatus is None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    listOfDevices = []
    for x in range(len(device_name)):
        listOfDevices.append(device_name[x])

    # Monitor for OTAP success
    GoToCurrentJobsUpgrade()
    i = 0
    result = Global.PASS
    for i in range(polltime):
        # Refresh page
        printFP("INFO - Locating Job that contains the devices")
        try:
            allJobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
        except:
            printFP("INFO - Exception while trying to get jobs in the Current Jobs Upgrade Page")
            return Global.FAIL, 'TEST FAIL - Exception occured while trying to get jobs in the current jobs Upgrade Page'

        if len(allJobs) == 0:
            printFP("INFO - No upgrades were found.")
            return Global.FAIL, 'TEST FAIL - No upgrades were found.'
        # Iterate through the list of devices while checking for the right device serial
        devicesDone = 0
        for t in range(len(allJobs)):
            try:
                allJobs[t].click()
            except:
                pass
            if SearchJobLink(device_name):
                break
            elif t == (len(allJobs) - 1):
                printFP("INFO - Test could not locate job with all devices listed.")
                return Global.FAIL, "TEST FAIL - Test could not locate job with all devices listed."

        # Find device from list
        for n in range(len(listOfDevices)):
            DeviceRow = GetDevice(listOfDevices[n])
            # Get otap status
            printFP("INFO - Information on Device %s" % listOfDevices[n])
            jobStatus = GetText(DeviceRow, By.XPATH, "td[6]/span")
            otapStatus = GetText(DeviceRow, By.XPATH, "td[7]/span/span/a")
            printFP('INFO - Job Status: %s  OTAP Status: %s' % (jobStatus, otapStatus))
            status = GetElement(DeviceRow, By.TAG_NAME, 'a')
            status.click()
            time.sleep(1)
            msgBox = GetElement(Global.driver, By.XPATH, "//div[@class='modal-content']")
            msg = GetText(msgBox, By.CSS_SELECTOR, 'p.ng-binding')
            time.sleep(2)
            printFP('INFO - Detailed OTAP message: %s' % msg)
            closeButton = GetElement(Global.driver, By.XPATH, "//button[text()='Close']")
            closeButton.click()
            if not CheckIfStaleElement(closeButton):
                printFP("INFO - Detailed OTAP message box did not close.")

            if (jobStatus == 'IN_PROGRESS' or jobStatus == 'ABORTING' or jobStatus == 'PENDING') and (otapStatus == 'INPROGRESS' or otapStatus == 'SCHEDULED' or otapStatus == 'UNRELIABLE_CONNECTION'):
                pass
            else:
                if jobStatus == desiredJobStatus and otapStatus == desiredOtapStatus:
                    printFP("INFO - Device %s is finished and matched desired output." % listOfDevices[n])
                else:
                    result = Global.FAIL
                    printFP("INFO - Device %s is finished and did not match desired output." % listOfDevices[n])
                devicesDone += 1

        if devicesDone == len(device_name):
            break
        else:
            printFP('INFO - Not all devices were complete .. waiting 60 seconds before checking again.')
            time.sleep(60)
            Global.driver.refresh()

    # Return of otap job failed
    if result == Global.FAIL:
        testComment = 'INFO - OTAP Failed. Job status: %s OTap status: %s' % (jobStatus, otapStatus)
        printFP(testComment)
        return Global.FAIL, testComment

    #check version #
    for m in range(len(listOfDevices)):
        DeviceRow = GetDevice(listOfDevices[m])
        sw_version = GetElement(DeviceRow, By.XPATH, 'td[5]/span').text
        if sw_version == target_version:
            pass
        else:
            result = Global.FAIL
            printFP("INFO - Upgraded OTAP version on Ample does not match target version for device %s." %listOfDevices[m])

    return result, ('TEST PASS - Test upgraded with no issue.') if result == Global.PASS else ('TEST FAIL - Test did not upgrade properly and encountered issues.')

def OTAPAbort(input_file_path=None, device_name=None):
    if input_file_path == None or device_name == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    GoToDevMan()
    GoToDevUpgrade()

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate locations based off input file"
        printFP(testComment)
        return Global.FAIL, testComment

    while True:
        SelectDevice(device_name)
        DeviceRow = GetDevice(device_name)
        try:
            GetElement(DeviceRow, By.XPATH, "//*[contains(text(),'SCHEDULED']")
            time.sleep(30)
            Global.driver.refresh()
        except:
            break

    try:
        link = GetElement(DeviceRow, By.XPATH, "//a[text()='Abort']")
        printFP("INFO - Link To Click has Text: %s" %link.text)
    except:
        testComment = 'Abort link does not exist currently for this device. Device possibly already aborting.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    link.click()
    if not CheckIfStaleElement(link):
        printFP("INFO - Link did not redirect to Current Jobs - Upgrade page")
    try:
        SelectDevice(device_name)
        AbortButton = GetElement(Global.driver, By.XPATH, "//button[text()='Abort']")
        if 'disabled' in AbortButton.get_attribute('class'):
            printFP("INFO - Test is unable to abort because abort button is disabled.")
            return Global.FAIL, 'TEST FAIL - Test is unable to abort because abort button is disabled.'
        else:
            AbortButton.click()
            printFP("INFO - Test initiated abort using abort button.")
    except:
        testComment = '%s not found in current upgrade jobs page.' % device_name
        printFP(testComment)
        result = Global.FAIL
        return result, testComment

    GoToDevMan()
    GoToDevUpgrade()

    SelectDevice(device_name)
    try:
        upgradeButton = WebDriverWait(Global.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpaths['dev_upgrade_button'])))
        upgradeButton.click()
        if 'disabled' in upgradeButton.get_attribute('class'):
            printFP('Upgrade Button is unavailable for device %s that is aborting.'% device_name)
        else:
            testComment = 'Upgrade button is still available for Device performing Abort'
            printFP(testComment)
            return Global.FAIL, testComment
    except:
        printFP('Upgrade Button is unavailable for device %s that is aborting.'% device_name)

    try:
        DeviceRow = GetDevice(device_name)
        linkText = GetElement(DeviceRow, By.XPATH, "td[20]/div/span/a").text
        testComment = "Link to click has text: %s" % linkText
        printFP(testComment)
        return Global.FAIL, testComment
    except:
        printFP('No links for this device while aborting. %s' %device_name)

    return Global.PASS, 'TEST PASS - Test has begun aborting successfully.'

def OTAPRetryUpgrade(input_file_path=None, device_name=None):
    if input_file_path == None or device_name == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    GoToDevMan()
    GoToDevUpgrade()

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate locations based off input file"
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    try:
        SelectDevice(device_name)
    except:
        testComment = 'Test could not locate device %s' % device_name
        printFP(testComment)
        return Global.FAIL, testComment

    DeviceRow = GetDevice(device_name)
    try:
        try:
            retryLink = GetElement(DeviceRow, By.LINK_TEXT, 'Retry')
            retryLink.click()
            if not CheckIfStaleElement(DeviceRow):
                printFP("INFO - Did not change from Device Upgrade Page to Current Jobs Upgrade Page")
            else:
                printFP("INFO - Changed from Device Upgrade Page to Current Jobs Upgrade Page")
        except:
            testComment = 'Test ran into issues while trying to get and click Retry Link'
            printFP('INFO - ' + testComment)
            return Global.FAIL, ('TEST FAIL - ' + testComment)

        try:
            deviceCheckBox = GetElement(Global.driver, By.XPATH, "//span[text()='"+device_name+"']/../../td[1]/input[1]")
            if 'disabled' in deviceCheckBox.get_attribute('class'):
                printFP("INFO - Test is unable to Retry because device checkbox is disabled.")
                return Global.FAIL, 'TEST FAIL - Test is unable to Retry because device checkbox is disabled.'
            else:
                deviceCheckBox.click()
            RetryButton = GetElement(Global.driver, By.XPATH, "//button[text()='Retry']")
            if 'disabled' in RetryButton.get_attribute('class'):
                printFP("INFO - Test is unable to Retry because Retry button is disabled.")
                return Global.FAIL, 'TEST FAIL - Test is unable to Retry because Retry button is disabled.'
            else:
                RetryButton.click()
                printFP("INFO - Test initiated Retry operation using Retry button.")

        except:
            testComment = '%s not found in current upgrade jobs page.' % device_name
            printFP(testComment)
            result = Global.FAIL
            return result, testComment
    except:
        testComment = 'Test ran into exception while trying to retry to Retry Upgrade'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    return Global.PASS, 'TEST PASS - Test successfully retried an upgrade on a device.'

def OTAPEmptyData(input_file_path=None):
    if input_file_path == None:
        testComment = 'Missing a mandatory input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    GoToDevMan()
    GoToDevUpgrade()

    if not GetLocationFromInput(params['Region'],params['Substation'],params['Feeder'],params['Site']):
        testComment = "Unable to locate locations based off input file"
        printFP(testComment)
        return Global.FAIL, testComment

    if 'No' in NoDataAvailable('device-management-upgrade'):
        return Global.PASS, ''
    else:
        testComment = 'Data available still for this empty site; data has not been cleared.'
        printFP(testComment)
        return Global.FAIL, testComment



def OTAPUpgrade(input_file_path=None, device_name=None, target_version=None, actionButton=False, timeout=1200):
    """This test will perform an OTAP upgrade on a device, monitor the progress,
    then return PASS when the upgrade completes. It checks that the job and otap
    status show complete, and that the software version reflects the target.

    Before starting the upgrade, it will check that the device is on the correct
    starting version.

    It is built to also use the simulators, but the simulators do not support
    OTAP yet."""
    if input_file_path == None or target_version == None:
        testComment = 'Test is missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    #Navigate to Upgrade page
    params = ParseJsonInputFile(input_file_path)
    GoToDevMan()
    GoToDevUpgrade()

    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    # Start the upgrade
    if not actionButton:
        try:
            for i in range(len(device_name)):
                SelectDevice(device_name[i])
        except Exception as e:
            printFP("INFO - Unable to select the device(s)")
            return Global.FAIL, 'TEST FAIL - Unable to select the device(s)'
    try:
        upgradebutton = GetElement(Global.driver, By.XPATH, "//button[text()='Firmware Upgrade']")
        if 'disabled' in upgradebutton.get_attribute('class'):
            printFP("INFO - Upgrade button was disabled.")
            return Global.FAIL, 'TEST FAIL - Upgrade button was disabled for this test.'
        upgradebutton.click()
    except:
        testComment = 'Test failed to click Upgrade button.'
        printFP('INFO - ' + testComment)
        return Global.FAIL , 'TEST FAIL - ' + testComment

    try:
        GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_warning_pass']).click()
        printFP('INFO - Commserver or SGW has short poll interval')
    except:
        printFP('INFO - Commserver or SGW does not have short poll interval')

    try:
        upgradeTitle = GetElement(Global.driver, By.XPATH, "//span[contains(@class, 'modal-title')]").text
        printFP("INFO - Upgrade Title: %s" %upgradeTitle)
        if str(len(device_name)) + ' Device' in upgradeTitle:
            printFP("Number of Devices Selected Matches the Amount to be Upgraded.")
        else:
            printFP("Number of Devices Selected Does not Match the Amount to be Upgraded.")
    except:
        printFP("INFO - No title was displayed. Refreshing and ending test.")
        Global.driver.refresh()
        return Global.FAIL, 'TEST FAIL - No title was displayed.'

    try:
        textBox = GetElement(Global.driver, By.CSS_SELECTOR, 'div.alert.ng-isolate-scope.alert-dismissable.alert-danger')
        divElement = GetElement(textBox, By.TAG_NAME, 'div')
        textmsg = GetElement(divElement, By.TAG_NAME, 'span').text
        ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_fail_close'])
        if any(word in textmsg for word in ['not available', 'Selection contains different']):
            printFP('INFO - ' + textmsg)
            return Global.FAIL, 'TEST FAIL - ' + textmsg
    except:
        singleselectElement = GetElement(Global.driver, By.TAG_NAME, 'single-select')
        dropdown = GetElement(singleselectElement, By.XPATH, xpaths['dev_upgrade_sw_dropdown'])
        dropdown.click()
        dropdownMenu = GetElement(Global.driver, By.XPATH, xpaths['dev_upgrade_sw_dropdown_menu'])
        if SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', target_version):
            print "Found upgrade version %s" % target_version
        else:
            ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_fail_close'])
            testComment = "Test did not find upgrade version %s. Please upload the firmware bundle for this version" % target_version
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment
    try:
        upgradeStart = GetElement(Global.driver, By.XPATH, "//button[text()='Start FW Upgrade']")
        if 'disabled' in upgradeStart.get_attribute('class'):
            closeButton = GetElement(Global.driver, By.XPATH, 'glyphicon-remove-circle')
            closeButton.click()
            printFP("INFO - Upgrade button was disabled.")
            return Global.FAIL, 'TEST FAIL - Upgrade button was disabled for this test.'
        upgradeStart.click()
    except:
        testComment = 'Test failed to click Start FW Upgrade button.'
        printFP('INFO - ' + testComment)
        return Global.FAIL , 'TEST FAIL - ' + testComment

    try:
        msg = GetText(Global.driver, By.XPATH, xpaths['dev_upgrade_fail_msg'], True)
        if any( word in msg for word in ['selected day','selected time','Configuration']):
            ClickButton(Global.driver, By.XPATH, xpaths['dev_upgrade_fail_close'])
            printFP('INFO - ' + msg)
            return Global.FAIL, 'TEST FAIL - ' + msg
    except:
        printFP("INFO - No error messages were displayed.")

    for i in range(len(device_name)):
        SelectDevice(device_name[i])
        devicesfwupgradestatus = FilteredDataFromTableMapping('Serial Number', 'FW Upgrade Status', 'device-management')
        try:
            upgradeButton = WebDriverWait(Global.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Firmware Upgrade']")))
            if 'disabled' in upgradeButton.get_attribute('class'):
                printFP("After initiating upgrade, device cannot click upgrade again.")
            else:
                testComment = 'Upgrade Button is still click-able despite starting Upgrade for the device: {}' .format(device_name[i])
                printFP(testComment)
                return Global.FAIL, testComment
            upgradeButton.click()
        except:
            printFP("After initiating upgrade, device cannot click upgrade again.")

        if str(devicesfwupgradestatus[device_name[i]]) == 'INPROGRESS':
            printFP('INFO - Device firmware upgrade is started. Current Status: INPROGRESS')
        elif str(devicesfwupgradestatus[device_name[i]]) == 'FAILED':
            fwstatusmsg = GetFWSatusMsgFromFWScreen(device_name[i])
            testComment = 'Test Fail - Device firmware upgrade is failed immediately. Current Status: FAILED and FW Status msg: {}' .format(fwstatusmsg)
            return Global.FAIL, testComment

    return Global.PASS, 'TEST PASS - Test started an upgrade for selected devices'

def PersistenceOfFilters(input_file_path, tabname, selectfilters, navigate_by, go_to, refresh_page, logout, username, password, profile_status_list, profile_name_list, device_status_list, fw_version_list, nw_grp_list, comm_type_list, device_state_list, serial_number_list, fw_status_list):

    allfilters = {"device_status_list": device_status_list, "fw_version_list": fw_version_list, "nw_grp_list": nw_grp_list, "comm_type_list": comm_type_list, "device_state_list": device_state_list, "serial_number_list": serial_number_list, "profile_status_list": profile_status_list, "profile_name_list": profile_name_list, "fw_status_list": fw_status_list}
    params = ParseJsonInputFile(input_file_path)
    
    GoToDevMan()
    Global.driver.refresh()
    time.sleep(5)
    if tabname == 'Configurations':
        GoToDevConfig()
        current_test_page = GoToDevConfig
    elif tabname == 'Firmware Upgrade':
        GoToDevUpgrade()
        current_test_page = GoToDevUpgrade
    elif tabname == 'Inactive Device Report':
        GoToDevInactDevRep()
        current_test_page = GoToDevInactDevRep
    elif tabname == 'Manage Devices':
        GoToDevMan()
        current_test_page = GoToDevMan

    if go_to == 'rootnode':
        GetRootNode()
        params['Region'], params['Substation'], params['Feeder'], params['Site']
        current_test_node = GetRootNode
    elif go_to == 'region':
        GetRegionFromTop(params['Region'])
        current_test_node = GetRegionFromTop
    elif go_to == 'substation':
        GetSubstationFromTop(params['Region'], params['Substation'])
        current_test_node = GetSubstationFromTop
    elif go_to == 'feeder':
        GetFeederFromTop(params['Region'], params['Substation'], params['Feeder'])
        current_test_node = GetFeederFromTop

    if not selectfilters:
        for item in list(allfilters):
            allfilters[item] = []
            allfilters[item] = ['Show All']
    time.sleep(3)
    try:
        selectFiltersByDeviceStatusManageDevice(allfilters['device_status_list'], tabname)
    except:
        pass
    try:
        selectFiltersByCommunicationTypeManageDevice(allfilters['comm_type_list'])
    except:
        pass
    try:
        selectFiltersByDeviceStateManageDevice(allfilters['device_state_list'], tabname)
    except:
        pass
    try:
        selectFiltersByFWVersionManageDeviceScreen(allfilters['fw_version_list'], tabname)
    except:
        pass
    try:
        selectFiltersByNetworkGroupManageDeviceScreen(allfilters['nw_grp_list'], tabname)
    except:
        pass
    try:
        selectFiltersBySerialNumber(allfilters['serial_number_list'])
    except:
        pass
    try:
        selectFiltersByProfileName(allfilters['profile_name_list'])
    except:
        pass
    try:
        selectFiltersByProfileStatus(allfilters['profile_status_list'])
    except:
        pass
    try:
        selectFiltersByUpgradeStatus(allfilters['fw_status_list'])
    except:
        pass

    GetElement(Global.driver, By.XPATH, "//button[text()='Apply']").click()
    time.sleep(4)

    results = []

    if not selectfilters:
        nodataavailable = NoDataAvailable('device-management')
        if nodataavailable == "No Data Available":
            testComment = 'TEST FAIL - Found "No Data Available" when selected "ShowAll" in all filters and applied'
            printFP(testComment)
            results.append(Global.FAIL)
        else:
            testComment = 'TEST PASS - Data displayed when selected "ShowAll" in all filters and applied '
            printFP(testComment)
            results.append(Global.PASS)
    elif selectfilters:
        ui_data_dict = {}
        nodataavailable = NoDataAvailable('device-management')
        if nodataavailable == "No Data Available":
            testComment = 'TEST FAIL - Found "No Data Available" when applied filters.Enter filters which has data and try again..'
            printFP(testComment)
            results.append(Global.FAIL)
        if device_status_list:
            device_status_list_from_ui = FilteredDataFromTable('Device Status', 'device-management')
            ui_data_dict["device_status_list_from_ui"] = device_status_list_from_ui
        else:
            ui_data_dict["device_status_list_from_ui"] = []
        if fw_version_list:
            fw_version_list_from_ui = FilteredDataFromTable('FW Version', 'device-management')
            ui_data_dict["fw_version_list_from_ui"] = fw_version_list_from_ui
        else:
            ui_data_dict["fw_version_list_from_ui"] = []
        if nw_grp_list:
            nw_grp_list_from_ui = FilteredDataFromTable('Network Group', 'device-management')
            ui_data_dict["nw_grp_list_from_ui"] = nw_grp_list_from_ui
        else:
            ui_data_dict["nw_grp_list_from_ui"] = []
        if comm_type_list:
            comm_type_list_from_ui = FilteredDataFromTable('Communication Type', 'device-management')
            ui_data_dict["comm_type_list_from_ui"] = comm_type_list_from_ui
        else:
            ui_data_dict["comm_type_list_from_ui"] = []
        if device_status_list:
            device_state_list_from_ui = FilteredDataFromTable('Device State', 'device-management')
            ui_data_dict["device_state_list_from_ui"] = device_state_list_from_ui
        else:
            ui_data_dict["device_state_list_from_ui"] = []
        if serial_number_list: 
            serial_number_list_from_ui = FilteredDataFromTable('Serial Number', 'device-management')
            ui_data_dict["serial_number_list_from_ui"] = serial_number_list_from_ui
        else:
            ui_data_dict["serial_number_list_from_ui"] = []
        if profile_name_list:
            profile_name_list_from_ui = FilteredDataFromTable('Profile Name', 'device-management')
            ui_data_dict["profile_name_list_from_ui"] = profile_name_list_from_ui
        else:
            ui_data_dict["profile_name_list_from_ui"] = []
        if profile_status_list:
            profile_status_list_from_ui = FilteredDataFromTable('Profile Status', 'device-management')
            ui_data_dict["profile_status_list_from_ui"] = profile_status_list_from_ui
        else:
            ui_data_dict["profile_status_list_from_ui"] = []
        if fw_status_list:
            fw_status_list_from_ui = FilteredDataFromTable('FW Upgrade Status', 'device-management')
            ui_data_dict["fw_status_list_from_ui"] = fw_status_list_from_ui
        else:
            ui_data_dict["fw_status_list_from_ui"] = []

        i=0        
        for filtercheck in list(allfilters):
            if filtercheck:
                tmpnameforuilist = list(allfilters)[i] + '_from_ui'
                if all(str(x) in allfilters[filtercheck] for x in ui_data_dict[tmpnameforuilist]):
                    testComment = 'TEST PASS - displayed {} matched with the filters applied.' .format(filtercheck)
                    printFP(testComment)
                    results.append(Global.PASS)
                else:
                    testComment = 'TEST FAIL - displayed {} are not matched with the filters applied.' .format(filtercheck)
                    printFP(testComment)
                    results.append(Global.FAIL)
            i = i+1

    if not navigate_by == '' or refresh_page or logout:
        if navigate_by == 'node':
            GetSiteFromTop(params['Region'], params['Substation'], params['Feeder'], params['Site'])
            time.sleep(1)
            if go_to == 'rootnode':
                GetRootNode()
            elif go_to == 'region':
                GetRegionFromTop(params['Region'])
            elif go_to == 'substation':
                GetSubstationFromTop(params['Region'], params['Substation'])
            elif go_to == 'feeder':
                GetFeederFromTop(params['Region'], params['Substation'], params['Feeder'])

        elif navigate_by == 'tab':
            GoToLineMon()
            time.sleep(3)
            GoToDevMan()
            current_test_page()     
            time.sleep(2)
        elif refresh_page:
            Global.driver.refresh()
            time.sleep(5)
        elif logout:
            Logout()
            time.sleep(3)
            Login(username, password)
            time.sleep(3)
            GoToDevMan()
            current_test_page()
            if go_to == 'rootnode':
                GetRootNode()
            elif go_to == 'region':
                GetRegionFromTop(params['Region'])
            elif go_to == 'substation':
                GetSubstationFromTop(params['Region'], params['Substation'])
            elif go_to == 'feeder':
                GetFeederFromTop(params['Region'], params['Substation'], params['Feeder'])
        
        filters_xpath = ["communicationTypeSettings.list", "statusSettings.list", "softwareVersionsSettings.list", "stateSettings.list", "networkGroupsSettings.list", "networkGroupSelection.list", "profileStatusSelection.list", "profileNameSelection.list", "fwUpgradeStatusSelection.list", "fwVersionSelection.list", "deviceStatusSelection.list", "deviceStateSelection.list"]
        currentfiltervalues = []
        time.sleep(4)
        for filterxpath in filters_xpath:
            value = filterDisplayedValue(filterxpath)
            if value:
                if value.strip() == 'Select':
                    currentfiltervalues.append('Show All')
                else:
                    currentfiltervalues.append(value.strip())
        printFP(currentfiltervalues)

        usergiven_values = allfilters['comm_type_list'] + allfilters['device_status_list'] + allfilters['fw_version_list'] + allfilters['device_state_list'] + allfilters['nw_grp_list'] + allfilters['profile_status_list'] + allfilters['profile_name_list'] + allfilters['fw_status_list']
        printFP(usergiven_values)

        if not navigate_by == '':
            if all(str(x) in usergiven_values for x in currentfiltervalues):
                testComment = 'TEST PASS - Values matched after navigating to some other node/tab and returning to same node'
                printFP(testComment)
                results.append(Global.PASS)
            else:
                testComment = 'TEST FAIL - Values did not matched after navigating to some other node/tab and returning to same node'
                printFP(testComment)
                results.append(Global.FAIL)
        elif refresh_page and logout:
            if not all(str(x) in currentfiltervalues for x in usergiven_values):
                testComment = 'TEST PASS - Values are not matched after refreshing the page/logout and login'
                printFP(testComment)
                results.append(Global.PASS)            
            else:
                testComment = 'TEST FAIL - Values are matched after refreshing the page/logout and login'
                printFP(testComment)
                results.append(Global.FAIL)

    if Global.FAIL in results:
        testComment = 'TEST FAIL - Some filters are not working.'
        printFP(testComment)
        return Global.FAIL, testComment
    else:
        testComment = 'TEST PASS - All filters are working fine.'
        printFP(testComment)
        return Global.PASS, testComment
