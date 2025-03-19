import discord
from discord.ext import commands, tasks
import logging
import random
import asyncio
from discord.ui import Button, View
from discord import Embed
import json
from pytubefix import YouTube
from functions import fetch_innate_techniques, fetch_technique_info, play_music_in_voice_channel, disconnect_after_inactivity, initiate_trade, websocket_check, create_health_bar
from helpers import get_random_greedy_image, questions
from cursed_energy import update_user_cursed_energy, get_user_cursed_energy  # Importing functions
from abilities import get_user_abilities, update_user_abilities, check_ability_purchase

# Set up logging to help with debugging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True  # Allow the bot to read message content

FACTION_FILE = 'factions.json'
FACTION_CHANNEL_ID = CHANNEL_ID_FOR_FACTIONS  # The faction management channel ID

# Set up bot with a command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

VOICE_CHANNEL_ID = VOICE_CHANNEL_ID  # The voice channel ID
TRADE_CHANNEL_ID = TRADE_CHANNEL_ID  # The trade channel ID

# Global variables for music queue
music_queue = []
current_track = None
disconnect_timer = None  # Initialize disconnect_timer globally

@bot.command(name="start_trivia")
async def start_trivia(ctx):
    # Create an activity (trivia)
    activity = discord.Game(name="Jujutsu Kaisen Trivia! Type !join to participate.")
    
    # Set the activity for the bot
    await bot.change_presence(activity=activity)
    
    await ctx.send(f"**Jujutsu Kaisen Trivia Game has started!** {ctx.author.mention} has started a trivia game. Type `!join` to participate.")

@bot.command(name="join")
async def join_trivia(ctx):
    # Add the user to the list of participants
    if not hasattr(ctx.bot, 'participants'):
        ctx.bot.participants = []

    if ctx.author not in ctx.bot.participants:
        ctx.bot.participants.append(ctx.author)
        await ctx.send(f"{ctx.author.mention} has joined the trivia game!")
    else:
        await ctx.send(f"{ctx.author.mention}, you have already joined the trivia game.")

# Command to start the trivia game and ask questions
@bot.command(name="trivia")
async def trivia_game(ctx):
    if not hasattr(ctx.bot, 'participants') or len(ctx.bot.participants) == 0:
        await ctx.send("No one has joined the trivia game yet! Type `!join` to participate.")
        return

    score = {user: 0 for user in ctx.bot.participants}  # Keep score for all participants

    # Ask 5 random trivia questions
    for i in range(5):
        question = random.choice(questions)  # Assuming questions are imported from helpers.py
        await ctx.send(f"**Question {i+1}:** {question['question']}")

        def check(msg):
            return msg.author in ctx.bot.participants and msg.channel == ctx.channel

        try:
            # Wait for responses from all users
            answer_msg = await bot.wait_for("message", check=check, timeout=30)

            if any(answer.lower() == answer_msg.content.lower() for answer in question['answers']):
                score[answer_msg.author] += 1
                await ctx.send(f"Correct! {answer_msg.author.mention} earns a point!")
            else:
                await ctx.send(f"Wrong! The correct answer was: **{', '.join(question['answers'])}**")
        except asyncio.TimeoutError:
            await ctx.send(f"Time's up! The correct answer was: **{', '.join(question['answers'])}**")

    # Determine the winner (the participant with the highest score)
    winner = max(score, key=score.get)
    winner_score = score[winner]
    
    # Display the final score and announce the winner
    leaderboard = "\n".join([f"{user.name}: {score[user]} points" for user in ctx.bot.participants])
    await ctx.send(f"**Final Scores:**\n{leaderboard}")
    await ctx.send(f"Congratulations {winner.mention}! You are the winner with {winner_score} points! 🎉")

    # Award the winner 2500 cursed energy
    update_user_cursed_energy(winner.id, 2500, ctx.bot)  # Award 2500 cursed energy
    updated_energy = get_user_cursed_energy(winner.id)["energy"]  # Get the updated cursed energy
    await ctx.send(f"{winner.mention}, you have earned 2500 cursed energy for winning! Total cursed energy is now {updated_energy}.")

    # Reset the trivia participants for future games
    ctx.bot.participants = []

# Function to load faction data from factions.json
def load_faction_data():
    with open("factions.json", "r") as file:
        return json.load(file)

# Function to save faction data to factions.json
def save_faction_data(data):
    with open("factions.json", "w") as file:
        json.dump(data, file, indent=4)

# Function to calculate the duel power (without factions)
def calculate_duel_power(user_id):
    """ Calculate the duel power based on cursed energy and abilities multiplier """
    # Get the user's cursed energy directly from their data (no factions involved)
    user_cursed_energy = get_user_cursed_energy(user_id)["energy"]  # Assuming this function exists in your abilities.py
    
    # Get the user's abilities (from abilities.py, assuming the user_id is correctly passed)
    abilities = get_user_abilities(user_id)
    
    # Calculate power based on abilities and cursed energy
    power = user_cursed_energy
    power += abilities.get("domain_expansion", 0) * 0.5
    power += abilities.get("reverse_cursed_technique", 0) * 0.45
    power += abilities.get("technique_maximum", 0) * 0.4
    power += abilities.get("hollow_wicker_basket", 0) * 0.25
    power += abilities.get("simple_domain", 0) * 0.2
    
    return power


@bot.command(name="duel")
async def duel(ctx):
    """ Handle the duel between two users without involving factions """
    
    # Prompt the user for duel details
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    # Ask the initiating user who they want to duel
    await ctx.send(f"{ctx.author.mention}, who would you like to duel? Mention the other user.")
    duel_mention_msg = await bot.wait_for('message', check=check)
    opponent = duel_mention_msg.mentions[0]  # Get the opponent mentioned

    # Ask how much cursed energy they want to wager
    await ctx.send(f"{ctx.author.mention}, how much cursed energy do you want to wager? (Must be a positive number)")

    wager_msg = await bot.wait_for('message', check=check)
    wager = int(wager_msg.content)

    # Send duel request to the opponent (the mentioned user)
    await opponent.send(f"**{ctx.author.name}** has challenged you to a duel! They want to wager {wager} cursed energy. Do you accept? (Reply 'yes' or 'no')")

    # Check for opponent's response
    def opponent_check(msg):
        return msg.author == opponent and msg.channel.type == discord.ChannelType.private  # Make sure it's the opponent's DM

    try:
        # Wait for the opponent to respond within 30 seconds
        duel_response = await bot.wait_for('message', check=opponent_check, timeout=30.0)

        if duel_response.content.lower() == "yes":
            # Proceed with duel if accepted
            user_duel_power = calculate_duel_power(ctx.author.id)
            opponent_duel_power = calculate_duel_power(opponent.id)
            
            # Ensure both users have enough cursed energy for the duel
            if user_duel_power < wager or opponent_duel_power < wager:
                await ctx.send("One of you does not have enough cursed energy to wager this amount. Duel canceled.")
                return

            # Create health bars for each user before the duel
            user_health_bar = create_health_bar(user_duel_power, user_duel_power + opponent_duel_power)
            opponent_health_bar = create_health_bar(opponent_duel_power, user_duel_power + opponent_duel_power)

            # Send duel status message with health bars
            duel_embed = discord.Embed(
                title="Duel Starting!",
                description=f"{ctx.author.name} vs {opponent.name}\n\n"
                            f"**{ctx.author.name}'s Health:** {user_health_bar} ({user_duel_power} CE)\n"
                            f"**{opponent.name}'s Health:** {opponent_health_bar} ({opponent_duel_power} CE)\n\n"
                            f"Wager: {wager} Cursed Energy",
                color=discord.Color.green()
            )

            duel_message = await ctx.send(embed=duel_embed)

            # Determine the winner
            winner = ctx.author if user_duel_power > opponent_duel_power else opponent
            loser = opponent if winner == ctx.author else ctx.author

            # Announce the winner and loser
            await ctx.send(f"{winner.mention} wins the duel and takes all the cursed energy!")

            # Store the duel outcome in a leaderboard (in a new `leaderboard.json` file)
            try:
                with open("leaderboard.json", "r") as file:
                    leaderboard = json.load(file)
            except FileNotFoundError:
                leaderboard = {}

            # Increment the winner's wins in the leaderboard
            winner_id = str(winner.id)
            if winner_id not in leaderboard:
                leaderboard[winner_id] = {"wins": 0}
            leaderboard[winner_id]["wins"] += 1

            # Save the leaderboard data
            with open("leaderboard.json", "w") as file:
                json.dump(leaderboard, file, indent=4)

            # Display the leaderboard
            leaderboard_embed = discord.Embed(title="Duel Leaderboard", color=discord.Color.blue())
            for user_id, stats in leaderboard.items():
                user = await bot.fetch_user(user_id)
                leaderboard_embed.add_field(name=user.name, value=f"{stats['wins']} wins", inline=False)

            duel_channel = bot.get_channel(1346591739930214531)  # Duel channel ID
            if duel_channel:
                await duel_channel.send(embed=leaderboard_embed)

            # After duel: Update health bars and display the result
            final_user_duel_power = user_duel_power + wager if winner == ctx.author else user_duel_power - wager
            final_opponent_duel_power = opponent_duel_power + wager if winner == opponent else opponent_duel_power - wager

            # Update health bars after duel
            user_health_bar = create_health_bar(final_user_duel_power, final_user_duel_power + final_opponent_duel_power)
            opponent_health_bar = create_health_bar(final_opponent_duel_power, final_user_duel_power + final_opponent_duel_power)

            # Update the duel embed with final health bars
            duel_embed.description = f"{ctx.author.name}'s Health: {user_health_bar} ({final_user_duel_power} CE)\n" \
                                     f"{opponent.name}'s Health: {opponent_health_bar} ({final_opponent_duel_power} CE)\n" \
                                     f"Final Result: {'You won!' if winner == ctx.author else 'You lost!'}"

            # Edit the duel message with updated health bars
            await duel_message.edit(embed=duel_embed)

        elif duel_response.content.lower() == "no":
            await opponent.send(f"**{ctx.author.name}**'s duel request has been declined.")
            await ctx.send(f"{opponent.mention} has declined the duel request.")
        else:
            await opponent.send(f"Invalid response. Duel request has been canceled.")
            await ctx.send(f"{opponent.mention} did not respond correctly. Duel canceled.")

    except asyncio.TimeoutError:
        await opponent.send("You took too long to respond! Duel request has been canceled.")
        await ctx.send(f"{opponent.mention} did not respond in time. Duel canceled.")


# Shop Command
@bot.command(name='shop')
async def shop(ctx):
    user_id = ctx.author.id
    cursed_energy = get_user_cursed_energy(user_id)["energy"]  # Get cursed energy from the user's record

    # Available abilities and their descriptions
    abilities = {
        "domain_expansion": {"cost": 1000, "description": "A powerful domain that increases your power."},
        "reverse_cursed_technique": {"cost": 800, "description": "The ability to reverse cursed techniques."},
        "technique_maximum": {"cost": 800, "description": "Unlock maximum techniques for ultimate strength."},
        "simple_domain": {"cost": 400, "description": "A simple domain that enhances your abilities."},
        "hollow_wicker_basket": {"cost": 400, "description": "A technique that traps enemies in a cursed domain."}
    }

    # Create an embed to display the abilities and their costs
    embed = Embed(title="Cursed Energy Shop", description="Welcome to the Cursed Energy Shop! Choose an ability to purchase.")
    
    for ability, info in abilities.items():
        status = "Unlocked" if get_user_abilities(user_id).get(ability, False) else "Locked"
        embed.add_field(
            name=f"{ability.replace('_', ' ').title()} - {info['cost']} CE",
            value=f"Description: {info['description']}\nStatus: {status}",
            inline=False
        )

    # Send the embed with abilities
    await ctx.send(embed=embed)

    # Ask the user to select an ability to purchase
    await ctx.send("Which ability would you like to purchase? Respond with the name.")

    # Wait for user's response
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        user_response = await bot.wait_for('message', check=check, timeout=60)
        ability_name = user_response.content.lower().replace(" ", "_")  # Normalize input to match ability names

        # Check if the user can purchase the ability
        can_purchase, result = check_ability_purchase(user_id, ability_name, cursed_energy)

        if can_purchase:
            # Unlock the ability and deduct cursed energy
            update_user_abilities(user_id, ability_name, True)
            update_user_cursed_energy(user_id, -result, bot)  # Deduct cursed energy
            await ctx.send(f"{ctx.author.mention}, you have successfully purchased the **{ability_name.replace('_', ' ').title()}**!")
        else:
            await ctx.send(f"{ctx.author.mention}, {result}")

    except TimeoutError:
        await ctx.send(f"{ctx.author.mention}, you took too long to respond. Please try again.")

# Load faction data from the JSON file
def load_faction_data():
    try:
        with open(FACTION_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"Higher Ups": {}, "Non-Sorcerer Killers": {}, "Brothers": {}}


# Save faction data to the JSON file
def save_faction_data(data):
    with open(FACTION_FILE, 'w') as file:
        json.dump(data, file, indent=4)


# Faction command
@bot.command(name='faction')
async def faction(ctx):
    faction_data = load_faction_data()

    # Check if the user is already in a faction
    user_faction = None
    for faction_name, members in faction_data.items():
        if ctx.author.id in members:
            user_faction = faction_name
            break
    
    if user_faction:
        await ctx.send(f"You are already a member of the {user_faction}.")
        return

    # Create faction selection buttons
    async def select_faction(interaction, faction_name):
        if ctx.author.id in faction_data[faction_name]:
            await interaction.response.send_message(f"You are already in the {faction_name}.")
            return

        # Assign the user to the faction
        if len(faction_data[faction_name]) == 0:
            faction_data[faction_name][ctx.author.id] = {"role": "Leader"}
            await interaction.response.send_message(f"Congratulations! You are the leader of the {faction_name}!")
        else:
            faction_data[faction_name][ctx.author.id] = {"role": "Member"}
            await interaction.response.send_message(f"You have joined the {faction_name}.")

        # Save the data
        save_faction_data(faction_data)

    # Create the embed and buttons for faction selection
    embed = discord.Embed(
        title="Select your faction",
        description="Choose one of the factions to join.",
        color=discord.Color.blue()
    )

    view = View()

    good_button = Button(label="The Higher Ups", style=discord.ButtonStyle.green)
    good_button.callback = lambda interaction: select_faction(interaction, "Higher Ups")
    view.add_item(good_button)

    evil_button = Button(label="Non-Sorcerer Killers", style=discord.ButtonStyle.red)
    evil_button.callback = lambda interaction: select_faction(interaction, "Non-Sorcerer Killers")
    view.add_item(evil_button)

    neutral_button = Button(label="Brothers", style=discord.ButtonStyle.grey)
    neutral_button.callback = lambda interaction: select_faction(interaction, "Brothers")
    view.add_item(neutral_button)

    await ctx.send(embed=embed, view=view)


# Leader command to view join requests and approve/deny
@bot.command(name='view_requests')
async def view_requests(ctx):
    faction_data = load_faction_data()

    # Check if the user is a leader of any faction
    for faction_name, members in faction_data.items():
        if ctx.author.id in members and members[ctx.author.id]["role"] == "Leader":
            # Display join requests for this faction
            requests = [user_id for user_id, member in members.items() if member["role"] == "Pending"]
            if not requests:
                await ctx.send("No join requests pending.")
                return
            
            # Create embed with the join requests
            embed = discord.Embed(
                title=f"{faction_name} Join Requests",
                description="Click a button to approve or deny a request.",
                color=discord.Color.orange()
            )

            # Generate buttons for each request
            view = View()
            for request_user_id in requests:
                user = await bot.fetch_user(request_user_id)
                approve_button = Button(label=f"Approve {user.name}", style=discord.ButtonStyle.green)
                deny_button = Button(label=f"Deny {user.name}", style=discord.ButtonStyle.red)

                async def approve(interaction, user_id=request_user_id):
                    faction_data[faction_name][user_id] = {"role": "Member"}
                    await interaction.response.send_message(f"User {user.name} has been approved to join {faction_name}.")
                    save_faction_data(faction_data)

                async def deny(interaction, user_id=request_user_id):
                    del faction_data[faction_name][user_id]
                    await interaction.response.send_message(f"User {user.name} has been denied from joining {faction_name}.")
                    save_faction_data(faction_data)

                approve_button.callback = approve
                deny_button.callback = deny

                view.add_item(approve_button)
                view.add_item(deny_button)

            await ctx.send(embed=embed, view=view)
            return
    
    await ctx.send("You are not the leader of any faction.")

# Trade command
@bot.command(name='trade')
async def trade(ctx):
    # First, initiate the trade process
    await initiate_trade(ctx)

    # Now, award cursed energy for offering the trade
    user_id = ctx.author.id
    # Award cursed energy immediately after the trade offer is made
    update_user_cursed_energy(user_id, 200, ctx.bot)  # Pass the bot instance here

    # Fetch the updated cursed energy and inform the user
    updated_energy = get_user_cursed_energy(user_id)['energy']
    # Inform the user of their cursed energy immediately after the trade offer
    await ctx.send(f"{ctx.author.mention}, you have earned 200 cursed energy for offering the trade! Total cursed energy is now {updated_energy}.")

# Function to play the next track in the queue
async def play_next(ctx, voice_client):
    global music_queue, current_track

    if music_queue:
        current_track = music_queue.pop(0)  # Get the next track in the queue

        # Get the greedier image and create an embed
        selected_image = get_random_greedy_image()
        embed = discord.Embed(title="Welcome to Jujutsu Tech!", description="Watch your back and protect your comrades....", color=discord.Color.green())
        embed.set_image(url=selected_image)

        # Send the greedier image embed first
        await ctx.send(embed=embed)

        # Now send the YouTube link
        await ctx.send(f"Now playing: {current_track}. Don't work TOO hard now!")

        # Attempt to play the music, reconnect if there's a failure
        success = await play_music_in_voice_channel(voice_client, current_track)
        if not success:
            # If playing the music failed, attempt to reconnect and retry
            voice_channel = ctx.author.voice.channel
            await voice_client.disconnect()
            voice_client = await voice_channel.connect()
            await play_music_in_voice_channel(voice_client, current_track)
    else:
        await voice_client.disconnect()

# Command to add a track to the queue
@bot.command(name='enqueue')
async def enqueue(ctx, *args):
    if not args:
        await ctx.send("This command is meant to be followed by a space and then a youtube link. (ex. !enqueue https://youtube.com/random_song")
        return
   
    video_url = args[0]
    music_queue.append(video_url)
    await ctx.send(f"Added {video_url} to the queue. Current queue: {len(music_queue)} track(s).")

    # Check if the bot is not playing anything and start the next track
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and not voice_client.is_playing():
        await play_next(ctx, voice_client)

# Command to view the current music queue
@bot.command(name='queue')
async def view_queue(ctx):
    if music_queue:
        queue_message = "\n".join([f"{index + 1}. {url}" for index, url in enumerate(music_queue)])
        await ctx.send(f"Current Queue:\n{queue_message}")
    else:
        await ctx.send("You forgot to load the queue up!")

# Command to skip to the next track
@bot.command(name='skip')
async def skip(ctx):
    if music_queue:
        # Get the voice channel the user is in
        voice_channel = ctx.author.voice.channel
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if voice_client and voice_client.is_playing():
            voice_client.stop()  # Stop the current track
            await play_next(ctx, voice_client)
        else:
            await ctx.send("No music is currently playing.")
    else:
        await ctx.send("There are no tracks in the queue to skip.")

# Command to play a random mix
@bot.command(name='grind')
async def grind(ctx, *args):
    global current_track  # Declare this as global to update it
    user_id = ctx.author.id
    if ctx.author.voice is None or ctx.author.voice.channel.id != VOICE_CHANNEL_ID:
        await ctx.send("You need to be in the designated voice channel to use this command.")
        return

    mixes = [
        "https://www.youtube.com/watch?v=EpwSSMf6MYE&t=10150s",
        "https://www.youtube.com/watch?v=wqi9b_AiVG8",
        "https://www.youtube.com/watch?v=vzuyBIw9ySQ",
        "https://www.youtube.com/watch?v=RFi98VZETm0",
        "https://www.youtube.com/watch?v=4N9HmMNf7EU",
        "https://www.youtube.com/watch?v=ji4iNHpfk6w",
        "https://www.youtube.com/watch?v=wA50qt0xoqw",
        "https://www.youtube.com/watch?v=VLqPvznkeXA"
        "https://www.youtube.com/watch?v=UE-ycV1hHkQ",
        "https://www.youtube.com/watch?v=oFqaDraJ0Bw",        
        "https://www.youtube.com/watch?v=2VY8Sx0guL4",
        "https://www.youtube.com/watch?v=bNVQ-WxXO7E",
        "https://www.youtube.com/watch?v=vZukymZfRrE",
        "https://www.youtube.com/watch?v=JdU0gDDCiB8",
        "https://www.youtube.com/watch?v=yKdskCnryAc",
        "https://www.youtube.com/watch?v=SEX7GQEoMr8",
        "https://www.youtube.com/watch?v=W4B7C7bntr0",
        "https://www.youtube.com/watch?v=XqmjkAqnLUg"
    ]

    # Randomly select a mix if no number is provided
    selected_mix = random.choice(mixes)
    music_queue.append(selected_mix)  # Add to the queue
    await ctx.send(f"Good luck out there sorcerer. Be greedy.\nAdded {selected_mix} to the queue.")

    # Get the voice channel the user is in
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    try:
        await play_next(ctx, voice_client)  # Start playing the first track in the queue
        # Add cursed energy
        update_user_cursed_energy(user_id, 500, bot)
        # Inform the user of their cursed energy
        await ctx.send(f"{ctx.author.mention}, you have earned 500 cursed energy for grinding! Total cursed energy is now {get_user_cursed_energy(user_id)['energy']}.")
    except Exception as e:
        logging.error(f"Error playing music: {e}")

# Command for community links (Reddit and Discord)
@bot.command(name='community')
async def community(ctx):
    # Post community links and award cursed energy
    user_id = ctx.author.id
    embed = discord.Embed(
        title="Join our Community!",
        description="Visit us on the SubReddit, join the JJI Discord server, or visit the trello board!",
        color=discord.Color.green()
    )
    embed.add_field(name="Reddit", value="https://www.reddit.com/r/JJKCommunity/")
    embed.add_field(name="Discord", value="https://discord.com/invite/jjkinf")
    embed.add_field(name="Trello", value="https://trello.com/b/mV6sSwXY/jujutsu-infinite")
    await ctx.send(embed=embed)
    # Add cursed energy
    update_user_cursed_energy(user_id, 300, bot)
    # Inform the user of their cursed energy
    await ctx.send(f"{ctx.author.mention}, you have earned 300 cursed energy for sharing community links! Total cursed energy is now {get_user_cursed_energy(user_id)['energy']}.")

# Command to display the market link
@bot.command(name='market')
async def market(ctx):
    # Post market link and award cursed energy
    user_id = ctx.author.id
    user_id = ctx.author.id
    market_link = "https://jujutsuinfinite.fandom.com/wiki/Market_Stock#Cursed_Market_Only"
    await ctx.send(f"Check out the curse market here: {market_link}.")
    # Add cursed energy
    update_user_cursed_energy(user_id, 100, bot)
    # Inform the user of their cursed energy
    await ctx.send(f"{ctx.author.mention}, you have earned 100 cursed energy for sharing the market link! Total cursed energy is now {get_user_cursed_energy(user_id)['energy']}.")


# Command to fetch a random innate technique
@bot.command(name='innate')
async def innate(ctx):
    # Spin for innates and award cursed energy
    user_id = ctx.author.id
    techniques = fetch_innate_techniques()
    # Add cursed energy
    update_user_cursed_energy(user_id, 100, bot)
    # Inform the user of their cursed energy
    await ctx.send(f"{ctx.author.mention}, you have earned 100 cursed energy for spinning! Total cursed energy is now {get_user_cursed_energy(user_id)['energy']}.")
    if not techniques:
        await ctx.send("Could not fetch any innate techniques right now.")
        return

    technique_name, technique_url = random.choice(techniques)
    description, image_url = fetch_technique_info(technique_url)

    embed = discord.Embed(
        title=technique_name,
        description=description if description else "No description available.",
        color=discord.Color.blue()
    )

    if image_url:
        embed.set_image(url=image_url)

    embed.add_field(name="More Info", value=technique_url)
    await ctx.send(embed=embed)

@bot.command(name='play')
async def play(ctx):
    global current_track  # Declare this as global to update it

    # Check if the user is in the right voice channel
    if ctx.author.voice is None or ctx.author.voice.channel.id != VOICE_CHANNEL_ID:
        await ctx.send("You need to be in the designated voice channel to start playing!")
        return

    # Check if the music queue is empty
    if not music_queue:
        await ctx.send("The queue is empty, adding a random grind mix...")
        await grind(ctx)  # Call the existing grind function to add and play a random mix
        return

    # Get the voice channel the user is in
    voice_channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # If the bot isn't already connected to the voice channel, connect it
    if not voice_client:
        voice_client = await voice_channel.connect()

    # Start the websocket check task
    bot.loop.create_task(websocket_check(voice_client))

    # Play the next track from the queue
    try:
        await play_next(ctx, voice_client)  # This plays the first track in the queue
    except Exception as e:
        logging.error(f"Error playing music: {e}")
        await ctx.send("An error occurred while trying to play the music.")

bot.run('YOUR_BOT_TOKEN')
