"""Cog for BESS. This cog provides mathematics utilities."""
# Standard Library imports
import asyncio
import io
# Third-party imports
import attr
import discord
from discord.ext import commands
from asteval import Interpreter
import matplotlib.pyplot as plt
import numpy as np


@attr.s
class Math(object):
    """Provides mathematics utilities."""

    bot = attr.ib()

    def __attrs_post_init__(self):
        """Create interpreter array."""
        self.interpreters = {}

    @commands.group()
    async def math(self, ctx):
        """Do math with an integrated Python interpreter."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")

    @math.group(invoke_without_command=True)
    async def clear(self, ctx):
        """Clear the state of your personal interpreter."""
        try:
            del self.interpreters[ctx.author.id]
        except KeyError:
            await ctx.message.add_reaction("👍")
        self.interpreters[ctx.author.id] = Interpreter(no_print=True)
        await ctx.message.add_reaction("👍")

    @clear.command()
    @commands.is_owner()
    async def interpreters(self, ctx):
        """Clear any outstanding interpreter assigned to you."""
        for i in self.interpreters:
            del i
        await ctx.message.add_reaction("👍")

    @clear.command()
    @commands.is_owner()
    async def plots(self, ctx):
        """Clear any outstanding figures."""
        plt.close("all")
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

    @math.group(invoke_without_command=True)
    async def plot(self, ctx, formatstring, title,
                   xlabel, ylabel, *, message: str):
            """Create various kinds of graphs using Matplotlib!"""
            if ctx.invoked_subcommand is None:
                await ctx.send("Invalid subcommand.")

    @plot.command()
    async def line(self, ctx, formatstring, title,
                   xlabel, ylabel, *, message: str):
        """Create a line graph."""
        with plt.xkcd():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            inputs = message.split(":")
            labels = inputs[0].split(",")
            for k, v in enumerate(labels):
                labels[k] = v.strip()
            index = np.arange(len(labels))
            for k, v in enumerate(labels):
                labels[k] = v.strip()
            nums = [float(s) for s in inputs[1].split(',')]
            if len(labels) != len(nums):
                raise ValueError
            index = np.arange(len(labels))
            ax.plot(nums, formatstring)
            ax.set_ylim(ymin=0)
            ax.set_xticks(index)
            ax.set_xticklabels(labels)
            ax.set_title(title)
            ax.grid(True)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            await self.__upload_plot(ctx, fig)

    @plot.command()
    async def bar(self, ctx, title,
                  xlabel, ylabel, *, message: str):
        """Create a vertical bar chart."""
        await self.__create_bar(ctx, title, ylabel, xlabel, message)

    @plot.command()
    async def hbar(self, ctx, title,
                   ylabel, xlabel, *, message: str):
        """Create a horizontal bar chart."""
        await self.__create_bar(ctx, title, ylabel,
                                xlabel, message, horizontal=True)

    @plot.command()
    async def pie(self, ctx, title, *, message: str):
        """Create a pie chart."""
        with plt.xkcd(scale=0.5):
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            inputs = message.split(":")
            labels = inputs[0].split(",")
            for k, v in enumerate(labels):
                labels[k] = v.strip()
            bars = [float(s) for s in inputs[1].split(',')]
            if len(labels) != len(bars):
                raise ValueError
            ax.pie(bars, labels=labels, autopct='%1i%%')
            ax.axis('equal')
            ax.set_title(title)
            await self.__upload_plot(ctx, fig)

    async def __upload_plot(self, ctx, fig):
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, filename="plot.png"))

    async def __create_bar(self, ctx, title,
                           ylabel, xlabel, message, horizontal=None):
        with plt.xkcd():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            inputs = message.split(":")
            labels = inputs[0].split(",")
            for k, v in enumerate(labels):
                labels[k] = v.strip()
            bars = [float(s) for s in inputs[1].split(',')]
            if len(labels) != len(bars):
                raise ValueError
            index = np.arange(len(labels))
            if horizontal:
                ax.barh(index, bars, 0.4)
                ax.set_xlim(left=0)
                ax.set_yticks(index)
                ax.set_yticklabels(labels)
            else:
                ax.bar(index, bars, 0.4)
                ax.set_ylim(bottom=0)
                ax.set_xticks(index)
                ax.set_xticklabels(labels)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            await self.__upload_plot(ctx, fig)


def setup(bot):
    """Load the cog."""
    bot.add_cog(Math(bot))
