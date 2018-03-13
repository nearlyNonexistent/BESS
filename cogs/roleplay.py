"""Cog for BESS. This cog provides roleplay utilities."""
# Standard Library imports
import random
# Third-party imports
import attr
import dice
from discord.ext import commands
from pyparsing import ParseException


@attr.s
class Roleplay(object):
    """Provides roleplay game mechanics."""

    bot = attr.ib()

    @commands.command()
    async def roll(self, ctx, *, message: str):
        """Roll dice using standard dice notation."""
        try:
            await ctx.message.add_reaction("🎲")
            await ctx.send(f"Your dice roll: {dice.roll(message)}")
        except ParseException:
            await ctx.send("Invalid dice roll!")

    @commands.command()
    async def flip(self, ctx):
        """Flip a coin."""
        flip = random.choice(["heads", "tails"])
        await ctx.send(f"You got: {flip}!")

    @commands.command()
    async def choose(self, ctx, *, message: str):
        """Have BESS choose one from a list of comma-separated items."""
        choice = random.choice(message.split(","))
        await ctx.send(f"I say: {choice.strip()}!")


def setup(bot):
    """Load the cog."""
    bot.add_cog(Roleplay(bot))
