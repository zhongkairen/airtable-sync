import io
import requests
import zipfile
import os
import re
import json
from datetime import datetime
import asyncio
import argparse
from tqdm import tqdm  # requires `pip install tqdm`

# GITHUB_AIRTABLE_SYNC_READONLY_ACTION_TOKEN = 'some-token'
# GITHUB_AIRTABLE_SYNC_READONLY_ACTION_TOKEN_PATH = '~/.ssh/github.airtable-sync.read-only.actions.pat'
# export GITHUB_AIRTABLE_SYNC_READONLY_ACTION_TOKEN_PATH=~/.ssh/github.airtable-sync.read-only.actions.pat
def parse_args():
    parser = argparse.ArgumentParser(description='Fetch GitHub workflow run history.')
    parser.add_argument('--owner', required=True, help='GitHub repository owner')
    parser.add_argument('--repo', required=True, help='GitHub repository name')
    parser.add_argument('--id', required=True, help='GitHub workflow ID')
    return parser.parse_args()

args = parse_args()
OWNER = args.owner
REPO = args.repo
WORKFLOW_ID = args.id
# OWNER = 'zhongkairen'
# REPO = 'airtable-sync'
# WORKFLOW_ID = '122549153'


class WorkflowRunHistory:
    def __init__(self, action_token_name, gist_token_name):
        action_token = os.environ.get(action_token_name)
        gist_token = os.environ.get(gist_token_name)
        if (action_token and gist_token):
            self.action_token = action_token
            self.gist_token = gist_token
        else:
            raise ValueError(
                f"Token not set from '{action_token_name}', '{gist_token_name}'")

    def do_request(self, url, stream=False):
        if not self.action_token:
            raise ValueError("Token not set")
        headers = {
            'Authorization': f'token {self.action_token}',
            'Accept': 'application/vnd.github.v3+json',
        }

        base_url = f"https://api.github.com/repos/{OWNER}/{REPO}"
        url = f"{base_url}{url}"
        return requests.get(url, headers=headers, stream=stream)

    async def get_workflow_runs(self):
        """Fetch workflow runs"""
        url = f"/actions/workflows/{WORKFLOW_ID}/runs"
        response = self.do_request(url)
        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])
            tasks = []
            run_data = {}

            runs = [run for run in runs if not self._csv.is_in_history(
                run.get('run_number'))]

            if len(runs) == 0:
                print("No new runs to process, first run_number" + self._csv.history[0].run_number)
                return self._csv

            progress_bar = tqdm(
                total=len(runs), desc="Processing", unit="task")

            for run in runs:
                status = run.get('status')
                run_number = run.get('run_number')
                if status != 'completed':
                    print(f"Skipping run {run.get('run_number')} as {status}")
                    continue
                run_id = run.get('id')
                event = run.get('event')
                conclusion = run.get('conclusion')
                started_at = run.get('run_started_at')
                updated_at = run.get('updated_at')
                started_at_dt = datetime.strptime(
                    started_at, '%Y-%m-%dT%H:%M:%SZ')
                updated_at_dt = datetime.strptime(
                    updated_at, '%Y-%m-%dT%H:%M:%SZ')
                duration = (updated_at_dt - started_at_dt).total_seconds()
                run_data[run_id] = {
                    'started_at': started_at,
                    'run_number': run_number,
                    'event': event,
                    'conclusion': conclusion,
                    'duration': duration,
                    'version': None}
                tasks.append(self.fetch_version(run_id, progress_bar))
            versions = await asyncio.gather(*tasks)
            for ver in versions:
                run_id = ver['run_id']
                version = ver['version']
                run_data[run_id]['version'] = version

            sorted_run_data = dict(
                sorted(run_data.items(), key=lambda item: item[1]['run_number'], reverse=True))

            def format_log(d):
                return ",".join([
                    str(d['started_at']),
                    str(d['run_number']),
                    str(d['event']),
                    str(d['conclusion']),
                    f"{int(d['duration'])}s",
                    f"v{d['version']}"
                ])
            logs = [format_log(d) for d in sorted_run_data.values()]

            progress_bar.close()

            history = [HistoryItem(line) for line in logs]
            self._csv.add_to_history(history)
            self._csv.write()
        else:
            print(
                f"Failed to fetch workflow runs: {response.status_code} {response.text}")
        return self._csv

    async def fetch_version(self, run_id, cursor):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_version_in_logs, run_id, cursor)

    def get_version_in_logs(self, run_id, cursor):
        url = f"/actions/runs/{run_id}/logs"
        response = self.do_request(url, stream=True)
        if response.status_code == 200:
            # Use BytesIO to hold the zip in memory
            zip_data = io.BytesIO(response.content)
            cursor.update(1)

            # Now extract the specific log file and find the version
            version = self.extract_and_find_version(zip_data)
            return {'run_id': run_id, 'version': version}

    def extract_and_find_version(self, zip_data):
        """Get version number from master log
            airtable_sync_wheel_file_name: airtable_sync-x.y.z"""
        log_filename = '0_run-prd-sync.txt'
        version_pattern = r'airtable_sync_wheel_file_name: airtable_sync-(\d+\.\d+\.\d+)'

        with zipfile.ZipFile(zip_data) as zip_ref:
            # Check if the log file exists in the zip
            if log_filename in zip_ref.namelist():
                with zip_ref.open(log_filename) as log_file:
                    log_content = log_file.read().decode('utf-8')
                    match = re.search(version_pattern, log_content)
                    if match:
                        version = match.group(1)
                        return version

    def fetch_existing_history(self):
        """Fetch existing history from Gist"""
        print("Fetching existing history...")
        gist_id = "584db1c30251ffee502796950b03f782"
        file_name = "run_history.csv"

        csv = CsvFile(gist_id, file_name, self.gist_token)
        csv.read()
        # print(f"Existing history: \n{csv}")
        self._csv = csv
        # print(f"Existing history: \n{self._run_numbers}")


class HistoryItem:
    def __init__(self, line):
        started_at, run_number, event, conclusion, duration, version = line.split(
            ",")
        self.started_at = started_at.strip()
        self.run_number = int(run_number.strip())
        self.event = event.strip()
        self.conclusion = conclusion.strip()
        self.duration = duration.strip()
        self.version = version.strip()

    def __str__(self):
        return f"{self.started_at},{self.run_number},{self.event},{self.conclusion},{self.duration},{self.version}"

    def __repr__(self):
        return self.__str__()


class CsvFile:
    def __init__(self, gist_id, file_name, token):
        self.gist_id = gist_id  # "584db1c30251ffee502796950b03f782"
        self.file_name = file_name
        self.token = token
        self._history = []
        self._updated = False

    def __str__(self):
        return '\n'.join(str(item) for item in self.history)

    @property
    def headers(self):
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
        }

    @property
    def history(self) -> list[HistoryItem]:
        return self._history

    def is_in_history(self, run_number) -> bool:
        return self._history_run_numbers.get(run_number, False)

    def add_to_history(self, items: list[HistoryItem]):
        self._updated = len(items) > 0
        self._history.extend(items)
        self._history.sort(key=lambda item: item.run_number, reverse=True)
        for item in items:
            self._history_run_numbers[item.run_number] = True

    def write(self):
        if not self._updated:
            return False

        url = f"https://api.github.com/gists/{self.gist_id}"
        payload = {
            "files": {
                self.file_name: {
                    "content": str(self)
                }
            }
        }

        response = requests.patch(
            url, headers=self.headers, data=json.dumps(payload))

        if response.status_code == 200:
            print(f"Successfully updated Gist: {self.file_name}")
            self._updated = False
            return True
        else:
            print(
                f"Failed to update Gist: {response.status_code} {response.text}")
            return False

    def read(self):
        url = f"https://gist.githubusercontent.com/{OWNER}/{self.gist_id}/raw/{self.file_name}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            lines = response.text.splitlines()
            self._history = [HistoryItem(line) for line in lines]
            self._history_run_numbers = {}
            for item in self._history:
                self._history_run_numbers[item.run_number] = True

            self._updated = False
        else:
            print(
                f"Failed to fetch existing history: {response.status_code} {response.text}")


if __name__ == '__main__':
    workflow_run_history = WorkflowRunHistory(
        action_token_name='GITHUB_AIRTABLE_SYNC_READONLY_ACTION_TOKEN',
        gist_token_name='GITHUB_AIRTABLE_SYNC_GIST_TOKEN')

    workflow_run_history.fetch_existing_history()

    history = asyncio.run(workflow_run_history.get_workflow_runs())
    print(history)
