"""Dallas trigger module - responds to messages containing 'fuck dallas'."""

import os
import json
import random
from . import BaseModule


class DallasTriggerModule(BaseModule):
    """Module that responds with random Eagles chants to messages containing 'fuck dallas'."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.responses_file = 'eagles_responses.json'  # In root directory
        self.eagles_responses = self.load_responses()

    @property
    def name(self) -> str:
        return "dallas_trigger"

    @property
    def description(self) -> str:
        return "Responds with random Eagles chants to messages containing 'fuck dallas'"

    def load_responses(self) -> list:
        """Load Eagles responses from JSON file in root directory."""
        try:
            if os.path.exists(self.responses_file):
                with open(self.responses_file, 'r') as f:
                    data = json.load(f)
                    responses = [item['text'] for item in data.get('responses', [])]
                    if responses:
                        print(f'  Loaded {len(responses)} Eagles responses from {self.responses_file}')
                        return responses
        except Exception as e:
            print(f'  Error loading Eagles responses: {e}')

        # Fallback to default responses if file doesn't exist or has errors
        print(f'  Using default Eagles responses')
        return [
            'Go Birds!',
            'da birds!',
            'E.A.G.L.E.S',
            'E-A-G-L-E-S EAGLES!',
            'Fly Eagles Fly!',
            'Bleed green!',
            'Go Birds.',
            'Bird Gang!',
            'Gang Green!',
            'Let\'s go Birds!',
            'In Jalen we trust!',
            'Philly Special!',
            'It\'s a Philly thing!',
            '🦅🦅🦅',
            'Fuck Dallas!',
            'Dallas sucks!',
            'Cowgirls!',
            'America\'s most overrated team!',
            'Rent free in Dallas!',
            'How bout them Cowboys? HAHAHAHA',
            'Dallas ain\'t shit!',
            'Poverty franchise!',
            'BOOOO DALLAS!',
        ]

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
