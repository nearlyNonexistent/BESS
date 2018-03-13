"""Cog for BESS. This cog provides a simple trivia game."""
# Standard Library Imports
import json
import os
# Third-Party Imports.
import attr
from discord.ext import commands


@attr.s
class Notes(object):
    """Note-taking & reminders."""

    bot = attr.ib()

    @commands.group(aliases=["notes"], invoke_without_command=True)
    async def note(self, ctx, id: int = -1):
        """Note-keeping commands."""
        id -= 1
        notes = self.__load_notes(ctx.author.id)
        if id < 0:
            notesend = "Your notes:\n"
            if len(notes) <= 0:
                notesend = "You don't have any notes!"
            for i, note in enumerate(notes):
                notesend += (f"{i+1}:\n    {note}\n")
        else:
            if notes[id]:
                notesend = f"Your note number: {id+1}:\n    {notes[id]}"
            else:
                notesend = "You don't have a note with that ID!"
        if len(str(notes)) < 80:
                await ctx.send(notesend)
        else:
            await ctx.author.send(notesend)

    def __load_notes(self, user):
        usernotes = []
        filename = os.path.join(os.getcwd(),
                                "data", "notes", f"{user}_notes.json")
        try:
            with open(filename) as notes:
                usernotes = json.load(notes)
        except FileNotFoundError:
            with open(filename, 'w') as notes:
                json.dump([], notes)
        except ValueError:
            pass
        return usernotes

    def __save_notes(self, notedata, user):
        filename = os.path.join(os.getcwd(),
                                "data", "notes", f"{user}_notes.json")
        with open(filename, 'w') as notes:
            json.dump(notedata, notes)

    @note.command(aliases=["list", "ls"])
    async def read(self, ctx, id: int = -1):
        """Read your notes either by index or all notes."""
        await ctx.invoke(self.bot.get_command("note"))

    @note.command(aliases=["add"])
    async def new(self, ctx, *, noteText):
        """Create new notes entry."""
        notes = self.__load_notes(ctx.author.id)
        notes.append(noteText)
        self.__save_notes(notes, ctx.author.id)
        await ctx.message.add_reaction("👍")

    @note.command(aliases=["remove", "rm", "del"])
    async def delete(self, ctx, noteID: int):
        """Delete a notes entry. -1 deletes all notes."""
        noteID -= 1
        notes = self.__load_notes(ctx.author.id)
        try:
            if noteID == -2:
                notes = []
                self.__save_notes(notes, ctx.author.id)
            elif notes[noteID]:
                del notes[noteID]
                self.__save_notes(notes, ctx.author.id)
            await ctx.message.add_reaction("👍")
        except IndexError:
            await ctx.send("You don't have a note with that ID!")

    @note.command()
    async def edit(self, ctx, noteID: int, *, newText):
        """Edit a note entry."""
        noteID -= 1
        notes = self.__load_notes(ctx.author.id)
        try:
            notes[noteID] = newText
            self.__save_notes(notes, ctx.author.id)
            await ctx.message.add_reaction("👍")
        except IndexError:
            await ctx.send("You don't have a note with that ID!")


def setup(bot):
    """Load the cog."""
    bot.add_cog(Notes(bot))
