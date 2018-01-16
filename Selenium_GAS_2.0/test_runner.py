"""
Test runner to ease hiptest integration
"""
import hiptest

class PublishTest:
    def __init__(self, result, method_name, hip_publisher, amplebuild, sgwbuild, browser):
        self.result = result
        self.method_name = method_name
        self.hip_publisher = hip_publisher
        self.amplebuild = amplebuild
        self.sgwbuild = sgwbuild
        self.browser = browser
        self.publish_result()

    def publish_result(self):
        print('Test Result: {}'.format(self.result.result.upper()))
        if self.hip_publisher == None:
            return
        if self.result.comment == None:
            comment = 'Ample_build: {}\nSGW_build: {}Browser: {}\n'.format(self.amplebuild, self.sgwbuild, self.browser)
        else:
            comment = 'Ample_build: {}\nSGW_build: {}\nBrowser: {}\nSelenium Comment: {}'.format(
                self.amplebuild, self.sgwbuild, self.browser, self.result.comment
            )
        if not self.method_name in self.hip_publisher.id_pairs:
            print('Test name not found on HipTest. Not publishing.')
            return
        test_id = self.hip_publisher.id_pairs[self.method_name]
        print('Succefully found Test name: {} and Test Id: {} on HipTest. So publishing the result.'.format(self.method_name, test_id))
        self.hip_publisher.add_test_result(
            test_id=test_id,
            result=self.result.result,
            result_author='Selenium Automation',
            comment=comment
        )

class TestRunner:
    def __init__(self, hiptest_config):
        self.config = hiptest_config
        self.connections = self.config['Ample Testbed Parameters']['ampleIP']
        self.amplebuild = self.config['Ample Testbed Parameters']['ample_build_version']
        self.sgwbuild = self.config['Ample Testbed Parameters']['sgw_build_version']
        self.browser = self.config['Selenium Config Parameters']['browser_name']
        self._start_hip_publisher()
        self._get_id_pairs()

    def _start_hip_publisher(self):
        print('INFO - Connecting to HipTest')
        self.hip_publisher = hiptest.HipTest(
            email = self.config['HipTest Parameters']['hiptest_account_email'],
            password = self.config['HipTest Parameters']['hiptest_account_password']
        )
        self.hip_publisher.set_project_id(self.config['HipTest Parameters']['hiptest_project_id'])
        self.hip_publisher.set_test_run_id(self.config['HipTest Parameters']['hiptest_test_run_id'])

    def _get_id_pairs(self):
        """pairs of scenario_id:test_id"""

        if self.hip_publisher == None:
            print("INFO - No HipTest Publisher was generated to use.")
            return
        print('Generating id pairs')
        self.hip_publisher.generate_test_id_pairs()

    def run_publishresult(self, result, method_name):
        PublishTest(
            result,
            method_name,
            self.hip_publisher,
            self.amplebuild,
            self.sgwbuild,
            self.browser
        )

class Result:
    def __init__(self, result, comment=None):
        self.result = result
        self.comment = comment