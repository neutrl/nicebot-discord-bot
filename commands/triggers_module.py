"""Triggers/Help command module - displays information about bot features."""

import discord
from discord.ext import commands
from . import BaseModule


class TriggersModule(BaseModule):
    """Module for the !triggers command that displays bot information."""

    @property
    def name(self) -> str:
        return "triggers"

    @property
    def description(self) -> str:
        return "Displays information about bot commands and triggers"

    async def setup(self):
        """Set up the triggers module."""
        @commands.command(name='triggers')
        async def triggers_cmd(ctx):
            await self.triggers_command(ctx)

        self.bot.add_command(triggers_cmd)
        print(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the triggers module."""
        self.bot.remove_command('triggers')

    async def triggers_command(self, ctx):
        """Display information about bot commands and triggers."""
        # Create an embed with bot information
        embed = discord.Embed(
            title="🤖 NiceBot Commands & Triggers",
            description="Here's everything I can do!",
            color=discord.Color.green()
        )

        # Commands section
        commands_text = (
            "**!weather** `[zip]` - Current weather conditions\n"
            "**!forecast** `[zip]` - 5-day weather forecast\n"
            "**!setlocation** `<zip>` - Save your zip code\n"
            "**!stock** `<ticker>` - Stock prices (e.g., AAPL, BTC-USD)\n"
            "**!quote** `[search]` - Random quote or search quotes\n"
            "**!chat** `<prompt>` - Chat with AI (remembers context) 🤖\n"
            "  • `!chat reset` - Clear your conversation\n"
            "  • `!chat history` - Show conversation stats\n"
            "**!friday** - Friday celebration (Fridays only!)\n"
            "**!bartender** - Link to Bartender song 🍹\n"
            "**!count** - Nice count statistics\n"
            "**!search** `<query>` - DuckDuckGo search\n"
            "**!triggers** - Show this help message"
        )
        embed.add_field(
            name="📋 Commands",
            value=commands_text,
            inline=False
        )

        # Automatic triggers section
        triggers_text = (
            "**nice** → Responds \"Nice!\" 🎉\n"
            "**shut up** → Responds \"No, u!\" 😤\n"
            "**eagles** → Random Eagles chant 🦅\n"
            "  _(10-minute cooldown per channel)_\n"
            "**fuck dallas** → Random Eagles chant 🦅\n"
            "  _(no cooldown, always responds)_"
        )
        embed.add_field(
            name="⚡ Automatic Triggers",
            value=triggers_text,
            inline=False
        )

        # Eagles responses info
        eagles_text = (
            "Both Eagles triggers use 23+ responses including:\n"
            "• Eagles chants: *Go Birds!, E.A.G.L.E.S, Philly Special!*\n"
            "• Anti-Dallas: *Cowgirls!, Poverty franchise!*\n"
            "\n✏️ Customize in `eagles_responses.json`"
        )
        embed.add_field(
            name="🦅 Eagles Responses",
            value=eagles_text,
            inline=False
        )

        # Footer with tips
        embed.set_footer(
            text="💡 Tip: Use !setlocation once, then !weather and !forecast work without a zip code!"
        )

        await ctx.send(embed=embed)
