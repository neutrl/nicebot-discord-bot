"""Weather command module - fetch weather data and manage user locations."""

import os
import json
from datetime import datetime
from collections import Counter
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
        return "Weather lookup commands (!weather, !forecast, !setlocation)"

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

        @commands.command(name='forecast')
        async def forecast_cmd(ctx, zip_code: str = None):
            await self.forecast_command(ctx, zip_code)

        # Add commands to bot
        self.bot.add_command(weather_cmd)
        self.bot.add_command(setlocation_cmd)
        self.bot.add_command(forecast_cmd)

        self.logger.info(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the weather module."""
        self.save_locations()
        self.bot.remove_command('weather')
        self.bot.remove_command('forecast')
        self.bot.remove_command('setlocation')

    def load_locations(self):
        """Load user locations from file if it exists."""
        try:
            if os.path.exists(self.locations_file):
                with open(self.locations_file, 'r') as f:
                    self.user_locations = json.load(f)
                self.logger.info(f'Loaded user locations from {self.locations_file}')
        except Exception as e:
            self.logger.warning(f'Error loading locations: {e}')

    def save_locations(self):
        """Save user locations to file."""
        try:
            with open(self.locations_file, 'w') as f:
                json.dump(self.user_locations, f, indent=2)
        except Exception as e:
            self.logger.error(f'Error saving locations: {e}')

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

    async def fetch_forecast(self, zip_code, country_code='US'):
        """Fetch 5-day forecast data from OpenWeatherMap API."""
        if not self.weather_api_key:
            return None, "Weather API key not configured. Please add 'weather_api_key' to config.json"

        url = f"http://api.openweathermap.org/data/2.5/forecast"
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
                        return None, f"Forecast service error (status {response.status})"
        except Exception as e:
            return None, f"Error fetching forecast: {str(e)}"

    def aggregate_daily_forecast(self, forecast_data):
        """
        Aggregate 3-hour forecast intervals into daily summaries.

        Args:
            forecast_data: Raw forecast data from API

        Returns:
            List of daily forecast dictionaries with date, temps, and conditions
        """
        daily_forecasts = {}

        # Process each 3-hour interval
        for entry in forecast_data['list']:
            # Extract date from timestamp
            dt_obj = datetime.fromtimestamp(entry['dt'])
            date_key = dt_obj.strftime('%Y-%m-%d')
            day_name = dt_obj.strftime('%a')  # Mon, Tue, etc.

            # Initialize day if not exists
            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = {
                    'date': date_key,
                    'day_name': day_name,
                    'temps': [],
                    'conditions': [],
                    'dt': entry['dt']
                }

            # Collect temperature and weather data
            daily_forecasts[date_key]['temps'].append(entry['main']['temp'])
            daily_forecasts[date_key]['conditions'].append(entry['weather'][0]['main'])

        # Calculate daily summaries
        summaries = []
        for date_key in sorted(daily_forecasts.keys()):
            day_data = daily_forecasts[date_key]
            temps = day_data['temps']

            # Find most common weather condition
            condition_counts = Counter(day_data['conditions'])
            most_common_condition = condition_counts.most_common(1)[0][0]

            summaries.append({
                'date': date_key,
                'day_name': day_data['day_name'],
                'high': max(temps),
                'low': min(temps),
                'condition': most_common_condition,
                'dt': day_data['dt']
            })

        return summaries[:5]  # Return only first 5 days

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

        # Fetch weather data and forecast data (for high/low temps)
        data, error = await self.fetch_weather(zip_code)

        if error:
            await ctx.send(f"Error: {error}")
            return

        # Fetch forecast to get today's high/low
        forecast_data, forecast_error = await self.fetch_forecast(zip_code)
        today_high = None
        today_low = None

        if not forecast_error and forecast_data:
            # Get today's date
            today = datetime.now().date()
            today_temps = []

            # Collect all temps for today from forecast
            for entry in forecast_data['list']:
                dt_obj = datetime.fromtimestamp(entry['dt']).date()
                if dt_obj == today:
                    today_temps.append(entry['main']['temp'])

            if today_temps:
                today_high = max(today_temps)
                today_low = min(today_temps)

        # Parse weather data
        location = data['name']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        description = data['weather'][0]['description'].capitalize()
        weather_main = data['weather'][0]['main'].lower()
        wind_speed = data['wind']['speed']
        wind_deg = data['wind'].get('deg', 0)
        visibility = data.get('visibility', 0) / 1609.34  # Convert meters to miles

        # Calculate dew point using Magnus formula
        # Convert Fahrenheit to Celsius for calculation
        temp_c = (temp - 32) * 5/9
        # Magnus formula constants
        a = 17.27
        b = 237.7
        # Calculate alpha using relative humidity
        import math
        alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
        dew_point_c = (b * alpha) / (a - alpha)
        # Convert back to Fahrenheit
        dew_point = (dew_point_c * 9/5) + 32

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

        # Convert pressure from hPa to inHg for US audience
        pressure_inhg = pressure * 0.02953

        # Create enhanced weather embed
        embed = discord.Embed(
            title=f"{weather_emoji} {location}",
            description=f"**{description}**",
            color=color,
            timestamp=discord.utils.utcnow()
        )

        # Main temperature display - clean and prominent
        temp_value = f"**{temp:.0f}°F**"
        if feels_like != temp:
            temp_value += f"  •  Feels like {feels_like:.0f}°F"

        # Add high/low if available
        if today_high is not None and today_low is not None:
            temp_value += f"\nH: {today_high:.0f}°  L: {today_low:.0f}°"

        embed.add_field(
            name="🌡️ Temperature",
            value=temp_value,
            inline=False
        )

        # Row 1: Conditions
        embed.add_field(
            name="💧 Humidity",
            value=f"{humidity}%",
            inline=True
        )

        embed.add_field(
            name="🌡️ Dew Point",
            value=f"{dew_point:.0f}°F",
            inline=True
        )

        embed.add_field(
            name="🌬️ Wind",
            value=f"{wind_speed:.0f} mph {wind_direction}",
            inline=True
        )

        # Row 2: Additional details
        embed.add_field(
            name="👁️ Visibility",
            value=f"{visibility:.1f} mi",
            inline=True
        )

        embed.add_field(
            name="🔽 Pressure",
            value=f"{pressure_inhg:.2f} inHg",
            inline=True
        )

        # Footer
        embed.set_footer(
            text=f"Zip: {zip_code} • OpenWeatherMap",
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

    async def forecast_command(self, ctx, zip_code: str = None):
        """Display 5-day weather forecast."""
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

        # Fetch forecast data
        data, error = await self.fetch_forecast(zip_code)

        if error:
            await ctx.send(f"Error: {error}")
            return

        # Aggregate into daily forecasts
        daily_forecasts = self.aggregate_daily_forecast(data)

        # Get location name
        location = data['city']['name']

        # Weather emoji mapping
        weather_emoji = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️',
            'Haze': '🌫️',
            'Smoke': '💨',
        }

        # Create forecast embed
        embed = discord.Embed(
            title=f"📅 {location}",
            description="5-Day Forecast",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        # Add each day's forecast
        today = datetime.now().date()
        for i, day in enumerate(daily_forecasts):
            forecast_date = datetime.strptime(day['date'], '%Y-%m-%d').date()

            # Determine day label
            if forecast_date == today:
                day_label = "Today"
            elif i == 0:
                day_label = "Today"
            elif i == 1 or (i == 0 and forecast_date > today):
                day_label = "Tomorrow"
            else:
                day_label = day['day_name']

            # Format date for display
            formatted_date = forecast_date.strftime('%m/%d')

            # Get emoji for condition
            emoji = weather_emoji.get(day['condition'], '🌤️')

            # Build field value - cleaner format
            field_value = f"{day['condition']}  •  H: {day['high']:.0f}°  L: {day['low']:.0f}°"

            # Add field with day's forecast
            embed.add_field(
                name=f"{emoji} {day_label} ({formatted_date})",
                value=field_value,
                inline=False
            )

        # Footer
        embed.set_footer(
            text=f"Zip: {zip_code} • OpenWeatherMap"
        )

        await ctx.send(embed=embed)
