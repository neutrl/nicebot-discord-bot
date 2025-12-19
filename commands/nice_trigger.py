"""Nice trigger module - responds to messages containing 'nice'."""

import os
import json
import random
from collections import defaultdict
from . import BaseModule


class NiceTriggerModule(BaseModule):
    """Module that responds 'Nice!' to messages containing 'nice'."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.nice_counts = defaultdict(lambda: defaultdict(int))
        self.counts_file = os.path.join(data_dir, 'nice_counts.json')
        self.count_module = None
        self.nice_responses = [
            'Nice!',
            'Nice.',
            'nice',
            'Niceee',
            'Niccceee',
            'Very nice!',
            'Noice!',
            'Noice.',
            'N🧊',
            '👌',
        ]

    @property
    def name(self) -> str:
        return "nice_trigger"

    @property
    def description(self) -> str:
        return "Responds 'Nice!' to messages containing 'nice'"

    async def setup(self):
        """Set up the nice trigger module."""
        self.load_counts()
        self.bot.add_listener(self.on_message, 'on_message')
        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the nice trigger module."""
        self.save_counts()
        self.bot.remove_listener(self.on_message, 'on_message')

    def load_counts(self):
        """Load counts from file if it exists."""
        try:
            if os.path.exists(self.counts_file):
                with open(self.counts_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to proper format
                    self.nice_counts = defaultdict(lambda: defaultdict(int))
                    for server_id, channels in data.items():
                        for channel_id, count in channels.items():
                            self.nice_counts[server_id][channel_id] = count
                self.logger.info(f'Loaded counts from {self.counts_file}')
        except Exception as e:
            self.logger.warning(f'Error loading counts: {e}')

    def save_counts(self):
        """Save counts to file."""
        try:
            with open(self.counts_file, 'w') as f:
                json.dump(self.nice_counts, f, indent=2)
        except Exception as e:
            self.logger.error(f'Error saving counts: {e}')

    async def on_message(self, message):
        """Handle messages containing 'nice'."""
        # Don't respond to the bot's own messages
        if message.author == self.bot.user:
            return

        message_lower = message.content.lower()

        # Check if the message contains "nice" (case-insensitive)
        if 'nice' in message_lower:
            # Get server and channel IDs
            server_id = str(message.guild.id) if message.guild else 'DM'
            channel_id = str(message.channel.id)

            # Increment the count
            self.nice_counts[server_id][channel_id] += 1

            # Save counts to file
            self.save_counts()

            # Try to update count module if it's loaded
            if hasattr(self, 'count_module') and self.count_module:
                self.count_module.nice_counts = self.nice_counts

            # Send a random response
            response = random.choice(self.nice_responses)
            await message.channel.send(response)
