from commands import Command
import asyncio
import discord
import time


class BasicCommands(Command):
    """The Basic Commands are essentially simple commands used as\
    a core for the rest of the bot. Debug commands, etc."""
    async def __unknownCommand__(self, trueself, message):
        await self.__respond__(message, f"Unknown command: {argument}")

    async def helpme(self, trueself, message):
        """Helpme lists all the commands. For more details about a command,\
        use inspector."""
        await self.client.add_reaction(message, "ℹ")
        commandListNames = []
        for command in trueself.commandList:
            commandListNames.append(command.__name__)
        await self.__respond__(message,
                               f"Commands: {str(commandListNames)}.")

    async def inspector(self, trueself, message):
        """Inspector gives details on a specific command."""
        await self.client.add_reaction(message, "🔎")
        matchFound = False
        argument = self.__parse__("inspector", message)[0]
        for command in trueself.commandList:
            if command.__name__ == argument:
                matchFound = command
        if matchFound:
            if matchFound.__doc__:
                await self.__respond__(message, ("Info: "
                                       f"{matchFound.__doc__}"))
            else:
                await self.__respond__(message, ("No info! Bug "
                                       f"{self.__mention__(trueself.config.owner)}."))
        else:
            await self.__respond__(message, f"Unknown command: {argument}")

    async def stop(self, trueself, message):
        """Disables the bot."""
        if message.author.id == trueself.config.owner:
            trueself.stop = True
            await self.__respond__(message, "Disabling.")
            await self.client.add_reaction(message, "🛏")
        else:
            await self.__respond__(message,
                                   ("I'm sorry, "
                                    f"{self.__mention__(message.author.id)}, "
                                    "I'm afraid I can't "
                                    "let you do that."))
            await self.client.add_reaction(message, "🔴")

    async def info(self, trueself, message):
        """Basic information about the bot."""
        embed = discord.Embed(title="BESS Extends Server Systems",
                              url='https://github.com/nearlyNonexistent/BESS',
                              description=("BESS is a bot that runs on "
                                           "Python. Developed by nearlyNonexis"
                                           "tent. Use 'helpme' for a list of c"
                                           "ommands, and 'inspector [command]'"
                                           "for information on one. Have a nic"
                                           "e day!"))
        embed.add_field(name="Version", value=trueself.config.version,
                        inline=False)
        embed.add_field(name="Servers", value=len(self.client.servers),
                        inline=True)
        embed.add_field(name="Commands", value=len(trueself.commandList),
                        inline=True)
        embed.add_field(name="Owner",
                        value=self.__mention__(trueself.config.owner),
                        inline=True)
        embed.set_footer(text=f"Generated {time.strftime('%x')}")
        await self.__respond__(message, embed=embed)
        await self.client.add_reaction(message, "🐄")
