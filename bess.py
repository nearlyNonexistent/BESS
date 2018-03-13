#!/usr/bin/env python3
"""BESS Extends Server Systems, a discord bot.

Usage: bess.py [-hd] [-v | -q] [--log=FILE] [--config=JSON]

Options:
-h --help                     show this
-d --debug                    debug output to log (SPAMMY)
-q --quiet                    error-only output
-v --verbose                  all output
--log FILE, --log=FILE        Log file  [default: bess.log]
--config JSON, --config=JSON  Config file  [default: config.json]
"""
# Standard Library Imports.
import asyncio
from datetime import datetime
import json
import logging
# Same-Project Imports.
from logger import Logger
# Third-Party Imports.
import aiohttp
import attr
import discord
from discord.ext import commands
from docopt import docopt
# Default configuration.
config = docopt(__doc__, version=json.load(open("version.json"))["version"])
cli_args = config


if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')


@attr.s
class Bess(commands.Bot):
    """Attempt at BESS core 2.0."""

    cli_args = attr.ib()
    logger = attr.ib()

    def __attrs_post_init__(self, **options):
        """Create the bot."""
        logging.info("BESS is loading...")
        with open(cli_args["--config"]) as conf:
            logging.info(("Loading default configuration from "
                          f"{self.cli_args['--config']}..."))
            default_config = json.load(conf)
            self.config = {**default_config, **config}
            logging.info("Configuration loaded.")
        if len(self.config["prefix"]) > 0:
            commandprefix = commands.when_mentioned_or(self.config["prefix"])
        else:
            commandprefix = commands.when_mentioned
        super().__init__(commandprefix, commands.formatter.HelpFormatter(),
                         self.config["description"], False)
        self.current_extensions = []
        self.add_command(self.exit)
        for extension in self.config["initial_extensions"]:
            try:
                self.load_extension(extension)
                logging.info(f"Loaded {extension}.")
                self.current_extensions.append(extension)
            except Exception as e:
                logging.exception(f"Failed to load {extension}.")
        self.loop.create_task(self.update_check())
        self.indate = True
        self.run(self.config["token"], reconnect=True,
                 bot=not self.config["PASTURE"])

    async def update_check(self):
        """Check for updates."""
        with open("version.json") as version:
            self.version = json.load(version)
        if self.indate:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.version['checkUrl']) as resp:
                    version = json.loads(await resp.text())
                    oldVersion = self.version["date"].split("-")
                    oldVersion = datetime(int(oldVersion[0]),
                                          int(oldVersion[1]),
                                          int(oldVersion[2]))
                    newVersion = version["date"].split("-")
                    newVersion = datetime(int(newVersion[0]),
                                          int(newVersion[1]),
                                          int(newVersion[2]))
                    if newVersion > oldVersion:
                        updateString = ("BESS is running: "
                                        f"{self.version['version']}."
                                        "\nHowever, a newer version exists: "
                                        f"{version['version']}."
                                        f"\nUpdate BESS at: "
                                        f"{version['downloadUrl']}")
                        await self.owner.send(updateString)
                        self.indate = False
                        self.logger.abbr_log("Update: "
                                             f"{version['downloadUrl']}",
                                             updateString)
                        self.versionInfo = [True, newVersion["downloadUrl"],
                                            version["version"]]
                    elif newVersion == oldVersion:
                        self.versionInfo = [False, self.version["downloadUrl"],
                                            self.version["version"]]
                    elif newVersion < oldVersion:
                        self.versionInfo = ["dev", self.version["downloadUrl"],
                                            version["version"]]
                        self.indate = False
                await asyncio.sleep(60 * 60)  # 1 hour timer

    @commands.command()
    @commands.is_owner()
    async def exit(self, ctx):
        """Stop the bot from running entirely."""
        await ctx.message.add_reaction("💤")
        await self.logout()

    async def on_ready(self):
        """Alert the user on BESS login."""
        app_info = await self.application_info()
        self.owner = app_info.owner
        self.logger.abbr_log("BESS started.",
                             ("BESS has connected successfully with"
                              f" extensions: {self.current_extensions}."))
        await self.update_check()


if cli_args["--verbose"]:
    loglevel = "v"
elif cli_args["--quiet"]:
    loglevel = "q"
else:
    loglevel = ""

logger = Logger(cli_args["--log"], cli_args["--debug"], loglevel)
bot = Bess(cli_args, logger)
logger.abbr_log("BESS exited.",
                f"BESS has exited. Full log saved to {config['--log']}")
