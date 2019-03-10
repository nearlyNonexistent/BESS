"""Cog for BESS. This cog provides a tool for a Q&A led by moderators."""
import discord
import shortuuid
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import database


class QAChannel(database.Database):
    """Q&A channels."""

    async def get_questions(self, uuid=None, answered=False):
        """PostgreSQL query generator for retrieving entries."""
        if uuid:
            self.cur.execute("SELECT * FROM qachannel WHERE uuid=%(uuid)s",
                             {"uuid": uuid})
            row = self.cur.fetchone()
        elif not answered:
            self.cur.execute("SELECT * FROM qachannel WHERE answer IS NULL")
            row = self.cur.fetchall()
        else:
            self.cur.execute("SELECT * FROM qachannel")
            row = self.cur.fetchall()
        return row

    @staticmethod
    async def uuid_format(uuid):
        """Formats UUID by dashes."""
        return "-".join(uuid[i:i+5] for i in range(0, len(uuid), 5))

    @staticmethod
    async def uuid_deformat(uuid):
        """Just removes all the dashes from the UUID."""
        return uuid.replace("-", "")

    async def result_format(self, title, rows):
        """Format results in a list form."""
        result_formatted = title
        for i, result in enumerate(rows):
            result_string = await self.uuid_format(result["uuid"])
            result_formatted += f"{result_string}"
            if result["tags"]:
                result_formatted += " ---- " + str(result["tags"])
            result_formatted += "\n"

    async def embed_generator(self, row):
        """Generate a Q&A embed."""
        user = self.bot.get_user(row["asked_by"])
        answerer = None
        uuid = await self.uuid_format(row["uuid"])
        if row["answered_by"]:
            answerer = self.bot.get_user(row["answered_by"])
        embed = discord.Embed(title="Question", description=row["question"])
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        if row["answer"]:
            embed.add_field(name=f"Answer by {answerer.display_name}",
                            value=row["answer"], inline=False)
        if row["tags"]:
            embed.add_field(name="Tagged", value=row["tags"], inline=False)
        embed.set_footer(text=uuid)
        return embed

    @commands.group()
    async def qna(self, ctx):
        """Questions & Answers commands for moderator-only answers."""
        if ctx.invoked_subcommand is None:
            rows = await self.get_questions()
            if rows:
                result_formatted = await self.result_format(
                        "**Unanswered questions:**\n\n")
                await ctx.send(result_formatted)
            else:
                await ctx.message.add_reaction("❌")

    @qna.command()
    @commands.cooldown(1, 30, BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask a question of the moderators."""
        uuid = shortuuid.uuid()
        self.cur.execute(("INSERT INTO qachannel(uuid, question, asked_by) "
                          "VALUES(%(uuid)s, %(question)s, %(author)s)"),
                          {"uuid": uuid, "question": question,
                           "author": ctx.message.author.id})
        self.conn.commit()
        row = await self.get_questions(uuid=uuid)
        embed = await self.embed_generator(row)
        message = await ctx.send(embed=embed)
        self.cur.execute(("UPDATE qachannel SET channel_id="
                          "%(channel_id)s, message_id="
                          "%(message_id)s WHERE uuid=%(uuid)s"),
                         {"uuid": uuid, "message_id": message.id,
                          "channel_id": message.channel.id})
        self.conn.commit()
        await ctx.message.delete()

    @commands.has_permissions(administrator=True)
    @qna.command()
    async def answer(self, ctx, uuid: str, answer: str, tags=None):
        """Answer a question."""
        cleaned_uuid = await self.uuid_deformat(uuid)
        row = await self.get_questions(uuid=cleaned_uuid)
        tag_array = []
        if tags:
            tag_array = tags.strip().split(",")
        if row:
            self.cur.execute(("UPDATE qachannel SET answer=%(answer)s, "
                              "tags=%(tags)s, answered_by=%(author)s"
                              " WHERE uuid=%(uuid)s"),
                             {"uuid": cleaned_uuid, "answer": answer,
                              "tags": tag_array,
                              "author": ctx.message.author.id})
            self.conn.commit()
        row = await self.get_questions(uuid=cleaned_uuid)
        embed = await self.embed_generator(row)
        channel = self.bot.get_channel(row["channel_id"])
        message = await channel.get_message(row["message_id"])
        await message.edit(embed=embed)
        await ctx.message.delete()

    @commands.has_permissions(administrator=True)
    @qna.command()
    async def tag(self, ctx, uuid: str, *, tags: str):
        """Tag a question in a QA channel. Comma separate tags."""
        cleaned_uuid = await self.uuid_deformat(uuid)
        row = await self.get_questions(uuid=cleaned_uuid)
        tag_array = tags.strip().split(",")
        if row:
            self.cur.execute(("UPDATE qachannel SET tags=%(tags)s"
                              " WHERE uuid=%(uuid)s"),
                             {"uuid": cleaned_uuid, "tags": tag_array})
            self.conn.commit()
        row = await self.get_questions(uuid=cleaned_uuid)
        embed = await self.embed_generator(row)
        channel = self.bot.get_channel(row["channel_id"])
        message = await channel.get_message(row["message_id"])
        await message.edit(embed=embed)
        await ctx.message.delete()

    @commands.has_permissions(administrator=True)
    @qna.command()
    async def delete(self, ctx, uuid: str):
        """Deletes a question and its embed. This cannot be undone."""
        cleaned_uuid = await self.uuid_deformat(uuid)
        row = await self.get_questions(uuid=cleaned_uuid)
        if row:
            self.cur.execute("DELETE FROM qachannel WHERE uuid=%(uuid)s",
                             {"uuid": cleaned_uuid})
            self.conn.commit()
            channel = self.bot.get_channel(row["channel_id"])
            message = await channel.get_message(row["message_id"])
            await message.delete()
            await ctx.message.add_reaction("👍")

    @qna.command()
    async def search(self, ctx, answered: bool, *, search_term: str):
        """Returns list of questions that contain the search term in their
        question, answer, or tag."""
        rows = await self.get_questions(answered=answered)
        results = []
        search_term = search_term.lower()
        for row in rows:
            if search_term in row["question"].lower():
                results.append(row)
                continue
            if row["answer"]:
                if search_term in row["answer"].lower():
                    results.append(row)
                    continue
            if row["tags"]:
                for tag in row["tags"]:
                    if search_term in tag.lower():
                        results.append(row)
                        continue
        if results:
            result_formatted = await self.result_format("**Results:**\n\n",
                                                        results)
            await ctx.send(result_formatted)
        else:
            await ctx.message.add_reaction("❌")

    @qna.command()
    async def mirror(self, ctx, uuid):
        """Mirrors a question to the channel you post in"""
        cleaned_uuid = await self.uuid_deformat(uuid)
        row = await self.get_questions(uuid=cleaned_uuid)
        channel = self.bot.get_channel(row["channel_id"])
        message = await channel.get_message(row["message_id"])
        await message.delete()
        embed = await self.embed_generator(row)
        message = await ctx.send(embed=embed)
        self.cur.execute(("UPDATE qachannel SET channel_id="
                          "%(channel_id)s, message_id="
                          "%(message_id)s WHERE uuid=%(uuid)s"),
                         {"uuid": cleaned_uuid, "message_id": message.id,
                          "channel_id": message.channel.id})
        self.conn.commit()
        await ctx.message.delete()


def setup(bot):
    """Load the cog."""
    bot.add_cog(QAChannel(bot))
