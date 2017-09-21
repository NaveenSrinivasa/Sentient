import Global
import logging
import os
import smtplib
import sys
import time
import json
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from Global import xpaths
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as soup
from Utilities_Framework import *


def WaitForXTime(min = 5):
    i = 0
    while i < min:
        time.sleep(120)
        Global.driver.refresh()
        i += 1

    return Global.PASS, ''

# Get/Select Elements on Ample
#  This section contains helper functions to get elements from Ample as well
#  as functions to select things.
def SkipCommentLine(fp):
    line = fp.readline().strip('\n')
    while re.match("^#", line):
        # skip the comment line
        line = fp.readline().strip('\n')
    return line

def WaitForTitle(title):
    printFP(Global.driver.current_url)

    """Wait until the webpage title has the given string"""
    try:
        time.sleep(10)
        assert title in Global.driver.current_url
        return True
    except:
        return False

def GetElement(driver, method, locator):
    """Get an element. Searches down the DOM from driver
    driver - either the webdriver or a webelement
    method - By.(XPATH, TAG_NAME, ID, CLASS_NAME, etc)
    locator - a string identifier to find the element using the method."""

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((method, locator)))
    return element

def CheckIfStaleElement(element):
    """Checks if the element has become stale -- typically stale
    means it can't be accessed/disappered/changed"""
    try:
        result = WebDriverWait(Global.driver, 10).until( EC.staleness_of(element))
    except:
        result = False
    return result

def GetElements(driver, method, locator):
    """Get all elements with the given method and locator"""

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_any_elements_located((method, locator)))
    except:
        pass

    elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((method, locator)))
    return elements

def GetButton(driver, method, locator):
    """This get method waits for the element to be clickable before returning."""

    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((method, locator)))
    return element

def GetText(driver, method, locator, visible=False):
    """Gets the text from the element.
    Returns: string"""

    if visible:
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((method, locator)))
    else:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((method, locator)))
    return element.text

def GetFirstText(driver):
    """This function returns the first string on the webdriver or submodule."""

    textElement = GetElement(driver, By.TAG_NAME, 'span')
    return textElement.text

def ClickButton(driver, method, locator):
    """Wrapper function to get the button element and click it."""
    button = GetElement(driver, method, locator)
    try:
        time.sleep(1)
        button.click()
        time.sleep(2)
        return True
    except:
        try:
            ActionChains(driver).move_to_element(button).click().perform()
        except:
            printFP('Failed to click button')
            return False

def JustClick(element):
    """Wrapper function to click it."""
    try:
        ActionChains(Global.driver).move_to_element(element).click().perform()
        return True
    except:
        printFP('Failed to click button')
        return False

def ClearInput(element):
    try:
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
    except:
        printFP("INFO - Test could not clear input.")

def SelectFromMenu(driver, method, locator, target):
    """Given a menu object, it reads the text of all the options in the menu
    and clicks the option with text matching 'target'"""

    options = GetElements(driver, method, locator)
    for option in options:
        if option.text == target:
            actions = ActionChains(Global.driver)
            actions.move_to_element(option).click(option).perform()
            time.sleep(1)
            printFP('Selected: %s' % target)
            return True
    return False

def SetSwitch(inputElement, value):
    """Set the switch to value.
    value = 0: switch off
    value = 1: switch on"""

    switchStatusElement = GetElement(inputElement, By.CLASS_NAME, 'toggle-switch-animate')
    if value == 0:
        if 'switch-on' in switchStatusElement.get_attribute('class'):
            printFP('Turned switch off')
            inputElement.click()
    else:
        if 'switch-off' in switchStatusElement.get_attribute('class'):
            printFP('Turned switch on')
            inputElement.click()

def SwitchOnOff(elementlocator, switchlocator, value):
    """Set the switch to value.
    value = false: switch off
    value = true: switch on"""

    if value in ['false','False']:
        if 'switch-on' in switchlocator.get_attribute('class'):
            printFP('Turned switch off')
            actions = ActionChains(Global.driver)
            actions.move_to_element(elementlocator).click(switchlocator).perform()

    elif value in ['true','True']:
        if 'switch-off' in switchlocator.get_attribute('class'):
            printFP('Turned switch on')
            actions = ActionChains(Global.driver)
            actions.move_to_element(elementlocator).click(switchlocator).perform()
    else:
        logCSVFP.write('N/A toggle-switch input value, ')

def SetCheckbox(inputElement, value):
    """This function sets the checkbox to selected or unselected."""

    if value == 0:
        if inputElement.is_selected():
            printFP('Unchecked')
            inputElement.click()
    else:
        if not inputElement.is_selected():
            printFP('Checked')
            inputElement.click()

def SetCheckBox(inputElement, value):
    """This function sets the checkbox to value."""
    value= value.replace("\r","")
    if value in ['false','False']:
        if inputElement.is_selected():
            print('Unchecking')
            time.sleep(1)
            inputElement.click()
            print('Unchecked')
    elif value in ['true','True']:
        if not inputElement.is_selected():
            print('Checking')
            time.sleep(1)
            inputElement.click()
            print('Checked')
    else:
        printFP('N/A check box input value, ')

def SetRadioButton(inputElement):
    if inputElement.is_selected():
        printFP('selected')
    elif not inputElement.is_selected():
        inputElement.click()
    else:
        printFP('N/A Radio Button input value, ')

def SendKeys(inputElement, text):
    try:
        inputElement.send_keys(text)
        printFP('Entered: %s' % text)
        return True
    except:
        printFP('Failed to send %s to inputElement' % text)
        return False

def SelectFromDropdown(driver, dropdownxpath, dropdownOption):
    """This function selects the given item from the dropdown menu 'select' element.
        Does nothing if the item is not present in the dropdown menu.
        Currently not working properly (sometimes) for Firefox on Windows sytsems.

    Args:
      webdriver (WebDriver): webdriver object that represents the browser to be tested.
      element (WebElement): WebElement object that is the <select> menu element.
      name (str): the item from the dropdown menu to be selected.

    Return:
      None"""

    xPath = dropdownxpath + "/li[" + dropdownOption + "]/a"
    element = GetElement(driver, By.XPATH, xPath)
    try:
        element.click()
    except:
        pass

def FindRowInTable(tableBodyElement, nameToSearchFor):
    """Finds a row containing string nameToSearchFor and returns the row.
    tableBodyElement should have the DOM tag name tbody."""

    rows = GetElements(tableBodyElement, By.TAG_NAME, 'tr')
    for row in rows:
        fields = GetElements(row, By.TAG_NAME, 'span')
        for field in fields:
            if field.text == nameToSearchFor:
                printFP('Found %s' % field.text)
                return row
    return None

# Site Navigation
def GoToDashboard():
    try:
        ClickButton(Global.driver, By.XPATH, xpaths['dashboard'])
    except:
        return False
    return True

def GoToDevMan():
    try:
        time.sleep(1)
        GetElement(Global.driver, By.XPATH, xpaths['dev_man']).click()
        time.sleep(3)
    except:
        Global.driver.refresh()
        time.sleep(10)
        try:
            time.sleep(1)
            GetElement(Global.driver, By.XPATH, xpaths['dev_man']).click()
            time.sleep(3)
        except:
            print "failed to go to Dev Man"
            return False
    time.sleep(1)
    return True

def GoToDevConfig():
    try:
        ClickButton(Global.driver, By.XPATH, xpaths['dev_man_config'])
    except:
        return False
    return True

def GoToDevUpgrade():
    try:
        ClickButton(Global.driver, By.XPATH, xpaths['dev_man_upgrade'])
    except:
        return False
    return True

def GoToLineMon():
    try:
        GetElement(Global.driver, By.XPATH, xpaths['line_mon']).click()
    except:
        Global.driver.refresh()
        time.sleep(10)
        try:
            GetElement(Global.driver, By.XPATH, xpaths['line_mon']).click()
        except:
            printFP("Could not click on Line Monitoring")
            return False
    return True

def GoToLineMonFaultEvents():
    try:
        ClickButton(Global.driver, By.XPATH, xpaths['line_mon_fault_events'])
    except:
        return False
    return True

def GoToLineMonDisturbances():
    try:
        ClickButton(Global.driver, By.XPATH, "//a[text()='Line Monitoring']")
        time.sleep(1)
        ClickButton(Global.driver, By.XPATH, "//a[text()='Disturbances']")
        time.sleep(1)
        return True
    except:
        return False

def GoToLineMonWaveforms():
    try:
        ClickButton(Global.driver, By.XPATH, xpaths['line_mon_waveforms'])
    except:
        return False
    return True

def GoToLineMonLogI():
    try:
        ClickButton(Global.driver, By.XPATH, xpaths['line_mon_logi'])
    except:
        return False
    return True

def GoToLineMonDNP3():
    try:
        ClickButton(Global.driver, By.XPATH, xpaths['line_mon_dnp3'])
    except:
        return False
    return True

def GoToCurrentJobsConfig():
    i = 0
    while i < 5:
        try:
            Global.driver.refresh()
            currentJobs = GetElement(Global.driver, By.XPATH, xpaths['current_jobs_menu'])
            currentJobs.click()
            time.sleep(1)
            currentJobConfig = GetElement(Global.driver, By.XPATH, xpaths['current_jobs_config'])
            currentJobConfig.click()
            time.sleep(1)
            break
        except:
            Global.driver.refresh()
            i += 1
            printFP("INFO - Function could not reach current jobs config page. Retry #%s"%i)
            time.sleep(1)

def GoToCurrentJobsUpgrade():
    ClickButton(Global.driver, By.XPATH, xpaths['current_jobs_menu'])
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['current_jobs_upgrade'])
    return True

def GoToManageProfile():
    i = 0
    while i < 5:
        try:
            Global.driver.refresh()
            time.sleep(5)
            gear = GetElement(Global.driver, By.CLASS_NAME, 'ion-ios-gear')
            gear.click()
            time.sleep(1)
            link = GetElement(Global.driver, By.XPATH, "//a[text()='Manage Profiles']")
            link.click()
            time.sleep(1)
            printFP("INFO - Test Reached Manage Profile page")
            return True
        except:
            Global.driver.refresh()
            time.sleep(5)
            i += 1
            if i < 5:
                printFP("INFO - Function could not reach current jobs config page. Retry #%s"%i)
                time.sleep(1)
            else:
                printFP("INFO - Test could not reach Manage Profile")
                return False

def GoToSysAdmin():
    try:
        GetElement(Global.driver, By.CLASS_NAME, 'ion-ios-gear').click()
        time.sleep(2)
        GetElement(Global.driver, By.LINK_TEXT, 'System Admin').click()
        time.sleep(2)
    except:
        Global.driver.refresh()
        time.sleep(10)
        try:
            GetElement(Global.driver, By.CLASS_NAME, 'ion-ios-gear').click()
            time.sleep(2)
            GetElement(Global.driver, By.LINK_TEXT, 'System Admin').click()
            time.sleep(2)
        except:
            return False
    try:
        GetElement(Global.driver, By.XPATH, "//div[contains(text(),'Import Firmware File')]")
        printFP("INFO - Reached System Admin Page")
    except:
        printFP("INFO - May not have reached System Admin Page")
        time.sleep(1)
    return True

def GoToConfigProp():
    Global.driver.refresh()
    time.sleep(2)
    GetElement(Global.driver, By.CLASS_NAME, 'ion-ios-gear').click()
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['settings_config_prop'])

def GoToEmailAlert():
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['dash_person_dropdown'])
    time.sleep(1)
    ClickButton(Global.driver, By.XPATH, xpaths['dash_person_email_alert'])

def GoToUpdateProfile():
    try:
        ClickButton(Global.driver, By.CLASS_NAME, 'ion-ios-person')
        time.sleep(1)
        ClickButton(Global.driver, By.LINK_TEXT, 'Update Profile')
        time.sleep(3)
    except:
        Global.driver.refresh()
        time.sleep(10)
        try:
            ClickButton(Global.driver, By.CLASS_NAME, 'ion-ios-person')
            time.sleep(1)
            ClickButton(Global.driver, By.LINK_TEXT, 'Update Profile')
            time.sleep(3)
        except:
            return False

def GoToUserMan():
    Global.driver.refresh()
    time.sleep(10)
    GetElement(Global.driver, By.CLASS_NAME, 'ion-ios-gear').click()
    GetElement(Global.driver, By.LINK_TEXT, 'User Management').click()

def UploadMTF(fileName):
    fileUpload = GetElement(Global.driver, By.ID, 'mFile')
    time.sleep(5)
    fileUpload.send_keys(fileName)
    time.sleep(2)

# Group Tree
def GetRootNode():
    """Finds the root node in the group tree and opens it.
    Return the root node."""

    try:
        node = WebDriverWait(Global.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ROOTNODE-name')))
        time.sleep(2)
        node.click()
    except:
        return None
    return node

def GetRegion(regionName):
    """Find the region node by name and click it.
    Return the region element."""

    allRegions = Global.driver.find_elements_by_class_name('REGION-name')
    for region in allRegions:
        if regionName == region.text:
            printFP('Found %s' % region.text)
            actions = ActionChains(Global.driver)
            actions.move_to_element(region).click(region).perform()
            time.sleep(2)
            region = GetElement(region, By.XPATH, '../..')
            time.sleep(1)
            return region
    printFP('Region %s not found' % regionName)
    return None

def GetSubstation(substationName):
    """Find the substation node by name and click it.
    Return the substation element."""

    allSubs = Global.driver.find_elements_by_class_name('SUBSTATION-name')
    for sub in allSubs:
        if substationName == sub.text:
            printFP('Found %s' % sub.text)
            actions = ActionChains(Global.driver)
            actions.move_to_element(sub).click(sub).perform()
            sub = GetElement(sub, By.XPATH, '../..')
            time.sleep(1)
            return sub
    printFP('Substation %s not found' % substationName)
    return None

def GetFeeder(feederName):
    """Find the feeder node by name and click it.
    Return the feeder element."""
    allFeeders = Global.driver.find_elements_by_class_name('FEEDER-name')
    for feeder in allFeeders:
        if feederName == feeder.text:
            printFP('Found %s' % feeder.text)
            ActionChains(Global.driver).move_to_element(feeder).click().perform()
            feeder = GetElement(feeder, By.XPATH, '../..')
            time.sleep(1)
            return feeder
    printFP('Feeder %s not found' % feederName)
    return None

def GetSite(siteName):
    """Find the site node by name and click it.
    Return the site element."""
    allSites = Global.driver.find_elements_by_class_name('SITE-name')
    for site in allSites:
        if siteName == site.text:
            printFP('Found %s' % site.text)
            ActionChains(Global.driver).move_to_element(site).click().perform()
            site = GetElement(site, By.XPATH, '../..')
            time.sleep(1)
            return site
    printFP('Site %s not found' % siteName)
    return None


def GetLocationFromInput(regionName, subName, feederName, siteName):
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()
        time.sleep(5)

    for i in range(3):
        region = GetRegion(regionName)
        if not region:
            Global.driver.refresh()
        else:
            break
    if not subName and region:
        return True
    time.sleep(2)

    if not region == None:
        for i in range(3):
            sub = GetSubstation(subName)
            if not sub:
                Global.driver.refresh()
            else:
                break
    else:
        return False
    if not feederName and sub :
        return True
    time.sleep(2)

    if not sub == None:
        for i in range(3):
            feeder = GetFeeder(feederName)
            if not feeder:
                Global.driver.refresh()
            else:
                break
    else:
        return False
    if not siteName and feeder:
        return True
    time.sleep(2)

    if not feeder == None:
        for i in range(3):
            site = GetSite(siteName)
            if not site:
                Global.driver.refresh()
            else:
                break
        if site == None:
            return False
        else:
            return True
    else:
        return False


def GetSiteFromTop(regionName, subName, feederName, siteName):
    """Navigate down the tree until you reach the site node by name and click it."""

    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    time.sleep(1)
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()
        time.sleep(5)

    for i in range(3):
        region = GetRegion(regionName)
        if not region:
            Global.driver.refresh()
        else:
            break
    time.sleep(2)

    if not region == None:
        for i in range(3):
            sub = GetSubstation(subName)
            if not sub:
                Global.driver.refresh()
            else:
                break
    else:
        return False
    time.sleep(2)
    if not sub == None:
        for i in range(3):
            feeder = GetFeeder(feederName)
            if not feeder:
                Global.driver.refresh()
            else:
                break
    else:
        return False
    time.sleep(2)
    if not feeder == None:
        for i in range(3):
            site = GetSite(siteName)
            if not site:
                Global.driver.refresh()
            else:
                break
        if site == None:
            return False
        else:
            return True
    else:
        return False

def GetFeederFromTop(regionName, subName, feederName):
    """Navigate down the tree until you reach the site node by name and click it."""
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    time.sleep(1)
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()
        time.sleep(2)

    region = GetRegion(regionName)
    time.sleep(2)
    if not region == None:
        sub = GetSubstation(subName)
    else:
        return False
    time.sleep(1)
    if not sub == None:
        feeder = GetFeeder(feederName)
        return True
    else:
        return False

def GetSubstationFromTop(regionName, subName):
    """Navigate down the tree until you reach the site node by name and click it."""
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    time.sleep(1)
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()
        time.sleep(2)

    region = GetRegion(regionName)
    time.sleep(2)
    if not region == None:
        sub = GetSubstation(subName)
        return True
    else:
        return False

def GetRegionFromTop(regionName):
    """Navigate down the tree until you reach the site node by name and click it."""
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    time.sleep(1)
    if rootElement.get_attribute('collapsed') == 'true':
        GetRootNode()
        time.sleep(2)

    region = GetRegion(regionName)
    time.sleep(2)
    if not region == None:
        return True
    else:
        return False


def GetDevice(serial):
    """Finds the device in the current table in device management and returns
    the web element for the row containing serial.
    Note that this will fail if the device is not showing on the current table.
    This can happen if the driver has not selected the node yet."""

    devTable = GetElement(Global.driver, By.TAG_NAME, 'table')
    time.sleep(1)
    devtbody = GetElement(devTable, By.TAG_NAME, 'tbody')
    time.sleep(1)
    deviceslist = GetElements(devtbody, By.TAG_NAME, 'tr')
    for device in deviceslist:
        devicedetails = GetElements(device, By.TAG_NAME, 'span')
        time.sleep(1)
        for finddevice in devicedetails:
            tmpdevicename = finddevice.text
            if serial == tmpdevicename:
                return device
    return None

def IsOnline(serial, interval = 120, timeout = 1200):
    """Polls the device and waits for the device to come online.
    Returns True if device comes online within timeout range.
    Returns False if device does not come online within timeout range.

    serial - string representing the serial of the device to poll
    interval - how long to wait between each poll for online status
    timeout - how long to wait for device to come online"""

    elapsed = 0
    printFP('Waiting for device to come online . . .')
    while elapsed < timeout:
        print elapsed
        time.sleep(interval)
        elapsed += interval
        Global.driver.refresh()
        time.sleep(10)
        device = GetDevice(serial)
        icon = GetElement(device, By.XPATH, 'td[4]/span').get_attribute('class')
        if 'ion-checkmark-circled' in icon:
            printFP('Device %s is online' % serial)
            return True
        else:
            printFP('Device %s is not online yet' % serial)
    printFP('Device %s failed to come online within timeout range' % serial)
    return False

def RightClickElement(element):
    """Right clicks the given element."""

    actions = ActionChains(Global.driver)
    actions.move_to_element_with_offset(element, 1, 5).perform()
    time.sleep(2)
    actions.context_click().perform()

def RefreshMenuTree(menuID):
    menu = 'node%s' % menuID[4:]
    xpath = '//*[@id="'+menu+'"]/div[2]/span[1]/a'
    try:
        menutreerefresh = WebDriverWait(Global.driver, 15).until(EC.presence_of_element_located((By.XPATH, xpath)))
        time.sleep(2)
        menutreerefresh.click()
        time.sleep(10)
        menutreerefresh.click()
        time.sleep (3)
        print True
        return True

    except:
        print False
        return False

def CreateRegion(regionName, node):
    """Right clicks the root node and creates a new region.
    Returns the region.
    regionName - string representing the region name
    node - root node (ie. Sentient)"""

    menuID = GetContextMenuID(node)

    RightClickElement(node)
    time.sleep(1)
    SelectFromMenu(node, By.CLASS_NAME, 'pull-left', 'Add Region')
    time.sleep(1)

    # Fill in fields
    inputElement = GetElement(Global.driver, By.NAME, 'newNodeName')
    SendKeys(inputElement, regionName)
    time.sleep(1)
    try:
        errors = GetElements(Global.driver, By.XPATH, "//p[@class='ample-error-message ng-binding']")
        for error in errors:
            if not 'ng-hide' in error.get_attribute('class'):
                GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
                printFP("Error Message: %s" % error.text)
                return None
    except:
        pass

    # Submit
    ClickButton(Global.driver, By.XPATH, xpaths['tree_add_node_submit'])
    time.sleep(1)
    try:
        errorBox = GetElement(Global.driver, By.CLASS_NAME, 'alert-danger')
        errorText = GetElement(errorBox, By.XPATH, 'div/span').text
        printFP("Error Message: %s" %errorText)
        GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        return None
    except:
        pass

    time.sleep(1)

    if RefreshMenuTree(menuID):
        # Get new node
        if not GetLocationFromInput(regionName,None,None,None):
            testComment = "Unable to locate site based on input file"
            printFP(testComment)
            return False
        else:
            return True
    else:
        testComment = 'Timed out while trying to refresh the node'
        print testComment
        return False


def CreateSubstation(substationName, region):
    """Right clicks the given region and creates a substation node.
    Returns the substation.
    substationName - string represeting the substation name
    region - web element of the region to create the substation from"""

    menuID = GetContextMenuID(region)

    RightClickElement(region)
    time.sleep(1)
    SelectFromMenu(region, By.CLASS_NAME, 'pull-left', 'Add Substation')
    time.sleep(1)

    # Fill in fields
    inputElement = GetElement(Global.driver, By.NAME, 'newNodeName')
    SendKeys(inputElement, substationName)
    time.sleep(1)
    try:
        errors = GetElements(Global.driver, By.XPATH, "//p[@class='ample-error-message ng-binding']")
        for error in errors:
            if not 'ng-hide' in error.get_attribute('class'):
                GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
                printFP("Error Message: %s" % error.text)
                return None
    except:
        pass

    # Submit
    ClickButton(Global.driver, By.XPATH, xpaths['tree_add_node_submit'])
    time.sleep(1)
    try:
        errorBox = GetElement(Global.driver, By.CLASS_NAME, 'alert-danger')
        errorText = GetElement(errorBox, By.XPATH, 'div/span').text
        printFP("Error Message: %s" %errorText)
        GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        return None
    except:
        pass

    time.sleep(1)

    if RefreshMenuTree(menuID):
        # Get new node
        substation = GetSubstation(substationName)
        return substation
    else:
        testComment = 'Timed out while trying to refresh the node'
        print testComment
        return None

def CreateFeeder(feederName, substation):
    """Right clicks the given substation and creates a feeeder node.
    Returns the feeder.
    feederName - string representing the feeder name
    substation - web element of the substation to create the feeder from"""

    menuID = GetContextMenuID(substation)
    RightClickElement(substation)
    time.sleep(1)
    SelectFromMenu(substation, By.CLASS_NAME, 'pull-left', 'Add Feeder')
    time.sleep(1)

    # Fill in fields
    inputElement = GetElement(Global.driver, By.NAME, 'newNodeName')
    SendKeys(inputElement, feederName)
    time.sleep(1)
    try:
        errors = GetElements(Global.driver, By.XPATH, "//p[@class='ample-error-message ng-binding']")
        print len(errors)
        for error in errors:
            if not 'ng-hide' in error.get_attribute('class'):
                GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
                printFP("Error Message: %s" % error.text)
                return None
    except:
        pass

    # Submit
    ClickButton(Global.driver, By.XPATH, xpaths['tree_add_node_submit'])
    time.sleep(1)
    try:
        errorBox = GetElement(Global.driver, By.CLASS_NAME, 'alert-danger')
        errorText = GetElement(errorBox, By.XPATH, 'div/span').text
        printFP("Error Message: %s" %errorText)
        GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        return None
    except:
        pass
    time.sleep(1)

    if RefreshMenuTree(menuID):
        # Get new node
        feeder = GetFeeder(feederName)
        return feeder
    else:
        testComment = 'Timed out while trying to refresh the node'
        print testComment
        return None


def CreateSite(siteName, feeder, latitude, longitude):
    """Right clicks the given feeder and creates a site node.
    Returns the site.
    siteName - string representing the site name
    feeder - web element of the feeder to create the site from
    latitude - string representing the latitude of the site
    longitude - string representing the longitude of the site"""

    menuID = GetContextMenuID(feeder)
    RightClickElement(feeder)
    time.sleep(1)
    SelectFromMenu(feeder, By.CLASS_NAME, 'pull-left', 'Add Site')
    time.sleep(1)

    # Fill in fields
    inputElement = GetElement(Global.driver, By.NAME, 'newNodeName')
    SendKeys(inputElement, siteName)
    time.sleep(1)

    try:
        errors = GetElements(Global.driver, By.XPATH, "//p[@class='ample-error-message ng-binding']")
        print len(errors)
        for error in errors:
            if not 'ng-hide' in error.get_attribute('class'):
                GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
                printFP("Error Message: %s" % error.text)
                return None
    except:
        pass

    if latitude and longitude:
        gpselement = GetElement(Global.driver, By.XPATH, "//label[contains(text(),'Override GPS')]")
        gpsswitch = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-model,'overrideGps')]/div")
        SwitchOnOff(gpselement, gpsswitch, 'true')
        time.sleep(1)
        inputElement = GetElement(Global.driver, By.XPATH, "//input[@placeholder='Latitude']")
        SendKeys(inputElement, latitude)
        inputElement = GetElement(Global.driver, By.XPATH, "//input[@placeholder='Longitude']")
        SendKeys(inputElement, longitude)

    # Submit
    ClickButton(Global.driver, By.XPATH, xpaths['tree_add_node_submit'])
    time.sleep(1)
    try:
        errorBox = GetElement(Global.driver, By.CLASS_NAME, 'alert-danger')
        errorText = GetElement(errorBox, By.XPATH, 'div/span').text
        printFP("Error Message: %s" %errorText)
        GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        return None
    except:
        pass

    if RefreshMenuTree(menuID):
        # Get new node
        site = GetSite(siteName)
        return site
    else:
        testComment = 'Timed out while trying to refresh the node'
        print testComment
        return None

def SelectDevice(serial):
    """Assumes page is showing the device. If it is, it will look at the list
    of devices on device management and select the checkbox on the left side
    of the row."""

    try:
        device = GetDevice(serial)
        checkbox = GetElement(device, By.TAG_NAME, 'input')
        time.sleep(1)
        SetCheckBox(checkbox, 'true')
        return device
    except:
        return None


def GetContextMenuID(element): # deprecated
    """Returns the HTML id of a context menu element."""

    elementID = element.get_attribute('id')
    if not elementID:
        elementID = GetElement(element, By.XPATH, '../..').get_attribute('id')
    menuID = 'menu%s' % elementID[4:]
    printFP(menuID)
    return menuID

def OpenContextMenu(identifier): # deprecated
    """This function opens the right-click menu of a node, given the HTML id of
        that node's menu. It should be in the format 'menu-...'. It creates the
        menu with its top left corner at the center of the node, so care must
        be taken to make sure that the entire menu is still visible, otherwise
        errors may occur.

    Args:
      webdriver (WebDriver): webdriver object that represents the browser to be tested.
      identifier (string): HTML id of the menu to be opened. should be in format 'menu-...'"""

    cmd = ("document.getElementById(\'%s\').className += \' open\';" % identifier)
    Global.driver.execute_script(cmd)
    printFP('OpenContextMenu')

def CloseContextMenu(identifier): # deprecated
    """Closes the right-click meny of a node."""

    cmd = ('document.getElementById(' + '\'' + identifier + '\''
           + ').className = document.getElementById('
           + '\'' + identifier + '\''
           + ').className.replace( /(?:^|\s)open(?!\S)/g , \'\' )')
    Global.driver.execute_script(cmd)

def CreateDeviceFromMTF(mtfPath):
    """Opens a Master Tracker File and generates a device dictionary
    representing that device."""

    mtf = open(mtfPath, 'r')
    mtf.readline()
    info = mtf.readline().strip('\n').split(',')
    return CreateDeviceDictionary(info)

def FindDeviceInCurrentJobs(listXPATH, serial):
    """Iterates down the list of jobs in current jobs until it finds a job
    for the given serial"""

    printFP('Looking for %s in current jobs' % serial)
    time.sleep(10)
    jobList = GetElement(Global.driver, By.XPATH, listXPATH)
    allJobs = GetElements(jobList, By.TAG_NAME, 'li')
    printFP('All jobs: %d' % len(allJobs))
    # Iterate through the list of devices while checking for the right device serial
    for job in allJobs:
        printFP('INFO - Looking through a job')
        job.click()
        time.sleep(0.5)
        # Check the serial number
        try:
            Element = GetElement(Global.driver, By.XPATH, "//span[text()="+serial+"]")
        except:
            return False
        printFP('Current serial: %s' % currentSerial)
        if currentSerial in serial:
            printFP('Found %s' % serial)
            return True
    return False

def SelectProfileConfig(profileName):
    menu = GetElement(Global.driver, By.XPATH, xpaths['dev_config_profile_menu'])
    SelectFromMenu(menu, By.TAG_NAME, 'li', profileName)

def PollCurrentJobsConfig(device, timeout):
    """Checks current jobs config to see if a config job completes
    It will click 'retry all' if the job fails"""

    i = 0
    retry = 0
    while i < timeout:
        printFP('Waiting for config to complete . . .')
        printFP(Global.driver.title)
        time.sleep(60)
        # Refresh page
        Global.driver.refresh()
        time.sleep(10)
        # Find device from list
        FindDeviceInCurrentJobs(xpaths['current_config_job_list'], device['serial'])
        # Get otap status
        jobStatus = GetText(Global.driver, By.XPATH, xpaths['current_first_job_status'], visible=True)
        printFP('Job Status: %s' % jobStatus)
        if jobStatus == 'SUCCESS':
            printFP('Config complete! # of retries: %d' % retry)
            return True
        elif jobStatus == 'INPROGRESS':
            i += 60
        elif jobStatus == 'FAILURE':
            printFP('Config failed. Retrying.')
            ClickButton(Global.driver, By.XPATH, xpaths['current_jobs_config_retry_all'])
            i = 0
            retry += 1
    return False

def CheckAppliedParameters(device, expectedParameters=[]):
    """Reads the parameters table in current jobs config to check which points were applied.
    Returns success if all parameters were applied successfully."""

    FindDeviceInCurrentJobs(xpaths['current_config_job_list'], device['serial'])
    parametersTable = GetElement(Global.driver, By.XPATH, xpaths['current_config_params_list'])
    rows = GetElements(parametersTable, By.TAG_NAME, 'tr')
    if len(rows) == 0:
        testComment = 'No parameters applied'
        printFP(testComment)
        return Global.FAIL, testComment
    # there were parameters applied
    # check for success
    fails = []
    passes = []
    for row in rows:
        # Get the name of the parameter in the row
        paramName = GetText(row, By.CLASS_NAME, 'truncate')
        # Get the status
        statusElement = GetElement(row, By.CLASS_NAME, 'icons')
        status = str(statusElement.get_attribute('tooltip'))
        printFP('Parameter: %s  Status: %s' % (paramName, status))
        if status == 'Success':
            passes.append(paramName)
        elif status == 'Failure':
            fails.append(paramName)
    if len(fails) > 0:
        testComment = 'Failed to apply parameters: '
        for param in fails:
            testComment = testComment + param + ' '
        printFP(testComment)
        return Global.FAIL, testComment
    else:
        if len(expectedParameters) > 0:
            for expect in expectedParameters:
                if expect in passes:
                    continue
                else:
                    testComment = 'Did not get %s in parameters' % expect
                    printFP(testComment)
                    return Global.FAIL, testComment
        testComment = 'Applied all parameters successfully: '
        for param in passes:
            testComment = testComment + param + ' '
        printFP(testComment)
        return Global.PASS, testComment

def ApplyProfile(device, profileName, timeout=600):
    """Applies a profile to device. It will wait until the config is
    successful. If the config fails, it will retry up to 3 times."""

    # Navigate to device configuration
    GoToDevMan()
    time.sleep(0.5)
    GoToDevConfig()

    # Get the device and apply the profile
    time.sleep(1)
    Global.driver.refresh()
    time.sleep(10)
    GetSiteFromTop(device['region'], device['substation'], device['feeder'], device['site'])
    SelectDevice(device['serial'])
    time.sleep(0.5)
    ClickButton(Global.driver, By.XPATH, xpaths['dev_man_configure'])
    time.sleep(0.5)
    ClickButton(Global.driver, By.XPATH, xpaths['dev_config_profile_menu_button'])
    SelectProfileConfig(profileName)
    time.sleep(0.5)
    ClickButton(Global.driver, By.XPATH, xpaths['dev_config_profile_apply'])

    # Read return message
    returnMessage = GetText(Global.driver, By.XPATH, xpaths['dev_config_profile_msg'])
    if 'Successfully configured profile to the selected device(s).' in returnMessage:
        printFP('Got: %s' % returnMessage)

    # Close profile
    time.sleep(0.5)
    ClickButton(Global.driver, By.XPATH, xpaths['dev_config_profile_close'])

    # Go check current jobs
    time.sleep(1)
    GoToCurrentJobsConfig()
    time.sleep(1)

    # Monitor for success
    configComplete = PollCurrentJobsConfig(device, timeout)
    if not configComplete:
        testComment = 'Config is taking longer than %d seconds to complete' % (timeout)
        printFP(testComment)
        return Global.FAIL, testComment
    else:
        return Global.PASS, ''

def SubscribeToAlerts(regions):
    """Subscribes to the given regions and substations for the current user."""

    GoToEmailAlert()
    time.sleep(1)
    nodeList = GetElement(Global.driver, By.XPATH, xpaths['email_alert_node_list'])
    allNodes = GetElements(nodeList, By.TAG_NAME, 'li')
    for node in allNodes:
        regionName = GetText(node, By.CLASS_NAME, 'REGION-name')
        if regionName in regions:
            # select this node
            checkbox = GetElement(node, By.TAG_NAME, 'input')
            checkbox.click()
    ClickButton(Global.driver, By.XPATH, xpaths['email_alert_save'])
    printFP(GetText(Global.driver, By.XPATH, xpaths['email_alert_return_msg']))
    ClickButton(Global.driver, By.XPATH, xpaths['email_alert_close'])

def printFP(message):
    """Writes a message to the log and prints to the console.
    level is the logging level
      0 - print to console only
      1 - debug
      2 - info
      3 - warning
      4 - error
      5 - critical"""
    print message
    if Global.loglevel == 'debug':
        logging.debug(message)
    elif Global.loglevel == 'info':
        logging.info(message)
    elif Global.loglevel == 'warning':
        logging.warning(message)
    elif Global.loglevel == 'error':
        logging.error(message)
    elif Global.loglevel == 'critical':
        logging.critical(message)
    else:
        pass

def GetOnlineDevice():
    """Finds an online device on ample and returns the device dictionary"""

    devID = Global.onDevs[0]
    return Global.devices[devID]

def GetOfflineDevice():
    """Finds a device not on ample and returns the device dictionary"""

    devID = Global.offDevs[0]
    return Global.devices[devID]

def MoveDeviceToOnline(serial):
    """Move a device from offline list to online list"""

    try:
        Global.offDevs.remove(serial)
    except Exception as e:
        print e.message
    Global.onDevs.append(serial)

def MoveDeviceToOffline(serial):
    """Move a device from online list to offline list"""

    try:
        Global.onDevs.remove(serial)
    except Exception as e:
        print e.messsage
    Global.offDevs.append(serial)

def ParseJsonInputFile(input_json):
    with open(input_json, 'r') as infile:
        inputfile = json.load(infile)
    return inputfile

def EmailAttachment(attachments, TOADDRS, subjectLine):
    """Emails a list of attachments to a list of recipients.
    Uses test.autpomation.server@gmail.com to send emails.

    attachments - list of files to attach
    TOADDRS - list of recipients to send the attachments to"""

    COMMASPACE = ', '
    sender = 'balaapptestacc@gmail.com'
    gmail_password = 'testaccount@123'
    recipients = TOADDRS

    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = subjectLine
    outer['To'] = COMMASPACE.join(recipients)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # Add the attachments to the message
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            outer.attach(msg)
        except:
            print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
            raise

    composed = outer.as_string()

    # Send the email
    try:
        s = smtplib.SMTP("smtp.gmail.com", 587)
        #with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(sender, gmail_password)
        s.sendmail(sender, TOADDRS, composed)
        s.close()
        print("Email sent!")
        return True
    except Exception as e:
        print("Unable to send the email.")
        print(str(e))
        return False

def NoDataAvailable(pagename):

    time.sleep(5)
    html = Global.driver.page_source

    elements = soup(html, "lxml")

    if pagename == "line-monitoring":
        keyword = 'line-monitoring'
    elif pagename == "device-management" or pagename == "device-management-upgrade":
        keyword = 'device-management'
    else:
        printFP('NoDataAvailable: Unable to find the requested Page')
        return None

    page = elements.find('div', class_=re.compile(keyword))
    try:
        tmppage = page.find('div', class_=re.compile('nodata-available'))
        classname = tmppage['class']
    except:
        printFP('NoDataAvailable: Unable to find the text')
        return None

    if not "ng-hide" in classname:
        nodataavailabletext = 'No Data Available'
        printFP('NoDataAvailable: %s' %nodataavailabletext)
        return nodataavailabletext
    else:
        nodataavailabletext = 'Data Available'
        printFP('NoDataAvailable: %s' %nodataavailabletext)
        return nodataavailabletext

def GetTableColumnOrder(pagename):

    columnnamesorder = {}

    html = Global.driver.page_source

    OrderElements = soup(html, "lxml")

    # find Page view
    page = OrderElements.find('div', class_=re.compile(pagename))

    if page.find('table'):
        tabledata = page.find('table')
        header = tabledata.find('thead')
        columnnames = header.find_all('div', class_=re.compile('ng-binding'))
        n=1
        for columnname in columnnames:
            name = columnname.text.strip().replace('"','')
            columnnamesorder[name] = n
            n = n+1
    return columnnamesorder


def FilteredDataFromTable(columnname, pagename):

    if pagename == "line-monitoring":
        keyword = 'line-monitoring'
    elif pagename == "device-management" or pagename == "device-management-upgrade":
        keyword = 'device-management'
    else:
        printFP('NoDataAvailable: Unable to find the requested Page')
        return None

    columnorder = GetTableColumnOrder(keyword)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(keyword))

    if page.find('table'):
        tabledata = page.find('table')
        # Get all rows
        rows = tabledata.find_all('tr', class_=re.compile('row'))
        for row in rows:
            if pagename == 'device-management':
                n=0
            else:
                n=1
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        columnnamevalueslist.append(value)
                    n = n+1

    printFP(columnnamevalueslist)
    return columnnamevalueslist


def FilteredDataFromTableMapping(columnname1, columnname2, pagename):

    if pagename == "line-monitoring":
        keyword = 'line-monitoring'
    elif pagename == "device-management" or pagename == "device-management-upgrade":
        keyword = 'device-management'
    else:
        printFP('NoDataAvailable: Unable to find the requested Page')
        return None

    columnorder = GetTableColumnOrder(keyword)

    column_1_position = columnorder[columnname1]

    column_2_position = columnorder[columnname2]

    # Create a dict
    valuesmappinglist = {}
    columnname1value = ''
    columnname2value = ''

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(keyword))

    if page.find('table'):
        tabledata = page.find('table')
        # Get all rows
        rows = tabledata.find_all('tr', class_=re.compile('row'))
        for row in rows:
            if pagename == 'device-management':
                n=0
            else:
                n=1
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == column_1_position:
                        value = td_tag.find('span').text.strip()
                        columnname1value = value
                    elif n == column_2_position:
                        value = td_tag.find('span').text.strip()
                        columnname2value = value
                    n = n+1
                if columnname1value and columnname2value:
                    valuesmappinglist[columnname1value] = columnname2value

    printFP(valuesmappinglist)
    return valuesmappinglist


def SelectYearMonthAndDateFromCalendar(year, month, date):
    datepicker = Global.driver.find_element_by_css_selector('.input-group.datepicker.pull-left')
    ultag = GetElement(datepicker, By.TAG_NAME, 'ul')
    visibility = ultag.get_attribute('style')

    if not "block" in visibility:
        datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
        time.sleep(1)
        datepickerbutton.click()
        time.sleep(1)

    findcurrentmonthandyear = GetDatePickerCurrentTitle()
    currentmonthandyear = findcurrentmonthandyear.text.strip()
    isalnum = currentmonthandyear.isalnum()

    if not isalnum:
        findcurrentmonthandyear.click()
        monthheaderbutton = GetElement(Global.driver, By.TAG_NAME, 'strong')
        monthheaderbutton.click()
    else:
        findcurrentmonthandyear.click()

    tables = GetElements(Global.driver, By.TAG_NAME, 'table')
    for table in tables:

        try:
            findcorrectable = table.get_attribute('aria-labelledby')
        except Exception as e:
            print e.message
            findcorrectable = None

        if "datepicker" in findcorrectable:
            tbody = GetElement(table, By.TAG_NAME, 'tbody')
            rows = GetElements(tbody, By.TAG_NAME, 'tr')
            for row in rows:
                columns = GetElements(row, By.TAG_NAME, 'td')
                for column in columns:
                    focusedyear = column.text.strip()
                    if focusedyear == year:
                        buttonelement = GetElement(column, By.TAG_NAME, 'button')
                        try:
                            isdisabled = buttonelement.get_attribute('disabled')
                        except Exception as e:
                            print e.message

                        if isdisabled is None:
                            buttonelement.click()
                            SelectMonthAndDateFromCalendar(month, date)
                            return True
                        else:
                            printFP('Given year %s is not enabled. Please choose valid year' % focusedyear)
                            return False
            if year < focusedyear:
                while not (year == focusedyear):
                    buttonpullleft = Global.driver.find_element_by_xpath("//i[contains(@class, 'glyphicon-chevron-left')]")
                    try:
                        buttonpullleft.click()
                    except:
                        return False
                    time.sleep(1)
                    rows = GetElements(tbody, By.TAG_NAME, 'tr')
                    for row in rows:
                        columns = GetElements(row, By.TAG_NAME, 'td')
                        for column in columns:
                            focusedyear = column.text.strip()
                            if focusedyear == year:
                                buttonelement = GetElement(column, By.TAG_NAME, 'button')
                                try:
                                    isdisabled = buttonelement.get_attribute('disabled')
                                except Exception as e:
                                    print e.message

                                if isdisabled is None:
                                    buttonelement.click()
                                    SelectMonthAndDateFromCalendar(month, date)
                                    return True
                                else:
                                    printFP('Given year %s is not enabled. Please choose valid year' % focusedyear)
                                    return False
            else:
                return False

def SelectMonthAndDateFromCalendar(month, date):
    datepicker = Global.driver.find_element_by_css_selector('.input-group.datepicker.pull-left')
    ultag = GetElement(datepicker, By.TAG_NAME, 'ul')
    visibility = ultag.get_attribute('style')

    if not "block" in visibility:
        datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
        time.sleep(1)
        datepickerbutton.click()
        time.sleep(1)

    findcurrentmonthandyear = GetDatePickerCurrentTitle()
    currentmonthandyear = findcurrentmonthandyear.text.strip()

    if not currentmonthandyear.isalnum():
        findcurrentmonthandyear.click()
    else:
        pass

    tables = GetElements(Global.driver, By.TAG_NAME, 'table')
    for table in tables:
        try:
            findcorrectable = table.get_attribute('aria-labelledby')
        except Exception as e:
            print e.message
            findcorrectable = None

        if 'datepicker' in findcorrectable:
            tbody = GetElement(table, By.TAG_NAME, 'tbody')
            rows = GetElements(tbody, By.TAG_NAME, 'tr')
            for row in rows:
                columns = GetElements(row, By.TAG_NAME, 'td')
                for column in columns:
                    focusedmonth = column.text.strip()
                    if focusedmonth == month:
                        buttonelement = GetElement(column, By.TAG_NAME, 'button')
                        try:
                            isdisabled = buttonelement.get_attribute('disabled')
                        except Exception as e:
                            print e.message

                        if isdisabled is None:
                            buttonelement.click()
                            SelectDateFromCalendar(date)
                            return True
                        else:
                            printFP('Given month %s is not enabled. Please choose valid month' % focusedmonth)
                            return False
            return False

def SelectDateFromCalendar(date):
    datepicker = Global.driver.find_element_by_css_selector('.input-group.datepicker.pull-left')
    ultag = GetElement(datepicker, By.TAG_NAME, 'ul')
    visibility = ultag.get_attribute('style')

    if not "block" in visibility:
        datepickerbutton = Global.driver.find_element_by_css_selector('.glyphicon.glyphicon-calendar')
        time.sleep(1)
        datepickerbutton.click()
        time.sleep(1)

    findcurrentmonthandyear = GetDatePickerCurrentTitle()
    currentmonthandyear = findcurrentmonthandyear.text.strip()

    if not currentmonthandyear.isalnum():

        tables = GetElements(Global.driver, By.TAG_NAME, 'table')
        for table in tables:
            try:
                findcorrectable = table.get_attribute('aria-labelledby')
            except Exception as e:
                print e.message
                findcorrectable = None

            if 'datepicker' in findcorrectable:
                tbody = GetElement(table, By.TAG_NAME, 'tbody')
                rows = GetElements(tbody, By.TAG_NAME, 'tr')
                if rows[0]:
                    n=0
                for row in rows:
                    columns = GetElements(row, By.TAG_NAME, 'td')
                    for column in columns:
                        focuseddate = column.text.strip()
                        if n == 0:
                            if focuseddate == "01":
                                startdate = focuseddate
                                n = None
                            else:
                                startdate = None
                        else:
                            startdate = "01"
                        if startdate == "01":
                            startdate == "01"
                            if focuseddate == date:
                                buttonelement = GetElement(column, By.TAG_NAME, 'button')
                                try:
                                    isdisabled = buttonelement.get_attribute('disabled')
                                except Exception as e:
                                    print e.message

                                if isdisabled is None:
                                    buttonelement.click()
                                    return True
                                else:
                                    printFP('Given date %s is not enabled. Please choose any other date' % focuseddate)
                                    return False
                return False
    else:
        printFP('Unable to select given date %s ' % date)
        return False



def GetDatePickerCurrentTitle():
    tables = GetElements(Global.driver, By.TAG_NAME, 'table')
    for table in tables:
        try:
            findcorrecttable = table.get_attribute('aria-labelledby')
        except Exception as e:
            print e.message
            findcorrecttable = None

        if "datepicker" in findcorrecttable:
            thead = GetElement(table, By.TAG_NAME, 'thead')
            row = GetElement(thead, By.TAG_NAME, 'tr')
            columns = GetElements(row, By.TAG_NAME, 'th')
            currenttitle = GetElement(columns[1], By.TAG_NAME, 'button')
            return currenttitle
        else:
            return None

def GetDatePickerCurrentDate():
    tables = GetElements(Global.driver, By.TAG_NAME, 'table')
    for table in tables:
        try:
            findcorrecttable = table.get_attribute('aria-labelledby')
        except Exception as e:
            print e.message
            findcorrecttable = None

        if "datepicker" in findcorrecttable:
            tbody = GetElement(table, By.TAG_NAME, 'tbody')
            rows = GetElements(tbody, By.TAG_NAME, 'tr')
            for row in rows:
                columns = GetElements(row, By.TAG_NAME, 'td')
                for column in columns:
                    try:
                        button = GetElement(column, By.TAG_NAME, 'button')
                    except Exception as e:
                        print e.message
                        button = None
                    if button is not None:
                        classname = button.get_attribute('class')
                        if 'active' in classname:
                            date = button.text.strip()
                            return date
        else:
            return None

def FaultEventsRegionTableGetColumnOrder(pagename):

    columnnamesorder = {}

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table')

    if table:
        thead = table.find('thead')
        columnnames = thead.find_all('div', class_=re.compile('ng-binding'))
        n=0
        for columnname in columnnames:
            name = columnname.text.strip().replace('"','')
            columnnamesorder[name] = n
            n = n+1
    return columnnamesorder


def FaultEventsRegionTableFilteredAllData(pagename, columnname):

    columnorder = FaultEventsRegionTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag,'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        columnnamevalueslist.append(value)
                    n = n+1

    printFP(columnnamevalueslist)
    return columnnamevalueslist

def FaultEventsFindSubstationWithFaults(pagename, columnname):

    columnorder = FaultEventsRegionTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag,'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        if value > 0:
                            substationelement = row.find('span', class_=re.compile('alink'))
                            substationname = substationelement.text.strip()
                            printFP(substationname)
                            return substationname
                    n = n+1

    return None

def FaultEventsCheckButtonStateandClick(button):
    tablepageroptions = GetElement(Global.driver, By.CLASS_NAME, 'pager-options')
    tablepagerbuttons = GetElements(tablepageroptions, By.TAG_NAME, 'a')
    for tablepagerbutton in tablepagerbuttons:
        buttonname = tablepagerbutton.text.split(' ')
        if button in buttonname[0] or button in buttonname[1] :
            parentelement = GetElement(tablepagerbutton, By.XPATH, '..')
            classname = parentelement.get_attribute('class')
            if 'disabled' in classname:
                return False
            else:
                JustClick(tablepagerbutton)
                time.sleep(3)
                return True
    return None


def FaultEventsGetSubstationFaultEventsCountInRegionTable(pagename, substationname):

    dictfaulteventscount = {}
    faulteventtypes = []

    columnorder = FaultEventsRegionTableGetColumnOrder(pagename)

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table')

    if table:
        thead = table.find('thead')
        columnnames = thead.find_all('div', class_=re.compile('ng-binding'))
        for columnname in columnnames:
            name = columnname.text.strip().replace('"','')
            if not 'Substation Name' in name:
                faulteventtypes.append(name)
                columnposition = columnorder[name]
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag,'class'):
                            if n == columnposition:
                                substationelement = row.find('span', class_=re.compile('alink'))
                                currentsubstationname = substationelement.text.strip()
                                if substationname in currentsubstationname:
                                    value = td_tag.find('span').text.strip()
                                    dictfaulteventscount[name] = value
                            n = n+1

    printFP(faulteventtypes)
    printFP(dictfaulteventscount)
    printFP(substationelement)
    return faulteventtypes, dictfaulteventscount, substationelement

def FaultEventsGroupTableGetTitle(pagename):

    title = {}

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('fault-group-table'))

    if table:
        tbody = table.find('tbody')
        titleframe = tbody.find('breadcrumb')
        names = titleframe.find_all('span', class_=re.compile('ng-binding'))
        n=0
        for name in names:
            filteredname = name.text.strip()
            if n==0:
                title[filteredname] = 'region'
            elif n==1:
                title[filteredname] = 'substation'
            elif n==2:
                title[filteredname] = 'feeder'
            elif n==3:
                title[filteredname] = 'site'
            n=n+1
    else:
        printFP('Unable to find fault events group table')
        return None

    printFP(title)
    return title

def FaultEventsGroupTableGetRowOrder(pagename):

    rownamesorder = {}

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('fault-group-table'))

    if table:
        tbody = table.find('tbody')
        rownames = tbody.find_all('tr', class_=re.compile('ng-scope'))
        time.sleep(1)
        n=0
        for rowname in rownames:
            name = rowname.find('td').text.strip()
            rownamesorder[name] = n
            n=n+1
    else:
        printFP('Unable to find fault events group table')
        return None

    printFP(rownamesorder)
    return rownamesorder

def FaultEventsGroupTableGetColumnOrder(pagename):

    columnnamesorder = {}

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('fault-group-table'))

    if table:
        tbody = table.find('tbody')
        columnnames = tbody.find_all('tr')
        for columnname in columnnames:
            if not columnname.has_attr('ng-repeat'):
                n=1
                correcttags = columnname.find_all('td', class_=re.compile('ng-binding'))
                for correcttag in correcttags:
                    name = correcttag.text.strip()
                    columnnamesorder[name] = n
                    n=n+1
    else:
        printFP('Unable to find fault events group table')
        return None

    printFP(columnnamesorder)
    return columnnamesorder

def FaultEventsGroupTableFilteredData(pagename, faultname, propertyname):

    columnorder = FaultEventsGroupTableGetColumnOrder(pagename)

    columnposition = columnorder[propertyname]

    roworder = FaultEventsGroupTableGetRowOrder(pagename)

    rowposition = roworder[faultname]

    # Create a list
    value = []

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('fault-group-table'))

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr', class_=re.compile('ng-scope'))
        time.sleep(1)
        m=0
        for row in rows:
            if m == rowposition:
                n=0
                for td_tag in row:
                    if n == columnposition:
                        filteredvalue = td_tag.text.strip()
                        value.append(filteredvalue)
                    n = n+1
            m=m+1
    else:
        printFP('Unable to find fault events group table')
        return None

    printFP(value)
    return value

def FaultEventsGetFaultEventsTotalDuration(pagename):

    columnname = 'Interruption Duration'

    columnorder = FaultEventsTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('list-styled-table'))

    FaultEventsCheckButtonStateandClick('First')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        totalvalueinseconds = 0
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.replace(' ','').strip()

                        if 'N/A' in value:
                            value = 0
                            pass
                        elif 'm' in value:
                            splitvalue = value.split('m')
                            mvalue = splitvalue[0]
                            mvalue = int(mvalue) * 60
                            tmpvalue = splitvalue[1].split('s')
                            svalue = tmpvalue[0]
                            value = int(mvalue) + int(svalue)
                            pass
                        elif 's' in value:
                            splitvalue = value.split('s')
                            value = splitvalue[0]
                            pass

                        columnnamevalueslist.append(value)
                        totalvalueinseconds = int(totalvalueinseconds) + int(value)
                        print('totalvalueinseconds : %s' %totalvalueinseconds)
                    n = n+1

        nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')
        while nextbuttonstatus:
            time.sleep(3)
            html = Global.driver.page_source
            FilterElements = soup(html, "lxml")
            page = FilterElements.find('div', class_=re.compile(pagename))
            table = page.find('table', class_=re.compile('list-styled-table'))
            if table:
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag, 'class'):
                            if n == columnposition:
                                value = td_tag.find('span').text.replace(' ','').strip()
                                if 'N/A' in value:
                                    value = 0
                                    pass
                                elif 'm' in value:
                                    splitvalue = value.split('m')
                                    mvalue = splitvalue[0]
                                    mvalue = int(mvalue) * 60
                                    tmpvalue = splitvalue[1].split('s')
                                    svalue = tmpvalue[0]
                                    value = int(mvalue) + int(svalue)
                                    pass
                                elif 's' in value:
                                    splitvalue = value.split('s')
                                    value = splitvalue[0]
                                    pass
                                columnnamevalueslist.append(value)
                                totalvalueinseconds = int(totalvalueinseconds) + int(value)
                                print('totalvalueinseconds : %s' %totalvalueinseconds)
                            n = n+1
                nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

        if totalvalueinseconds == 0:
            totalduration = 0
        else:
            m, s = divmod(totalvalueinseconds, 60)
            totalduration = '%dm %ds' %(m,s)

    printFP(columnnamevalueslist)
    printFP(totalduration)
    return columnnamevalueslist, totalduration


def FaultEventsTableGetColumnOrder(pagename):

    columnnamesorder = {}

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('list-styled-table'))

    if table:
        thead = table.find('thead')
        columnnames = thead.find_all('div', class_=re.compile('ng-binding'))
        n=0
        for columnname in columnnames:
            name = columnname.text.strip().replace('"','')
            columnnamesorder[name] = n
            n = n+1
    printFP(columnnamesorder)
    return columnnamesorder


def FaultEventsTableFilteredAllData(pagename, columnname):

    columnorder = FaultEventsTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('list-styled-table'))

    FaultEventsCheckButtonStateandClick('First')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag,'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        columnnamevalueslist.append(value)
                    n = n+1

        nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')
        while nextbuttonstatus:
            time.sleep(3)
            html = Global.driver.page_source
            FilterElements = soup(html, "lxml")
            # find Page view
            page = FilterElements.find('div', class_=re.compile(pagename))
            table = page.find('table', class_=re.compile('list-styled-table'))
            if table:
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag,'class'):
                            if n == columnposition:
                                value = td_tag.find('span').text.strip()
                                columnnamevalueslist.append(value)
                            n = n+1
                nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

    printFP(columnnamevalueslist)
    return columnnamevalueslist

def FaultEventsSiteTableGetColumnOrder(pagename):

    columnnamesorder = {}

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('phase-level-events-table'))

    if table:
        thead = table.find('thead')
        columnnames = thead.find_all('div', class_=re.compile('ng-binding'))
        n=0
        for columnname in columnnames:
            name = columnname.text.strip().replace('"','')
            columnnamesorder[name] = n
            n = n+1
    printFP(columnnamesorder)
    return columnnamesorder


def FaultEventsSiteTableFilteredAllData(pagename, columnname):

    columnorder = FaultEventsSiteTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('phase-level-events-table'))

    FaultEventsCheckButtonStateandClick('First')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag,'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        columnnamevalueslist.append(value)
                    n = n+1

        nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')
        while nextbuttonstatus:
            time.sleep(3)
            html = Global.driver.page_source
            FilterElements = soup(html, "lxml")
            # find Page view
            page = FilterElements.find('div', class_=re.compile(pagename))
            table = page.find('table', class_=re.compile('phase-level-events-table'))
            if table:
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag,'class'):
                            if n == columnposition:
                                value = td_tag.find('span').text.strip()
                                columnnamevalueslist.append(value)
                            n = n+1
                nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

    printFP(columnnamevalueslist)
    return columnnamevalueslist

def FaultEventsGetFeederFaultEventsCountInSubstationTable(pagename, columnname, feedername):

    columnorder = FaultEventsTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('list-styled-table'))

    FaultEventsCheckButtonStateandClick('First')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        count = 0
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        if feedername in value:
                            columnnamevalueslist.append(value)
                            count = count+1
                    n = n+1

        nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')
        while nextbuttonstatus:
            time.sleep(3)
            html = Global.driver.page_source
            FilterElements = soup(html, "lxml")
            page = FilterElements.find('div', class_=re.compile(pagename))
            table = page.find('table', class_=re.compile('list-styled-table'))
            if table:
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag, 'class'):
                            if n == columnposition:
                                value = td_tag.find('span').text.strip()
                                if feedername in value:
                                    columnnamevalueslist.append(value)
                                    count = count+1
                            n = n+1
                nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

    printFP(columnnamevalueslist)
    printFP(count)
    return columnnamevalueslist, count

def FaultEventsGetFeederFaultEventsCountInSubstationTableFilteredSpecificType (pagename, columnname, feedername, filtername):

    feedercolumnname = 'Feeder'
    columnorder = FaultEventsTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]
    feedercolumnposition = columnorder[feedercolumnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('list-styled-table'))

    FaultEventsCheckButtonStateandClick('First')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        count = 0
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == feedercolumnposition:
                        value = td_tag.find('span').text.strip()
                        if feedername in value:
                            m=0
                            for td_tag in row:
                                if hasattr(td_tag, 'class'):
                                    if m == columnposition:
                                        value = td_tag.find('span').text.strip()
                                        if value in filtervalue:
                                            columnnamevalueslist.append(value)
                                            count = count+1
                                    m = m+1
                    n = n+1

        nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')
        while nextbuttonstatus:
            time.sleep(3)
            html = Global.driver.page_source
            FilterElements = soup(html, "lxml")
            page = FilterElements.find('div', class_=re.compile(pagename))
            table = page.find('table', class_=re.compile('list-styled-table'))
            if table:
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag, 'class'):
                            if n == feedercolumnposition:
                                value = td_tag.find('span').text.strip()
                                if feedername in value:
                                    m=0
                                    for td_tag in row:
                                        if hasattr(td_tag, 'class'):
                                            if m == columnposition:
                                                value = td_tag.find('span').text.strip()
                                                if value in filtervalue:
                                                    columnnamevalueslist.append(value)
                                                    count = count+1
                                            m = m+1
                            n = n+1
                nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

    printFP(columnnamevalueslist)
    printFP(count)
    return columnnamevalueslist, count

def FaultEventsGetFaultEventsCount(pagename, columnname):

    columnorder = FaultEventsTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('list-styled-table'))

    FaultEventsCheckButtonStateandClick('First')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        count = 0
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        columnnamevalueslist.append(value)
                        count = count+1
                    n = n+1

        nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')
        while nextbuttonstatus:
            time.sleep(3)
            html = Global.driver.page_source
            FilterElements = soup(html, "lxml")
            page = FilterElements.find('div', class_=re.compile(pagename))
            table = page.find('table', class_=re.compile('list-styled-table'))
            if table:
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag, 'class'):
                            if n == columnposition:
                                value = td_tag.find('span').text.strip()
                                columnnamevalueslist.append(value)
                                count = count+1
                            n = n+1
                nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

    printFP(columnnamevalueslist)
    printFP(count)
    return columnnamevalueslist, count

def FaultEventsTableFilteredSpecificData(pagename, columnname, filtervalue):
    print filtervalue

    columnorder = FaultEventsTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    table = page.find('table', class_=re.compile('list-styled-table'))

    if table:

        firstbuttonstatus = FaultEventsCheckButtonStateandClick('First')
        print firstbuttonstatus
        if firstbuttonstatus:
            time.sleep(5)

        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        count = 0
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        print value
                        if value in filtervalue:
                            columnnamevalueslist.append(value)
                            count = count+1
                    n = n+1

        nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

        while nextbuttonstatus:
            time.sleep(3)
            html = Global.driver.page_source
            FilterElements = soup(html, "lxml")
            page = FilterElements.find('div', class_=re.compile(pagename))
            table = page.find('table', class_=re.compile('list-styled-table'))
            if table:
                tbody = table.find('tbody')
                # Get all rows
                rows = tbody.find_all('tr')
                for row in rows:
                    n=0
                    for td_tag in row:
                        if hasattr(td_tag, 'class'):
                            if n == columnposition:
                                value = td_tag.find('span').text.strip()
                                print value
                                if value in filtervalue:
                                    columnnamevalueslist.append(value)
                                    count = count+1
                            n = n+1
                nextbuttonstatus = FaultEventsCheckButtonStateandClick('Next')

    printFP(columnnamevalueslist)
    printFP(count)
    return columnnamevalueslist, count

def FaultEventsGroupViewTableGetColumnOrder(pagename):

    columnnamesorder = {}

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile(pagename))
    tableparent = page.find('table', class_=re.compile('list-styled-table'))
    groupview = tableparent.find('td', class_=re.compile('group-view'))
    table = groupview.find('table')

    if table:
        thead = table.find('thead')
        columnnames = thead.find_all('div', class_=re.compile('ng-binding'))
        n=0
        for columnname in columnnames:
            name = columnname.text.strip().replace('"','')
            columnnamesorder[name] = n
            n = n+1
    return columnnamesorder


def FaultEventsGroupViewTableFilteredAllData(pagename, columnname):

    columnorder = FaultEventsGroupViewTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    tableparent = page.find('table', class_=re.compile('list-styled-table'))
    groupview = tableparent.find('td', class_=re.compile('group-view'))
    table = groupview.find('table')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag,'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        columnnamevalueslist.append(value)
                    n = n+1

    printFP(columnnamevalueslist)
    return columnnamevalueslist

def FaultEventsGroupViewTableFilteredSpecificData(pagename, columnname, filtervalue):

    columnorder = FaultEventsGroupViewTableGetColumnOrder(pagename)

    columnposition = columnorder[columnname]

    # Create a list
    columnnamevalueslist = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))
    tableparent = page.find('table', class_=re.compile('list-styled-table'))
    groupview = tableparent.find('td', class_=re.compile('group-view'))
    table = groupview.find('table')

    if table:
        tbody = table.find('tbody')
        # Get all rows
        rows = tbody.find_all('tr')
        count = 0
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.find('span').text.strip()
                        print value
                        if filtervalue in value:
                            columnnamevalueslist.append(value)
                            count = count+1
                    n = n+1

    printFP(columnnamevalueslist)
    printFP(count)
    return columnnamevalueslist, count

def SelectAllEventTypes():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Event Type: %s' %filtername)
            if filtername and not 'UncheckAll' in filtername:
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
                        return False
                else:
                    printFP('Event Type "%s" is already selected by default' %filtername)
    return True

def UnselectAllEventTypes():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Unselecting Event Type: %s' %filtername)
            if filtername and not 'UncheckAll' in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Event Type "%s" is unselected successfully' %filtername)
                        time.sleep(1)
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Event Type "%s" is not selected by default' %filtername)
    return True

def UnCheckAllEventTypes():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')

        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('UnCheckAll Event Type: %s' %filtername)
            if filtername and 'UncheckAll' in filtername:
                eventbutton = GetElement(option, By.TAG_NAME, 'a')
                try:
                    eventbutton.click()
                    printFP('Event Type "%s" is selected successfully' %filtername)
                    time.sleep(1)
                except:
                    testComment = 'Test Fail - Unable to click "%s" option' %filtername
                    printFP(testComment)
                    return False

        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            if filtername and not 'UncheckAll' in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    testComment = 'Test Fail - Still Event Type "%s" is enabled after clicked "UnCheckAll" option' %filtername
                    printFP(testComment)
                    return False
    return True


def SelectEventType(eventtype):
    eventtype = eventtype.replace(' ','')
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Event Type: %s' %filtername)
            if filtername and eventtype in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if not "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Event Type "%s" is selected successfully' %filtername)
                        time.sleep(1)
                        return True
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Event Type "%s" is already selected by default' %filtername)

def UnselectEventType(eventtype):
    eventtype = eventtype.replace(' ','')
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultType-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event Type drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Unselecting Event Type: %s' %filtername)
            if filtername and eventtype in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Event Type "%s" is unselected successfully' %filtername)
                        time.sleep(1)
                        return True
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Event Type "%s" is not selected by default' %filtername)


def SelectAllEventStates():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event State drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Event State: %s' %filtername)
            if filtername and not 'UncheckAll' in filtername:
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
                        return False
                else:
                    printFP('Event State "%s" is already selected by default' %filtername)
    return True

def UnselectAllEventStates():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event State drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Unselecting Event State: %s' %filtername)
            if filtername and not 'UncheckAll' in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Event State "%s" is unselected successfully' %filtername)
                        time.sleep(1)
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Event State "%s" is not selected by default' %filtername)
    return True

def UnCheckAllEventStates():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event State drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')

        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('UnCheckAll Event State: %s' %filtername)
            if filtername and 'UncheckAll' in filtername:
                eventbutton = GetElement(option, By.TAG_NAME, 'a')
                try:
                    eventbutton.click()
                    printFP('Event State "%s" is selected successfully' %filtername)
                    time.sleep(1)
                except:
                    testComment = 'Test Fail - Unable to click "%s" option' %filtername
                    printFP(testComment)
                    return False

        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            if filtername and not 'UncheckAll' in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    testComment = 'Test Fail - Still Event State "%s" is enabled after clicked "UnCheckAll" option' %filtername
                    printFP(testComment)
                    return False
    return True


def SelectEventState(eventstate):
    eventstate = eventstate.replace(' ','')
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event State drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Event State: %s' %filtername)
            if filtername and eventstate in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if not "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Event State "%s" is selected successfully' %filtername)
                        time.sleep(1)
                        return True
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Event State "%s" is already selected by default' %filtername)

def UnselectEventState(eventstate):
    eventstate = eventstate.replace(' ','')
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'faultStatus-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Event State drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Event State: %s' %filtername)
            if filtername and eventstate in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Event State "%s" is unselected successfully' %filtername)
                        time.sleep(1)
                        return True
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Event State "%s" is not selected by default' %filtername)


def SelectAllTriggeredDetectors():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'detector-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Triggered Detector drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Triggered Detector: %s' %filtername)
            if filtername and not 'UncheckAll' in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if not "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Triggered Detector "%s" is selected successfully' %filtername)
                        time.sleep(1)
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Triggered Detector "%s" is already selected by default' %filtername)
    return True

def UnselectAllTriggeredDetectors():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'detector-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Triggered Detector drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Unselecting Triggered Detector: %s' %filtername)
            if filtername and not 'UncheckAll' in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Triggered Detector "%s" is unselected successfully' %filtername)
                        time.sleep(1)
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Triggered Detector "%s" is not selected by default' %filtername)
    return True

def UnCheckAllTriggeredDetectors():
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'detector-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Triggered Detector drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')

        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('UnCheckAll Triggered Detector: %s' %filtername)
            if filtername and 'UncheckAll' in filtername:
                eventbutton = GetElement(option, By.TAG_NAME, 'a')
                try:
                    eventbutton.click()
                    printFP('Triggered Detector "%s" is selected successfully' %filtername)
                    time.sleep(1)
                except:
                    testComment = 'Test Fail - Unable to click "%s" option' %filtername
                    printFP(testComment)
                    return False

        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            if filtername and not 'UncheckAll' in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    testComment = 'Test Fail - Still Triggered Detector "%s" is enabled after clicked "UnCheckAll" option' %filtername
                    printFP(testComment)
                    return False
    return True


def SelectTriggeredDetector(detectorname):
    detectorname = detectorname.replace(' ','')
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'detector-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Triggered Detector drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Triggered Detector: %s' %filtername)
            if filtername and detectorname in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if not "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Triggered Detector "%s" is selected successfully' %filtername)
                        time.sleep(1)
                        return True
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Triggered Detector "%s" is already selected by default' %filtername)

def UnselectTriggeredDetector(detectorname):
    detectorname = detectorname.replace(' ','')
    dropdown = GetElement(Global.driver, By.CLASS_NAME, 'detector-select-list')
    dropdownbutton = GetElement(dropdown, By.TAG_NAME, 'button')
    try:
        dropdownbutton.click()
        time.sleep(2)
    except:
        testComment = 'Test Fail - Unable to click "Triggered Detector drop down button"'
        printFP(testComment)
        return False
    time.sleep(1)
    try:
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')
        print dropdownlist
    except:
        dropdownbutton.click()
        time.sleep(1)
        dropdownlist = GetElement(dropdown, By.TAG_NAME, 'ul')

    if dropdownlist:
        dropdownoptions = GetElements(dropdownlist, By.TAG_NAME, 'li')
        for option in dropdownoptions:
            rawfiltername = option.text
            filtername = rawfiltername.strip().replace(' ','').replace('"','')
            filtername = ''.join(filtername.split())
            printFP('Selecting Triggered Detector: %s' %filtername)
            if filtername and detectorname in filtername:
                currentbuttonstatus = GetElement(option, By.TAG_NAME, 'span')
                classname = currentbuttonstatus.get_attribute('class')
                if "glyphicon-ok" in classname:
                    eventbutton = GetElement(option, By.TAG_NAME, 'a')
                    try:
                        eventbutton.click()
                        printFP('Triggered Detector "%s" is unselected successfully' %filtername)
                        time.sleep(1)
                        return True
                    except:
                        testComment = 'Test Fail - Unable to click "%s" option' %filtername
                        printFP(testComment)
                        return False
                else:
                    printFP('Triggered Detector "%s" is not selected by default' %filtername)


def ClickPhaseDetailsArrow():
    phasedetailarrow = GetElement(Global.driver, By.CLASS_NAME, 'phase-detail-arrow')
    phasedetailarrowbutton = GetElement(phasedetailarrow, By.TAG_NAME, 'span')
    classname = phasedetailarrowbutton.get_attribute('class')
    if 'ion-ios-arrow-back' in classname:
        JustClick(phasedetailarrowbutton)


def WaveformGetTableRowOrder(keyword):

    propertiesrownamesorder = {}
    detailsrownamesorder = {}

    html = Global.driver.page_source

    OrderElements = soup(html, "lxml")

    # find Page view
    waveformtable = OrderElements.find('div', class_=re.compile(keyword))
    waveformtablecontents = waveformtable.find_all('div', class_=re.compile('tab-pane'))

    i=0
    for waveformtablecontent in waveformtablecontents:
        if i == 0:
            if waveformtablecontent.find('table'):
                tabledata = waveformtablecontent.find('table')
                tbody = tabledata.find('tbody')
                rownames = tbody.find_all('tr', class_=re.compile('row'))
                n=0
                for rowname in rownames:
                    name = rowname.find('td').text.strip().replace('"','')
                    propertiesrownamesorder[name] = n
                    n = n+1
                i = 1
        elif i == 1:
            if waveformtablecontent.find('table'):
                tabledata = waveformtablecontent.find('table')
                tbody = tabledata.find('tbody')
                rownames = tbody.find_all('tr', class_=re.compile('row'))
                n=0
                for rowname in rownames:
                    name = rowname.find('td').text.strip().replace('"','')
                    detailsrownamesorder[name] = n
                    n = n+1

    print propertiesrownamesorder
    print detailsrownamesorder
    return propertiesrownamesorder, detailsrownamesorder


def WaveformFilteredDataFromTable(tabname, rowname):
    keyword = 'ui-waveform-details'

    propertiesrownamesorder, detailsrownamesorder = WaveformGetTableRowOrder(keyword)

    if tabname == 'Properties':

        rowposition = propertiesrownamesorder[rowname]

        # Create a list
        rownamevalueslist = []

        html = Global.driver.page_source

        FilterElements = soup(html, "lxml")

        # find Page view
        waveformtable = FilterElements.find('div', class_=re.compile(keyword))
        waveformtablecontents = waveformtable.find_all('div', class_=re.compile('tab-pane'))
        if waveformtablecontents[0].find('table'):
            tabledata = waveformtablecontents[0].find('table')
            # Get all rows
            rows = tabledata.find_all('tr', class_=re.compile('row'))
            n=0
            for row in rows:
                if n == rowposition:
                    tdtags = row.find_all('td')
                    value = tdtags[1].text.strip()
                    rownamevalueslist.append(value)
                n = n+1

        printFP(rownamevalueslist)
        return rownamevalueslist

    elif tabname == 'Details':

        rowposition = detailsrownamesorder[rowname]

        # Create a list
        rownamevalueslist = []

        html = Global.driver.page_source

        FilterElements = soup(html, "lxml")

        # find Page view
        waveformtable = FilterElements.find('div', class_=re.compile(keyword))
        waveformtablecontents = waveformtable.find_all('div', class_=re.compile('tab-pane'))
        if waveformtablecontents[1].find('table'):
            tabledata = waveformtablecontents[1].find('table')
            # Get all rows
            rows = tabledata.find_all('tr', class_=re.compile('row'))
            print rows
            n=0
            for row in rows:
                print row
                if n == rowposition:
                    tdtags = row.find_all('td')
                    value = tdtags[1].text.strip()
                    rownamevalueslist.append(value)
                n = n+1

        printFP(rownamevalueslist)
        return rownamevalueslist

    else:
        printFP('Unable to locate given tabname: %s' % tabname)
        return None

def GetWaveformChartDisplayStatus():
    try:
        waveformchart = GetElement(Global.driver, By.CLASS_NAME, 'chart-holder')
        downloadelement = GetElement(Global.driver, By.CLASS_NAME, 'noborder')
        downloadbutton = GetElement(downloadelement, By.TAG_NAME, 'button')
        classname = downloadbutton.get_attribute('class')
        if waveformchart is not None and 'hide' in classname :
            return True
        else:
            return False
    except Exception as e:
        print e.message
        return False

def GetUnitStatusOnWaveformGraph(unit):
    waveformchart = GetElement(Global.driver, By.CLASS_NAME, 'chart-container')
    series = GetElement(waveformchart, By.CLASS_NAME, 'highcharts-series-group')
    seriesgroups = GetElements(series, By.CLASS_NAME, 'highcharts-series')
    currentseries = [seriesgroups[0],seriesgroups[2]]
    electricfieldseries = [seriesgroups[1],seriesgroups[3]]

    if unit == 'Current':
        for group in currentseries:
            try:
                visibility = group.get_attribute('visibility')
            except Exception as e:
                print e.message
            if visibility:
                print('visibility: %s' %visibility)
                if 'hidden' in visibility:
                    return False
                else:
                    return True
            else:
                return True

    elif unit == 'E-field':
        for group in electricfieldseries:
            try:
                visibility = group.get_attribute('visibility')
            except Exception as e:
                print e.message
            if visibility:
                print('visibility: %s' %visibility)
                if 'hidden' in visibility:
                    return False
                else:
                    return True
            else:
                return True

def GetUnitStatusOnLogIGraph(unit):
    logichart = GetElement(Global.driver, By.TAG_NAME, 'stock-chart')
    series = GetElement(logichart, By.CLASS_NAME, 'highcharts-series-group')
    seriesgroups = GetElements(series, By.CLASS_NAME, 'highcharts-series')
    currentseries = [seriesgroups[0],seriesgroups[1],seriesgroups[2]]
    temperatureseries = [seriesgroups[3],seriesgroups[4],seriesgroups[5]]

    if unit == 'Current':
        for group in currentseries:
            try:
                classname = group.get_attribute('visibility')
                if 'hidden' in classname:
                    return False
            except Exception as e:
                print e.message

        return True

    elif unit == 'Temperature':
        for group in temperatureseries:
            try:
                classname = group.get_attribute('visibility')
                if 'hidden' in classname:
                    return False
            except Exception as e:
                print e.message

        return True

def LogiGetTableRowOrder(keyword):

    phasedetailsrownamesorder = {}

    html = Global.driver.page_source

    OrderElements = soup(html, "lxml")

    # find Page view
    logitable = OrderElements.find('div', class_=re.compile(keyword))
    logitablecontents = logitable.find_all('div', class_=re.compile('tab-pane'))

    for logitablecontent in logitablecontents:
            if logitablecontent.find('table'):
                tabledata = logitablecontent.find('table')
                tbody = tabledata.find('tbody')
                rownames = tbody.find_all('tr', class_=re.compile('row'))
                n=0
                for rowname in rownames:
                    name = rowname.find('td').text.strip().replace('"','')
                    phasedetailsrownamesorder[name] = n
                    n=n+1
    printFP(phasedetailsrownamesorder)
    return phasedetailsrownamesorder

def LogiGetTableColumnOrder(pagename):

    phasedetailscolumnnamesorder = {}

    html = Global.driver.page_source

    OrderElements = soup(html, "lxml")

    # find Page view
    page = OrderElements.find('div', class_=re.compile(pagename))

    if page.find('table'):
        tabledata = page.find('table')
        header = tabledata.find('thead')
        columnnames = header.find_all('th', class_=re.compile('ng-binding'))
        n=0
        for columnname in columnnames:
            name = columnname.text.strip().replace('"','')
            phasedetailscolumnnamesorder[name] = n
            n = n+1
    printFP(phasedetailscolumnnamesorder)
    return phasedetailscolumnnamesorder

def LogiFilteredDataFromTable(pagename, phase, propertyname):

    columnorder = LogiGetTableColumnOrder(pagename)

    columnposition = columnorder[phase]

    roworder = LogiGetTableRowOrder(pagename)

    rowposition = roworder[propertyname]

    # Create a list
    phasevalue = []

    html = Global.driver.page_source

    FilterElements = soup(html, "lxml")

    # find Page view
    page = FilterElements.find('div', class_=re.compile(pagename))

    if page.find('table'):
        tabledata = page.find('table')
        # Get all rows
        rows = tabledata.find_all('tr', class_=re.compile('row'))
        m=0
        for row in rows:
            if m == rowposition:
                n=0
                for td_tag in row:
                    if hasattr(td_tag, 'class'):
                        if n == columnposition:
                            value = td_tag.text.strip()
                            phasevalue.append(value)
                        n = n+1
            m=m+1

    printFP(phasevalue)
    return phasevalue

def GetPhaseStatusOnLogIGraph(phase):
    logichart = GetElement(Global.driver, By.TAG_NAME, 'stock-chart')
    series = GetElement(logichart, By.CLASS_NAME, 'highcharts-series-group')
    seriesgroups = GetElements(series, By.CLASS_NAME, 'highcharts-series')
    a_series = [seriesgroups[0],seriesgroups[3]]
    b_series = [seriesgroups[1],seriesgroups[4]]
    c_series = [seriesgroups[2],seriesgroups[5]]

    if phase == 'A':
        currentseries = a_series
    elif phase == 'B':
        currentseries = b_series
    elif phase == 'C':
        currentseries = c_series

    for group in currentseries:
        try:
            visibility = group.get_attribute('visibility')
        except Exception as e:
            print e.message
        if visibility:
            print('visibility: %s' %visibility)
            if 'hidden' in visibility:
                return False
            else:
                return True
        else:
            return True

def GetTimeRangeButtonStatus(selectedtimerange):
    timerangeframe = GetElement(Global.driver, By.TAG_NAME, 'zoom-filter')
    time.sleep(1)
    timerangefilters = GetElements(timerangeframe, By.TAG_NAME, 'label')
    time.sleep(1)
    for timerangefilter in timerangefilters:
        timerangefiltername = timerangefilter.text
        if timerangefiltername == selectedtimerange:
            buttonclassname = timerangefilter.get_attribute('class')
            if "active" in buttonclassname:
                return True
            elif not "active" in buttonclassname:
                return False
    printFP('Unable to find selected time range "%s" button status' %selectedtimerange)
    return None

def GetDnp3ViewChartTimeRangeButtonStatus(selectedtimerange, driver):
    timerangeframe = GetElement(driver, By.TAG_NAME, 'zoom-filter')
    time.sleep(1)
    timerangefilters = GetElements(timerangeframe, By.TAG_NAME, 'label')
    time.sleep(1)
    for timerangefilter in timerangefilters:
        timerangefiltername = timerangefilter.text
        if timerangefiltername == selectedtimerange:
            buttonclassname = timerangefilter.get_attribute('class')
            if "active" in buttonclassname:
                return True
            elif not "active" in buttonclassname:
                return False
    printFP('Unable to find selected time range "%s" button status' %selectedtimerange)
    return None

def GetHeadersOfLogiCharts(sitename):
    # Create a list
    listofheaders = []
    html = Global.driver.page_source
    Elements = soup(html, "lxml")
    # find Page view
    headers = Elements.find_all('breadcrumb')

    for header in headers:
        frame = header.find('span')
        nametags = frame.find_all('span', class_=re.compile('ng-binding'))
        for nametag in nametags:
            value = nametag.text.strip()
            listofheaders.append(value)
        if sitename in listofheaders:
            printFP(listofheaders)
            return listofheaders
        else:
            printFP(listofheaders)
            printFP('"%s" is not in the above list' % sitename)
            listofheaders = []

def GetCurrentDnp3TableColumnNames():

    # Create a list
    dnp3tablecolumnnameslist = []

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # Get all dnp3 points table hidden column names
    dnp3tablecolumnnames = Elements.find_all('th',{'colspan':'3'}, class_=re.compile('hide'))


    for div_tag in dnp3tablecolumnnames:
        # Add each hidden column names to the list
        dnp3tablecolumnname = div_tag.text.strip('\n')
        dnp3tablecolumnnameslist.append(dnp3tablecolumnname)

    return dnp3tablecolumnnameslist


def GetCurrentDnp3PointChartNames():

    # Create a list
    dnp3pointchartnames = []

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    page = Elements.find('div', class_=re.compile('modal-dialog'))
    chart = page.find('div', class_='chart')
    yaxis = chart.find_all('span', class_=re.compile('highcharts-yaxis-title'))

    for row in yaxis:
            title = row.text.strip()
            dnp3pointchartnames.append(title)
    return dnp3pointchartnames


def Dnp3PointsPhaseDataStatus(chartname, phase):

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    page = Elements.find('div', class_=re.compile('modal-dialog'))
    chart = page.find('div', class_='chart')
    dnp3charts = chart.find_all('dnp3-chart')
    for dnp3chart in dnp3charts:
        yaxis = dnp3chart.find('span', class_=re.compile('highcharts-yaxis-title'))
        title = yaxis.text.strip()
        if title in chartname:
            series = dnp3chart.find('g', class_=re.compile('highcharts-series-group'))
            seriesgroups = series.find_all('g', class_=re.compile('highcharts-series'))
            a_series = seriesgroups[1]
            b_series = seriesgroups[3]
            c_series = seriesgroups[5]

            if phase == 'A':
                currentseries = a_series
            elif phase == 'B':
                currentseries = b_series
            elif phase == 'C':
                currentseries = c_series
            currentseries.find('path')

            if currentseries.find('path'):
                return True
            else:
                return False

def GetPhaseStatusOnDnp3ViewChartGraph(chartname, phase):

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    page = Elements.find('div', class_=re.compile('modal-dialog'))
    chart = page.find('div', class_='chart')
    dnp3charts = chart.find_all('dnp3-chart')
    for dnp3chart in dnp3charts:
        yaxis = dnp3chart.find('span', class_=re.compile('highcharts-yaxis-title'))
        title = yaxis.text.strip()
        if title in chartname:
            series = dnp3chart.find('g', class_=re.compile('highcharts-series-group'))
            seriesgroups = series.find_all('g', class_=re.compile('highcharts-series'))
            a_series = [seriesgroups[0],seriesgroups[1]]
            b_series = [seriesgroups[2],seriesgroups[3]]
            c_series = [seriesgroups[4],seriesgroups[5]]

            if phase == 'A':
                currentseries = a_series
            elif phase == 'B':
                currentseries = b_series
            elif phase == 'C':
                currentseries = c_series

            for group in currentseries:
                if group.attrs.get('visibility'):
                    visibility = group['visibility']
                    if 'hidden' in visibility:
                        return False
                    else:
                        return True
                else:
                    return True


def CheckAllTimeStampsForSelectedDate():

    columnposition = 0

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile('line-monitoring'))

    if page.find('table'):
        tabledata = page.find_all('table')
        tablebody = tabledata[1].find('tbody')
        # Get all rows
        rows = tablebody.find_all('tr', class_=re.compile('row'))
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.text.split(" ")
                        value = value[0].strip()
                        if n>0:
                            compare = cmp(tmp, value)
                            if compare != 0:
                                return False
                        tmp = value
                        n = n+1
    return True

def GetCurrentTimeStamp():

    columnposition = 0

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile('line-monitoring'))

    if page.find('table'):
        tabledata = page.find_all('table')
        tablebody = tabledata[1].find('tbody')
        # Get all rows
        rows = tablebody.find_all('tr', class_=re.compile('row'))
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        value = td_tag.text.split(" ")
                        value = value[0].strip()
                        if value is not None:
                            return value
    return None

def GetCurrentAllTimeRanges(minchange, maxchange):

    dnp3tabletimelist = []

    columnposition = 0

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile('line-monitoring'))

    if page.find('table'):
        tabledata = page.find_all('table')
        tablebody = tabledata[1].find('tbody')
        # Get all rows
        rows = tablebody.find_all('tr', class_=re.compile('row'))
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        rawvalue = td_tag.text.split(" ")
                        value = rawvalue[1][:2]
                        if minchange:
                            if value == '12' and 'AM' in rawvalue[2]:
                                value = value.replace('12','00')
                        elif maxchange:
                            if value == '01' and 'PM' in rawvalue[2]:
                                value = value.replace('01','13')
                        else:
                            value = rawvalue[1][:2]
                        dnp3tabletimelist.append(value)
                        n=n+1
    printFP(dnp3tabletimelist)
    return dnp3tabletimelist

def GetPhaseRowColumnHeaders():

    # Create a list
    dnp3tablecolumnnameslist = []

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    page = Elements.find('div', class_=re.compile('line-monitoring'))

    if page.find('table'):
        tabledata = page.find_all('table')
        tableheader = tabledata[1].find('thead')
        rows = tableheader.find_all('span', class_=re.compile('ng-binding'))
        # Get all rows
        for span in rows:
            dnp3tablecolumnname = span.text.replace('"','')
            dnp3tablecolumnname = ''.join(dnp3tablecolumnname.split())
            dnp3tablecolumnnameslist.append(dnp3tablecolumnname)
        printFP(dnp3tablecolumnnameslist)
        return dnp3tablecolumnnameslist
    return None


def Dnp3FilteredDataFromTable(Phase):
    dnp3tablephasevaluelist = []

    if Phase == 'A':
        columnposition = 1
    elif Phase == 'B':
        columnposition = 2
    elif Phase == 'C':
        columnposition = 3
    else:
        printFP('Invalid Phase name')
        return None

    tmp = columnposition

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # find Page view
    page = Elements.find('div', class_=re.compile('line-monitoring'))

    if page.find('table'):
        tabledata = page.find_all('table')
        tablebody = tabledata[1].find('tbody')
        # Get all rows
        rows = tablebody.find_all('tr', class_=re.compile('row'))
        for row in rows:
            n=0
            for td_tag in row:
                if hasattr(td_tag, 'class'):
                    if n == columnposition:
                        if n<7:
                            value = td_tag.text.strip()
                            dnp3tablephasevaluelist.append(value)
                            columnposition = columnposition+2
                        else:
                            columnposition = tmp
                    else:
                        n=n+1
        printFP(dnp3tablephasevaluelist)
        return dnp3tablephasevaluelist
    return None

def FindNetworkGroupRow(comm_server_name, network_group):
    retval, comment = OpenNetworkGroupList(comm_server_name)
    if retval == Global.FAIL:
        return None, comment
    time.sleep(3)
    try:
        NetworkGroupRow = GetElement(Global.driver, By.CLASS_NAME, 'group-row')
    except:
        testComment = 'Table does not exist for this comm server'
        printFP(testComment)
        return None, testComment

    tbody = GetElement(NetworkGroupRow, By.TAG_NAME, 'tbody')
    rows = GetElements(tbody, By.TAG_NAME, 'tr')
    search = True

    while search:
        for row in rows:
            networkgroup = GetElement(row, By.XPATH, 'td[1]/span').text
            if networkgroup == network_group:
                return row, ''
        try:
            linkElement = GetElement(NetworkGroupRow, By.PARTIAL_LINK_TEXT, 'Next')
            parent = GetElement(linkElement, By.XPATH, '..').get_attribute('class')
            if 'disabled' in parent:
                search = False
            else:
                linkElement.click()
            time.sleep(2)
        except:
            search = False
        NetworkGroupRow = GetElement(Global.driver, By.CLASS_NAME, 'group-row')
        tbody = GetElement(NetworkGroupRow, By.TAG_NAME, 'tbody')
        rows = GetElements(tbody, By.TAG_NAME, 'tr')

    testComment = 'Test could not locate Network Group {} within SGW {}' .format(network_group, comm_server_name)
    return None, testComment

def OpenEditForSGW(comm_server_name):
    tablebody = GetElement(Global.driver, By.XPATH, xpaths['sys_admin_comm_table'])
    commserverrow = None
    rows = GetElements(tablebody, By.TAG_NAME, 'tr')
    for row in rows:
        if GetElement(row, By.XPATH, 'td[2]/span').text == comm_server_name:
            commserverrow = row
            break

    if commserverrow:
        try:
            GetElement(commserverrow, By.XPATH, 'td[11]/div/span[1]').click()
            return Global.PASS, ''
        except:
            testComment = 'Error occured when attempting to click button to edit SGW.'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = "Test could not find comm server name %s" % comm_server_name
        printFP(testComment)
        return Global.FAIL, testComment

def OpenAddNetworkGroupForSGW(comm_server_name):
    tablebody = GetElement(Global.driver, By.XPATH, xpaths['sys_admin_comm_table'])
    commserverrow = None
    rows = GetElements(tablebody, By.TAG_NAME, 'tr')
    for row in rows:
        if GetElement(row, By.XPATH, 'td[2]/span').text == comm_server_name:
            commserverrow = row
            break

    if commserverrow:
        try:
            GetElement(commserverrow, By.XPATH, 'td[11]/div/span[2]').click()
            return Global.PASS, ''
        except:
            testComment = 'Error occured when attempting to click button to add network group to SGW.'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = "Test could not find comm server name %s" % comm_server_name
        printFP(testComment)
        return Global.FAIL, testComment

def OpenNetworkGroupList(comm_server_name):
    tablebody = GetElement(Global.driver, By.XPATH, xpaths['sys_admin_comm_table'])
    print tablebody
    commserverrow = None
    rows = GetElements(tablebody, By.TAG_NAME, 'tr')
    print rows
    for row in rows:
        print row
        if GetElement(row, By.XPATH, 'td[2]/span').text == comm_server_name:
            commserverrow = row
            if 'group-open' in commserverrow.get_attribute('class'):
                return Global.PASS, ''
            break

    if commserverrow:
        try:
            GetElement(commserverrow, By.XPATH, 'td[1]/i').click()
            return Global.PASS, ''
        except:
            testComment = 'Error occured when attempting to open Network Group List'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        testComment = "Test could not find comm server name %s" % comm_server_name
        printFP(testComment)
        return Global.FAIL, testComment

def VerifyDeviceListInTable(device_names=None):
    if not device_names:
        return False
    else:
        jobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
        if len(jobs) == 0:
            return False

        numberOfDevicesFound = 0
        for i in range(len(jobs)):
            jobs[i].click()
            numberOfDevicesFound = 0
            for n in range(len(device_names)):
                try:
                    GetElement(Global.driver, By.XPATH, "//span[text()='"+device_names[n]+"']")
                    numberOfDevicesFound += 1
                except:
                    pass
            if numberOfDevicesFound == len(device_names):
                return True
        return False

def findLargestNumber(text):
    ls = list()
    for w in text.split():
        try:
            ls.append(int(w))
        except:
            pass
    try:
        return max(ls)
    except:
        return None

def GrabDeviceNamesOnPage():
    """Grabs all devices on the current page and returns it in a list"""
    deviceOnPage = []
    deviceNames = GetElements(Global.driver, By.XPATH, "//td[2]/span")
    for n in range(len(deviceNames)):
        deviceOnPage.append(deviceNames[n].text)
    return deviceOnPage

def SearchBar(searchKeyword):
    """Inserts searchKeyword into the SearchBar on the current page"""
    try:
        searchBox = GetElement(Global.driver, By.XPATH, "//input[@ng-model='jobsSearch' or @id='searchJobs']")
        ClearInput(searchBox)
        searchBox.send_keys(searchKeyword)
        return True
    except:
        return False

def SearchJobLink(device_names):
    numFound = 0
    for j in range(len(device_names)):
        try:
        # Check the serial number
            GetElement(Global.driver, By.XPATH, "//span[contains(text(),'"+device_names[j]+"')]")
            numFound += 1
        except:
            pass

    if numFound != len(device_names):
        return False
    else:
        return True


def GetOverrideGPSStatus(region, substation, feeder, site):
    GoToDevMan()
    time.sleep(5)
    GetSiteFromTop(region, substation, feeder, site)
    siteelement = GetSite(site)
    RightClickElement(siteelement)
    time.sleep(1)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Edit')
    time.sleep(2)
    overridegpsswitch = GetElement(Global.driver, By.CLASS_NAME, 'toggle-switch-animate')
    classname = overridegpsswitch.get_attribute('class')
    time.sleep(1)
    if "switch-on" in classname:
        return True
    elif "switch-off" in classname:
        return False

def GetLatAndLonValuesOfSite(region, substation, feeder, site):
    GoToDevMan()
    time.sleep(5)
    GetSiteFromTop(region, substation, feeder, site)
    siteelement = GetSite(site)
    RightClickElement(siteelement)
    time.sleep(1)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Edit')
    time.sleep(2)
    overridegpsswitch = GetElement(Global.driver, By.CLASS_NAME, 'toggle-switch-animate')
    classname = overridegpsswitch.get_attribute('class')
    time.sleep(1)
    if not 'switch-off' in classname:
        sitelatitude = GetElement(Global.driver, By.XPATH, "//input[@placeholder='Latitude']").get_attribute('value')
        sitelongitude = GetElement(Global.driver, By.XPATH, "//input[@placeholder='Longitude']").get_attribute('value')
        return sitelatitude, sitelongitude
    else:
        return None, None


def GetCurrentTableColumnNamesNotShown():

    # Create a list
    tablecolumnnameslist = []

    html = Global.driver.page_source

    Elements = soup(html, "lxml")

    # Get all dnp3 points table hidden column names
    table = Elements.find('table')
    tablehead = table.find('thead')
    tablecolumnnames = tablehead.find_all('th', class_=re.compile('ng-hide'))

    for div_tag in tablecolumnnames:
        # Add each hidden column names to the list
        tablecolumnname = div_tag.text.strip().strip('\n')
        tablecolumnnameslist.append(tablecolumnname)

    return tablecolumnnameslist


def GetFWSatusMsgFromFWScreen(device_name):
    GetElement(Global.driver, By.XPATH, "//table//tr[contains(td[2], device_name)]/td[6]/span/a").click()
    time.sleep(1)
    fwstatusmsg = GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'modal-body')]/p").text
    ClickButton(Global.driver, By.XPATH, "//div[contains(@class, 'modal-header')]//button[contains(@class, 'close')")
    return fwstatusmsg


def GetFirmwareUpgradeEachPhaseStatus():

    firmwareupgradeeachphasestatus = {}
    otapstatusframe = GetElement(Global.driver, By.XPATH, "//div[@class='otapStatusModel']")
    otapstatus = GetElement(otapstatusframe, By.TAG_NAME, 'ul')
    options = GetElements(otapstatus, By.XPATH, "li[@class='ng-scope']")
    for option in options:
        phasename = GetElement(option, By.XPATH, 'div[1]').text
        phasestatus = GetElement(option, By.XPATH, 'div[2]').get_attribute('class')
        phasestatus = phasestatus.split(' ')
        firmwareupgradeeachphasestatus[phasename] = phasestatus[2]
    printFP(firmwareupgradeeachphasestatus)
    return firmwareupgradeeachphasestatus


def CheckAllJobsPresence():
    printFP("INFO - Locating Job that contains the devices")
    try:
        allJobs = GetElements(Global.driver, By.XPATH, "//li[@ng-repeat='job in dataset']")
    except:
        printFP("INFO - Exception while trying to get jobs in the Current Jobs Upgrade Page")
        return False, 'TEST FAIL - Exception occurred while trying to get jobs in the current jobs Page'

    if len(allJobs) == 0:
        printFP("INFO - No upgrades were found.")
        return False, 'TEST FAIL - No Jobs were found.'

    return True, ''

