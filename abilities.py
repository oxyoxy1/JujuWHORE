import json
import os

# Path to the abilities JSON file
ABILITIES_FILE = "abilities.json"

# Ensure abilities.json exists
if not os.path.exists(ABILITIES_FILE):
    with open(ABILITIES_FILE, 'w') as f:
        json.dump({}, f)  # Start with an empty dict if no file exists

def get_user_abilities(user_id):
    """ Get the abilities for a specific user from the JSON file """
    with open(ABILITIES_FILE, 'r') as f:
        data = json.load(f)
    return data.get(str(user_id), {
        "domain_expansion": False,
        "reverse_cursed_technique": False,
        "technique_maximum": False,
        "simple_domain": False,
        "hollow_wicker_basket": False
    })

def update_user_abilities(user_id, ability_name, status):
    """ Update a specific user's ability status in the JSON file """
    with open(ABILITIES_FILE, 'r') as f:
        data = json.load(f)

    # Initialize user if not found
    if str(user_id) not in data:
        data[str(user_id)] = {
            "domain_expansion": False,
            "reverse_cursed_technique": False,
            "technique_maximum": False,
            "simple_domain": False,
            "hollow_wicker_basket": False
        }

    # Update the specific ability's status
    data[str(user_id)][ability_name] = status

    # Save the updated data back to the file
    with open(ABILITIES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def check_ability_purchase(user_id, ability_name, cursed_energy):
    """ Check if the user has enough cursed energy to buy an ability """
    ability_costs = {
        "domain_expansion": 1000,
        "reverse_cursed_technique": 800,
        "technique_maximum": 800,
        "simple_domain": 400,
        "hollow_wicker_basket": 400
    }

    # Check if the user has enough cursed energy
    if ability_name not in ability_costs:
        return False, "Ability not found."

    required_energy = ability_costs[ability_name]
    if cursed_energy >= required_energy:
        return True, required_energy
    else:
        return False, "You don't have enough cursed energy."
