"""Cog for BESS. This cog provides a simple trivia game."""
import asyncio
import json
import os
import random

from discord.ext import commands

import database


class Trivia(database.Database):
    """Trivia Game 9000!"""
    pass


class Trivia(commands.Cog):
    """Trivia Game 9000!"""
    def __init__(self, bot):
        self.bot = bot
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
        questions_possible = []
        for question in self.questions:
            for categoryChecked in question["categories"]:
                if category.lower() in categoryChecked.lower():
                    questions_possible.append(question)
        question = random.choice(questions_possible)
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
    async def list(self, ctx, question_id: int = -1):
        """List total Trivia questions"""
        question_id -= 1
        if question_id == -2:
            await ctx.send(f"Total trivia questions: {len(self.questions)}")
            await ctx.send(f"Trivia categories: {', '.join(self.categories)}.")
        else:
            await ctx.send((f"Question with that ID:\n"
                           f"{self.questions[question_id]}"))

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
    async def edit(self, ctx, question_id: int, newQ, answer, detail):
        """Edit a question by question_id."""
        question_id -= 1
        try:
            self.questions[question_id] = {"question": newQ,
                                           "categories": ["all"],
                                           "answer": answer, "detail": detail}
            self.__save_questions()
            await ctx.message.add_reaction("👍")
        except IndexError:
            await ctx.send("No such question!")

    @trivia.command()
    @commands.has_permissions(administrator=True)
    async def tag(self, ctx, question_id: int, *, categories: str):
        """Tag categories for a trivia question."""
        question_id -= 1
        categories = categories.strip().lower()
        self.questions[question_id]["categories"] = json.loads(categories)
        self.questions[question_id]["categories"].append("all")
        self.__save_questions()
        self.__load_questions()
        await ctx.message.add_reaction("👍")

    @trivia.command(aliases=["del", "rm"])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, question_id: int):
        """Delete trivia question."""
        question_id -= 1
        if question_id != -2:
            del self.questions[question_id]
        else:
            self.questions = []
        self.__save_questions()
        self.__load_questions()
        await ctx.message.add_reaction("👍")

    @trivia.command()
    @commands.has_permissions(administrator=True)
    async def search(self, ctx, *, search_term: str):
        """Search for questions containing search_term."""
        search_term = search_term.lower()
        search_results = ""
        for i, q in enumerate(self.questions):
            if search_term in q["question"].lower() or \
                    search_term in q["answer"].lower() or \
                    search_term in q["detail"].lower():
                search_results += f"{i+1}: {q['question']}?\n"
        await ctx.send(f"Search results:\n{search_results}")


def setup(bot):
    """Load the cog."""
    bot.add_cog(Trivia(bot))
