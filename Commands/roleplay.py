from commands import Command
import asyncio
import random


class RoleplayCommands(Command):
    """Roleplay commands are various tools for roleplaying, such as\
    random name generators and dice rollers."""
    async def roll(self, trueself, message):
        """Rolls a random number. One argument: dice notation string."""
        await self.client.add_reaction(message, "🎲")

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

    async def flip(self, trueself, message):
        """Flips a heart shaped coin."""
        coin = await self.__respondPing__(message,
                                          ("Okay, let's flip a coin... "
                                           "green is heads, red is tails."))
        await asyncio.sleep(1)
        result = random.randrange(1, 6000)
        if trueself.config.debug:
            print(f"Result: {result}")
        if result == 1:
            flipResult = "💛"  # yellow
            await self.client.edit_message(coin,
                                           coin.contents +
                                           ("... it landed on its side! "
                                            "That's a 1/6000 chance!"))
        elif result <= 3060:   # 51% of 6000
            flipResult = "💚"  # green
        else:
            flipResult = "❤"  # red
        await self.client.add_reaction(message, flipResult)
