import json
import requests

"""
HipTest.get() methods return request objects.
request objects have json string attributes.
These json strings can be converted to Python dictionaries using
    json.loads(json_string)
request objects have the following attributes:
response.header
response.text
response.errors
response.status_code

For automation, the main uses are likely:
h = hiptest.HipTest($YOUR_HIPTEST_EMAIL, $YOUR_HIPTEST_PASSWORD)
h.set_project_id($PROJECT_ID)
h.set_test_run_id($TEST_RUN_ID)
h.add_test_result(test_id=$TEST_ID, result=$RESULT, result_author=$YOUR_NAME, comment=$TEST_COMMENT/BUILD #)
"""

class HipTest:
    def __init__(self, email, password):
        self.credentials = {
            'email': email,
            'password': password
        }
        self.stem = 'https://hiptest.net/api/projects'
        self._get_api_credentials()

    def _get_api_credentials(self):
        url = 'https://hiptest.net/api/auth/sign_in'
        payload = self.credentials
        response = requests.post(url, data=payload)
        payload = response.headers
        self.headers = {
            'Accept': 'application/vnd.api+json; version=1',
            'access-token': payload['access-token'],
            'client': payload['client'],
            'uid': self.credentials['email']
        }

    def _get_request(self, url):
        response = requests.get(url, headers=self.headers)
        return response

    def _post_request(self, url, payload):
        response = requests.post(url, data=json.dumps(payload), headers=self.headers)
        return response

    def set_project_id(self, project_id):
        self.project_id = project_id

    def set_scenario_id(self, scenario_id):
        self.scenario_id = scenario_id

    def set_folder_id(self, folder_id):
        self.folder_id = folder_id

    def set_test_run_id(self, test_run_id):
        self.test_run_id = test_run_id

    def set_test_id(self, test_id):
        self.test_id = test_id

    def get_scenarios(self, project_id=None):
        if project_id == None:
            project_id = self.project_id

        url = '{}/{}/scenarios'.format(
            self.stem, project_id
        )
        return self._get_request(url)

    def get_scenario(self, project_id=None, scenario_id=None):
        if project_id == None:
            project_id = self.project_id
        if scenario_id == None:
            scenario_id = self.scenario_id

        url = '{}/{}/scenarios/{}'.format(
            self.stem, project_id, scenario_id
        )
        return self._get_request(url)

    def get_datatable(self, project_id=None, scenario_id=None):
        if project_id == None:
            project_id = self.project_id
        if scenario_id == None:
            scenario_id = self.scenario_id

        url = '{}/{}/scenarios/{}/datatable'.format(
            self.stem, project_id, scenario_id
        )
        return self._get_request(url)

    def get_folders(self, project_id=None):
        if project_id == None:
            project_id = self.project_id

        url = '{}/{}/folders'.format(
            self.stem, project_id
        )
        return self._get_request(url)

    def get_folder(self, project_id=None, folder_id=None):
        if project_id == None:
            project_id = self.project_id
        if folder_id == None:
            folder_id = self.folder_id

        url = '{}/{}/folders/{}'.format(
            self.stem, project_id, folder_id
        )
        return self._get_request(url)

    def get_folder_children(self, project_id=None, folder_id=None):
        if project_id == None:
            project_id = self.project_id
        if folder_id == None:
            folder_id = self.folder_id

        url = '{}/{}/folders/{}/children'.format(
            self.stem, project_id, folder_id
        )
        return self._get_request(url)

    def get_folder_scenarios(self, project_id=None, folder_id=None):
        if project_id == None:
            project_id = self.project_id
        if folder_id == None:
            folder_id = self.folder_id

        url = '{}/{}/folders/{}/scenarios'.format(
            self.stem, project_id, folder_id
        )
        return self._get_request(url)

    def get_tags(self, project_id=None, scenario_id=None):
        if project_id == None:
            project_id = self.project_id
        if scenario_id == None:
            scenario_id = self.scenario_id

        url = '{}/{}/scenarios/{}/tags'.format(
            self.stem, project_id, scenario_id
        )
        return self._get_request(url)

    def get_test_runs(self, project_id=None):
        if project_id == None:
            project_id = self.project_id

        url = '{}/{}/test_runs'.format(
            self.stem, project_id
        )
        return self._get_request(url)

    def get_test_runs_with_tags(self, project_id=None):
        if project_id == None:
            project_id = self.project_id

        url = '{}/{}/test_runs?include=tags'.format(
            self.stem, project_id
        )
        return self._get_request(url)

    def get_test_run(self, project_id=None, test_run_id=None):
        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id

        url = '{}/{}/test_runs/{}'.format(
            self.stem, project_id, test_run_id
        )
        return self._get_request(url)

    def get_test_run_with_tags(self, project_id=None, test_run_id=None):
        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id

        url = '{}/{}/test_runs/{}?include=tags'.format(
            self.stem, project_id, test_run_id
        )
        return self._get_request(url)

    def get_tests(self, project_id=None, test_run_id=None):
        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id

        url = '{}/{}/test_runs/{}/test_snapshots'.format(
            self.stem, project_id, test_run_id
        )
        return self._get_request(url)

    def get_test(self, project_id=None, test_run_id=None, test_id=None):
        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id
        if test_id == None:
            test_id = self.test_id

        url = '{}/{}/test_runs/{}/test_snapshots/{}'.format(
            self.stem, project_id, test_run_id, test_id
        )
        return self._get_request(url)

    def get_test_with_scenario(self, project_id=None, test_run_id=None, test_id=None):
        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id
        if test_id == None:
            test_id = self.test_id

        url = '{}/{}/test_runs/{}/test_snapshots/{}?include=scenario'.format(
            self.stem, project_id, test_run_id, test_id
        )
        return self._get_request(url)

    def add_test_result(self, project_id=None, test_run_id=None, test_id=None,
            result="undefined", result_author='', comment=''):
        """Valid result codes are: passed, failed, blocked, wip, retest,
        skipped, undefined"""

        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id
        if test_id == None:
            test_id = self.test_id

        url = '{}/{}/test_runs/{}/test_snapshots/{}/test_results'.format(
            self.stem, project_id, test_run_id, test_id
        )
        payload = {
            'data': {
                "type": "test-results",
                "attributes": {
                    "status": result,
                    "status-author": result_author,
                    "description": comment
                }
            }
        }
        return self._post_request(url, payload)

    def update_test_result(self, project_id=None, test_run_id=None,
            test_id=None, test_result_id=None,
            result="undefined", result_author='', comment=''):
        """Valid result codes are: passed, failed, blocked, wip, retest,
        skipped, undefined"""

        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id
        if test_id == None:
            test_id = self.test_id
        if test_result_id == None:
            test_result_id = self.test_result_id

        url = '{}/{}/test_runs/{}/test_snapshots/{}/test_results/{}'.format(
            self.stem, project_id, test_run_id, test_id, test_result_id
        )
        payload = {
            'data': {
                "type": "test-results",
                "attributes": {
                    "status": result,
                    "status-author": result_author,
                    "description": comment
                }
            }
        }
        return self._post_request(url, payload)

    def generate_test_id_pairs(self, project_id=None, test_run_id=None):
        if project_id == None:
            project_id = self.project_id
        if test_run_id == None:
            test_run_id = self.test_run_id

        self.id_pairs = {}
        response = self.get_tests(project_id, test_run_id)
        tests = json.loads(response.text)
        for test in tests['data']:
            test_id = int(test['id'])
            name = test['attributes']['name'].lower()
            test_name = '_'.join(name.split()).replace('-','')
            self.id_pairs[test_name] = test_id
