"""A scheduled Toronto weather card for Discord."""

import asyncio
import logging
import os
from datetime import time
from io import BytesIO
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord.ext import tasks
from dotenv import load_dotenv

from card import make_weather_gif
from weather import get_toronto_forecast

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", "0"))
TZ = ZoneInfo(os.environ.get("TIMEZONE", "America/Toronto"))


class WeatherBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        self.daily_forecast.start()

    async def on_ready(self):
        logging.info("Connected as %s", self.user)

    @tasks.loop(time=time(hour=7, minute=0, tzinfo=TZ))
    async def daily_forecast(self):
        try:
            await self.post_forecast()
        except Exception:
            logging.exception("Daily forecast failed; scheduler remains active")

    @daily_forecast.before_loop
    async def before_daily_forecast(self):
        await self.wait_until_ready()

    async def post_forecast(self, channel: discord.abc.Messageable | None = None):
        """Fetch the forecast, produce a looping GIF, then send one card."""
        if channel is None:
            channel = self.get_channel(CHANNEL_ID)
            if channel is None:
                channel = await self.fetch_channel(CHANNEL_ID)

        async with aiohttp.ClientSession() as session:
            forecast = await get_toronto_forecast(session)
        animation = await asyncio.to_thread(make_weather_gif, forecast)
        filename = f"toronto-weather-{forecast['date']}.gif"
        attachment = discord.File(BytesIO(animation), filename=filename)
        embed = discord.Embed(
            title="Good morning, Mozilla PEY! ☀️",
            description=(
                f"**Toronto downtown · Today**\n"
                f"{forecast['description']} · High {forecast['high']}°C · Low {forecast['low']}°C"
            ),
            colour=discord.Colour.blurple(),
        )
        embed.set_image(url=f"attachment://{filename}")
        embed.set_footer(text="Forecast: Open-Meteo · Updates daily at 7:00 AM ET")
        await channel.send(embed=embed, file=attachment)


bot = WeatherBot()


@bot.tree.command(name="weather", description="Post today's Toronto downtown weather card")
async def weather_now(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        await bot.post_forecast(interaction.channel)
        await interaction.followup.send("Today's weather card is up!", ephemeral=True)
    except Exception:
        logging.exception("Could not post weather card")
        await interaction.followup.send("I couldn't get the forecast right now. Please try again shortly.", ephemeral=True)


if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        raise SystemExit("Set DISCORD_TOKEN and DISCORD_CHANNEL_ID in .env before starting the bot.")
    bot.run(TOKEN)
