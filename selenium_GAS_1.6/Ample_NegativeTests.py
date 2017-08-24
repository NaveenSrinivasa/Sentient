import pexpect
import time
import datetime
from Utilities_Ample import *
from Utilities_Framework import *
from Ample_DevMan import *

def RestartSGWduringConfig(sgw_ip=None, comm_server=None, input_file_path=None, device_names=None, config=None):
    sshChild = pexpect.spawn('/bin/bash\r')
    sshChild.send('ssh ampleadmin@' + sgw_ip + '\r')
    try:
        sshChild.expect('Are you sure you want to continue connecting (yes/no)?', timeout=30)
        sshChild.send(sshChild, 'yes\r')
    except:
        pass

    try:
        sshChild.expect('password', timeout=30)
        sshChild.send('ampacity\r')
    except:
        sshChild.close()
        testComment = 'Test could not SSH into Sensor Gateway machine of the device.'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    try:
        result, message = configureDevice(input_file_path, device_names, config, False, False)
    except:
        testComment = "Exception error when attempting to configure Device"
        printFP('INFO - ' + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment

    if result == Global.FAIL:
        testComment = 'Test failed at configuring the device. Test is ending SSH to testbed and ending test.'
        printFP("INFO - " + testComment)
        return Global.FAIL, 'TEST FAIL - ' + testComment
    else:
        time.sleep(5)
        sshChild.send('sudo service ' + comm_server + ' restart\r')
        try:
            sshChild.expect('password', timeout=30)
            sshChild.send('ampacity\r')
            sshChild.expect('Starting Jetty: OK', timeout=60)
        except:
            sshChild.close()
            testComment = 'Test could not restart the comm server specified.'
            printFP("INFO - " + testComment)
            return Global.FAIL, 'TEST FAIL - ' + testComment
        sshChild.close()
        testComment = 'Test successfully restarted the SGW while configuring'
        printFP("INFO - " + testComment)
        return Global.PASS, 'TEST PASS - ' + testComment
