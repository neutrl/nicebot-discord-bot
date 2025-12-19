import discord
from discord.ext import commands
import os
import json
import importlib
import sys
import logging


def setup_logging():
    """Configure logging for the bot."""
    # Get log level from environment variable (default: INFO)
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Create formatter with timestamp
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Reduce discord.py logging noise
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)

    return logging.getLogger(__name__)


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

# Module-level logger (will be configured in main)
logger = logging.getLogger(__name__)


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
            'quote': ('commands.quote_module', 'QuoteModule'),
            'friday': ('commands.friday_module', 'FridayModule'),
            'stock': ('commands.stock_module', 'StockModule'),
            'triggers': ('commands.triggers_module', 'TriggersModule'),
            'bartender': ('commands.bartender_module', 'BartenderModule'),
            'chatgpt': ('commands.chatgpt_module', 'ChatGPTModule'),
            'nice_trigger': ('commands.nice_trigger', 'NiceTriggerModule'),
            'shutup_trigger': ('commands.shutup_trigger', 'ShutUpTriggerModule'),
            'eagles_trigger': ('commands.eagles_trigger', 'EaglesTriggerModule'),
            'dallas_trigger': ('commands.dallas_trigger', 'DallasTriggerModule'),
        }

        if module_name not in module_map:
            logger.error(f'✗ Unknown module: {module_name}')
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
        logger.error(f'✗ Error loading module {module_name}: {e}')
        logger.exception('Exception details:')
        return False


async def setup_modules(config: dict):
    """
    Set up all enabled modules from config.

    Args:
        config: Configuration dictionary with 'enabled_modules' list
    """
    enabled_modules = config.get('enabled_modules', [])

    if not enabled_modules:
        logger.warning('No modules enabled in config.json')
        logger.warning('Add "enabled_modules" to your config.json to enable features')
        return

    logger.info(f'Loading {len(enabled_modules)} module(s)...')

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

    logger.info(f'✓ Successfully loaded {len(loaded_modules)} module(s)')


async def teardown_modules():
    """Tear down all loaded modules."""
    for module_name, module_instance in loaded_modules.items():
        try:
            await module_instance.teardown()
            logger.info(f'✓ Unloaded module: {module_name}')
        except Exception as e:
            logger.error(f'✗ Error unloading module {module_name}: {e}')


@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')

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
    # Set up logging first
    logger = setup_logging()

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
            logger.info(f'Loaded configuration from {CONFIG_FILE}')

            # Check for weather API key
            if config.get('weather_api_key'):
                logger.info('Weather API key loaded successfully')
            else:
                logger.warning('No weather API key found (weather module will not work)')
        except Exception as e:
            logger.error(f'Error loading config file: {e}')

    # Fall back to environment variable if config file didn't work
    if not TOKEN:
        TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        if TOKEN:
            logger.info('Loaded token from environment variable')

    if not TOKEN:
        error_msg = """
============================================================
Error: No bot token found!
============================================================

Please either:
  1. Create a config.json file (copy config.example.json and add your token)
  2. Set the DISCORD_BOT_TOKEN environment variable

Example config.json:
""" + json.dumps({
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
        }, indent=2) + "\n" + "="*60
        logger.error(error_msg)
        sys.exit(1)

    # Store config in bot instance for access in setup_modules
    bot.config = config

    # Run the bot
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logger.info('Shutting down...')
    finally:
        # Cleanup
        import asyncio
        asyncio.run(teardown_modules())
