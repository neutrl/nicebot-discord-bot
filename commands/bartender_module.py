"""Bartender command module - Links to Bartender song on YouTube."""

import discord
from discord.ext import commands
from . import BaseModule


class BartenderModule(BaseModule):
    """Module for the !bartender command."""

    @property
    def name(self) -> str:
        return "bartender"

    @property
    def description(self) -> str:
        return "Links to Bartender song on YouTube (!bartender)"

    async def setup(self):
        """Set up the bartender module."""

        # Create wrapper function for the command
        @commands.command(name='bartender')
        async def bartender_cmd(ctx):
            await self.bartender_command(ctx)

        # Add command to bot
        self.bot.add_command(bartender_cmd)

        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the bartender module."""
        self.bot.remove_command('bartender')

    async def bartender_command(self, ctx):
        """Send a link to the Bartender song on YouTube."""
        # YouTube link for Bartender song
        youtube_url = "https://www.youtube.com/watch?v=pdEvL6jxUYA"

        # Create an embed for a nicer presentation
        embed = discord.Embed(
            title="🍹 Bartender",
            description="Rehab - Bartender",
            color=discord.Color.red(),
            url=youtube_url
        )

        embed.add_field(
            name="🎵 Listen Now",
            value=f"[Click here to listen on YouTube]({youtube_url})",
            inline=False
        )

        await ctx.send(embed=embed)
