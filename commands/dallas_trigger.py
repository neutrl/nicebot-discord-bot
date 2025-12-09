"""Dallas trigger module - responds to messages containing 'fuck dallas'."""

import random
from . import BaseModule


class DallasTriggerModule(BaseModule):
    """Module that responds with random Eagles chants to messages containing 'fuck dallas'."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.eagles_responses = [
            'Go Birds!',
            'da birds!',
            'E.A.G.L.E.S',
            'E-A-G-L-E-S EAGLES!',
            'Fly Eagles Fly!',
            'Bleed green!',
            'Fuck Dallas!',
            'Go Birds.',
        ]

    @property
    def name(self) -> str:
        return "dallas_trigger"

    @property
    def description(self) -> str:
        return "Responds with random Eagles chants to messages containing 'fuck dallas'"

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
            response = random.choice(self.eagles_responses)
            await message.channel.send(response)
