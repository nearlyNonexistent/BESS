"""Cog for BESS. This cog contains administrative commands."""
import logging
import attr
from discord.ext import commands


@attr.s
class CommandErrorHandler:
    """This handles errors for BESS without overriding local error handlers."""

    bot = attr.ib()

    @bot.check
    async def globally_check_length(self, ctx):
        """Check if the command exceeds max length."""
        return len(ctx.message) > self.bot.config["max-length"]

    async def on_command_error(self, ctx, error):
        """Handle errors."""
        if hasattr(ctx.command, 'on_error'):
            return
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)
        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} is not for PMs.')
            except:
                pass
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('I could not find that member.')
        logging.exception(error)


def setup(bot):
    """Load the cog."""
    bot.add_cog(CommandErrorHandler(bot))
