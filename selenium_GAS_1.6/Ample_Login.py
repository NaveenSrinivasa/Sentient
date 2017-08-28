# TEST_AmpleLogin.py
import Global
from Utilities_Ample import *



def Login(username, password):
    # Login Test -- takes arguments of string username and password to try to login to
    # Every new test module must begin with a valid Login combination and end with a Logout
    try:
        # wait for the page to refresh
        inputElement = GetElement(Global.driver, By.ID, 'j_username')
        printFP(Global.driver.title)
    except:
        testComment = 'Did not reach login page'
        printFP(testComment)
        return Global.FAIL, testComment

    # find the username field and enter a username
    SendKeys(inputElement, username)
    # inputElement.send_keys(usrname)

    # fine the password field and enter the password
    inputElement = GetElement(Global.driver, By.ID, 'j_password')
    SendKeys(inputElement, password)

    inputElement.submit()

    if WaitForTitle('dashboard'):
        printFP('INFO - Reached dashboard')
        return Global.PASS, 'TEST PASS - Successfully Logged In'
    else:
        testComment = 'Timed out trying to login'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


def Logout():
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['dash_person_dropdown'])
    time.sleep(2)
    ClickButton(Global.driver, By.XPATH, xpaths['dash_person_logout'])
    time.sleep(15)
    try:
        WebDriverWait(Global.driver, 15).until(EC.visibility_of_element_located((By.ID, "j_username")))
        printFP('INFO - Logout success!')
        return Global.PASS, 'TEST PASS - Logout success.'
    except:
        testComment = 'Test could not logout'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


def ChangePassword(old_password, new_password):
    # Navigate to change password
    ClickButton(Global.driver, By.XPATH, xpaths['dash_person_dropdown'])
    time.sleep(1)

    ClickButton(Global.driver, By.XPATH, xpaths['dash_person_change_pw'])
    time.sleep(1)

    inputElement = GetElement(Global.driver, By.ID, 'oldPassword')
    SendKeys(inputElement, old_password)
    inputElement = GetElement(Global.driver, By.ID, 'newPassword')
    SendKeys(inputElement, new_password)
    inputElement = GetElement(Global.driver, By.ID, 'confirmPassword')
    SendKeys(inputElement, new_password)
    ClickButton(Global.driver, By.XPATH, xpaths['dash_change_pw_update'])
    time.sleep(6)               # changed from 2 to 5 because of current IE testing
    ClickButton(Global.driver, By.XPATH, xpaths['change_pw_close'])

    if WaitForTitle('login'):
        printFP('INFO - Returned to login page')
        return Global.PASS, 'TEST PASS - Returned to login page'
    else:
        testComment = 'Failed to return to login page'
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
