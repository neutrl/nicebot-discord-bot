"""ChatGPT command module - OpenAI ChatGPT integration."""

import discord
from discord.ext import commands
import asyncio
from . import BaseModule

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class ChatGPTModule(BaseModule):
    """Module for the !chat command using OpenAI ChatGPT."""

    def __init__(self, bot, config: dict, data_dir: str = "data"):
        super().__init__(bot, config, data_dir)
        self.api_key = config.get('openai_api_key')
        self.client = None

        if not OPENAI_AVAILABLE:
            print("  Warning: openai package not installed")
            print("  Install with: pip install openai")
        elif self.api_key:
            try:
                # Strip any whitespace from the key
                self.api_key = self.api_key.strip()

                # Debug: Show key format (first/last chars only for security)
                if len(self.api_key) > 20:
                    print(f"  OpenAI API key format: {self.api_key[:7]}...{self.api_key[-4:]} (length: {len(self.api_key)})")

                # Initialize the OpenAI client
                self.client = OpenAI(api_key=self.api_key)
                print(f"  Successfully configured OpenAI API client")
            except Exception as e:
                print(f"  Error configuring OpenAI API: {e}")
                print(f"  Error type: {type(e).__name__}")

    @property
    def name(self) -> str:
        return "chatgpt"

    @property
    def description(self) -> str:
        return "OpenAI ChatGPT chat integration (!chat)"

    async def setup(self):
        """Set up the chatgpt module."""

        # Create wrapper function for the command
        @commands.command(name='chat')
        async def chat_cmd(ctx, *, prompt: str = None):
            await self.chat_command(ctx, prompt=prompt)

        # Add command to bot
        self.bot.add_command(chat_cmd)

        print(f"✓ Loaded module: {self.name}")

    async def teardown(self):
        """Clean up the chatgpt module."""
        self.bot.remove_command('chat')

    async def chat_command(self, ctx, *, prompt: str = None):
        """Ask ChatGPT a question and return the response."""
        if not prompt:
            await ctx.send("Please provide a prompt. Example: `!chat What is the capital of France?`")
            return

        # Check if API is configured
        if not OPENAI_AVAILABLE:
            await ctx.send("❌ ChatGPT module requires the `openai` package.\nInstall with: `pip install openai`")
            return

        if not self.api_key:
            await ctx.send("❌ OpenAI API key not configured. Please add `openai_api_key` to your config.json")
            return

        if not self.client:
            await ctx.send("❌ OpenAI client not initialized. Check your API key configuration.")
            return

        # Send a "thinking" message
        thinking_msg = await ctx.send(f"🤖 Asking ChatGPT: **{prompt[:100]}{'...' if len(prompt) > 100 else ''}**")

        try:
            # Call OpenAI API in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
            )

            # Extract the response text
            response_text = response.choices[0].message.content

            # Check if response is empty
            if not response_text:
                await thinking_msg.edit(content="❌ Received empty response from ChatGPT.")
                return

            # Truncate response if too long for Discord (2000 char limit)
            if len(response_text) > 1900:
                response_text = response_text[:1897] + "..."

            # Create embed for response
            embed = discord.Embed(
                title="🤖 ChatGPT Response",
                description=response_text,
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="Prompt",
                value=prompt[:1024] if len(prompt) <= 1024 else prompt[:1021] + "...",
                inline=False
            )

            embed.set_footer(text="Powered by OpenAI GPT-4o-mini")

            # Edit the thinking message with response
            await thinking_msg.edit(content=None, embed=embed)

        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__

            # Log full error for debugging
            print(f"ChatGPT Error: {error_type}: {error_message}")

            if len(error_message) > 1800:
                error_message = error_message[:1797] + "..."

            # Check for specific error types with detailed troubleshooting
            if '429' in error_message or 'rate limit' in error_message.lower():
                await thinking_msg.edit(content="❌ **Rate Limit Exceeded**\n\nYou've hit the OpenAI API rate limit. Please wait a moment before trying again.")

            elif 'quota' in error_message.lower() or 'insufficient_quota' in error_message.lower() or 'billing' in error_message.lower():
                detailed_message = (
                    "❌ **API Quota Exceeded**\n\n"
                    "Your OpenAI account has exceeded its quota. Here's how to fix it:\n\n"
                    "**1. Check Your Usage:**\n"
                    "→ Visit: https://platform.openai.com/usage\n"
                    "→ See how much credit you've used\n\n"
                    "**2. Check Your Billing:**\n"
                    "→ Visit: https://platform.openai.com/settings/organization/billing\n"
                    "→ Add a payment method if you haven't already\n"
                    "→ Free credits ($5) expire after 3 months\n\n"
                    "**3. Check Your Limits:**\n"
                    "→ Visit: https://platform.openai.com/settings/organization/limits\n"
                    "→ See your current tier and limits\n\n"
                    f"**Error Details:** `{error_message[:200]}`"
                )
                await thinking_msg.edit(content=detailed_message)

            elif 'invalid' in error_message.lower() and 'key' in error_message.lower():
                detailed_message = (
                    "❌ **Invalid API Key Error**\n\n"
                    "The OpenAI API rejected your key. Possible causes:\n\n"
                    "**1. Key is revoked or deleted**\n"
                    "→ Check: https://platform.openai.com/api-keys\n"
                    "→ Regenerate if needed\n\n"
                    "**2. Wrong key format**\n"
                    "→ Should start with `sk-proj-` or `sk-`\n"
                    "→ Check for extra spaces/newlines\n\n"
                    "**3. Organization/Project mismatch**\n"
                    "→ Key might be for wrong organization\n"
                    "→ Create a new project key\n\n"
                    f"**Error:** `{error_message[:250]}`"
                )
                await thinking_msg.edit(content=detailed_message)

            elif 'billing' in error_message.lower() or 'payment' in error_message.lower():
                await thinking_msg.edit(
                    content="❌ **Billing Issue**\n\n"
                    "There's a problem with your OpenAI billing.\n"
                    "Check: https://platform.openai.com/settings/organization/billing\n\n"
                    f"Error: `{error_message[:300]}`"
                )

            else:
                await thinking_msg.edit(
                    content=f"❌ **Error communicating with ChatGPT**\n\n"
                    f"**Error Type:** `{error_type}`\n"
                    f"**Details:** ```{error_message}```\n\n"
                    "Check the bot console for full error details."
                )
