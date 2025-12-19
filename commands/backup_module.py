"""Backup module - Automatic Dropbox backups for bot data."""

import os
import json
import zipfile
import tempfile
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from . import BaseModule

try:
    import dropbox
    from dropbox.exceptions import ApiError, AuthError
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False


class BackupModule(BaseModule):
    """Module for automatic Dropbox backups of bot data."""

    def __init__(self, bot, config: dict, data_dir: str):
        super().__init__(bot, config, data_dir)
        self.dropbox_token = config.get('dropbox_access_token', '')
        self.backup_enabled = config.get('dropbox_backup_enabled', True)
        self.backup_folder = config.get('dropbox_backup_folder', '/NiceBotBackups')
        self.backup_interval_hours = config.get('dropbox_backup_interval_hours', 6)
        self.backup_on_startup = config.get('dropbox_backup_on_startup', True)
        self.retention_days = config.get('dropbox_retention_days', 30)
        self.dbx = None
        self.last_backup_time = None

    @property
    def name(self) -> str:
        return "backup"

    @property
    def description(self) -> str:
        return "Automatic Dropbox backups (!backup)"

    async def setup(self):
        """Set up the backup module."""
        if not DROPBOX_AVAILABLE:
            self.logger.error("Dropbox library not installed. Run: pip install dropbox")
            return

        if not self.backup_enabled:
            self.logger.info("✓ Loaded module: backup (disabled)")
            return

        if not self.dropbox_token:
            self.logger.warning("✓ Loaded module: backup (no access token configured)")
            return

        # Initialize Dropbox client
        try:
            self.dbx = dropbox.Dropbox(self.dropbox_token)
            # Test authentication
            self.dbx.users_get_current_account()
            self.logger.info("✓ Dropbox authentication successful")
        except AuthError as e:
            self.logger.error(f"Dropbox authentication failed: {e}")
            self.dbx = None
            return
        except Exception as e:
            self.logger.error(f"Error initializing Dropbox: {e}")
            self.dbx = None
            return

        # Create backup command
        @commands.command(name='backup')
        @commands.has_permissions(administrator=True)
        async def backup_cmd(ctx):
            await self.manual_backup_command(ctx)

        self.bot.add_command(backup_cmd)

        # Start scheduled backup task
        if self.dbx:
            self.scheduled_backup.start()
            self.logger.info(f"✓ Loaded module: {self.name} (interval: {self.backup_interval_hours}h)")

            # Perform initial backup if configured
            if self.backup_on_startup:
                self.bot.loop.create_task(self.perform_backup())

    async def teardown(self):
        """Clean up the backup module."""
        if hasattr(self, 'scheduled_backup') and self.scheduled_backup.is_running():
            self.scheduled_backup.cancel()
        self.bot.remove_command('backup')

    @tasks.loop(hours=1)
    async def scheduled_backup(self):
        """Scheduled task that checks if it's time to backup."""
        if not self.dbx or not self.backup_enabled:
            return

        # Check if enough time has passed since last backup
        if self.last_backup_time:
            time_since_backup = datetime.now() - self.last_backup_time
            if time_since_backup.total_seconds() < (self.backup_interval_hours * 3600):
                return

        await self.perform_backup()

    async def perform_backup(self):
        """Perform a backup of all data files to Dropbox."""
        if not self.dbx:
            self.logger.error("Cannot perform backup: Dropbox not initialized")
            return False

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"nicebot_backup_{timestamp}.zip"

            # Create temporary ZIP file
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.zip', delete=False) as tmp_file:
                temp_path = tmp_file.name

                try:
                    with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        # Backup all files in data directory
                        if os.path.exists(self.data_dir):
                            for root, dirs, files in os.walk(self.data_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, os.path.dirname(self.data_dir))
                                    zipf.write(file_path, arcname)
                                    self.logger.debug(f"Added to backup: {arcname}")

                        # Backup config.json (with all API tokens)
                        config_path = "config.json"
                        if os.path.exists(config_path):
                            zipf.write(config_path, "config.json")
                            self.logger.debug("Added to backup: config.json")

                        # Backup eagles_responses.json
                        eagles_path = "eagles_responses.json"
                        if os.path.exists(eagles_path):
                            zipf.write(eagles_path, "eagles_responses.json")
                            self.logger.debug("Added to backup: eagles_responses.json")

                    # Upload to Dropbox
                    with open(temp_path, 'rb') as f:
                        dropbox_path = f"{self.backup_folder}/{backup_filename}"
                        self.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

                    self.logger.info(f"✓ Backup successful: {backup_filename} uploaded to Dropbox")
                    self.last_backup_time = datetime.now()

                    # Clean up old backups
                    await self.cleanup_old_backups()

                    return True

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

        except ApiError as e:
            self.logger.error(f"Dropbox API error during backup: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error during backup: {e}")
            return False

    async def cleanup_old_backups(self):
        """Delete backups older than retention period."""
        try:
            # List all files in backup folder
            result = self.dbx.files_list_folder(self.backup_folder)

            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0

            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    # Check if file is older than retention period
                    if entry.server_modified < cutoff_date:
                        self.dbx.files_delete_v2(entry.path_display)
                        deleted_count += 1
                        self.logger.debug(f"Deleted old backup: {entry.name}")

            if deleted_count > 0:
                self.logger.info(f"✓ Cleaned up {deleted_count} old backup(s)")

        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                # Backup folder doesn't exist yet, create it
                try:
                    self.dbx.files_create_folder_v2(self.backup_folder)
                    self.logger.info(f"Created backup folder: {self.backup_folder}")
                except Exception as create_error:
                    self.logger.error(f"Error creating backup folder: {create_error}")
            else:
                self.logger.error(f"Error cleaning up old backups: {e}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")

    async def manual_backup_command(self, ctx):
        """Handle manual backup command."""
        if not self.dbx:
            await ctx.send("❌ Dropbox backup is not configured or initialized.")
            return

        if not self.backup_enabled:
            await ctx.send("❌ Backup is currently disabled in config.")
            return

        await ctx.send("⏳ Starting manual backup...")

        success = await self.perform_backup()

        if success:
            backup_info = f"Last backup: {self.last_backup_time.strftime('%Y-%m-%d %H:%M:%S')}"
            await ctx.send(f"✅ Backup completed successfully!\n{backup_info}")
        else:
            await ctx.send("❌ Backup failed. Check bot logs for details.")
