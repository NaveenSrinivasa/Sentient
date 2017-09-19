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

def NumberOfErrorsSupportedForAFailedMTFUpload():
    '''This Method will check number of error lines in MTF file is greater then 50 lines,
    number of error lines shouldn't be restricted to any number!'''
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
    if not match:
        testComment = 'Test Fail - Unable to scroll when MTF file upload has more than 50 error messages'
        printFP(testComment)
        return Global.FAIL, testComment
    else:
        testComment='Test Pass - Able to scroll when MTF file upload has more then 50 error message lines'
        printFP(testComment)
        return Global.PASS, testComment


def MTFErrorFormatToIndicateColumnHeadingInsteadOfColumnNumber(input_file_path):
    '''This method is to Indicate Column heading instead of column number,
    when there are errors in MTF file'''
    errorpopup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
    errormessage = GetElement(errorpopup, By.TAG_NAME,'p')
    errormessage.click()
    errormsg = errormessage.text.strip()
    errormsg = errormsg.replace('"','')
    errormsg = ''.join(errormsg.split('\n'))
    errormsg = errormsg.split('Line')
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


def ExportErrorLogForFailedMTF(downloadfolder=None):
    #This method is to export the error messages of MTF file to text file.
    if downloadfolder == None:
        testComment = "Test Fail - Missing download folder path"
        printFP(testComment)
        return Global.FAIL, testComment
    errorText = GetElement(Global.driver, By.XPATH, "//p[@ng-bind-html='details']").text
    #########################################################################################################################
    #                        PARSER FOR UPLOAD MTF ERROR BOX
    # Since this is UTF-8, we need to parse the entire thing.
    # string will hold the parsed string until the new line.
    # strings will hold all the error lines that Ample has.
    string = ""
    strings = []
    #Using a for loop, you can only parse letter by letter only.
    for x in errorText:
        #if you find new line, then put the string into the array and reset string to empty.
        if x == '\n':
            #We only want to move strings that contain Line.
            if 'Line' in string:
                strings.append(string)
            #Clear the string regardless if it contains Line or not.
            string = ""
        else:
            #Concatenate the string with each letter.
            string = string + x
    #Last line will not be added since there is no new line and it is an EOF (will find better solution to this)
    if 'Line' in string:
        strings.append(string)
    dl_button = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Download')]")
    dl_button.click()
    #Wait for it to finish downloading
    time.sleep(10)
    # Place where downloaded file exists
    location = downloadfolder + 'error_messages.txt'
    #Opening the downloaded file and reading its content
    if os.path.exists(location):
        with open(location,'r') as fp:
            num_err_file = 0
            num_err_ample = len(strings)
            for line in fp:
                error_line = line.strip().replace("   ", " ").replace("  ", " ")
                num_err_file += 1
                #We want to start at 5 because that's where the error messages start in the file.
                if num_err_file < 5:
                    continue
                else:
                    if error_line in strings:
                        strings.remove(error_line)
                    else:
                        testComment = 'Test could not find this line in downloaded file "{}"' .format(error_line)
                        printFP("Test Fail - " + testComment)
                        return Global.FAIL, testComment
            if (num_err_file - 4) != num_err_ample:
                testComment = 'The amount of errors on Ample error window does not match the downloaded error log.'
                printFP("INFO - " + testComment)
                return Global.FAIL, ''
    else:
        testComment = "INFO - Test did not successfully download file. Please verify issue."
        printFP(testComment)
        return Global.FAIL, testComment
    #After reading content of downloaded file, deleting the opened file
    try:
        os.remove(location)
    except OSError as e:
        printFP(e)
        return Global.FAIL, 'TEST FAIL - ' + e
    time.sleep(1)
    testComment = 'TEST PASS - GUI error message is matched in the downloaded file'
    printFP(testComment)
    return Global.PASS, testComment


def ASCIICharSetValidationForAllFieldsInMTF():
    '''This method will check non- ascii character for all the fields in MTF file and
    if exists it will throw an error message.'''
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
    if len(nonascii) > 0:
        testComment = 'Test Pass- MTF File failed to upload with Non-ASCII characters in the MTF file'
        printFP(testComment)
        return Global.PASS , testComment
    else:
        testComment = 'Test Fail - MTF File upload successful with Non-ASCII characters in the MTF file'
        printFP(testComment)
        return Global.FAIL , testComment


def UploadMTFNegativeTestValidation(input_file_path, list_of_errors, validateerror=False, validateargs=None):
    '''This method will check whether multiple devices are uploaded with same DNP address'''
    if input_file_path == None:
        testComment = "Test Fail - Missing a mandatory parameter."
        printFP(testComment)
        return Global.FAIL, testComment
    printFP("INFO - Going to System Admin Page")
    GoToSysAdmin()
    time.sleep(2)
    printFP('INFO - Uploading the MTF File')
    UploadMTF(input_file_path)
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(2)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "Failed to upload" in returnMessage and not validateerror:
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
        for error in list_of_errors:
            if error in errormsg:
                testComment = 'INFO - Expected error message : {} is matched with GUI error message' .format(error)
                printFP(testComment)
            else:
                testComment = 'Test Fail - Expected error message : {} is not matched with GUI error message : {}' .format(error, errormsg)
                printFP(testComment)
                return Global.FAIL , testComment
        testComment = 'Test Pass- list of expected error messages are matched with GUI error messages'
        printFP(testComment)
        return Global.PASS , testComment
    elif "Failed to upload" in returnMessage and validateerror:
        GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
        time.sleep(2)
        validate_method_name = validateargs['validatemethodname']
        printFP('External validate method for this negative case: {}' .format(validate_method_name))
        del validateargs['validatemethodname']
        args = validateargs
        result, testComment = globals()[validate_method_name](**args)
        closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
        closebutton.click()
        return result, testComment
    else:
        testComment = 'Test Fail - Invalid MTF Uploaded Successfully'
        printFP(testComment)
        return Global.FAIL, testComment

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


def VerifyNumberOfErrorsOnMTFFile():
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
    #Scrolling the page to see complete error message details
    lines = GetElement(popup, By.TAG_NAME,'p')
    time.sleep(2)
    Global.driver.execute_script("window.scrollTo(0,0/6)")
    if line_count == 151:
        testComment = 'Test Pass - The number of errors listed is equal to the number of errors we created on the bad MTF file'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment='Test Fail - The number of errors listed is NOT equal to the number of errors we created on the bad MTF file'
        printFP(testComment)
        return Global.FAIL, testComment


def ImportMTFNoGPSCoordinates(mtf_full_path=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""

    # Generate a temporary mtf with only 1 device
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
        overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
        if not overridegpsstatus:
            testComment = 'Test Pass - Override GPS switch is OFF when uploaded mtf without GPS coordinates'
            printFP(testComment)
            result = Global.PASS
            if wait_for_online:
                GoToDevMan()
                time.sleep(3)
                Global.driver.refresh()
                time.sleep(10)
                GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
                if IsOnline(device['serial']):
                    testComment = 'TEST PASS - %s did come online and successfully uploaded'% device['serial']
                    printFP(testComment)
                    result = Global.PASS
                    overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
                    if not overridegpsstatus:
                        testComment = 'Test Pass - Override GPS switch is still OFF after device come online when uploaded mtf without GPS coordinates'
                        printFP(testComment)
                        return Global.PASS, testComment
                    else:
                        testComment = 'Test Fail - Override GPS is switched on after device come online when uploaded mtf without GPS coordinates'
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    testComment = 'TEST FAIL - %s did not come online' % device['serial']
                    printFP(testComment)
                    result = Global.FAIL
            else:
                return result, testComment
        else:
            testComment = 'Test Fail - Override GPS switch is ON when uploaded mtf without GPS coordinates'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        try:
            GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
            time.sleep(1)
            popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
            message = GetElement(popup,By.TAG_NAME,'p').text
            GetElement(popup, By.TAG_NAME, 'a').click()
            testComment = message.replace('\n', '')
        except:
            testComment = "MTF upload message: %s" % returnMessage
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


def ImportMTFContainsGPSCoordinates(mtf_full_path=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""

    # Generate a temporary mtf with only 1 device
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
        overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
        if overridegpsstatus:
            testComment = 'Test Pass - Override GPS switch is ON when uploaded mtf with GPS coordinates'
            printFP(testComment)
            sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(device['region'], device['substation'], device['feeder'], device['site'])
            if str(sitelatitude) == str(device['lat']) and str(sitelongitude) == str(device['lon']):
                testComment = 'Test Pass - site longitude and latitude values are matched with MTF latitude and longitude'
                printFP(testComment)
                result = Global.PASS
                if wait_for_online:
                    GoToDevMan()
                    time.sleep(3)
                    Global.driver.refresh()
                    time.sleep(10)
                    GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
                    if IsOnline(device['serial']):
                        testComment = 'TEST PASS - %s did come online and successfully uploaded'% device['serial']
                        printFP(testComment)
                        result = Global.PASS
                        overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
                        if overridegpsstatus:
                            testComment = 'Test Pass - Override GPS switch is still ON after device come online when uploaded mtf with GPS coordinates'
                            printFP(testComment)
                            sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(device['region'], device['substation'], device['feeder'], device['site'])
                            if str(sitelatitude) == str(device['lat']) and str(sitelongitude) == str(device['lon']):
                                testComment = 'Test Pass - site longitude and latitude values are matched with MTF latitude and longitude after device come online'
                                printFP(testComment)
                                return Global.PASS, testComment
                            else:
                                testComment = 'Test Fail - site longitude and latitude values are not matched with MTF latitude and longitude after device come online'
                                printFP(testComment)
                                return Global.FAIL, testComment
                        else:
                            testComment = 'Test Fail - Override GPS switch changed to OFF state after device come online when uploaded mtf with GPS coordinates'
                            printFP(testComment)
                            return Global.FAIL, testComment
                    else:
                        testComment = 'TEST FAIL - %s did not come online' % device['serial']
                        printFP(testComment)
                        result = Global.FAIL
                else:
                    return result, testComment
            else:
                testComment = 'Test Fail - site longitude and latitude values are not matched with MTF latitude and longitude'
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            testComment = 'Test Fail - Override GPS switch is OFF when uploaded mtf with GPS coordinates'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        try:
            GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
            time.sleep(1)
            popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
            message = GetElement(popup,By.TAG_NAME,'p').text
            GetElement(popup, By.TAG_NAME, 'a').click()
            testComment = message.replace('\n', '')
        except:
            testComment = "MTF upload message: %s" % returnMessage
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


def ImportMTFEmptyDeviceStateColumn(mtf_full_path=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""

    # Generate a temporary mtf with only 1 device
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
    printFP("INFO - MTF upload message: %s" % returnMessage)
    if "The file has been uploaded successfully." in returnMessage:
        GoToDevMan()
        time.sleep(5)
        GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
        getdevicestates = FilteredDataFromTable('Device State', 'device-management')
        printFP(getdevicestates)
        if 'Production' in getdevicestates:
            testComment = 'Test Pass - MTF File with empty device column uploaded successfully and device state has default value "Production"'
            printFP(testComment)
            result = Global.PASS
        else:
            testComment = 'Test Fail - MTF File with empty device column uploaded successfully but device state is not having default value "Production"'
            printFP(testComment)
            result = Global.FAIL
    else:
        try:
            GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
            time.sleep(1)
            popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
            message = GetElement(popup,By.TAG_NAME,'p').text
            GetElement(popup, By.TAG_NAME, 'a').click()
            message = message.replace('\n', '')
        except:
            message = "MTF upload message: %s" % returnMessage
        testComment = 'Test Fail - MTF File with empty device column upload is failed'
        printFP(message)
        printFP(testComment)
        return Global.FAIL, testComment

    if wait_for_online:
        GoToDevMan()
        time.sleep(3)
        Global.driver.refresh()
        time.sleep(10)
        GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
        if IsOnline(device['serial']):
            testComment = 'TEST PASS - %s did come online when MTF File with empty device column uploaded successfully and device state has default value "Production"' % device['serial']
            result = Global.PASS
        else:
            testComment = 'TEST FAIL - %s did not come online when MTF File with empty device column uploaded successfully and device state has default value "Production"' % device['serial']
            result = Global.FAIL
    else:
        result = Global.PASS
        testComment = 'TEST PASS - Successfully uploaded MTF file to Ample.'

    return result, testComment

def ImportMTFValidDeviceStateinDeviceStateColumn(mtf_full_path=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""
    deviceandstatemapping = {}
    # Generate a temporary mtf with only 1 device
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
                    deviceandstatemapping[device['serial']] = device['devicestate']
                except:
                    pass
    printFP(deviceandstatemapping)
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
        GetRegionFromTop(device['region'])
        getdevicestates = FilteredDataFromTableMapping('Serial Number', 'Device State', 'device-management')
        printFP(getdevicestates)
        if all(str(deviceandstatemapping[x]) == str(getdevicestates[x]) for x in deviceandstatemapping):
            testComment = 'Test Pass - MTF File with all type of device states uploaded successfully and device states are matched with GUI'
            printFP(testComment)
            result = Global.PASS
        else:
            testComment = 'Test Fail - MTF File with all type of device states uploaded successfully but device states are not matched with GUI'
            printFP(testComment)
            result = Global.FAIL
    else:
        try:
            GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
            time.sleep(1)
            popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
            message = GetElement(popup,By.TAG_NAME,'p').text
            GetElement(popup, By.TAG_NAME, 'a').click()
            message = message.replace('\n', '')
        except:
            message = "MTF upload message: %s" % returnMessage
        testComment = 'Test Fail - MTF File with all type of device states upload is failed'
        printFP(message)
        printFP(testComment)
        return Global.FAIL, testComment
    if wait_for_online:
        GoToDevMan()
        time.sleep(3)
        Global.driver.refresh()
        time.sleep(10)
        GetRegionFromTop(device['region'], device['substation'], device['feeder'], device['site'])
        if IsOnline(device['serial']):
            testComment = 'TEST PASS - %s did come online when MTF File with all type of device states uploaded successfully and device states are matched with GUI' % device['serial']
            result = Global.PASS
        else:
            testComment = 'TEST FAIL - %s did not come online when MTF File with all type of device states uploaded successfully and device states are matched with GUI' % device['serial']
            result = Global.FAIL
    else:
        result = Global.PASS
        testComment = 'TEST PASS - Successfully uploaded MTF file to Ample.'
    return result, testComment


def ImportMTFSameSiteFirstWithGPSSecondWithoutGPS(mtf_full_path_1=None, mtf_full_path_2=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""

    # Generate a temporary mtf with only 1 device
    if mtf_full_path_1 == None:
        mtf_full_path = Global.mtfPath
    else:
        mtf_full_path = mtf_full_path_1
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
        testComment = 'INFO - MTF file 1 without GPS is uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
        printFP(testComment)
        if mtf_full_path_2 == None:
            mtf_full_path = Global.mtfPath
        else:
            mtf_full_path = mtf_full_path_2
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
        printFP("INFO - MTF upload message: %s" % returnMessage)
        if "The file has been uploaded successfully." in returnMessage:
            testComment = 'INFO - MTF file 2 with GPS is uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
            printFP(testComment)
            overridegpsstatus = GetOverrideGPSStatus(device['region'], device['substation'], device['feeder'], device['site'])
            if overridegpsstatus:
                testComment = 'Test Pass - Override GPS switch is ON when uploaded mtf with GPS coordinates'
                printFP(testComment)
                sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(device['region'], device['substation'], device['feeder'], device['site'])
                if str(sitelatitude) == str(device['lat']) and str(sitelongitude) == str(device['lon']):
                    testComment = 'Test Pass - site longitude and latitude values are matched with MTF latitude and longitude'
                    printFP(testComment)
                    result = Global.PASS
            else:
                testComment = 'Test Fail - Override GPS switch is OFF when uploaded mtf file 2 with GPS coordinates'
                printFP(testComment)
                return Global.FAIL, testComment
        else:
            try:
                GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
                time.sleep(1)
                popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
                message = GetElement(popup,By.TAG_NAME,'p').text
                GetElement(popup, By.TAG_NAME, 'a').click()
                message = message.replace('\n', '')
            except:
                message = "MTF upload message: %s" % returnMessage

            testComment = 'Test Fail - MTF file 2 with GPS is not uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
            printFP(message)
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        try:
            GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
            time.sleep(1)
            popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
            message = GetElement(popup,By.TAG_NAME,'p').text
            GetElement(popup, By.TAG_NAME, 'a').click()
            message = message.replace('\n', '')
        except:
            message = "MTF upload message: %s" % returnMessage
        testComment = 'Test Fail - MTF file 1 without GPS is not uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
        printFP(message)
        printFP(testComment)
        return Global.FAIL, testComment
    if wait_for_online:
        GoToDevMan()
        time.sleep(3)
        Global.driver.refresh()
        time.sleep(10)
        GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
        if IsOnline(device['serial']):
            testComment = 'TEST PASS - %s did come online when uploaded 2 devices with and without GPS coordinates for the same site one after the other'% device['serial']
            result = Global.PASS
        else:
            testComment = 'TEST FAIL - %s did not come online when uploaded 2 devices with and without GPS coordinates for the same site one after the other' % device['serial']
            result = Global.FAIL
    return result, testComment
