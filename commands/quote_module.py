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

    def get_next_quote_id(self) -> int:
        """Get the next available quote ID."""
        if not self.quotes:
            return 1

        max_id = max(quote.get('id', 0) for quote in self.quotes)
        return max_id + 1

    def can_add_quote(self, ctx) -> bool:
        """
        Check if the user has permission to add quotes.

        Args:
            ctx: Discord context

        Returns:
            True if user can add quotes, False otherwise
        """
        # Get allowed roles from config
        allowed_roles = self.config.get('quote_add_roles', [])

        # If empty list, anyone can add
        if not allowed_roles:
            return True

        # Check if user has any of the allowed roles
        if ctx.guild:
            user_roles = [role.name for role in ctx.author.roles]
            return any(role in allowed_roles for role in user_roles)

        # In DMs, deny by default
        return False

    def create_quote_from_message(self, message, quote_text: str = None) -> dict:
        """
        Create a quote dictionary from a Discord message.

        Args:
            message: Discord message object
            quote_text: Optional custom quote text (defaults to message content)

        Returns:
            Quote dictionary with full metadata
        """
        import datetime

        quote_id = self.get_next_quote_id()

        # If no custom quote_text provided (reply method), format as "<name>: <quote>"
        # If custom quote_text provided (direct method), use it as-is
        if quote_text is None:
            formatted_quote = f"{message.author.display_name}: {message.content}"
        else:
            formatted_quote = quote_text

        quote = {
            "id": quote_id,
            "quote": formatted_quote,
            "author": {
                "id": str(message.author.id),
                "username": message.author.name
            },
            "created_at": datetime.datetime.utcnow().isoformat() + "Z"
        }

        # Add channel metadata if in a guild
        if message.guild:
            quote["channel"] = {
                "id": str(message.channel.id),
                "name": message.channel.name,
                "guild": message.guild.name
            }

        return quote

    def add_quote(self, quote: dict) -> bool:
        """
        Add a quote to the collection and save to file.

        Args:
            quote: Quote dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            self.quotes.append(quote)
            self.save_quotes()
            return True
        except Exception as e:
            self.logger.error(f"Error adding quote: {e}")
            return False

    async def setup(self):
        """Set up the quote module."""

        # Create wrapper function for the command
        @commands.command(name='quote')
        async def quote_cmd(ctx, *, search_term: str = None):
            await self.quote_command(ctx, search_term=search_term)

        # Create wrapper function for the addquote command
        @commands.command(name='addquote')
        async def addquote_cmd(ctx, *, quote_text: str = None):
            await self.addquote_command(ctx, quote_text=quote_text)

        # Add commands to bot
        self.bot.add_command(quote_cmd)
        self.bot.add_command(addquote_cmd)

        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the quote module."""
        self.bot.remove_command('quote')
        self.bot.remove_command('addquote')

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

    async def addquote_command(self, ctx, *, quote_text: str = None):
        """
        Add a new quote to the collection.

        Supports two methods:
        1. Reply to a message with !addquote (captures that message)
        2. Type !addquote <text> (adds custom text as quote)

        Args:
            ctx: Discord context
            quote_text: Optional quote text (if not replying to a message)
        """
        # Check permissions
        if not self.can_add_quote(ctx):
            allowed_roles = self.config.get('quote_add_roles', [])
            roles_str = ", ".join(allowed_roles) if allowed_roles else "Admin"
            await ctx.send(f"❌ You don't have permission to add quotes. Required role(s): **{roles_str}**")
            return

        # Method 1: Reply to a message
        if ctx.message.reference:
            try:
                # Get the message being replied to
                replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

                # Create quote from the replied message
                quote = self.create_quote_from_message(replied_message)

                # Add to collection
                if self.add_quote(quote):
                    # Create success embed
                    embed = discord.Embed(
                        title="✅ Quote Added!",
                        description=f"Quote #{quote['id']} has been added to the collection.",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Quote", value=quote['quote'][:1024], inline=False)
                    embed.add_field(name="Author", value=f"<@{quote['author']['id']}>", inline=True)
                    embed.add_field(name="Total Quotes", value=str(len(self.quotes)), inline=True)

                    await ctx.send(embed=embed)
                    self.logger.info(f"Quote #{quote['id']} added by {ctx.author.name} (reply method)")
                else:
                    await ctx.send("❌ Failed to save quote. Check bot logs for details.")
            except Exception as e:
                self.logger.error(f"Error fetching replied message: {e}")
                await ctx.send("❌ Failed to fetch the message you replied to.")
            return

        # Method 2: Direct text input
        if quote_text:
            # Create quote from current message context
            quote = self.create_quote_from_message(ctx.message, quote_text=quote_text)

            # Add to collection
            if self.add_quote(quote):
                # Create success embed
                embed = discord.Embed(
                    title="✅ Quote Added!",
                    description=f"Quote #{quote['id']} has been added to the collection.",
                    color=discord.Color.green()
                )
                embed.add_field(name="Quote", value=quote['quote'][:1024], inline=False)
                embed.add_field(name="Added By", value=f"<@{ctx.author.id}>", inline=True)
                embed.add_field(name="Total Quotes", value=str(len(self.quotes)), inline=True)

                await ctx.send(embed=embed)
                self.logger.info(f"Quote #{quote['id']} added by {ctx.author.name} (direct method)")
            else:
                await ctx.send("❌ Failed to save quote. Check bot logs for details.")
            return

        # No quote provided
        await ctx.send(
            "❌ Please provide a quote using one of these methods:\n\n"
            "**Method 1:** Reply to a message with `!addquote`\n"
            "**Method 2:** Type `!addquote <your quote text here>`"
        )
