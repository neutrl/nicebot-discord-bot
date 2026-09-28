"""Test script for weather module functionality."""

import asyncio
import json
from commands.weather_module import WeatherModule
from unittest.mock import Mock, MagicMock


class MockBot:
    """Mock Discord bot for testing."""
    def __init__(self):
        self.commands = {}

    def add_command(self, command):
        self.commands[command.name] = command

    def remove_command(self, name):
        if name in self.commands:
            del self.commands[name]


class MockContext:
    """Mock Discord context for testing."""
    def __init__(self, author_id=12345):
        self.author = Mock()
        self.author.id = author_id
        self.sent_messages = []
        self.sent_embeds = []

    async def send(self, content=None, embed=None):
        if content:
            self.sent_messages.append(content)
        if embed:
            self.sent_embeds.append(embed)
        print(f"\n{'='*60}")
        if content:
            print(f"MESSAGE: {content}")
        if embed:
            print(f"EMBED TITLE: {embed.title}")
            print(f"EMBED DESCRIPTION: {embed.description}")
            print(f"EMBED COLOR: {embed.color}")
            print(f"EMBED FIELDS ({len(embed.fields)}):")
            for field in embed.fields:
                print(f"  - {field.name}: {field.value} (inline={field.inline})")
            if embed.footer:
                print(f"EMBED FOOTER: {embed.footer.text}")
        print('='*60)


async def test_weather_module():
    """Test the weather module functionality."""

    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Create mock bot and weather module
    bot = MockBot()
    weather_module = WeatherModule(bot, config, data_dir='data')

    print("\n" + "="*60)
    print("WEATHER MODULE TEST SUITE")
    print("="*60)

    # Test 1: Check API key is loaded
    print("\n[TEST 1] Check API Key Configuration")
    print(f"API Key loaded: {'Yes' if weather_module.weather_api_key else 'No'}")
    print(f"API Key (masked): {weather_module.weather_api_key[:10]}..." if weather_module.weather_api_key else "None")

    # Test 2: Setup module
    print("\n[TEST 2] Setting up module...")
    await weather_module.setup()
    print(f"Commands registered: {list(bot.commands.keys())}")

    # Test 3: Fetch weather data for a known zip code
    print("\n[TEST 3] Fetching weather data for zip code 19019 (Philadelphia area)")
    data, error = await weather_module.fetch_weather('19019')

    if error:
        print(f"ERROR: {error}")
    else:
        print(f"SUCCESS!")
        print(f"Location: {data['name']}")
        print(f"Temperature: {data['main']['temp']:.1f}°F")
        print(f"Feels Like: {data['main']['feels_like']:.1f}°F")
        print(f"Description: {data['weather'][0]['description']}")
        print(f"Humidity: {data['main']['humidity']}%")
        print(f"Wind Speed: {data['wind']['speed']} mph")
        print(f"Pressure: {data['main']['pressure']} hPa")
        print(f"Visibility: {data.get('visibility', 'N/A')} meters")

    # Test 4: Fetch forecast data
    print("\n[TEST 4] Fetching 5-day forecast for zip code 19019")
    forecast_data, forecast_error = await weather_module.fetch_forecast('19019')

    if forecast_error:
        print(f"ERROR: {forecast_error}")
    else:
        print(f"SUCCESS!")
        print(f"Location: {forecast_data['city']['name']}")
        print(f"Forecast entries: {len(forecast_data['list'])}")

        # Aggregate daily forecasts
        daily_forecasts = weather_module.aggregate_daily_forecast(forecast_data)
        print(f"Daily summaries: {len(daily_forecasts)}")
        for day in daily_forecasts:
            print(f"  - {day['date']} ({day['day_name']}): High {day['high']:.0f}°F, Low {day['low']:.0f}°F, {day['condition']}")

    # Test 5: Test weather command with embed
    print("\n[TEST 5] Testing !weather command with embed output")
    ctx = MockContext()
    await weather_module.weather_command(ctx, '19019')

    if ctx.sent_embeds:
        embed = ctx.sent_embeds[0]
        print(f"\nEmbed validated:")
        print(f"  - Title: {embed.title}")
        print(f"  - Has temperature field: {any('Temperature' in f.name for f in embed.fields)}")
        print(f"  - Has humidity field: {any('Humidity' in f.name for f in embed.fields)}")
        print(f"  - Has dew point field: {any('Dew Point' in f.name for f in embed.fields)}")
        print(f"  - Has wind field: {any('Wind' in f.name for f in embed.fields)}")
        print(f"  - Has visibility field: {any('Visibility' in f.name for f in embed.fields)}")
        print(f"  - Has pressure field: {any('Pressure' in f.name for f in embed.fields)}")

    # Test 6: Test forecast command with embed
    print("\n[TEST 6] Testing !forecast command with embed output")
    ctx = MockContext()
    await weather_module.forecast_command(ctx, '19019')

    if ctx.sent_embeds:
        embed = ctx.sent_embeds[0]
        print(f"\nForecast embed validated:")
        print(f"  - Title: {embed.title}")
        print(f"  - Number of day fields: {len(embed.fields)}")
        print(f"  - Fields contain high/low temps: {any('High' in f.value and 'Low' in f.value for f in embed.fields)}")

    # Test 7: Test setlocation command
    print("\n[TEST 7] Testing !setlocation command")
    ctx = MockContext(author_id=99999)
    await weather_module.setlocation_command(ctx, '19019')

    if ctx.sent_messages:
        print(f"Response: {ctx.sent_messages[0]}")
        print(f"Location saved: {'99999' in weather_module.user_locations}")
        if '99999' in weather_module.user_locations:
            print(f"Saved zip code: {weather_module.user_locations['99999']}")

    # Test 8: Test weather command without zip (using saved location)
    print("\n[TEST 8] Testing !weather command without zip code (saved location)")
    ctx = MockContext(author_id=99999)
    await weather_module.weather_command(ctx, None)

    if ctx.sent_embeds:
        print(f"SUCCESS! Used saved location to fetch weather")
    elif ctx.sent_messages:
        print(f"Message: {ctx.sent_messages[0]}")

    # Test 9: Invalid zip code
    print("\n[TEST 9] Testing invalid zip code handling")
    ctx = MockContext()
    await weather_module.weather_command(ctx, '00000')

    if ctx.sent_messages:
        print(f"Error message: {ctx.sent_messages[0]}")

    # Test 10: Weather without saved location
    print("\n[TEST 10] Testing !weather without zip and no saved location")
    ctx = MockContext(author_id=88888)
    await weather_module.weather_command(ctx, None)

    if ctx.sent_messages:
        print(f"Error message: {ctx.sent_messages[0]}")

    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_weather_module())
