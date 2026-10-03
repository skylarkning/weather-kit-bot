"""Skip a daily delivery if an earlier run confirmed its send step succeeded."""
import json
import os
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], text=True))


def already_sent(runs, today, current_run, jobs_for):
    for run in runs:
        if str(run['id']) == str(current_run):
            continue
        day = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Toronto')).date()
        if day != today:
            continue
        for job in jobs_for(run['id']):
            if any(step['name'] == 'Generate and send weather card' and step.get('conclusion') == 'success' for step in job.get('steps', [])):
                return True
    return False


if __name__ == '__main__':
    repo = os.environ['GITHUB_REPOSITORY']
    today = datetime.now(ZoneInfo('America/Toronto')).date()
    runs = api(f'repos/{repo}/actions/workflows/weather.yml/runs?per_page=100&created={today}')['workflow_runs']
    skip = already_sent(runs, today, os.environ['GITHUB_RUN_ID'],
                        lambda run: api(f'repos/{repo}/actions/runs/{run}/jobs?per_page=100')['jobs'])
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write(f'send={str(not skip).lower()}\n')
    print('Already sent today; skipping duplicate.' if skip else 'No confirmed delivery today; sending.')
