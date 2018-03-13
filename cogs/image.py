"""Cog for BESS. Manipulates images."""
# Standard Library Imports.
import asyncio
from io import BytesIO
import logging
import os
# Third Party Imports.
import aiohttp
import attr
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


@attr.s
class ImageManip(object):
    """Image manipulation commands."""

    bot = attr.ib()

    def __attrs_post_init__(self):
        """Post-initialization after attr."""
        self.image_array = os.listdir(os.path.join(os.getcwd(),
                                      "data", "image"))
        self.fontfile = os.path.join(os.getcwd(),
                                     "data", "font", "impact.ttf")

    async def _image_reload(self):
        self.image_array = os.listdir(os.path.join(os.getcwd(),
                                      "data", "image"))

    async def outline_text(self, drobject, x, y, text,
                           fillcolor, shadowcolor, fontobj):
        """Outline text with shadowcolor."""
        drobject.text((x - 1, y), text, font=fontobj, fill=shadowcolor)
        drobject.text((x + 1, y), text, font=fontobj, fill=shadowcolor)
        drobject.text((x, y - 1), text, font=fontobj, fill=shadowcolor)
        drobject.text((x, y + 1), text, font=fontobj, fill=shadowcolor)
        drobject.text((x - 1, y - 1), text, font=fontobj, fill=shadowcolor)
        drobject.text((x + 1, y - 1), text, font=fontobj, fill=shadowcolor)
        drobject.text((x - 1, y + 1), text, font=fontobj, fill=shadowcolor)
        drobject.text((x + 1, y + 1), text, font=fontobj, fill=shadowcolor)
        drobject.text((x, y), text, font=fontobj, fill=fillcolor)

    @commands.command(name="meme")
    async def makememe(self, ctx, memename="",
                       toptext="", middletext="", bottomtext=""):
        """Create a meme."""
        toptext = toptext.upper()
        middletext = middletext.upper()
        bottomtext = bottomtext.upper()
        if len(memename + toptext + middletext + bottomtext) <= 1:
            await ctx.send(f"List of memes: {self.image_array}")
            return False
        if memename in self.image_array:
            base = Image.open(os.path.join(os.getcwd(),
                                           "data", "image", memename))
        d = ImageDraw.Draw(base)
        width, height = base.size
        drawqueue = []
        for text in [toptext, middletext, bottomtext]:
            if not text:
                text = " "
            fontsize = 0
            line = ImageFont.truetype(self.fontfile, fontsize)
            while line.getsize(text)[0] < (width * 0.4):
                fontsize += 2
                line = ImageFont.truetype(self.fontfile, fontsize)
                logging.info(f"font size: {fontsize}")
            fontsize -= 2
            if fontsize < 16:
                raise commands.UserInputError(ctx)
            logging.info(f"Final font size: {fontsize}")
            textw, texth = d.textsize(text, font=line)
            drawqueue.append([text, ((width - textw) / 2),
                             ((height - texth) / 2), texth, line, fontsize])

        for i, text in enumerate(drawqueue):
            if i == 0:
                texth = 0 - (text[4].getoffset(text[0])[0])
            elif i == 1:
                texth = text[2]
            elif i == 2:
                texth = height - (text[3] + 4)
            await self.outline_text(d, text[1],
                                    texth, text[0], "white", "black", text[4])

        output = BytesIO()
        base.save(output, "PNG")
        output.seek(0)
        await ctx.send(file=discord.File(output, filename="meme.png"))

    @commands.group()
    async def image(self, ctx):
        """Image listing and modification."""
        def check(m):
            return m.author.id == ctx.author.id and \
                   m.content in self.image_array
        if ctx.invoked_subcommand is None:
            filen = False
            try:
                filen = await self.bot.wait_for("message", check=check,
                                                timeout=10)
                filen = filen.content
            except asyncio.TimeoutError:
                await ctx.send(("Invalid subcommand. Either provide a"
                                " subcommand or image to display."))
            if filen:
                output = open(os.path.join(os.getcwd(),
                              "data", "image", filen), 'rb')
                await ctx.send(file=discord.File(output, filename="image.png"))

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
