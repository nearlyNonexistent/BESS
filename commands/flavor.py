from commands import Command
import asyncio
import random


class FlavorCommands(Command):
    """Flavor commands for fun."""
    async def moo(self, trueself, message):
        """Random cow image"""
        with open("data/cows") as f:
            cows = f.read().split()
        await self.__respond__(message, "Moo. " + random.choice(cows))
        await self.client.add_reaction(message, "🐮")

    async def kickflip(self, trueself, message):
        """Kicks."""
        arguments = self.__parse__("kickflip", message)
        print(arguments)
        with open("data/kickflips") as f:
            kickflips = f.read().split("\n")
        if arguments[0]:
            await self.__respond__(message,
                                   (f"*kickflips into {arguments[0]} "
                                    "bouncing them "
                                    f"into {random.choice(kickflips)}!*"))
            if message.author.id == trueself.config.attrs["owner"]:
                if arguments[1]:
                    if arguments[1] == "hardcore":
                        banUser = False
                        for members in message.server.members:
                            if f"<@{members.id}>" == arguments[0]:
                                banUser = members
                                print("match found")
                        if banUser:
                            await self.client.kick(banUser)
                            await self.__repsond__(message,
                                                   ("*and out of the"
                                                    " server!*"))
        else:
            await self.__respond__(message,
                                   ("*kickflips into "
                                    f"{random.choice(kickflips)}!*"))
