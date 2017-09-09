import asyncio

class Command(object):
    """The command object implements a series of commands as functions,
    and reports them back to the CommandHolder."""
    def __init__(self, client):
        """Each command object needs to make a list of all commands implemented.
        This ignores internal commands like __parse__."""
        self.attributes = []
        self.client = client
        for func in dir(self):
            if callable(getattr(self, func)) and not func.startswith("__"):
                self.attributes.append(getattr(self, func))

    def __mention__(self, id):
        """Internal command used to generate a mention."""
        return f"<@{id}>"

    def __parse__(self, function, message):
        """Internal command used to parse for arguments,
        separated by whitespace."""
        result = message.content[(len(function)+1):].split()
        if result:
            return result
        else:
            return [""]

    async def __respondPing__(self, message, text):
        """Respond to a user with a ping wrapped around the message."""
        return await self.client.send_message(message.channel,
                                              f"{self.__mention__(message.author.id)}: {text}")

# hack hack HACK!
# all commands need to be added below here, until
# a better solution has been found
# possibly a configuration file?
# unfortunately violates PEP8 too -- can't
# have it before the definition of Command!

from .basic import *
from .example import *
from .roleplay import *
from .flavor import *


class CommandHolder:
    """The CommandHolder is used to call commands,
    doing some basic parsing and matching."""
    def __init__(self, client, config, voiceclient):
        """The primary purpose of these variables are to store settings for the
        commands themselves to use, and to store a list of every command."""
        self.client = client
        self.config = config
        self.voiceclient = voiceclient
        self.commandList = []
        self.stop = False
        self.commandObjects = [cls(self.client) for cls in
                               Command.__subclasses__()]
        commandListNames = []
        for command in self.commandObjects:
            for commandFinal in command.attributes:
                self.commandList.append(commandFinal)
                commandListNames.append(commandFinal.__name__)
        print(f"Loaded commands: {commandListNames}")

    async def __call__(self, message):
        """This function is used to find the relevant command and pass it
        the settings and arguments it needs."""
        message.content = message.content.lower()
        matchFound = False
        for possibleCommand in self.commandList:
            if message.content.startswith(possibleCommand.__name__):
                matchFound = True
                break
        # include semi-commands
        if matchFound:
            await possibleCommand(self, message)
        else:
            await self.unknownCommand(message)
        if self.config.debug:
            print(f"Stop Toggle: {self.stop}.")
        return self.stop

    async def unknownCommand(self, message):
        await self.client.add_reaction(message, "❓")
