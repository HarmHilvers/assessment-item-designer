"""Notify via brrr using the BRRR_KEY repository secret, never logging the key."""

import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def notification(root, env):
    version = json.loads((root / 'plugin.json').read_text())['version']
    repository = env['GITHUB_REPOSITORY']
    run_url = f'https://github.com/{repository}/actions/runs/{env["GITHUB_RUN_ID"]}'
    failed = env.get('RELEASE_JOB_STATUS') != 'success'
    return {
        'title': 'Assessment Item Designer',
        'message': (f'Release {version} is mislukt. Bekijk de workflow voor details.' if failed
                    else f'Release {version} is beschikbaar. De uploadzip staat op GitHub.'),
        'open_url': run_url if failed else f'https://github.com/{repository}/releases/tag/v{version}',
        'thread_id': 'assessment-item-designer-releases',
    }


def send(payload, key):
    key = key.strip()
    if not key:
        raise ValueError('Repository secret BRRR_KEY ontbreekt of is leeg.')
    # Accept either the key alone or the complete documented webhook URL.
    if key.startswith('https://'):
        url = urllib.parse.urlsplit(key)
        if url.netloc != 'api.brrr.now' or not url.path.startswith('/v1/') or url.query or url.fragment:
            raise ValueError('BRRR_KEY bevat geen geldige brrr-webhook.')
        key = url.path[len('/v1/'):]
    if not key or '/' in key or any(c.isspace() for c in key):
        raise ValueError('BRRR_KEY bevat geen geldige webhook-sleutel.')
    request = urllib.request.Request(
        'https://api.brrr.now/v1/send',
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        method='POST')
    with urllib.request.urlopen(request, timeout=20) as response:
        if not 200 <= response.status < 300:
            raise ValueError(f'brrr gaf HTTP {response.status}.')
        print(f'brrr heeft de melding geaccepteerd (HTTP {response.status}).')


def main():
    try:
        send(notification(ROOT, os.environ), os.environ.get('BRRR_KEY', ''))
    except urllib.error.HTTPError as error:
        print(f'::warning::brrr-melding geweigerd (HTTP {error.code}).', file=sys.stderr)
        return 1
    except urllib.error.URLError:
        print('::warning::brrr kon niet worden bereikt.', file=sys.stderr)
        return 1
    except (ValueError, TimeoutError) as error:
        print(f'::warning::{error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
