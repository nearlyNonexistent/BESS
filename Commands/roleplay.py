from commands import Command
import asyncio
import random


class RoleplayCommands(Command):
    """Roleplay commands are various tools for roleplaying, such as random name generators and dice rollers."""
    async def roll(self, trueself, message):
        """Rolls a random number. One argument: dice notation string."""
        def dieParse(rollString):
            return False  # NYI
        dieCount = dieParse(self.__parse__("roll", message))
        if dieCount:
            await self.client.send_message(message.channel, "result goes here")
        else:
            await self.client.send_message(message.channel, "NYI")

    async def seventhsanctum(self, trueself, message):
        """Returns the first result of a seventhsanctum number generator."""
        return "NYI"
