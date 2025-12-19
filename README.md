# NiceBot - A Feature-Rich Discord Bot

A modular Discord bot with fun triggers, utility commands, and Philadelphia Eagles team spirit! 🦅

**Key Features:**
- 🎉 **Interactive Triggers** - Responds to "nice", "shut up", "eagles", and more with randomized messages
- 🤖 **AI Integration** - ChatGPT (GPT-4o-mini) for intelligent Q&A and conversations
- 🌤️ **Weather Integration** - Real-time weather and forecasts with location saving
- 📈 **Stock Ticker** - Live stock prices from Yahoo Finance
- 🔍 **Web Search** - DuckDuckGo search integration
- 💬 **Quote Database** - 1,000+ searchable quotes
- 🎵 **Music Links** - Quick access to favorite songs
- 📊 **Statistics Tracking** - Persistent counters and analytics
- ⚙️ **Fully Modular** - Enable/disable any feature via config

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

### 🤖 Automatic Triggers
- **Nice Trigger** - Responds with randomized "nice" variations to messages containing "nice"
  - 10 different responses including: "Nice!", "Noice!", "Very nice!", "N🧊", and more
  - Tracks counts per channel and server with persistent storage
- **Shut Up Trigger** - Playfully responds "No, u!" to messages containing "shut up"
- **Eagles Trigger** - Random Eagles chants for messages containing "eagles"
  - 23+ responses including team chants and anti-Dallas jokes
  - 10-minute per-channel cooldown to prevent spam
  - Customizable via `eagles_responses.json`
- **Dallas Trigger** - Random Eagles chants for "fuck dallas" (no cooldown)
  - Uses the same response pool as Eagles trigger

### 📋 Commands
- **!weather** `[zip]` - Current weather conditions for any US zip code
- **!forecast** `[zip]` - 5-day weather forecast with daily highs/lows
- **!setlocation** `<zip>` - Save your zip code for quick lookups
- **!stock** `<ticker>` - Real-time stock prices, crypto, and indices (AAPL, BTC-USD, etc.)
- **!quote** `[search]` - Random quote or search 1,008 quotes by keyword/ID
- **!addquote** `<text>` - Add a new quote to the collection (role-restricted)
- **!chat** `<prompt>` - Chat with AI (remembers conversation context per user)
  - **!chat reset** - Clear your conversation history
  - **!chat history** - View your conversation stats
- **!search** `<query>` - DuckDuckGo web search with top 5 results
- **!friday** - Friday celebration (Rebecca Black) - Only works on Fridays, once per channel!
- **!bartender** - Quick link to Bartender song on YouTube
- **!count** - Display "nice" count statistics with channel breakdown
- **!triggers** - Show help message with all commands and triggers

### ⚙️ Technical Features
- **Modular Design** - Enable/disable any feature via `config.json`
- **Persistent Storage** - Counts, locations, and timestamps survive restarts
- **Docker Support** - Easy deployment with Docker Compose
- **Smart Caching** - Stock prices cached for 5 minutes to reduce API calls
- **Cooldown Management** - Per-channel cooldowns with automatic cleanup
- **Error Handling** - Graceful fallbacks and user-friendly error messages

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
| `chatgpt` | OpenAI ChatGPT (GPT-4o-mini) integration | `!chat` |
| `bartender` | Links to Bartender song on YouTube | `!bartender` |
| `triggers` | Display bot help and information | `!triggers` |
| `nice_trigger` | Responds with randomized "nice" variations (10 responses) | (automatic trigger) |
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

### 4. Set Your Bot Token and API Keys

#### Option 1: Config File (Recommended)

1. Copy the example config file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` and add your bot token, API keys, and enabled modules:
   ```json
   {
     "bot_token": "your-discord-bot-token-here",
     "weather_api_key": "your-openweathermap-api-key-here",
     "openai_api_key": "your-openai-api-key-here",
     "enabled_modules": [
       "weather",
       "count",
       "search",
       "quote",
       "friday",
       "stock",
       "chatgpt",
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

3. Get free API keys:

   **OpenWeatherMap API (for weather commands):**
   - Go to [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account
   - Navigate to "API keys" in your account settings
   - Copy your API key and add it to `config.json`
   - Note: Optional - the bot will work without it, but weather commands will not be available

   **OpenAI API (for ChatGPT):**
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Sign in or create an account
   - Click "Create new secret key"
   - Copy your API key and add it to `config.json`
   - Note: Optional - the bot will work without it, but `!chat` command will not be available
   - Install the package: `pip install openai`

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

The bot responds with randomized "nice" variations whenever someone says "nice":

**How it works:**
1. Type any message containing "nice" in a channel the bot can see
2. The bot will respond with a random variation and increment the counter

**Available responses** (10 total):
- Nice! / Nice. / nice
- Niceee / Niccceee
- Very nice!
- Noice! / Noice.
- N🧊 (nice ice cube)
- 👌 (OK hand emoji)

**Examples:**
- User: "nice"
- Bot: "Noice!" (or any other random response)

- User: "That's really nice!"
- Bot: "Very nice!"

- User: "NICE work!"
- Bot: "N🧊"

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

The bot shows team spirit with randomized Eagles responses when "fuck dallas" is mentioned (no cooldown):

**Examples:**
- User: "fuck dallas"
- Bot: "Cowgirls!" (or "Poverty franchise!", "Gang Green!", "Dallas ain't shit!", etc.)

- User: "man fuck dallas!"
- Bot: "How bout them Cowboys? HAHAHAHA"

- User: "FUCK DALLAS"
- Bot: "America's most overrated team!"

**Note:** This trigger has no cooldown and will respond every time "fuck dallas" is mentioned in any message. Uses the same 23+ responses as the eagles trigger (both Eagles chants and anti-Dallas chants).

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

### Add Quote Command

Add new quotes to the collection with full metadata capture!

```
!addquote <your quote text here>
```

Or reply to any message with:
```
!addquote
```

**Features:**
- 📝 **Two input methods** - Type quote text directly OR reply to any message
- 🔒 **Role-based permissions** - Restrict who can add quotes via configuration
- 📊 **Full metadata** - Captures author, channel, timestamp, and guild information
- 🔢 **Auto-increment IDs** - Automatically assigns the next sequential ID
- 💾 **Instant save** - Quotes are immediately saved to `data/quotes.json`

**Examples:**

Add a quote by typing text:
```
!addquote The only thing we have to fear is fear itself
```

Add a quote by replying to a message:
1. Right-click any message and select "Reply"
2. Type `!addquote` in the reply
3. The bot will capture the original message as a quote

**Quote Metadata:**

When you add a quote, the bot captures:
- **Quote ID** - Auto-assigned sequential number (starting at 1009)
- **Quote text** - The message content
- **Author** - Discord user ID and username
- **Channel** - Channel ID, name, and server/guild name
- **Timestamp** - ISO 8601 UTC timestamp (e.g., "2025-12-18T12:34:56.789Z")

**Configuration:**

Control who can add quotes by editing `config.json`:

```json
{
  "quote_add_roles": ["Admin", "Moderator", "Trusted"]
}
```

- **Empty array `[]`**: Anyone can add quotes (default)
- **List of role names**: Only users with those roles can add quotes
- Role names are case-sensitive and must match exactly

**Example permission denied response:**
```
❌ You don't have permission to add quotes. Required role(s): Admin, Moderator
```

**Example success response:**
```
✅ Quote Added!
Quote #1009 has been added to the collection.

Quote: "The only thing we have to fear is fear itself"
Added By: @YourUsername
Total Quotes: 1009
```

**Note:** Added quotes immediately appear in `!quote` searches and can be retrieved by their assigned ID number.

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

### Chat Command (ChatGPT)

Have natural conversations with OpenAI's ChatGPT! The bot remembers your conversation context, allowing for multi-turn discussions.

```
!chat What is the capital of France?
!chat Tell me more about its history
!chat What are some must-see landmarks there?
```

**Features:**
- 🤖 **Powered by GPT-4o-mini** - Fast, intelligent, and cost-effective AI model
- 💭 **Conversation Memory** - Bot remembers your chat history for contextual responses
- 💬 **Unlimited topics** - Ask about anything: facts, coding, creative writing, explanations, and more
- 🎯 **Smart responses** - Get detailed, context-aware answers
- ⚡ **Fast processing** - Responses typically arrive in seconds
- 🔒 **Private conversations** - Each user has their own independent chat history
- 💰 **Cost-effective** - GPT-4o-mini is optimized for performance and affordability

**Commands:**
```
!chat <prompt>          - Chat with AI (remembers context)
!chat history           - View your conversation stats
!chat reset             - Clear your conversation history
```

**Examples:**

Multi-turn conversation:
```
!chat What is Python?
!chat What are some popular frameworks for it?
!chat Can you show me an example of a Flask app?
```

Ask factual questions:
```
!chat What is the capital of France?
!chat How does photosynthesis work?
!chat Who won the Super Bowl in 2024?
```

Get coding help:
```
!chat How do I write a Python function to reverse a string?
!chat Explain what async/await means in JavaScript
!chat What's the difference between SQL and NoSQL?
```

Creative writing:
```
!chat Write a haiku about the Eagles
!chat Tell me a short joke about programming
!chat Create a motivational quote about teamwork
```

**Setup:**
1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add it to your `config.json` as `openai_api_key`
3. Install the package: `pip install openai`
4. Enable the `chatgpt` module in your config

**Configuration Options:**
```json
{
  "openai_api_key": "your-api-key-here",
  "chatgpt_max_history": 10,
  "chatgpt_system_message": "You are a helpful assistant.",
  "chatgpt_channels": []
}
```
- `chatgpt_max_history` - Maximum message pairs to remember per user (default: 10)
- `chatgpt_system_message` - System prompt that defines the AI's behavior
- `chatgpt_channels` - List of channel names where !chat is allowed (empty = all channels)
  - Example: `["bot-commands", "general"]` to restrict to only those channels
  - Default: `[]` (available in all channels)

**Conversation Management:**
- The bot stores up to 10 message exchanges per user by default
- When the limit is reached, older messages are automatically removed
- Use `!chat reset` to clear your history and start fresh
- Use `!chat history` to see how many messages you've exchanged
- Conversation history is saved to disk and persists across bot restarts

**Pricing:**
- GPT-4o-mini is very affordable: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- Most chat responses cost less than $0.01
- Longer conversation histories use more tokens per request
- Check your usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage)

**Note:** Responses are truncated if they exceed Discord's 2000 character limit. Make sure you have API credits in your OpenAI account.

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
