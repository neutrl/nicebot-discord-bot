# Discord "Nice" Bot

A simple Discord bot that responds with "Nice!" whenever a user says "nice" in any message, responds with "No, u!" when someone says "shut up", shows team spirit with randomized Eagles responses when someone mentions "eagles", and responds "go birds." when someone says "fuck dallas".

## 🐳 Quick Start with Docker

**Recommended for easy deployment!**

```bash
# 1. Set up your token
cp config.example.json config.json
# Edit config.json with your bot token

# 2. Run with Docker
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

See [DOCKER.md](DOCKER.md) for complete Docker documentation.

## Features

- **Modular Design**: Enable/disable features via config.json
- Responds "Nice!" to any message containing the word "nice" (case-insensitive)
- Responds "No, u!" to any message containing "shut up" (case-insensitive)
- Responds with randomized Eagles responses to any message containing "eagles" (case-insensitive)
  - Includes: "Go Birds!", "da birds!", "E.A.G.L.E.S", "Fly Eagles Fly!", "Philly Special!", "Gang Green!", and more
  - Also includes anti-Dallas chants: "Cowgirls!", "Dallas sucks!", "Poverty franchise!", and more
  - 10-minute per-channel cooldown to prevent spam (each channel independent)
- Responds with randomized Eagles responses to any message containing "fuck dallas" (case-insensitive, no cooldown)
  - Uses the same expanded list of Eagles chants and anti-Dallas responses
- Tracks the number of "Nice!" responses per server and per channel
- Persists counts to a file so they survive bot restarts
- `!count` command to display statistics
- `!weather` command to check current weather by zip code
- `!forecast` command to view 5-day weather forecast
- `!setlocation` command to save your location for quick weather lookups
- `!search` command for DuckDuckGo searches
- `!quote` command to search and display quotes from a database
- `!friday` command to celebrate Fridays with Rebecca Black (only works on Fridays!)
- `!stock` command to check real-time stock prices and market data
- `!bartender` command to link to the Bartender song on YouTube
- `!triggers` command to display help and information about bot features
- User location persistence across bot restarts
- Ignores its own messages to prevent infinite loops
- Simple and lightweight

## Available Modules

The bot uses a modular system where you can enable or disable features individually:

| Module Name | Description | Commands |
|-------------|-------------|----------|
| `weather` | Weather lookup and location management | `!weather`, `!forecast`, `!setlocation` |
| `count` | Display nice count statistics | `!count` |
| `search` | DuckDuckGo search integration | `!search` |
| `quote` | Search and display quotes from database | `!quote` |
| `friday` | Friday celebration (Rebecca Black video) | `!friday` |
| `stock` | Real-time stock prices and market data | `!stock` |
| `bartender` | Links to Bartender song on YouTube | `!bartender` |
| `triggers` | Display bot help and information | `!triggers` |
| `nice_trigger` | Responds "Nice!" to messages containing "nice" | (automatic trigger) |
| `shutup_trigger` | Responds "No, u!" to messages containing "shut up" | (automatic trigger) |
| `eagles_trigger` | Random Eagles chants for messages containing "eagles" | (automatic trigger) |
| `dallas_trigger` | Random Eagles chants for messages containing "fuck dallas" | (automatic trigger) |

## Setup Instructions

> **💡 Tip**: If you have Docker installed, see the [Quick Start with Docker](#-quick-start-with-docker) section above for easier deployment!

### Manual Setup

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - **Message Content Intent** (required for the bot to read messages)
6. Click "Reset Token" and copy your bot token (keep this secret!)

### 2. Invite the Bot to Your Server

1. In the Developer Portal, go to "OAuth2" > "URL Generator"
2. Select the following scopes:
   - `bot`
3. Select the following bot permissions:
   - `Send Messages`
   - `Read Messages/View Channels`
4. Copy the generated URL and open it in your browser
5. Select the server you want to add the bot to

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Your Bot Token and Weather API Key

#### Option 1: Config File (Recommended)

1. Copy the example config file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` and add your bot token, weather API key, and enabled modules:
   ```json
   {
     "bot_token": "your-discord-bot-token-here",
     "weather_api_key": "your-openweathermap-api-key-here",
     "enabled_modules": [
       "weather",
       "count",
       "search",
       "quote",
       "friday",
       "stock",
       "bartender",
       "triggers",
       "nice_trigger",
       "shutup_trigger",
       "eagles_trigger",
       "dallas_trigger"
     ],
     "eagles_cooldown": 600
   }
   ```

3. Get a free OpenWeatherMap API key:
   - Go to [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account
   - Navigate to "API keys" in your account settings
   - Copy your API key and add it to `config.json`
   - Note: The weather API key is optional - the bot will work without it, but weather commands will not be available

#### Option 2: Environment Variable

Set your Discord bot token as an environment variable:

**Linux/Mac:**
```bash
export DISCORD_BOT_TOKEN='your-token-here'
```

**Windows (Command Prompt):**
```cmd
set DISCORD_BOT_TOKEN=your-token-here
```

**Windows (PowerShell):**
```powershell
$env:DISCORD_BOT_TOKEN='your-token-here'
```

**Note:** The bot will try to load from `config.json` first, then fall back to the environment variable.

### 5. Run the Bot

```bash
python discord_bot.py
```

You should see a message saying the bot has connected to Discord!

## Configuring Modules

The bot uses a modular system that allows you to enable or disable features individually. This is controlled by the `enabled_modules` array in your `config.json` file.

### Enabling/Disabling Modules

To disable a module, simply remove it from the `enabled_modules` array in `config.json`. For example, to disable the search and eagles trigger:

```json
{
  "bot_token": "your-token-here",
  "weather_api_key": "your-api-key-here",
  "enabled_modules": [
    "weather",
    "count",
    "nice_trigger",
    "shutup_trigger"
  ]
}
```

To enable all modules, include all available module names:

```json
{
  "bot_token": "your-token-here",
  "weather_api_key": "your-api-key-here",
  "enabled_modules": [
    "weather",
    "count",
    "search",
    "quote",
    "friday",
    "stock",
    "bartender",
    "triggers",
    "nice_trigger",
    "shutup_trigger",
    "eagles_trigger",
    "dallas_trigger"
  ]
}
```

### Module Configuration Options

Some modules have additional configuration options:

- `eagles_cooldown`: Time in seconds between Eagles responses per channel (default: 600 = 10 minutes)
- `eagles_cleanup_days`: Days to keep channel timestamps before cleanup (default: 7 days)
- `friday_cleanup_days`: Days to keep Friday usage records before cleanup (default: 30 days)
- `stock_cache_minutes`: Minutes to cache stock price data (default: 5 minutes)
- `weather_api_key`: Required for the weather module to work

### Module Dependencies

Note: The `nice_trigger` module tracks counts that the `count` module displays. If you want to use `!count`, you should also enable `nice_trigger`.

## Usage

Once the bot is running and in your server:

### Responding to "nice"

1. Type any message containing "nice" in a channel the bot can see
2. The bot will respond with "Nice!" and increment the counter

Examples:
- User: "nice"
- Bot: "Nice!"

- User: "That's really nice!"
- Bot: "Nice!"

- User: "NICE work!"
- Bot: "Nice!"

### Responding to "shut up"

The bot has a playful response to "shut up":

Examples:
- User: "shut up"
- Bot: "No, u!"

- User: "Oh shut up bot"
- Bot: "No, u!"

### Responding to "eagles"

The bot shows team spirit with randomized responses when "eagles" is mentioned (with a 10-minute per-channel cooldown):

Examples:
- User: "eagles"
- Bot: "Go Birds!" (or "da birds!", "E.A.G.L.E.S", "Fly Eagles Fly!", "Bleed green!", "Philly Special!", etc.)

- User: "Let's go Eagles!"
- Bot: "Bird Gang!"

- User: "Did you see the Eagles game?"
- Bot: "Cowgirls!" (or any other random response)

**Available responses** (23 total):
- **Eagles chants**: Go Birds!, da birds!, E.A.G.L.E.S, E-A-G-L-E-S EAGLES!, Fly Eagles Fly!, Bleed green!, Bird Gang!, Gang Green!, Let's go Birds!, In Jalen we trust!, Philly Special!, It's a Philly thing!, 🦅🦅🦅
- **Anti-Dallas chants**: Fuck Dallas!, Dallas sucks!, Cowgirls!, America's most overrated team!, Rent free in Dallas!, How bout them Cowboys? HAHAHAHA, Dallas ain't shit!, Poverty franchise!, BOOOO DALLAS!

**Note:** The bot will only respond once every 10 minutes **per channel** to prevent spam. Each channel has its own independent cooldown, so #general and #sports can both enjoy Eagles responses separately. Each response is randomly selected from the full list above.

### Responding to "fuck dallas"

The bot shows team spirit with randomized responses when "fuck dallas" is mentioned (no cooldown):

Examples:
- User: "fuck dallas"
- Bot: "Cowgirls!" (or "Poverty franchise!", "Gang Green!", "Dallas ain't shit!", etc.)

- User: "man fuck dallas!"
- Bot: "How bout them Cowboys? HAHAHAHA"

- User: "FUCK DALLAS"
- Bot: "America's most overrated team!"

**Note:** This trigger has no cooldown and will respond every time "fuck dallas" is mentioned in any message. Uses the same 23 responses as the eagles trigger (both Eagles chants and anti-Dallas chants).

#### Customizing Eagles Responses

Both the eagles and dallas triggers load their responses from `eagles_responses.json` in the project root, making it easy to customize without editing code!

**To add or edit responses:**

1. Open `eagles_responses.json` in any text editor (it's in the main project folder)
2. Add, remove, or modify responses in the JSON array
3. Each response has a `text` (the message) and `category` (either "eagles" or "anti-dallas")
4. Restart the bot to load the new responses

**Example format:**
```json
{
  "responses": [
    {
      "text": "Your custom Eagles chant here!",
      "category": "eagles"
    },
    {
      "text": "Your custom Dallas diss!",
      "category": "anti-dallas"
    }
  ]
}
```

**Note:**
- This file is tracked by git, so your custom responses will be committed with the project
- If the JSON file is missing or has errors, the bot will automatically fall back to the default 23 responses

### Checking Statistics

Use the `!count` command to see statistics:

```
!count
```

This will display:
- Number of "nice" responses in the current channel
- Total number of "nice" responses in the server
- Breakdown by channel (top 10 channels shown)

The counts are saved automatically and will persist even if the bot restarts.

### Weather Commands

The bot can fetch weather information for US zip codes (requires OpenWeatherMap API key):

#### Check Weather by Zip Code

```
!weather 10001
```

This will display:
- Current temperature (°F)
- Feels like temperature
- Weather description
- Humidity percentage
- Wind speed

#### Save Your Location

Save your zip code to quickly check weather without typing it each time:

```
!setlocation 10001
```

After setting your location, you can use `!weather` without a zip code:

```
!weather
```

The bot will automatically use your saved location. User locations are saved and persist across bot restarts.

#### Get 5-Day Forecast

View the 5-day weather forecast:

```
!forecast 10001
```

Or use your saved location:

```
!forecast
```

The forecast displays:
- Daily high and low temperatures
- Weather conditions for each day
- 5-day outlook with emoji indicators
- Easy-to-read format showing "Today", "Tomorrow", and upcoming days

**Note:** The forecast uses the same saved location system as `!weather`. Set your location once with `!setlocation` and both commands will use it.

### Search Command

The bot can perform DuckDuckGo searches directly in Discord:

```
!search python discord bot
```

This will display:
- Top 5 search results
- Title, description, and link for each result
- Formatted in an easy-to-read embed

Example:
```
!search how to make pizza
```

The bot will search DuckDuckGo and display the top 5 results with links.

### Quote Command

The bot can search and display quotes from a JSON database:

#### Random Quote

To get a random quote, simply use:

```
!quote
```

#### Search Quotes by ID

To retrieve a specific quote by its ID number:

```
!quote 42
```

This will display quote #42 exactly.

#### Search Quotes by Keyword

To search for specific quotes by keyword:

```
!quote programming
```

This will search through the quote text and return a random matching quote.

Examples:
```
!quote neutral
!quote eagles
!quote nice
```

The bot will search for quotes containing your keyword and display a random matching result with the quote ID.

**Quote Database**: Quotes are stored in `data/quotes.json` (1,008 quotes total). The bot will display how many matching quotes were found for your search term.

### Friday Command

Celebrate Friday with Rebecca Black's iconic video!

```
!friday
```

**Special Rules:**
- ✅ **Only works on Fridays** - The bot checks the day of the week
- ✅ **Once per channel per Friday** - Each channel can post it once, then must wait until next Friday
- 🎉 **Automatic reset** - At midnight, the countdown starts again for the next Friday

**Example responses:**

On Friday (first use):
```
🎉 It's Friday, Friday! 🎉
Gotta get down on Friday! 🎵

https://www.youtube.com/watch?v=kfVsfOSbJY0

Everybody's lookin' forward to the weekend! 🎊
```

On Friday (already used):
```
⏸️ Hold up! This channel already got its Friday fix today!
Come back next Friday for more fun, fun, fun, fun! 😄
```

On any other day:
```
❌ It's not Friday yet! Today is Wednesday.
Come back in 2 days when the weekend arrives! 🗓️
```

**Note:** The bot uses server time to determine if it's Friday. The video link is automatically tracked per channel and resets weekly.

### Stock Command

Get real-time stock prices and market data from Yahoo Finance!

```
!stock AAPL
```

**Features:**
- ✅ **Real-time stock prices** - Powered by Yahoo Finance (no API key required)
- ✅ **Comprehensive data** - Current price, change, day range, volume, market cap
- ✅ **Visual indicators** - Color-coded embeds (green for up, red for down, blue for unchanged)
- ✅ **5-minute caching** - Reduces API calls and provides faster responses
- ✅ **Supports multiple asset types** - Stocks, crypto, indices, and more

**Examples:**

Check a stock price:
```
!stock AAPL
!stock TSLA
!stock MSFT
```

Check cryptocurrency:
```
!stock BTC-USD
!stock ETH-USD
```

Check market indices:
```
!stock ^GSPC    (S&P 500)
!stock ^DJI     (Dow Jones)
```

**Display Format:**

The bot shows a beautiful Discord embed with:
- 💰 Current price (large display)
- 📊 Change amount and percentage
- 🔙 Previous close
- 📏 Day's trading range (high/low)
- 📦 Trading volume
- 💎 Market capitalization (formatted in billions/millions)

**Example output for `!stock AAPL`:**
```
📈 AAPL
Apple Inc.

💰 Current Price
# $182.45

📊 Change                    🔙 Previous Close
+$2.35 (+1.31%)             $180.10

📏 Day Range                 📦 Volume
$180.00 - $183.50           52,847,234

💎 Market Cap
$2.89T

Powered by Yahoo Finance • Data may be delayed
```

**Caching:**
- Stock data is cached for 5 minutes (configurable)
- Cached responses show "Cached data" in the footer
- Prevents excessive API calls and provides faster responses

**Note:** Yahoo Finance data may be delayed by 15-20 minutes for some exchanges. The stock module requires no API key and works immediately after enabling it in your config.

### Bartender Command

Link to the Bartender song on YouTube!

```
!bartender
```

**Features:**
- 🍹 **Quick link** - Instantly shares the Bartender song
- 🎵 **YouTube integration** - Direct link to the song on YouTube
- 📱 **Embed format** - Beautiful Discord embed with clickable link

**Example output:**

The bot displays an embed titled "🍹 Bartender" with:
- Song title: "Rehab - Bartender"
- Direct YouTube link: https://www.youtube.com/watch?v=pdEvL6jxUYA
- Clickable button to open the video

Perfect for sharing your favorite song with the server! 🎶

## Security Note

Never share your bot token or API keys publicly! If you accidentally expose them, regenerate them immediately.

**Important:**
- The `config.json` file is included in `.gitignore` to prevent accidentally committing your tokens and API keys to version control
- Use `config.example.json` as a template - never commit your actual `config.json` file
- Keep your bot token and weather API key secure and treat them like passwords
- If you expose your Discord bot token, regenerate it in the Discord Developer Portal
- If you expose your OpenWeatherMap API key, regenerate it in your OpenWeatherMap account settings

## Troubleshooting

- **Bot doesn't respond**: Make sure "Message Content Intent" is enabled in the Discord Developer Portal
- **Bot can't connect**: Verify your token is set correctly
- **Permission errors**: Ensure the bot has "Send Messages" and "Read Messages/View Channels" permissions in your server
- **Weather command not working**:
  - Verify you have added your OpenWeatherMap API key to `config.json`
  - Check that your API key is active (new keys can take a few minutes to activate)
  - Ensure you're using a valid 5-digit US zip code
  - Free tier API keys have a rate limit (60 calls/minute)
