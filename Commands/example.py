from commands import Command
import asyncio
import codecs
import random
import string

class TemplateCommands(Command):
    """The TemplateCommands are just a template for future commands. Includes several example commands for voice and text."""
    async def test(self, trueself, message):
        """Test does nothing but count your messages then repeat back what you said."""
        counter = 0
        tmp = await self.client.send_message(message.channel, 'Calculating messages...')
        async for log in self.client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await self.client.send_message(message.channel, f"You said: {message.content}")
        await self.client.edit_message(tmp, 'You have {} messages.'.format(counter))

    async def sleep(self, trueself, message):
        """Sleep waits for 5 seconds then says it's done. Only for diagnostics."""
        await asyncio.sleep(5)
        await self.client.send_message(message.channel, 'Done sleeping')