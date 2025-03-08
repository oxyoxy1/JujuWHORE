# cursed_energy.py
import json
import os

# Path to the cursed energy JSON file
CursedEnergyFile = "cursed_energy.json"

# Ensure cursed_energy.json exists
if not os.path.exists(CursedEnergyFile):
    with open(CursedEnergyFile, 'w') as f:
        json.dump({}, f)  # Start with an empty dict if no file exists

def get_user_cursed_energy(user_id):
    """ Get the cursed energy for a specific user from the JSON file """
    with open(CursedEnergyFile, 'r') as f:
        data = json.load(f)
    return data.get(str(user_id), {"energy": 0, "level": 0})

def update_user_cursed_energy(user_id, energy_to_add, bot):
    """ Update the cursed energy for a specific user in the JSON file """
    with open(CursedEnergyFile, 'r') as f:
        data = json.load(f)

    # Get current data, defaulting to 0 energy and level 0 if user not found
    current_data = data.get(str(user_id), {"energy": 0, "level": 0})
    current_data["energy"] += energy_to_add

    # Check if level-up is triggered
    new_level = current_data["energy"] // 500
    if new_level > current_data["level"]:
        current_data["level"] = new_level
        # Notify level-up in the channel
        level_up_message(user_id, new_level, bot)

    # Save the updated data back to the file
    data[str(user_id)] = current_data
    with open(CursedEnergyFile, 'w') as f:
        json.dump(data, f, indent=4)

def level_up_message(user_id, new_level, bot):
    """ Notify the user of their level-up in the level-up channel """
    level_up_channel_id = 1346594687909232671  # Channel ID for level-up notifications
    # Construct the level-up message
    message = f"User <@{user_id}> has reached level {new_level}! Congratulations on accumulating more cursed energy!"

    # Send the message to the level-up channel (this requires a bot instance)
    level_up_channel = bot.get_channel(level_up_channel_id)
    if level_up_channel:
        bot.loop.create_task(level_up_channel.send(message))
