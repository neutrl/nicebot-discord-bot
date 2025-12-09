"""Dallas trigger module - responds to messages containing 'fuck dallas'."""

from . import BaseModule


class DallasTriggerModule(BaseModule):
    """Module that responds 'go birds.' to messages containing 'fuck dallas'."""

    @property
    def name(self) -> str:
        return "dallas_trigger"

    @property
    def description(self) -> str:
        return "Responds 'go birds.' to messages containing 'fuck dallas'"

    async def setup(self):
        """Set up the dallas trigger module."""
        self.bot.add_listener(self.on_message, 'on_message')
        print(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the dallas trigger module."""
        self.bot.remove_listener(self.on_message, 'on_message')

    async def on_message(self, message):
        """Handle messages containing 'fuck dallas'."""
        # Don't respond to the bot's own messages
        if message.author == self.bot.user:
            return

        message_lower = message.content.lower()

        # Check if the message contains "fuck dallas"
        if 'fuck dallas' in message_lower:
            await message.channel.send('go birds.')
