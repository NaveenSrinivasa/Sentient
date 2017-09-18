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

def VerifyDefaultManagePage(existing_profile=False):
    """
    Verifies if Default Manage Page has the following buttons enabled/disabled:
    
    existing_profile argument should tell me if it is testing whether or not there is an actual profile.

    PASS/FAIL Conditions
        - If No existing elements are on the page then it's empty and only new should be enabled.
        - If Existing profiles are already on the page, then the top profile should be selected and all buttons should be enabled.
    """

    result = Global.PASS
    GoToManageProfile()

    newStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_new']).get_attribute('class')
    saveStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_save']).get_attribute('class')
    saveasStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_save_as']).get_attribute('class')
    deleteStatus = 'disabled' in GetElement(Global.driver, By.XPATH, xpaths['man_prof_delete']).get_attribute('class')

    printFP("INFO - Running Default Manage Page Verification with Existing Profile set to %s" %(existing_profile))

    #Checks if disabled is naturally in the buttons; the following variables are boolean types
    if existing_profile:
        printFP("INFO - Profiles should exist. Running Check on Default Manage Profile Page.")
        profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
        #Grabs the first link at the top of the list
        try:
            firstlink = GetElement(profilenameslist, By.XPATH, 'li[1]')
        except:
            testComment = "No Profiles exist currently."
            printFP('INFO - ' + testComment)
            printFP("INFO - Exiting Test.")
            return Global.FAIL, 'TEST FAIL - ' + testComment

        #Checks if the first item is active; if it is, PASS, else FAIL
        if 'item-active' in firstlink.get_attribute('class'):
            printFP("INFO - First link is active by default.")
            result = Global.PASS
        else:
            printFP("INFO - First link is not active by default.")
            result = Global.FAIL

        if (newStatus or saveStatus or saveasStatus or deleteStatus):
            printFP("INFO - One of the four buttons (New, Save, Save As or Delete) was disabled.")
            result = Global.FAIL
        else:
            printFP("INFO - All four buttons displayed were enabled.")
    else:
        listNoData = GetElement(Global.driver, By.XPATH, "//div[@ng-show='profileList.length === 0']")
        tableNoData = GetElement(Global.driver, By.XPATH, "//div[@ng-show='profileData == null']")

        if 'ng-hide' in listNoData.get_attribute('class'):
            result = Global.FAIL
            printFP("INFO - No Data Available Message in the Profile List is hidden. It should be enabled.")
        else:
            printFP("INFO - No Data Available in Profile List.")

        if 'ng-hide' in tableNoData.get_attribute('class'):
            result = Global.FAIL
            printFP("INFO - No Data Available Message in the Data Table is hidden. It should be enabled.")
        else:
            printFP("INFO - No Data Available in Profile Data Table.")

        if (not(newStatus) and saveStatus and saveasStatus and deleteStatus):
            printFP("INFO - New button was the only button available.")
        else:
            printFP("INFO - New button was not the only button available.")
            result = Global.FAIL

    return result, ('INFO - Some portions of the test failed. Please refer to log file.') if result == Global.FAIL else ''

def VerifyProfileTabs(existing_profile_name=None):
    """
    Checks if all tabs exist in either creating a new profile or in an existing profile.
    User should pass an argument to existing_profile_name if we want to check existing profile else leave none.

    PASS/FAIL CONDITIONS:
        - PASS if all tabs are there. Tabs are located through their id on the page.
        - FAIL if tabs are missing.
    """
    GoToManageProfile()
    idLocators = ["info", "cfciData", "nonCfciData", "logiData", "anomalyData"]
    result = Global.PASS
    if not(existing_profile_name):
        #Checks if new profile creation has all the neceessary tabs
        ClickButton(Global.driver, By.XPATH, xpaths['man_prof_new'])
        for i in range(len(idLocators)):
            try:
                GetElement(Global.driver, By.ID, idLocators[i])
            except:
                result = Global.FAIL
                printFP("INFO - Could not locate tab with ID %s" %idLocators[i])

    else:
        #Checks if a given profile has all the mandatory tabs
        profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
        selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', existing_profile_name)
        if not selectedstatus:
            testComment = "Could not locate profile name"
            printFP('INFO - ' + testComment)
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

def EditProfile(existing_profile_name=None, profile_json=None, save_key=None):
    """
    Edits an existing profile

    existing_profile_name is the existing profile to modify.
    profile_json is the json that will contain the new values for DNP points inside the profile.
    save_key will determine whether to use SAVE AS or SAVE button (Only takes string values of 'SAVE AS' or 'SAVE')

    PASS - If it successfully saves.
    FAIL - If it does not save.
    """
    if not existing_profile_name:
        testComment = "Test did not run because test is missing mandatory parameter(s)."
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    elif not(save_key == 'SAVE' or save_key == 'SAVE AS'):
        testComment = "Test did not run because save_key is not valid"
        printFP("INFO - " + testComment)
        return Global.FAIL, testComment

    GoToManageProfile()
    #goes to the specific profile given by existing profile name and selects it
    if SelectProfileManage(existing_profile_name):
        with open(profile_json, 'r') as infile:
            profile = json.load(infile)

        if 'Profile Name' in profile:
            inputElement = GetElement(Global.driver, By.XPATH, xpaths['mp_profile_name'])
            ClearInput(inputElement)
            SendKeys(inputElement, profile['Profile Name'])
        if 'cfciData' in profile:
            FillInProfileFields('cfciData', profile['cfciData'])
        if 'nonCfciData' in profile:
            FillInProfileFields('nonCfciData', profile['nonCfciData'])
        if 'logiData' in profile:
            FillInProfileFields('logiData', profile['logiData'])
        time.sleep(1)
        try:
            if save_key == 'SAVE':
                GetElement(Global.driver, By.XPATH, xpaths['man_prof_save']).click()
            else:
                GetElement(Global.driver, By.XPATH, xpaths['man_prof_save_as']).click()
                time.sleep(1)
                GetElement(Global.driver, By.XPATH, "//div[@class='modal-footer ng-scope']/button[text()='Create']").click()
        except:
            testComment = 'Test could not retrieve/click save button for this profile'
            printFP('INFO - ' + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

        #Gets the return message after clicking save
        message = GetText(Global.driver, By.XPATH, xpaths['mp_return_message'], visible=True)
        printFP("INFO - Return message: " + message.strip().strip("-"))

        #if it displays 'no change' error then PASS else FAIL
        if 'No change' in message or 'already exist' in message:
            return Global.FAIL, 'TEST FAIL - ' + message
        else:
            printFP("INFO - Profile saved successfully.")

        if 'Profile Name' in profile:
            if profile['Profile Name'] != existing_profile_name:
                menu = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
                try:
                    retVal = SelectFromMenu(menu, By.TAG_NAME, 'li', profile['Profile Name'])
                    if not retVal:
                        testComment = 'Could not locate new changed profile'
                        printFP("INFO - " + testComment)
                        return Global.FAIL, testComment
                except:
                    testComment = 'Could not locate new changed profile'
                    printFP("INFO - " + testComment)
                    return Global.FAIL, testComment

        return Global.PASS, ''
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
    time.sleep(1)
    for field_label in fields:
        print field_label
        value = fields[field_label]
        if 'latch' not in field_label: 
            inputelement = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']//span[contains(text(),'"+field_label+"')]/parent::span/parent::fieldset/span[2]/input")
            inputelement.clear()
            inputelement.send_keys(value)
        else:
            inputElement = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']//span[contains(text(),'"+field_label+"')]/parent::span/parent::fieldset/span[2]/div")
            SetSwitch(inputElement, value)

def CreateProfile(profile_json):
    """
    Reads in a json file that contains all the information for this profile to be created.
    Json file should contain key for profile name because that is the bare minimum to get it to save.
    FillInProfileFields will fill in the rest of the fields

    PASS - If it successfully creates the profile
    FAIL - If it does not successfully create the profile (determined if there is an error when you click create)
    """
    with open(profile_json, 'r') as infile:
        profile = json.load(infile)

    if 'Profile Name' not in profile:
        testComment = 'Test did not run because json input did not contain Profile Name.'
        printFP("INFO - " + testComment)
        return Global.FAIL, testComment

    GoToManageProfile()
    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_new'])
    time.sleep(1)

    inputElement = GetElement(Global.driver, By.XPATH, xpaths['mp_profile_name'])
    ClearInput(inputElement)
    SendKeys(inputElement, profile['Profile Name'])

    if 'cfciData' in profile:
        FillInProfileFields('cfciData', profile['cfciData'])
    if 'nonCfciData' in profile:
        FillInProfileFields('nonCfciData', profile['nonCfciData'])
    if 'logiData' in profile:
        FillInProfileFields('logiData', profile['logiData'])
    ClickButton(Global.driver, By.XPATH, xpaths['man_prof_create'])
    time.sleep(1)
    try:
        confirmButton = GetElement(Global.driver, By.XPATH, xpaths['man_prof_submit'])
        confirmButton.click()
        time.sleep(1)
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

    menu = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
    return SelectFromMenu(menu, By.TAG_NAME, 'li', profile_name)

def DeleteProfile(profile_name):
    """
    Function deletes profile from the profile list in Manage Profiles

    profileName - profile to be searched for inside the profile list and deleted.
    
    PASS - If it successfully deletes and removes it off the list of profiles.
    FAIL - if it fails to delete and remove it from the list of profiles.
    """

    GoToManageProfile()
    profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
    selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', profile_name)
    if selectedstatus:
        ClickButton(Global.driver, By.XPATH, xpaths['man_prof_delete'])
        time.sleep(1)
        confirmDelete = GetElement(Global.driver, By.XPATH, "//button[text()='Ok']")
        confirmDelete.click()
        time.sleep(1)
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

def ValidateProfileFieldValues(input_file_path):
    """
        Reads input_file_path which is the path to the DNP Point Map (must be csv file)

        Function enters the minimum-1, minimum, random value between min and max, maximum and maximum+1
        and tries to create a profile. Tries creating.

        FAIL - if a value is outside of the range and does not generate an error. If it saves with points outside of range.
        PASS - if profile saves only given with valid values between range.
    """
    with open(input_file_path, 'rt') as f:
        reader = csv.reader(f)
        dnpPoints = {r[0]: [r[1],r[2],r[3]] for r in reader}

    tabIDs = ['cfciData', 'nonCfciData', 'logiData', 'anomalyData']
    result = Global.PASS
    # Does five checks -- lower than min , min, default, max, greater than max
    for n in range(5):
        #Creates A new profile Each time
        GoToManageProfile()
        newProfileButton = GetElement(Global.driver, By.XPATH, "//button[text()=' New']")
        newProfileButton.click()
        time.sleep(1)
        #For each tab, fill it out each field with lower than min, min, default, max or greater than max
        for m in range(len(tabIDs)):
            tabElement = GetElement(Global.driver, By.ID, tabIDs[m])
            time.sleep(2)
            tabElement.click()
            time.sleep(2)

            if tabIDs[m] == 'anomalyData':
                aedEnable = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']/div[not(contains(@class,'ng-hide'))]//span[@class='knob ng-binding']")
                aedEnable.click()

            activedivElement = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']/div[not(contains(@class,'ng-hide'))]")
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

def FloatingPointInProfiles(profile_name=None):
    GoToManageProfile()

    if profile_name:
        SelectProfileManage(profile_name)
    else:
        ClickButton(Global.driver, By.XPATH, xpaths['man_prof_new'])
    time.sleep(0.5)

    tabs = ['cfciData', 'nonCfciData', 'logiData', 'anomalyData']
    for x in range(len(tabs)):
        ClickButton(Global.driver, By.ID, tabs[x])

        time.sleep(0.5)
        divElement = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']/div[not(contains(@class,'ng-hide'))]")
        inputElements = GetElements(divElement, By.TAG_NAME, 'input')
        for i in range(len(inputElements)):
            defaultValue = inputElements[i].get_attribute("value")
            try:
                ClearInput(inputElements[i])
                inputElements[i].send_keys('99.99')
            except:
                print "INFO - Field is not Interactable. Skipping Field."
                continue

            if profile_name:
                button = GetElement(Global.driver, By.XPATH, xpaths['man_prof_save'])
            else:
                button = GetElement(Global.driver, By.XPATH, '//button[contains(text(),"Create")]')
            button.click()
            time.sleep(0.5)
            try:
                GetElement(Global.driver, By.XPATH, '//span[contains(text(),"Please change the float to integer on the form.")]')
            except:
                testComment = 'Test was did not find error message after creating the profile.'
                printFP("INFO - " +  testComment)
                return Global.FAIL, testComment              

            if 'field-error' not in inputElements[i].get_attribute('class'):
                testComment = 'A field generates error message, but does not get highlighted red when creating with bad value.'
                printFP("INFO - " + testComment)
                return Global.FAIL, testComment
            inputElements[i].clear()
            inputElements[i].send_keys(defaultValue)
    
    return Global.PASS, ''

def VerifyAEDEnableOn(inputElements, enabled=None):
    """ 
    Checks if AED is on and if the fields can be edittable

    """
    if enabled:
        for i in range(len(inputElements)):
            try:
                ClearInput(inputElements[i])
                printFP("INFO - Field is edittable.")
            except:
                return False
    else:
        for i in range(len(inputElements)):
            try:
                ClearInput(inputElements[i])
                return False
            except:
                printFP("INFO - Field is not edittable")
                pass
    return True

def VerifyAEDEnableLatch(profile_name=None):
    """
    Verify a profile (whether is exist or new) has AED tab and has the AED enable latch. Enable latch should control the editability of fields.

    PASS - AED latch controls the editablility of fields.
    FAIL - AED latch does not control the editability of fields.

    """
    GoToManageProfile()

    if profile_name:
        profilenameslist = GetElement(Global.driver, By.CLASS_NAME, 'listview-ol')
        selectedstatus = SelectFromMenu(profilenameslist, By.TAG_NAME, 'li', profile_name)
    else:
        GetElement(Global.driver, By.XPATH, xpaths['man_prof_new']).click()

    time.sleep(0.5)
    try:
        GetElement(Global.driver, By.ID, 'anomalyData').click()
    except:
        testComment = 'AED Enable Latch does not exist'
        printFP("INFO - " + testComment)
        return Global.FAIL, testComment

    toggleButton = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']//span[text()='AED enable latch']/parent::span/parent::fieldset/span[2]/div/div")
    if not(profile_name):
        if 'switch-off' in toggleButton.get_attribute('class'):
            printFP("INFO - AED Enable Latch is disabled by default.")
        else:
            testComment = 'AED Enable Latch is enabled by default for New Profile.'
            printFP("INFO - " + testComment)
            return Global.FAIL, testComment

    aedpage = GetElement(Global.driver, By.XPATH, "//div[@class='tab-pane ng-scope active']/div[@class='anomaly tabs ng-scope']")
    inputElements = GetElements(aedpage, By.TAG_NAME, 'input')

    if 'switch-off' in toggleButton.get_attribute('class'):

        if not(VerifyAEDEnableOn(inputElements, False)):
            testComment = 'Test could interact with Fields while AED is off.'
            printFP('INFO - ' + testComment)
            return Global.FAIL, testComment

        printFP("INFO - All fields inside AED are not interactable while AED button is set to off. Now Turning AED on.")

        toggleKnob = GetElement(toggleButton, By.XPATH, 'span[2]')
        toggleKnob.click()

        if not(VerifyAEDEnableOn(inputElements, True)):
            testComment = 'Test could not interact with Fields while AED is on.'
            printFP('INFO - ' + testComment)
            return Global.FAIL, testComment

    elif 'switch-on' in toggleButton.get_attribute('class'):
        if not(VerifyAEDEnableOn(inputElements, True)):
            testComment = 'Test could not interact with Fields while AED is on.'
            printFP('INFO - ' + testComment)
            return Global.FAIL, testComment

        printFP("INFO - All fields inside AED are interactable while AED button is set to ON. Now Turning AED OFF.")

        toggleKnob = GetElement(toggleButton, By.XPATH, 'span[2]')
        toggleKnob.click()

        if not(VerifyAEDEnableOn(inputElements, False)):
            testComment = 'Test could interact with Fields while AED is off.'
            printFP('INFO - ' + testComment)
            return Global.FAIL, testComment

    return Global.PASS, ''





