"""Eagles trigger module - responds to messages containing 'eagles' with random chants."""

import os
import json
import time
import random
from . import BaseModule


class EaglesTriggerModule(BaseModule):
    """Module that responds to 'eagles' with random Eagles chants (per-channel 10-minute cooldown)."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.last_eagles_response = {}  # Dictionary: {channel_id: timestamp}
        self.eagles_file = os.path.join(data_dir, 'eagles_timestamp.json')
        self.responses_file = os.path.join(data_dir, 'eagles_responses.json')
        self.cooldown = config.get('eagles_cooldown', 600)  # Default 10 minutes
        self.cleanup_days = config.get('eagles_cleanup_days', 7)  # Clean up after 7 days
        self.eagles_responses = self.load_responses()

    @property
    def name(self) -> str:
        return "eagles_trigger"

    @property
    def description(self) -> str:
        return "Responds to 'eagles' with random Eagles chants (10-min cooldown)"

    def load_responses(self) -> list:
        """Load Eagles responses from JSON file."""
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
        """Set up the eagles trigger module."""
        self.load_timestamp()
        self.bot.add_listener(self.on_message, 'on_message')
        print(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the eagles trigger module."""
        self.save_timestamp()
        self.bot.remove_listener(self.on_message, 'on_message')

    def load_timestamp(self):
        """Load eagles response timestamps from file if it exists."""
        try:
            if os.path.exists(self.eagles_file):
                with open(self.eagles_file, 'r') as f:
                    data = json.load(f)

                    # Backward compatibility: detect old format {"last_response": timestamp}
                    if 'last_response' in data and isinstance(data.get('last_response'), (int, float)):
                        # Old global format - migrate to new format (empty dict)
                        self.last_eagles_response = {}
                        print(f'  Migrated eagles timestamp from global to per-channel format')
                    else:
                        # New per-channel format: {channel_id: timestamp}
                        # Convert string keys back to integers
                        self.last_eagles_response = {int(k): v for k, v in data.items()}
                        print(f'  Loaded eagles timestamps for {len(self.last_eagles_response)} channels')
        except Exception as e:
            print(f'  Error loading eagles timestamp: {e}')
            self.last_eagles_response = {}

    def cleanup_old_channels(self):
        """Remove channel timestamps older than cleanup_days to prevent unbounded growth."""
        current_time = time.time()
        max_age_seconds = self.cleanup_days * 24 * 60 * 60

        # Find channels to remove
        channels_to_remove = [
            channel_id for channel_id, timestamp in self.last_eagles_response.items()
            if current_time - timestamp > max_age_seconds
        ]

        # Remove old channels
        for channel_id in channels_to_remove:
            del self.last_eagles_response[channel_id]

        if channels_to_remove:
            print(f'  Cleaned up {len(channels_to_remove)} old channel timestamps')

    def save_timestamp(self):
        """Save eagles response timestamps to file (per-channel format)."""
        try:
            # Clean up old channels before saving
            self.cleanup_old_channels()

            # Convert integer keys to strings for JSON serialization
            data_to_save = {str(k): v for k, v in self.last_eagles_response.items()}

            with open(self.eagles_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            print(f'  Error saving eagles timestamp: {e}')

    async def on_message(self, message):
        """Handle messages containing 'eagles' with per-channel cooldown."""
        # Don't respond to the bot's own messages
        if message.author == self.bot.user:
            return

        message_lower = message.content.lower()

        # Check if the message contains "eagles" (case-insensitive)
        if 'eagles' in message_lower:
            current_time = time.time()
            channel_id = message.channel.id

            # Get last response time for this specific channel (default to 0 if never responded)
            last_response_time = self.last_eagles_response.get(channel_id, 0)
            time_since_last_response = current_time - last_response_time

            # Only respond if cooldown has passed for this channel
            if time_since_last_response >= self.cooldown:
                self.last_eagles_response[channel_id] = current_time
                self.save_timestamp()
                response = random.choice(self.eagles_responses)
                await message.channel.send(response)
