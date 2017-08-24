import Global
from Utilities_Ample import *
import re
from bs4 import BeautifulSoup as soup
import pdb
from pdb import set_trace as bp
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import calendar
import time
from datetime import date, datetime, timedelta


def FaultEventsDebug(input_file_path):

    printFP('Test Methods Debug')

    params = ParseJsonInputFile(input_file_path)

    region = params['Region']
    substation = params['Substation']
    feeder = params['Feeder']
    site = params['Site']

    GoToLineMon()
    GoToLineMonFaultEvents()

    #get = GetSubstationFromTop(region, substation)
    #get = GetFeederFromTop(region, substation, feeder)
    get = GetSiteFromTop(region, substation, feeder, site)
    #get = GetRegionFromTop(region)
    pagename = 'line-monitoring'
    time.sleep(5)
    if get:
        #print 'title'
        #title =  FaultEventsGroupTableGetTitle(pagename)
        #print 'roworder'
        #roworder = FaultEventsGroupTableGetRowOrder(pagename)
        #print 'columnorder'
        #columnorder = FaultEventsGroupTableGetColumnOrder(pagename)
        #print 'FilteredData'
        #FilteredData = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', 'Total Event Count')
        #FilteredData = FaultEventsGroupTableFilteredData(pagename, 'SUSTAINED', 'Total Duration(minutes)')
        #FilteredData = FaultEventsGroupTableFilteredData(pagename, 'MOMENTARY', 'Total Event Count')
        #FilteredData = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', 'Total Event Count')
        #FilteredData = FaultEventsGroupTableFilteredData(pagename, 'ACTIVE', 'Total Duration(minutes)')
        #print 'columnorder'
        #columnorder = FaultEventsGroupTableGetColumnOrder(pagename)
        #UnCheckAllEventTypes()
        #SelectAllEventStates()
        #SelectAllEventTypes()
        #time.sleep(20)
        #SelectEventType('Interruption Without Fault')
        #print 'FilteredData'
        #FilteredData = FaultEventsTableFilteredAllData(pagename, 'Event Type')
        #print 'FilteredSpecificData'
        #FilteredData, Count = FaultEventsTableFilteredSpecificData(pagename, 'Event Type', 'Interruption Without Fault')
        #print 'FilteredData'
        #FilteredData = FaultEventsGroupViewTableFilteredAllData(pagename, 'Event Type')
        #print 'FilteredSpecificData'
        #FilteredData, Count = FaultEventsGroupViewTableFilteredSpecificData(pagename, 'Event Type', 'Fault Without Interruption')
        #cloumnorder = FaultEventsRegionTableGetColumnOrder(pagename)
        #print 'cloumnorder : %s' % cloumnorder
        #print 'FilteredData'
        #FilteredData = FaultEventsRegionTableFilteredAllData(pagename, 'Fault Without Interruptions')
        #print 'substationelement'
        #substationname = FaultEventsFindSubstationWithFaults(pagename, 'Fault Without Interruptions')
        #substations = GetElements(Global.driver, By.CLASS_NAME, 'alink')
        '''for substation in substations:
            filtername = substation.text.strip()
            if filtername in substationname:
                substation.click()
        time.sleep(15)'''
        '''print 'SelectAllEventType'
        selectalleventtype = SelectAllEventTypes()
        print selectalleventtype
        print 'UnselectAllEventTypes'
        status = UnselectAllEventTypes()
        print status
        print 'UnCheckAllEventTypes'
        status = UnCheckAllEventTypes()
        print status
        print 'SelectEventType'
        status = SelectEventType('Sustained Interruption')
        print status
        print 'SelectEventType'
        status = SelectEventType('Interruption Without Fault')
        print status
        print 'UnselectEventType'
        status = UnselectEventType('Interruption Without Fault')
        print status
        print 'UnselectEventType'
        status = UnselectEventType('Sustained Interruption')
        print status
        print 'SelectAllEventStates'
        status = SelectAllEventStates()
        print status
        print 'UnselectAllEventStates'
        status = UnselectAllEventStates()
        print status
        print 'UnCheckAllEventStates'
        status = UnCheckAllEventStates()
        print status
        print 'SelectEventState'
        status = SelectEventState('Active')
        print status
        print 'SelectEventState'
        status = SelectEventState('Cleared')
        print status
        print 'UnselectEventState'
        status = UnselectEventState('Active')
        print status
        print 'UnselectEventState'
        status = UnselectEventState('Cleared')
        print status'''
        print 'SelectAllTriggeredDetectors'
        status = SelectAllTriggeredDetectors()
        print status
        print 'UnselectAllTriggeredDetectors'
        status = UnselectAllTriggeredDetectors()
        print status
        print 'SelectTriggeredDetector'
        status = SelectTriggeredDetector('Threshold')
        print status
        print 'SelectTriggeredDetector'
        status = SelectTriggeredDetector('DiDt')
        print status
        print 'UnselectTriggeredDetector'
        status = UnselectTriggeredDetector('Threshold')
        print status
        print 'UnselectTriggeredDetector'
        status = UnselectTriggeredDetector('DiDt')
        print 'SelectAllTriggeredDetectors'
        status = SelectAllTriggeredDetectors()
        print status
        print 'UnCheckAllTriggeredDetectors'
        status = UnCheckAllTriggeredDetectors()
        print status
        print status
        testComment = 'Test Pass'
        printFP(testComment)
        return Global.PASS, testComment
    else:
        testComment = 'Test Fail - Unable to locate Given Feeder "%s"' %feeder
        printFP(testComment)
        return Global.FAIL, testComment