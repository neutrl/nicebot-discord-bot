#!/usr/bin/env python3
"""Diagnostic script to check if bot commands are registered"""

import sys
sys.path.insert(0, '.')

# Mock the bot token so we can import the module
import os
os.environ['DISCORD_BOT_TOKEN'] = 'test-token'

# Create a dummy config to prevent file loading issues
with open('config.json', 'w') as f:
    import json
    json.dump({'bot_token': 'test', 'weather_api_key': 'test'}, f)

try:
    # Import the discord_bot module (but don't run it)
    import importlib.util
    spec = importlib.util.spec_from_file_location("discord_bot", "discord_bot.py")
    discord_bot = importlib.util.module_from_spec(spec)

    # Execute module to register commands but don't run bot
    import discord_bot as bot_module

    print("Bot instance found!")
    print(f"Bot command prefix: {bot_module.bot.command_prefix}")
    print("\nRegistered commands:")
    for command in bot_module.bot.commands:
        print(f"  - !{command.name}: {command.help or 'No description'}")

    print(f"\nTotal commands: {len(list(bot_module.bot.commands))}")

    # Check specifically for weather commands
    weather_cmd = bot_module.bot.get_command('weather')
    setlocation_cmd = bot_module.bot.get_command('setlocation')

    if weather_cmd:
        print("\n✓ 'weather' command is registered")
    else:
        print("\n✗ 'weather' command is NOT registered")

    if setlocation_cmd:
        print("✓ 'setlocation' command is registered")
    else:
        print("✗ 'setlocation' command is NOT registered")

except Exception as e:
    print(f"Error loading bot module: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Clean up test config
    if os.path.exists('config.json'):
        os.remove('config.json')
