import discord
from discord.ext import commands
import os
import json
import importlib
import sys

# Set up bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Data directory for persistent storage
DATA_DIR = 'data'

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Dictionary to store loaded modules
loaded_modules = {}


def load_module(module_name: str, config: dict):
    """
    Load a command module by name.

    Args:
        module_name: Name of the module to load (e.g., 'weather', 'count')
        config: Configuration dictionary

    Returns:
        True if module loaded successfully, False otherwise
    """
    try:
        # Map module names to their class names and files
        module_map = {
            'weather': ('commands.weather_module', 'WeatherModule'),
            'count': ('commands.count_module', 'CountModule'),
            'search': ('commands.search_module', 'SearchModule'),
            'nice_trigger': ('commands.nice_trigger', 'NiceTriggerModule'),
            'shutup_trigger': ('commands.shutup_trigger', 'ShutUpTriggerModule'),
            'eagles_trigger': ('commands.eagles_trigger', 'EaglesTriggerModule'),
        }

        if module_name not in module_map:
            print(f'✗ Unknown module: {module_name}')
            return False

        module_path, class_name = module_map[module_name]

        # Import the module
        module = importlib.import_module(module_path)

        # Reload if already imported (useful for development)
        if module_path in sys.modules:
            module = importlib.reload(module)

        # Get the module class
        module_class = getattr(module, class_name)

        # Instantiate the module
        module_instance = module_class(bot, config, DATA_DIR)

        # Store the module instance
        loaded_modules[module_name] = module_instance

        return True

    except Exception as e:
        print(f'✗ Error loading module {module_name}: {e}')
        import traceback
        traceback.print_exc()
        return False


async def setup_modules(config: dict):
    """
    Set up all enabled modules from config.

    Args:
        config: Configuration dictionary with 'enabled_modules' list
    """
    enabled_modules = config.get('enabled_modules', [])

    if not enabled_modules:
        print('\nWarning: No modules enabled in config.json')
        print('Add "enabled_modules" to your config.json to enable features')
        return

    print(f'\nLoading {len(enabled_modules)} module(s)...')

    for module_name in enabled_modules:
        if load_module(module_name, config):
            # Call the module's setup method
            module_instance = loaded_modules[module_name]
            await module_instance.setup()

    # Special handling: share data between nice_trigger and count modules
    if 'nice_trigger' in loaded_modules and 'count' in loaded_modules:
        nice_module = loaded_modules['nice_trigger']
        count_module = loaded_modules['count']
        # Share the same counts dictionary
        nice_module.count_module = count_module
        count_module.nice_counts = nice_module.nice_counts

    print(f'\n✓ Successfully loaded {len(loaded_modules)} module(s)\n')


async def teardown_modules():
    """Tear down all loaded modules."""
    for module_name, module_instance in loaded_modules.items():
        try:
            await module_instance.teardown()
            print(f'✓ Unloaded module: {module_name}')
        except Exception as e:
            print(f'✗ Error unloading module {module_name}: {e}')


@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')

    # Load modules after bot is ready
    await setup_modules(bot.config)


@bot.event
async def on_message(message):
    """
    Handle incoming messages.

    This event is needed to process both message triggers and commands.
    Message trigger modules will handle their own logic via listeners.
    """
    # Don't respond to the bot's own messages
    if message.author == bot.user:
        return

    # Process commands (this will trigger command modules)
    await bot.process_commands(message)


# Run the bot
if __name__ == '__main__':
    # Try to load token from config file first, then fall back to environment variable
    TOKEN = None
    CONFIG_FILE = 'config.json'
    config = {}

    # Try loading from config file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                TOKEN = config.get('bot_token')
            print(f'Loaded configuration from {CONFIG_FILE}')

            # Check for weather API key
            if config.get('weather_api_key'):
                print('Weather API key loaded successfully')
            else:
                print('Note: No weather API key found (weather module will not work)')
        except Exception as e:
            print(f'Error loading config file: {e}')

    # Fall back to environment variable if config file didn't work
    if not TOKEN:
        TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        if TOKEN:
            print('Loaded token from environment variable')

    if not TOKEN:
        print("\n" + "="*60)
        print("Error: No bot token found!")
        print("="*60)
        print("\nPlease either:")
        print("  1. Create a config.json file (copy config.example.json and add your token)")
        print("  2. Set the DISCORD_BOT_TOKEN environment variable")
        print("\nExample config.json:")
        print(json.dumps({
            "bot_token": "your-discord-bot-token",
            "weather_api_key": "your-openweathermap-api-key",
            "enabled_modules": [
                "weather",
                "count",
                "search",
                "nice_trigger",
                "shutup_trigger",
                "eagles_trigger"
            ]
        }, indent=2))
        print("\n" + "="*60)
        sys.exit(1)

    # Store config in bot instance for access in setup_modules
    bot.config = config

    # Run the bot
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print('\nShutting down...')
    finally:
        # Cleanup
        import asyncio
        asyncio.run(teardown_modules())
