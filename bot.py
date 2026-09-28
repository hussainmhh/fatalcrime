import os
import json
import asyncio
import discord
from pathlib import Path

TOKEN = os.environ["DISCORD_TOKEN"]

TARGET_USER_IDS = [
    804660273444159518,
    312616732034596866,
]

ALERT_CHANNEL_ID = 1554034362327105546

STATE_FILE = Path("avatar_state.json")

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


def load_state():
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state))


async def check_avatars():
    await client.wait_until_ready()

    while not client.is_closed():
        try:
            state = load_state()

            for user_id in TARGET_USER_IDS:
                try:
                    user = await client.fetch_user(user_id)

                    new_avatar = str(user.display_avatar.url)
                    old_avatar = state.get(str(user_id))

                    # First time seeing this user:
                    # remember their current PFP without sending an alert.
                    if old_avatar is None:
                        state[str(user_id)] = new_avatar
                        save_state(state)
                        print(f"Saved starting PFP for {user}")

                    elif old_avatar != new_avatar:
                        channel = client.get_channel(ALERT_CHANNEL_ID)

                        if channel is None:
                            channel = await client.fetch_channel(
                                ALERT_CHANNEL_ID
                            )

                        embed = discord.Embed(
                            title="Lil nig changed his pfp again 💔✌🏿"
                        )

                        embed.add_field(
                            name="Old pfp",
                            value=f"[Open old pfp]({old_avatar})",
                            inline=False,
                        )

                        embed.add_field(
                            name="To:",
                            value=f"[Open new pfp]({new_avatar})",
                            inline=False,
                        )

                        embed.set_thumbnail(url=old_avatar)
                        embed.set_image(url=new_avatar)

                        await channel.send(embed=embed)

                        state[str(user_id)] = new_avatar
                        save_state(state)

                        print(f"PFP change detected for {user}")

                except Exception as e:
                    print(f"Error checking {user_id}: {e}")

        except Exception as e:
            print(f"Watcher error: {e}")

        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    for user_id in TARGET_USER_IDS:
        print(f"Watching user: {user_id}")


async def main():
    async with client:
        asyncio.create_task(check_avatars())
        await client.start(TOKEN)


asyncio.run(main())
