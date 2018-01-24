import Global
import json
import time
import csv
import re
from Utilities_Ample import *
from Ample_SysAdmin import *
from Ample_DevMan import *
from Ample_DevMan_ManageDevices import *
import subprocess as sp
import filecmp
import unicodedata

def GetDeviceInfo(mtf_full_path):
    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
            header = inmtf.readline()
            for line in inmtf:
                devInfo = line.strip('\n').split(',')
    return devInfo

def GetFailureImportInfo():
    try:
        GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
        time.sleep(1)
        popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
        message = GetElement(popup,By.TAG_NAME,'p').text
        GetElement(popup, By.TAG_NAME, 'a').click()
        message = message.replace('\n', '')
        return message
    except:
        return None

def parseErrorMsg():
    try:
        errorText = GetElement(Global.driver, By.XPATH, "//p[@ng-bind-html='details']").text
        string = ""
        strings = []
        #Using a for loop, you can only parse letter by letter only.
        for x in errorText:
            #if you find new line, then put the string into the array and reset string to empty.
            if x == '\n':
                #We only want to move strings that contain Line.
                if string != "":
                    strings.append(string)
                #Clear the string regardless if it contains Line or not.
                string = ""
            else:
                #Concatenate the string with each letter.
                string = string + x
        #Last line will not be added since there is no new line and it is an EOF (will find better solution to this)
        strings.append(string)
        strings.remove('The master tracker upload has data problem(s). Please correct the problem(s) and upload again.')

        return [x.encode('UTF8') for x in strings]
    except:
        return []

def ExportErrorLogForFailedMTF(strings):
    # Place where downloaded file exists
    location = Global.downloadFolder + '/error_messages.txt'
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

def UploadMTFNegativeTestValidation(input_file_path, list_of_errors=None, validateerror=None):
    '''This method will check whether multiple devices are uploaded with same DNP address'''
    if input_file_path == None:
        testComment = "Test Fail - Missing a mandatory parameter."
        printFP(testComment)
        return Global.FAIL, testComment
    printFP("INFO - Going to System Admin Page")
    GoToSysAdmin()
    time.sleep(1)
    printFP('INFO - Uploading the MTF File')
    UploadMTF(Global.deviceFolderPath + input_file_path)
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(3)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if not("Failed to upload" in returnMessage):
        testComment = 'Upload did not fail'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    try:
        errorMsgLink = GetElement(Global.driver, By.XPATH, "//a[contains(text(),'Click here for more details')]")
        errorMsgLink.click()
        time.sleep(2)
    except:
        printFP("INFO - Exception with trying to wait for Click for more Details Link.")
        return Global.EXCEPTION, ''

    errormsg = parseErrorMsg()
    if validateerror == 'VALIDATE_DOWNLOAD':
        dl_button = GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Download')]")
        dl_button.click()
        time.sleep(10)

    closebutton = GetElement(Global.driver, By.XPATH, "/html/body/div[4]/div/div/div[1]/span[2]/a")
    closebutton.click()

    if not validateerror:
        if len(errormsg) != len(list_of_errors):
            printFP("%s"%(errormsg))
            testComment = 'TEST FAIL - Length of Errors on Ample GUI and List of Errors parameter passed mismatch.'
            printFP(testComment)
            return Global.FAIL, testComment

        list_cpy = list(list_of_errors)
        for error in list_of_errors:
            try:
                val = next(i for i, e in enumerate(errormsg) if error in e)
            except StopIteration:
                val = -1

            if val >= 0:
                errormsg.remove(errormsg[val])
                list_cpy.remove(error)

        if len(list_cpy) > 0 or len(errormsg) > 0:
            testComment = "Test Fail - There are mismatching errors. List of Error Param: %s ,Error Msg: %s" %(list_cpy, errormsg)
            printFP(testComment)
            return Global.FAIL, testComment
        else:
            testComment = 'Test Pass- list of expected error messages are matched with GUI error messages'
            printFP(testComment)
            return Global.PASS , testComment
    else:
        if validateerror == 'VALIDATE_HEADERS':
            for error in errormsg:
                result = re.match(r'Line [0-9]+ - [^0-9]+ : (.*)', error)
                if result == None:
                    testComment = 'TEST FAIL - A line does not match the regex. Line contents: %s' %(error)
                    printFP(testComment)
                    return Global.FAIL, testComment
            testComment = 'TEST PASS - All Errors Contain Header Names.'
            printFP(testComment)
            return Global.PASS, testComment
        elif validateerror == 'VALIDATE_NUMBEROFERRORS':
            if len(errormsg) > 50:
                testComment = 'TEST PASS - Number of Error Messages supported exceeds 50.'
                printFP(testComment)
                return Global.PASS, testComment
            else:
                testComment = 'TEST FAIL - Number of Error Messages supported does not exceed 50.'
                printFP(testComment)
                return Global.FAIL, testComment
        elif validateerror == 'VALIDATE_DOWNLOAD':
            result,comment = ExportErrorLogForFailedMTF(errormsg)
            return result,comment
        elif validateerror == 'VALIDATE_CORRECTNUMBEROFERRORS':
            if len(errormsg) != 150:
                testComment = 'TEST FAIL - Number of Errors displayed did not match number of actual errors in MTF.'
                printFP(testComment)
                return Global.FAIL, testComment
            else:
                testComment = 'TEST PASS - Number of Errors matched the number of actual errors in MTF.'
                printFP(testComment)
                return Global.PASS, testComment

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
    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
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
        time.sleep(3)
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
    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
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
        time.sleep(3)
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
    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
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

def ImportMTFNoGPSCoordinates(mtf_full_path=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""

    returnVal, comment = UploadMTFTest(mtf_full_path, False)
    if returnVal == Global.PASS:
        devInfo = GetDeviceInfo(mtf_full_path)
        overridegpsstatus = GetOverrideGPSStatus(devInfo[0],devInfo[1],devInfo[2],devInfo[3])
        if not overridegpsstatus:
            testComment = 'Override GPS switch is OFF when uploaded mtf without GPS coordinates'
            printFP('INFO - ' + testComment)
            result = Global.PASS
            if wait_for_online:
                GetSiteFromTop(devInfo[0],devInfo[1],devInfo[2],devInfo[3])
                if IsOnline(devInfo[5]):
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
                return result, 'TEST PASS - ' + testComment
        else:
            testComment = 'Test Fail - Override GPS switch is ON when uploaded mtf without GPS coordinates'
            printFP('INFO - ' + testComment)
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
            testComment = "Error Clicking on More Details Link on Upload MTF Error"
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


def ImportMTFContainsGPSCoordinates(mtf_full_path=None, wait_for_online=True):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""

    # Generate a temporary mtf with only 1 device
    returnVal, comment = UploadMTFTest(mtf_full_path, False)
    if returnVal == Global.PASS:
        devInfo = GetDeviceInfo(mtf_full_path)
        overridegpsstatus = GetOverrideGPSStatus(devInfo[0],devInfo[1],devInfo[2],devInfo[3])
        if overridegpsstatus:
            testComment = 'Test Pass - Override GPS switch is ON when uploaded mtf with GPS coordinates'
            printFP(testComment)
            sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(devInfo[0],devInfo[1],devInfo[2],devInfo[3])
            if str(sitelatitude) == str(devInfo[9]) and str(sitelongitude) == str(devInfo[10]):
                testComment = 'Site longitude and latitude values are matched with MTF latitude and longitude'
                printFP('INFO - ' + testComment)
                result = Global.PASS
                if wait_for_online:
                    GetSiteFromTop(devInfo[0],devInfo[1],devInfo[2],devInfo[3])
                    if IsOnline(devInfo[5]):
                        testComment = 'TEST PASS - %s did come online and successfully uploaded'% device['serial']
                        printFP(testComment)
                        result = Global.PASS
                        overridegpsstatus = GetOverrideGPSStatus(devInfo[0],devInfo[1],devInfo[2],devInfo[3])
                        if overridegpsstatus:
                            testComment = 'Override GPS switch is still ON after device come online when uploaded mtf with GPS coordinates'
                            printFP('INFO - ' + testComment)
                            sitelatitude, sitelongitude = GetLatAndLonValuesOfSite(devInfo[0],devInfo[1],devInfo[2],devInfo[3])
                            if str(sitelatitude) == str(devInfo[9]) and str(sitelongitude) == str(devInfo[10]):
                                testComment = 'Site longitude and latitude values are matched with MTF latitude and longitude after device come online'
                                printFP('INFO - ' + testComment)
                                return Global.PASS, 'TEST PASS - ' + testComment
                            else:
                                testComment = 'Site longitude and latitude values are not matched with MTF latitude and longitude after device come online'
                                printFP('INFO - ' + testComment)
                                return Global.FAIL, 'TEST FAIL - ' + testComment
                        else:
                            testComment = 'Override GPS switch changed to OFF state after device come online when uploaded mtf with GPS coordinates'
                            printFP('INFO - ' + testComment)
                            return Global.FAIL, 'TEST FAIL - ' + testComment
                    else:
                        testComment = '%s did not come online' % (devInfo[5])
                        printFP('INFO - ' + testComment)
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

    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
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
        message = GetFailureImportInfo()
        if not(message):
            message = "MTF upload message: %s" % returnMessage
        testComment = 'Test Fail - MTF File with empty device column upload is failed'
        printFP(message)
        printFP(testComment)
        return Global.FAIL, testComment

    if wait_for_online:
        GoToDevMan()
        time.sleep(3)
        Global.driver.refresh()
        time.sleep(2)
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
    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
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
        message = GetFailureImportInfo()
        if not(message):
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
    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
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
        with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
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
        message = GetFailureImportInfo()
        if not(message):
            message = "MTF upload message: %s" % returnMessage

        testComment = 'Test Fail - MTF file 1 without GPS is not uploaded successfully when uploaded 2 devices with and without GPS coordinates for the same site one after the other'
        printFP(message)
        printFP(testComment)
        return Global.FAIL, testComment
    if wait_for_online:
        GoToDevMan()
        time.sleep(3)
        Global.driver.refresh()
        time.sleep(3 )
        GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
        if IsOnline(device['serial']):
            testComment = 'TEST PASS - %s did come online when uploaded 2 devices with and without GPS coordinates for the same site one after the other'% device['serial']
            result = Global.PASS
        else:
            testComment = 'TEST FAIL - %s did not come online when uploaded 2 devices with and without GPS coordinates for the same site one after the other' % device['serial']
            result = Global.FAIL
    return result, testComment
