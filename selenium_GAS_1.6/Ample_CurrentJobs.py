import datetime
from time import strftime
from Utilities_Ample import *
from Utilities_Framework import *
from Ample_DevMan import *
from Ample_NegativeTests import *


def SearchForDeviceCurrentJobs(page=None, device=None):
    if not (page and device):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    if page == 'Config':
        GoToCurrentJobsConfig()
    elif page == 'Upgrade':
        GoToCurrentJobsUpgrade()
    else:
        testComment = 'Test received invalid input for the page parameter'
        printFP("INFO - " + testComment)
        return Global.FAIL, ('TEST FAIL - ' + testComment)

    time.sleep(2)
    if not SearchBar(device):
        testComment = 'Test ran into an exception error when searching.'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    searchReturn = GetElement(Global.driver, By.XPATH, "//ul[contains(@class,'node-search-dropdown')]")
    if not ('ng-hide' in GetElement(searchReturn, By.XPATH, "//span[text()='No Data Available']/..").get_attribute('class')):
        printFP("TEST INFO - No Data Available while searching for % s" % device)
        return Global.FAIL, "TEST FAIL - No Data Available while searching for %s" % device
    else:
        printFP("TEST INFO - Inputting %s generated a list." % device)
        return Global.PASS, "TEST PASS - Inputting %s generated a list." % device


def ClickThroughJobsTest(page=None):
    printFP("Navigating to Current Jobs - %s Page." % page)
    if page == 'Config':
        GoToCurrentJobsConfig()
    elif page == 'Upgrade':
        GoToCurrentJobsUpgrade()
    else:
        printFP('INFO - Test was given a bad value for the argument, page.')
        return Global.FAIL, 'TEST FAIL - Test was given a bad value for the argument, page.'

    time.sleep(1)

    try:
        jobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
    except:
        jobs = []

    result = Global.PASS
    if len(jobs) < 2:
        printFP("INFO - There are less than 2 jobs in Current Jobs - Configuration page. Will skip this portion of the test.")
    else:
        statusConfig = []
        for i in range(len(jobs)):
            statusConfig.append(GetElement(jobs[i], By.XPATH, "span[1]/div").get_attribute("class"))

        for i in range(len(jobs)):
            jobs[i].click()
            time.sleep(2)
            if jobs[i].get_attribute('id') != GetElement(jobs[i], By.XPATH, 'span[2]').text:
                printFP("INFO - Job Name (%s) does not match the Job Link ID (%s)." % (GetElement(jobs[i], By.XPATH, 'span[2]').text, jobs[i].get_attribute('id')))
                result = Global.FAIL
            else:
                printFP("INFO - Job Name (%s) matches the Job Link ID (%s)." % (GetElement(jobs[i], By.XPATH, 'span[2]').text, jobs[i].get_attribute('id')))

            if GetElement(jobs[i], By.XPATH, "span[1]/div").get_attribute("class") != statusConfig[i]:
                printFP("INFO - Navigating to job %s changed the Status" % jobs[i].get_attribute('id'))
                result = Global.FAIL
            else:
                printFP("INFO - Navigating to job %s did not change the status" % jobs[i].get_attribute('id'))

    printFP("Navigating to Current Jobs - Upgrade Page.")
    GoToCurrentJobsUpgrade()
    time.sleep(1)

    try:
        jobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
    except:
        jobs = []

    result = Global.PASS
    if len(jobs) < 2:
        printFP("INFO - There are less than 2 jobs in Current Jobs - Upgrade page. Will skip this portion of the test.")
    else:
        statusConfig = []
        for i in range(len(jobs)):
            statusConfig.append(GetElement(jobs[i], By.XPATH, "span[1]/div").get_attribute("class"))

        for i in range(len(jobs)):
            jobs[i].click()
            time.sleep(1)
            if jobs[i].get_attribute('id') != GetElement(jobs[i], By.XPATH, 'span[2]').text:
                printFP("INFO - Job Name (%s) does not match the Job Link ID (%s)." % (GetElement(jobs[i], By.XPATH, 'span[2]').text, jobs[i].get_attribute('id')))
                result = Global.FAIL
            else:
                printFP("INFO - Job Name (%s) matches the Job Link ID (%s)." % (GetElement(jobs[i], By.XPATH, 'span[2]').text, jobs[i].get_attribute('id')))

            if GetElement(jobs[i], By.XPATH, "span[1]/div").get_attribute("class") != statusConfig[i]:
                printFP("INFO - Navigating to job %s changed the Status" % jobs[i].get_attribute('id'))
                result = Global.FAIL
            else:
                printFP("INFO - Navigating to job %s did not change the status" % jobs[i].get_attribute('id'))

    if result == Global.FAIL:
        testComment = "Job details changed while navigating during the test. Please refer to log file for more information."
    else:
        testComment = "Job details did not change while navigating during the test."
    printFP("INFO - " + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)


def JobStatusToolTip(page=None):
    if page == 'Config':
        GoToCurrentJobsConfig()
    elif page == 'Upgrade':
        GoToCurrentJobsUpgrade()
    else:
        printFP('INFO - One of the test parameters is not valid.')
        return Global.FAIL, 'TEST FAIL - One of the test parameters is not valid.'
    time.sleep(2)

    result = Global.PASS
    printFP('INFO - Locating Device on Jobs List for Current Jobs - %s' % page)
    jobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
    if len(jobs) == 0:
        printFP('INFO - No jobs found on this page.')
    else:
        for i in range(len(jobs)):
            Tooltip = GetElement(jobs[i], By.XPATH, 'span[1]/div').get_attribute('tooltip')
            Class = GetElement(jobs[i], By.XPATH, 'span[1]/div').get_attribute('class')
            ColorRGB = GetElement(jobs[i], By.XPATH, 'span[1]/div').value_of_css_property("background-color")
            if Tooltip == 'Success' and (Class == 'job-status-SUCCESS' if page == 'Config' else Class == 'job-status-COMPLETED') and str(ColorRGB) == 'rgba(2, 160, 38, 1)':
                printFP("INFO - Job %s's status is SUCCESS and it's tooltip displays %s and the icon color was GREEN" % (jobs[i].get_attribute('id'), Tooltip))
            elif Tooltip == 'Failure' and Class == 'job-status-FAILURE' and str(ColorRGB) == 'rgba(202, 0, 19, 1)':
                printFP("INFO - Job %s's status is FAILURE and it's tooltip displays %s and the icon color was RED" % (jobs[i].get_attribute('id'), Tooltip))
            elif Tooltip == 'In Progress' and Class == 'job-status-INPROGRESS' and str(ColorRGB) == 'rgba(255, 255, 255, 1)':
                printFP("INFO - Job %s's status is INPROGRESS and it's tooltip displays %s and the icon color was WHITE" % (jobs[i].get_attribute('id'), Tooltip))
            else:
                result = Global.FAIL
                printFP("INFO - Job %s's status is %s and it's tooltip displays %s and it's icon color has RGB code %s" % (jobs[i].get_attribute('id'), Class, Tooltip, str(ColorRGB)))

    if result == Global.FAIL:
        testComment = 'One or more jobs had mismatching tooltiip and jobstatus while checking Current Jobs - Upgrade Page.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    else:
        testComment = 'No jobs had mismatching tooltip and jobstatuses in Current Jobs Configuration and Upgrade Page'
        printFP('INFO - ' + testComment)
        return Global.PASS, 'TEST PASS - ' + testComment


def ValidateCurrentJobsConfigDetails(input_file_path=None, device_names=None, config=None, device_detail_json=None):
    if not (device_names and device_detail_json):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    devicedetails = ParseJsonInputFile(device_detail_json)
    try:
        result, msg = configureDevice(input_file_path, device_names, config, False, False)
    except:
        testComment = 'Configuration of device caused an exception. Please refer to log file for more information.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    if result == Global.FAIL:
        return Global.FAIL, msg

    time.sleep(2)
    GoToCurrentJobsConfig()
    time.sleep(2)
    result = Global.PASS

    printFP("INFO - Checking Device details under Device List")
    ClickButton(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]")
    time.sleep(1)
    divElement = GetElement(Global.driver, By.XPATH, "//div[@class = 'dropdown-menu column-wrap']")
    inputElements = GetElements(divElement, By.TAG_NAME, 'input')
    for element in inputElements:
        if not element.is_selected():
            element.click()
    ClickButton(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]")
    time.sleep(1)
    JobTable = GetElement(Global.driver, By.CLASS_NAME, 'jobs-list-table')
    result = Global.PASS

    for i in range(len(device_names)):
        JobTbody = GetElement(JobTable, By.TAG_NAME, 'tbody')
        DeviceRow = FindRowInTable(JobTbody, device_names[i])
        printFP("Checking device details for device %s" % device_names[i])
        for n in range(0, 8):
            col = GetElement(Global.driver, By.XPATH, "//thead/tr/th[" + str(n + 2) + "]").text
            printFP('INFO - Column Text = %s ' % col)
            if n == 2 or n == 4:
                pass
            elif n == 6:
                date = strftime('%m/%d/%Y')
                t1 = datetime.datetime.strptime(date, '%m/%d/%Y')
                dateOnAmple = GetElement(DeviceRow, By.XPATH, "td[" + str(n + 2) + "]/span").text
                try:
                    t2 = datetime.datetime.strptime(dateOnAmple, '%m/%d/%Y')
                except ValueError:
                    printFP("INFO - Incorrect date format, should be MM/DD/YYYY HH:MM:SS")
                    result = Global.FAIL
                if not (t1 == t2):
                    result = Global.FAIL
                    printFP('INFO - Last Modified Time does not match for device %s' % device_names[i])
                else:
                    printFP('INFO - Last Modified Time does match for device %s' % device_names[i])
            elif not GetElement(DeviceRow, By.XPATH, "td[" + str(n + 2) + "]/span").text == devicedetails[device_names[i]][col]:
                printFP('INFO - Column %s does not match for device %s.' % (col, device_names[i]))
                result = Global.FAIL
            else:
                printFP('INFO - %s matches for device %s.' % (col, device_names[i]))

    if result == Global.PASS:
        testComment = 'Device details matched for all devices.'
    else:
        testComment = 'Device details did not match for all devices. Please refer to log file for more information.'

    printFP('INFO - ' + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)


def ValidateRetryButtonConfig(input_file_path=None, device_name=None, config=None):
    if not (input_file_path and device_name and config):
        testComment = 'Test is missing mandatory input parameter(s).'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    try:
        configureDevice(input_file_path, [device_name], config, False, False)
    except:
        testComment = 'Configuration of device caused an exception. Please refer to log file for more information.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    GoToCurrentJobsConfig()
    time.sleep(1)
    result = Global.PASS
    foundDevice = False

    while(True):
        printFP('INFO - Locating Device on Jobs List')
        jobList = GetElement(Global.driver, By.XPATH, "//ol[@class='listview-ol']")
        jobs = GetElements(jobList, By.CLASS_NAME, 'li')
        for i in range(len(jobs)):
            jobs[i].click()
            JobTable = GetElement(Global.driver, By.CLASS_NAME, 'jobs-list-table')
            JobTbody = GetElement(JobTable, By.TAG_NAME, 'tbody')
            DeviceRow = FindRowInTable(JobTbody, device_name)
            if DeviceRow is not None:
                foundDevice = True
                break

        if not foundDevice:
            testComment = 'Test did not locate specific device inside job table after configuration.'
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

        JobTable = GetElement(Global.driver, By.CLASS_NAME, 'jobs-list-table')
        JobTbody = GetElement(JobTable, By.TAG_NAME, 'tbody')
        DeviceRow = FindRowInTable(JobTbody, device_name[i])
        time.sleep(1)
        DeviceStatus = GetElement(DeviceRow, By.XPATH, 'td[6]/span').text
        RetryButton = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Retry')]").get_attribute('class')
        RetryAllButton = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Retry All')]").get_attribute('class')

        if DeviceStatus == 'SUCCESS' or DeviceStatus == 'INPROGRESS':
            if 'disabled' in RetryButton and 'disabled' in RetryAllButton:
                printFP('INFO - Both Retry Button and Retry All Button are disabled while Device Status is %s' % DeviceStatus)
            else:
                printFP('INFO - One or more of the Buttons are not disabled while Device Status is %s' % DeviceStatus)
                result = Global.FAIL

            if DeviceStatus == 'SUCCESS':
                break
            else:
                time.sleep(30)
                Global.driver.refresh()

        elif DeviceStatus == 'FAILED':
            if 'disabled' in RetryButton and 'disabled' in RetryAllButton:
                printFP('INFO - Retry button and Retry All Button is disabled while the configuration failed.')
                result = Global.FAIL
            else:
                printFP('INFO - Retry button and Retry All button is not disabled while the configuration failed.')
            break

    if result == Global.FAIL:
        testComment = 'Retry and Retry All button is available outside of failed configurations.'
    else:
        testComment = 'Retry and Retry All button is available only for failed configurations.'

    printFP('INFO - ' + testComment)
    return result, 'TEST PASS - ' + testComment if result == Global.PASS else 'Test FAIL - ' + testComment


def ValidateJobStatusConfig(input_file_path=None, device_name=None, config=None):
    if not (input_file_path and device_name and config):
        testComment = 'Test is missing mandatory input parameter(s).'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    try:
        configureDevice(input_file_path, [device_name], config, False, False)
    except:
        testComment = 'Configuration of device caused an exception. Please refer to log file for more information.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    GoToCurrentJobsConfig()
    time.sleep(1)
    foundDevice = False

    while(True):
        printFP('INFO - Locating Device on Jobs List')
        jobList = GetElement(Global.driver, By.XPATH, "//ol[@class='listview-ol']")
        jobs = GetElements(jobList, By.CLASS_NAME, 'li')
        for i in range(len()):
            jobs[i].click()
            JobTable = GetElement(Global.driver, By.CLASS_NAME, 'jobs-list-table')
            JobTbody = GetElement(JobTable, By.TAG_NAME, 'tbody')
            DeviceRow = FindRowInTable(JobTbody, device_name)
            if DeviceRow is not None:
                foundDevice = True
                JobStatusIcon = GetElement(jobs[i], By.XPATH, 'span[1]/div').get_attribute('class')
                break

        if not foundDevice:
            testComment = 'Test did not locate specific device inside job table after configuration.'
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

        DeviceStatus = GetElement(DeviceRow, By.XPATH, 'td[6]/span').text
        if not (DeviceStatus in JobStatusIcon):
            testComment = 'Device %s attempted to configure and the job status icon (%s) does not match actual Job Status(%s) in table.' % device_name, JobStatusIcon, DeviceStatus
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment
        else:
            printFP('INFO - Device %s has job status icon %s and matches Job Status %s on table.' % device_name, JobStatusIcon, DeviceStatus)

        if DeviceStatus == 'SUCCESS' or DeviceStatus == 'FAILURE':
            break
        else:
            time.sleep(30)
            Global.driver.refresh()

        testComment = 'Job Statuses Icon matched Job Status on table for Device'
        printFP('INFO - ' + testComment)
        return Global.PASS, 'TEST PASS - ' + testComment


def ValidateUpgradeDetails(device_names=None):
    if not (device_names):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    printFP("INFO - Verifying Current Jobs Upgrade Page Details")
    time.sleep(1)
    GoToCurrentJobsUpgrade()

    if not VerifyDeviceListInTable(device_names):
        testComment = 'Test could not locate a job that contained all test devices'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    result = Global.PASS
    UpgradeInfo = GetElement(Global.driver, By.XPATH, "//div[@class='job-status margin-t-5']")
    UpgradeInfoValues = GetElements(UpgradeInfo, By.TAG_NAME, 'span')
    while True:
        for i in range(len(UpgradeInfoValues)):
            if i == 0:
                GoToUpdateProfile()
                time.sleep(1)
                firstName = GetElement(Global.driver, By.ID, 'firstName').get_attribute('value')
                middleName = GetElement(Global.driver, By.ID, 'middleName').get_attribute('value')
                lastName = GetElement(Global.driver, By.ID, 'lastName').get_attribute('value')
                time.sleep(1)
                GetElement(Global.driver, By.CLASS_NAME, 'close-icon').click()

                if not (firstName and middleName and lastName):
                    name = 'Admin'
                else:
                    name = firstName + ' ' + middleName + ' ' + lastName
                if name == UpgradeInfoValues[i].text:
                    printFP('INFO - Created By Value matches.')
                else:
                    printFP('INFO - Created By Value does not match.')
                    result = Global.FAIL
            elif i == 1:
                t1 = datetime.datetime.strptime(strftime('%m/%d/%y'), '%m/%d/%y')
                t2 = datetime.datetime.strptime(UpgradeInfoValues[i].text, '%m/%d/%y')
                if not (t1 == t2):
                    result = Global.FAIL
                    printFP('INFO - Created On does not match.')
                else:
                    printFP('INFO - Created On does match.')
            elif i == 2:
                if str(len(GetElements(Global.driver, By.XPATH, "//tr[@ng-repeat='device in $data']"))) == UpgradeInfoValues[i].text:
                    printFP('INFO - Number of Devices matches.')
                else:
                    result = Global.FAIL
                    printFP('INFO - Number of Devices does not match.')
            else:
                if i == 3:
                    xpathString = "//a[text()='UNRELIABLE_CONNECTION' or text()='INPROGRESS']"
                elif i == 4:
                    xpathString = "//a[text()='UPGRADE_COMPLETE']"
                elif i == 5:
                    xpathString = "//a[text()='FAILED' or text()='ABORTED']"
                try:
                    value = str(len(GetElements(Global.driver, By.XPATH, xpathString)))
                except:
                    value = '0'
                if value == UpgradeInfoValues[i].text:
                    printFP('INFO - Number of devices that are %s does match.' % ('In Progress' if i == 3 else ('Success' if i == 4 else 'Fail')))
                else:
                    printFP('INFO - Number of devices that are %s does not match.' % ('In Progress' if i == 3 else ('Success' if i == 4 else 'Fail')))
                    result = Global.FAIL

        if len(GetElements(Global.driver, By.XPATH, "//a[text()='UNRELIABLE_CONNECTION' or text()='INPROGRESS']")) == 0:
            break
        else:
            time.sleep(50)
            Global.driver.refresh()
            time.sleep(10)

    if result == Global.FAIL:
        testComment = 'Upgrade Details failed at one point in the test. Please refer to log for more information.'
    else:
        testComment = 'Upgrade Details were consistent at all points of the test.'
    printFP('INFO - ' + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)
