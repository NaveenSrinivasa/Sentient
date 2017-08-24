import Global
import json
import time
import csv
import math
import random
import re
from bs4 import BeautifulSoup as soup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from Utilities_Ample import *


def VerifyDefaultManagePage():

    GoToManageProfile()
    #Checks if disabled is naturally in the buttons; the following variables are boolean types
    newStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_new']).get_attribute('class')
    saveStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_save']).get_attribute('class')
    saveasStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_save_as']).get_attribute('class')
    deleteStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_delete']).get_attribute('class')

    #All of them should have disabled hence should be all true
    if (newStatus):
        printFP("INFO - New Button was disabled by default")
    if saveStatus:
        printFP("INFO - Save Button was disabled by default")
    if saveasStatus:
        printFP("INFO - Save As Button was disabled by default")
    if deleteStatus:
        printFP("INFO - Delete Button was disabled by default")

    if (newStatus and saveStatus and saveasStatus and deleteStatus):
        result = Global.FAIL
        testComment = 'Some buttons were disabled by default'
    else:
        result = Global.PASS
        testComment = 'No buttons were disabled by default'
    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def VerifyDefaultSelectedProfile():
    """Checks if the first profile is the default selected profile"""
    GoToManageProfile()
    #Gets all Profile List
    profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
    #Grabs the first link at the top of the list
    try:
        firstlink = GetElement(profilenameslist, By.XPATH, 'li[1]')
    except:
        testComment = "No Profiles exist currently"
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    #Checks if the first item is active; if it is, PASS, else FAIL
    if 'item-active' in firstlink.get_attribute('class'):
        testComment = 'First profile is active'
        result = Global.PASS
    else:
        testComment = 'First profile is not active.'
        result = Global.FAIL

    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def VerifyProfileTabs(existing_profile_name=None):
    if not existing_profile_name:
        testComment = "Test is missing mandatory parameter(s)."
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    """Checks if all tabs exist"""
    GoToManageProfile()
    idLocators = ["info", "cfciData", "nonCfciData", "logiData", "anomalyData"]
    result = Global.PASS

    #Checks if new profile creation has all the neceessary tabs
    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_new'])
    for i in range(len(idLocators)):
        try:
            GetElement(Global.driver, By.ID, idLocators[i])
        except:
            result = Global.FAIL
            printFP("INFO - Could not locate tab with ID %s" %idLocators[i])

    Global.driver.refresh()

    #Checks if a given profile has all the mandatory tabs
    profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
    selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', existing_profile_name)
    if not selectedstatus:
        testComment = "Could not locate profile name"
        printFP(testComment)
        return Global.FAIL, testComment

    for i in range(len(idLocators)):
        try:
            GetElement(Global.driver, By.ID, idLocators[i])
        except:
            result = Global.FAIL
            printFP("INFO - Could not locate tab with ID %s" %idLocators[i])

    if result == Global.FAIL:
        testComment = 'Some tabs were unable to be found.'
    else:
        testComment = 'All tabs were found and exist'

    printFP('INFO - ' + testComment)
    return result, (('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment))

def SaveProfileWithoutChanges(existing_profile_name=None):
    if not existing_profile_name:
        testComment = "Test is missing mandatory parameter(s)."
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    GoToManageProfile()
    #goes to the specific profile given by existing profile name and selects it
    profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
    selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', existing_profile_name)
    if selectedstatus:
        #Clicks save
        try:
            time.sleep(2)
            GetElement(Global.driver, By.XPATH, xpaths['man_prof_save']).click()
        except:
            testComment = 'Test could not retrieve/click save button for this profile'
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

        #Gets the return message after clicking save
        message = GetText(Global.driver, By.XPATH, xpaths['mp_return_message'], visible=True)
        printFP(message.strip().strip("-"))

        #if it displays 'no change' error then PASS else FAIL
        if 'No change' in message:
            return Global.PASS, 'TEST PASS - ' + message
        else:
            return Global.FAIL, 'TEST FAIL - ' + message

    else:
        testComment = 'Test could not locate profile name %s' %existing_profile_name
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

def FillInProfileFields(tabID, fields):
    """Clicks the given tab and fills in the fields with values. Assumes
    that the new profile dialogue is open.
    Args:
      string tabID - id of tab you wish to fill out ('logi' or 'cfci')
      dict fields - dictionary of fields:values

    If the field is a checkbox, the value should be 1 for check, 0 for clear"""

    # Navigate to the appropriate tab
    tabElement = GetElement(Global.driver, By.ID, tabID)
    tabElement.click()
    # Get all the fields in profile
    fieldElements = GetElements(Global.driver, By.TAG_NAME, 'fieldset')
    # Iterate through the config profile parameters
    for field_label in fields:
        value = fields[field_label]
        # Check if the field matches the desired ones from the config csv
        for fieldElement in fieldElements:
            fieldName = GetText(fieldElement, By.CLASS_NAME, 'pull-left') # pull-left
            if field_label in fieldName:
                # Check the input type (ie. checkbox or text field)
                try:
                    inputElement = fieldElement.find_element_by_tag_name('input')
                    inputType = inputElement.get_attribute('type')
                    # Input value
                    if 'checkbox' in inputType:
                        SetCheckBox(inputElement, value)
                    elif 'text' in inputType:
                        ClearInput(inputElement)
                        inputElement.send_keys(value)
                        time.sleep(1)
                    else:
                        printFP('INFO - Do not recognize this input type')
                except:
                    # switch type
                    inputElement = GetElement(fieldElement, By.CLASS_NAME, 'toggle-switch')
                    SetSwitch(inputElement, value)

def CreateProfile(profile_name, profile_json):
    """Reads profile name and config file from inputFP and calls
    FillInProfileFields to generate the profile."""

    GoToManageProfile()
    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_new'])

    with open(profile_json, 'r') as infile:
        time.sleep(1)
        profile = json.load(infile)

    #Fill in fields
    time.sleep(2)
    inputElement = GetElement(Global.driver, By.XPATH, xpaths['mp_profile_name'])
    SendKeys(inputElement, profile_name)
    if 'cfciData' in profile:
        FillInProfileFields('cfciData', profile['cfciData'])
    if 'nonCfciData' in profile:
        FillInProfileFields('nonCfciData', profile['nonCfciData'])
    if 'logiData' in profile:
        FillInProfileFields('logiData', profile['logiData'])
    if 'anomalyData' in profile:
        FillInProfileFields('anomalyData', profile['anomalyData'])
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_create'])
    time.sleep(2)
    try:
        confirmButton = GetElement(Global.driver, By.XPATH, xpaths['man_prof_submit'])
        confirmButton.click()
        time.sleep(2)
        if not CheckIfStaleElement(confirmButton):
            printFP("INFO - Confirm button was not gone.")
    except:
        printFP("INFO - Test unable to locate submit button")
        pass

    message = GetText(Global.driver, By.XPATH, xpaths['mp_return_message'], visible=True)
    printFP('INFO - ' + message.strip().strip("-"))
    if 'Profile saved successfully' in message:
        result = Global.PASS
    else:
        result = Global.FAIL

    return result, (('TEST PASS - ' + message) if result == Global.PASS else ('TEST FAIL - ' + message))

def SelectProfileManage(profile_name):
    """In manage profile, if the dropdown is open, selects profileName
    from the dropdown"""

    menu = GetElement(Global.driver, By.XPATH, xpaths['man_prof_menu'])
    SelectFromMenu(menu, By.TAG_NAME, 'li', profile_name)

def DeleteProfile(profile_name):
    """Reads profileName from inputFP. Selects profileName and deletes it."""

    GoToManageProfile()
    profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
    selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', profile_name)
    if selectedstatus:
        ClickButton(Global.driver, By.XPATH, xpaths['man_prof_delete'])
        time.sleep(1)
        confirmDelete = GetElement(Global.driver, By.XPATH, "//button[text()='Ok']")
        confirmDelete.click()
        time.sleep(5)
        if not CheckIfStaleElement(confirmDelete):
            printFP("INFO - Confirm delete window did not close.")
        returnMessage = GetText(Global.driver, By.XPATH, xpaths['mp_delete_return_message'])
        printFP('INFO - ' + returnMessage)
        if 'Profile deleted successfully.' in returnMessage:
            result = Global.PASS
        else:
            result = Global.FAIL
            returnMessage = 'There is an error displayed for deleting profile name : %s' % profile_name
        closeWindow = GetElement(Global.driver, By.XPATH, "//button[text()='Close']")
        closeWindow.click()
        if not CheckIfStaleElement(closeWindow):
            printFP("INFO - Message box did not close.")
        return result, (('TEST PASS - ' + returnMessage) if result == Global.PASS else ('TEST FAIL - ' + returnMessage))
    else:
        testComment = 'Unable to find profile name : %s' % profile_name
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

def CloneProfile(profile_name=None, clone_profile_name=None):
    GoToManageProfile()
    time.sleep(2)
    #Selects a profile name
    profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
    time.sleep(2)
    selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', profile_name)
    time.sleep(2)
    if selectedstatus:
        #Go to profile name tab and click Save
        if not ('active' in GetElement(Global.driver, By.XPATH, '//*[@id="info"]').get_attribute('class')):
            ClickButton(Global.driver, By.ID, 'info')
        tabcontentDiv = GetElement(Global.driver, By.CSS_SELECTOR, 'div.info.tabs.ng-scope')
        try:
            time.sleep(2)
            nameElement = GetElement(tabcontentDiv, By.TAG_NAME, 'input')
            time.sleep(2)
            ClearInput(nameElement)
            nameElement.send_keys(clone_profile_name)
        except:
            testComment = 'Exception occured when trying to fill out name text box'
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

        ClickButton(Global.driver, By.XPATH, "//button[text()=' Save As']")
        try:
            time.sleep(2)
            element = WebDriverWait(Global.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//span[contains(text(),"Save Profile As")]')))
            ClickButton(Global.driver, By.XPATH, xpaths['man_prof_submit'])
            time.sleep(2)
            if not CheckIfStaleElement(element):
                printFP("INFO - Save Profile As window did not close.")
        except:
            printFP("INFO - Pop up window for cloning profile did not work.")

        #check what the return message is after clicking submit
        try:
            message = GetText(Global.driver, By.XPATH, xpaths['mp_return_message'], visible=True)
            printFP('INFO - ' + message.strip().strip("-"))
            if 'Profile name is already exist' in message:
                return Global.FAIL, 'TEST FAIL - ' + message
        except:
            pass

        #Checks if the new cloned profile is in the list of profiles
        profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
        selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', profile_name)
        if selectedstatus:
            result = Global.PASS
            returnMessage = "Found new cloned profile %s" %clone_profile_name
        else:
            result = Global.FAIL
            returnMessage = "Did not find new cloned profile %s" %clone_profile_name
        printFP('INFO - ' + returnMessage)
        return result, (('TEST PASS - ' + returnMessage) if result == Global.PASS else ('TEST FAIL - ' + returnMessage))
    else:
        testComment = 'Unable to find profile name : %s' % profile_name
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

def ValidateProfileFieldValues(input_file_path):
    with open(input_file_path, 'rt') as f:
        reader = csv.reader(f)
        dnpPoints = {r[0]: [r[1],r[2],r[3]] for r in reader}

    tabIDs = ['cfciData', 'nonCfciData', 'logiData', 'anomalyData']
    result = Global.PASS
    # Does five checks -- lower than min , min, default, max, greater than max
    for n in range(5):
        #Creates A new profile Each time
        GoToManageProfile()
        print 'bala'
        newProfileButton = GetElement(Global.driver, By.XPATH, "//button[text()=' New']")
        newProfileButton.click()
        #For each tab, fill it out each field with lower than min, min, default, max or greater than max
        for m in range(len(tabIDs)):
            time.sleep(2)
            tabElement = GetElement(Global.driver, By.ID, tabIDs[m])
            time.sleep(2)
            print tabElement
            time.sleep(1)
            tabElement.click()
            time.sleep(2)

            activedivElement = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']")
            spanFields = GetElements(activedivElement, By.TAG_NAME, 'input')
            #For each field in the active div fill out each field
            for i in range(len(spanFields)):
                precedingSibling = GetElement(spanFields[i], By.XPATH, "../preceding-sibling::span/span")
                tooltip = precedingSibling.get_attribute('tooltip')
                ClearInput(spanFields[i])
                #Offsets must be handled differently since they are time based not integer based
                if 'Offset' in tooltip:
                    if n == 0:
                        spanFields[i].send_keys('-1300')
                    elif n == 1:
                        spanFields[i].send_keys('-1200')
                    elif n == 2:
                        spanFields[i].send_keys('0000')
                    elif n == 3:
                        spanFields[i].send_keys('1200')
                    elif n == 4:
                        spanFields[i].send_keys('1300')
                else:
                    if n == 0:
                        spanFields[i].send_keys(str(int(dnpPoints[tooltip][0])-1))
                    elif n == 1:
                        spanFields[i].send_keys(dnpPoints[tooltip][0])
                    elif n == 2:
                        spanFields[i].send_keys(dnpPoints[tooltip][1])
                    elif n == 3:
                        spanFields[i].send_keys(dnpPoints[tooltip][2])
                    elif n == 4:
                        spanFields[i].send_keys(str(int(dnpPoints[tooltip][2])+1))

                """after each field has been filled out, if it is under min or greater than max, test will hit create
                to check if the input field changes its class to contain 'field-error'; if it is checking for valid values,
                then it will wait until """
                if n == 0 or n == 4:
                    try:
                        saveButton = GetElement(Global.driver, By.XPATH, "//button[text()=' Create']")
                        saveButton.click()
                    except:
                        printFP("INFO - Test was unable to click Create.")
                        return Global.FAIL, 'TEST FAIL - Test was unable to click create'
                    try:
                        error = GetElement(Global.driver, By.XPATH, "//span[contains(text(),'Please correct the errors on the form.')]")
                    except:
                        try:
                            saveWindow = GetElement(Global.driver, By.XPATH, "//span[text()=' Save Profile As ']")
                            closeButton = GetElement(Global.driver, By.CLASS_NAME, 'close-icon')
                            closeButton.click()
                        except:
                            printFP("INFO - Test encountered unknown error. Refreshing page and ending test.")
                            Global.driver.refresh()
                            return Global.FAIL, 'TEST FAIL - Unknown error occurred while hitting Create in outside range test'

                    classVal = spanFields[i].get_attribute('class')
                    if n == 0 or n == 4:
                        if 'field-error' in classVal:
                            pass
                        else:
                            result = Global.FAIL
                            printFP("INFO - Field %s did not have an error when inputting a value outside its range." %tooltip)

        if n != 0 and n != 4:
            try:
                saveButton = GetElement(Global.driver, By.XPATH, "//button[text()=' Create']")
                saveButton.click()
                saveWindow = GetElement(Global.driver, By.XPATH, "//span[text()=' Save Profile As ']")
                nameElement = GetElement(Global.driver, By.ID, 'newProfileName')
                ClearInput(nameElement)
                nameElement.send_keys('TESTTRIAL')
                createButton = GetElement(Global.driver, By.XPATH, "//button[text()='Create']")
                createButton.click()
                if not CheckIfStaleElement(createButton):
                    printFP("INFO - Save Profile window may still be up")
            except:
                printFP("INFO - Test ran into an exception while trying to save the profile after clicking create. Refreshing and then ending test.")
                Global.driver.refresh()
                return Global.FAIL, 'TEST FAIL - Test ran into exception when trying to create and save a valid profile.'

            try:
                successmsg = GetElement(Global.driver, By.CLASS_NAME, 'inline-success')
                if 'Profile saved successfully' in successmsg.text:
                    printFP("INFO - Profile saved successfully.")
                else:
                    printFP("INFO - Wrong return message. Return message was %s" % successmsg.text)
            except:
                printFP("INFO - Test did not save profile correctly. Refreshing page and ending test.")
                Global.driver.refresh()
                return Global.FAIL, 'TEST FAIL - Test did not save profile correctly.'
            DeleteProfile('TESTTRIAL')

    return Global.PASS, 'TEST PASS - Test verified that all ranges are good according to DNP point CSV file'

def CompareDefault(profileFile, testfield, testfieldvalue):

    tabIDdict = {
        "cFCI Events": 'cfciData',
        "NoncFCI Events": 'nonCfciData',
        'Log-I': 'logiData',
        'Anomaly': 'anomalyData'
    }
    tabID=None

    with open(profileFile,'r') as reqdnp3pointslist:
        for line in reqdnp3pointslist:
            pair = line.strip('\n').split(',')
            if testfield == pair[0]:
                tabID = pair[1]
    if not tabID:
        testComment = 'Could not find test field in required DNP csv file.'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    GoToManageProfile()

    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_new'])
    time.sleep(1)
    ClickButton(Global.driver, By.ID, tabIDdict[tabID])
    try:
        tooltipElement = GetElement(Global.driver, By.XPATH, "//span[@tooltip='"+testfield+"']/../../span[2]/input")
        printFP("INFO - Found element with tool tip %s" % testfield)
        inputValue = tooltipElement.get_attribute('value')
        if inputValue == testfieldvalue:
            testComment = "Default value on CSV {} matches GUI default value {}." .format(testfieldvalue, inputValue)
            result = Global.PASS
        else:
            testComment = "Default value on CSV {} does not match GUI default value {}" .format(testfieldvallue, inputValue)
            result = Global.FAIL
        printFP("INFO - " + testComment)
        return result, testComment
    except:
        return Global.FAIL, "TEST FAIL - Could not locate test field %s " % testfield

def FillInProfileField(tabID, field, value):
    # Navigate to the appropriate tab
    tab = GetElement(Global.driver, By.ID, tabID)
    tab.click()
    time.sleep(2)

    xpath = "//*[@tooltip='"+field+"']/../../span[2]/input"
    try:
        inputElement = GetElement(Global.driver, By.XPATH, xpath)
        ClearInput(inputElement)
        inputElement.send_keys(value)
    except:
        xpath = xpath = "//*[@tooltip='"+field+"']/../../span[2]/div/div/span[2]"
        inputElement = GetElement(Global.driver, By.XPATH, xpath)
        SwitchOnOff(fieldelement, inputElement, value)