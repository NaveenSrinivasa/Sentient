import re
import email
import imaplib
import html2text
from Utilities_Ample import *



def ForgotPassword():
    return Global.PASS, ''


def SubscribeForEmailNotifications(regions=None, substations=None):
    GoToEmailAlert()
    time.sleep(2)
    windowBody = GetElement(Global.driver, By.TAG_NAME, 'notificationtree-view')
    regionOptions = GetElements(windowBody, By.TAG_NAME, 'li')
    for option in regionOptions:
        option.click()
        time.sleep(1)

    if regions:
        for i in range(len(regions)):
            try:
                inputElement = GetElement(Global.driver, By.XPATH, "//span[@title='" + regions[i] + "']/../span[4]/input")
                if not inputElement.is_selected():
                    inputElement.click()
            except:
                testComment = 'Test could not locate Region %s' % regions[i]
                printFP('INFO - ' + testComment)
                return Gllobal.FAIL, 'TEST FAIL - ' + testComment
    time.sleep(5)

    if substations:
        for i in range(len(substations)):
            try:
                inputElement = GetElement(Global.driver, By.XPATH, "//span[@title='" + substations[i] + "']/../span[4]/input")
                if not inputElement.is_selected():
                    inputElement.click()
            except:
                testComment = 'Test could not locate Substation %s' % substations
                printFP('INFO - ' + testComment)
                return Gllobal.FAIL, 'TEST FAIL - ' + testComment
    time.sleep(2)
    GetElement(Global.driver, By.XPATH, "//button[text()='Update']").click()
    time.sleep(2)
    Global.driver.refresh()
    GoToEmailAlert()
    time.sleep(2)
    windowBody = GetElement(Global.driver, By.TAG_NAME, 'notificationtree-view')
    regionOptions = GetElements(windowBody, By.TAG_NAME, 'li')
    for option in regionOptions:
        option.click()
        time.sleep(1)

    result = Global.PASS
    if regions:
        for i in range(len(regions)):
            inputElement = GetElement(Global.driver, By.XPATH, "//span[@title='" + regions[i] + "']/../span[4]/input")
            if not inputElement.is_selected():
                result = Global.FAIL
                printFP("INFO - %s is not selected." % regions[i])
            else:
                printFP("INFO - %s is selected." % regions[i])

    if substations:
        for i in range(len(substations)):
            inputElement = GetElement(Global.driver, By.XPATH, "//span[@title='" + substations[i] + "']/../span[4]/input")
            if not inputElement.is_selected():
                result = Global.FAIL
                printFP("INFO - %s is not selected." % substations[i])
            else:
                printFP("INFO - %s is selected." % substations[i])
    time.sleep(5)

    GetElement(Global.driver, By.CLASS_NAME, "close-icon").click()
    if result == Global.FAIL:
        testComment = 'Test ran into issue while subscribing for email notifications'
    else:
        testComment = 'Test successfully subscribed for email notifications for the given regions and substations'
    printFP("INFO - " + testComment)
    return result, 'TEST PASS - ' + testComment if result == Global.PASS else ('TEST FAIL - ' + testComment)


def CheckEmailforNotification(username=None, password=None, subscribed_regions_json=None):
    if not (username and password and subscribed_regions_json):
        testComment = 'Test is missing mandatory '
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    if 'gmail' in username:
        m = imaplib.IMAP4_SSL("imap.gmail.com")
    elif 'sentient-energy' in username:
        m = imaplib.IMAP4_SSL("outlook.office365.com")
    m.login(username, password)

    m.select("INBOX")   # here you a can choose a mail box like INBOX instead

    resp, items = m.search(None, '(FROM "noreply@sentient-energy.com")')   # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
    items = items[0].split()   # getting the mails id
    result = Global.PASS
    params = ParseJsonInputFile(subscribed_regions_json)
    required_values = [params['Testbed'] + '/amplemanage', 'Timestamp', 'Detector', 'Value']
    total = 0

    for emailid in items:
        resp, data = m.fetch(emailid, "(RFC822)")   # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
        email_body = data[0][1]   # getting the mail content
        mail = email.message_from_string(email_body)   # parsing the mail content to get a mail object

        printFP("[" + mail["From"] + "]: " + mail["Subject"])
        regEx = re.compile('\w+:\w+-\w+\ | \w+ Phase \w+ \| Detector-\w+ \| Timestamp-\w+')
        if not (regEx.match(mail["Subject"])):
            printFP("INFO - Subject does not match the desired format.")
            result = Global.FAIL
        else:
            printFP("INFO - Subject matches the desired format.")

        semiparsedstring = re.split(":|-|\|\s|", mail["Subject"])
        parsedSubject = semiparsedstring[0:3] + semiparsedstring[3].split(" ", 1)

        # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
        for part in mail.walk():
            if part.get_payload(decode=True):
                body = html2text.html2text(part.get_payload(decode=True))

        try:
            for value in required_values:
                if value in body:
                    printFP("INFO - %s is in Email Notification." % ('Link' if required_values.index(value) == 0 else value))
                else:
                    result = Global.FAIL
                    printFP("INFO - %s is not in Email Notification." % ('Link' if required_values.index(value) == 0 else value))

            for i in range(2):
                if params[parsedSubject[0]][parsedSubject[1]][parsedSubject[2]][parsedSubject[3]][parsedSubject[4]][i] in body:
                    printFP("INFO - Value for %s is %s. Notification matches." % (required_values[1 + i], params[parsedSubject[0]][parsedSubject[1]][parsedSubject[2]][parsedSubject[3]][parsedSubject[4]][i]))
                else:
                    result = Global.FAIL
                    printFP("INFO - Value for %s is %s. Notification did not have the correct value.")
            total += 1
        except KeyError:
            printFP("INFO - Found a notification from a region or substation that was not on the JSON file. Notification Subject: %s" % mail["Subject"])
            result = Global.FAIL

    if len(items) == params['Expected Total'] and total == params['Expected Total']:
        printFP("INFO - Total Number of Expected Notifications matches the number of actual Notifications received at this email.")
    else:
        printFP("INFO - Total Number of Expected Notifications does not match the number of actual Notifications received at this email.")
        result = Global.FAIL

    if result == Global.FAIL:
        testComment = 'One or more parts of the test failed. Please refer to log file to determine what the issues were.'
    else:
        testComment = 'All parts of the test passed.'

    printFP("INFO - " + testComment)
    return result, ('TEST PASS - ' + testComment) if result == Global.PASS else ('TEST FAIL - ' + testComment)


def DeleteEmailNotification(username, password):
    try:
        m = imaplib.IMAP4_SSL("imap.gmail.com")
        m.login(username, password)

        m.select("INBOX")   # here you a can choose a mail box like INBOX instead
        # use m.list() to get all the mailboxes

        resp, items = m.search(None, '(FROM "noreply@sentient-energy.com")')   # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
        items = items[0].split()   # getting the mails id
        for emailid in items:
            m.store(emailid, '+FLAGS', '\\Deleted')

        printFP("Test successfully deleted all notifications from email %s" % username)
        return Global.PASS, 'TEST PASS - Test successfully deleted all notifications from email %s' % username
    except:
        testComment = 'Test ran into issues while trying to delete Notifications from email %s' % username
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
