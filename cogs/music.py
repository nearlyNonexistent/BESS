"""Cog for BESS. Controls music."""
# Standard Library imports.
import asyncio
import os
# Third Party imports.
import discord
import youtube_dl
from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(os.getcwd(),
                            "data", "music", '%(extractor)s-%(id)s-%(title)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, ytdl.extract_info, url)
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@attr.s
class Music:
    bot = attr.ib()

    @commands.group()
    async def music(self, ctx):
        """Control music."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")

    @music.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @music.command()
    async def local_play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        if ctx.voice_client is None:
            if ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("Not connected to a voice channel.")
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send(f"Now playing: {query}")

    @music.command(aliases=["play", "yt"])
    async def stream(self, ctx, *, url):
        """Streams from a url (almost anything youtube_dl supports)"""
        if ctx.voice_client is None:
            if ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("Not connected to a voice channel.")
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        player = await YTDLSource.from_url(url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send(f"Now playing: {player.title}")

    @music.command()
    async def volume(self, ctx, volume: int = -1):
        """Change the player's volume, 0-100 integer."""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if volume != -1:
            ctx.voice_client.source.volume = volume
            await ctx.send(f"Changed volume to {volume}%.")
        else:
            ctx.send(f"Volume is: {volume}%")

    @music.command()
    async def stop(self, ctx):
        """Stop and disconnect the bot from voice"""
        await ctx.voice_client.disconnect()


def setup(bot):
    """Load the cog."""
    bot.add_cog(Music(bot))
