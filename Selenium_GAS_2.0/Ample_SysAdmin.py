import json
import os
from time import strftime, strptime
import datetime
import Global
from Utilities_Ample import *

def EditNetworkGroup(comm_server_name=None, network_group=None, editjson=None):
    if not(comm_server_name and network_group):
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s)'
        printFP(testComment)
        return Global.FAIL, testComment

    if not GoToSysAdmin():
        testComment = 'Test could not navigate to Go To Sys Admin'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    #Json file contains all edits wish to be made on SGW
    params = ParseJsonInputFile(Global.testResourcePath + editjson)

    #Checks if SGW name is valid on this testbed return FAIL if not
    row, testComment = FindNetworkGroupRow(comm_server_name, network_group)
    if row:
        result = Global.PASS
        ClickButton(row, By.XPATH, 'td[4]/div/span[1]')
        time.sleep(2)
        tabs = params.keys()
        #for each tab, it will go through that tab's dictionary and fill out the fields
        #please reference example json file for more information
        for i in range(len(tabs)):
            try:
                GetElement(Global.driver, By.ID, tabs[i]).click()
            except:
                pass
            time.sleep(1)
            keys = params[tabs[i]].keys();
            for key in keys:
                if not (key == 'allow.time.sync' or key == 'default.device.unsolicited.enable'):
                    location = GetElement(Global.driver, By.XPATH, "//span[@tooltip='"+key+"']/parent::span[@class='pull-left input-label']/following-sibling::span[@class='input-fields']/input")
                    if location.get_attribute('readonly'):
                        printFP("INFO - Test cannot edit field %s because it is read-only." % key)
                    else:
                        ClearInput(location)
                        location.send_keys(params[tabs[i]][key])
                else:
                    location = GetElement(Global.driver, By.XPATH, "//span[@tooltip='"+key+"']/parent::span[@class='pull-left input-label']/following-sibling::span[@class='input-fields']/div/div")
                    if not params[tabs[i]][key].lower() in location.get_attribute('class'):
                        GetElement(location, By.XPATH, 'span[1]').click()
            time.sleep(1)
        GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Update')]").click()
        time.sleep(1)
        try:
            msg = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'alert-danger')]/div/span").text
            printFP('INFO - ' + msg)
            GetElement(Global.driver, By.CLASS_NAME, 'close-icon').click()
            return Global.FAIL, 'TEST FAIL - ' + msg
        except:
            GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Close')]").click()
    else:
        printFP("INFO - Unable to find Network Group")
        return Global.FAIL, testComment
    printFP('INFO - Test was a success in Editting the Network Group.')
    return Global.PASS, 'TEST PASS - Test was a success in editting the network group.'

def NetworkGroupSupportTest():
    if not GoToSysAdmin():
        testComment = 'Test could not navigate to Go To Sys Admin'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    time.sleep(1)

    #grab table of SGW+CS
    commServerTbody = GetElement(Global.driver, By.XPATH, xpaths['sys_admin_comm_table'])
    rows = GetElements(commServerTbody, By.XPATH, 'tr')
    result = Global.PASS
    disabled = False

    #Checks if there is a match between SGW and network groups and comm servers
    for i in range(len(rows)):
        #check if disabled
        if 'disabled' in GetElement(rows[i], By.XPATH, 'td[1]/i').get_attribute('class'):
            disabled = True
        else:
            disabled = False

        #if disabled, should not support adding Network Groups -- if CS supports Network Groups, result is set to FAIL
        if disabled and 'disabled' in GetElement(rows[i], By.XPATH, 'td[11]/div/span[2]').get_attribute('class'):
            printFP("INFO - Comm server %s does not support Network Groups and cannot add Network Groups" % GetElement(rows[i], By.XPATH, 'td[2]/span').text)
        elif not disabled and not 'disabled' in GetElement(rows[i], By.XPATH, 'td[11]/div/span[2]').get_attribute('class'):
            printFP("INFO - Comm server %s does support Network Groups and can add Network Groups" % GetElement(rows[i], By.XPATH, 'td[2]/span').text)
        else:
           printFP("INFO - Comm server %s has a mismatch on whether it can add Network Groups or not." % GetElement(rows[i], By.XPATH, 'td[2]/span').text)
           result = Global.FAIL
        time.sleep(2)

    if result == Global.FAIL:
        testComment = 'A problem with comm servers and the ability to add network groups. Please refer to log.'
    else:
        testComment = 'Legacy Comm servers cannot add Network Groups; Only new SGWs are allowed to add.'
    print('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def AddDeviceToDeletedNetworkGroup(input_json=None, comm_server_name=None, mtf_full_path=None):
    if not (input_json and comm_server_name and mtf_full_path):
        testComment = 'TEST FAIL - Test is missing one or more mandatory parameter.'
        printFP(testComment)
        return Global.FAIL, testComment

    if not GoToSysAdmin():
        testComment = 'Test could not navigate to Go To Sys Admin'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    time.sleep(1)

    params = ParseJsonInputFile(Global.testResourcePath + input_json)

    #Adds a network group to a selected SGW, if result is FAIL, end the test
    result, msg = AddNetworkGroup(input_json, comm_server_name)
    if result == Global.FAIL:
        printFP("INFO - Encountered issue while adding device; please check logs.")
        return result, msg
    time.sleep(1)

    #Deletes the network group from the SGW
    result, msg = DeleteNetworkGroup(comm_server_name, params['input'][0])
    if result == Global.FAIL:
        printFP("INFO - Encountered issue while deleting device; please check logs.")
        return result, msg

    #tries to Upload an MTF file with the deleted network group on the sensor gateway
    result, message = UploadMTFTest(mtf_full_path, True)

    if result == Global.FAIL:
        testComment = "Uploading MTF with deleted Network Group does not allow import."
    else:
        testComment = "Upload MTF with deleted Network Group allows import."

    printFP('INFO - ' + testComment)
    return (Global.PASS, ('TEST PASS - ' + testComment)) if result == Global.FAIL else (Global.FAIL, ('TEST FAIL - ' + testComment))

def NetworkGroupPages(input_json=None, comm_server_name=None):
    if not (input_json and comm_server_name):
        testComment = 'TEST FAIL - Test is missing one or more mandatory parameter.'
        printFP(testComment)
        return Global.FAIL, testComment

    #json file with 10+ inputfiles
    params = ParseJsonInputFile(Global.testResourcePath + input_json)
    if len(params["listOfJson"])<=10:
        testComment = 'TEST FAIL - List of Input Files for Network Groups is too small. Please add more.'
        printFP(testComment)
        return Global.FAIL, testComment

    finalresult = Global.PASS
    #starts adding those network groups to the system
    for i in range(len(params["listOfJson"])):
        result, msg = AddNetworkGroup(params["listOfJson"][i], comm_server_name)
        if result == Global.FAIL:
            printFP("INFO - Failed to add a network group. Stopping addition of Network Groups.")
            finalresult = Global.FAIL
            break

    #check if all has been added
    if i == 10:
        printFP("INFO - Succesfully added 10+ devices. Checking if multiple pages exist.")
    else:
        printFP("INFO - Test did not successfully add 10+ devices. Deleting all ")
    Global.driver.refresh()

    retval, comment = OpenNetworkGroupList(comm_server_name)
    if retval == Global.FAIL:
        return Global.FAIL, comment

    try:
        NetworkGroupRow = GetElement(Global.driver, By.CLASS_NAME, 'group-row')
    except:
        testComment = 'Table does not exist for this comm server'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    tbody = GetElement(NetworkGroupRow, By.TAG_NAME, 'tbody')
    rows = GetElements(tbody, By.TAG_NAME, 'tr')
    try:
        GetElement(NetworkGroupRow, By.PARTIAL_LINK_TEXT, 'Next')
        printFP("INFO - Multiple pages exist for SGW %s after adding 10+ devices"%comm_server_name)
    except:
        finalresult = Global.FAIL

    Global.driver.refresh()
    time.sleep(2)
    for n in range(0, i+1):
        parsedjson = ParseJsonInputFile(Global.testResourcePath + params["listOfJson"][n])
        result, msg = DeleteNetworkGroup(comm_server_name, parsedjson['input'][0])
        if result == Global.FAIL:
            printFP("INFO - Failed to delete a network group. Stopping Deletion of Network Groups")
            finalresult = Global.FAIL
            break

    if finalresult == Global.FAIL:
        testComment = 'Test failed at one portion of the process.'
    else:
        testComment = 'Added 10+ devices and found that it creates pages succesfully. Deleted all 10+ devices as well.'
    printFP('INFO - ' + testComment)
    return finalresult, (('TEST PASS - ' + testComment) if finalresult == Global.PASS else ('TEST FAIL - ' + testComment))

def CloneThenDelete(comm_server_name=None, network_group=None, clone_info=None):
    if not (comm_server_name and network_group and clone_info):
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s)'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToSysAdmin()
    time.sleep(1)
    params = ParseJsonInputFile(Global.testResourcePath + clone_info)

    #clones a network group
    result, comment = CloneNetworkGroup(comm_server_name, network_group, clone_info)
    if result == Global.FAIL:
        return result, comment
    Global.driver.refresh()

    #deletes the network group
    result, comment = DeleteNetworkGroup(params['Sensor Gateway Name'], params['Network Group Name'])

    Global.driver.refresh()
    if result == Global.FAIL:
        return result, comment
    else:
        testComment = 'Successfully cloned a network group {} and deleted the clone {}.' .format(network_group, params['Network Group Name'])
        printFP('INFO - ' + testComment)
        return Global.PASS, 'TEST PASS - ' + testComment

def NetworkGroupLayout(comm_server_name=None):
    if not comm_server_name:
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    headers = ["Network Group", "Description", "Master DNP Address", "Actions"]
    actions = ["Edit", "Clone", "Delete"]

    GoToSysAdmin()
    retval, comment = OpenNetworkGroupList(comm_server_name)
    if retval == Global.FAIL:
        return Global.FAIL, ('TEST FAIL - ' + comment)

    result = Global.PASS
    try:
        NetworkGroupRow = GetElement(Global.driver, By.CLASS_NAME, 'group-row')
    except:
        testComment = 'Table does not exist for this comm server'
        printFP('INFO - ' + testComment)
        return Global.FAIL, ('TEST FAIL - ' + testComment)

    time.sleep(1)
    headerNames = GetElements(NetworkGroupRow, By.TAG_NAME, 'th')
    for header in headerNames:
        if not header.text:
            try:
                headerval = GetElement(header, By.TAG_NAME, 'div').text
                printFP("INFO - Header Name: %s" %headerval)
                if not headerval in headers:
                    result = Global.FAIL
            except:
                pass
        else:
            printFP("INFO - Header Name: %s" %header.text)
            if not header.text in headers:
                result = Global.FAIL

    if result == Global.FAIL:
        testComment = 'TEST FAIL - Header Names are bad. Please refer to log to isolate which ones.'
        printFP(testComment)
        return Global.FAIL, testComment

    tbody = GetElement(NetworkGroupRow, By.TAG_NAME, 'tbody')
    rows = GetElements(tbody, By.TAG_NAME, 'tr')
    for row in rows:
        for i in range(1,5):
            if i == 4:
                for n in range(1,4):
                    button = GetElement(row, By.XPATH, 'td[4]/div/span['+str(n)+']')
                    printFP("Action: %s" %button.get_attribute('tooltip'))
                    if not button.get_attribute('tooltip') in actions:
                        printFP("INFO - This button should not be here.")
                        result = Global.FAIL
            else:
                textvalue = GetElement(row, By.XPATH, 'td[%s]/span'%i).text
                if i == 2:
                    printFP("INFO - Description for network group: %s"%textvalue)
                elif (textvalue == ''):
                    printFP("INFO - One field outside of description displayed an empty value")
                    result = Global.FAIL
                else:
                    printFP("INFO - {}: {}".format(headers[i-1], textvalue))

    if result == Global.PASS:
        testComment = 'Network Groups are properly displayed.'
    else:
        testComment = 'Network Group has some parts that are not properly displayed'
    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def AddNetworkGroup(input_json=None, comm_server_name=None):
    if not input_json:
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(Global.testResourcePath + input_json)

    GoToSysAdmin()

    #expands SGW
    retval, comment = OpenAddNetworkGroupForSGW(comm_server_name)
    if retval == Global.FAIL:
        return Global.FAIL, comment

    time.sleep(1)
    #fills in SGW information
    body = GetElement(Global.driver, By.CLASS_NAME, 'section-body')
    textbox = GetElement(body, By.TAG_NAME, 'textarea')
    textbox.send_keys(params['description'])
    inElement = GetElement(body, By.XPATH, '//fieldset[1]/span[2]/input')
    inElement.send_keys(params['input'][0])
    inElement = GetElement(body, By.XPATH, '//fieldset[4]/span[2]/input')
    inElement.send_keys(params['input'][1])
    result = Global.PASS
    confirm = GetElement(Global.driver, By.XPATH, '//div[3]/button[2]')
    confirm.click()

    #checks if there are any warning messages after clicking OK
    try:
        warningmessage = GetElement(Global.driver, By.CLASS_NAME, 'alert-danger')
        testComment = GetElement(warningmessage, By.CLASS_NAME, 'ng-binding').text
        GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        result = Global.FAIL
    except:
        if 'successfully' in GetElement(Global.driver, By.XPATH, "//div[contains(@class,'modal-body')]/p").text:
            testComment = 'Test did not get error message and successfully added network group.'
        else:
            result = Global.FAIL
            testComment = 'Test did not get error message but did not successfully add network group.'
        GetElement(Global.driver, By.XPATH, "//button[text()='Close']").click()

    printFP("INFO - " + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)

def DeleteNetworkGroup(comm_server_name=None, network_group_deleted=None, checkUnregister=False, input_file_path=None, devices=None):
    if not (comm_server_name and network_group_deleted):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToSysAdmin()

    #finds network group for the given SGW
    row, testComment = FindNetworkGroupRow(comm_server_name, network_group_deleted)
    if row:
        result = Global.PASS
        #deletes network group by clicking delete for a network group
        ClickButton(row, By.XPATH, 'td[4]/div/span[3]')
        time.sleep(1)
        title = GetElement(Global.driver, By.CLASS_NAME, 'modal-title').text
        printFP("Title: %s" %title)
        if "Delete" in title:
            GetElement(Global.driver, By.XPATH, '//button[text()="Ok"]').click()
            time.sleep(1)
            msg = GetElement(Global.driver, By.XPATH, "//div[@class='modal-body ng-scope']/p")
            if not 'The network group deleted successfully.' in msg.text:
                result = Global.FAIL
                printFP("INFO - Network group cannot be removed at this time.")
            closeButton = GetElement(Global.driver, By.XPATH, '//button[text()="Close"]')
            closeButton.click()
            time.sleep(1)
        else:
            GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
            result = Global.FAIL

        """if checkUnregister is set and a delete was successful then it will go to device management and search for device
        device should display that it is unregistered"""
        if checkUnregister and result == Global.PASS:
            if not (input_file_path and devices):
                printFP("INFO - Test was to check for unregister button, but was not given an input file to find devices")
                return Global.FAIL, 'TEST FAIL - Test was not given input file or devices to check for unregister.'

            params = ParseJsonInputFile(Global.testResourcePath + input_file_path)
            GoToDevMan()
            if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
                testComment = "Test was unable to get to desired location based on input file"
                printFP('INFO - ' + testComment)
                return Global.FAIL, 'TEST FAIL - ' + testComment
            time.sleep(1)
            for i in range(len(devices)):
                printFP("INFO - Trying to find device: %s" %(devices[i]))
                classValue = GetElement(Global.driver, By.XPATH, "//span[a='"+devices[i]+"']/../../td[4]/span").get_attribute('class')
                if classValue != 'glyphicon glyphicon-transfer':
                    result = Global.FAIL
            if result == Global.FAIL:
                testComment = 'Devices that were using network group %s failed to unregister.' % network_group_deleted
                printFP('INFO - ' + testComment)
            else:
                testComment = 'Devices that were using network group %s properly unregistered.' % network_group_deleted
                printFP('INFO - ' + testComment)
        else:
            """if checkUnregister is not set then it will either say it deleted the network group or it didn't"""
            if result == Global.PASS:
                testComment = 'Successfully deleted network group %s' %network_group_deleted
            else:
                testComment = 'Unable to delete network group %s. Please refer to log file.' %network_group_deleted
        printFP('INFO - ' + testComment)
        return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))
    else:
        return Global.FAIL, testComment

def returnParameterDictionary(comm_server_name, network_group):
    tabIDs = ["otapData", "dnp3Data", "lttpData"]
    row, testComment = FindNetworkGroupRow(comm_server_name, network_group)
    if row:
        paramDict = {}
        ClickButton(row, By.XPATH, 'td[4]/div/span[1]')
        time.sleep(1)
        for i in range(len(tabIDs)):
            ClickButton(Global.driver, By.ID, tabIDs[i])
            time.sleep(1)
            tabcontent = GetElement(Global.driver, By.CLASS_NAME, 'tab-content')
            activetab = GetElement(tabcontent, By.CLASS_NAME, 'active')
            fields = GetElements(activetab, By.TAG_NAME, 'fieldset')
            for field in fields:
                key = GetElement(field, By.XPATH, 'span[1]/span').text
                try:
                    value = GetElement(field, By.XPATH, 'span[2]/input').get_attribute('value')
                except:
                    try:
                        value = GetElement(field, By.XPATH, 'span[2]/div/div').get_attribute('class')
                    except:
                        print "INFO - Error in evaluating input value; neither toggle button nor input field"
                        return None
                paramDict[key] = value

        GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        time.sleep(1)
        return paramDict
    else:
        printFP("INFO - Test could not locate network group {} under SGW {}" .format(network_group, comm_server_name))
        return None

def CloneNetworkGroup(comm_server_name=None, network_group=None, clone_info=None):
    if not (comm_server_name and network_group and clone_info):
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToSysAdmin()
    time.sleep(1)

    row, testComment = FindNetworkGroupRow(comm_server_name, network_group)
    if row == None:
        return Global.FAIL, testComment

    result = Global.PASS
    params = ParseJsonInputFile(Global.testResourcePath + clone_info)
    ClickButton(row, By.XPATH, 'td[4]/div/span[2]')
    title = GetElement(Global.driver, By.CLASS_NAME, 'modal-title').text
    printFP("Title: %s" %title)
    if "Clone" in title:
        GetElement(Global.driver, By.ID, "name").send_keys(params['Network Group Name'])
        GetElement(Global.driver, By.ID, "description").send_keys(params['Description'])
        GetElement(Global.driver, By.ID, 'sgwName').click()
        menu = GetElement(Global.driver, By.ID, 'sgwName')
        links = GetElements(menu, By.TAG_NAME, 'a')
        for link in links:
            linkText = GetElement(link, By.TAG_NAME, 'span').text
            if linkText == params['Sensor Gateway Name']:
                ActionChains(Global.driver).click(link).perform()
                break
        GetElement(Global.driver, By.ID, 'masterDnpAddress').send_keys(params['Master DNP Address'])
        footer = GetElement(Global.driver, By.CLASS_NAME, 'modal-footer')
        GetElement(footer, By.XPATH, 'button[2]').click()
        time.sleep(1)
        msg = GetElement(Global.driver, By.XPATH, "//div[@class='modal-body ng-scope']/p")
        printFP('INFO - ' + msg.text)
        if not 'The network group configure properties is successfully cloned.' in msg.text:
            printFP("INFO - Network group was not configured successfully. Return message: %s" %msg.text)
            Global.driver.refresh()
            return Global.FAIL, 'TEST FAIL - ' + msg
        closeRetMsg = GetElement(Global.driver, By.XPATH, "//div[@class='modal-footer ng-scope']/button[text()='Close']")
        closeRetMsg.click()
        time.sleep(1)
    else:
        GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        return Global.FAIL, 'TEST FAIL - Wrong page was reached.'

    Global.driver.refresh()
    dict1 = returnParameterDictionary(comm_server_name, network_group)
    if dict1 == None:
        testComment = 'Test could not generate a dictionary for the parameters and values for the original.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    Global.driver.refresh()
    dict2 = returnParameterDictionary(params['Sensor Gateway Name'], params['Network Group Name'])
    if dict2 == None:
        testComment = 'Test could not generate a dictionary for the parameters and values for the clone.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, ('TEST FAIL - ' + testComment)

    if dict1.keys() == dict2.keys():
        for key in dict1.keys():
            if not dict1[key] == dict2[key]:
                printFP("INFO - Disagreement between cloned and actual value for key {}. Actual:{} Clone: {}".format(key, dict1[key], dict2[key]))
                result = Global.FAIL
            else:
                printFP("INFO - Cloned network group and actual key,{},matches" .format(key))
    else:
        testComment = "One parameter dictionary has more values than the other. Please check logs and Ample."
        printFP('INFO - ' + testComment)
        return Global.FAIL, ('TEST FAIL - ' + testComment)

    if result == Global.PASS:
        testComment = 'Succesfully cloned and the clone has the same values as original.'
    else:
        testComment = 'Did not succesfully clone the original. The two have differing values. Please refer to log to find which values differ.'

    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def EditSGWParameterOutsideRange(input_json=None, comm_server_name=None):
    if not(input_json and comm_server_name):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(Global.testResourcePath + input_json)

    GoToSysAdmin()

    retval, comment = OpenEditForSGW(comm_server_name)
    if retval == Global.FAIL:
        return Global.FAIL, comment

    result = Global.PASS
    tabs = params['Tabs']

    for i in range(len(tabs)):
        #Try and click tab in SGW edit screen
        try:
            tab = GetElement(Global.driver, By.ID, tabs[i])
            if not 'active' in tab.get_attribute('class'):
                tab.click()
        except:
            printFP("INFO - Tab %s of the tabs did not appear." %tabs[i])
            return Global.FAIL, 'TEST FAIL - Test could not locate tab %s' %tabs[i]

        tabKeys = params['Range'][tabs[i]].keys()
        for j in range(len(tabKeys)):
            try:
                inputfield = GetElement(Global.driver, By.XPATH, "//span[@tooltip='"+tabKeys[j]+"']/../../span[2]/input")
            except:
                printFP("INFO - Test could not locate input field within this tab. Skipping key %s" %tabKeys[j])
                continue
            
            defaultvalue = inputfield.get_attribute('value')
            for k in range(2):
                ClearInput(inputfield)
                inputfield.send_keys(str(params['Range'][tabs[i]][tabKeys[j]][k]))
                try:
                    saveButton = GetElement(Global.driver, By.XPATH, "//button[text()=' Save']")
                    saveButton.click()
                    time.sleep(1)
                except:
                    printFP("INFO - Save Button was not available for click.")
                    result = Global.FAIL

                try:
                    alertElement = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-dismissable alert-danger']/div/span")
                    printFP("Alert message: %s" %alertElement.text)
                    if str(tabKeys[j]) in alertElement.text or 'Please correct the errors on the form.' in alertElement.text:
                        printFP("INFO - %s field caused an error." %tabKeys[j])
                    else:
                        printFP("INFO - %s field did not cause an error with value %s." %(tabKeys[j],str(params['Range'][tabs[i]][tabKeys[j]][k])))
                        result = Global.FAIL
                    ClearInput(inputfield)
                    inputfield.send_keys(defaultvalue)
                except:
                    printFP("INFO - Test was unable to get an alert for this element")
                    result = Global.FAIL

    GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
    if result == Global.PASS:
        testComment = 'All parameters passed the range test.'
    else:
        testComment = 'Some parameters did not pass the range test. Please refer to log to see which did not pass'
    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def EditSGWSetting(input_json=None, comm_server_name=None):
    if not input_json:
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(Global.testResourcePath + input_json)

    GoToSysAdmin()

    retval, comment = OpenEditForSGW(comm_server_name)
    if retval == Global.FAIL:
        testComment = 'TEST FAIL - Could not open Edit for SGW'
        return Global.FAIL, testComment

    result = Global.PASS
    tabs = params['Tabs']

    for i in range(len(tabs)):
        #Try and click tab in SGW edit screen
        try:
            tab = GetElement(Global.driver, By.ID, tabs[i])
            if not 'active' in tab.get_attribute('class'):
                tab.click()
        except:
            printFP("INFO - Tab %s of the tabs did not appear." %tabs[i])
            return Global.FAIL, 'TEST FAIL - Test could not locate tab %s' %tabs[i]

        tabKeys = params['Range'][tabs[i]].keys()
        for j in range(len(tabKeys)):
            try:
                inputfield = GetElement(Global.driver, By.XPATH, "//span[@tooltip='"+tabKeys[j]+"']/../../span[2]/input")
            except:
                printFP("INFO - Test could not locate input field within this tab. Skipping key %s" %tabKeys[j])
                continue
            ClearInput(inputfield)
            inputfield.send_keys(str(params['Range'][tabs[i]][tabKeys[j]]))

    try:
        saveButton = GetElement(Global.driver, By.XPATH, "//button[text()=' Save']")
        try:
            if 'disabled' in saveButton.get_attribute('disabled'):
                printFP("INFO - Save button had disable attribute on. Refreshing page and ending test.")
                Global.driver.refresh()
                return Global.FAIL, 'TEST FAIL - Save button had disable attribute on.'
        except:
            pass
        saveButton.click()
    except:
        printFP("INFO - Save Button was not available for click. Refreshing page and ending test.")
        Global.driver.refresh()
        return Global.FAIL, 'TEST FAIL - Save button was not available.'

    try:
        alertElement = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-dismissable alert-danger']/div/span")
        printFP("Alert message: %s" %alertElement.text)
    except:
        printFP("INFO - Test was unable to get an error alert for this element")


    msgbox = GetElement(Global.driver, By.CLASS_NAME, 'modal-content')
    msg = GetElement(msgbox, By.TAG_NAME, 'p').text
    printFP('INFO - ' + msg)
    if not ('successfully' in msg):
        testComment = "Error occured while applying new editted values"
        GetElement(msgbox, By.TAG_NAME, 'button').click()
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    else:
        testComment = 'INFO - Editting the values was succesful.'
    GetElement(msgbox, By.TAG_NAME, 'button').click()

    Global.driver.refresh()
    retval, comment = OpenEditForSGW(comm_server_name)
    if retval == Global.FAIL:
        return Global.FAIL, comment

    tabs = params['Tabs']
    for i in range(len(tabs)):
        #Try and click tab in SGW edit screen
        try:
            tab = GetElement(Global.driver, By.ID, tabs[i])
            if not 'active' in tab.get_attribute('class'):
                tab.click()
        except:
            printFP("INFO - Tab %s of the tabs did not appear." %tabs[i])
            return Global.FAIL, 'TEST FAIL - Test could not locate tab %s' %tabs[i]

        tabKeys = params['Range'][tabs[i]].keys()
        for j in range(len(tabKeys)):
            try:
                inputfield = GetElement(Global.driver, By.XPATH, "//span[@tooltip='"+tabKeys[j]+"']/../../span[2]/input")
            except:
                printFP("INFO - Test could not locate input field within this tab. Skipping key %s" %tabKeys[j])
                continue
            if not (inputfield.get_attribute('value') == str(params['Range'][tabs[i]][tabKeys[j]])):
                printFP("INFO - {} did not match. GUI value was {}. Input file Value {}." .format(tabKeys[j], inputfield.get_attribute('value'), params['Range'][tabs[i]][tabKeys[j]]))
                result = Global.FAIL
            else:
                printFP("INFO - {} matched on GUI and input file value." .format(tabKeys[j]))

    GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
    if result == Global.PASS:
        testComment = 'All editted values matched.'
    else:
        testComment = 'Some values did not match. Please refer to log and find out which specific ones.'

    printFP("INFO - " + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def VerifySensorGateWayDetails():
    GoToSysAdmin()

    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_comm_header_btn'])
    inputElements = GetElements(Global.driver, By.TAG_NAME, 'input')
    for x in inputElements:
        if x.get_attribute('type') == 'checkbox':
            SetCheckBox(x, "true")

    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_comm_header_btn'])

    commServerTbody = GetElement(Global.driver, By.XPATH, xpaths['sys_admin_comm_table'])
    rows = GetElements(commServerTbody, By.TAG_NAME, 'tr')
    result = Global.PASS
    printFP("INFO - Verifying Headers")
    correctHeaders = ["Name", "Host", "Port", "Master DNP Address", "Uptime", "Status", "Last Modified", "Description", "Software Version", "Actions"]
    tableheaders = GetElements(Global.driver, By.XPATH, "//th[@ng-repeat='column in columns' or contains(text(),'Actions')]")
    headers = []
    for i in range(len(tableheaders)):
        if tableheaders[i].text != 'Actions':
            string = str(GetElement(tableheaders[i], By.XPATH, 'div').text)
            if 'Last Modified' in string:
                string = 'Last Modified'
            headers.append(string)
        else:
            headers.append(tableheaders[i].text)

    if not(sorted(headers) == sorted(correctHeaders)):
        testComment = 'The displayed table headers for the Sensor Gateways in System Admin is incorrect.'
        printFP("INFO - " + testComment)
        return Global.FAIL, testComment
    else:
        printFP("INFO - SGW Displayed Headers Match.")

    for row in rows:
        onlineStatus = True
        edit_gateway_flag = True
        add_network_flag = True
        #Each iteration from 1-11 represents the column of the sensor gateway table inside System Admin
        #Hence, 1 presents the first, while 11 represents the 11th.
        for i in range(1,12):
            if i == 1:
                if 'toggle-icon disabled' in GetElement(row, By.XPATH, 'td[1]/i').get_attribute('class'):
                    printFP("INFO - Toggle Button for show/hide Network Groups does not exist")
                    result = Global.FAIL
                else:
                    printFP("INFO - Toggle Button for show/hide Network Groups exist")
            elif i == 5:
                masterDNP = GetElement(row, By.XPATH, 'td[5]/span').text
                if not('NA' == masterDNP):
                    printFP("INFO - Master DNP Address should be NA. For this SGW, it is %s."%(masterDNP))
                    result = Global.FAIL
                else:
                    printFP("INFO - Master DNP Address is NA, which is correct")
            elif i == 7:
                classval = GetElement(row, By.XPATH, 'td[7]/span').get_attribute('class')
                if not(classval == 'icon ion-checkmark-circled'):
                    onlineStatus = False
            elif i == 11:
                try:
                    GetElement(row, By.XPATH, 'td[11]/div/span[1]').click()
                    time.sleep(1)
                    title = GetElement(Global.driver, By.CLASS_NAME, "modal-title").text
                    if not 'Edit Sensor Gateway' in title:
                        printFP("Wrong title for Editting Sensor Gateway.")
                    GetElement(Global.driver, By.XPATH, "//a[@class='glyphicon glyphicon-remove-circle close-icon']").click()
                except:
                    printFP("Error trying to get title of Editting Sensor Gateway")
                    edit_gateway_flag = False
                time.sleep(1)
                try:
                    GetElement(row, By.XPATH, 'td[11]/div/span[2]').click()
                    time.sleep(1)
                    title = GetElement(Global.driver, By.CLASS_NAME, "modal-title").text
                    if not 'Add Network Group' in title:
                        printFP("wrong title for adding network group. Title: %s" %title)
                        result = Global.FAIL
                    GetElement(Global.driver, By.XPATH, "//a[@class='glyphicon glyphicon-remove-circle close-icon']").click()
                except:
                    printFP("Error trying to get title of Adding Network Group")
                    add_network_flag = False
                time.sleep(1)

        if onlineStatus == edit_gateway_flag == add_network_flag:
            printFP("INFO - This is an %s sensor gateway." %('online' if onlineStatus else 'offline'))
        else:
            printFP("INFO - This sensor gateway is incorrect.")
            result = Global.FAIL

    if result == Global.FAIL:
        testComment = 'Test failed and there were things wrong with the System Admin SGW screen. Refer to log.'
    else:
        testComment = 'Test passed and all displays were displayed correctly'

    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def UploadMTFTest(mtf_full_path=None, wait_for_online=True, verifyLongFieldNotes=False):
    """Navigates to the System admin page and uploads MTF to Ample.
    Also generates a dictionary representing the device to be used during the test. Currently only supports 1 device in the MTF.
    If you do not specify an mtf_path, it will use the Global.MTF"""

    # Generate a temporary mtf with only 1 device
    with open(Global.deviceFolderPath + mtf_full_path, 'r') as inmtf:
        with open('/tmp/UploadMTFTest' + mtf_full_path[mtf_full_path.rfind('.'):], 'w+') as outmtf:
            header = inmtf.readline()
            outmtf.write(header)
            for line in inmtf:
            #line = inmtf.readline()
                outmtf.write(line)
                devInfo = line.strip('\n').split(',')
    GoToSysAdmin()
    time.sleep(1)
    UploadMTF('/tmp/UploadMTFTest'+mtf_full_path[mtf_full_path.rfind('.'):])
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf'])
    time.sleep(1)
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_msg'], visible=True)
    if "The file has been uploaded successfully." in returnMessage:
        printFP("INFO - MTF upload message: %s" % returnMessage)
    else:
        try:
            GetElement(Global.driver, By.LINK_TEXT, 'Click here for more details').click()
            time.sleep(1)
            popup = GetElement(Global.driver, By.CSS_SELECTOR, 'div.modal-content')
            message = GetElement(popup,By.TAG_NAME,'p').text
            GetElement(popup, By.TAG_NAME, 'a').click()
            testComment = message.replace('\n', '')
            Global.driver.refresh()
        except:
            testComment = "MTF upload message: %s" % returnMessage
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    if wait_for_online or verifyLongFieldNotes:
        GoToDevMan()
        time.sleep(2)
        GetSiteFromTop(devInfo[0], devInfo[1], devInfo[2], devInfo[3])
        result = Global.PASS
        testComment = ""
        if verifyLongFieldNotes:
            columnControl = GetElement(Global.driver, By.XPATH, "//button[contains(@class,'column-settings-btn')]")
            columnControl.click()
            time.sleep(2)
            fieldnote = GetElement(Global.driver, By.XPATH, "//span[text()='Field Notes']/preceding-sibling::input")
            if not(fieldnote.is_selected()):
                printFP('INFO - Field note is not checked...Now checking')
                fieldnote.click()
                time.sleep(1)
            columnControl.click()
            fieldNote = GetElement(Global.driver, By.XPATH, "//a[text()='"+devInfo[5]+"']/../../../td[20]")
            fieldNote.click()
            fieldnote_popup = GetElement(Global.driver, By.XPATH, "//div[@class='modal-body more-details-tooltip ng-scope']/p")
            if fieldnote_popup.text.strip() == devInfo[14]:
                printFP("INFO - Long Field Notes Matches.")
                testComment = testComment + 'Long Field Notes Matched. '
            else:
                printFP("INFO - Long Field Notes did not match")
                testComment = testComment + 'Long Field Notes did not Match. '
                result = Global.FAIL

        if wait_for_online:
            if IsOnline(devInfo[5]):
                testComment = testComment + ('%s did come online and successfully uploaded'% devInfo[5])
            else:
                testComment = testComment + ('%s did not come online' % devInfo[5])
                result = Global.FAIL
    else:
        result = Global.PASS
        testComment = 'TEST PASS - Successfully uploaded MTF file to Ample.'

    return result, testComment


def VerifyUploadDetails(file_path=None, wait_for_online=False, Status=None, importType=None):
    if not(file_path and Status and importType):
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s)'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToSysAdmin()
    uploadtime = strftime('%m/%d/%Y %I:%M %p')
    if importType == 'MTF':
        UploadMTFTest(file_path, wait_for_online)
    elif importType == 'Firmware':
        LoadAmpleBundle(file_path)
    else:
        testComment = 'TEST FAIL - Invalid import type specified. Please choose between MTF or Firmware'
        printFP(testComment)
        return Global.FAIL, testComment

    result = Global.PASS
    for i in range(1,5):
        if importType == 'MTF':
            time.sleep(1)
            firstRow = GetElement(Global.driver, By.XPATH, xpaths['sys_admin_upload_mtf_firstrow'])
        else:
            firstRow = GetElement(Global.driver, By.XPATH, xpaths['sys_admin_upload_firmware_firstrow'])
        textVal = GetElement(firstRow, By.XPATH, 'td[' + str(i) + ']/div').text
        if i == 1:
            if importType == 'MTF' and textVal in ('/tmp/UploadMTFTest'+file_path[file_path.rfind('.'):]):
                printFP("INFO - Correct input file name was displayed for MTF upload.")
            elif importType == 'Firmware' and textVal in file_path:
                printFP("INFO - Correct input file name was displayed for Firmware upload.")
            else:
                printFP("INFO - Incorrect input file name was displayed for upload.")
                result = Global.FAIL
        elif i == 2:
            GoToUpdateProfile()
            username = GetElement(Global.driver, By.XPATH, '//*[@id="userName"]').get_attribute('value')
            GetElement(Global.driver, By.XPATH, '/html/body/div[4]/div/div/div[1]/span[2]/a').click()
            if username == textVal:
                printFP("INFO - Usernames match the user that uploaded the file and the one displayed on the table.")
            else:
                printFP("INFO - Usernames do not match the user that uploaded the file and the one displayed on the table.")
                result = Global.FAIL
        elif i == 3:
            t1 = datetime.datetime.strptime(uploadtime, '%m/%d/%Y %I:%M %p')
            t2 = datetime.datetime.strptime(textVal, '%m/%d/%Y %I:%M %p')
            diff = t2 - t1
            if abs(diff.total_seconds()) <= 90:
                printFP("INFO - Time of upload matches.")
            else:
                printFP("INFO - Time of upload does not match")
                result = Global.FAIL
        else:
            if Status == 'SUCCESS' and Status == textVal:
                printFP("INFO - Status of upload was supposed to be SUCCESS and its matched the GUI output.")
            elif Status == 'FAILURE' and Status == textVal:
                printFP("INFO - Status of upload was supposed to be FAILURE and its matched the GUI output.")
            else:
                printFP("INFO - Error in either the status provided or the matching between the GUI and value given in input file")
                result = Global.FAIL

    if result == Global.PASS:
        testComment = 'Everything matched.'
    else:
        testComment = 'Not all values matched. Please refer to log file to find out which fields did not'

    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def LoadAmpleBundles(path_to_bundles):
    """loads all ample bundles in the folder"""
    GoToSysAdmin()
    fileUpload = GetElement(Global.driver, By.ID, 'firmFile')

    bundles = os.listdir(path_to_bundles)
    for bundle in bundles:
        fileName = path_to_bundles + bundle
        fileUpload.send_keys(fileName)
        ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_bundle'])
        returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_bundle_msg'], visible=True)
        printFP(returnMessage)
        if returnMessage == 'The file has been uploaded successfully.':
            printFP('INFO - Loaded %s' % bundle)
        else:
            return Global.FAIL, 'TEST FAIL - '+ returnMessage
    printFP('TEST PASS - Uploaded all bundles in %s' % path_to_bundles)
    return Global.PASS, 'TEST PASS - ' + returnMessage

def LoadAmpleBundle(path_to_bundle):
    GoToSysAdmin()
    fileUpload = GetElement(Global.driver, By.ID, 'firmFile')

    #loads a singular ample bundle
    fileUpload.send_keys(Global.testResourcePath + path_to_bundle)
    ClickButton(Global.driver, By.XPATH, xpaths['sys_admin_upload_bundle'])

    #checks for successful or failed upload message
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['sys_admin_upload_bundle_msg'], visible=True)
    printFP('INFO - ' + returnMessage)
    if returnMessage == 'The file has been uploaded successfully.':
        printFP('INFO - Uploaded bundle %s' % (Global.testResourcePath + path_to_bundle))
    else:
        return Global.FAIL, 'TEST FAIL - ' + returnMessage
    return Global.PASS, 'TEST PASS - ' + returnMessage

def ConfigureAmple(config_file_path):
    GoToConfigProp()
    with open(config_file_path, 'r') as config_json:
        ampleconfig = json.load(config_json)
    form = GetElement(Global.driver, By.TAG_NAME, 'form')
    formGroups = GetElements(Global.driver, By.CLASS_NAME, 'form-group')
    for formGroup in formGroups:
        label = GetText(formGroup, By.TAG_NAME, 'label')
        if label in ampleconfig:
            inputElement = GetElement(formGroup, By.TAG_NAME, 'input')
            ClearInput(inputElement)
            SendKeys(inputElement, ampleconfig['label'])
    ClickButton(driver, By.XPATH, xpaths['sys_admin_config_prop_save'])
    time.sleep(1)
    return Global.PASS, ''

def FillInField(field_label, input_value):
    fieldsets = GetElements(Global.driver, By.TAG_NAME, 'fieldset')
    for fieldset in fieldsets:
        label = GetText(fieldset, By.CLASS_NAME, 'input-label')
        if field_label in label:
            inputElement = GetElement(fieldset, By.TAG_NAME, 'input')
            if inputElement.get_attribute('type') == 'text':
                ClearInput(inputElement)
                SendKeys(inputElement, input_value)
            else:
                SetCheckbox(inputElement, value)
            return True
    return False
