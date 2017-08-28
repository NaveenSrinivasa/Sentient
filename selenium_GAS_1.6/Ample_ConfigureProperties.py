import random
from Utilities_Ample import *


def ResetDefaults():
    pass


def FillOutPageGeneral(Level=None, tab=None, tabDictionary=None, generalInput=None):
    if tab != 'comPropertyGeneralData':
        inputElement = GetElement(Global.driver, By.XPATH, "//span[@tooltip='comm.server.names']/../../span[2]/input")
        ClearInput(inputElement)
        inputElement.send_keys(generalInput[0])

        inputElement = GetElement(Global.driver, By.XPATH, "//span[@tooltip='default.platforms']/../../span[2]/input")
        ClearInput(inputElement)
        inputElement.send_keys(generalInput[1])

        inputElement = GetElement(Global.driver, By.XPATH, "//span[@tooltip='default.product.types']/../../span[2]/input")
        ClearInput(inputElement)
        inputElement.send_keys(generalInput[2])
    try:
        if 'active' in GetElement(Global.driver, By.ID, tab).get_attribute('class'):
            pass
        else:
            GetElement(Global.driver, By.ID, tab).click()
    except:
        printFP("INFO - Test could not locate tab %s." % tab)
        return Global.FAIL, 'TEST FAIL - Test could not locate tab %s.' % tab

    fieldIDs = tabDictionary.keys()
    for i in range(len(fieldIDs)):
        print fieldIDs[i]
        inputElement = GetElement(Global.driver, By.XPATH, "//span[@tooltip='" + fieldIDs[i] + "']/../../span[2]/input")
        ClearInput(inputElement)
        if fieldIDs[i] in ['comm.server.names', 'default.platforms', 'default.product.types', 'default.health.status.points', 'default.unsolicited.exception.points']:
            if Level == 0 or Level == 4:
                inputElement.send_keys("Adssadasadsa")
            else:
                inputElement.send_keys(tabDictionary[fieldIDs[i]][0])
        else:
            if Level == 0:
                inputElement.send_keys(str(int(tabDictionary[fieldIDs[i]][0]) - 1))
            elif Level == 1:
                inputElement.send_keys(str(int(tabDictionary[fieldIDs[i]][0])))
            elif Level == 2:
                value = random.randint(tabDictionary[fieldIDs[i]][0] + 1, tabDictionary[fieldIDs[i]][1] - 1)
                inputElement.send_keys(str(value))
            elif Level == 3:
                inputElement.send_keys(str(int(tabDictionary[fieldIDs[i]][1])))
            elif Level == 4:
                inputElement.send_keys(str(int(tabDictionary[fieldIDs[i]][1]) + 1))
    time.sleep(15)
    GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Save')]").click()

    result = Global.PASS
    if Level in [0, 4]:
        try:
            msg = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-dismissable alert-danger']/div/span").text
            if tab != 'comPropertyLttpData':
                for n in range(len(fieldIDs)):
                    if fieldIDs[n] in msg:
                        printFP("INFO - Test found key %s within error message." % fieldIDs[n])
                    else:
                        printFP("INFO - Test did not find key %s within the error message. ")
            else:
                printFP("Message - %s" % msg)
                if 'Please correct the errors on the form.' in msg:
                    printFP("INFO - Test correctly displays error alert.")
                else:
                    result = Global.FAIL
                    printFP("INFO - Test did not correctly display error alert.")

                for n in range(len(fieldIDs)):
                    inputElement = GetElement(Global.driver, By.XPATH, "//span[@tooltip='" + fieldIDs[n] + "']/../../span[2]/input")
                    if not ('field-error' in inputElement.get_attribute('class')):
                        result = Global.FAIL
                        printFP("INFO - Input field for %s did not have error." % fieldIDs[n])
                    else:
                        printFP("INFO - Input field for %s did have error." % fieldIDs[n])

        except:
            printFP("INFO - Test did not return an error message.")
            return False
    else:
        pass

    if result == Global.PASS:
        return True
    else:
        return False


def ConfigurePropertiesTest(range_json_file=None):
    if not (range_json_file):
        printFP("INFO - Test is missing mandatory parameter(s).")
        return Global.FAIL, 'TEST FAIL - Test is missing mandatory paramter(s).'

    params = ParseJsonInputFile(range_json_file)
    tabs = ["comPropertyGeneralData", "comPropertyLttpData", "comPropertyOtapData", "comPropertyDnp3Data", "comPropertyLogIData"]

    generalInputs = [params["comPropertyGeneralData"]["comm.server.names"], params["comPropertyGeneralData"]["default.platforms"], params["comPropertyGeneralData"]["default.product.types"]]

    for x in range(5):
        if x in [1, 2, 3]:
            continue
        for i in range(len(tabs)):
            GoToConfigProp()
            if not FillOutPageGeneral(x, tabs[i], params[tabs[i]], generalInputs):
                printFP("INFO - Test ran into an issue. Please refer to logfile to see where test failed.")
                return Global.FAIL, 'TEST FAIL - Test ran into an issue. Please refer to logfile to see where test failed.'
            Global.driver.refresh()

    ResetDefaults()

    return Global.PASS, ''


def ConfigurePropertiesEmptyTest():
    tabs = ["comPropertyGeneralData", "comPropertyLttpData", "comPropertyOtapData", "comPropertyDnp3Data", "comPropertyLogIData"]
    result = Global.PASS
    for i in range(len(tabs)):
        GoToConfigProp()
        try:
            if 'active' in GetElement(Global.driver, By.ID, tabs[i]).get_attribute('class'):
                pass
        except:
            GetElement(Global.driver, By.ID, tabs[i]).click()

        inputElements = GetElements(Global.driver, By.XPATH, "//input[contains(@class,'form-control') and contains(@class, 'ng-touched')]")
        for j in range(len(inputElements)):
            ClearInput(inputElements[j])
        GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Save')]").click()

        try:
            msg = GetElement(Global.driver, By.XPATH, "//div[@class='alert ng-isolate-scope alert-dismissable alert-danger']/div/span").text
            if 'error' in msg:
                printFP("INFO - Test displayed valid error message.")
            else:
                printFP("INFO - Test did not display an error message.")
        except:
            printFP("INFO - Test did not return a error message.")
            result = Global.FAIL

        inputElements = GetElements(Global.driver, By.XPATH, "//input[contains(@class,'form-control') and contains(@class, 'ng-touched')]")
        for n in range(len(inputElements)):
            if not ('field-error' in inputElements[n].get_attribute('class')):
                printFP("INFO - Test does not have an error with an empty field.")
                result = Global.FAIL

        Global.driver.refresh()

    if result == Global.FAIL:
        testComment = 'Test failed while running this test and certain parts did not display an error.'
    else:
        testComment = 'Test shows that there are errors for empty strings being passed as argument'
    printFP("INFO - " + testComment)
    return result, 'TEST PASS - ' + testComment if result == Global.PASS else ('TEST FAIL - ' + testComment)


def ConfigurePropertiesStringInputs(range_json_file=None):
    pass
