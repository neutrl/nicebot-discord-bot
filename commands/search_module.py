"""Search command module - DuckDuckGo search integration."""

import discord
from discord.ext import commands
import ddgs
from . import BaseModule


class SearchModule(BaseModule):
    """Module for the !search command using DuckDuckGo."""

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "DuckDuckGo search integration (!search)"

    async def setup(self):
        """Set up the search module."""

        # Create wrapper function for the command
        @commands.command(name='search')
        async def search_cmd(ctx, *, query: str = None):
            await self.search_command(ctx, query=query)

        # Add command to bot
        self.bot.add_command(search_cmd)

        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the search module."""
        self.bot.remove_command('search')

    async def search_command(self, ctx, *, query: str = None):
        """Search DuckDuckGo for a query and return results."""
        if not query:
            await ctx.send("Please provide a search query. Example: `!search python discord bot`")
            return

        # Send a "searching" message
        searching_msg = await ctx.send(f"🔍 Searching for: **{query}**...")

        try:
            # Perform DuckDuckGo search
            search = ddgs.DDGS()
            results = list(search.text(query, max_results=5))

            if not results:
                await searching_msg.edit(content=f"No results found for: **{query}**")
                return

            # Create embed for search results
            embed = discord.Embed(
                title=f"🔍 Search Results for: {query}",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )

            # Add search results to embed
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                link = result.get('href', '')
                body = result.get('body', 'No description')

                # Truncate body if too long
                if len(body) > 150:
                    body = body[:147] + "..."

                embed.add_field(
                    name=f"{i}. {title}",
                    value=f"{body}\n[🔗 Link]({link})",
                    inline=False
                )

            embed.set_footer(text="Powered by DuckDuckGo")

            # Edit the searching message with results
            await searching_msg.edit(content=None, embed=embed)

        except Exception as e:
            await searching_msg.edit(content=f"❌ Error performing search: {str(e)}")
