"""Cog for BESS. This cog contains administrative commands."""
# Standard Library Imports.
import io
import json
import logging
# Third-Party Imports.
import asyncio
import textwrap
import traceback
import attr
import discord
from contextlib import redirect_stdout
import inspect
from discord.ext import commands


@attr.s
class Mod(object):
    """Moderation-only commands."""

    bot = attr.ib()
    sessions = attr.ib(default=set())

    def cleanup_code(self, content):
        """Automatically remove code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    def get_syntax_error(self, e):
        """Retrieve syntax errors from REPL sessions."""
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return (f'```py\n{e.text}{"^":>{e.offset}}'
                f'\n{e.__class__.__name__}: {e}```')

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
        """Check the BESS version versus latest on GitHub."""
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

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
            """Run and evaluate code."""
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message
            }

            env.update(globals())

            body = self.cleanup_code(body)
            stdout = io.StringIO()

            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

            try:
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction('\u2705')
                except:
                    pass
                if ret is None:
                    if value:
                        await ctx.send(f'```py\n{value}\n```')
                else:
                    self._last_result = ret
            await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command()
    @commands.is_owner()
    async def repl(self, ctx):
        """Launch an interactive REPL session."""
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send(('Already running a REPL session in this channel. '
                           'Exit it with `quit`.'))
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send(('Enter code to execute or evaluate.'
                       ' `exit()` or `quit` to exit.'))

        def check(m):
            return m.author.id == ctx.author.id and \
                   m.channel.id == ctx.channel.id and \
                   m.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check,
                                                   timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.')
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f'Unexpected error: `{e}`')


def setup(bot):
    """Load the cog."""
    bot.add_cog(Mod(bot))
