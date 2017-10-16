import Global
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
from Ample_DevMan import *


def Add100UsersTest():
    #Custom test designed for Chong's use.
    role = ['Administrator', 'User']
    user = {}
    for i in range(100):
        user['username']='userTest%s'%i
        user['firstname']='selenium'
        user['middlename']='testing'
        user['lastname']='onehundred'
        user['email']='user%s@acceptance.testing'%i
        user['timezone']='(UTC-08:00) America/Los_Angeles'
        user['password']='@mpacity'
        user['confirmpassword']='@mpacity'
        user['role']=role[random.randint(0,1)]

        if not AddUser(user):
            testComment = 'Failed to add a user .. quitting test.'
            printFP("INFO - " + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

    testComment = 'Test successfully added 100 users.'
    printFP("INFO - " + testComment)
    return Global.PASS, 'TEST PASS - ' + testComment

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
    '''if not CheckIfStaleElement(inputElement):
        printFP("INFO - Update Information window may not have disappeared.")

    #Checks if there are error messages displayed due to your input
    try:
        error = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-warning']/div/span").text
        printFP("INFO - Error encountered. Message is %s. Refreshing page and ending." %error )
        Global.driver.refresh()
        return Global.FAIL, 'TEST FAIL - ' + error
    except:
        pass'''

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
    time.sleep(2)

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

def SelectMultipleUsersTest(usernames=None):
    if not usernames:
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    try:
        GoToUserMan()
    except WebDriverException :
        testComment = "TEST FAIL - WebDriverException Occured. May be caused due to being logged in at user level."
        printFP(testComment)
        return Global.FAIL, testComment

    #Selects multiple users
    SelectMultipleUser(usernames)

    #Checks if they are still checked as you navigate through pages
    testComment = ''
    result = Global.PASS
    for i in range(len(usernames)):
        userRow = FindUser(usernames[i])
        userCheckBox = GetElement(userRow, By.TAG_NAME, 'input')
        if not userCheckBox.is_selected():
            testComment = 'TEST FAIL - Username %s was selected, but became unselected' % usernames[i]
            result = Global.FAIL
            printFP(testComment)
        try:
            GetElement(Global.driver, By.PARTIAL_LINK_TEXT, 'First').click()
        except:
            pass

    if result == Global.PASS:
        return result, 'TEST PASS - ' + testComment
    else:
        return result, 'TEST FAIL - ' + testComment

def SelectMultipleUser(usernames):
    for i in range(len(usernames)):
        userRow = FindUser(usernames[i])
        userCheckBox = GetElement(userRow, By.TAG_NAME, 'input')
        SetCheckBox(userCheckBox, 'true')
        time.sleep(2)
        try:
            GetElement(Global.driver, By.PARTIAL_LINK_TEXT, 'First').click()
        except:
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

    if 'sysadmin' in checkonscreens:
    #Attempts to go into Management/Settings locations as a User
        for i in range(len(sysadmin)):
            GetElement(Global.driver, By.XPATH, xpaths['settings']).click()
            try:
                link = GetElement(Global.driver, By.XPATH, sysadmin[i])
                if 'disabled' in link.get_attribute('class'):
                    pass
                else:
                    link.click()
                    testComment = 'TEST FAIL - User is able to access location in Ample where only Admins are allowed. Please check log file.'
                    printFP(testComment)
                    return Global.FAIL, testComment
            except:
                Global.driver.refresh()
                time.sleep(1)

    if 'accounts' in checkonscreens:
    #Attempts to go into Management/Settings locations as a User
        for i in range(len(accounts)):
            GetElement(Global.driver, By.XPATH, xpaths['dash_gear']).click()
            try:
                link = GetElement(Global.driver, By.XPATH, accounts[i])
                if 'disabled' in link.get_attribute('class'):
                    testComment = 'TEST FAIL - User is not able to access location in Ample where all user roles are allowed. Please check log file.'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    pass
            except:
                Global.driver.refresh()
                time.sleep(1)

    if 'currentjobs' in checkonscreens:
        for i in range(len(currentjobs)):
            GetElement(Global.driver, By.XPATH, xpaths['current_jobs_menu']).click()
            try:
                link = GetElement(Global.driver, By.XPATH, currentjobs[i])
                if 'disabled' in link.get_attribute('class'):
                    testComment = 'TEST FAIL - User is not able to access location in Ample where all user roles are allowed. Please check log file.'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    link.click()
                    pass
            except:
                Global.driver.refresh()
                time.sleep(1)

    #Attempts to perform Administrative actions such as delete/configure/unregister
    if 'devman' in checkonscreens:
        GoToDevMan()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "TEST FAIL - Unable to locate locations based off input file in Manage Device Page"
            printFP(testComment)
            return Global.FAIL, testComment

        for n in range(len(devman)):
            SelectDevice(testDev)
            try:
                link = GetElement(Global.driver, By.XPATH, devman[n])
                if 'disabled' in link.get_attribute('class'):
                    pass
                else:
                    link.click()
                    testComment = 'TEST FAIL - User is able to modify and change elements in Manage Device Page'
                    printFP(testComment)
                    return Global.FAIL, testComment
            except:
                Global.driver.refresh()
                time.sleep(1)

        if not TableColumnSettingsButtonAccess():
            return Global.FAIL, 'TEST FAIL - User is not able to access column settings button in Ample where all user roles are allowed. Please check log file.'

    if 'devconfig' in checkonscreens:
        GoToDevConfig()
        if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
            testComment = "Unable to locate locations based off input file in Configuration Page"
            printFP(testComment)
            return Global.FAIL, testComment

        SelectDevice(testDev)
        try:
            link = GetElement(Global.driver, By.XPATH, devconfig)
            if 'disabled' in link.get_attribute('class'):
                pass
            else:
                link.click()
                testComment = 'TEST FAIL - User is able to modify and change elements in Device Configuration Page'
                printFP(testComment)
                return Global.FAIL, testComment
        except:
            pass

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
        try:
            link = GetElement(Global.driver, By.XPATH, devup)
            if 'disabled' in link.get_attribute('class'):
                pass
            else:
                link.click()
                testComment = 'TEST FAIL - User is able to modify and change elements in Device Firmware Upgrade Page'
                printFP(testComment)
                return Global.FAIL, testComment
        except:
            pass

        if not TableColumnSettingsButtonAccess():
            return Global.FAIL, 'TEST FAIL - User is not able to access column settings button in Ample where all user roles are allowed. Please check log file.'

    if 'linemon' in checkonscreens:
        GoToLineMonitoring()
        for i in range(len(linemon)):
            try:
                link = GetElement(Global.driver, By.XPATH, linemon[i])
                if 'disabled' in link.get_attribute('class'):
                    testComment = 'TEST FAIL - User is not able to access location in Ample where all user roles are allowed. Please check log file.'
                    printFP(testComment)
                    return Global.FAIL, testComment
                else:
                    link.click()
                    pass
            except:
                Global.driver.refresh()
                time.sleep(1)

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
    except:
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
    except:
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
    time.sleep(5)
    usernameslist = []

    html = Global.driver.page_source

    page = soup(html, "lxml")

        # Get all usernames
    table = page.find('div', class_="user-management-table-view")

    tablebody = table.find('tbody')

    elements = tablebody.find_all('tr')

    for tr_tag in elements:
        usernameelement = tr_tag.find('span')

        username = usernameelement.text.strip('\n')

        usernameslist.append(username)

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

    table = GetElement(Global.driver, By.XPATH, xpaths['user_man_table'])
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
    usermgnttableview = GetElement(Global.driver, By.CLASS_NAME, 'user-management-table-view')
    time.sleep(1)
    usermgnttable = GetElement(usermgnttableview, By.TAG_NAME, 'table')
    time.sleep(1)
    usermgnttbody = GetElement(usermgnttable, By.TAG_NAME, 'tbody')
    time.sleep(1)
    usermgntusers = GetElements(usermgnttbody, By.TAG_NAME, 'tr')
    for usermgntuser in usermgntusers:
        usermgntusername = GetElements(usermgntuser, By.TAG_NAME, 'td')
        time.sleep(1)
        for finduser in usermgntusername:
            tmpusername = finduser.text
            #print ('tmpusername: %s' %tmpusername)
            #print ('Given username: %s' %username)
            if username == tmpusername:
                parentelementfinduser = finduser.find_element_by_xpath("..")
                #print parentelementfinduser
                time.sleep(1)
                cols = GetElements(parentelementfinduser, By.TAG_NAME, 'input')
                time.sleep(1)
                for element in cols:
                    #print element
                    if element.get_attribute('type') == "checkbox":
                        SetCheckBox(element, 'true')
                        return True
    return False

def AddUser(user):
    printFP('INFO - Going to user management')
    GoToUserMan()
    printFP('INFO - Adding a user')
    time.sleep(4)
    ClickButton(Global.driver, By.XPATH, xpaths['user_man_add'])
    time.sleep(2)
    printFP('INFO - Filling out form')
    returnval = True
    time.sleep(2)
    addusertabset = GetElement(Global.driver, By.CLASS_NAME, 'screen-tabset')
    addusertabframe = GetElement(addusertabset, By.TAG_NAME, 'ul')
    addusertabs = GetElements(addusertabframe, By.TAG_NAME, 'li')
    for tab in addusertabs:
        tabElement = GetElement(tab, By.TAG_NAME, 'a')
        JustClick(tabElement)
        time.sleep(1)
        tabname = tabElement.text
        print('tabname: %s' %tabname)
        if 'General' in tabname:
            forms = GetElements(Global.driver, By.TAG_NAME, 'form')
            for form in forms:
                parentelement = GetElement(form, By.XPATH, '../../../../..')
                classname = parentelement.get_attribute('class')
                print('classname: %s' %classname)
                if 'active' in classname:
                    time.sleep(1)
                    formGroups = GetElements(form, By.CLASS_NAME, 'form-group')
                    # Fill in fields on form
                    field = GetElement(formGroups[0], By.TAG_NAME, 'input')
                    SendKeys(field, user['username'])

                    field = GetElement(formGroups[1], By.TAG_NAME, 'input')
                    SendKeys(field, user['firstname'])

                    field = GetElement(formGroups[2], By.TAG_NAME, 'input')
                    SendKeys(field, user['middlename'])

                    field = GetElement(formGroups[3], By.TAG_NAME, 'input')
                    SendKeys(field, user['lastname'])

                    field = GetElement(formGroups[4], By.TAG_NAME, 'input')
                    SendKeys(field, user['email'])

                    field = GetElement(formGroups[5], By.TAG_NAME, 'input')
                    SendKeys(field, user['password'])

                    field = GetElement(formGroups[6], By.TAG_NAME, 'input')
                    SendKeys(field, user['confirmpassword'])

                    GetElement(formGroups[7], By.TAG_NAME, 'button').click()
                    time.sleep(1)
                    dropdownMenu = GetElement(formGroups[7], By.XPATH, xpaths['user_man_role_dropdown'])
                    SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', user['role'])
        elif 'Preferences' in tabname:
            forms = GetElements(Global.driver, By.TAG_NAME, 'form')
            for form in forms:
                parentelement = GetElement(form, By.XPATH, '../../../../..')
                classname = parentelement.get_attribute('class')
                print('classname: %s' %classname)
                if 'active' in classname:
                    formGroups = GetElements(form, By.CLASS_NAME, 'form-group')
                    print formGroups
                    time.sleep(1)
                    # Fill in fields on form
                    time.sleep(1)
                    '''GetElement(formGroups[0], By.TAG_NAME, 'button').click()
                    dropdownMenu = GetElement(formGroups[0], By.XPATH, xpaths['user_man_timezone_dropdown'])
                    SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', user['timezone'])
                    time.sleep(2)'''
                    fields = GetElement(formGroups[0], By.XPATH, "//span[@tabindex='-1']").click()
                    inputElement = GetElement(formGroups[0], By.XPATH, "//input[@type='search']")
                    inputElement.send_keys(user['timezone'])
                    inputElement.send_keys(Keys.RETURN)
                    time.sleep(2)
                    # Fill in fields on form
                    '''GetElement(formGroups[1], By.TAG_NAME, 'button').click()
                    time.sleep(1)
                    dropdownMenu = GetElement(formGroups[1], By.XPATH, xpaths['user_man_temperatureunit_dropdown'])
                    SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', user['temperatureunit'])'''
                    fields = GetElement(formGroups[1], By.XPATH, "//span[@tabindex='-1']").click()
                    time.sleep(1)
                    inputElement = GetElement(formGroups[1], By.XPATH, "//input[@type='search']")
                    inputElement.send_keys(user['temperatureunit'])
                    inputElement.send_keys(Keys.RETURN)
                    time.sleep(2)

    try:
        ClickButton(Global.driver, By.XPATH, xpaths['user_man_submit'])
    except Exception as e:
        print e.message
        printFP('Unable to click Add User Create Button')
        return False
    #Checks for error messages with fields
    try:
        errormsgs = GetElements(formElement, By.CLASS_NAME, "ample-error-message")
        for errormsg in errormsgs:
            if not 'ng-hide' in errormsg.get_attribute('class'):
                printFP("INFO - Error in creating User: %s" %errormsg.text)
                returnval = False
    except:
        pass

    #Checks for error message popup
    try:
        msg = GetElement(Global.driver, By.XPATH, xpaths['user_man_create_err']).text
        time.sleep(1)
        if "Email address already exists" in msg:
            printFP("INFO - Error: %s" %msg)
            returnval = False
    except:
        pass

    if not returnval:
        GetElement(Global.driver, By.XPATH, xpaths['user_man_close']).click()
    return True

def EditUser(user=None):
    printFP("Editting User: {}" .format(user['username']))
    returnval = True
    rowWithUser = FindUser(user['username'])
    checkBox = GetElement(rowWithUser, By.TAG_NAME, 'input')
    SetCheckBox(checkBox, 'true')
    time.sleep(1)
    GetElement(Global.driver, By.XPATH, xpaths['user_man_edit']).click()
    try:
        addusertabset = GetElement(Global.driver, By.CLASS_NAME, 'screen-tabset')
        addusertabframe = GetElement(addusertabset, By.TAG_NAME, 'ul')
        addusertabs = GetElements(addusertabframe, By.TAG_NAME, 'li')
        for tab in addusertabs:
            tabElement = GetElement(tab, By.TAG_NAME, 'a')
            JustClick(tabElement)
            time.sleep(1)
            tabname = tabElement.text
            print('tabname: %s' %tabname)
            if 'General' in tabname:
                forms = GetElements(Global.driver, By.TAG_NAME, 'form')
                for form in forms:
                    parentelement = GetElement(form, By.XPATH, '../../../../..')
                    classname = parentelement.get_attribute('class')
                    print('classname: %s' %classname)
                    if 'active' in classname:
                        time.sleep(1)
                        formGroups = GetElements(form, By.CLASS_NAME, 'form-group')
                        # Fill in fields on form
                        field = GetElement(formGroups[0], By.TAG_NAME, 'input')
                        SendKeys(field, user['username'])

                        field = GetElement(formGroups[1], By.TAG_NAME, 'input')
                        SendKeys(field, user['firstname'])

                        field = GetElement(formGroups[2], By.TAG_NAME, 'input')
                        SendKeys(field, user['middlename'])

                        field = GetElement(formGroups[3], By.TAG_NAME, 'input')
                        SendKeys(field, user['lastname'])

                        field = GetElement(formGroups[4], By.TAG_NAME, 'input')
                        SendKeys(field, user['email'])

                        field = GetElement(formGroups[5], By.TAG_NAME, 'input')
                        SendKeys(field, user['password'])

                        field = GetElement(formGroups[6], By.TAG_NAME, 'input')
                        SendKeys(field, user['confirmpassword'])

                        GetElement(formGroups[7], By.TAG_NAME, 'button').click()
                        time.sleep(1)
                        dropdownMenu = GetElement(formGroups[7], By.XPATH, xpaths['user_man_role_dropdown'])
                        SelectFromMenu(dropdownMenu, By.TAG_NAME, 'li', user['role'])
            elif 'Preferences' in tabname:
                forms = GetElements(Global.driver, By.TAG_NAME, 'form')
                for form in forms:
                    parentelement = GetElement(form, By.XPATH, '../../../../..')
                    classname = parentelement.get_attribute('class')
                    print('classname: %s' %classname)
                    if 'active' in classname:
                        formGroups = GetElements(form, By.CLASS_NAME, 'form-group')
                        time.sleep(1)
                        # Fill in fields on form
                        fields = GetElement(formGroups[0], By.XPATH, "//span[@tabindex='-1']").click()
                        inputElement = GetElement(formGroups[0], By.XPATH, "//input[@type='search']")
                        inputElement.send_keys(user['timezone'])
                        inputElement.send_keys(Keys.RETURN)
                        time.sleep(2)
                        # Fill in fields on form
                        fields = GetElement(formGroups[1], By.XPATH, "//span[@tabindex='-1']").click()
                        inputElement = GetElement(formGroups[1], By.XPATH, "//input[@type='search']")
                        inputElement.send_keys(user['temperatureunit'])
        try:
            ClickButton(Global.driver, By.XPATH, xpaths['user_man_submit'])
        except Exception as e:
            print e.message
            printFP('Unable to click Add User Create Button')
            return False
        #Checks for error messages with fields
        try:
            errormsgs = GetElements(formElement, By.CLASS_NAME, "ample-error-message")
            for errormsg in errormsgs:
                if not 'ng-hide' in errormsg.get_attribute('class'):
                    printFP("INFO - Error in creating User: %s" %errormsg.text)
                    returnval = False
        except:
            pass

        #Checks for error message popup
        try:
            msg = GetElement(Global.driver, By.XPATH, xpaths['user_man_create_err']).text
            time.sleep(1)
            if "Email address already exists" in msg:
                printFP("INFO - Error: %s" %msg)
                returnval = False
        except:
            pass

        if not returnval:
            GetElement(Global.driver, By.XPATH, xpaths['user_man_close']).click()
        return True
    except:
        return False

def DeleteUser(username):
    #Finds username and deletes it, false if not able to find username
    if SelectUser(username):
        ClickButton(Global.driver, By.XPATH, xpaths['user_man_delete'])
        time.sleep(1)
        ClickButton(Global.driver, By.XPATH, xpaths['user_man_confirm_delete'])
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
    user = CreateUser(edit_user_path)
    try:
        GoToUserMan()
    except WebDriverException:
        testComment = "TEST FAIL - WebDriverException Occured. May be caused due to being logged in at user level."
        printFP(testComment)
        return Global.FAIL, testComment
    time.sleep(2)

    #Shows all fields in user management table
    ButtonElement = GetElement(Global.driver, By.XPATH, xpaths['user_man_header_btn'])
    ButtonElement.click()

    fields = GetElement(Global.driver, By.XPATH, xpaths['user_man_header_box'])
    fieldinputs = GetElements(fields, By.TAG_NAME, 'input')
    for i in fieldinputs:
        try:
            SetCheckBox(i, "true")
        except:
            pass
    GetElement(Global.driver, By.XPATH, xpaths['user_man_header_btn']).click()
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
    user = CreateUser(user_profile_path)
    time.sleep(2)

    #Adds user to AMPLE; if unable to add returns FAIL
    if AddUser(user):
        Global.driver.refresh()
        time.sleep(10)

        usernamelist = GetUserNamesList()
        addeduser = user['username']

        printFP(usernamelist)

        if addeduser in usernamelist:
            testComment = 'TEST PASS - Successfully added user %s' % user['username']
            printFP('INFO - Successfully added user %s' % user['username'])
            return Global.PASS, testComment

        else:
            while GoToNextPageInTable():
                usernamelist = GetUserNamesList()
                print usernamelist
                if addeduser in usernamelist:
                    testComment = 'TEST PASS - Successfully added user %s' % user['username']
                    printFP('INFO - Successfully added user %s' % user['username'])
                    return Global.PASS, testComment
            while GoToPrevPageInTable():
                usernamelist = GetUserNamesList()
                print usernamelist
                if addeduser in usernamelist:
                    testComment = 'TEST PASS - Successfully added user %s' % user['username']
                    printFP('INFO - Successfully added user %s' % user['username'])
                    return Global.PASS, testComment

            testComment = 'User added but not found in table'
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment
    else:
        testComment = 'Failed to add user to table'
        printFP('INFO - '+ testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


def DeleteUserTest(user_profile_path, deleteuserstatus=False):

    params = ParseJsonInputFile(user_profile_path)

    deleteuser = params['username']
    printFP('Deleting user: %s' %deleteuser)

    GoToUserMan()
    time.sleep(3)
    Global.driver.refresh()
    time.sleep(5)

    usernamelist = GetUserNamesList()
    printFP(usernamelist)

    if deleteuser in usernamelist:
        deleteuserstatus = DeleteUser(deleteuser)
    else:
        while GoToPrevPageInTable():
            usernamelist = GetUserNamesList()
            if deleteuser in usernamelist:
                deleteuserstatus = DeleteUser(deleteuser)
        while GoToNextPageInTable():
            usernamelist = GetUserNamesList()
            if deleteuser in usernamelist:
                deleteuserstatus = DeleteUser(deleteuser)

    if deleteuserstatus:
        time.sleep(5)
        Global.driver.refresh()
        time.sleep(5)

        usernamelist = GetUserNamesList()

        printFP(usernamelist)

        if deleteuser in usernamelist:
            testComment = 'Successfully Deleted user %s . But user is still exist in the table' % params['username']
            printFP('INFO - '+testComment)
            return Global.FAIL, 'TEST FAIL - '+testComment
        else:
            while GoToPrevPageInTable():
                usernamelist = GetUserNamesList()
                if deleteuser in usernamelist:
                    testComment = 'Successfully Deleted user %s . But user is still exist in the table' % params['username']
                    printFP('INFO - '+testComment)
                    return Global.FAIL, 'TEST FAIL - '+testComment
            while GoToNextPageInTable():
                usernamelist = GetUserNamesList()
                if deleteuser in usernamelist:
                    testComment = 'Successfully Deleted user %s . But user is still exist in the table' % params['username']
                    printFP('INFO - '+testComment)
                    return Global.FAIL, 'TEST FAIL - '+testComment

        testComment = 'Successfully Deleted user %s' % params['username']
        printFP('INFO - '+ testComment)
        return Global.PASS, 'TEST PASS - '+ testComment
    else:
            testComment = 'Failed to delete user %s' % params['username']
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - '+testComment


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
                except:
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
