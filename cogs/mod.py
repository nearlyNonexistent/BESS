"""Cog for BESS. This cog contains administrative commands."""
# Standard Library Imports.
import json
import logging
# Third-Party Imports.
import attr
import discord
from discord.ext import commands


@attr.s
class Mod(object):
    """Moderation-only commands."""

    bot = attr.ib()

    @commands.group()
    async def cog(self, ctx):
        """Control cog modules."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")

    @cog.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        """Load a module. Uses cog dotpaths."""
        try:
            if cog not in self.bot.current_extensions:
                self.bot.load_extension(cog)
                self.bot.current_extensions.append(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.message.add_reaction("👍")

    @cog.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        """Unload a module. Uses cog dotpaths."""
        try:
            if cog in self.bot.current_extensions:
                self.bot.unload_extension(cog)
                self.bot.current_extensions.remove(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.message.add_reaction("👍")

    @cog.command(name="reload")
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        """Reload a module. Uses cog dotpaths."""
        try:
            if cog in self.bot.current_extensions:
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.message.add_reaction("👍")

    @cog.command(name="list", aliases=["ls"])
    @commands.is_owner()
    async def list_cog(self, ctx):
        """List the cog modules loaded. Uses cog dotpaths."""
        await ctx.send(
            "Current extensions:" + str(self.bot.current_extensions))

    @commands.group()
    async def config(self, ctx):
        """Control configuration features."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")

    @config.command(name="reload")
    @commands.is_owner()
    async def reload_config(self, ctx):
        """Reload configuration file."""
        with open(self.bot.config["--config"]) as conf:
            logging.info(("Loading default configuration from "
                         f"{self.bot.config['--config']}..."))
            default_config = json.load(conf)
            self.bot.config = {}
            self.bot.config = {**default_config, **self.bot.cli_args}
            await ctx.message.add_reaction("👍")
        logging.info("Configuration loaded.")

    @config.command(name="list", aliases=["ls"])
    @commands.is_owner()
    async def list_config(self, ctx):
        """List configuration values."""
        await ctx.author.send((f"Configuration: ```{self.bot.config}```\n\n"
                               f"Cli args: ```{self.bot.cli_args}```"))

    @commands.command()
    async def version(self, ctx):
        """Check the BESS version versus latest"""
        if self.bot.versionInfo[0] == "dev":
            desc = ("I am currently running a development version."
                    " The latest public release is: ")
        elif self.bot.versionInfo[0]:
            desc = (f"I am out of date! The current version is: ")
        else:
            desc = (f"I am currently running the current version: ")
        version = discord.Embed(title="BESS Version Information", type="rich",
                                description=f"{desc}{self.bot.versionInfo[2]}",
                                url=self.bot.versionInfo[1])
        version.set_thumbnail(url=("https://cdn.discordapp.com/"
                                   "avatars/296489481106620416/f2fb191d2076214"
                                   "b9caec8d7bce19d59.webp?size=128%22"))
        version.set_author(name=self.bot.owner.name)
        await ctx.send(embed=version)


def setup(bot):
    """Load the cog."""
    bot.add_cog(Mod(bot))
