"""Count command module - display nice count statistics."""

import os
import json
import discord
from discord.ext import commands
from collections import defaultdict
from . import BaseModule


class CountModule(BaseModule):
    """Module for the !count command to display nice statistics."""

    def __init__(self, bot: commands.Bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.nice_counts = defaultdict(lambda: defaultdict(int))
        self.counts_file = os.path.join(data_dir, 'nice_counts.json')

    @property
    def name(self) -> str:
        return "count"

    @property
    def description(self) -> str:
        return "Display nice count statistics (!count)"

    async def setup(self):
        """Set up the count module."""
        self.load_counts()

        # Create wrapper function for the command
        @commands.command(name='count')
        async def count_cmd(ctx):
            await self.count_command(ctx)

        # Add command to bot
        self.bot.add_command(count_cmd)

        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the count module."""
        self.save_counts()
        self.bot.remove_command('count')

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

    def increment_count(self, server_id: str, channel_id: str):
        """Increment the nice count for a given server and channel."""
        self.nice_counts[server_id][channel_id] += 1
        self.save_counts()

    async def count_command(self, ctx):
        """Display nice count statistics for the current server and channel."""
        server_id = str(ctx.guild.id) if ctx.guild else 'DM'
        channel_id = str(ctx.channel.id)

        # Get counts
        channel_count = self.nice_counts[server_id][channel_id]
        server_count = sum(self.nice_counts[server_id].values())

        # Create embed for nice formatting
        embed = discord.Embed(
            title="📊 Nice Statistics",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="This Channel",
            value=f"**{channel_count}** nice{'s' if channel_count != 1 else ''}",
            inline=True
        )

        if ctx.guild:
            embed.add_field(
                name="This Server",
                value=f"**{server_count}** nice{'s' if server_count != 1 else ''}",
                inline=True
            )

            # Add breakdown by channel if there are multiple channels
            if len(self.nice_counts[server_id]) > 1:
                channel_breakdown = []
                for ch_id, count in sorted(self.nice_counts[server_id].items(), key=lambda x: x[1], reverse=True):
                    channel = ctx.guild.get_channel(int(ch_id))
                    channel_name = channel.name if channel else f"Channel {ch_id}"
                    channel_breakdown.append(f"#{channel_name}: {count}")

                # Limit to top 10 channels
                if len(channel_breakdown) > 10:
                    channel_breakdown = channel_breakdown[:10]
                    channel_breakdown.append("...")

                embed.add_field(
                    name="Channel Breakdown",
                    value="\n".join(channel_breakdown),
                    inline=False
                )

        await ctx.send(embed=embed)
