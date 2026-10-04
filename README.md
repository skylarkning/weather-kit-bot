# Mozilla PEY Toronto Weather — GitHub Actions

An animated Toronto weather card featuring detailed weather artwork and a weather-aware Firefox fox. Targets **07:00 America/Toronto**, with fallback attempts at :10, :25 and :40. UTC schedules at 11h and 12h cover EDT and EST; Python's America/Toronto time-window guard and daily delivery check prevent early or duplicate sends. GitHub may delay or drop scheduled runs, so exact-time delivery is not guaranteed. Manual sending is available from **Actions → Toronto Weather → Run workflow**, with an opt-in force-send checkbox. No always-on computer is needed.

## Deploy

1. In the target Discord channel, go to Edit Channel → Integrations → Webhooks → New Webhook. Copy its URL. Requires Manage Webhooks permission.
2. Push this directory's **contents** to the root of a GitHub repository's default branch, including the hidden `.github/workflows/weather.yml` file.
3. Repository Settings → Secrets and variables → Actions → New repository secret: name **DISCORD_WEBHOOK_URL**, value the complete Discord webhook URL. Do not commit this URL.
4. Open Actions → Toronto Weather → Run workflow. Verify the run succeeds and a GIF arrives in Discord.

The only secret required is DISCORD_WEBHOOK_URL. No Bot Token or channel ID is needed; the webhook selects the destination channel. This workflow does not provide the Discord `/weather` slash command. Stop any old running Bot instance to avoid double posts.

GitHub scheduling may be delayed or dropped under load. Manual runs send an extra card. Workflows must be on the default branch; public repositories may have scheduled runs disabled after 60 days without repository activity. Private repositories use your account's Actions allowance.

## Local dry run

```bash
python3 -m pip install -r requirements-actions.txt
python3 send_once.py --dry-run
```

Fetches a forecast and saves artifacts/toronto-weather-DATE.gif without contacting Discord. Each Actions run also keeps its generated GIF as a downloadable artifact for seven days. Upload failures are reported without printing the secret webhook URL; no automatic send retries are made to avoid duplicate messages after ambiguous network failures.

## Legacy mode

bot.py, Dockerfile and requirements.txt are the previous always-on Discord Bot implementation. GitHub Actions uses **send_once.py** and **requirements-actions.txt** instead.

## Verification

```bash
python3 -m unittest test_send_once.py
```

Weather art covers all 28 supported WMO codes. Fox moods respond to snow, storms, rain and temperature extremes; GIF colours are reserved for the mascot to prevent palette distortion.

Official references: [GitHub workflow scheduling](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [Discord webhooks](https://docs.discord.com/developers/resources/webhook).
