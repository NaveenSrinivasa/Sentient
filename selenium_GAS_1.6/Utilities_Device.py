import pexpect
import time
import Global
from Utilities_Ample import *

def SendSSHCommand(child, cmd):
    printFP('SSH command: %s' % cmd)
    child.send(cmd)

def FlashUnitFromSSD(ipAddress, pathToRSAKey, targetVersion, portNumber, networkType):
    child, connect = SpawnSSHConnection(ipAddress, pathToRSAKey, portNumber, networkType)
    if not connect:
        printFP('Failed to connect')
        child.close()
        return False

    SendSSHCommand(child, 'mount -rw -t vfat /dev/mmcblk0p1 /media/mmc1\r')
    time.sleep(5)
    SendSSHCommand(child, 'ls /media/mmc1\r')
    try:
        child.expect(targetVersion, timeout=180)
    except:
        printFP('INFO - %s image is not on the ssd. Ending Flash.' % targetVersion)
        child.close()
        return False
    time.sleep(3)

    SendSSHCommand(child, 'cp /media/mmc1/%s/* /media/mmc1\r' % targetVersion)
    time.sleep(10)

    SendSSHCommand(child, 'fw_setenv bootcmd "setenv loaddev 2; run fkernel; run froot; env default -f bootcmd; saveenv; reset;"\r')
    time.sleep(2)
    SendSSHCommand(child, 'reboot\r')
    try:
        child.expect('Connection to %s closed.' % ipAddress, timeout=600)
        printFP('Device rebooted')
    except:
        printFP('Device did not reboot')
    child.close()
    return True

def SpawnSSHConnection(ipAddress, pathToRSAKey, portNumber, networkType):
    sshChild = pexpect.spawn('/bin/bash\r')
    sshChild.logfile = open('ssh.log', 'w')
    
    if networkType == 'SSN':
        SendSSHCommand(sshChild, 'ssh-keygen -f ~/.ssh/known_hosts -R [127.0.0.1]:%s\r' % (portNumber))
        SendSSHCommand(sshChild, 'ssh -i %s -p %s root@127.0.0.1\r' % (pathToRSAKey, portNumber))
    elif networkType == '4G':
        SendSSHCommand(sshChild, 'ssh-keygen -f ~/.ssh/known_hosts -R %s\r' % ipAddress)
        SendSSHCommand(sshChild, 'ssh -i %s root@%s\r' % (pathToRSAKey, ipAddress))
    else:
        printFP('Given device network type is not in the defined list')
        return sshChild, False

    try:
        sshChild.expect('Are you sure you want to continue connecting (yes/no)?', timeout=60)
    except:
        return sshChild, False

    SendSSHCommand(sshChild, 'yes\r')
    try:
        sshChild.expect('Warning:', timeout=60)
    except:
        printFP("Got Warning.")
        return sshChild, False

    printFP('INFO - Connected to %s' % ipAddress)
    return sshChild, True


def CheckIfFlashComplete(ipAddress, pathToRSAKey, expectedVersion, portNumber, networkType):
    i = 0
    while i < 1200:
        print 'Waiting for flash to complete . . .'
        Global.driver.refresh()
        time.sleep(120)
        child, canConnect = SpawnSSHConnection(ipAddress, pathToRSAKey, portNumber, networkType)
        if canConnect:
            break
        else:
            printFP('Flash is not complete yet')
        i += 180
    SendSSHCommand(child, 'cat /etc/sentient-release\r')
    time.sleep(2)
    try:
        printFP('Expect: %s' % expectedVersion)
        child.expect(expectedVersion)
        printFP('Flash complete: %s' % expectedVersion)
        return True
    except:
        printFP('Flash failed')
        printFP(child.before)
        printFP('After: %s' % child.after)
        return False
