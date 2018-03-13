"""Cog for BESS. This cog provides a simple trivia game."""
# Standard Library Imports
import asyncio
import json
import os
import random
# Third-Party Imports.
import attr
from discord.ext import commands

@attr.s
class Trivia(object):
    """Trivia Game 9000!"""

    bot = attr.ib()

    def __attrs_post_init__(self):
        """Post-initialization after attr."""
        random.seed()
        self.__load_questions()

    def __load_questions(self):
        self.questions = []
        with open(os.path.join(os.getcwd(),
                               "data", "trivia.json")) as questions:
            self.questions = json.load(questions)
        self.categories = []
        for question in self.questions:
            for category in question["categories"]:
                if category not in self.categories:
                    self.categories.append(category)

    def __save_questions(self):
        json.dump(self.questions, open(os.path.join(os.getcwd(),
                                       "data", "trivia.json"), 'w'))

    @commands.group(invoke_without_command=True)
    async def trivia(self, ctx, category="all"):
        """Manage or play trivia."""
        questionsPossible = []
        for question in self.questions:
            for categoryChecked in question["categories"]:
                if category.lower() in categoryChecked.lower():
                    questionsPossible.append(question)
        question = random.choice(questionsPossible)
        await ctx.send(f"Your question is... \n {question['question']}?")

        def check(m):
            check1 = question["answer"].lower() in m.content.lower()
            check2 = not m.author.bot
            return check1 and check2
        try:
            answer = await self.bot.wait_for("message", check=check,
                                             timeout=10)
        except asyncio.TimeoutError:
            await ctx.send(("No one answered! "
                            f" It was...\n {question['answer']}"
                            f" {question['detail']}."))
            return 0
        if answer:
            await ctx.send((f"You got the answer, {answer.author.mention}!"
                            f" It was...\n {question['answer']}"
                            f" {question['detail']}."))
            await answer.add_reaction("🏆")

    @trivia.command()
    @commands.is_owner()
    async def reload(self, ctx):
        """Reload trivia questions."""
        self.__load_questions()
        await ctx.message.add_reaction("👍")

    @trivia.command(aliases=["ls"])
    async def list(self, ctx, qID: int = -1):
        """List total Trivia questions"""
        qID -= 1
        if qID == -2:
            await ctx.send(f"Total trivia questions: {len(self.questions)}")
            await ctx.send(f"Trivia categories: {', '.join(self.categories)}.")
        else:
            await ctx.send(f"Question with that ID:\n{self.questions[qID]}")

    @trivia.command(aliases=["new"])
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, question, answer, detail):
        """Add a new trivia question."""
        self.questions.append({"question": question, "categories": ["all"],
                               "answer": answer, "detail": detail})
        json.dump(self.questions, open(os.path.join(os.getcwd(),
                                       "data", "trivia.json"), 'w'))
        self.__load_questions()
        await ctx.message.add_reaction("👍")

    @trivia.command()
    @commands.has_permissions(administrator=True)
    async def edit(self, ctx, qID: int, newQ, answer, detail):
        """Edit a question by qID."""
        qID -= 1
        try:
            self.questions[qID] = {"question": newQ, "categories": ["all"],
                                   "answer": answer, "detail": detail}
            self.__save_questions()
            await ctx.message.add_reaction("👍")
        except IndexError:
            await ctx.send("No such question!")

    @trivia.command()
    @commands.has_permissions(administrator=True)
    async def tag(self, ctx, qID: int, *, categories: str):
        """Tag categories for a trivia question."""
        qID -= 1
        categories = categories.strip().lower()
        self.questions[qID]["categories"] = json.loads(categories)
        self.questions[qID]["categories"].append("all")
        self.__save_questions()
        self.__load_questions()
        await ctx.message.add_reaction("👍")

    @trivia.command(aliases=["del", "rm"])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, qID: int):
        """Delete trivia question."""
        qID -= 1
        if qID != -2:
            del self.questions[qID]
        else:
            self.questions = []
        self.__save_questions()
        self.__load_questions()
        await ctx.message.add_reaction("👍")

    @trivia.command()
    @commands.has_permissions(administrator=True)
    async def search(self, ctx, *, searchterm: str):
        """Search for questions containing searchterm."""
        searchterm = searchterm.lower()
        searchResults = ""
        for i, q in enumerate(self.questions):
            if searchterm in q["question"].lower() or \
                    searchterm in q["answer"].lower() or \
                    searchterm in q["detail"].lower():
                searchResults += f"{i+1}: {q['question']}?\n"
        await ctx.send(f"Search results:\n{searchResults}")


def setup(bot):
    """Load the cog."""
    bot.add_cog(Trivia(bot))
