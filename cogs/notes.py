"""Cog for BESS. This cog provides a note-keeping system."""
from discord.ext import commands

import database


class Notes(database.Database):
    """Note-taking & reminders."""
    async def get_note(self, user_id, note_title=None):
        """PostgreSQL retrieval query generator."""
        if not note_title:
            self.cur.execute("SELECT * FROM notes WHERE uid=%(uid)s",
                             {"uid": user_id})
            row = self.cur.fetchall()
        else:
            self.cur.execute(("SELECT * FROM notes WHERE uid=%(uid)s AND "
                             "note_title=%(note_title)s"),
                             {"uid": user_id, "note_title": note_title})
            row = self.cur.fetchone()
        return row

    @staticmethod
    async def format_notes(note_array):
        """Formats notes into a list."""
        cleaned = "***Your notes:*** \n\n"
        for note in note_array:
            cleaned += f"**{note['note_title']}**:\n    {note['contents']}\n\n"
        return cleaned

    @commands.group()
    async def notes(self, ctx):
        """Note-taking commands. Use without a subcommand to have your notes
        PMed to you."""
        if ctx.invoked_subcommand is None:
            rows = await self.get_note(ctx.message.author.id)
            if rows:
                notes = await self.format_notes(rows)
                await ctx.message.author.send(notes)
            else:
                await ctx.message.add_reaction("❌")

    @notes.command()
    async def write(self, ctx, note_title: str, *, content: str):
        """Write a note."""
        note = await self.get_note(ctx.message.author.id, note_title)
        if note:
            await ctx.send("Note already exists!")
        else:
            self.cur.execute(("INSERT INTO notes VALUES(%(uid)s, "
                              "%(note_title)s, "
                              "%(contents)s)"), {"uid": ctx.message.author.id,
                                                 "note_title": note_title,
                                                 "contents": content})
            self.conn.commit()
            await ctx.message.add_reaction("👍")

    @notes.command()
    async def delete(self, ctx, note_title: str):
        """Delete one of your notes."""
        note = await self.get_note(ctx.message.author.id, note_title)
        if note:
            self.cur.execute(("DELETE FROM notes WHERE uid=%(uid)s AND "
                             "note_title=%(note_title)s"),
                             {"uid": ctx.message.author.id,
                              "note_title": note_title})
            self.conn.commit()
            await ctx.message.add_reaction("👍")

    @notes.command()
    async def edit(self, ctx, note_title: str, *, contents: str):
        """Edit an existing note."""
        note = await self.get_note(ctx.message.author.id, note_title)
        if note:
            self.cur.execute(("UPDATE notes SET contents=%(contents)s "
                              "WHERE uid=%(uid)s "
                              "AND note_title=%(note_title)s"),
                    {"contents": contents, "uid": ctx.message.author.id,
                     "note_title": note_title})
            self.conn.commit()
            await ctx.message.add_reaction("👍")

    @notes.command()
    async def search(self, ctx, *, search_term: str):
        """Search through your notes. (Results are public!)"""
        notes = await self.get_note(ctx.message.author.id)
        results = [note for note in notes
                   if search_term.lower() in note["contents"].lower()
                   or search_term.lower() in note["note_title"].lower()]
        if results:
            formatted = await self.format_notes(results)
            await ctx.send(formatted)
        else:
            await ctx.message.add_reaction("❌")


def setup(bot):
    """Load the cog."""
    bot.add_cog(Notes(bot))
