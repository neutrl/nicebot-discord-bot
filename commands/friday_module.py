"""Friday module - posts Rebecca Black's Friday video, but only on Fridays!"""

import os
import json
from datetime import datetime
from discord.ext import commands
from . import BaseModule


class FridayModule(BaseModule):
    """Module for the !friday command - only works on Fridays, once per channel."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.usage_file = os.path.join(data_dir, 'friday_usage.json')
        self.usage_data = {}  # {channel_id: "YYYY-MM-DD"}
        self.cleanup_days = config.get('friday_cleanup_days', 30)
        self.youtube_url = "https://www.youtube.com/watch?v=kfVsfOSbJY0"
        self.load_usage()

    @property
    def name(self) -> str:
        return "friday"

    @property
    def description(self) -> str:
        return "Friday video command (!friday) - only works on Fridays"

    async def setup(self):
        """Set up the Friday module."""

        # Create wrapper function for the command
        @commands.command(name='friday')
        async def friday_cmd(ctx):
            await self.friday_command(ctx)

        # Add command to bot
        self.bot.add_command(friday_cmd)

        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the Friday module."""
        self.save_usage()
        self.bot.remove_command('friday')

    def load_usage(self):
        """Load Friday usage data from file if it exists."""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    self.usage_data = json.load(f)
                print(f'  Loaded Friday usage data for {len(self.usage_data)} channels')
        except Exception as e:
            self.logger.warning(f'Error loading Friday usage: {e}')
            self.usage_data = {}

    def save_usage(self):
        """Save Friday usage data to file."""
        try:
            # Clean up old entries before saving
            self.cleanup_old_usage()

            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            self.logger.error(f'Error saving Friday usage: {e}')

    def cleanup_old_usage(self):
        """Remove usage records older than cleanup_days to prevent unbounded growth."""
        from datetime import timedelta

        current_date = datetime.now()
        cutoff_date = current_date - timedelta(days=self.cleanup_days)

        # Find channels to remove
        channels_to_remove = []
        for channel_id, date_str in self.usage_data.items():
            try:
                usage_date = datetime.strptime(date_str, '%Y-%m-%d')
                if usage_date < cutoff_date:
                    channels_to_remove.append(channel_id)
            except ValueError:
                # Invalid date format, remove it
                channels_to_remove.append(channel_id)

        # Remove old channels
        for channel_id in channels_to_remove:
            del self.usage_data[channel_id]

        if channels_to_remove:
            print(f'  Cleaned up {len(channels_to_remove)} old Friday usage records')

    def is_friday(self) -> bool:
        """Check if today is Friday."""
        return datetime.now().weekday() == 4  # Monday=0, Friday=4

    def get_friday_date(self) -> str:
        """Get current date as YYYY-MM-DD string."""
        return datetime.now().strftime('%Y-%m-%d')

    def has_used_today(self, channel_id: int) -> bool:
        """Check if this channel has already used !friday today."""
        today = self.get_friday_date()
        return str(channel_id) in self.usage_data and self.usage_data[str(channel_id)] == today

    def mark_used(self, channel_id: int):
        """Mark this channel as having used !friday today."""
        self.usage_data[str(channel_id)] = self.get_friday_date()
        self.save_usage()

    def get_days_until_friday(self) -> int:
        """Calculate how many days until the next Friday."""
        current_day = datetime.now().weekday()  # Monday=0, Friday=4

        if current_day < 4:  # Before Friday
            return 4 - current_day
        else:  # Friday or after (Saturday=5, Sunday=6)
            return (7 - current_day) + 4  # Days until Monday + days to Friday

    def get_current_day_name(self) -> str:
        """Get the name of the current day."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[datetime.now().weekday()]

    async def friday_command(self, ctx):
        """Handle the !friday command - posts Rebecca Black's Friday video."""

        # Check if today is Friday
        if not self.is_friday():
            days_until = self.get_days_until_friday()
            current_day = self.get_current_day_name()

            # Fun messages for different days
            if days_until == 1:
                message = (
                    f"❌ It's not Friday yet! Today is {current_day}.\n"
                    f"Tomorrow is Friday! Check back then! 🗓️"
                )
            else:
                message = (
                    f"❌ It's not Friday yet! Today is {current_day}.\n"
                    f"Come back in {days_until} days when the weekend arrives! 🗓️"
                )

            await ctx.send(message)
            return

        # Check if channel has already used it today
        channel_id = ctx.channel.id

        if self.has_used_today(channel_id):
            await ctx.send(
                "⏸️ Hold up! This channel already got its Friday fix today!\n"
                "Come back next Friday for more fun, fun, fun, fun! 😄"
            )
            return

        # It's Friday and hasn't been used yet - post the video!
        self.mark_used(channel_id)

        message = (
            "🎉 **It's Friday, Friday!** 🎉\n"
            "Gotta get down on Friday! 🎵\n\n"
            f"{self.youtube_url}\n\n"
            "Everybody's lookin' forward to the weekend! 🎊"
        )

        await ctx.send(message)
