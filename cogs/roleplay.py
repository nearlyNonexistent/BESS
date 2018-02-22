"""Cog for BESS. This cog provides roleplay utilities."""
# Standard Library imports
import asyncio
# Third-party imports
import attr
import dice
from asteval import Interpreter
from discord.ext import commands
from pyparsing import ParseException


@attr.s
class Roleplay(object):
    """Provides roleplay game mechanics."""

    bot = attr.ib()

    def __attrs_post_init__(self):
        """Create interpreter array."""
        self.interpreters = {}

    @commands.command()
    async def roll(self, ctx, *, message: str):
        """Roll dice."""
        try:
            await ctx.send(f"Your dice roll: {dice.roll(message)}")
            await ctx.message.add_reaction("🎲")
        except ParseException:
            await ctx.send("Invalid dice roll!")

    @commands.group()
    async def math(self, ctx):
        """Do math with an integrated Python interpreter."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")

    @math.command()
    async def clear(self, ctx):
        """Clear the state of your personal interpreter."""
        try:
            del self.interpreters[ctx.author.id]
        except KeyError:
            await ctx.message.add_reaction("👍")
        self.interpreters[ctx.author.id] = Interpreter(no_print=True)
        await ctx.message.add_reaction("👍")

    @math.command()
    async def run(self, ctx, *, message: str):
        """Run a math interpreter for the user."""
        message = message.replace("```", "")
        try:
            interp = self.interpreters[ctx.author.id]
        except KeyError:
            self.interpreters[ctx.author.id] = Interpreter(no_print=True)
            interp = self.interpreters[ctx.author.id]
        try:
            answer = "`" + str(interp(message, show_errors=False)) + "`"
        except:  # to catch interpreter errors
            answer = ""
            if len(interp.error) > 0:
                answer = "```"
                for err in interp.error:
                    answer += str(err.get_error()) + ", "
                answer += "```"
        if answer != "`None`":
            if len(answer) < 80:
                await ctx.send(answer)
            else:
                await ctx.author.send(answer)
        else:
            await ctx.message.add_reaction("👍")

        def check(m):
                override = "math run" in m.content or "math clear" in m.content
                return m.author == ctx.author and override
        try:
            answer = await self.bot.wait_for("message", check=check,
                                             timeout=60 * 2)
        except asyncio.TimeoutError:
            await ctx.message.add_reaction("🚿")
            del self.interpreters[ctx.author.id]


def setup(bot):
    """Load the cog."""
    bot.add_cog(Roleplay(bot))
