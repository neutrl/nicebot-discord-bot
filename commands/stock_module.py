"""Stock command module - fetch stock prices using Yahoo Finance."""

import time
import discord
from discord.ext import commands
from . import BaseModule


class StockModule(BaseModule):
    """Module for the !stock command to fetch stock prices."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.cache = {}  # {ticker: {'data': {...}, 'expires': timestamp}}
        self.cache_duration = config.get('stock_cache_minutes', 5) * 60  # Default 5 minutes

    @property
    def name(self) -> str:
        return "stock"

    @property
    def description(self) -> str:
        return "Stock price lookup (!stock)"

    async def setup(self):
        """Set up the stock module."""

        # Create wrapper function for the command
        @commands.command(name='stock')
        async def stock_cmd(ctx, ticker: str = None):
            await self.stock_command(ctx, ticker)

        # Add command to bot
        self.bot.add_command(stock_cmd)

        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the stock module."""
        self.bot.remove_command('stock')

    def validate_ticker(self, ticker: str) -> tuple:
        """
        Validate and clean ticker symbol.

        Args:
            ticker: Raw ticker input from user

        Returns:
            (is_valid, cleaned_ticker, error_message)
        """
        if not ticker:
            return False, None, "Please provide a ticker symbol. Example: `!stock AAPL`"

        # Clean and uppercase
        ticker = ticker.upper().strip()

        # Length check (1-10 characters, allowing for suffixes like BTC-USD)
        if len(ticker) < 1 or len(ticker) > 10:
            return False, ticker, "Ticker symbol must be 1-10 characters"

        # Allow alphanumeric and hyphens (for crypto like BTC-USD)
        if not all(c.isalnum() or c == '-' or c == '.' for c in ticker):
            return False, ticker, "Ticker symbol can only contain letters, numbers, hyphens, and periods"

        return True, ticker, None

    def get_cached_data(self, ticker: str):
        """Get cached stock data if still valid."""
        if ticker in self.cache:
            cached = self.cache[ticker]
            if time.time() < cached['expires']:
                return cached['data']
        return None

    def cache_data(self, ticker: str, data: dict):
        """Cache stock data."""
        self.cache[ticker] = {
            'data': data,
            'expires': time.time() + self.cache_duration
        }

    async def fetch_stock_data(self, ticker: str) -> tuple:
        """
        Fetch stock data using yfinance.

        Args:
            ticker: Stock ticker symbol

        Returns:
            (data_dict, error_message)
        """
        try:
            import yfinance as yf

            # Create ticker object
            stock = yf.Ticker(ticker)

            # Get info (this makes the API call)
            info = stock.info

            # Check if we got valid data
            if not info or 'symbol' not in info:
                return None, f"No data found for ticker: **{ticker}**\nPlease check the ticker symbol and try again."

            # Check if it's a valid stock (has price data)
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if current_price is None:
                return None, f"Unable to get price data for: **{ticker}**\nTicker may be invalid or delisted."

            # Extract relevant data
            data = {
                'symbol': info.get('symbol', ticker),
                'name': info.get('longName') or info.get('shortName', ticker),
                'current_price': current_price,
                'previous_close': info.get('previousClose', 0),
                'open': info.get('regularMarketOpen') or info.get('open'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                'volume': info.get('volume') or info.get('regularMarketVolume'),
                'market_cap': info.get('marketCap'),
                'currency': info.get('currency', 'USD'),
            }

            # Calculate change
            if data['previous_close'] and data['previous_close'] > 0:
                change = data['current_price'] - data['previous_close']
                change_percent = (change / data['previous_close']) * 100
                data['change'] = change
                data['change_percent'] = change_percent
            else:
                data['change'] = 0
                data['change_percent'] = 0

            return data, None

        except ImportError:
            return None, "❌ yfinance library not installed. Run: `pip install yfinance`"
        except Exception as e:
            error_msg = str(e)
            if "No data found" in error_msg or "404" in error_msg:
                return None, f"Invalid ticker: **{ticker}**\nPlease check the symbol and try again."
            return None, f"Error fetching stock data: {error_msg}"

    def create_stock_embed(self, data: dict) -> discord.Embed:
        """
        Create a Discord embed for stock data.

        Args:
            data: Stock data dictionary

        Returns:
            Discord embed object
        """
        symbol = data['symbol']
        name = data['name']
        price = data['current_price']
        change = data['change']
        change_percent = data['change_percent']
        currency = data.get('currency', 'USD')

        # Determine color and emoji based on change
        if change > 0:
            color = discord.Color.green()
            emoji = "📈"
            direction = "+"
        elif change < 0:
            color = discord.Color.red()
            emoji = "📉"
            direction = ""
        else:
            color = discord.Color.blue()
            emoji = "➡️"
            direction = ""

        # Create embed
        embed = discord.Embed(
            title=f"{emoji} {symbol}",
            description=f"**{name}**",
            color=color,
            timestamp=discord.utils.utcnow()
        )

        # Current price (large display)
        price_str = f"${price:,.2f}" if currency == 'USD' else f"{price:,.2f} {currency}"
        embed.add_field(
            name="💰 Current Price",
            value=f"# {price_str}",
            inline=False
        )

        # Change
        change_str = f"{direction}${abs(change):,.2f} ({direction}{change_percent:.2f}%)"
        embed.add_field(
            name="📊 Change",
            value=f"**{change_str}**",
            inline=True
        )

        # Previous close
        prev_close = data.get('previous_close')
        if prev_close:
            prev_str = f"${prev_close:,.2f}" if currency == 'USD' else f"{prev_close:,.2f} {currency}"
            embed.add_field(
                name="🔙 Previous Close",
                value=f"**{prev_str}**",
                inline=True
            )

        # Empty field for spacing
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        # Day range
        day_low = data.get('day_low')
        day_high = data.get('day_high')
        if day_low and day_high:
            range_str = f"${day_low:,.2f} - ${day_high:,.2f}" if currency == 'USD' else f"{day_low:,.2f} - {day_high:,.2f}"
            embed.add_field(
                name="📏 Day Range",
                value=f"**{range_str}**",
                inline=True
            )

        # Volume
        volume = data.get('volume')
        if volume:
            embed.add_field(
                name="📦 Volume",
                value=f"**{volume:,}**",
                inline=True
            )

        # Market cap
        market_cap = data.get('market_cap')
        if market_cap:
            # Format market cap in billions/millions
            if market_cap >= 1_000_000_000:
                cap_str = f"${market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                cap_str = f"${market_cap / 1_000_000:.2f}M"
            else:
                cap_str = f"${market_cap:,}"

            embed.add_field(
                name="💎 Market Cap",
                value=f"**{cap_str}**",
                inline=True
            )

        # Footer
        embed.set_footer(
            text="Powered by Yahoo Finance • Data may be delayed",
            icon_url="https://s.yimg.com/cv/apiv2/social/images/yahoo_default_logo-1200x1200.png"
        )

        return embed

    async def stock_command(self, ctx, ticker: str = None):
        """Handle the !stock command."""

        # Validate ticker
        is_valid, cleaned_ticker, error = self.validate_ticker(ticker)
        if not is_valid:
            await ctx.send(f"❌ {error}")
            return

        ticker = cleaned_ticker

        # Check cache first
        cached_data = self.get_cached_data(ticker)
        if cached_data:
            embed = self.create_stock_embed(cached_data)
            embed.set_footer(
                text="Powered by Yahoo Finance • Cached data",
                icon_url="https://s.yimg.com/cv/apiv2/social/images/yahoo_default_logo-1200x1200.png"
            )
            await ctx.send(embed=embed)
            return

        # Send "fetching" message
        fetching_msg = await ctx.send(f"🔍 Fetching stock data for **{ticker}**...")

        # Fetch data
        data, error = await self.fetch_stock_data(ticker)

        if error:
            await fetching_msg.edit(content=f"❌ {error}")
            return

        # Cache the data
        self.cache_data(ticker, data)

        # Create and send embed
        embed = self.create_stock_embed(data)
        await fetching_msg.edit(content=None, embed=embed)
