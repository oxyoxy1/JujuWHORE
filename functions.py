import random
import logging
import requests
from pytubefix import YouTube
from bs4 import BeautifulSoup
import re
import discord
from discord import Embed
import asyncio

TRADE_CHANNEL_ID = TRADE_CHANNEL_ID  # The trade channel ID

# URLs for scraping
INNATE_URL = 'https://jujutsu-kaisen.fandom.com/wiki/Category:Innate_Techniques?from=U'

def create_health_bar(current_health, max_health):
    """Creates a health bar representation using emojis."""
    # Calculate health percentage
    health_percentage = current_health / max_health
    # Determine the number of green squares (full health) and red squares (damage)
    full_health_blocks = int(health_percentage * 20)  # We use 20 blocks to represent full health
    empty_health_blocks = 20 - full_health_blocks  # Remaining blocks are empty

    # Construct health bar using green and red squares
    health_bar = "🟩" * full_health_blocks + "🟥" * empty_health_blocks
    return health_bar

async def websocket_check(voice_client):
    print("Creating websocket check loop")
    while True:
        try:
            # Check if voice client is connected
            if not voice_client.is_connected():
                print("Voice client is not connected. Attempting to reconnect...")
                # Try reconnecting if disconnected
                voice_channel = voice_client.channel
                await voice_client.disconnect()
                voice_client = await voice_channel.connect()

            # Check if voice client WebSocket is open
            elif not voice_client.ws or not voice_client.ws._connection.is_open:
                print("WebSocket is closed. Reconnecting...")
                # Reconnect if WebSocket is closed
                voice_channel = voice_client.channel
                await voice_client.disconnect()
                voice_client = await voice_channel.connect()

        except Exception as e:
            print(f"Error in websocket check: {e}")

        # Check every second
        await asyncio.sleep(1)

# Function to initiate the trade process
async def initiate_trade(ctx):
    # Step 1: Ask the user what they're offering
    await ctx.send("Let's start your trade. What item are you offering? (Type 'done' when finished)")

    offered_items = []  # Store the items being offered
    while True:
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        # Wait for the user's response
        offered_item_msg = await ctx.bot.wait_for('message', check=check)
        if offered_item_msg.content.lower() == 'done':
            break
        else:
            offered_items.append(offered_item_msg.content)

    # Step 2: Ask the user what they want in return
    await ctx.send("What are you looking for in return? (Type 'done' when finished)")

    wanted_items = []  # Store the items the user wants
    while True:
        wanted_item_msg = await ctx.bot.wait_for('message', check=check)
        if wanted_item_msg.content.lower() == 'done':
            break
        else:
            wanted_items.append(wanted_item_msg.content)

    # Step 3: Post the trade request in the #tradengrind channel
    trade_embed = Embed(
        title=f"Trade Request from {ctx.author.name}",
        description="Here is the trade offer:",
        color=discord.Color.blue()
    )

    trade_embed.add_field(name="Offered Items", value="\n".join(offered_items) if offered_items else "None")
    trade_embed.add_field(name="Wanted Items", value="\n".join(wanted_items) if wanted_items else "None")

    trade_channel = ctx.guild.get_channel(TRADE_CHANNEL_ID)
    if trade_channel:
        # Mention the roles for notifications
        roles = ["<@&YOUR_ROLE_ID_1>", "<@&YOUR_ROLE_ID_2>", "<@YOUR_ROLE_ID_3>", 
                 "<@&YOUR_ROLE_ID_4>", "<@&YOUR_ROLE_ID_5>"]
        await trade_channel.send(" ".join(roles), embed=trade_embed)
        await ctx.send("Your trade request has been posted in the trade channel!")
    else:
        await ctx.send("Error: Could not find the trade channel.")

    logging.info(f"Trade initiated by {ctx.author.name} with offered items: {offered_items} and wanted items: {wanted_items}")

# Scrape the Innate Techniques page to get the list of techniques
def fetch_innate_techniques():
    try:
        response = requests.get(INNATE_URL)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the technique links
        techniques = []
        for link in soup.find_all('a', class_='category-page__member-link'):
            technique_name = link.get_text(strip=True)
            technique_url = 'https://jujutsu-kaisen.fandom.com' + link.get('href')

            if not technique_name.lower().startswith("category:"):
                techniques.append((technique_name, technique_url))
        
        logging.info(f"Successfully fetched {len(techniques)} techniques.")
        return techniques
    except Exception as e:
        logging.error(f"Error fetching techniques: {e}")
        return []

# Scrape the specific technique page for more info (description and image)
def fetch_technique_info(technique_url):
    try:
        response = requests.get(technique_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        description = None
        image_url = None

        # Get description and image if available
        description_section = soup.find('div', class_='pi-item pi-data pi-item-spacing pi-border-color')
        if description_section:
            description = description_section.get_text(strip=True)
            description = re.sub(r"(kanji\s*:*\s*)", "", description, flags=re.IGNORECASE).strip()

        image_section = soup.find('img', {'class': 'pi-image-thumbnail'})
        if image_section:
            image_url = image_section.get('src')

        logging.info(f"Fetched description: {description[:50]}...")
        logging.info(f"Fetched image URL: {image_url}")
        return description, image_url
    except Exception as e:
        logging.error(f"Error fetching technique info from {technique_url}: {e}")
        return None, None

# Play music in the voice channel
async def play_music_in_voice_channel(voice_client, selected_mix):
    max_retries = 3  # Limit the number of retries
    attempt = 0
    while attempt < max_retries:
        try:
            yt = YouTube(selected_mix)
            audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
            audio_url = audio_stream.url

            audio_source = discord.FFmpegPCMAudio(audio_url, executable="ffmpeg")
            
            if not voice_client.is_playing():
                logging.info(f"Playing {selected_mix}")
                voice_client.play(audio_source, after=lambda e: print('done', e))
                return True
            else:
                logging.info("Already playing music, skipping...")
            return False
        except Exception as e:
            logging.error(f"Error playing music: {e}. Attempt {attempt + 1}/{max_retries}")
            attempt += 1
            if attempt < max_retries:
                await asyncio.sleep(3)  # Delay before retrying
            else:
                logging.error(f"Max retries reached for {selected_mix}. Could not play the music.")
                return False

async def disconnect_after_inactivity(voice_client):
    await asyncio.sleep(600)
    if not voice_client.is_playing():
        await voice_client.disconnect()
