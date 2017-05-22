#!/usr/bin/env python3
# USAGE:
# python ./main.py [optional: config file name] [optional: log file name]

import discord
import asyncio
import json
import sys
import commands
import warnings


class Config:
    """This reads the configuration details for the bot. Most of these are accessed using the attrs index, though the prefix is an exception as it is used a lot."""
    class Logger():
        """Private interface for the log file. Essentially just a list that also writes to file."""
        def __init__(self):
            self.attributes =[]

        def append(self, message):
            self.attributes.append(f"[{message.timestamp}] {message.author}: {message.content}\n")

        def save(self, savefile="latest.log"):
            with open(savefile, 'w') as f:
                for logmessage in self.attributes:
                    f.write(logmessage)

    def __init__(self, configfile="config.json"):
        """Reads configuration details, in JSON format."""
        with open(configfile) as f:
            self.attrs = json.load(f)
        if self.attrs["use_username_mentions_instead"] == "true":
            self.prefix = f"<@{self.attrs['id']}> "
        else:
            self.prefix = self.attrs['prefix']
        self.owner = self.attrs["owner"]
        self.logger = self.Logger()
        self.voiceclient = None

config = Config(sys.argv[1] if len(sys.argv) >= 2 else 'config.json')
client = discord.Client()


@client.event
async def on_ready():
    print('-----')
    print('Logged in as')
    print(client.user.name)
    print("Invite Link:")
    print(f"https://discordapp.com/oauth2/authorize?&client_id={client.user.id}&scope=bot&permissions={config.attrs['perms']}")
    print('------')
    if discord.opus.is_loaded():
        voiceclient = await client.join_voice_channel(discord.utils.get(client.get_all_channels(), type=discord.ChannelType.voice, server__name=config.attrs["server"]))
        global commandScan
        commandScan = commands.CommandHolder(client, config, voiceclient)
    else:
        warnings.warn("BESS failure in Voice!!! Restart!!!")


@client.event
async def on_message(message):
    if message.content.startswith(config.prefix):
        config.logger.append(message)
        message.content = message.content[len(config.prefix):]
        await commandScan(message)
    elif message.author == client.user:
        config.logger.append(message)

client.run(config.attrs["token"])
print("Saving log...")
config.logger.save(sys.argv[2] if len(sys.argv) >= 3 else "latest.log")
print("Complete.")
