"""Eagles trigger module - responds to messages containing 'eagles' with random chants."""

import os
import json
import time
import random
from . import BaseModule


class EaglesTriggerModule(BaseModule):
    """Module that responds to 'eagles' with random Eagles chants (10-minute cooldown)."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.last_eagles_response = 0
        self.eagles_file = os.path.join(data_dir, 'eagles_timestamp.json')
        self.cooldown = config.get('eagles_cooldown', 600)  # Default 10 minutes
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
        return "eagles_trigger"

    @property
    def description(self) -> str:
        return "Responds to 'eagles' with random Eagles chants (10-min cooldown)"

    async def setup(self):
        """Set up the eagles trigger module."""
        self.load_timestamp()
        self.bot.add_listener(self.on_message, 'on_message')
        print(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the eagles trigger module."""
        self.save_timestamp()
        self.bot.remove_listener(self.on_message, 'on_message')

    def load_timestamp(self):
        """Load eagles response timestamp from file if it exists."""
        try:
            if os.path.exists(self.eagles_file):
                with open(self.eagles_file, 'r') as f:
                    data = json.load(f)
                    self.last_eagles_response = data.get('last_response', 0)
                print(f'  Loaded eagles timestamp from {self.eagles_file}')
        except Exception as e:
            print(f'  Error loading eagles timestamp: {e}')

    def save_timestamp(self):
        """Save eagles response timestamp to file."""
        try:
            with open(self.eagles_file, 'w') as f:
                json.dump({'last_response': self.last_eagles_response}, f, indent=2)
        except Exception as e:
            print(f'  Error saving eagles timestamp: {e}')

    async def on_message(self, message):
        """Handle messages containing 'eagles'."""
        # Don't respond to the bot's own messages
        if message.author == self.bot.user:
            return

        message_lower = message.content.lower()

        # Check if the message contains "eagles" (case-insensitive)
        if 'eagles' in message_lower:
            current_time = time.time()
            time_since_last_response = current_time - self.last_eagles_response

            # Only respond if cooldown has passed
            if time_since_last_response >= self.cooldown:
                self.last_eagles_response = current_time
                self.save_timestamp()
                response = random.choice(self.eagles_responses)
                await message.channel.send(response)
