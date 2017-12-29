import sys
import time
import Global
import json
import traceback
import logging
import os
import datetime
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from Ample_Login import *

def GenerateXPATHDictionary(xpath_file_path):
    # open xpath dictionary
    with open(xpath_file_path, 'r') as infile:
        for line in infile:
            pair = line.strip('\n').split(' ')
            Global.xpaths[pair[0]] = pair[1]

def ReplaceDeviceSGWandNG(devices_folder):
    #Only limited to CSV files for devices -- will never replace json file anymore
    pass

def SpawnBrowser(platform, browser, ip):
    if browser == 'chrome':
        desired = DesiredCapabilities.CHROME
        desired['platform'] = platform
    elif 'internet explorer' in browser:
        desired = DesiredCapabilities.INTERNETEXPLORER
        desired['platform'] = platform
        desired['nativeEvents'] = True
        desired['enablePersistentHover'] = False
        desired['pageLoadStrategy'] = "eager"
        #desired['ie.usePerProcessProxy'] = True
        desired['requireWindowFocus'] = False
        desired['ie.ensureCleanSession'] = True

    #pass it the IP of the machine that the Selenium Browser instance is running on
    driver = webdriver.Remote(command_executor=('http://%s/wd/hub'%(ip)), desired_capabilities=desired)
    
    return driver

def ConfigureLogging(log_location, log_level):
    configured_log_level = log_level
    Global.loglevel = configured_log_level
    if configured_log_level == 'debug':
        log_level = logging.DEBUG
    elif configured_log_level == 'info':
        log_level = logging.INFO
    elif configured_log_level == 'warning':
        log_level = logging.WARNING
    elif configured_log_level == 'error':
        log_level = logging.ERROR
    elif configured_log_level == 'critical':
        log_level = logging.CRITICAL
    else:
        log_level = logging.DEBUG
    log_f = log_location+'/ample_%s.log'%((datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")))
    logging.basicConfig(filename=log_f, level=log_level, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def RunTest(test, report):
    method_name = test['method_name']
    expect_pass = test['expect_pass']
    hiptest_name = test['hiptest_name']
    del test['method_name']
    del test['skip']
    del test['expect_pass']
    del test['hiptest_name']
    try:
        del test['comment']
    except:
        pass
    args = test

    # call each test
    testStartTime = time.time()
    printFP('\n%s - Test case: %s' % (time.strftime('%H:%M:%s'), hiptest_name))
    if expect_pass:
        printFP('This is a positive test case')
    else:
        printFP('This is a negative test case')

    try:
        result, testComment = globals()[method_name](**args)
    except:
        printFP(str(traceback.print_exc()))
        testComment = 'Exception in test. May cause other tests to fail. Continuing . . .'
        printFP(testComment)
        result = Global.EXCEPTION

    testElapsedTime = time.time() - testStartTime

    # test report handling is at the Main level
    # individual tests do not need to touch the test report
    # write the test result
    if hiptest_name:
        if result == Global.PASS and expect_pass:
            finaltestresult = Global.PASS
            report.write('%s, expect_pass = %s, %d, PASS, %s\n' % (hiptest_name, expect_pass, testElapsedTime, testComment))
        elif result == Global.FAIL and not expect_pass:
            finaltestresult = Global.PASS
            report.write('%s, expect_pass = %s, %d, PASS, %s\n' % (hiptest_name, expect_pass, testElapsedTime, testComment))
        elif result == Global.PASS and not expect_pass:
            finaltestresult = Global.FAIL
            report.write('%s, expect_pass = %s, %d, FAIL, %s\n' % (hiptest_name, expect_pass, testElapsedTime, testComment))
        elif result == Global.FAIL and expect_pass:
            finaltestresult = Global.FAIL
            report.write('%s, expect_pass = %s, %d, FAIL, %s\n' % (hiptest_name, expect_pass, testElapsedTime, testComment))
        elif result == Global.EXCEPTION:
            report.write('%s, expect_pass = %s, %d, EXCEPTION, %s\n' % (hiptest_name, expect_pass, testElapsedTime, testComment))
    return result

def RunModules(module, platform, browser, file, selenium_ip):

    running_msg = 'Running Module : {}'.format(module['Module'])
    left_border = '~ '*6
    right_border = ' ~'*6
    printFP(left_border+running_msg+right_border)

    #Spawn a new browser to run the test
    Global.driver = SpawnBrowser(platform, browser, selenium_ip)
    Global.driver.maximize_window()
    Global.driver.get('https://172.20.4.40/amplemanage/login')
    if (Global.driver.desired_capabilities['browserName'] == 'internet explorer'):
        Global.driver.get("javascript:document.getElementById('overridelink').click();")

    # Write subheader for each test
    with open(file, 'a') as report:
        report.write('\n\nModule: %s\n\n' % module['Module'])
        with open(module['test_json'], 'r') as submodule_json:
            parsed_submodule = json.load(submodule_json)
        for submodule_test in parsed_submodule['Tests']:
            if submodule_test['skip']:
                continue
            if submodule_test['hiptest_name']:
                expect_pass = submodule_test['expect_pass']
                result = RunTest(submodule_test, report)

    Global.driver.close()
    Global.driver.quit()

def StartTests(config):
    #Open the configuration file and find where the test files are located
    with open(config['seleniumDir']+config['inputfilesDir']+config['testfile'], 'r') as testfile:
        testfile = json.load(testfile)

    with open('test_report.csv', 'w+') as report:
        report.write('Test Case, Hip Test Name, Test Case Type, Time in seconds, Result, Test Comment if any\n')

    startTime = time.time()
    for module in testfile['Tests']:
        if not(module['skip']):
            p = Process(target=RunModules, args=(module, 'MAC', 'chrome', 'test_report.csv', config['selenium_ip']))
            p.start()
            p.join()

        time.sleep(5)
        
    # finalize the test report
    totalTime = time.time() - startTime
    with open('test_report.csv', 'r') as report:
        count_PASS = 0
        count_FAIL = 0
        count_EXCEPTION = 0
        count_TOTAL = 0
        for line in report:
            if 'PASS' in line:
                count_PASS += 1
            elif 'FAIL' in line:
                count_FAIL += 1
            elif 'EXCEPTION' in line:
                count_EXCEPTION += 1

        count_TOTAL = count_PASS+count_FAIL+count_EXCEPTION

    with open('test_report.csv', 'a') as report:
        report.write('\n\nTotal Test Time: %d seconds\n' % totalTime)
        report.write('Total Test Count: %d\n' % (count_TOTAL))
        report.write('Total PASS: %d (%f%%)\n' % (count_PASS, (count_PASS/(count_TOTAL*1.0)*100)))
        report.write('Total FAIL: %d (%f%%)\n' % (count_FAIL, (count_FAIL/(count_TOTAL*1.0)*100)))
        report.write('Total EXCEPTION: %d (%f%%)\n\n' % (count_EXCEPTION, (count_EXCEPTION/(count_TOTAL*1.0)*100)))
        report.write('--------------------------------------\n\n')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as user_defined_json:
            parsed_userdefinedtmp = json.load(user_defined_json)
            config = parsed_userdefinedtmp['user_defined']

        ConfigureLogging(config['seleniumDir']+config['log_location'], config['loglevel'])
        StartTests(config)
    else:
        print 'Missing input file'
        print 'Not enough arguments.'
        print 'python SeleniumMain.py [maininputfile.json]'

