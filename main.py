#!/usr/bin/env python3
"""BESS Extends Server Systems, a discord bot.
Usage: main.py [-hd] [-v | -q] [--log=FILE] [--config=JSON]

Options:
-h --help                     show this
-d --debug                    debug output to log (SPAMMY)
-q --quiet                    error-only output
-v --verbose                  all output
--log FILE, --log=FILE        Log file  [default: bess.log]
--config JSON, --config=JSON  Config file  [default: config.json]
"""
import json
import sys
import traceback

from discord.ext import commands
from docopt import docopt

docopt_args = docopt(__doc__, version=json.load(open("version.json"))[
    "version"])


class BESS(commands.Bot):
    """BESS primary class. Minimal functionality; only global-level
    commands."""
    def __init__(self, cli_args: dict, formatter=None,
                 pm_help=False, **options):
        self.config = {}
        self.cli_args = {}
        self.set_config(cli_args)
        super().__init__(self.config["prefix"], formatter=formatter,
                         description=self.config["description"],
                         pm_help=pm_help, **options)

    def set_config(self, cli_args: dict):
        """Hot-reloads configuration file."""
        self.cli_args = cli_args
        with open(cli_args["--config"]) as conf:
            self.config = {**json.load(conf), **cli_args}
        self.description = self.config["description"]
        self.prefix = self.config["prefix"]  # NOT "defined out of init",
        # defined in super().__init__, ignore the linter.


bess = BESS(docopt_args)

if __name__ == "__main__":
    for extension in bess.config["initial_extensions"]:
        try:
            bess.load_extension(f"cogs.{extension}")
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

bess.run(bess.config["token"], reconnect=True)
print("Exited successfully.")
