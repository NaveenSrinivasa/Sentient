import json
import os
from selenium.webdriver.common.keys import Keys
from Utilities_Ample import *
from Utilities_Framework import *
from Ample_DevMan import *


def DefaultCustomGroups():
    printFP("INFO - Testing Default Items under Custom Groups for Group Tree.")
    #Checks if there are the default Custom Groups in the Group Tree
    GoToDevMan()
    time.sleep(2)
    defaultCustomGroups = ["Active Faults", "Feeders with Faults", "Sites with Faults"]
    try:
        #Opens the custom group tree if it is collapsed
        customGroups = GetElement(Global.driver, By.XPATH, '//*[@id="node-2"]')
        if customGroups.get_attribute('collapsed') == 'true':
            customGroups.click()
            time.sleep(2)

        #Custom Groups have class 'item-name PREDEFINED_GROUP_NODE-name' so we use xpath to search for it
        groupNames = GetElements(Global.driver, By.XPATH, "//span[@class='item-name PREDEFINED_GROUP_NODE-name']")
        result = Global.PASS
        total = 0
        #Go through each Group Name and check if it is the same
        for group in groupNames:
            printFP('INFO - Found category: ' + group.text)
            if not (group.text in defaultCustomGroups):
                infoComment = 'Found group name called %s which is not in the default set of custom groups.' %group.text
                result = Global.FAIL
            else:
                total += 1
    except:
        testComment = 'Test ran into an exception error while performing test'
        printFP('INFO - ' + testComment)
        return Global.FAIL , 'TEST FAIL - ' + testComment

    #ensure that there was 3 default custom group under the custom group tree
    if total != len(defaultCustomGroups):
        result = Global.FAIL

    if result == Global.PASS:
        testComment = 'The default three categories appeared under Custom Group'
    else:
        testComment = 'The default three categories did not appear under Custom Group'
    printFP('INFO - ' + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)

def SearchandSelectGroupTree(input_file_path=None, searchFeeder=None):
    if not (input_file_path and searchFeeder):
        testComment = "Test is missing mandatory parameter(s)."
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    GoToDevMan()

    params = ParseJsonInputFile(input_file_path)
    #Goes to random node on the tree that exists
    if not GetLocationFromInput(params['Region'],params['Substation'],params['Feeder'],params['Site']):
        testComment = "Information provided by input file is invalid"
        printFP(testComment)
        return Global.FAIL, testComment

    #Performs a
    Tree = GetElement(Global.driver, By.XPATH, '//tree-view/div[2]/div[1]/ol')
    if GetElement(Tree, By.XPATH, "//span[contains(@class, 'item-active')]").text == params['Feeder']:
        result = Global.PASS
        searchtextbox = GetElement(Global.driver,By.CLASS_NAME, "node-search")
        ClearInput(searchtextbox)
        SendKeys(searchtextbox, searchFeeder)
        time.sleep(1)
        try:
            if 'ng-hide' not in GetElement(Global.driver, By.XPATH, "//ul[@class='dropdown-menu node-search-dropdown']/li").get_attribute('class'):
                testComment = 'Test could not locate feeder %s.' %searchFeeder
                printFP('INFO - ' + testComment)
                return Global.FAIL, 'TEST FAIL - ' + testComment
        except:
            pass

        GetElement(Global.driver, By.XPATH, "//ul[@class='dropdown-menu node-search-dropdown']/li[2]").click()

        time.sleep(3)
        if GetElement(Tree, By.XPATH, "//span[contains(@class, 'item-active')]").text == searchFeeder:
            testComment = 'Searched Feeder is now active after searching and clicking on link.'
        else:
            testComment = 'Searched Feeder is not active after searching and clicking on link.'
            result = Global.FAIL
        printFP('INFO - ' + testComment)
        return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)
    else:
        testComment = "Test found that the selected feeder was not active."
        printFP('INFO - ' + testComment)
        return Global.FAIL, testComment

def JumpFromDashToGroupTree():
    GoToDevMan()
    rootElement = GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]')
    if rootElement.get_attribute('collapsed') != 'true':
        rootElement.click()
    time.sleep(2)
    if not(GoToDashboard()):
        testComment = 'Test could not navigate to Dashboard'
        printFP("INFO - " + testComment)
        return Global.FAIL, testComment

    #Active Feeder Table
    divActiveTable = GetElement(Global.driver, By.TAG_NAME, 'feeder-tableview')
    activefaultTableBody = GetElement(divActiveTable, By.TAG_NAME, "tbody")
    try:
        activeFaults = GetElements(activefaultTableBody, By.TAG_NAME, 'tr')
    except:
        printFP("INFO - No active faults found.")
        return Global.PASS, 'TEST PASS - No Active Faults Found to run test with.'

    #Fault in Table , Get device name and click on it.
    result = Global.PASS
    feedername = GetElement(activeFaults[0], By.XPATH, 'td[3]/div').text
    time.sleep(1)
    try:
        GetElement(activeFaults[0], By.XPATH, 'td[1]/div').click()
    except:
        testComment = 'Exception when attempting to click a row of the active fault table'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    time.sleep(5)
    #Checks if it returns to feeder's fault page
    try:
        Tree = GetElement(Global.driver, By.XPATH, '//tree-view/div[2]/div[1]/ol')
        if GetElement(Tree, By.XPATH, "//span[contains(@class, 'item-active')]").text == feedername:
            testComment = 'Clicking one of the rows on the active faults table on the dash board does lead to the Feeder\'s Fault page'
        else:
            testComment = 'Clicking one of the rows on the active faults table does not lead to the fault page for the feeder'
            result = Global.FAIL
        printFP('INFO - ' + testComment)
        return result, 'TEST PASS - ' + testComment if result == Global.PASS else 'TEST FAIL - ' + testComment
    except:
        testComment = 'Exception error when attempting to get feeder name for active fault'
        printFP('INFO - ' + testComment)
        return Global.FAIL , 'TEST FAIL - ' + testComment


def CreateNodeAfterDeleting(input_file_path=None, node_to_delete=None):
    # find node first -- if exist, delete it and then add it again

    if input_file_path == None or device_detail_path == None:
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
        testComment = "Unable to locate node based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    node = GetElement(Global.driver, By.XPATH, "//span[contains(text(),"+node_to_delete+")]")
    nodeclass = node.get_attribute('class')

    RightClickElement(node)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Delete')
    ClickButton(Global.driver, By.XPATH, xpaths['tree_add_node_submit'])

    time.sleep(5)

    if 'SITE' in nodeclass:
        CreateSite(region, sub, feeder)
    elif 'FEEDER' in nodeclass:
        CreateFeeder(region, sub)
    elif 'SUBSTATION' in nodeclass:
        CreateSubstation(sub, region)
    elif 'REGION' in nodeclass:
        nodeElement = GetElement(Global.driver, By.ID, 'node-1')
        result = CreateRegion(region, nodeElement)

    node = GetElement(Global.driver, By.XPATH, "//span[contains(text(),"+node_to_delete+")]")
    node.click()

    time.sleep(2)

    returnval = NoDataAvailable('device-management')
    if returnval == None:
        testComment = 'Unable to find if data is available.'
        result = Global.FAIL
    elif 'No Data' in returnval:
        testComment = 'No Data available after deleting and creating the same node.'
        result = Global.PASS
    elif 'Data' in returnval:
        testComment = 'Data still exists after deleting and recreating the node.'
        result = Global.FAIL

    printFP('INFO - ' + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)

def AddDeviceToTree(input_file_path=None, device_detail_path=None, wait_for_online=True):
    if input_file_path == None or device_detail_path == None:
        testComment = 'Missing an input parameter value for this test'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    #Adds a device to the tree by clicking the site location that was specified by the input file
    GoToDevMan()
    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    siteLocation = GetSite(site)
    RightClickElement(siteLocation)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Add Device')

    time.sleep(5)
    #device_detail_path is a json file with all the fields to fill out which is parsed to deviceInfo
    deviceInfo = ParseJsonInputFile(device_detail_path)

    #starts filling out the fields based on deviceInfo
    serialNumber = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
    time.sleep(2)
    serialNumber.send_keys(deviceInfo["Serial Number"])

    if not deviceInfo["Description"] == "":
        Description = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'description')]/textarea")
        Description.send_keys(deviceInfo["Description"])

    productName = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'productName')]/descendant::button")
    productName.click()
    parentelement = GetElement(productName, By.XPATH, '..')
    SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Product Name'])
    time.sleep(2)

    platform = GetElement(Global.driver, By.XPATH, "//span[contains(@ng-if,'platform')]/descendant::button")
    platform.click()
    parentelement = GetElement(platform, By.XPATH, '..')
    SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Platform'])
    time.sleep(2)

    phase = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'phase')]/descendant::button")
    phase.click()
    parentelement = GetElement(phase, By.XPATH, '..')
    SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Phase'])
    time.sleep(2)

    macAddr = GetElement(Global.driver, By.XPATH, "//form/div[12]/div/input")
    macAddr.send_keys(deviceInfo["MAC Address"])

    sIPAddr = GetElement(Global.driver, By.XPATH, "//form/div[13]/div/input")
    sIPAddr.send_keys(deviceInfo["Sensor IP Address"])

    sDNP = GetElement(Global.driver, By.XPATH, "//form/div[14]/div/input")
    sDNP.send_keys(deviceInfo["Sensor DNP Address"])

    dnpPort = GetElement(Global.driver, By.XPATH, "//form/div[15]/div/input")
    ClearInput(dnpPort)
    dnpPort.send_keys(deviceInfo["DNP General Port"])

    swVer = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'softwareVersion')]/descendant::button")
    swVer.click()
    parentelement = GetElement(swVer, By.XPATH, '..')
    SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Software Version'])
    time.sleep(2)

    partNumber = GetElement(Global.driver, By.XPATH, "//form/div[17]/div/input")
    partNumber.send_keys(deviceInfo["SEI Part Number"])

    network = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'networkType')]/descendant::button")
    network.click()
    parentelement = GetElement(network, By.XPATH, '..')
    SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Type'])
    time.sleep(2)

    if not deviceInfo['Sensor Gateway Name'] == '':
        commserver = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'commServerSelection')]")
        commserver.click()
        time.sleep(1)
        print deviceInfo['Sensor Gateway Name']
        button = GetElement(Global.driver, By.XPATH, "//a[@class='option']/span[2]/span[text()='"+ deviceInfo['Sensor Gateway Name'] +"']")
        button.click()
        time.sleep(2)

        network = GetElement(Global.driver, By.XPATH, "//div[contains(@selected-model,'networkGroupSelection')]")
        network.click()
        parentelement = GetElement(network, By.XPATH, '..')
        SelectFromMenu(parentelement, By.TAG_NAME, 'span', deviceInfo['Network Group Name'])

    # secondaryIP = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-if,'serialNumber')]/input")
    # secondaryIP.send_keys(deviceInfo["Secondary IP Address"])

    time.sleep(3)

    #Clicks the Add Button to attempt to add it into the tree
    ClickButton(Global.driver, By.XPATH, "//div[contains(@ng-show,'addDevice_form')]/descendant::button")
    time.sleep(5)

    #This is to check if there are any errors that occur while adding the device
    try:
        msgBox = GetElement(Global.driver, By.CLASS_NAME, 'alert-danger')
        msg = GetElement(msgBox, By.XPATH, 'div/span').text
        if msg:
            printFP('INFO - Adding Device encountered an error.')
            printFP('INFO - Error message: '+ msg)
            GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
            time.sleep(3)
            return Global.FAIL, 'TEST FAIL - ' + msg
    except:
        pass
    GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
    time.sleep(2)
    """Check if the device is within the table and check the state that it is in based on whether it was
    given SGW/comm servers or not; unregistered if no SGW/CS was given."""
    JobTbody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
    DeviceRow = FindRowInTable(JobTbody, deviceInfo['Serial Number'])
    if DeviceRow:
        if deviceInfo['Sensor Gateway Name']:
            if wait_for_online:
                if IsOnline(deviceInfo['Serial Number']):
                    result = Global.PASS
                    testComment = '%s did come online and successfully uploaded'% deviceInfo['Serial Number']
                else:
                    testComment = '%s did not come online' % deviceInfo['Serial Number']
                    result = Global.FAIL
            else:
                result = Global.PASS
                testComment = 'Successfully added device %s, but did not wait for it to come online.' % deviceInfo['Serial Number']
        else:
            if 'glyphicon-transfer' in GetElement(DeviceRow, By.XPATH, 'td[4]/span').get_attribute('class'):
                result = Global.PASS
                testComment = 'Test did not register a device to a sensor gateway and it correctly displays unregistered icon.'
            else:
                result = Global.FAIL
                testComment = 'Device Status is not unregistered after not being registered to a sensor gateway.'

    else:
        result = Global.FAIL
        testComment = 'Test could not locate newly added device %s in table.' %deviceInfo['Serial Number']

    printFP('INFO - ' + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)

def VerifyOrganizationDetails():

    GoToDevMan()
    time.sleep(1)
    """Opens up the root node"""
    nodeElement = GetElement(Global.driver, By.XPATH, "//span[contains(@class, 'ROOTNODE-name')]")
    RootNodeTitle = nodeElement.text
    ListofDetails = []
    ListofTitles = ["Name", "Number of Regions", "Number of Substations", "Number of Feeders", "Number of Sites", "Number of Devices"]
    ListofDetails.append(RootNodeTitle)
    nodeElement.click()

    totalDevices = 0

    time.sleep(2)
    """Opens up the region and counts the number of devices there based on the amount displayed at the bottom of the table"""
    Regions = GetElements(Global.driver, By.XPATH, "//span[contains(@class, 'REGION-name')]")
    ListofDetails.append(str(len(Regions)))
    for x in Regions:
        x.click()
        time.sleep(1)
    """Counts the number of substations and for each substation opens each of them for feederes"""
    Substations = GetElements(Global.driver, By.XPATH, "//span[contains(@class, 'SUBSTATION-name')]")
    ListofDetails.append(str(len(Substations)))
    for x in Substations:
        x.click()
        time.sleep(1)
    """Counts the number of feeders and for each feeder opens the feeder"""
    Feeders = GetElements(Global.driver, By.XPATH, "//span[contains(@class, 'FEEDER-name')]")
    ListofDetails.append(str(len(Feeders)))
    for x in Feeders:
        x.click()
        time.sleep(1)
    """Counts the number of sites and for each site opens the site"""
    Sites = GetElements(Global.driver, By.XPATH, "//span[contains(@class, 'SITE-name')]")
    ListofDetails.append(str(len(Sites)))
    for x in Sites:
        x.click()
        time.sleep(1)
        if 'ng-hide' in GetElement(Global.driver, By.XPATH, "//div[contains(@class, 'nodata-available') and contains(@class, 'display-table')]").get_attribute('class'):
            tablebody = GetElement(Global.driver, By.TAG_NAME, 'tbody')
            totalDevices += len(GetElements(tablebody, By.TAG_NAME, 'tr'))
        else:
            printFP('INFO - No Devices Available for this region.')
        
    ListofDetails.append(str(totalDevices))

    """Right clicks the root node for the information and does a comparison to see if the information in the root node was correct"""
    nodeElement = GetElement(Global.driver, By.XPATH, "//span[contains(@class, 'ROOTNODE-name')]")
    RootNodeTitle = nodeElement.text
    RightClickElement(nodeElement)
    SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Details')

    time.sleep(1)
    textVal = GetElements(Global.driver, By.XPATH, "//span[contains(@class, 'section-value')]")
    result = Global.PASS
    for i in range(len(textVal)):
        if not textVal[i].text == ListofDetails[i]:
            printFP("INFO - %s did not match. Test had %s while details said it was %s" %(ListofTitles[i], ListofDetails[i], textVal[i].text))
            result = Global.FAIL
        else:
            printFP("INFO - %s did match. Test had %s while details said it was %s" %(ListofTitles[i], ListofDetails[i], textVal[i].text))

    if result == Global.FAIL:
        printFP("INFO - Some details did not match. Please refer to log file to determine which ones.")
        return Global.FAIL , 'TEST FAIL - Some details did not match. Refer to log file to determine which ones.'
    else:
        printFP('INFO - All group tree details matched.')
        return Global.PASS, 'TEST PASS - All group tree details matched.'

def SwitchTabsWhileSearching(searchKeyword=None):
    if not searchKeyword:
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()
    time.sleep(2)
    #Fills out the search box
    searchtextbox = GetElement(Global.driver,By.CLASS_NAME, "node-search")
    time.sleep(1)
    ClearInput(searchtextbox)
    time.sleep(1)
    SendKeys(searchtextbox, searchKeyword)
    time.sleep(5)
    searchtextbox = GetElement(Global.driver,By.CLASS_NAME, "node-search")
    printFP('INFO - Value inside Search Text Box: %s' %searchtextbox.get_attribute('value'))

    #Switches to Dashboard
    if not GoToDashboard():
        testComment = 'Test could not navigate to Dashboard to complete test.'
        printFP("INFO - " + testComment)
        return Global.FAIL, testComment
    time.sleep(5)

    #Go back to Device Management and check if the search box still has items
    GoToDevMan()
    searchtextbox = GetElement(Global.driver,By.CLASS_NAME, "node-search")
    time.sleep(1)
    if searchtextbox.get_attribute('value') == searchKeyword:
        testComment = 'Value inside the Search Text Box is %s. Should be empty.' % searchtextbox.get_attribute('value')
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    else:
        testComment = 'Value inside the Search Text Box is %s' %searchtextbox.get_attribute('value')
        printFP('INFO - ' + testComment)
        return Global.PASS, 'TEST PASS - ' + testComment

def HideGroupTree():

    LocationsWithGroupTree = [GoToLineMon, GoToLineMonWaveforms, GoToLineMonLogI, GoToLineMonDNP3, GoToDevMan, GoToDevUpgrade]

    """Goes to each location with a group tree and attempts to hide the group tree"""
    for n in range(len(LocationsWithGroupTree)):
        LocationsWithGroupTree[n]()
        time.sleep(3)
        rootnode = GetElement(Global.driver, By.ID, 'node-1')
        time.sleep(1)
        #Checks if the group tree is expanded, if it is not, close it
        if rootnode.get_attribute('collapsed') == 'true':
            printFP("INFO - Group Tree is not currently expanded. Opening it for test.")
            ClickButton(rootnode, By.XPATH, 'div[2]/span[1]/a')
            time.sleep(3)

        #Attempts to hide the root node of the tree by clicking on it
        rootnode = GetElement(Global.driver, By.ID, 'node-1')
        ClickButton(rootnode, By.XPATH, 'div[2]/span[1]/a')
        time.sleep(1)

        #Checks if it is hidden; if not, end the test and return fail
        if 'hidden' in GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]/ol').get_attribute('class'):
            printFP("INFO - Clicking hides the group tree.")
        else:
            testComment = 'Clicking the expanded Group Tree does not hide the Group Tree'
            printFP("INFO - " + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

        #Return it back to an expanded state for other tabs to test it
        rootnode = GetElement(Global.driver, By.ID, 'node-1')
        ClickButton(rootnode, By.XPATH, 'div[2]/span[1]/a')
        time.sleep(3)

        if not 'hidden' in GetElement(Global.driver, By.XPATH, '//*[@id="node-1"]/ol').get_attribute('class'):
            printFP("INFO - Clicking expands the group tree.")
        else:
            testComment = 'Clicking the expanded Group Tree does not hide the Group Tree'
            printFP("INFO - " + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment

    testComment = 'Group Tree hiding operated correctly.'
    printFP('INFO - ' + testComment)
    return Global.PASS, 'TEST PASS - ' + testComment

def RefreshGroupTree(input_file_path=None, selectedNodeName=None, typeofNode=None):
    if not (input_file_path and selectedNodeName and typeofNode):
        testComment = 'Test is missing manadatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']
    #Go to a specific node and expand it (node selected is based on input_file_path)
    GoToDevMan()
    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Unable to locate locations based off input file"
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL ' + testComment

    if typeofNode == 'Site':
        location = GetSite(selectedNodeName)
    elif typeofNode == 'Feeder':
        location = GetFeeder(selectedNodeName)
    elif typeofNode == 'Substation':
        location = GetSubstation(selectedNodeName)
    elif typeofNode == 'Region':
        location = GetRegion(selectedNodeName)

    #Check if the data exists for this node.
    dataExist = False
    if 'ng-hide' in GetElement(Global.driver, By.XPATH, "//span[text()='No Data Available']").get_attribute('class'):
        dataExist = True

    Global.driver.refresh()
    time.sleep(2)
    #Checks for the active element within the group tree
    activeElement = GetElement(Global.driver, By.XPATH, "//span[contains(@class,'item-active')]")
    if not activeElement.text == selectedNodeName:
        testComment = 'Node is not selected after refresh.'
        printFP(testComment)
        return Global.FAIL, testComment

    #Makes sure that after refresh that the data is consistent prior to refresh
    printFP('INFO - Node is still selected after refresh.')
    if ('ng-hide' in GetElement(Global.driver, By.XPATH, "//span[text()='No Data Available']").get_attribute('class')) and dataExist:
        result = Global.PASS
        testComment = 'Node had data and after refresh, the node still showed data.'
    elif not ('ng-hide' in GetElement(Global.driver, By.XPATH, "//span[text()='No Data Available']").get_attribute('class') and dataExist):
        result = Global.PASS
        testComment = 'Node had no data and after refresh, the node still shows no data.'
    else:
        result = Global.FAIL
        testComment = 'Node has mismatching data availability after refresh.'
    printFP('INFO - ' + testComment)
    return result, testComment

def SearchBarTreeView(searchKeyword=None):
    if searchKeyword == None:
        testComment = "No string was provided to search for in this test"
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()
    Global.driver.refresh()
    time.sleep(1)
    printFP('Searching given keyword: %s in node tree' % searchKeyword)
    if Search(searchKeyword,0):
        testComment = 'Search was succesful for finding keyword in Nodes Tree.'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'Searching nodes tree with Input %s returns nothing' % searchKeyword
        printFP(testComment)
        return Global.FAIL, testComment

def AddRegion(regionName=None, node=None):
    if not (regionName and node):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()

    nodeElement = GetElement(Global.driver, By.ID, 'node-1')

    result = CreateRegion(regionName, nodeElement)

    if result:
        testComment = 'Successfully created region {}' .format(regionName)
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'Test did not successfully create region {}.' .format(regionName)
        printFP(testComment)
        return Global.FAIL, testComment

def AddSubstation(substationName=None, region=None):
    if not (substationName and region):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment
    GoToDevMan()

    if not GetLocationFromInput(region,None,None,None):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    regionElement = GetRegion(region)
    result = CreateSubstation(substationName, regionElement)

    if result:
        testComment = 'Successfully created substation {}' .format(substationName)
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'Test did not successfully create substation {}.' .format(substationName)
        printFP(testComment)
        return Global.FAIL, testComment

def AddFeeder(feederName=None, substation=None, region=None):
    if not (region and substation and feederName):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()
    if not GetLocationFromInput(region,substation,None,None):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    substationElement = GetSubstation(substation)
    result = CreateFeeder(feederName, substationElement)

    if result:
        testComment = 'Successfully created feeder {}' .format(feederName)
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'Test did not successfully create feeder {}.' .format(feederName)
        printFP(testComment)
        return Global.FAIL, testComment

def AddSite(siteName=None, feeder=None, latitude=None, longitude=None, substation=None, region=None):
    if not (siteName and feeder and latitude and longitude and substation and region):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP(testComment)
        return Global.FAIL, testComment

    GoToDevMan()
    if not GetLocationFromInput(region,substation,feeder,None):
        testComment = "Unable to locate site based on input file"
        printFP(testComment)
        return Global.FAIL, testComment

    feederElement = GetFeeder(feeder)
    result = CreateSite(siteName, feederElement, latitude, longitude)

    if result:
        testComment = 'Successfully created site {}' .format(siteName)
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'Test did not successfully create site {}.' .format(siteName)
        printFP(testComment)
        return Global.FAIL, testComment

def EditNode(input_file_path=None, node_type=None, title=None, site_details=None, save=True):
    if not (input_file_path and node_type):
        testComment = "Test is missing mandatory parameter(s)."
        printFP(testComment)
        return Global.FAIL, testComment

    params = ParseJsonInputFile(input_file_path)
    region = params['Region']
    sub = params['Substation']
    feeder = params['Feeder']
    site = params['Site']
    count = 0

    Global.driver.refresh()
    time.sleep(1)
    GoToDevMan()
    if not GetLocationFromInput(region,sub,feeder,site):
        testComment = "Could not locate portions of the data in the location input file"
        printFP(testComment)
        return Global.FAIL, testComment

    if not node_type == 'Site':
        if node_type == 'Region':
           location = GetRegion(region)
        elif node_type == 'Substation':
           location = GetSubstation(sub)
        elif node_type == 'Feeder':
           location = GetFeeder(feeder)

        RightClickElement(location)
        time.sleep(1)
        SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Edit')
        time.sleep(1)
        inputElement = GetElement(Global.driver, By.NAME, 'newNodeName')
        ClearInput(inputElement)
        SendKeys(inputElement, title)
        time.sleep(1)
        try:
            errors = GetElements(Global.driver, By.XPATH, "//p[@class='ample-error-message ng-binding']")
            for error in errors:
                if not 'ng-hide' in error.get_attribute('class'):
                    GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
                    printFP("Error Message: %s" % error.text)
                    return Global.FAIL, error.text
        except:
            pass

        if save:
            ClickButton(Global.driver, By.XPATH, xpaths['tree_add_node_submit'])
            time.sleep(2)
            try:
                errorBox = GetElement(Global.driver, By.CLASS_NAME, 'alert-danger')
                errorText = GetElement(errorBox, By.XPATH, 'div/span').text
                printFP("Error Message: %s" %errorText)
                GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
                return Global.FAIL, errorText
            except:
                pass
        else:
            GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
            time.sleep(2)
        if node_type == 'Region':
            location = GetRegion(title)
        elif node_type == 'Substation':
            location = GetSubstation(title)
        elif node_type == 'Feeder':
            location = GetFeeder(title)

        if location and save:
            return Global.PASS, ''
        elif location and not save:
            testComment = 'Test did not save editted values, but somehow still found it in the group tree.'
            printFP(testComment)
            return Global.FAIL, ''
        elif not location and not save:
            return Global.PASS, ''
        else:
            testComment = 'Test could not locate new editted value'
            printFP(testComment)
            return Global.FAIL, testComment
    else:
        formdetails = ParseJsonInputFile(site_details)
        siteLocation = GetSite(site)
        RightClickElement(siteLocation)
        SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Edit')
        form = GetElement(Global.driver, By.CLASS_NAME, 'modal-content')
        textboxes = GetElements(form, By.CLASS_NAME, 'form-group')
        dictVals = {}
        for x in textboxes:
            count += 1
            label = x.find_element_by_css_selector('label.col-xs-4.col-sm-4.control-label.text-left.font-weight-normal.ng-binding')
            if not label.text == 'Override GPS':
                if label.text == 'Description':
                    box = GetElement(x, By.TAG_NAME, 'textarea')
                else:
                    box = GetElement(x, By.TAG_NAME, 'input')
                dictVals[label.text] = box.get_attribute('value')
                ClearInput(box)
                box.send_keys(formdetails[label.text])
            elif formdetails['Latitude'] or formdetails['Longitude']:
                gpselement = GetElement(Global.driver, By.XPATH, "//label[contains(text(),'Override GPS')]")
                gpsswitch = GetElement(Global.driver, By.XPATH, "//div[contains(@ng-model,'overrideGps')]/div")
                SwitchOnOff(gpselement, gpsswitch, 'true')
                time.sleep(1)
        if save:
            ClickButton(Global.driver, By.XPATH, xpaths['tree_edit_close'])
            time.sleep(1)
            try:
                msg = GetText(Global.driver, By.XPATH, xpaths['tree_edit_err_msg'])
                if msg:
                    ClickButton(Global.driver, By.XPATH, xpaths['dev_man_detail_close'])
                    printFP('INFO - Error message:' + msg)
                    return Global.FAIL, 'TEST FAIL - ' + msg
            except:
                pass
        else:
            GetElement(Global.driver, By.CLASS_NAME, 'glyphicon-remove-circle').click()
        time.sleep(2)
        if save:
            siteLocation = GetSite(formdetails['Site name*'])
        else:
            siteLocation = GetSite(site)

        RightClickElement(siteLocation)
        printFP("Verifying Values --- Save was {}" .format(save))
        count = 0

        SelectFromMenu(Global.driver, By.CLASS_NAME, 'pull-left', 'Edit')
        form = GetElement(Global.driver, By.CLASS_NAME, 'modal-content')
        textboxes = GetElements(form, By.CLASS_NAME, 'form-group')
        for x in textboxes:
            label = x.find_element_by_css_selector('label.col-xs-4.col-sm-4.control-label.text-left.font-weight-normal.ng-binding')
            if not label.text == 'Override GPS':
                if label.text == 'Description':
                    box = GetElement(x, By.TAG_NAME, 'textarea')
                else:
                    box = GetElement(x, By.TAG_NAME, 'input')
                if save:
                    if not box.get_attribute('value') == formdetails[label.text]:
                        ClickButton(Global.driver, By.CSS_SELECTOR, 'a.glyphicon.glyphicon-remove-circle.close-icon')
                        testComment = "Edited Site values do not match the Site Input File"
                        printFP(testComment)
                        return Global.FAIL, testComment
                else:
                    if not box.get_attribute('value') == dictVals[label.text]:
                        ClickButton(Global.driver, By.CSS_SELECTOR, 'a.glyphicon.glyphicon-remove-circle.close-icon')
                        testComment = "Edited Site values do not match the Site Input File"
                        printFP(testComment)
                        return Global.FAIL, testComment
        ClickButton(Global.driver, By.CSS_SELECTOR, 'a.glyphicon.glyphicon-remove-circle.close-icon')
        return Global.PASS, ''
