import json
import random
import os
import csv
import pexpect
import sys
import time
import xlrd
from Utilities_Ample import *

FAULT_PRODUCER_PATH = 'fault_producer/'


def GetHeaderNames():
    headerNames = []
    headerElement = GetElement(Global.driver, By.TAG_NAME, 'thead')
    length = len(GetElements(headerElement, By.TAG_NAME, 'th'))
    for i in range(2, length + 1):
        headerNames.append((GetElement(Global.driver, By.XPATH, "//table/thead/tr/th[" + str(i) + "]").text).replace(" Count", ""))
    return headerNames


def VerifyDisturbanceCountersDownload(download_type=None, input_file_path=None, download_folder=None):
    if not(download_type and input_file_path and download_folder):
        testComment = 'Test is missing mandatory parameter(s).'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


    params = ParseJsonInputFile(input_file_path)
    if download_type == 'CSV' or download_type == 'EXCEL':
        path = download_folder + '/export.csv' if download_type == 'CSV' else ('/export.xls')
    else:
        testComment = 'Invalid download type was given to the test.'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    GoToLineMonDisturbances()
    time.sleep(1)
    if not GetLocationFromInput(params['Region'], params['Substation'], params['Feeder'], params['Site']):
        testComment = 'Test could not locate desired Group Tree Location'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    ZoomLevels = ['1D', '1W', '1M', '3M', '6M', '1Y']
    for level in ZoomLevels:
        GetElement(Global.driver, By.XPATH, "//label[text()='"+level+"']").click()
        time.sleep(2)
        if not 'ng-hide' in GetElement(Global.driver, By.XPATH, "//span[contains(text(),'No Data Available')]/..").get_attribute("class"):
            printFP("INFO - Skipping Zoom Level %s because there is no data available." % level)
            continue
        else:
            Headers = GetHeaderNames()

        if download_type == 'CSV':
            GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Export')]").click()
            time.sleep(1)
            GetElement(Global.driver, By.XPATH, "//span[text()='CSV']").click()
            time.sleep(10)
            with open(path) as csvfile:
                next(csvfile)
                reader = csv.DictReader(csvfile)
                if params['Site']:
                    Phase = {'A': '1', 'B' : '2', 'C': '3'}
                for row in reader:
                    if params['Site']:
                        if row['Disturbance Count'] == GetElement(Global.driver, By.XPATH, '//tbody/tr['+Phase[row['Phase']]+']/td['+str(Headers.index(row['Time Period'])+2)+']/span').text:
                            printFP("INFO - Phase %s at Time Period %s matches with value %s."%(row['Phase'], row['Time Period'], row['Disturbance Count']))
                        else:
                            printFP("INFO - Phase %s at Time Period %s does not match.")
                    else:
                        if params['Substation'] or params['Feeder']:
                            if str(row['Phase'] + ' : ' + row['Disturbance Count']) in GetElement(Global.driver, By.XPATH, "//td[contains(text(),'"+row[('Feeder' if params['Feeder'] else 'Substation')]+"')]/../td["+str(Headers.index(row['Time Period'])+2)+"]/span").text:
                                printFP("INFO - %s %s with Phase %s at Time Period %s matches with value %s." % ('Site' if params['Feeder'] else 'Feeder', row[('Feeder' if params['Feeder'] else 'Substation')], row['Phase'] , row['Time Period'], row['Disturbance Count']))
                            else:
                                printFP("INFO - %s %s at Time Period %s does not match" %('Site' if params['Feeder'] else 'Feeder', row[('Feeder' if params['Feeder'] else 'Substation')], row['Time Period']))
                        else:
                            if row['Disturbance Count'] == GetElement(Global.driver, By.XPATH, "//td[contains(text(),'"+row['Region']+"')]/../td["+str(Headers.index(row['Time Period'])+2)+"]/span").text:
                                printFP("INFO - Substation %s at Time Period %s matches with value %s."%(row['Region'], row['Time Period'], row['Disturbance Count']))
                            else:
                                printFP("INFO - Substation %s at Time Period %s does not match." %(row['Region'], row['Time Period']))

            csvfile.close()
        elif download_type == 'EXCEL':
            GetElement(Global.driver, By.XPATH, "//button[contains(text(),'Export')]").click()
            time.sleep(1)
            GetElement(Global.driver, By.XPATH, "//span[text()='EXCEL']").click()
            time.sleep(10)
            workbook = xlrd.open_workbook(path)

            for sheet in workbook.sheets():
                number_of_rows = sheet.nrows
                number_of_cols = sheet.ncols
                if params['Site']:
                    if number_of_cols != 4:
                        printFP("INFO - Excel Sheet does not have 4 columns for site xls sheet.")
                    Phase = {'A': '1', 'B' : '2', 'C': '3'}
                for n in range(1, number_of_rows):
                    if params['Site']:
                        if sheet.cell(n,3).value == GetElement(Global.driver, By.XPATH, '//tbody/tr['+Phase[sheet.cell(n,2).value]+']/td['+str(Headers.index(sheet.cell(n,1).value)+2)+']/span').text:
                            printFP("INFO - Phase %s at Time Period %s matches with value %s."%(sheet.cell(n,2).value, sheet.cell(n,1).value ,sheet.cell(n,3).value))
                        else:
                            printFP("INFO - Phase %s at Time Period %s does not match." %(sheet.cell(n,2).value, sheet.cell(n,1).value))
                    else:
                        if params['Substation'] or params['Feeder']:
                            if str(sheet.cell(n,2).value + ' : ' + sheet.cell(n,3).value) in GetElement(Global.driver, By.XPATH, "//td[contains(text(),'"+sheet.cell(n,0).value+"')]/../td["+str(Headers.index(sheet.cell(n,1).value)+2)+"]/span").text:
                                printFP("INFO - %s %s with Phase %s at Time Period %s matches with value %s." % ('Site' if params['Feeder'] else 'Feeder', sheet.cell(n,0).value, sheet.cell(n,2).value , sheet.cell(n,1).value, sheet.cell(n,3).value))
                            else:
                                printFP("INFO - %s %s at Time Period %s does not match" %('Site' if params['Feeder'] else 'Feeder', sheet.cell(n,0).value, sheet.cell(n,2).value , sheet.cell(n,1).value))
                        else:
                            if sheet.cell(n,2).value == GetElement(Global.driver, By.XPATH, "//td[contains(text(),'"+sheet.cell(n,0).value+"')]/../td["+str(Headers.index(sheet.cell(n,1).value)+2)+"]/span").text:
                                printFP("INFO - Substation %s at Time Period %s matches with value %s."%(sheet.cell(n,0).value, sheet.cell(n,1).value, sheet.cell(n,2).value))
                            else:
                                printFP("INFO - Substation %s at Time Period %s does not match." %(sheet.cell(n,0).value, sheet.cell(n,1).value))
        os.remove(path)

    return Global.PASS, ''

def VerifyDisturbanceCounterCharts(input_file_path):
    return Global.PASS, ''

def GenerateMTFSelenium(sgw_name,group_name,mtf_config):
    printFP("INFO - Generating the MTF file for Disturbance Counts")
    try:
        GenerateMTF(sgw_name,group_name,mtf_config)
        testComment = 'Test was successfully able to generate the MTF file'
        printFP("INFO - " + testComment)
        return Global.PASS, "TEST PASS - " + testComment
    except:
        testComment = 'Test failed to generate the MTF and ran into an exception.'
        printFP("INFO - " + testComment)
        return Global.FAIL, "TEST PASS - " + testComment

def GenerateDisturbancesSelenium(mtf, target):
    printFP("INFO - Generating Disturbances for given MTF file on testbed %s" %target)
    result = True
    try:
        returnval = GenerateDisturbances(mtf, target)
        if returnval == 'Fail' or False:
            result = False
        if result:
            testComment = 'Test successfully generated disturbances for devices on the given MTF file on testbed %s' % target
        else:
            testComment = 'Test did not successfully generate disturbances for devices on the given MTF file on testbed %s' % target
        printFP("INFO - " + testComment)
        return Global.PASS, 'TEST PASS - ' + testComment if result else 'TEST FAIL - ' + testComment
    except:
        testComment = 'Test to generate Disturbances on the devices on the given MTF file failed.'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment


def SSHToAmpleServer(ip_addr):
    print('Connecting to ample')
    ample = pexpect.spawn('ssh ampleadmin@%s' % ip_addr)
    try:
        ample.expect('yes/no', timeout=3)
        ample.sendline('yes')
        try:
            ample.expect('password', timeout=3)
            ample.sendline('ampacity')
        except:
            print('no password')
            return False
    except:
        ample.sendline('ampacity')
    return ample

def GenerateMTF(sgw_name,group_name,mtf_config):
    """Generate the MTF with the correct region/substation/feeder/site
    topology. Run this first and upload the MTF to ample before running
    the disturbances."""

    prefix = 'dist_test_'

    with open(mtf_config, 'r') as infile:
        json_file = infile.read()
    topology = json.loads(json_file)

    header = 'Region,Substation,Feeder,Site,Phase,Serial Number,Product Name,Software Release,Platform,Latitude,Longitude,MAC Address,Sensor IP Address,Sensor DNP Address,Field Notes,DA Port,Comm Server Name,SEI Part Number,Secondary IP Address,Network Type,Network Group Name\n'
    lat = random.randint(-80,80)
    lon = random.randint(-170,170)
    dnp_addr = 65000
    ip_addr_base = 1
    with open(os.path.dirname(mtf_config)+'/dist_test_mtf.csv', 'w') as mtf:
        mtf.write(header)
        for region in topology:
            region_name = prefix+region
            for substation in topology[region]:
                substation_name = prefix+substation
                for feeder in topology[region][substation]:
                    feeder_name = prefix+feeder
                    for site in topology[region][substation][feeder]:
                        site_name = prefix+site
                        lat += 0.1
                        lon += 0.1
                        for phase in topology[region][substation][feeder][site]:
                            serial = 'serial_'+site+phase
                            mtf.write('%s,%s,%s,%s,%s,%s,' % (region_name,
                                                              substation_name,
                                                              feeder_name,
                                                              site_name,
                                                              phase,
                                                              serial))
                            mtf.write('MM3,2.4.2,corgi,%.2f,%.2f,' % (lat,lon))
                            mtf.write('10301%d,10.30.1.%d,%d,,' % (ip_addr_base,
                                                                   ip_addr_base,
                                                                   dnp_addr))
                            mtf.write('20000,%s,dist_test,,SSN,%s\n' % (sgw_name,
                                                                        group_name))
                            dnp_addr += 1
                            ip_addr_base += 1


def CreateSeqFile(mtf, serial,sgw_name):
    seq_name = 'dist_%s.seq' % serial
    with open(os.path.dirname(mtf)+'/'+seq_name, 'w') as seq:
        seq.write('%s   %s\n' % (sgw_name, serial))
        count = random.randint(0,100)
        for sleep_time in [129600,43200,10800,10800,2880,1200,240,240,20]:
            seq.write('DistClass3Counter    %d\n%dm\n' % (count,sleep_time))
            count += random.randint(1,100)
    return seq_name

def GenerateDisturbanceSeqs(mtf):
    """Give it the uploaded mtf so that it can use the data to generate
    disturbance seq files."""

    seq_list = []
    with open(mtf, 'r') as infile:
        infile.readline()
        for line in infile:
            device = line.strip('\n').split(',')
            serial = device[5]
            sgw_name = device[16]
            seq_name = CreateSeqFile(mtf, serial,sgw_name)
            seq_list.append(seq_name)

    return seq_list

def UploadDisturbanceSeqs(mtf, seq_list, target):
    """Upload the given disturbance seq file to Ample to run."""

    for seq in seq_list:
        print('Uploading %s' % seq)
        scp = pexpect.spawn('scp ' + str(os.path.dirname(mtf)) +'/%s ampleadmin@%s:/tmp/.' % (seq, target))
        try:
            scp.expect('yes/no', timeout=3)
            scp.sendline('yes')
        except:
            pass
        try:
            scp.expect('password', timeout=3)
            scp.sendline('ampacity')
        except:
            return False
        try:
            scp.expect('100%', timeout=5)
        except:
            return False
    return True

def RunDisturbanceSeqs(seq_list, target):
    """Runs the list of disturbance sequences.
    Upload and run each or upload all and then run all?"""

    ample = SSHToAmpleServer(target)
    time.sleep(2)
    ample.sendline('cd %s' % FAULT_PRODUCER_PATH)

    ample.sendline('./fault_producer stop_app')
    time.sleep(20)
    ample.sendline('./fault_producer start_app')
    time.sleep(10)
    try:
        ample.expect('ok', timeout=15)
    except:
        print('failed to start fault producer')
        print(ample.before)
        return False
    for seq in seq_list:
        ample.sendline('./fault_producer run_file /tmp/%s' % seq)
        time.sleep(1)
    return True

def GenerateDisturbances(mtf, target):
    seq_list = GenerateDisturbanceSeqs(mtf)
    result = UploadDisturbanceSeqs(mtf, seq_list, target)
    if not result:
        return False
    result = RunDisturbanceSeqs(seq_list, target)
    if result:
        print 'Success'
    else:
        print 'Fail'

def PrintHelp():
    print('python generate_disturbances.py make_mtf [sgw_name] [group_name] topology.json')
    print('python generate_disturbances.py make_dist dist_test_mtf.csv [ample_ip_addr]')

if __name__=='__main__':
    if len(sys.argv) < 4:
        PrintHelp()
    else:
        if sys.argv[1] == 'make_mtf':
            sgw_name = sys.argv[2]
            group_name = sys.argv[3]
            mtf_config = sys.argv[4]
            GenerateMTF(sgw_name, group_name, mtf_config)
        elif sys.argv[1] == 'make_dist':
            mtf = sys.argv[2]
            target = sys.argv[3]
            GenerateDisturbances(mtf, target)
        else:
            PrintHelp()
