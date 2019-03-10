"""Cog for BESS. This cog provides mathematics utilities."""
import asyncio
from io import BytesIO

import discord
import matplotlib.font_manager
import matplotlib.pyplot as plt
from asteval import Interpreter
from discord.ext import commands


class Mathematics(commands.Cog):
    """Provides assistance in mathematics operations."""
    def __init__(self, bot):
        self.bot = bot
        self.interpreters = {}

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
        message = message.replace("```python", "")
        message = message.replace("`", "")
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

    @commands.group()
    async def graph(self, ctx):
        """Generate graphs with matplotlib."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")

    @staticmethod
    def _clean_data(message: str):
        """Converts comma-and-colon separated data into two arrays,
        for usage in graph generation."""
        group_names, group_data = message.split(":")
        group_names = group_names.strip().split(",")
        group_data = group_data.strip().split(",")
        for i, datum in enumerate(group_data):
            group_data[i] = float(datum)
        return group_names, group_data

    @staticmethod
    async def _export_graph(ctx, fig):
        """Exports graph to Discord image upload."""
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        await ctx.send(file=discord.File(buf, filename="plot.png"))
        buf.close()
        plt.close(fig)

    @graph.command()
    async def bar(self, ctx, bar_type: str, title: str, y_label: str,
                  x_label: str, *, message: str):
        """Valid types: horizontal, vertical. All chart data is to be
        written in the form of Names:Values, comma separated."""
        bar_type = bar_type.lower()
        group_names, group_data = self._clean_data(message)
        if bar_type != "vertical" and bar_type != "horizontal":
            await ctx.send("Please select a bar type: vertical or horizontal.")
        with plt.xkcd():
            fig, ax = plt.subplots()
            fig.tight_layout(pad=5)
            if bar_type == "vertical":
                ax.bar(group_names, group_data)
            elif bar_type == "horizontal":
                ax.barh(group_names, group_data)
            ax.set(xlabel=x_label, ylabel=y_label, title=title)
            await self._export_graph(ctx, fig)

    @graph.command()
    async def pie(self, ctx, title: str, *, message: str):
        """All chart data is to be written in the form of Names:Values,
        comma separated."""
        group_names, group_data = self._clean_data(message)
        with plt.xkcd():
            fig, ax = plt.subplots()
            fig.tight_layout(pad=2)
            ax.pie(group_data, labels=group_names)
            ax.set_title(title)
            await self._export_graph(ctx, fig)

    @graph.command()
    async def line(self, ctx, format_string: str, title: str, y_label: str,
                   x_label: str, *, message: str):
        """All chart data is to be
        written in the form of X:Y, comma separated between."""
        group_names, group_data = self._clean_data(message)
        for i, datum in enumerate(group_names):
            group_names[i] = float(datum)
        with plt.xkcd():
            fig, ax = plt.subplots()
            fig.tight_layout(pad=2)
            ax.plot(group_names, group_data, format_string)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            await self._export_graph(ctx, fig)

    @graph.command(hidden=True)
    @commands.is_owner()
    async def cache_reload(self, ctx):
        """Rebuilds the font cache."""
        matplotlib.font_manager._rebuild()
        await ctx.message.add_reaction("👍")


def setup(bot):
    """Load the cog."""
    bot.add_cog(Mathematics(bot))
