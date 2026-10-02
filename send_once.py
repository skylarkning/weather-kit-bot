"""Fetch, render and send one forecast through a Discord webhook, then exit."""
import argparse
import json
import os
import re
import secrets
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from card import make_weather_gif
from weather import WEATHER_URL, forecast_params, forecast_from_payload

def webhook_payload(forecast, filename):
    return {
        'username':'Weather Kit',
        'allowed_mentions':{'parse':[]},
        'attachments':[{'id':0,'filename':filename}],
        'embeds':[{
            'title':"Toronto's Weather Today",
            'description':f"{forecast['description']} · High {forecast['high']}°C · Low {forecast['low']}°C",
            'color':0xFF7139,
            'image':{'url':f'attachment://{filename}'},
            'footer':{'text':'Forecast: Open-Meteo · Daily at 7:00 AM Toronto time'},
        }],
    }

def multipart(payload, gif, filename):
    boundary='pey-'+secrets.token_hex(16)
    parts=[
        f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\nContent-Type: application/json\r\n\r\n'.encode(),
        json.dumps(payload).encode(),
        f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; filename="{filename}"\r\nContent-Type: image/gif\r\n\r\n'.encode(),
        gif,
        f'\r\n--{boundary}--\r\n'.encode(),
    ]
    return b''.join(parts),f'multipart/form-data; boundary={boundary}'

def validate_webhook(url):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in ('discord.com','discordapp.com') or not re.fullmatch(r'/api(?:/v\d+)?/webhooks/\d+/[A-Za-z0-9_-]+',parsed.path):
        raise ValueError('DISCORD_WEBHOOK_URL must be a Discord incoming webhook URL.')
    return url

def send(url, payload, gif, filename):
    body,content_type=multipart(payload,gif,filename)
    # wait=true makes Discord return confirmation, not just an empty response.
    parsed=urlsplit(validate_webhook(url))
    endpoint=parsed._replace(query='wait=true').geturl()
    request=Request(endpoint,data=body,headers={'Content-Type':content_type,'User-Agent':'MozillaPEYWeather/1.0'},method='POST')
    with urlopen(request,timeout=60) as response:
        message=json.load(response)
    if not message.get('id'):
        raise RuntimeError('Discord did not confirm the message.')
    print('Discord confirmed weather message:',message['id'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--fixture',type=Path,help='Offline sample forecast JSON for verification')
    args=parser.parse_args()
    webhook=os.environ.get('DISCORD_WEBHOOK_URL','')
    if not args.dry_run:validate_webhook(webhook)
    if args.fixture:
        forecast=json.loads(args.fixture.read_text())
    else:
        request=Request(WEATHER_URL+'?'+urlencode(forecast_params()),headers={'User-Agent':'MozillaPEYWeather/1.0'})
        with urlopen(request,timeout=30) as response:data=json.load(response)
        forecast=forecast_from_payload(data)
    gif=make_weather_gif(forecast)
    filename=f"toronto-weather-{forecast['date']}.gif"
    target=Path('artifacts');target.mkdir(exist_ok=True)
    (target/filename).write_bytes(gif)
    print('Rendered',filename,'bytes:',len(gif))
    if args.dry_run:
        print('Dry run: no Discord message sent.')
    else:
        send(webhook,webhook_payload(forecast,filename),gif,filename)

if __name__=='__main__':
    try:main()
    except HTTPError as error:
        # Never print exception URLs: a Discord webhook URL contains a secret token.
        print(f'HTTP request failed (status {error.code}). Check webhook permissions or API availability.',file=sys.stderr);sys.exit(1)
    except (URLError,TimeoutError):
        print('Network request failed. Check Actions logs and retry manually.',file=sys.stderr);sys.exit(1)
    except (ValueError,RuntimeError) as error:
        print(str(error),file=sys.stderr);sys.exit(1)
