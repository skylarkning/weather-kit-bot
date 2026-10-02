import io
import json
import unittest
from unittest.mock import patch
from send_once import multipart, send, validate_webhook, webhook_payload

class WebhookTests(unittest.TestCase):
    def test_attachment_filename_and_multipart(self):
        forecast={'description':'Snow','high':-2,'low':-8}
        payload=webhook_payload(forecast,'weather.gif')
        body,content_type=multipart(payload,b'GIF89a','weather.gif')
        self.assertIn(b'name="files[0]"; filename="weather.gif"',body)
        self.assertIn(b'GIF89a',body)
        self.assertEqual(payload['embeds'][0]['image']['url'],'attachment://weather.gif')
        boundary=content_type.split('boundary=')[1]
        self.assertTrue(body.endswith(f'--{boundary}--\r\n'.encode()))

    def test_rejects_non_discord_url(self):
        for url in ('https://example.com/api/webhooks/123/token','http://discord.com/api/webhooks/123/token',''):
            with self.assertRaises(ValueError):validate_webhook(url)

    @patch('send_once.urlopen')
    def test_requires_confirmed_message_and_uses_wait(self,request):
        request.return_value=io.BytesIO(json.dumps({'id':'123'}).encode())
        send('https://discord.com/api/webhooks/123/test_token',{},b'GIF89a','weather.gif')
        self.assertTrue(request.call_args.args[0].full_url.endswith('?wait=true'))
        request.return_value=io.BytesIO(b'{}')
        with self.assertRaises(RuntimeError):send('https://discord.com/api/webhooks/123/test_token',{},b'GIF89a','weather.gif')

if __name__=='__main__':unittest.main()
