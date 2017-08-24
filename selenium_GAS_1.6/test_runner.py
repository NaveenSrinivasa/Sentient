"""
Test runner to ease hiptest integration
"""

import json
import logging
import os
#import socket
import hiptest
from Utilities_Ample import printFP

#import settings
#import test_constants as tc
#from test_result import *
#from Utilities import printFP
#import mm3_tests
#import zm1_tests

class PublishTest:
    def __init__(self, result, test_name, hip_publisher, amplebuild, sgwbuild, browser):
        self.result = result
        self.test_name = test_name
        self.hip_publisher = hip_publisher
        self.amplebuild = amplebuild
        self.sgwbuild = sgwbuild
        self.browser = browser
        self.publish_result()

    def run_tests(self):
        printFP('Running tests')
        for test in self.tests:
            continue_test = self.run_test(test)
            if not continue_test:
                break

    def run_test(self, test):
        if test['test_name'] == 'End':
            return False
        if test['skip']:
            printFP('Skipping {}'.format(test['test_name']))
            return True

        running_msg = 'Running {}'.format(test['test_name'])
        left_border = '~ '*6
        right_border = ' ~'*6
        printFP(left_border+running_msg+right_border)
        if self.module.lower() == 'zm1':
            test_to_run = getattr(zm1_tests, test['test_name'])
        elif self.module.lower() == 'mm3':
            test_to_run = getattr(mm3_tests, test['test_name'])
        result = test_to_run(**test['args'])
        self.publish_result(result, test['test_name'])
        self.write_result(result, test['test_name'])
        return True

    def write_result(self, result, test_name):
        with open(self.test_report_path, 'w') as report:
            if result.comment == None:
                comment = ''
            else:
                comment = result.comment
            report.write('{},{},{}\n'.format(
                test_name, result.result.upper(), comment)
            )

    def publish_result(self):
        printFP('Test Result: {}'.format(self.result.result.upper()))
        if self.hip_publisher == None:
            return
        if self.result.comment == None:
            comment = 'Ample_build: {}\nSGW_build: {}Browser: {}\n'.format(self.amplebuild, self.sgwbuild, self.browser)
        else:
            comment = 'Ample_build: {}\nSGW_build: {}\nBrowser: {}\nSelenium Comment: {}'.format(
                self.amplebuild, self.sgwbuild, self.browser, self.result.comment
            )
        if not self.test_name in self.hip_publisher.id_pairs:
            printFP('Test name not found on HipTest. Not publishing.')
            return
        test_id = self.hip_publisher.id_pairs[self.test_name]
        printFP('Succefully found Test name: {} and Test Id: {} on HipTest. So publishing the result.'.format(self.test_name, test_id))
        self.hip_publisher.add_test_result(
            test_id=test_id,
            result=self.result.result,
            result_author='Selenium Automation',
            comment=comment
        )


class TestRunner:
    def __init__(self, config, connections, browser):
        self.config = config
        self.connections = connections
        self.amplebuild = self.config['ample_build']
        self.sgwbuild = self.config['sgw_build']
        self.browser = browser
        #self._parse_test_files(test_files)
        #self._configure_logging()
        #self._configure_host()
        self._start_hip_publisher(self.config['hiptest'])
        self._get_id_pairs()

    '''def _parse_config(self, config_file):
        with open(config_file, 'r') as config_json:
            self.config = json.load(config_json)

    def _parse_connections(self, connections_file):
        with open(connections_file, 'r') as connections_json:
            self.connections = json.load(connections_json)
        settings.connections = self.connections

    def _parse_test_files(self, test_files):
        self.tests = []
        for test_file in test_files:
            with open(test_file, 'r') as test_json:
                testset = json.load(test_json)
                self.tests.append(testset)'''

    def _configure_logging(self):
        log_path = self.config['log_path']
        os.system('sudo rm {}/*log'.format(log_path))
        configured_log_level = self.config['log_level'].lower()
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
        logging.basicConfig(
            filename='{}/full.log'.format(log_path),
            level=log_level,
            filemode='w',
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    '''def _configure_host(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',1))
        user_ip_addr = s.getsockname()[0]
        s.close()
        settings.connections['user_ip_address'] = user_ip_addr'''

    def _start_hip_publisher(self, hiptest_config):
        if not hiptest_config['publish']:
            self.hip_publisher = None
            printFP('HipTest publishing disabled')
            return
        printFP('Connecting to HipTest')
        self.hip_publisher = hiptest.HipTest(
            email = hiptest_config['email'],
            password = hiptest_config['password']
        )
        self.hip_publisher.set_project_id(hiptest_config['project_id'])
        self.hip_publisher.set_test_run_id(hiptest_config['test_run_id'])

    def _get_id_pairs(self):
        """pairs of scenario_id:test_id"""

        if self.hip_publisher == None:
            return
        printFP('Generating id pairs')
        self.hip_publisher.generate_test_id_pairs()

    def run_publishresult(self, result, test_name):
        PublishTest(
            result,
            test_name,
            self.hip_publisher,
            self.amplebuild,
            self.sgwbuild,
            self.browser
        )

class Result:
    def __init__(self, result, comment=None):
        self.result = result
        self.comment = comment