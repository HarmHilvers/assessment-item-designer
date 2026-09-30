import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('notify_brrr', ROOT / 'scripts/notify_brrr.py')
notify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(notify)


class NotificationTests(unittest.TestCase):
    def test_success_links_to_release(self):
        payload = notify.notification(ROOT, {'GITHUB_REPOSITORY': 'owner/repo',
            'GITHUB_RUN_ID': '123', 'RELEASE_JOB_STATUS': 'success'})
        self.assertIn('/releases/tag/v', payload['open_url'])
        self.assertIn('beschikbaar', payload['message'])

    def test_failure_links_to_workflow(self):
        payload = notify.notification(ROOT, {'GITHUB_REPOSITORY': 'owner/repo',
            'GITHUB_RUN_ID': '123', 'RELEASE_JOB_STATUS': 'failure'})
        self.assertEqual(payload['open_url'], 'https://github.com/owner/repo/actions/runs/123')
        self.assertIn('mislukt', payload['message'])

    def test_key_is_in_header_not_url_or_payload(self):
        response = subprocess.CompletedProcess([], 0, stdout='200')
        with patch.object(notify.subprocess, 'run', return_value=response) as run:
            notify.send({'message': 'Test'}, 'br_usr_test')
            command = run.call_args.args[0]
            self.assertEqual(command[-1], 'https://api.brrr.now/v1/send')
            self.assertFalse(any('br_usr_test' in argument for argument in command))
            self.assertIn('Authorization: Bearer br_usr_test', run.call_args.kwargs['input'])
            self.assertEqual(json.loads(command[command.index('--data') + 1]), {'message': 'Test'})

    def test_complete_webhook_is_supported(self):
        response = subprocess.CompletedProcess([], 0, stdout='200')
        with patch.object(notify.subprocess, 'run', return_value=response) as run:
            notify.send({'message': 'Test'}, 'https://api.brrr.now/v1/br_usr_test')
            self.assertIn('Authorization: Bearer br_usr_test', run.call_args.kwargs['input'])

    def test_missing_secret_sends_nothing(self):
        with patch.object(notify.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'ontbreekt'):
                notify.send({'message': 'Test'}, '')
            run.assert_not_called()

    def test_unrelated_webhook_is_rejected(self):
        with patch.object(notify.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                notify.send({'message': 'Test'}, 'https://example.com/v1/br_usr_test')
            run.assert_not_called()

    def test_http_failure_is_not_reported_as_delivery(self):
        response = subprocess.CompletedProcess([], 22, stdout='403')
        with patch.object(notify.subprocess, 'run', return_value=response):
            with self.assertRaisesRegex(ValueError, 'HTTP 403'):
                notify.send({'message': 'Test'}, 'br_usr_test')
