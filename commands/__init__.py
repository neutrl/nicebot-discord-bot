"""
Command modules for the Discord bot.
Each module can be independently enabled/disabled via config.
"""

from abc import ABC, abstractmethod
import discord


class BaseModule(ABC):
    """Base class for all bot command modules."""

    def __init__(self, bot: discord.ext.commands.Bot, config: dict, data_dir: str = "data"):
        """
        Initialize the module.

        Args:
            bot: The Discord bot instance
            config: Configuration dictionary
            data_dir: Directory for persistent data storage
        """
        self.bot = bot
        self.config = config
        self.data_dir = data_dir

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the module name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what this module does."""
        pass

    @abstractmethod
    async def setup(self):
        """
        Set up the module (load data, register commands, etc.).
        Called when the module is loaded.
        """
        pass

    async def teardown(self):
        """
        Clean up the module (save data, unregister commands, etc.).
        Called when the module is unloaded (optional override).
        """
        pass
