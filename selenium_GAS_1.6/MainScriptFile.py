import sys
import time
import Global
import json
import traceback
import logging
import os
import shutil
import test_constants as tc
from test_runner import TestRunner
from test_runner import PublishTest
from test_runner import Result
from multiprocessing import Process
from Utilities_Ample import *
from Utilities_Framework import *
from Ample_Login import *
from Ample_DevMan import *
from Ample_LineMon import *
from Ample_UserMan import *
from Ample_SysAdmin import *
from Ample_ManageProfile import *
from Ample_GroupTree import *
from Ample_CurrentJobs import *
from Ample_AlertNotifications import *
from Ample_Disturbances import *
from Ample_NegativeTests import *
from Ample_ConfigureProperties import *
from Ample_SysAdmin_MTF_0 import *
from Ample_SysAdmin_MTF_1 import *
from testdebug import *
from Ample_DevMan_ManageDevices import *
from Ample_LinMon_LogI import *




def Sleep(sleep_time):
    printFP('sleeping for %d seconds' % sleep_time)
    elapsed = 0
    while elapsed < sleep_time:
        time.sleep(180)
        Global.driver.refresh()
        elapsed += 180
    return Global.PASS, ''


def ConfigureLogging(parsed_config, browser, platform):
    configured_log_level = parsed_config['log_level'].lower()
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
    log_location = '%sample_%s_%s.log' % (parsed_config['log_path'], browser[:2], platform[:2])
    logging.basicConfig(filename=log_location, level=log_level, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def RunTest(test, report, test_runner):
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
    printFP('\n%s - Test #%d: %s - hiptest scenario name: %s' % (time.strftime('%H:%M:%s'), Global.testCount, method_name, hiptest_name))
    if expect_pass:
        printFP('Positive test case')
    else:
        printFP('Negative test case')
    Global.currentmethod_name = method_name
    try:
        result, testComment = globals()[method_name](**args)
    except:
        printFP(str(traceback.print_exc()))
        testComment = 'Exception in test. May cause other tests to fail. Continuing . . .'
        printFP(testComment)
        result = Global.FAIL
        hipresult = tc.FAILED
        hiptestresults = Result(hipresult, testComment)

    testElapsedTime = time.time() - testStartTime

    # test report handling is at the Main level
    # individual tests do not need to touch the test report
    # write the test result
    if hiptest_name:
        if result == Global.PASS and expect_pass:
            finaltestresult = Global.PASS
            Global.totalPass += 1
            report.write('%d %s, %s, expect_pass = %s, %d, PASS, %s\n' % (Global.testCount, method_name, FormatParams(args), expect_pass, testElapsedTime, testComment))
        elif result == Global.FAIL and not expect_pass:
            finaltestresult = Global.PASS
            Global.totalPass += 1
            report.write('%d %s, %s, expect_pass = %s, %d, PASS, %s\n' % (Global.testCount, method_name, FormatParams(args), expect_pass, testElapsedTime, testComment))
        elif result == Global.PASS and not expect_pass:
            finaltestresult = Global.FAIL
            Global.totalFail += 1
            TakeScreenshot()
            report.write('%d %s, %s, expect_pass = %s, %d, FAIL, %s\n' % (Global.testCount, method_name, FormatParams(args), expect_pass, testElapsedTime, testComment))
        elif result == Global.FAIL and expect_pass:
            finaltestresult = Global.FAIL
            Global.totalFail += 1
            TakeScreenshot()
            report.write('%d %s, %s, expect_pass = %s, %d, FAIL, %s\n' % (Global.testCount, method_name, FormatParams(args), expect_pass, testElapsedTime, testComment))

        if finaltestresult == Global.PASS:
                hipresult = tc.PASSED
        elif finaltestresult == Global.FAIL:
                hipresult = tc.FAILED
        hiptestresults = Result(hipresult, testComment)
        name = hiptest_name.lower()
        hiptest_name = '_'.join(name.split()).replace('-','')
        test_runner.run_publishresult(hiptestresults, hiptest_name)
    return result


def RunTests(tests, platform, browser, config, url, count, test_runner):
    GenerateXPATHDictionary(config['xpath_file_path'])
    # Create new webdriver
    Global.driver = SpawnBrowser(browser, platform)
    Global.driver.maximize_window()

    # Go to Ample
    print Global.driver
    Global.driver.get('https://%s/amplemanage/login' % url)
    if (Global.driver.desired_capabilities['browserName'] == 'internet explorer'):
        time.sleep(2)
        Global.driver.get("javascript:document.getElementById('overridelink').click();")

    ConfigureLogging(config, browser, platform)

    # Configure devices
    Global.mtfPath = '/tmp/MTF_%s_%s.csv' % (browser, platform)
    with open(Global.mtfPath, 'r') as mtfData:
        mtfData.readline()
        devData = mtfData.readlines()
    CreateAllDevicesDictionary(devData)

    # Run tests
    startTime = time.time()
    with open('%s/test_report_%s_%s.csv' % (config['test_report_path'], browser[:2], platform[:2]), 'w') as report:
        # Write subheader for each test
        report.write('Browser: %s\nPlatform: %s\n\n' % (browser, platform))
        report.write('Test Case, Parameters, Test Case Type, Time in seconds, Result, Test Comment if any\n')

        # run the tests
        for test in tests:
            if test == 'End_Test':
                break
            if test['skip']:
                # Skip tests with skip flag set to true
                continue

            # Two modes: module-wise and test-wise
            # Module mode will assume that the tests are in a different
            #  file. It will open the testfile (should be in test-wise
            #  format) and run the tests one by one.
            # Test-wise mode will assume the test is in the main test file
            #  and calls the test directly.
            # Both modes can be mixed in one file.
            if 'Module' in test:
                #printFP(test['Module'])
                running_msg = 'Running Module : {}'.format(test['Module'])
                left_border = '~ '*6
                right_border = ' ~'*6
                printFP(left_border+running_msg+right_border)
                report.write('\nModule: %s\n\n' % test['Module'])
                with open(test['test_json'], 'r') as submodule_json:
                    parsed_submodule = json.load(submodule_json)
                for submodule_test in parsed_submodule['Tests']:
                    if submodule_test['skip']:
                        continue
                    if submodule_test['hiptest_name']:
                        Global.testCount += 1
                    expect_pass = submodule_test['expect_pass']
                    result = RunTest(submodule_test, report, test_runner)
            else:
                if test['hiptest_name']:
                    Global.testCount += 1
                expect_pass = test['expect_pass']
                result = RunTest(test, report, test_runner)

        # finalize the test report
        totalTime = time.time() - startTime
        report.write('\n\nTotal Test Time: %d seconds\n' % totalTime)
        report.write('Total Test Count: %d\n' % Global.testCount)
        report.write('Total PASS: %d\n' % Global.totalPass)
        report.write('Total FAIL: %d\n\n' % Global.totalFail)
        report.write('--------------------------------------\n\n')
    Global.driver.close()
    Global.driver.quit()


def TestConfig(config, connections, tests):
    """Set up the ample tests, then run the test for each browser/platform
    combination in separate asynchronous threads. Afterwards, email
    the test report to recipients."""

    count = 0
    CreateSubMTF(config['mtf_file_path'], connections['browsers'], connections['platforms'])
    Global.tmpPath = config['tmp_file_path']
    Global.screenshotsPath = config['screenshots_path']

    BackupScreenshotsAndTestReport(Global.screenshotsPath)   # Back up old screenshots to backup folder

    threads = []
    for platform in connections['platforms']:
        print('Platform: %s' %platform)
        for browser in connections['browsers']:
            print('Browser: %s' %browser)
            if browser == 'internet explorer' and platform == 'linux':
                pass
            else:
                # start test in a separate asynchronous thread
                test_runner = TestRunner(config, connections, browser)
                p = Process(target=RunTests, args=(tests, platform, browser, config, connections['url'], count, test_runner))
                threads.append(p)
                p.start()  # start the test
                count += 1
    for p in threads:
        p.join()  # wait for the tests to finish before continuing

    # merge test report
    MergeTestReports(config, connections)
    # MergeTestReportsMultipleUsers(config, connections)
    # Stop hub and node
    # cmd = 'ps aux | grep java | grep selenium | awk \'{ print $2; }\' | xargs kill'
    # subprocess.call('ps aux | grep java | grep selenium | awk \'{ print $2; }\' | xargs kill', shell=True)


if __name__ == '__main__':
    """Order of events is:
    Main -> TestConfig -> CreateSubMTF -> Create a new sub process ->
    -> RunTests -> MergeTestReports -> Send email -> done"""

    if len(sys.argv) == 2:

        with open(sys.argv[1], 'r') as user_defined_json:
            parsed_userdefinedtmp = json.load(user_defined_json)
            usrdeftmp = parsed_userdefinedtmp['user_defined']

        # To set up inputs for all modules
        inputdir = usrdeftmp['seleniumDir'] + '/' + usrdeftmp['inputfilesDir']
        newinputfilePath = InitialDirectorySetup(inputdir)

        with open(newinputfilePath, 'r') as user_defined_json:
            parsed_userdefined = json.load(user_defined_json)
            usrdef = parsed_userdefined['user_defined']
        FilePathAndInputDataSetup(usrdef, 'none')
        newinputdir = usrdef['seleniumDir'] + '/' + usrdef['inputfilesDir']

        for i in range(len(usrdeftmp['devices'])):
            device = usrdeftmp['devices'][i]
            with open(usrdeftmp['seleniumDir'] + '/' + usrdeftmp['inputfilesDir'] + '/' + usrdeftmp[device] + '.csv', 'r') as mtf:
                mtf.readline()
                info = mtf.readline().strip('\n').split(',')
                devicedict = DeviceDictionaryForPreSetUp(info, device)
            FilePathAndInputDataSetup(devicedict, newinputdir)

        with open(usrdef['seleniumDir'] + '/' + usrdef['inputfilesDir'] + '/configurations.json', 'r') as config_json:
            parsed_config = json.load(config_json)

        #config_file = usrdef['seleniumDir'] + '/' + usrdef['inputfilesDir'] + '/configurations.json'
        open(parsed_config['Config']['log_path'] + 'ample_ch_li.log', "w+").close()
        time.sleep(2)
        open(parsed_config['Config']['log_path'] + 'ample_in_WI.log', "w+").close()
        time.sleep(2)
        # Get test connections
        # In template, there are:seconds
        #  parsed_connections["Connections"] - ample ip address
        with open(usrdef['seleniumDir'] + '/' + usrdef['inputfilesDir'] + '/connections.json', 'r') as connections_json:
            parsed_connections = json.load(connections_json)

        with open(usrdef['seleniumDir'] + '/' + usrdef['inputfilesDir'] + '/all_modules.json', 'r') as test_json:
            # parsed_json = json.load(test_json, object_pairs_hook=OrderedDict)
            parsed_json = json.load(test_json)
            # kick off the test

        TestConfig(parsed_config['Config'], parsed_connections['Connections'], parsed_json['Tests'])
        FindAndReplace(usrdef['seleniumDir'], usrdef['internet_explorer_machine_ip'], 'internet_explorer_machine_ip', "Utilities_Framework.py")
        if parsed_config['Email']['enabled']:
            EmailAttachment(parsed_config['Email']['attachments'], parsed_config['Email']['recipients'], parsed_config['Email']['subject_line'])
    else:
        print('Missing input file')
        print 'Not enough arguments.'
        print 'python MainScriptFile.py [maininputfile.json]'
