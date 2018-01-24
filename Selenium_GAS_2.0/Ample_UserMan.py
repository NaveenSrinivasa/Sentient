import Global
import json
import random
import os
import csv
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from Utilities_Ample import *
from Ample_DevMan import *
from Ample_Login import *

def VerifyDisable(disabled_user=None, disabled_pw=None):
    GoToUserMan()
    returnVal = DisableUserAccount(disabled_user)

    if not(returnVal):
        printFP("INFO - Test ran into issues while trying to disable user account.")
        return Global.FAIL , 'TEST FAIL - Test ran into issues while trying to disable account. Please refer to log.'

    result, comment = CheckDisableResult(disabled_user, disabled_pw)

    return result, comment

def VerifyEnable(enable_user, enable_pw):
    GoToUserMan()
    returnVal = EnableUserAccount(enable_user)

    if not(returnVal):
        printFP("INFO - Test ran into issues while trying to enable user account.")
        return Global.FAIL , 'TEST FAIL - Test ran into issues while trying to enable account. Please refer to log.'

    result, comment = CheckEnableResult(enable_user, enable_pw)
    Logout()
    return result, comment

def VerifyForceReset(reset_user, reset_pw, new_pw):
    GoToUserMan()
    result = ResetPasswordForUserAccount(reset_user)

    if not(result):
        printFP("INFO - Test ran into issues while trying to force reset.")
        return Global.FAIL , 'TEST FAIL - Test ran into issues while trying to force reset on user %s. Please refer to log for more information.' %(reset_user)

    result = CheckResetPasswordUserAccountLogin(reset_user, reset_pw, new_pw)
    Logout()

    if result:
        printFP("INFO - Force Reset was successful for user %s" %(reset_user))
        return Global.PASS, 'TEST PASS - Force Reset was successful for user %s' %(reset_user)
    else:
        printFP("INFO - Force Reset was unsuccessful for user %s" %(reset_user))
        return Global.PASS, 'TEST FAIL - Force Reset was unsuccessful for user %s' %(reset_user)

def CheckEnableResult(disabled_user=None, disabled_pw=None):
    if not(any(substring in Global.driver.current_url for substring in ['disabled','login'])):
        Logout()
        time.sleep(2)
    else:
        Global.driver.get('https://172.20.4.40/amplemanage/login')
        time.sleep(2)

    if not('amplemanage/login' in Global.driver.current_url):
        printFP("INFO - Test did not navigate to login page.")
        return Global.FAIL, 'TEST FAIL - Test did not navigate to login page.'

    inputElement = GetElement(Global.driver, By.ID, 'j_username')
    SendKeys(inputElement, disabled_user)

    inputElement = GetElement(Global.driver, By.ID, 'j_password')
    SendKeys(inputElement, disabled_pw)

    inputElement.submit()

    time.sleep(3)

    if (any(substring in Global.driver.current_url for substring in ['disabled','login'])):
        printFP("INFO - Test navigated to user disabled page. Current URL: %s" %(Global.driver.current_url))
        return Global.FAIL, "TEST FAIL - Test navigated to user disabled page. Current URL: %s" %(Global.driver.current_url)

    try:
        message = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-danger']/div/span")
        printFP("INFO - There is an error message that is displayed.")
        return Global.FAIL, 'TEST FAIL - No error message to say that the user is disabled.'
    except:
        printFP("INFO - No error message to say that the user is disabled.")

    printFP("INFO - Enabled user is able to log in.")
    return Global.PASS, 'TEST PASS - Enabled user is able to log in.'

def CheckDisableResult(disabled_user=None, disabled_pw=None):
    if not(any(substring in Global.driver.current_url for substring in ['disabled','login'])):
        Logout()
        time.sleep(2)
    else:
        Global.driver.get('https://172.20.4.40/amplemanage/login')
        time.sleep(2)

    if not('amplemanage/login' in Global.driver.current_url):
        printFP("INFO - Test did not navigate to login page.")
        return Global.FAIL, 'TEST FAIL - Test did not navigate to login page.'

    inputElement = GetElement(Global.driver, By.ID, 'j_username')
    SendKeys(inputElement, disabled_user)

    inputElement = GetElement(Global.driver, By.ID, 'j_password')
    SendKeys(inputElement, disabled_pw)

    inputElement.submit()

    time.sleep(3)

    if not('amplemanage/login/disabled' in Global.driver.current_url):
        printFP("INFO - Test did not navigate to user disabled page. Current URL: %s" %(Global.driver.current_url))
        return Global.FAIL, "TEST FAIL - Test did not navigate to user disabled page. Current URL: %s" %(Global.driver.current_url)

    try:
        message = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-danger']/div/span")
        printFP("INFO - There is an error message that is displayed.")
    except:
        printFP("INFO - No error message to say that the user is disabled.")
        return Global.FAIL, 'TEST FAIL - No error message to say that the user is disabled.'

    return Global.PASS, 'TEST PASS - %s' %(message.text)

def UpdateOwnProfile(updated_values=None):
    if not (updated_values):
        testComment = "Test is missing mandatory parameter(s)."
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    #Navigate to Update Profile -- will use information in json file
    GoToUpdateProfile()
    params = ParseJsonInputFile(updated_values)

    result = Global.PASS
    #Tries editting Username field
    if GetElement(Global.driver, By.ID, 'userName').get_attribute("readonly") == 'true':
        printFP("User Name is Read-Only and cannot be editted.")
    else:
        printFP("User Name is not Read-Only and can be editted.")
        result = Global.FAIL

    #Fills in each field
    fieldIDs = ["firstName", "middleName", "lastName", "email"]
    for ID in fieldIDs:
        inputElement = GetElement(Global.driver, By.ID, ID)
        ClearInput(inputElement)
        inputElement.send_keys(params[ID])

    #Fills in the Time Zone field
    preference_tab = GetElement(Global.driver, By.XPATH, "//*[@id='preferences']/a").click()
    time.sleep(2)
    GetElement(Global.driver, By.XPATH, "//span[@tabindex='-1']").click()
    inputElement = GetElement(Global.driver, By.XPATH, "//input[@type='search']")
    inputElement.send_keys(params['Time Zone'])
    inputElement.send_keys(Keys.RETURN)
    GetElement(Global.driver, By.XPATH, "//button[text()='Update']").click()

    #Checks for success message
    returnmsg = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-success']/div/span").text
    if 'Your profile have been updated successfully.' in returnmsg:
        printFP("INFO - Clicking Update returns 'Your profile have been updated successfully'.")
    else:
        GetElement(Global.driver, By.CLASS_NAME,'glyphicon-remove-circle').click()
        printFP('INFO - ' + returnmsg)
        return Global.FAIL, 'TEST FAIL - ' + returnmsg

    #Perform verification to ensure that the data was correctly changed.
    Global.driver.refresh()
    time.sleep(2)
    GoToUpdateProfile()

    for ID in fieldIDs:
        if GetElement(Global.driver, By.ID, ID).get_attribute("value") == params[ID]:
            printFP("INFO - Field with ID %s matches. Both have value %s" % (ID, GetElement(Global.driver, By.ID, ID).get_attribute("value")))
        else:
            printFP("INFO - Field with ID %s does not match. JSON value is %s while displayed Ample value is %s" %(ID, params[ID], GetElement(Global.driver, By.ID, ID).get_attribute("value")))
            result = Global.FAIL

    inputElement = GetElement(Global.driver, By.XPATH, "//span[@class='ui-select-match-text pull-left']/span")
    if inputElement.text != params["Time Zone"]:
        printFP("INFO - Time Zone Field did not match. JSON value is %s while Ample value is %s." % (inputElement.get_attribute("value"), params["Time Zone"]))
        result = Global.FAIL
    else:
        printFP("INFO - Time Zone Field did match. Both have value %s" % params["Time Zone"])

    #Closes window using exit button on the window
    GetElement(Global.driver, By.CLASS_NAME,'glyphicon-remove-circle').click()

    #Return result
    if result == Global.PASS:
        testComment = "Test was able to successfully update the profile of the currently logged in user."
    else:
        testComment = "Test was unable to update the profile of the currently logged in user."
    printFP("INFO - " + testComment)
    return result, 'TEST PASS - ' + testComment if result == Global.PASS else ('TEST FAIL - ' + testComment)

def TableSortTest(username=None):
    if not username:
        testComment = 'TEST FAIL - Test is missing mandatory parameter(s)'
        printFP(testComment)
        return Global.FAIL, testComment

    try:
        GoToUserMan()
    except WebDriverException :
        testComment = "TEST FAIL - WebDriverException Occured. May be caused due to being logged in at user level."
        printFP(testComment)
        return Global.FAIL, testComment

    OrderOfUsers=[]
    OrderOfUsersAfter=[]

    #Finds the page that the username is on then grabs the order of the users on that page
    userRow = FindUser(username)
    tbodyElement = GetElement(Global.driver, By.TAG_NAME, 'tbody')
    users = GetElements(tbodyElement, By.TAG_NAME, 'tr')
    for i in range(len(users)):
        OrderOfUsers.append(GetElement(users[i], By.XPATH, 'td[2]/span').text)
    printFP("INFO - Original order: {}" .format(OrderOfUsers))
    GetElement(userRow, By.TAG_NAME, 'input').click()

    #Changes the rights of the specified user from User->Admin or Admin->User
    GetElement(Global.driver, By.XPATH, xpaths['user_man_edit']).click()
    time.sleep(2)
    formElement = GetElement(Global.driver, By.TAG_NAME, 'form')
    formGroups = GetElements(formElement, By.CLASS_NAME, 'form-group')
    if 'User' in GetElement(formGroups[5], By.TAG_NAME, 'button').text:
        original = 'User'
        new = 'Administrator'
    else:
        original = 'Administrator'
        new = 'User'

    ClickButton(formGroups[5], By.TAG_NAME, 'button')
    dropdownMenu = GetElement(formGroups[5], By.XPATH, xpaths['user_man_role_dropdown'])
    SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', new)

    ClickButton(Global.driver, By.XPATH, xpaths['user_man_update'])
    time.sleep(2)

    #Checks if there was any change at all to the table because of the change
    tbodyElement = GetElement(Global.driver, By.TAG_NAME, 'tbody')
    users = GetElements(tbodyElement, By.TAG_NAME, 'tr')
    for i in range(len(users)):
        OrderOfUsersAfter.append(GetElement(users[i], By.XPATH, 'td[2]/span').text)
    printFP("INFO - Order after changing role values: {}" .format(OrderOfUsersAfter))

    #Changes the user back to it's original access rights
    userRow = FindUser(username)
    GetElement(userRow, By.TAG_NAME, 'input').click()

    GetElement(Global.driver, By.XPATH, xpaths['user_man_edit']).click()
    formElement = GetElement(Global.driver, By.TAG_NAME, 'form')
    formGroups = GetElements(formElement, By.CLASS_NAME, 'form-group')
    ClickButton(formGroups[5], By.TAG_NAME, 'button')
    dropdownMenu = GetElement(formGroups[5], By.XPATH, xpaths['user_man_role_dropdown'])
    SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', original)

    ClickButton(Global.driver, By.XPATH, xpaths['user_man_update'])

    #Checks if the order of the users are the same
    if OrderOfUsers == OrderOfUsersAfter:
        testComment = 'Order was not changed when changing Roles.'
        result = Global.PASS
    else:
        testComment = 'Order was changed when changing Roles.'
        result = Global.FAIL

    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def SelectMultipleUser(usernames):
    for i in range(len(usernames)):
        userRow = FindUser(usernames[i])
        userCheckBox = GetElement(userRow, By.TAG_NAME, 'input')
        SetCheckBox(userCheckBox, 'true')
        time.sleep(2)
        try:
            GetElement(Global.driver, By.PARTIAL_LINK_TEXT, 'First').click()
        except Exception as e:
            printFP(e.message)
            pass

def EditOwnDetailsInUserMan(user_name=None):
    if not user_name:
        testComment = 'Test is missing mandatory parameter(s)'
        printFP(testComment)
        return Global.FAIL, testComment
    try:
        GoToUserMan()
    except WebDriverException:
        testComment = "TEST FAIL - WebDriverException Occured. May be caused due to being logged in at user level."
        printFP(testComment)
        return Global.FAIL, testComment
    #Tries to edit own user details inside User Management
    printFP("INFO - Attempting to Edit Own User Details.")
    row = GetDevice(user_name)
    time.sleep(0.5)

    #Own user checkbox should be disabled by default; returns PASS or FAIL dependent on that
    value = GetElement(row, By.TAG_NAME, 'input').get_attribute('disabled')
    if value == 'true':
        testComment = 'TEST PASS - Unable to edit own user details. Unable to click checkbox'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'TEST FAIL - Able to click checkbox for own user name {}'.format(user_name)
        printFP(testComment)
        return Global.FAIL, testComment

def VerifyUserCapabilities(input_file_path=None, testDev=None, checkonscreens=None, checkexportbutton=False,  exportargs=None):
    if not (input_file_path and testDev and checkonscreens):
        testComment = 'Test is missing mandatory parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    """Must be logged in as a User"""
    params = ParseJsonInputFile(input_file_path)

    sysadmin = [xpaths['settings_sys_admin'], xpaths['settings_config_prop'], xpaths['settings_man_prof'], xpaths['dev_upgrade_settings_button'], xpaths['settings_user_man'], xpaths['settings_audit_trail'], xpaths['settings_notif_temp']]
    devman = [xpaths['dev_man_edit'], xpaths['dev_man_add_device'], xpaths['dev_man_unregister'], xpaths['dev_man_register'], xpaths['dev_man_delete']]
    devconfig = [xpaths['dev_configure_button']]
    devup = [xpaths['dev_upgrade_button']]
    linemon = [xpaths['line_mon_fault_events'], xpaths['line_mon_disturbances'], xpaths['line_mon_waveforms'], xpaths['line_mon_logi'], xpaths['line_mon_dnp3'],]
    currentjobs = [xpaths['current_jobs_config'], xpaths['current_jobs_upgrade']]
    accounts = [xpaths['dash_person_update_prof'], xpaths['dash_person_email_alert'], xpaths['dash_person_change_pw'], xpaths['dash_person_logout']]

    if 'sysadmin' in checkonscreens:
    #Attempts to go into Management/Settings locations as a User
        for i in range(len(sysadmin)):
            result, testComment = CheckPageButtonLinkAccessibility(sysadmin[i], 'disabled', xpaths['settings'])
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    if 'accounts' in checkonscreens:
    #Attempts to go into Management/Settings locations as a User
        for i in range(len(accounts)):
            result, testComment = CheckPageButtonLinkAccessibility(accounts[i], 'enabled', xpaths['dash_gear'])
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    if 'currentjobs' in checkonscreens:
        for i in range(len(currentjobs)):
            result, testComment = CheckPageButtonLinkAccessibility(currentjobs[i], 'enabled', xpaths['current_jobs_menu'])
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    #Attempts to perform Administrative actions such as delete/configure/unregister
    if 'devman' in checkonscreens:
        GoToDevMan()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "TEST FAIL - Unable to locate locations based off input file in Manage Device Page"
            printFP(testComment)
            return Global.FAIL, testComment

        for n in range(len(devman)):
            SelectDevice(testDev)
            result, testComment = CheckPageButtonLinkAccessibility(devman[n], 'disabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

        if not TableColumnSettingsButtonAccess():
            return Global.FAIL, 'TEST FAIL - User is not able to access column settings button in Ample where all user roles are allowed. Please check log file.'

    if 'devconfig' in checkonscreens:
        GoToDevConfig()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "Unable to locate locations based off input file in Configuration Page"
            printFP(testComment)
            return Global.FAIL, testComment

        SelectDevice(testDev)
        for n in range(len(devconfig)):
            result, testComment = CheckPageButtonLinkAccessibility(devconfig[n], 'disabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

        if not TableColumnSettingsButtonAccess():
            return Global.FAIL, 'TEST FAIL - User is not able to access column settings button in Ample where all user roles are allowed. Please check log file.'

    #Attemps to perform Administrative action such as OTAP upgrade
    if 'devup' in checkonscreens:
        GoToDevUpgrade()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "Unable to locate locations based off input file in Upgrade Page"
            printFP(testComment)
            return Global.FAIL, testComment

        SelectDevice(testDev)
        for n in range(len(devup)):
            result, testComment = CheckPageButtonLinkAccessibility(devup[n], 'disabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

        if not TableColumnSettingsButtonAccess():
            return Global.FAIL, 'TEST FAIL - User is not able to access column settings button in Ample where all user roles are allowed. Please check log file.'

    if 'linemon' in checkonscreens:
        GoToLineMonitoring()
        for i in range(len(linemon)):
            result, testComment = CheckPageButtonLinkAccessibility(linemon[i], 'enabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    if checkexportbutton:
        new_test_method_name = exportargs['exporttestmethodname']
        printFP('Testing export button access. Calling external function: {}' .format(new_test_method_name))
        del exportargs['exporttestmethodname']
        exportargs['input_file_path'] = input_file_path
        args = exportargs
        result, testComment = globals()[new_test_method_name](**args)
        if result == Global.FAIL:
            testComment = 'TEST FAIL - User is not able to access excel/csv export button. Please check the log file.'
            printFP(testComment)
            return Global.FAIL, testComment

    testComment = 'TEST PASS - User level is unable to access certain parts of the GUI and unable to perform any edits.'
    printFP(testComment)
    return Global.PASS, testComment

def GetFirstUserName(tableBodyElement):
    """Reads the first username in the user management page. The purpose is
    to determine whether the test is on the last page of user management.
    If it tries to click next page and the first user is the same, then
    it reached the last page.
    Args:
      tableBodyElement = web element representing the user management
                         table on GUI"""

    firstrow = GetElement(tableBodyElement, By.TAG_NAME, 'tr')
    username = GetText(firstrow, By.TAG_NAME, 'span')
    #printFP(username)
    return username

def GoToNextPageInTable():
    #Clicks the next page in the table, return true if able else return false
    try:
        usermgnttableview = GetElement(Global.driver, By.CLASS_NAME, 'user-management-table-view')
        tablefooter = GetElement(usermgnttableview, By.CLASS_NAME, 'table-footer')
        pageoptions = GetElement(tablefooter, By.CLASS_NAME, 'pager-options')
        pageoptionslist = GetElements(pageoptions, By.TAG_NAME, 'div')
    except Exception as e:
        return False

    for pageoption in pageoptionslist:
        elementtmp = GetElement(pageoption, By.TAG_NAME, 'a')
        elementname = elementtmp.text.strip()
        classname = pageoption.get_attribute('class')

        if "Next" in elementname:
            if not 'disabled' in classname:
                try:
                    elementtmp.click()
                    time.sleep(2)
                    return True
                except Exception as e:
                    printFP(e.message)
                    printFP('INFO - Unable to click "%s" Page Button' % elementname)
                    return False
            else:
                return False
    return False

def GoToPrevPageInTable():
    #clicks the previous page in the user management table, return true if able else false
    try:
        usermgnttableview = GetElement(Global.driver, By.CLASS_NAME, 'user-management-table-view')
        tablefooter = GetElement(usermgnttableview, By.CLASS_NAME, 'table-footer')
        pageoptions = GetElement(tablefooter, By.CLASS_NAME, 'pager-options')
        pageoptionslist = GetElements(pageoptions, By.TAG_NAME, 'div')
    except Exception as e:
        return False

    for pageoption in pageoptionslist:
        elementtmp = GetElement(pageoption, By.TAG_NAME, 'a')
        elementname = elementtmp.text.strip()
        classname = pageoption.get_attribute('class')

        if "Prev" in elementname:
            if not 'disabled' in classname:
                try:
                    elementtmp.click()
                    time.sleep(2)
                    return True
                except Exception as e:
                    printFP(e.message)
                    printFP('INFO - Unable to click "%s" Page Button' % elementname)
                    return False
            else:
                return False
    return False

def GetUserNamesList():
    """Reads the user management table to find a user.
    Args:
      string username - name that you want to find
    Returns:
      Usernames List"""

    # Create a list
    usernameslist = []
    try:
        tableRows = GetElements(Global.driver, By.XPATH, "//tr[@ng-repeat='user in $data']/td[2]")
    except:
        printFP("INFO - No Table Rows were found.")
        return []

    for i in range(len(tableRows)):
        usernameslist.append(tableRows[i].text)

    return usernameslist

def FindUser(username):
    """Reads the user management table to find a user. Navigates to next page
    until it finds the user or reachs the last page.
    Args:
      string username - name that you want to find
    Returns:
      None - Could not find user
      rowWithUser - web element representing the row of the table that contains
                    username"""

    table = GetElement(Global.driver, By.XPATH, "//table/tbody")
    firstusers = []
    for page in range(10):
        # try to find the user in the visible table
        rowWithUser = FindRowInTable(table, username)

        # compare the last first user to the current first user
        # if they are the same, then the test has reached the last page of the user table
        #  without finding the username
        firstusers.append(GetFirstUserName(table))
        if len(firstusers) > 1:
            if firstusers[page] == firstusers[page-1]:
                printFP('INFO - %s not found on any page.' % username)
                return None

        # go to next page if did not find user
        if rowWithUser == None:
            if ClickButton(Global.driver, By.XPATH, xpaths['user_man_next_page']):
                time.sleep(0.5)
                printFP('INFO - Did not find %s. Searching in next page.' % username)
                continue
        else:
            return rowWithUser

def SelectUser(username):
    """Searches user management table for username then checks the box """
    printFP("INFO - Selecting User %s" %(username))
    usermgntusers = GetElements(Global.driver, By.XPATH, "//tr[@ng-repeat='user in $data']")
    for i in range(len(usermgntusers)):
        rowUser = GetElement(usermgntusers[i], By.XPATH, "td[2]").text
        if username == rowUser:
            printFP("INFO - Found username %s" %(username))
            inputElement = GetElement(usermgntusers[i], By.XPATH, "td[1]/input")
            if inputElement.get_attribute('disabled') == 'disabled':
                printFP("INFO - Could not select checkbox.")
                return False
            elif inputElement.get_attribute('type') == "checkbox":
                SetCheckBox(inputElement, 'true')
                return True

    return False

def AddUser(user):
    printFP('INFO - Going to user management')
    GoToUserMan()
    printFP('INFO - Adding a user')
    ClickButton(Global.driver, By.XPATH, xpaths['user_man_add'])
    time.sleep(2)
    printFP('INFO - Filling out form')
    returnval = True
    try:
        GetElement(Global.driver, By.XPATH, "//span[@class='modal-title h4 ng-scope ng-binding' and text()='Create A New User']")
    except:
        printFP("INFO - Create User Window did not open.")
        return False

    if 'General' in user.keys():
        general = GetElement(Global.driver, By.ID, "general")
        if not('active' in general.get_attribute('class')):
            general.click()

        time.sleep(1)

        tabWindow = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']")
        formGroups = GetElements(tabWindow, By.CLASS_NAME, 'form-group')
        # Fill in fields on form
        field = GetElement(formGroups[0], By.TAG_NAME, 'input')
        SendKeys(field, user['General']['username'])

        field = GetElement(formGroups[1], By.TAG_NAME, 'input')
        SendKeys(field, user['General']['firstname'])

        field = GetElement(formGroups[2], By.TAG_NAME, 'input')
        SendKeys(field, user['General']['middlename'])

        field = GetElement(formGroups[3], By.TAG_NAME, 'input')
        SendKeys(field, user['General']['lastname'])

        field = GetElement(formGroups[4], By.TAG_NAME, 'input')
        SendKeys(field, user['General']['email'])

        field = GetElement(formGroups[5], By.TAG_NAME, 'input')
        SendKeys(field, user['General']['password'])

        field = GetElement(formGroups[6], By.TAG_NAME, 'input')
        SendKeys(field, user['General']['confirmpassword'])

        GetElement(formGroups[7], By.TAG_NAME, 'button').click()
        time.sleep(1)
        dropdownMenu = GetElement(formGroups[7], By.XPATH, xpaths['user_man_role_dropdown'])
        if not SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', user['General']['role']):
            printFP('Unable to select given role: ' + user['General']['role'])
            return False

    if 'Preferences' in user.keys():
        pref = GetElement(Global.driver, By.ID, "preferences")
        pref.click()
        time.sleep(1)

        tabWindow = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']")
        formGroups = GetElements(tabWindow, By.CLASS_NAME, 'form-group')
        # Fill in fields on form
        if('timezone' in user['Preferences'].keys()):
            fields = GetElement(formGroups[0], By.XPATH, "//span[@tabindex='-1']").click()
            inputElement = GetElement(formGroups[0], By.XPATH, "//input[@type='search']")
            inputElement.send_keys(user['Preferences']['timezone'])
            inputElement.send_keys(Keys.RETURN)
        # Fill in fields on form
        if('temperatureunit' in user['Preferences'].keys()):
            dropdownMenu = GetElement(Global.driver, By.XPATH, xpaths['user_man_temperatureunit_dropdown'])
            dropdownMenu.click()
            selectTemp = GetElement(Global.driver, By.XPATH, "//div[text()='"+user['Preferences']['temperatureunit']+"']")
            selectTemp.click()
        time.sleep(1)

    try:
        ClickButton(Global.driver, By.XPATH, xpaths['user_man_submit'])
    except Exception as e:
        printFP(e.message)
        printFP('Unable to click Add User Create Button')
        return False
    
    try:
        errorVerify = GetElements(Global.driver, By.XPATH, "//span[contains(@ng-show, '(key ==')]")
        for error in errorVerify:
            if not('ng-hide' in error.get_attribute('class')):
                printFP("INFO - Error message shown: %s" %(error.text))
                returnval = False

        errorLength = GetElement(Global.driver, By.XPATH, "//span[@ng-show='objectKeys(form.userFieldsForm.$error).length > 1']")
        if not('ng-hide' in errorLength.get_attribute('class')):
            printFP("INFO - Error message shown: %s" %(errorLength.text))
            returnval = False

        errorMultiple = GetElement(Global.driver, By.XPATH, "//span[@ng-show='(errors && (errors.length > 1))']")
        if not('ng-hide' in errorMultiple.get_attribute('class')):
            printFP("INFO - Error message shown: %s" %(errorMultiple.text))
            returnval = False
    except:
        printFP("INFO - No String Verification Error")

    #Checks for error messages with fields
    try:
        errormsgs = GetElements(Global.driver, By.CLASS_NAME, "ample-error-message")
        for errormsg in errormsgs:
            if not 'ng-hide' in errormsg.get_attribute('class'):
                printFP("INFO - Error in creating User: %s" %errormsg.text)
                returnval = False
    except:
        printFP('INFO - No Ample Error Messages')

    #Checks for error message popup
    try:
        msg = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-danger']/div/span")
        if msg.text != '':
            printFP("INFO - Error: %s" %msg.text)
            returnval = False
        else:
            printFP("INFO - No Alert-Danger Messages.")
    except:
        printFP("INFO - No Alert-Danger Messages.")

    if not returnval:
        GetElement(Global.driver, By.XPATH, xpaths['user_man_close']).click()
    return returnval

def EditUser(user=None):
    printFP('INFO - Going to user management')
    GoToUserMan()
    printFP("Editting User: {}" .format(user['username']))
    returnval = True
    rowWithUser = FindUser(user['username'])
    checkBox = GetElement(rowWithUser, By.TAG_NAME, 'input')
    if checkBox.get_attribute('disabled'):
        testComment = 'Test cannot edit user because user is disabled.'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    SetCheckBox(checkBox, 'true')
    time.sleep(1)
    try:
        GetElement(Global.driver, By.XPATH, xpaths['user_man_edit']).click()
    except Exception as e:
        printFP(e.message)
        printFP('Unable to click Edit User Create Button')
        return False

    try:
        addusertabs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='tab in userProfileTabs']")
        for i in range(len(addusertabs)):
            linkElement = GetElement(addusertabs[i], By.XPATH, 'a')
            time.sleep(1)
            if not('active' in linkElement.get_attribute('class')):
                linkElement.click()

            if 'General' in linkElement.text:
                forms = GetElements(Global.driver, By.TAG_NAME, 'form')
                for form in forms:
                    parentelement = GetElement(form, By.XPATH, '../../../../..')
                    classname = parentelement.get_attribute('class')
                    if 'active' in classname:
                        time.sleep(1)
                        formGroups = GetElements(form, By.CLASS_NAME, 'form-group')
                        # Fill in fields on form
                        if 'username' in user['General'].keys():
                            field = GetElement(formGroups[0], By.TAG_NAME, 'input')
                            ClearInput(field)
                            SendKeys(field, user['General']['username'])

                        if 'firstname' in user['General'].keys():
                            field = GetElement(formGroups[1], By.TAG_NAME, 'input')
                            ClearInput(field)
                            SendKeys(field, user['General']['firstname'])

                        if 'middlename' in user['General'].keys():
                            field = GetElement(formGroups[2], By.TAG_NAME, 'input')
                            ClearInput(field)
                            SendKeys(field, user['General']['middlename'])

                        if 'lastname' in user['General'].keys():
                            field = GetElement(formGroups[3], By.TAG_NAME, 'input')
                            ClearInput(field)
                            SendKeys(field, user['General']['lastname'])

                        if 'email' in user['General'].keys():
                            field = GetElement(formGroups[4], By.TAG_NAME, 'input')
                            ClearInput(field)
                            SendKeys(field, user['General']['email'])

                        if 'role' in user['General'].keys():
                            GetElement(formGroups[5], By.TAG_NAME, 'button').click()
                            time.sleep(1)
                            dropdownMenu = GetElement(formGroups[5], By.XPATH, xpaths['user_man_role_dropdown'])
                            if not(SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', user['General']['role'])):
                                testComment = "Test could not find %s role." %(user['General']['role'])
                                printFP("INFO - " + testComment)
                                Global.driver.refresh()
                                return Global.FAIL, 'TEST FAIL - ' + testComment
            elif 'Preferences' in linkElement.text and 'Preferences' in user.keys():
                forms = GetElements(Global.driver, By.TAG_NAME, 'form')
                for form in forms:
                    parentelement = GetElement(form, By.XPATH, '../../../../..')
                    classname = parentelement.get_attribute('class')
                    if 'active' in classname:
                        formGroups = GetElements(form, By.CLASS_NAME, 'form-group')
                        # Fill in fields on form
                        if 'timezone' in user['Preferences'].keys():
                            fields = GetElement(formGroups[0], By.XPATH, "//span[@tabindex='-1']").click()
                            inputElement = GetElement(formGroups[0], By.XPATH, "//input[@type='search']")
                            inputElement.send_keys(user['Preferences']['timezone'])
                            inputElement.send_keys(Keys.RETURN)
                            time.sleep(2)

                        # Fill in fields on form
                        if 'temperatureunit' in user['Preferences'].keys():
                            dropdownMenu = GetElement(formGroups[1], By.XPATH, xpaths['user_man_temperatureunit_dropdown'])
                            dropdownMenu.click()
                            SelectFromMenu(dropdownMenu, By.XPATH, "//span[@class='ui-select-choices-row-inner']", user['Preferences']['temperatureunit'])
                            time.sleep(1)
    except Exception as e:
        printFP("INFO - Exception occurred before clicking Update.")
        printFP(e.message)
        return False

    try:
        ClickButton(Global.driver, By.XPATH, "//div[@class='modal-footer']/button[text()='Update']")
    except Exception as e:
        printFP(e.message)
        printFP('Unable to click Edit User Update Button')
        return False

    #Checks for error messages with fields
    try:
        errormsgs = GetElements(formElement, By.CLASS_NAME, "ample-error-message")
        for errormsg in errormsgs:
            if not 'ng-hide' in errormsg.get_attribute('class'):
                printFP("INFO - Error in creating User: %s" %errormsg.text)
                returnval = False
    except:
        printFP('INFO - There were no errors found')
        pass

    #Checks for error message popup
    try:
        msg = GetElement(Global.driver, By.XPATH, xpaths['user_man_create_err']).text
        time.sleep(1)
        if "Email address already exists" in msg:
            printFP("INFO - Error: %s" %msg.text)
            returnval = False
    except:
        printFP('INFO - There were no errors found')
        pass

    if not returnval:
        GetElement(Global.driver, By.XPATH, xpaths['user_man_close']).click()
    return True

def DeleteUser(username):
    #Finds username and deletes it, false if not able to find username
    if SelectUser(username):
        deleteButton = GetElement(Global.driver, By.XPATH, "//button[text()='Delete']")
        if 'disabled' in deleteButton.get_attribute('class'):
            printFP("INFO - Delete Button is disabled.")
            return False
        deleteButton.click()
        time.sleep(1)
        ClickButton(Global.driver, By.XPATH, "//div[@class='modal-footer ng-scope']/button[text()='Ok']")
        return True
    else:
        return False

def CreateUser(user_json):
    #loads the json into a variable
    with open(user_json, 'r') as infile:
        user = json.load(infile)
    return user

def EditUserTest(edit_user_path=None):
    if not edit_user_path:
        testComment = 'TEST FAIL - Test is missing a mandatory parameter(s)'
        printFP(testComment)
        return Global.FAIL, testComment

    #Creates dictionary based on json file
    user = CreateUser(Global.testResourcePath + edit_user_path)
    try:
        GoToUserMan()
    except WebDriverException:
        testComment = "TEST FAIL - WebDriverException Occurred. May be caused due to being logged in at user level."
        printFP(testComment)
        return Global.FAIL, testComment

    #Shows all fields in user management table
    ButtonElement = GetElement(Global.driver, By.XPATH, "//button[@class='btn btn-default column-settings-btn dropdown-toggle']")
    ButtonElement.click()

    fields = GetElement(Global.driver, By.XPATH, xpaths['user_man_header_box'])
    fieldinputs = GetElements(Global.driver, By.XPATH, "//label[@class='checkbox column-label ng-scope']/input[@type='checkbox' and @ng-model='column.visible']")
    for i in fieldinputs:
        if i.get_attribute("checked"):
            pass
        else:
            SetCheckBox(i, "true")
    GetElement(Global.driver, By.XPATH, "//button[@class='btn btn-default column-settings-btn dropdown-toggle']").click()
    time.sleep(1)

    #Gets information of the user before change
    userInfoList = GetUserInformation(user['username'])

    #Performs edit of user and checks if it changed, if it did then return true else return false
    if EditUser(user):
        if not userInfoList == (GetUserInformation(user['username'])):
            testComment = 'User Information changes immediately after editing details of user {}' .format(user['username'])
            printFP('INFO - ' + testComment)
            Global.driver.refresh()
            return Global.PASS, 'TEST PASS - ' + testComment
        else:
            testComment = 'User Information still matches.'
            printFP('INFO - ' + testComment)
            Global.driver.refresh()
            return Global.FAIL, 'TEST FAIL - ' + testComment
    else:
        testComment = 'Test was unable to edit the user details'
        printFP('INFO - ' + testComment)
        Global.driver.refresh()
        return Global.FAIL, 'TEST FAIL - ' + testComment

def GetUserInformation(username):
    #Returns a list of the username's information in order as shown on AMPLE
    rowUser = FindUser(username)
    userInfo = []
    for i in range(2,9):
        userInfo.append(GetElement(rowUser, By.XPATH, 'td['+str(i)+']/span').text)
    return userInfo

def AddUserTest(user_profile_path):
    #creates user dictionary based on user json file
    user = CreateUser(Global.testResourcePath + user_profile_path)

    #Adds user to AMPLE; if unable to add returns FAIL
    if AddUser(user):
        usernamelist = GetUserNamesList()
        addeduser = user['General']['username']

        if addeduser in usernamelist:
            testComment = 'TEST PASS - Successfully added user %s' % user['General']['username']
            printFP('INFO - Successfully added user %s' % user['General']['username'])
            return Global.PASS, testComment

        else:
            while GoToNextPageInTable():
                usernamelist = GetUserNamesList()
                if addeduser in usernamelist:
                    testComment = 'TEST PASS - Successfully added user %s' % user['General']['username']
                    printFP('INFO - Successfully added user %s' % user['General']['username'])
                    return Global.PASS, testComment
                    
            while GoToPrevPageInTable():
                usernamelist = GetUserNamesList()
                if addeduser in usernamelist:
                    testComment = 'TEST PASS - Successfully added user %s' % user['General']['username']
                    printFP('INFO - Successfully added user %s' % user['General']['username'])
                    return Global.PASS, testComment

            testComment = 'User added but not found in table'
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment
    else:
        testComment = 'Failed to add user to table'
        printFP('INFO - '+ testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

def DeleteUserTest(username):
    printFP('Deleting user: %s' %username)
    GoToUserMan()
    usernamelist = GetUserNamesList()
    deleteuserstatus = None

    if username in usernamelist:
        deleteuserstatus = DeleteUser(username)
    else:
        while GoToPrevPageInTable():
            usernamelist = GetUserNamesList()
            if username in usernamelist:
                deleteuserstatus = DeleteUser(username)
        while GoToNextPageInTable():
            usernamelist = GetUserNamesList()
            if username in usernamelist:
                deleteuserstatus = DeleteUser(username)

    if deleteuserstatus:
        Global.driver.refresh()
        time.sleep(2)
        usernamelist = GetUserNamesList()

        if username in usernamelist:
            testComment = 'Successfully Deleted user %s . But user is still exist in the table' % username
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - '+testComment
        else:
            while GoToPrevPageInTable():
                usernamelist = GetUserNamesList()
                if username in usernamelist:
                    testComment = 'Successfully Deleted user %s . But user is still exist in the table' % username
                    printFP('INFO - ' + testComment)
                    return Global.FAIL, 'TEST FAIL - ' + testComment
            while GoToNextPageInTable():
                usernamelist = GetUserNamesList()
                if username in usernamelist:
                    testComment = 'Successfully Deleted user %s . But user is still exist in the table' % username
                    printFP('INFO - ' + testComment)
                    return Global.FAIL, 'TEST FAIL - ' + testComment

        testComment = 'Successfully Deleted user %s' % username
        printFP('INFO - '+ testComment)
        return Global.PASS, 'TEST PASS - '+ testComment
    else:
        testComment = 'Failed to delete user %s' % username
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

def VerifyUserCapabilitiesExportData(input_file_path=None, downloadfolder=None):
    if input_file_path == None or downloadfolder == None:
        testComment = "Missing a mandatory parameter"
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    linemon = [xpaths['line_mon_disturbances'], xpaths['line_mon_waveforms'], xpaths['line_mon_logi']]
    devman = [xpaths['dev_man_manage_dev'], xpaths['dev_man_config'], xpaths['dev_man_inactive_dev'], xpaths['dev_man_phaseid']]

    GoToDevman()
    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = 'Provided input values are not valid.'
        printFP(testComment)
        return Global.FAIL, testComment

    for i in range(len(devman)):
        GetElement(Global.driver, By.XPATH, devman[i]).click()
        nodataavailable = NoDataAvailable()
        if not nodataavailable == "No Data Available":
            exportbutton = ClickExportButton()
            if not ClickExportCSVEXCELButton(exportbutton, 'CSV'):
                testComment = 'TEST FAIL - User is not able to access csv export button in Dev Management Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            csvlocation = downloadfolder + "export.csv"
            exportbutton = ClickExportButton()
            if not ClickExportCSVEXCELButton(exportbutton, 'EXCEL'):
                testComment = 'TEST FAIL - User is not able to access excel export button in Dev Management Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            excellocation = downloadfolder + "export.xls"
            time.sleep(5) # must keep this sleep for export download time (bigger file will require you to change it)
            try:
                os.remove(csvlocation)
                os.remove(excellocation)
            except OSError as e:
                os.remove(downloadfolder + 'export.xlsx')
                printFP('INFO - ' + e.message)

            testComment = "Successfully deleted exported files from download folder"
            printFP('INFO - ' + testComment)

    testComment = "Successfully exported files from device management pages with View Only Role Permission"
    printFP('INFO - ' + testComment)

    GoToLineMonitoring()
    time.sleep(1)

    for i in range(len(linemon)):
        GetElement(Global.driver, By.XPATH, linemon[i]).click()
        nodataavailable = NoDataAvailable()
        if not nodataavailable == "No Data Available":
            exportbutton = ClickExportButton()
            if not ClickExportCSVEXCELButton(exportbutton, 'CSV'):
                testComment = 'TEST FAIL - User is not able to access csv export button in Line Monitoring Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            csvlocation = downloadfolder + "export.csv"
            exportbutton = ClickExportButton()
            if not ClickExportCSVEXCELButton(exportbutton, 'EXCEL'):
                testComment = 'TEST FAIL - User is not able to access excel export button in Line Monitoring Pages. Please check the log file.'
                printFP(testComment)
                return Global.FAIL, testComment
            excellocation = downloadfolder + "export.xls"
            time.sleep(5) # must keep this sleep for export download time (bigger file will require you to change it)
            try:
                os.remove(csvlocation)
                os.remove(excellocation)
            except OSError as e:
                os.remove(downloadfolder + 'export.xlsx')
                printFP('INFO - ' + e.message)

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

    params = ParseJsonInputFile(input_file_path)

    GoToLineMonitoring()
    GoToLineMonFaultEvents()
    getsite = GetSiteFromTop(params['Region'], params['Substation'], params['Feeder'], params['Site'])
    time.sleep(1)
    if getsite:
        SelectAllEventStates()
        time.sleep(1)
        SelectAllEventTypes()
        time.sleep(1)
        SelectAllTriggeredDetectors()
        time.sleep(2)
        nodataavailable = NoDataAvailable()
        if not nodataavailable == "No Data Available":
            printFP("Given site has faultevents")
            siterows = GetElements(Global.driver, By.XPATH, "//span[text()='" + params['Site'] + "']")
            for row in siterows:
                try:
                    parentelement = GetElement(row, By.XPATH, "..")
                    deviceevent = GetElement(parentelement, By.XPATH, "//span[text()='" + params['Phase'] + "']")
                except Exception as e:
                    printFP(e.message)
                    pass
            deviceevent.click()
            time.sleep(2)
            downloadbutton = GetElement(Global.driver, By.XPATH, "//button[text()='Download']")
            if 'disabled' in downloadbutton.get_attribute('class'):
                GoToLineMonWaveforms()
                time.sleep(1)
                downloadbutton = GetElement(Global.driver, By.XPATH, "//button[text()='Download']")
                if 'disabled' in downloadbutton.get_attribute('class'):
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
        testComment = 'Test Fail - Unable to locate Given site "%s"' %params['Site']
        printFP(testComment)
        return Global.FAIL, testComment

def DisableUserAccount(username=None):
    printFP('INFO - Going to user management')
    GoToUserMan()
    printFP("Disabling Account for the user: {}" .format(username))
    returnval = True
    rowWithUser = FindUser(username)
    try:
        disablebutton = GetElement(rowWithUser, By.XPATH, "td[contains(@class,'action-column')]/div/span[contains(@tooltip,'Disable')]")
    except Exception as e:
        printFP('INFO - Unable to find disable user button')
        return False

    if not 'disabled' in disablebutton.get_attribute('class'):
        disablebutton.click()
        time.sleep(1)
    else:
        printFP('INFO - Disable User button is disabled for user: ' + username)
        return False

    try:
        disablepromptframe = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'confirm-modal-body')]")
    except:
        Global.driver.refresh()
        printFP("INFO - Disable User confirmation window is not prompted")
        return False

    if 'Do you want to disable this user?' in disablepromptframe.text:
        ClickButton(Global.driver, By.XPATH, "//button[@ng-click='confirm()' and text()='Ok']")
        time.sleep(2)

    try:
        errormsg = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'modal-body']")
        printFP("INFO - Error in disabling user: %s" %errormsg.text)
        GetElement(Global.driver, By.XPATH, "//span[@ng-click='closeModal()']").click()
        return Global.FAIL, 'TEST FAIL - Error in disabling user.'
    except:
        printFP('INFO - There were no errors found')

    currentenabledsstatus = FilteredDataFromTableMapping('User Name', 'Enabled', 'user-management-view')
    if currentenabledsstatus[username] == 'false':
        printFP("INFO - Enabled Status in the table is updated to False after disabled the user successfully")
        return True
    else:
        printFP("INFO - Enabled Status in the table is not updated to False after disabled the user successfully")
        return False

def EnableUserAccount(username):
    printFP('INFO - Going to user management')
    GoToUserMan()
    printFP("Enabling Account for the user: {}" .format(username))
    returnval = True
    rowWithUser = FindUser(username)
    try:
        enablebutton = GetElement(rowWithUser, By.XPATH, "td[contains(@class,'action-column')]/div/span[contains(@tooltip,'Enable')]")
    except Exception as e:
        printFP('INFO - Unable to find enable user button')
        return False

    if not 'disabled' in enablebutton.get_attribute('class'):
        enablebutton.click()
        time.sleep(1)
    else:
        printFP('INFO - Enable User button is disabled for user:' + username)
        return False

    enablepromptframe = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'confirm-modal-body')]")
    if 'Do you want to enable this user?' in enablepromptframe.text:
        ClickButton(Global.driver, By.XPATH, "//button[@ng-click='confirm()' and text()='Ok']")
        time.sleep(2)
    else:
        printFP("INFO - Enable User confirmation window is not prompted")
        return False

    try:
        errormsg = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'modal-body']")
        printFP("INFO - Error in enabling user: %s" %errormsg.text)
        GetElement(Global.driver, By.XPATH, "//span[@ng-click='closeModal()']").click()
        return False
    except:
        printFP('INFO - There were no errors found')
        pass

    currentenabledsstatus = FilteredDataFromTableMapping('User Name', 'Enabled', 'user-management-view')
    if currentenabledsstatus[username] == 'true':
        printFP("INFO - Enabled Status in the table is updated to True after enabled the user successfully")
        return True
    else:
        printFP("TEST FAIL - Enabled Status in the table is not updated to True after enabled the user successfully")
        return False

def ResetPasswordForUserAccount(username):
    printFP('INFO - Going to user management')
    GoToUserMan()
    printFP("Reset Password for the user: {}" .format(username))
    returnval = True
    rowWithUser = FindUser(username)
    try:
        resetpwdbutton = GetElement(rowWithUser, By.XPATH, "td[contains(@class,'action-column')]/div/span[contains(@tooltip,'Reset')]")
    except Exception as e:
        printFP('INFO - Unable to find reset password button')
        return False

    if not 'disabled' in resetpwdbutton.get_attribute('class'):
        resetpwdbutton.click()
        time.sleep(1)
    else:
        printFP('INFO - Reset Password button is disabled for user:' + username)
        return False

    resetpasswordpromptframe = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'confirm-modal-body')]")
    if 'Do you want to force the user to reset password on the next login?' in resetpasswordpromptframe.text:
        ClickButton(Global.driver, By.XPATH, "//button[@ng-click='confirm()' and text()='Ok']")
    else:
        printFP("INFO - Reset Password confirmation window is not prompted")
        return False
    try:
        errormsg = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'modal-body']")
        printFP("INFO - Error while reset password: %s" %errormsg.text)
        GetElement(Global.driver, By.XPATH, "//span[@ng-click='closeModal()']").click()
        returnval = False
    except:
        printFP('INFO - There were no errors found')

    return True

def CheckResetPasswordUserAccountLogin(username, password, new_password):
    Logout()
    result, testComment = Login(username, password)

    if result == Global.FAIL:
        alertmessage = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-warning')]/div/span").text
        printFP('INFO - Reset Message: ' + alertmessage)
        if 'Kindly reset your password' in alertmessage:
            currentPw = GetElement(Global.driver, By.ID, 'currentPassword')
            SendKeys(currentPw, password)
            inputElement = GetElement(Global.driver, By.ID, 'newPassword')
            SendKeys(inputElement, new_password)
            inputElement = GetElement(Global.driver, By.ID, 'confirmPassword')
            SendKeys(inputElement, new_password)
            ClickButton(Global.driver, By.XPATH, "//button[contains(text(),'Reset')]")
            time.sleep(2)
            try:
                alertmessage = GetElement(Global.driver, By.XPATH, "//div[contains(@class,'alert-success')]/div/span").text
                printFP(alertmessage)
            except Exception as e:
                printFP('TEST FAIL - Error while setting new password')
                return False

            if 'Your password was successfully changed - please login with your new password' in alertmessage:
                GetElement(Global.driver, By.XPATH, "//a[@ng-show='!resetPasswordSuccess' and text()='Ok']")
                time.sleep(2)
                result, testComment = Login(username, new_password)
                time.sleep(1)
                if result == Global.PASS:
                    return True
                else:
                    printFP('INFO - Timed out trying to login after successfully set up new password')
                    return False
            else:
                printFP('TEST FAIL - Set new password successfully. But Expected Alert Success message is not matched')
                return False
        else:
            printFP('TEST FAIL - Set new password screen shown successfully. But Expected Alert Warning is not matched')
            return False
    else:
        printFP('TEST FAIL - Reached dashboard successfully with Forced Reset Password account credentials')
        return False

def CheckDisableAndForceResetActionButtons():
    printFP('INFO - Verifying User Management Disable and Reset Password action buttons presence and its status')
    GoToUserMan()

    tablerows = GetElements(Global.driver, By.XPATH, "//tr[@ng-repeat='user in $data']")
    for row in tablerows:
        try:
            GetElement(row, By.XPATH, "td[14]/div/span[contains(@class,'glyphicons-lock')]")
            printFP("INFO - Disable Button exists for user row")
        except:
            printFP("INFO - Disable Button does not exist one of the user rows")
            return Global.FAIL, "Disable Button does not exist one of the user rows"
        try:
            GetElement(row, By.XPATH, "td[14]/div/span[contains(@class,'glyphicons-force-reset')]")
            printFP("INFO - Force Reset Button exists for user row")
        except:
            printFP("INFO - Force Reset Button does not exist one of the user rows")
            return Global.FAIL, "Force Reset Button does not exist one of the user rows"
 
    testComment = "Each row in User Management had a Disable and Force Reset Button."
    printFP("INFO - " + testComment)
    return Global.PASS, testComment
     
def VerifyUserCapabilitiesAdminSuperAdmin(input_file_path=None, testDev=None, role=None, checkonscreens=None, checkexportbutton=False,  exportargs=None):
    if not (input_file_path and testDev and role and checkonscreens):
        testComment = 'Test is missing mandatory parameter'
        printFP(testComment)
        return Global.FAIL, testComment

    """Must be logged in as a User"""
    params = ParseJsonInputFile(input_file_path)

    sysadmin = [xpaths['settings_sys_admin'], xpaths['settings_config_prop'], xpaths['settings_man_prof'], xpaths['dev_upgrade_settings_button'], xpaths['settings_user_man'], xpaths['settings_audit_trail'], xpaths['settings_notif_temp']]
    devman = [xpaths['dev_man_edit'], xpaths['dev_man_add_device'], xpaths['dev_man_unregister'], xpaths['dev_man_register'], xpaths['dev_man_delete']]
    devconfig = [xpaths['dev_configure_button']]
    devup = [xpaths['dev_upgrade_button']]
    linemon = [xpaths['line_mon_fault_events'], xpaths['line_mon_disturbances'], xpaths['line_mon_waveforms'], xpaths['line_mon_logi'], xpaths['line_mon_dnp3'],]
    currentjobs = [xpaths['current_jobs_config'], xpaths['current_jobs_upgrade']]
    accounts = [xpaths['dash_person_update_prof'], xpaths['dash_person_email_alert'], xpaths['dash_person_change_pw'], xpaths['dash_person_logout']]
    configprop = [xpaths['settings_config_prop']]

    if 'sysadmin' in checkonscreens:
    #Attempts to go into Management/Settings locations as a User
        for i in range(len(sysadmin)):
            result, testComment = CheckPageButtonLinkAccessibility(sysadmin[i], 'enabled', xpaths['settings'])
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    if 'accounts' in checkonscreens:
    #Attempts to go into Management/Settings locations as a User
        for i in range(len(accounts)):
            result, testComment = CheckPageButtonLinkAccessibility(accounts[i], 'enabled', xpaths['dash_gear'])
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    if 'currentjobs' in checkonscreens:
        for i in range(len(currentjobs)):
            result, testComment = CheckPageButtonLinkAccessibility(currentjobs[i], 'enabled', xpaths['current_jobs_menu'])
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    if 'configprop' in checkonscreens:
        GetElement(Global.driver, By.XPATH, xpaths['settings']).click()
        GetElement(Global.driver, By.XPATH, configprop[0]).click()
        time.sleep(2)
        GetElement(Global.driver, By.ID, 'comPropertyLttpData').click()
        readonlyfieldcount = CountOfReadOnlyFieldsInTheForm()

        if role == 'admin':
            if readonlyfieldcount == 14:
                testComment = 'TEST PASS - Unable to edit LTTP setting with Admin role permission'
                printFP(testComment)
                ClickButton(Global.driver, By.XPATH, "//button[contains(text(),'Cancel')]")
            else:
                ClickButton(Global.driver, By.XPATH, "//button[contains(text(),'Cancel')]")
                testComment = 'TEST FAIL - Able to edit LTTP setting with Admin role permission'
                printFP(testComment)
                return Global.FAIL, testComment

        if role == 'superadmin' :
            if readonlyfieldcount == 0:
                try:
                    inputfield = GetElement(Global.driver, By.XPATH, "//span[contains(text(),'LTTP pull interval')]/../../span/input")
                    ClearInput(inputfield)
                    SendKeys(inputfield, randint(3, 20))
                    ClickButton(Global.driver, By.XPATH, "//button[contains(text(),'Save')]")
                    time.sleep(2)
                    lttpeditstatus = GetElement(Global.driver, By.XPATH, "//h4[contains(@class,'modal-title')]/span[2]")
                    if 'Success' in lttpeditstatus.text:
                        testComment = 'TEST PASS - Able to modify LTTP setting with Super Admin role permission'
                        printFP(testComment)
                    ClickButton(Global.driver, By.XPATH, "//button[contains(@class,'close')]")
                except Exception as e:
                    try:
                        ClickButton(Global.driver, By.XPATH, "//button[contains(text(),'Cancel')]")
                    except:
                        ClickButton(Global.driver, By.XPATH, "//button[contains(@class,'close')]")
                    printFP(e.message)
                    testComment = 'TEST FAIL - Unable to edit LTTP setting with Super Admin role permission'
                    printFP(testComment)
                    return Global.FAIL, testComment
            else:
                testComment = 'TEST FAIL - fields of LTTP setting are in readonly state for Super Admin User'
                printFP(testComment)
                return Global.FAIL, testComment


    #Attempts to perform Administrative actions such as delete/configure/unregister
    if 'devman' in checkonscreens:
        GoToDevMan()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "TEST FAIL - Unable to locate locations based off input file in Manage Device Page"
            printFP(testComment)
            return Global.FAIL, testComment

        for n in range(len(devman)):
            SelectDevice(testDev)
            result, testComment = CheckPageButtonLinkAccessibility(devman[n], 'enabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

        if not TableColumnSettingsButtonAccess():
            return Global.FAIL, 'TEST FAIL - User is not able to access column settings button in Ample where all user roles are allowed. Please check log file.'

    if 'devconfig' in checkonscreens:
        GoToDevConfig()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "Unable to locate locations based off input file in Configuration Page"
            printFP(testComment)
            return Global.FAIL, testComment

        SelectDevice(testDev)
        for n in range(len(devconfig)):
            result, testComment = CheckPageButtonLinkAccessibility(devconfig[n], 'enabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    #Attemps to perform Administrative action such as OTAP upgrade
    if 'devup' in checkonscreens:
        GoToDevUpgrade()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "Unable to locate locations based off input file in Upgrade Page"
            printFP(testComment)
            return Global.FAIL, testComment

        SelectDevice(testDev)
        for n in range(len(devup)):
            result, testComment = CheckPageButtonLinkAccessibility(devup[n], 'enabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

        if not TableColumnSettingsButtonAccess():
            return Global.FAIL, 'TEST FAIL - User is not able to access column settings button in Ample where all user roles are allowed. Please check log file.'

    if 'linemon' in checkonscreens:
        GoToLineMonitoring()
        for i in range(len(linemon)):
            result, testComment = CheckPageButtonLinkAccessibility(linemon[i], 'enabled')
            if not result:
                printFP(testComment)
                return Global.FAIL, testComment

    if checkexportbutton:
        new_test_method_name = exportargs['exporttestmethodname']
        printFP('Testing export button access. Calling external function: {}' .format(new_test_method_name))
        del exportargs['exporttestmethodname']
        exportargs['input_file_path'] = input_file_path
        args = exportargs
        result, testComment = globals()[new_test_method_name](**args)
        if result == Global.FAIL:
            testComment = 'TEST FAIL - User is not able to access excel/csv export button. Please check the log file.'
            printFP(testComment)
            return Global.FAIL, testComment

    testComment = 'TEST PASS - Admin/SuperAdmin is able to access all features in Ample'
    printFP(testComment)
    return Global.PASS, testComment
