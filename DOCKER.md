# Docker Deployment Guide

This guide explains how to run the Discord Nice Bot using Docker and Docker Compose.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

### 1. Set Up Your Bot Token

You have two options:

#### Option A: Using config.json (Recommended)

```bash
cp config.example.json config.json
# Edit config.json and add your bot token
```

#### Option B: Using Environment Variables

```bash
cp .env.example .env
# Edit .env and add your bot token
```

### 2. Build and Run

```bash
# Build and start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

## Docker Commands Reference

### Building and Running

```bash
# Build and start in detached mode
docker-compose up -d

# Build and start with logs visible
docker-compose up

# Rebuild after code changes
docker-compose up -d --build

# Start existing container
docker-compose start

# Stop container (keeps data)
docker-compose stop

# Stop and remove container (keeps data)
docker-compose down
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Managing Data

```bash
# View persistent data
ls -la ./data/

# Backup counts file
cp ./data/nice_counts.json ./nice_counts_backup.json

# The data/ directory is mounted as a volume, so counts persist even if you:
# - Stop the container
# - Remove the container
# - Rebuild the image
```

### Troubleshooting

```bash
# Check if container is running
docker-compose ps

# Restart the bot
docker-compose restart

# View container details
docker-compose ps -a

# Access container shell (for debugging)
docker-compose exec discord-bot /bin/bash

# Remove everything and start fresh (WARNING: loses data)
docker-compose down -v
```

## File Structure

```
.
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── discord_bot.py          # Bot code
├── requirements.txt        # Python dependencies
├── config.json            # Bot token (gitignored)
├── config.example.json    # Config template
├── .env                   # Environment variables (gitignored)
├── .env.example          # Environment template
└── data/                 # Persistent data directory (gitignored)
    └── nice_counts.json  # Count statistics
```

## Features

- **Automatic restarts**: Bot automatically restarts if it crashes
- **Persistent data**: Counts are saved in `./data/` directory and survive container restarts
- **Easy updates**: Just rebuild with `docker-compose up -d --build`
- **Isolated environment**: Runs in its own container with all dependencies

## Updating the Bot

```bash
# Pull latest code changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Production Tips

1. **Use config.json**: More secure than environment variables in production
2. **Backup data**: Regularly backup the `./data/` directory
3. **Monitor logs**: Use `docker-compose logs -f` to watch for issues
4. **Resource limits**: Add resource limits in docker-compose.yml if needed:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

## Troubleshooting

### Bot won't start
- Check logs: `docker-compose logs`
- Verify token in `config.json` or `.env`
- Ensure Message Content Intent is enabled in Discord Developer Portal

### Counts not persisting
- Check if `./data/` directory exists
- Verify volume mount in docker-compose.yml
- Check file permissions: `ls -la ./data/`

### Permission errors
```bash
# Fix permissions on Linux
sudo chown -R $USER:$USER ./data/
```

## Security Notes

- Never commit `config.json` or `.env` to version control
- The `.gitignore` file excludes these automatically
- Keep your bot token secret
- Use read-only mount for config.json in production
