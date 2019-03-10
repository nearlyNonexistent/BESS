"""Cog for BESS. Generates memes using external API."""
from aiohttp_requests import requests
from discord.ext import commands


class MemeGen(commands.Cog):
    """MemeGen.link interface."""
    @commands.group(invoke_without_command=True)
    async def meme(self, ctx, meme="", top_text="", bottom_text=""):
        """Generates a meme from the memegen.link API."""
        response = await requests.get(
                "https://memegen.link/api/templates/")
        memes = await response.json()
        for api_name, api_key in memes.items():
            if meme.lower() in api_name.lower():
                top_text = await self.clean(top_text)
                bottom_text = await self.clean(bottom_text)
                meme_template = api_key.rsplit('/', 1)[-1]
                await ctx.send(f"https://memegen.link/"
                               f"{meme_template}/"
                               f"{top_text}/"
                               f"{bottom_text}.jpg")
                break
        else:
            await ctx.message.add_reaction("❌")

    @meme.command()
    async def search(self, ctx, *, meme_name: str):
        """Search for valid meme templates."""
        results = "RESULTS:\n"
        response = await requests.get(
                "https://memegen.link/api/templates/")
        memes = await response.json()
        for api_name, api_key in memes.items():
            if meme_name.lower() in api_name.lower():
                results += f"{api_name}\n"
        await ctx.send(results)

    @staticmethod
    async def clean(text):
        """Escapes text into memegen.link format."""
        for replacement in (("_", "__"), ("-", "--"),
                            ("?", "~q"), ("%", "~p"),
                            ("/", "~s"), ("\"", "''"),
                            ("#", "~h"), (" ", "_")):
            text = text.replace(*replacement)
        return text


def setup(bot):
    """Load the cog."""
    bot.add_cog(MemeGen(bot))
