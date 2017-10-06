import Global
import time
import shutil
import os.path
import os
import glob
import fnmatch
import sys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Utilities_Ample import *


def SpawnBrowser(browser, platform):
    if browser == 'chrome':
        desired = DesiredCapabilities.CHROME.copy()
        desired['platform'] = platform
        print('desired: %s' % desired)
        driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', desired_capabilities=desired)
        session_id = driver.session_id # To get current Session ID
        print('session_id : %s' %session_id)
        driver.session_id = '39f272cf-2d6b-4f96-aa30-beb44055ce6b' # To connect with your desirable session

    elif browser == 'firefox':
        desired = DesiredCapabilities.FIREFOX.copy()
        desired['platform'] = platform
        print('desired: %s' % desired)
        driver = webdriver.Firefox()
    elif 'internet explorer' in browser:
        desired = DesiredCapabilities.INTERNETEXPLORER.copy()
        desired['platform'] = platform
        desired['nativeEvents'] = True
        desired['pageLoadStrategy'] = "eager"
        desired['enablePersistentHover'] = False
        desired['requireWindowFocus'] = False
        desired['IE_ENSURE_CLEAN_SESSION'] = True
        print('desired: %s' % desired)
        if '11' in browser:
            # driver = webdriver.Remote(command_executor='http://10.16.56.154:5555/wd/hub', desired_capabilities=desired)
            driver = webdriver.Remote(command_executor='http://172.20.3.50:5555/wd/hub', desired_capabilities=desired)
        elif '10' in browser:
            driver = webdriver.Remote(command_executor='http://172.20.3.49:5555/wd/hub', desired_capabilities=desired)
    return driver

def CreateSubMTF(mtf_file_path, browsers, platforms):
    with open(mtf_file_path, 'r') as infile:
        header = infile.readline()
        for platform in platforms:
            for browser in browsers:
                if browser == 'internet explorer' and platform == 'linux':
                    pass
                else:
                    with open('/tmp/MTF_%s_%s.csv' % (browser, platform), 'w') as subMTF:
                        subMTF.write(header)
                        subMTF.write(infile.readline())

def MergeTestReports(config, connections):
    """Merge the test reports for each platform/browser combination
    into one test report to email out."""
    with open('%s/test_report.csv' % config['test_report_path'], 'w') as outfile:
        outfile.write('Testbed: %s \nAmple version: %s \nSGW build version: %s \n' % (connections['url'], config['ample_build'], config['sgw_build']))
        for platform in connections['platforms']:
            for browser in connections['browsers']:
                if browser == 'internet explorer' and platform == 'linux':
                    pass
                else:
                    with open('%s/test_report_%s_%s.csv' % (config['test_report_path'], browser[:2], platform[:2]), 'r') as infile:
                        sub_report = infile.read()
                        outfile.write(sub_report)

def MergeTestReportsMultipleUsers(config, connections):
    """Merge the test reports for each platform/browser combination
    into one test report to email out."""

    currentTime = time.time()

    time.sleep(1)

    with open('%s/multipleusers/reports/test_report_%s.csv' % (config['tmp_file_path'], currentTime), 'w') as outfile1:
        outfile1.write('Testbed: %s \nAmple version: %s\n' % (connections['url'], config['ample_build']))
        for platform in connections['platforms']:
            for browser in connections['browsers']:
                if browser == 'internet explorer' and platform == 'linux':
                    pass
                else:
                    with open('%s/test_report_%s_%s.csv' % (config['test_report_path'], browser[:2], platform[:2]), 'r') as infile1:
                        sub_report = infile1.read()
                        outfile1.write(sub_report)

def PrettyParam(param):
    if type(param) == dict:
        line = '{'
        for arg in param:
            line += '%s = %s; ' % (arg, PrettyParam(param[arg]))
        line += '}'
        return line
    elif type(param) == list:
        line = '['
        for arg in param:
            line += '%s; ' % PrettyParam(arg)
        line += ']'
        return line
    elif type(param) == str:
        return param
    elif type(param) == int or type(param) == float:
        return str(param)
    elif type(param) == bool:
        if param:
            return 'True'
        else:
            return 'False'
    else:
        return str(param)

def FormatParams(dictParams):
    """Returns the arguments for the tests as a neatly formatted string
    to write to the test report."""

    if len(dictParams) == 0:
        return 'None'
    params = ''

    # format params so that it has at most 3 params per line
    # otherwise, it will jump to next line
    i = 0
    for key in dictParams:
        i += 1
        params += '%s=%s;  ' % (key, PrettyParam(dictParams[key]))
    return params

def StartSims(inputfp):
    # Get parameters for simulators
    simFP = SkipCommentLine(inputfp)
    nDevices = int(SkipCommentLine(inputfp))
    pathToSimulators = SkipCommentLine(inputfp)

    currentDirectory = os.getcwd()
    os.chdir(pathToSimulators)
    os.system('python simlauncher.py %s %d\r' % (simFP, nDevices))
    time.sleep(3)
    cmd = 'mv %s/MTF.csv /tmp/MTF.csv' % pathToSimulators
    printFP(cmd)
    os.system(cmd)

def GenerateXPATHDictionary(xpath_file_path):
    # open xpath dictionary
    with open(xpath_file_path, 'r') as infile:
        for line in infile:
            pair = line.strip('\n').split(' ')
            Global.xpaths[pair[0]] = pair[1]


def CreateDeviceDictionary(info):
    # Generate dictionary for each simulator
    devDataDic = {}
    devDataDic['region'] = info[0]
    devDataDic['substation'] = info[1]
    devDataDic['feeder'] = info[2]
    devDataDic['site'] = info[3]
    devDataDic['phase'] = info[4]
    devDataDic['serial'] = info[5]
    devDataDic['product'] = info[6]
    devDataDic['swversion'] = info[7]
    devDataDic['platform'] = info[8]
    if not info[9] or info[9] is None or not info[10] or info[10] is None:
        devDataDic['lon'] = info[9]
        devDataDic['lat'] = info[10]
    else:
        devDataDic['lon'] = float(info[9])
        devDataDic['lat'] = float(info[10])
    devDataDic['mac'] = info[11]
    devDataDic['ipaddr'] = info[12]
    devDataDic['dnpaddr'] = int(info[13])
    devDataDic['description'] = info[14]
    devDataDic['daport'] = int(info[15])
    devDataDic['commserver'] = info[16]
    devDataDic['sei'] = info[17]
    devDataDic['networktype'] = info[19]
    devDataDic['networkgroupname'] = info[20]
    devDataDic['devicestate'] = info[21]

    return devDataDic

def DeviceDictionaryForPreSetUp(info, device):
    if device == 'device_1':
        prefix = 'd1_'
    elif device == 'device_2':
        prefix = 'd2_'
    elif device == 'lm_devicename':
        prefix = 'lm_device_'
    # Generate dictionary for each simulator
    devDataDic = {}
    devDataDic[prefix + 'region'] = str(info[0])
    devDataDic[prefix + 'sub'] = str(info[1])
    devDataDic[prefix + 'feeder'] = str(info[2])
    devDataDic[prefix + 'site'] = str(info[3])
    devDataDic[prefix + 'phase'] = str(info[4])
    devDataDic[prefix + 'name'] = str(info[5])
    devDataDic[prefix + 'type'] = str(info[6])
    devDataDic[prefix + 'swversion'] = str(info[7])
    devDataDic[prefix + 'platform'] = str(info[8])
    devDataDic[prefix + 'long'] = str(info[9])
    devDataDic[prefix + 'lat'] = str(info[10])
    devDataDic[prefix + 'macaddress'] = str(info[11])
    devDataDic[prefix + 'ipaddress'] = str(info[12])
    devDataDic[prefix + 'dnpaddr'] = str(info[13])
    devDataDic[prefix + 'description'] = str(info[14])
    devDataDic[prefix + 'daport'] = str(info[15])
    devDataDic[prefix + 'commservername'] = str(info[16])
    devDataDic[prefix + 'sei'] = str(info[17])
    devDataDic[prefix + 'networktype'] = str(info[19])
    devDataDic[prefix + 'networkgroupname'] = str(info[20])

    return devDataDic

def CreateAllDevicesDictionary(devData):
    for line in devData:
        info = line.strip('\n').split(',')
        serial = info[5]
        Global.offDevs.append(serial) # append the simID

        # Generate dictionary for each simulator
        devDataDic = CreateDeviceDictionary(info)

        # Generate dictionary of devID:deviceDic
        Global.devices[serial] = devDataDic

def TakeScreenshot():
    currenttime = time.strftime("%b_%d_%Y__%H_%M_%S")
    Global.driver.save_screenshot('%s/%s_%s.png' %(Global.screenshotsPath, Global.currentmethod_name, currenttime))
    time.sleep(2)

def BackupScreenshotsAndTestReport(src):
    if os.path.exists(src):
        src_level_down = os.path.split(src)[0]
        testreport_list = glob.glob(src_level_down + '/backup/testreport_*')
        testlog_list = glob.glob(src_level_down + '/backup/ample_*')
        dir_list = glob.glob(src_level_down + '/backup/screenshots_*')
        for path in dir_list:
            if os.path.isdir(path):
                shutil.rmtree(path)
        for file in testreport_list:
                os.remove(file)
        for logfile in testlog_list:
                os.remove(logfile)
        currenttime = time.strftime("%b_%d_%Y__%H_%M_%S")
        time.strftime('%H:%M:%s')
        dest = src_level_down + '/backup/screenshots_' + currenttime

        try:
            shutil.copytree(src, dest)
            if 'test_report.csv' in os.listdir(src_level_down + '/report'):
                shutil.copy(src_level_down + '/report/test_report.csv', src_level_down + '/backup/testreport_' + currenttime + '.csv')
        # Directories are the same
        except shutil.Error as e:
            print('Consolidated test report is not copied. Error: %s' % e)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('Consolidated test report is not copied. Error: %s' % e)

        try:
            if 'test_report_ch_li.csv' in os.listdir(src_level_down + '/report'):
                shutil.copy(src_level_down + '/report/test_report_ch_li.csv', src_level_down + '/backup/testreport_ch_li_' + currenttime + '.csv')
            if 'ample_ch_li.log' in os.listdir(src_level_down + '/log'):
                shutil.copy(src_level_down + '/log/ample_ch_li.log', src_level_down + '/backup/ample_ch_li_' + currenttime + '.log')
        # Directories are the same
        except shutil.Error as e:
            print('chrome test report is not copied. Error: %s' % e)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('chrome test report is not copied. Error: %s' % e)

        try:
            if 'test_report_in_WI.csv' in os.listdir(src_level_down + '/report'):
                shutil.copy(src_level_down + '/report/test_report_in_WI.csv', src_level_down + '/backup/testreport_in_WI_' + currenttime + '.csv')
            if 'ample_in_WI.log' in os.listdir(src_level_down + '/log'):
                shutil.copy(src_level_down + '/log/ample_in_WI.log', src_level_down + '/backup/ample_in_WI_' + currenttime + '.log')
        # Directories are the same
        except shutil.Error as e:
            print('Internet Explorer test report is not copied. Error: %s' % e)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('Internet Explorer test report is not copied. Error: %s' % e)

        for logfile in os.listdir(src_level_down + '/log'):
            logfilepath = os.path.join(src_level_down + '/log/', logfile)
            os.remove(logfilepath)

        for filename in os.listdir(src):   # Cleaning up old screenshots from screenshots folder
            filepath = os.path.join(src, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)
    else:
        print('Not found given screenshot path directory to back up screenshots : %s' % src)

def FindAndReplace(directory, find, replace, filePattern):
    if 'Utilities_Framework.py' in filePattern or 'connections.json' in filePattern or 'configurations.json' in filePattern:
        filepath = os.path.join(directory, filePattern)
        #print(filepath)
        time.sleep(2)
        with open(filepath) as f:
            s = f.read()
        #print('find: %s' %find)
        time.sleep(3)
        #print('replace: %s' %replace)
        time.sleep(3)
        s = s.replace(find, replace)
        with open(filepath, "w") as f:
            f.write(s)
    else:
        for path, dirs, files in os.walk(os.path.abspath(directory)):
            for filename in fnmatch.filter(files, filePattern):
                filepath = os.path.join(path, filename)
                #print(filepath)
                if 'maininputfile' not in filepath and 'Point' not in filepath and 'non_ascii' not in filepath and 'zip' not in filepath and 'tar' not in filepath:
                    with open(filepath) as f:
                        s = f.read()
                    #print('find: %s' %find)
                    #print('replace: %s' %replace)
                    s = s.replace(find, replace)
                    with open(filepath, "w") as f:
                        f.write(s)

def InitialDirectorySetup(src):
    if os.path.exists(src):
        dirname = os.path.split(src)[1]
        dir_list = glob.glob(src + '_*')
        for path in dir_list:
            if os.path.isdir(path):
                shutil.rmtree(path)
        currenttime = time.strftime("%b_%d_%Y__%H_%M_%S")
        time.strftime('%H:%M:%s')
        dest = src + '_' + currenttime
        newdirname_level_down = os.path.split(dest)[0]
        newdirname = os.path.split(dest)[1]
        try:
            shutil.copytree(src, dest)
        # Directories are the same
        except shutil.Error as e:
            print('Consolidated test report is not copied. Error: %s' % e)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('Consolidated test report is not copied. Error: %s' % e)
        filePath = dest + '/maininputfile.json'
        with open(filePath) as f:
            s = f.read()
        s = s.replace('fp/' + dirname, 'fp/' + newdirname)
        with open(filePath, "w") as f:
            f.write(s)

        return filePath
    else:
        print('Not found given input path to duplicate input directory : %s' % src)

def FilePathAndInputDataSetup(userdefinedvariables, directory):
    if directory == 'none':
        directory = userdefinedvariables['seleniumDir'] + '/' + userdefinedvariables['inputfilesDir'] + '/'
    for key, value in userdefinedvariables.items():
        if not key == 'guidance' and not key == 'devices' and not key == 'browser_name' and not key == 'platform_name' and not key == 'email_recipients' and not key == '172.20.3.50':
            FindAndReplace(directory, key, value, "*")
        elif key == 'browser_name':
            for i in range(len(userdefinedvariables['browser_name'])):
                if i==0:
                    tmpvalue = '"' + userdefinedvariables['browser_name'][i] + '",'
                else:
                    tmpvalue = value + '"' + userdefinedvariables['browser_name'][i] + '",'
                value = tmpvalue
            newvalue = value[:-1]
            FindAndReplace(directory, key, newvalue, "connections.json")
        elif key == 'platform_name':
            for i in range(len(userdefinedvariables['platform_name'])):
                if i==0:
                    tmpvalue = '"' + userdefinedvariables['platform_name'][i] + '",'
                else:
                    tmpvalue = value + '"' + userdefinedvariables['platform_name'][i] + '",'
                value = tmpvalue
            newvalue = value[:-1]
            FindAndReplace(directory, key, newvalue, "connections.json")
        elif key == 'email_recipients':
            for i in range(len(userdefinedvariables['email_recipients'])):
                if i==0:
                    tmpvalue = '"' + userdefinedvariables['email_recipients'][i] + '",'
                else:
                    tmpvalue = value + '"' + userdefinedvariables['email_recipients'][i] + '",'
                value = tmpvalue
            newvalue = value[:-1]
            FindAndReplace(directory, key, newvalue, "configurations.json")
        elif key == '172.20.3.50':
            directory = userdefinedvariables['seleniumDir']
            FindAndReplace(directory, key, value, "Utilities_Framework.py")
