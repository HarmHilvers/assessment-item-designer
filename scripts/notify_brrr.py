"""Notify via brrr using the BRRR_KEY repository secret, never logging the key."""

import json
import os
from pathlib import Path
import sys
import subprocess
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]


def notification(root, env):
    version = json.loads((root / 'plugin.json').read_text())['version']
    repository = env['GITHUB_REPOSITORY']
    run_url = f'https://github.com/{repository}/actions/runs/{env["GITHUB_RUN_ID"]}'
    failed = env.get('RELEASE_JOB_STATUS') != 'success'
    return {
        'title': 'Assessment Item Designer',
        'message': (f'Release {version} failed. Check the workflow for details.' if failed
                    else f'Release {version} is available. Download the upload ZIP from GitHub.'),
        'open_url': run_url if failed else f'https://github.com/{repository}/releases/tag/v{version}',
        'thread_id': 'assessment-item-designer-releases',
    }


def send(payload, key):
    key = key.strip()
    if not key:
        raise ValueError('Repository secret BRRR_KEY is missing or empty.')
    # Accept either the key alone or the complete documented webhook URL.
    if key.startswith('https://'):
        url = urllib.parse.urlsplit(key)
        if url.netloc != 'api.brrr.now' or not url.path.startswith('/v1/') or url.query or url.fragment:
            raise ValueError('BRRR_KEY does not contain a valid brrr webhook.')
        key = url.path[len('/v1/'):]
    if not key or '/' in key or any(c.isspace() for c in key):
        raise ValueError('BRRR_KEY does not contain a valid webhook key.')
    # Use the documented curl transport. Pass the credential through stdin,
    # rather than exposing it in a URL, command argument or diagnostic output.
    result = subprocess.run(
        ['curl', '--silent', '--show-error', '--fail', '--max-time', '20',
         '--config', '-', '--header', 'Content-Type: application/json',
         '--data', json.dumps(payload, ensure_ascii=False), '--output', '/dev/null',
         '--write-out', '%{http_code}', 'https://api.brrr.now/v1/send'],
        input='header = ' + json.dumps(f'Authorization: Bearer {key}') + '\n',
        text=True, capture_output=True, timeout=25)
    status = result.stdout.strip()
    if result.returncode or not status.startswith('2'):
        raise ValueError(f'brrr notification was not sent (HTTP {status if status.isdigit() else "unknown"}).')
    print(f'brrr accepted the notification (HTTP {status}).')


def main():
    try:
        send(notification(ROOT, os.environ), os.environ.get('BRRR_KEY', ''))
    except (subprocess.TimeoutExpired, OSError):
        print('::warning::brrr could not be reached or curl is unavailable.', file=sys.stderr)
        return 1
    except (ValueError, TimeoutError) as error:
        print(f'::warning::{error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
