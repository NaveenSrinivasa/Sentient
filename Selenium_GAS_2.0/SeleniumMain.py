import sys
import time
import Global
import json
import traceback
import logging
import os
import datetime
from multiprocessing import Process
import threading
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from Ample_Login import *
from Ample_ManageProfile import *
from Ample_SysAdmin import *
from Ample_DevMan import *

def GenerateXPATHDictionary(xpath_file_path):
    """
        Checks if the XPATH_FILE_PATH is a directory before going through it. If it isn't, then return false and end the process.
        Iterates through each file within xpath and loads it into the xpath dictionary within Global.py
    """
    if os.path.isdir(xpath_file_path):
        for filename in os.listdir(xpath_file_path):
            with open(xpath_file_path + '/' + filename, 'r') as infile:
                for line in infile:
                    pair = line.strip('\n').split(' ')
                    Global.xpaths[pair[0]] = pair[1]
        return True
    else:
        printFP("INFO - The provided xpath folder path is incorrect (%s). Please provide valid file path for the xpath folder." % (xpath_file_path))
        return False

def ReplaceDeviceSGWandNG(devices_folder, config):
    #Only limited to CSV files for devices -- will never replace json file anymore
    if os.path.isdir(devices_folder):
        command = "find devices -type f -exec sed -i '' 's/%s/%s/g' {} \;" %('sensor_gw1_name',config['sensor_gw1_name'])
        os.system(command)
        command = "find devices -type f -exec sed -i '' 's/%s/%s/g' {} \;" %('sensor_gw2_name',config['sensor_gw2_name'])
        os.system(command)
        command = "find devices -type f -exec sed -i '' 's/%s/%s/g' {} \;" %('networkgroup1_name',config['networkgroup1_name'])
        os.system(command)
        command = "find devices -type f -exec sed -i '' 's/%s/%s/g' {} \;" %('networkgroup2_name',config['networkgroup2_name'])
        os.system(command)
        return True
    else:
        printFP("INFO - %s is not a directory. Please provide a proper directory for the device CSV files.")
        return False

def UndoReplaceSGWandNG(devices_folder, config):
    #Only limited to CSV files for devices -- will never replace json file anymore
    if os.path.isdir(devices_folder):
        command = "find ./devices/*.csv -type f -exec sed -i '' 's/%s/%s/g' {} \;" %(config['sensor_gw1_name'],'sensor_gw1_name')
        os.system(command)
        command = "find ./devices/*.csv -type f -exec sed -i '' 's/%s/%s/g' {} \;" %(config['sensor_gw2_name'],'sensor_gw2_name')
        os.system(command)
        command = "find ./devices/*.csv -type f -exec sed -i '' 's/%s/%s/g' {} \;" %(config['networkgroup1_name'],'networkgroup1_name')
        os.system(command)
        command = "find ./devices/*.csv -type f -exec sed -i '' 's/%s/%s/g' {} \;" %(config['networkgroup2_name'],'networkgroup2_name')
        os.system(command)
        return True
    else:
        printFP("INFO - %s is not a directory. Please provide a proper directory for the device CSV files.")
        return False

def SpawnBrowser(platform, browser, ip):
    if browser == 'chrome':
        desired = DesiredCapabilities.CHROME
        desired['platform'] = platform
    elif 'internet explorer' in browser:
        desired = DesiredCapabilities.INTERNETEXPLORER
        desired['platform'] = platform
        desired['nativeEvents'] = True
        desired['enablePersistentHover'] = False
        desired['requireWindowFocus'] = True
        desired['ie.ensureCleanSession'] = True

    #pass it the IP of the machine that the Selenium Browser instance is running on
    driver = webdriver.Remote(command_executor=('http://%s/wd/hub'%(ip)), desired_capabilities=desired)
    
    return driver

def ConfigureLoggingAndTestReport(log_location, report_location, testResourcePath, deviceFolder):
    log_file = log_location+'/ample_%s.log'%((datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")))
    logging.basicConfig(filename=log_file, level=logging.INFO, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    Global.reportPath = report_location + '/test_report_%s.csv' %((datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))) 
    Global.testResourcePath = testResourcePath
    Global.deviceFolderPath = deviceFolder

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
        printFP('INFO - This is a positive test case')
    else:
        printFP('INFO - This is a negative test case')

    try:
        result, testComment = globals()[method_name](**args)
    except:
        printFP(str(traceback.print_exc()))
        testComment = 'Exception in test. May cause other tests to fail. Continuing . . .'
        printFP('INFO - ' + testComment)
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
            else:
                result = RunTest(submodule_test, report)

    Global.driver.close()
    Global.driver.quit()

def StartTests(config):
    #Open the configuration file and find where the test files are located
    with open(config['seleniumDir'] + config['inputfilesDir'] + config['testfile'], 'r') as testfile:
        testfile = json.load(testfile)

    with open(Global.reportPath, 'w+') as report:
        report.write('Hip Test Name, Test Case Type, Time in seconds, Result, Test Comment if any\n')

    startTime = time.time()
    for module in testfile['Tests']:
        if not(module['skip']):
            p = threading.Thread(target=RunModules, args=(module, config['platform_name'], config['browser_name'], Global.reportPath, config['selenium_ip']))
            p.start()
            p.join()

        time.sleep(5)
        
    # finalize the test report
    totalTime = time.time() - startTime
    with open(Global.reportPath, 'r') as report:
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

    with open(Global.reportPath, 'a') as report:
        report.write('\n\nTotal Test Time: %d seconds\n' % totalTime)
        report.write('Total Test Count: %d\n' % (count_TOTAL))
        report.write('Total PASS: %d (%f%%)\n' % (count_PASS, (count_PASS/(count_TOTAL*1.0)*100)))
        report.write('Total FAIL: %d (%f%%)\n' % (count_FAIL, (count_FAIL/(count_TOTAL*1.0)*100)))
        report.write('Total EXCEPTION: %d (%f%%)\n\n' % (count_EXCEPTION, (count_EXCEPTION/(count_TOTAL*1.0)*100)))
        report.write('--------------------------------------\n\n')

def Prerequisite(config):
    if not (os.path.exists(config) and os.path.isfile(config)):
        return False

    with open(config, 'r') as userjson:
        parsed_json = json.load(userjson)
        config_path = parsed_json['config_info']
        if not (os.path.isdir(config_path['seleniumDir'] + '/xpaths') and os.path.isfile(config_path['seleniumDir'] + '/xpaths' + '/xpaths')):
            return False
        """
        Below statements Checks if logs and reports folder exists, if it does not-
        it will create both the folders. 
        """
        if not os.path.exists(config_path['seleniumDir'] + config_path['log_location']):
            os.makedirs(config_path['seleniumDir'] + config_path['log_location'])
        
        if not os.path.exists(config_path['seleniumDir'] + config_path['report_location']):
            os.makedirs(config_path['seleniumDir'] + config_path['report_location'])

        return parsed_json

def main():
    if len(sys.argv) == 2:
        """
        checks for xpath directory and file,
        if it is does not exist,script wont continue further since it is a mandatory directory..
        """
        return_value = Prerequisite(sys.argv[1])
        if return_value == False:
            printFP("Xpath directory/file doesn't exist which is mandatory, hence terminated.")
            #Returns nothing and Exit main function
            return 0
        '''with open(sys.argv[1], 'r') as user_defined_json:
            parsed_userdefinedtmp = json.load(user_defined_json)
            config = parsed_userdefinedtmp['user_defined']

        #Configure the logging to write into the location given by seleniumDir+log_folder_location
        ConfigureLoggingAndTestReport(config['seleniumDir']+config['log_location'], config['seleniumDir']+config['report_location'], config['seleniumDir']+config['inputfilesDir'], config['seleniumDir']+config['devices_folder'])

        #Replace Sensor Gateway and Network Group keywords with actual names inside the CSV files
        if not(ReplaceDeviceSGWandNG(config['seleniumDir'] + config['devices_folder'], config)):
            printFP("INFO - Did not successfully replace Sensor Gateway Names and/or Network Group Names in device CSV files.")
            return 0

        if not(GenerateXPATHDictionary(config['seleniumDir']+'/xpaths')):
            printFP("INFO - Improper XPATHS Folder path given. XPATHS Path: %s" %(config['seleniumDir']+'/xpaths'))
            return 0

        #Starts the Tests
        StartTests(config)

        #Replace SGW and Network Group names within the CSV files with Sensor Gateway and Network Group keywords
        if not(UndoReplaceSGWandNG(config['seleniumDir'] + config['devices_folder'], config)):
            printFP("INFO - Did not successfully replace Sensor Gateway Names and/or Network Group Names back to keywords in device CSV files.")
            return 0
    else:
        print 'Missing input file'
        print 'Not enough arguments.'
        print 'python SeleniumMain.py [maininputfile.json]'''

if __name__ == '__main__':
    main()