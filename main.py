#!/usr/bin/env python3
# USAGE:
# python ./main.py [optional: config file name] [optional: log file name]

import discord
import asyncio
import json
import sys
import commands
import os
import warnings
import time
import Levenshtein as levenshtein


class Config:
    """This reads the configuration details for the bot. Most of these are accessed
    using the attrs index, with exceptions for often used variables."""
    class Logger():
        """Private interface for the log file. Essentially just
        a list that also writes to file."""
        def __init__(self):
            self.attributes = []

        def append(self, message):
            logMessage = (f"[{message.timestamp}] "
                          f"<{message.server} - {message.channel}> "
                          f"@{message.author}: "
                          f"{message.content}")
            print(logMessage)
            self.attributes.append(logMessage+"\n")

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
        self.debug = self.attrs["debug"]
        self.startTime = time.time()
        with open("version", 'r') as f:
            self.version = f.read()


print('Loading...')
config = Config(sys.argv[1] if len(sys.argv) >= 2 else 'config.json')
client = discord.Client()


@client.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(("------------\n"
           "Logged in.\n"
           f" {client.user.name} - {config.version}.\n"
           " Invite link:\n"
           " https://discordapp.com/oauth2/authorize?&client_id="
           f"{client.user.id}&scope=bot&permissions={config.attrs['perms']}\n"
           "------------"))

    if discord.opus.is_loaded():
        voiceChannel = discord.utils.get(client.get_all_channels(),
                                         type=discord.ChannelType.voice,
                                         server__name=config.attrs["server"])
        voiceclient = await client.join_voice_channel(voiceChannel)
        global commandScan
        commandScan = commands.CommandHolder(client, config, voiceclient)
        print("System online.")
    else:
        warnings.warn("BESS failure in Voice!!! Restart!!!")
    await client.change_presence(game=discord.Game(name=config.attrs["game"]))


@client.event
async def on_message(message):
    if not message.author.bot:
        if message.content.startswith(config.prefix):
            config.logger.append(message)
            message.content = message.content[len(config.prefix):]
            stop = await commandScan(message)
            if stop:
                await client.logout()
        elif message.author == client.user:
            config.logger.append(message)


@client.event
async def on_message_edit(before, after):
    if not before.author.bot:
        if before.author != client.user:
            dist = levenshtein.distance(before.content, after.content)
            if dist > config.attrs["minimum-levenshtein"]:
                await client.send_message(before.channel,
                                          (f"\u200B*{before.author}*"
                                           " edited a message:\n"
                                           f"Original: ```{before.content}```"
                                           f"After: ```{after.content}```"))

client.run(config.attrs["token"])
print("Saving log...")
config.logger.save(sys.argv[2] if len(sys.argv) >= 3 else "latest.log")
print("Complete.")
