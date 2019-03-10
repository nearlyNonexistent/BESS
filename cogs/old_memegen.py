"""Cog for BESS. Manipulates images"""
# Standard Library Imports.
from io import BytesIO
import os
from functools import partial
from itertools import product
# Third Party Imports.
import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


class ImageManip(commands.Cog):
    """Image manipulation commands."""
    def __init__(self, bot):
        self.bot = bot
        self.image_array = os.listdir(os.path.join(os.getcwd(),
                                      "data", "image"))
        self.font_file = os.path.join(os.getcwd(),
                                      "data", "font", "impact.ttf")

    async def _image_reload(self):
        self.image_array = os.listdir(os.path.join(os.getcwd(),
                                      "data", "image"))

    @staticmethod
    async def outline_text(draw_surface, coords, draw_text, font):
        """Creates filled text with the outline in shadow_color.
        Functions by creating a partially filled out function stub, then
        replacing the coordinates with calculated offsets from the base
        coordinates. """
        draw = partial(draw_surface.text, text=draw_text, font=font,
                       fill="black")
        for offset_pair in product(range(-1, 2), repeat=2):
            draw((coords[0]+offset_pair[0], coords[1]+offset_pair[1]))
        draw(coords, fill="white")

    @commands.command(name="meme")
    async def make_meme(self, ctx, meme_name="",
                        top_text="", middle_text="", bottom_text=""):
        """Create a meme!"""
        if meme_name not in self.image_array:
            await ctx.send(f"List of memes: {self.image_array}")
            return False
        else:
            base = Image.open(os.path.join(os.getcwd(),
                                           "data", "image", meme_name))
            canvas = ImageDraw.Draw(base)
        width, height = base.size
        draw_queue = []
        texts = [top_text, middle_text, bottom_text]
        # if no bottom_text, convert middle_text to bottom_text
        if len(bottom_text) <= 1:
            texts[2] = middle_text
            texts[1] = ""
        # Processing text sizes for draw queue
        for text in texts:
            if not text:
                draw_queue.append({"skip":True})
                continue
            text = text.upper()
            font_size = 10
            line = ImageFont.truetype(self.font_file, font_size)
            # Until we reach 90% of the canvas size, keep scaling the text up.
            # No, I don't think there's a faster way.
            while line.getsize(text)[0] < (width * 0.9):
                font_size += 2
                line = ImageFont.truetype(self.font_file, font_size)
            font_size -= 2
            text_width, text_height = canvas.textsize(text, font=line)
            draw_queue.append({"text": text, "size": font_size, "skip": False,
                               "centers": ((width - text_width)/2,
                                           (height-text_height)/2),
                               "height": text_height, "font": line})
        for i, text in enumerate(draw_queue):
            text_height = 0
            if text["skip"]:
                continue
            if i == 0:
                text_height = 0 - (text["font"].getoffset(text["text"])[0])
            elif i == 1:
                text_height = text["centers"][1]
            elif i == 2:
                text_height = height - (text["height"] + 4)
            await self.outline_text(canvas, (text["centers"][0], text_height),
                                    text["text"],
                                    text["font"])
        # Outputting file
        output = BytesIO()
        base.save(output, "PNG")
        output.seek(0)
        await ctx.send(file=discord.File(output, filename="meme.png"))
        output.close()

    @commands.group()
    async def image(self, ctx):
        """Image listing and modification."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"List of images: {str(self.image_array)}")

    @image.command()
    @commands.is_owner()
    async def reload(self, ctx):
        """Reload the meme list."""
        await self._image_reload()
        await ctx.message.add_reaction("👍")

    @image.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, url, name):
        """Add an image to BESS's meme repository."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.read()
                with open(os.path.join(os.getcwd(), "data",
                          "image", name), "wb") as img:
                    img.write(data)
                    await self._image_reload()
                    await ctx.message.add_reaction("👍")


def setup(bot):
    """Load the cog."""
    bot.add_cog(ImageManip(bot))
