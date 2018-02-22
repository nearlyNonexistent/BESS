"""Cog for BESS. This cog provides a simple trivia game."""
import attr
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


@attr.s
class QAChannel(object):
    """For running a Q&A channel with limited access to regular users."""

    bot = attr.ib()

    def __attrs_post_init__(self):
        """Post-initialization after attr."""
        self.lastMesage = []

    @commands.command()
    @commands.cooldown(1, 30, BucketType.user)
    async def question(self, ctx, *, message: str):
        """Ask a question to a QA channel."""
        await ctx.message.delete()
        channel = discord.utils.get(ctx.guild.channels, name='questions')
        embed = discord.Embed(title="Asked:", description=message)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        self.lastEmbed = embed
        self.lastMessage = await channel.send("Unanswered question:",
                                              embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def answer(self, ctx, *, message: str):
        """Answer a question in a QA channel."""
        if self.lastMessage:
            await ctx.message.delete()
            self.lastEmbed.description = (f"{self.lastEmbed.description}\n\n"
                                          f"***ANSWER BY {ctx.author.name}:***"
                                          f"\n    {message}")
            await self.lastMessage.edit(content="Question answered:",
                                        embed=self.lastEmbed)
        else:
            await ctx.send("No question queued to be answered!")


def setup(bot):
    """Load the cog."""
    bot.add_cog(QAChannel(bot))
