import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

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
        response = MagicMock()
        response.__enter__.return_value.status = 200
        with patch.object(notify.urllib.request, 'urlopen', return_value=response) as open_url:
            notify.send({'message': 'Test'}, 'br_usr_test')
            request = open_url.call_args.args[0]
            self.assertEqual(request.full_url, 'https://api.brrr.now/v1/send')
            self.assertEqual(request.get_header('Authorization'), 'Bearer br_usr_test')
            self.assertEqual(json.loads(request.data), {'message': 'Test'})

    def test_complete_webhook_is_supported(self):
        response = MagicMock()
        response.__enter__.return_value.status = 200
        with patch.object(notify.urllib.request, 'urlopen', return_value=response) as open_url:
            notify.send({'message': 'Test'}, 'https://api.brrr.now/v1/br_usr_test')
            self.assertEqual(open_url.call_args.args[0].get_header('Authorization'), 'Bearer br_usr_test')

    def test_missing_secret_sends_nothing(self):
        with patch.object(notify.urllib.request, 'urlopen') as open_url:
            with self.assertRaisesRegex(ValueError, 'ontbreekt'):
                notify.send({'message': 'Test'}, '')
            open_url.assert_not_called()

    def test_unrelated_webhook_is_rejected(self):
        with patch.object(notify.urllib.request, 'urlopen') as open_url:
            with self.assertRaises(ValueError):
                notify.send({'message': 'Test'}, 'https://example.com/v1/br_usr_test')
            open_url.assert_not_called()
