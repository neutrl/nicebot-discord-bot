"""Quote command module - Search and display quotes."""

import json
import random
import os
import discord
from discord.ext import commands
from . import BaseModule


class QuoteModule(BaseModule):
    """Module for the !quote command to search and display quotes."""

    def __init__(self, bot, config: dict, data_dir: str):
        super().__init__(bot, config, data_dir)
        self.quotes_file = os.path.join(data_dir, "quotes.json")
        self.quotes = []
        self.load_quotes()

    @property
    def name(self) -> str:
        return "quote"

    @property
    def description(self) -> str:
        return "Search and display quotes (!quote)"

    def load_quotes(self):
        """Load quotes from the JSON file."""
        try:
            if os.path.exists(self.quotes_file):
                with open(self.quotes_file, 'r', encoding='utf-8') as f:
                    self.quotes = json.load(f)
            else:
                # Create empty quotes file if it doesn't exist
                self.quotes = []
                self.save_quotes()
        except Exception as e:
            print(f"Error loading quotes: {e}")
            self.quotes = []

    def save_quotes(self):
        """Save quotes to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.quotes_file), exist_ok=True)
            with open(self.quotes_file, 'w', encoding='utf-8') as f:
                json.dump(self.quotes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving quotes: {e}")

    async def setup(self):
        """Set up the quote module."""

        # Create wrapper function for the command
        @commands.command(name='quote')
        async def quote_cmd(ctx, *, search_term: str = None):
            await self.quote_command(ctx, search_term=search_term)

        # Add command to bot
        self.bot.add_command(quote_cmd)

        print(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the quote module."""
        self.bot.remove_command('quote')

    def search_quotes(self, search_term: str) -> list:
        """
        Search quotes by text content.

        Args:
            search_term: Term to search for (case-insensitive)

        Returns:
            List of matching quote dictionaries
        """
        if not search_term:
            return []

        search_term = search_term.lower()
        matching_quotes = []

        for quote in self.quotes:
            # Search in quote text
            quote_text = quote.get('quote', '')
            if search_term in quote_text.lower():
                matching_quotes.append(quote)

        return matching_quotes

    def get_quote_by_id(self, quote_id: int) -> dict:
        """
        Get a specific quote by its ID number.

        Args:
            quote_id: The ID number of the quote to retrieve

        Returns:
            Quote dictionary if found, None otherwise
        """
        for quote in self.quotes:
            if quote.get('id') == quote_id:
                return quote
        return None

    async def quote_command(self, ctx, *, search_term: str = None):
        """Display a quote - random if no search term, by ID if number, or matching search."""
        if not self.quotes:
            await ctx.send("❌ No quotes available. Add some quotes to the `data/quotes.json` file!")
            return

        # If no search term, return a random quote
        if not search_term:
            quote = random.choice(self.quotes)
            await self.display_quote(ctx, quote)
            return

        # Check if search term is a number (ID search)
        if search_term.isdigit():
            quote_id = int(search_term)
            quote = self.get_quote_by_id(quote_id)

            if quote:
                embed = self.create_quote_embed(quote)
                embed.set_footer(text=f"Quote retrieved by ID: {quote_id}")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ No quote found with ID: **{quote_id}**\nTry `!quote` for a random quote.")
            return

        # Search for matching quotes by text
        matching_quotes = self.search_quotes(search_term)

        if not matching_quotes:
            await ctx.send(f"❌ No quotes found matching: **{search_term}**\nTry `!quote` for a random quote.")
            return

        # Return a random matching quote if multiple results
        quote = random.choice(matching_quotes)

        # Create embed with search info
        embed = self.create_quote_embed(quote)

        # Add search info to footer
        if len(matching_quotes) > 1:
            embed.set_footer(text=f"Found {len(matching_quotes)} matching quotes for '{search_term}'")
        else:
            embed.set_footer(text=f"Found 1 matching quote for '{search_term}'")

        await ctx.send(embed=embed)

    def create_quote_embed(self, quote: dict) -> discord.Embed:
        """
        Create a Discord embed for a quote.

        Args:
            quote: Quote dictionary with 'id' and 'quote' fields

        Returns:
            Discord embed object
        """
        quote_text = quote.get('quote', 'No quote text')
        quote_id = quote.get('id', 0)

        # Create embed with quote
        embed = discord.Embed(
            title=f"💬 Quote #{quote_id}",
            description=quote_text,
            color=discord.Color.blue()
         #   timestamp=discord.utils.utcnow()
        )

        return embed

    async def display_quote(self, ctx, quote: dict):
        """Display a single quote as an embed."""
        embed = self.create_quote_embed(quote)
        await ctx.send(embed=embed)
