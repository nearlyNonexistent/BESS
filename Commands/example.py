from commands import Command
import asyncio


class TemplateCommands(Command):
    """The TemplateCommands are just a template for future commands.
    Mostly example commands for voice and text."""
    async def test(self, trueself, message):
        """Test does nothing but count your messages then repeat back yours."""
        counter = 0
        tmp = await self.client.send_message(message.channel,
                                             'Calculating messages...')
        async for log in self.client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await self.client.send_message(message.channel,
                                       f"You said: {message.content}")
        await self.client.edit_message(tmp,
                                       'You have {} messages.'.format(counter))

    async def sleep(self, trueself, message):
        """Sleep waits for 5 seconds then responds. Only for diagnostics."""
        await asyncio.sleep(5)
        await self.client.send_message(message.channel,
                                       'Done sleeping')
