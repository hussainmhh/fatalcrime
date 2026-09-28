import os
import json
import asyncio
import discord
from pathlib import Path

TOKEN = os.environ["MTU1NDAzMjc5MTA3Nzc4MTUyNA.GLSaNY.pmJF2lIs9MyDjJlS3oZRFinnGsZo7ga49h4CUA"]

TARGET_USER_ID = 804660273444159518
ALERT_CHANNEL_ID = 1554034362327105546

STATE_FILE = Path("avatar_state.json")

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


def load_last_avatar():
    if not STATE_FILE.exists():
        return None

    try:
        return json.loads(STATE_FILE.read_text()).get("avatar_url")
    except Exception:
        return None


def save_avatar(url):
    STATE_FILE.write_text(json.dumps({"avatar_url": url}))


async def check_avatar():
    await client.wait_until_ready()

    while not client.is_closed():
        try:
            user = await client.fetch_user(TARGET_USER_ID)
            new_avatar = user.display_avatar.url
            old_avatar = load_last_avatar()

            # First run: remember current PFP without alerting
            if old_avatar is None:
                save_avatar(new_avatar)

            elif old_avatar != new_avatar:
                channel = client.get_channel(ALERT_CHANNEL_ID)

                if channel is None:
                    channel = await client.fetch_channel(ALERT_CHANNEL_ID)

                embed = discord.Embed(
                    title="Lil nig changed his pfp again 💔✌🏿"
                )

                embed.add_field(
                    name="Old pfp",
                    value=f"[Open old pfp]({old_avatar})",
                    inline=False
                )

                embed.add_field(
                    name="To:",
                    value=f"[Open new pfp]({new_avatar})",
                    inline=False
                )

                embed.set_thumbnail(url=old_avatar)
                embed.set_image(url=new_avatar)

                await channel.send(embed=embed)

                save_avatar(new_avatar)

        except Exception as e:
            print(f"Watcher error: {e}")

        # Check every 60 seconds
        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


async def main():
    async with client:
        asyncio.create_task(check_avatar())
        await client.start(TOKEN)


asyncio.run(main())
