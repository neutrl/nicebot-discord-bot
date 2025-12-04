"""Weather command module - fetch weather data and manage user locations."""

import os
import json
import discord
from discord.ext import commands
import aiohttp
from . import BaseModule


class WeatherModule(BaseModule):
    """Module for weather commands (!weather and !setlocation)."""

    def __init__(self, bot: commands.Bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.user_locations = {}
        self.locations_file = os.path.join(data_dir, 'user_locations.json')
        self.weather_api_key = config.get('weather_api_key')

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Weather lookup commands (!weather, !setlocation)"

    async def setup(self):
        """Set up the weather module."""
        self.load_locations()

        # Create wrapper functions for the commands
        @commands.command(name='weather')
        async def weather_cmd(ctx, zip_code: str = None):
            await self.weather_command(ctx, zip_code)

        @commands.command(name='setlocation')
        async def setlocation_cmd(ctx, zip_code: str):
            await self.setlocation_command(ctx, zip_code)

        # Add commands to bot
        self.bot.add_command(weather_cmd)
        self.bot.add_command(setlocation_cmd)

        print(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the weather module."""
        self.save_locations()
        self.bot.remove_command('weather')
        self.bot.remove_command('setlocation')

    def load_locations(self):
        """Load user locations from file if it exists."""
        try:
            if os.path.exists(self.locations_file):
                with open(self.locations_file, 'r') as f:
                    self.user_locations = json.load(f)
                print(f'  Loaded user locations from {self.locations_file}')
        except Exception as e:
            print(f'  Error loading locations: {e}')

    def save_locations(self):
        """Save user locations to file."""
        try:
            with open(self.locations_file, 'w') as f:
                json.dump(self.user_locations, f, indent=2)
        except Exception as e:
            print(f'  Error saving locations: {e}')

    async def fetch_weather(self, zip_code, country_code='US'):
        """Fetch weather data from OpenWeatherMap API."""
        if not self.weather_api_key:
            return None, "Weather API key not configured. Please add 'weather_api_key' to config.json"

        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'zip': f"{zip_code},{country_code}",
            'appid': self.weather_api_key,
            'units': 'imperial'  # Use Fahrenheit
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data, None
                    elif response.status == 404:
                        return None, "Invalid zip code. Please check and try again."
                    elif response.status == 401:
                        return None, "Invalid API key. Please check your OpenWeatherMap API key."
                    else:
                        return None, f"Weather service error (status {response.status})"
        except Exception as e:
            return None, f"Error fetching weather: {str(e)}"

    async def weather_command(self, ctx, zip_code: str = None):
        """Get weather information by zip code or use saved location."""
        user_id = str(ctx.author.id)

        # If no zip code provided, try to use saved location
        if not zip_code:
            if user_id in self.user_locations:
                zip_code = self.user_locations[user_id]
            else:
                await ctx.send("Please provide a zip code or save your location with `!setlocation <zipcode>`")
                return

        # Validate zip code format (5 digits)
        if not zip_code.isdigit() or len(zip_code) != 5:
            await ctx.send("Please provide a valid 5-digit US zip code")
            return

        # Fetch weather data
        data, error = await self.fetch_weather(zip_code)

        if error:
            await ctx.send(f"Error: {error}")
            return

        # Parse weather data
        location = data['name']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        description = data['weather'][0]['description'].capitalize()
        weather_main = data['weather'][0]['main'].lower()
        wind_speed = data['wind']['speed']
        wind_deg = data['wind'].get('deg', 0)
        visibility = data.get('visibility', 0) / 1609.34  # Convert meters to miles

        # Get weather emoji based on condition
        weather_emoji = {
            'clear': '☀️',
            'clouds': '☁️',
            'rain': '🌧️',
            'drizzle': '🌦️',
            'thunderstorm': '⛈️',
            'snow': '❄️',
            'mist': '🌫️',
            'fog': '🌫️',
            'haze': '🌫️',
            'smoke': '💨',
        }.get(weather_main, '🌤️')

        # Choose color based on temperature
        if temp >= 80:
            color = discord.Color.red()
        elif temp >= 60:
            color = discord.Color.gold()
        elif temp >= 40:
            color = discord.Color.blue()
        else:
            color = discord.Color.from_rgb(135, 206, 250)  # Light blue for cold

        # Get wind direction
        def get_wind_direction(degrees):
            directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            index = round(degrees / 45) % 8
            return directions[index]

        wind_direction = get_wind_direction(wind_deg)

        # Create enhanced weather embed
        embed = discord.Embed(
            title=f"{weather_emoji} Weather in {location}",
            description=f"**{description}**",
            color=color,
            timestamp=discord.utils.utcnow()
        )

        # Main temperature display (bigger, centered)
        embed.add_field(
            name="🌡️ Current Temperature",
            value=f"# {temp:.0f}°F\nFeels like **{feels_like:.0f}°F**",
            inline=False
        )

        # High/Low temps
        embed.add_field(
            name="📊 High / Low",
            value=f"↑ **{temp_max:.0f}°F** / ↓ **{temp_min:.0f}°F**",
            inline=True
        )

        # Humidity
        humidity_emoji = "💧" if humidity > 70 else "💨"
        embed.add_field(
            name=f"{humidity_emoji} Humidity",
            value=f"**{humidity}%**",
            inline=True
        )

        # Wind
        embed.add_field(
            name="🌬️ Wind",
            value=f"**{wind_speed:.1f} mph** {wind_direction}",
            inline=True
        )

        # Additional details
        embed.add_field(
            name="👁️ Visibility",
            value=f"**{visibility:.1f} mi**",
            inline=True
        )

        embed.add_field(
            name="🔽 Pressure",
            value=f"**{pressure} hPa**",
            inline=True
        )

        # Empty field for spacing
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        # Footer
        embed.set_footer(
            text=f"📍 Zip Code: {zip_code} • Powered by OpenWeatherMap",
            icon_url="https://openweathermap.org/img/wn/{}@2x.png".format(data['weather'][0]['icon'])
        )

        await ctx.send(embed=embed)

    async def setlocation_command(self, ctx, zip_code: str):
        """Save your location for quick weather lookups."""
        # Validate zip code format (5 digits)
        if not zip_code.isdigit() or len(zip_code) != 5:
            await ctx.send("Please provide a valid 5-digit US zip code")
            return

        # Verify the zip code is valid by fetching weather
        data, error = await self.fetch_weather(zip_code)

        if error:
            await ctx.send(f"Unable to verify zip code: {error}")
            return

        # Save the location
        user_id = str(ctx.author.id)
        self.user_locations[user_id] = zip_code
        self.save_locations()

        location = data['name']
        await ctx.send(f"Your location has been saved as {location} ({zip_code}). Use `!weather` without a zip code to get weather for your saved location.")
