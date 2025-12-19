"""Shut up trigger module - responds to messages containing 'shut up'."""

from . import BaseModule


class ShutUpTriggerModule(BaseModule):
    """Module that responds 'No, u!' to messages containing 'shut up'."""

    @property
    def name(self) -> str:
        return "shutup_trigger"

    @property
    def description(self) -> str:
        return "Responds 'No, u!' to messages containing 'shut up'"

    async def setup(self):
        """Set up the shut up trigger module."""
        self.bot.add_listener(self.on_message, 'on_message')
        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the shut up trigger module."""
        self.bot.remove_listener(self.on_message, 'on_message')

    async def on_message(self, message):
        """Handle messages containing 'shut up'."""
        # Don't respond to the bot's own messages
        if message.author == self.bot.user:
            return

        message_lower = message.content.lower()

        # Check if the message contains "shut up"
        if 'shut up' in message_lower:
            await message.channel.send('No, u!')
