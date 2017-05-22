from commands import Command
import asyncio


class BasicCommands(Command):
    """The Basic Commands are essentially simple commands used to determine functionality of the bot. Debug commands and such are the most important."""
    async def helpme(self, trueself, message):
        """Helpme lists all the commands. For more details about a command, use inspector."""
        commandListNames = []
        for command in trueself.commandList:
            commandListNames.append(command.__name__)
        await self.client.send_message(message.channel, f"List of commands: {str(commandListNames)}.")

    async def inspector(self, trueself, message):
        """Inspector gives details on a specific command."""
        flag = False
        for command in trueself.commandList:
            argument = self.__parse__("inspector", message)[0]
            if command.__name__ == argument:
                flag = True
                if command.__doc__:
                    await self.client.send_message(message.channel, f"Command details: {command.__doc__}")
                else:
                    await self.client.send_message(message.channel, f"No documentation. Bug {self.__mention__(trueself.config.owner)}.")
        if not flag:
            await self.client.send_message(message.channel, f"Unknown command: {argument}")