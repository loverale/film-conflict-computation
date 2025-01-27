import re
import os
import json
from api import * # all file paths

def fargo_script_cleaning():
    with open("fargo_transcript.txt", "r") as file:
        text_data = file.read()

    # print(text_data)

    # Regex pattern to find scenes
    pattern = r'^[A-Z\s.,\'()\-]+$'

    # Find all matches in the script text
    scenes = re.findall(pattern, text_data, re.MULTILINE)

    # Remove duplicates by converting to a set, then back to a list
    unique_scenes = [line.strip() for line in list(set(scenes))]
    unique_scenes = [scene for scene in unique_scenes if scene != "POLICE OFFICER"]

    # Print the scene names
    print(unique_scenes)

    pattern = r"^([A-Z]{3,}(?: [A-Z]{3,})*)(?= )"

    # Find all matches in the script text
    character_names = re.findall(pattern, text_data, re.MULTILINE)

    # Remove duplicates by converting to a set, then back to a list
    unique_character_names = list(set(character_names))

    # Print the character names
    print(unique_character_names)

    noise_items = ['NEARBY', 'ROAD', 'KITCHEN', 'CARLTON CELEBRITY', 'CARL GOT', 'CARL HOLD', 'CHAIN', 'CHAIN RESTAURANT PHONE', 'DINING', 'PARKING', 'FLARE', 'MILLE LACS', 'LOBBY', 'DOWN', 'EMBERS FAMILY', 'HOTEL', 'RAMP', 'MINNEAPOLIS SUBURBAN', 'WIDE', 'UPSTAIRS', 'INSIDE THE',
                'THEIR', 'MASTER', 'BRAINERD MAIN', 'THE', 'LUNDEGAARD', 'THE DOWNTOWN RADISSON', 'MAN', 'GUSTAFSON OLD', 'GUSTAFSON OLDS', 'LIVING', 'FRONT', 'HIGH SHOT', 'FADE OUT', 'BRAINERD POLICE', 'HIGH AND WIDE', 'BACK', 'ROOFTOP PARKING', 'EXIT', 'THROUGH', 'CLOSE', 'FADE', 'MOTEL', 'MOTEL ROOM', 'HARD CUT']

    unique_character_names = [name for name in unique_character_names if name not in noise_items]
    print(unique_character_names)

    new_character_names = []
    for name in unique_character_names:
        # Create a modified name with spaces replaced by underscores
        modified_name = name.replace(" ", "_")
        new_character_names.append(modified_name)

        # Replace the name in the text_data with the modified name
        text_data = re.sub(r'\b' + re.escape(name) + r'\b', modified_name, text_data)

    # Define the output file path
    output_file_path = "fargo_extracted_cleaned.txt"

    # Write the updated content back to a new file
    with open(output_file_path, "w") as file:
        file.write(text_data)

def fargo_json_conversion():
    with open("fargo_extracted_cleaned.txt", "r") as file:
        lines = file.readlines()

    formatted_lines = []
    current_scene = ""
    current_character = ""
    dialogue = ""
    action = ""
    notes = ""

    for line in lines:
        line_dict = {}
        if not line.strip():
            continue
        if line.strip() in unique_scenes:
            current_scene = line.strip()
        elif line.strip().split()[0] in new_character_names:
            current_character = line.strip().split()[0]
            dialogue = line.strip().replace(current_character + " ", "")

            # Add the current scene, character, and text to the line_dict
            line_dict["scene"] = current_scene
            line_dict["character"] = current_character
            line_dict["dialogue"] = dialogue

            mentioned_characters = []
            for character_name in new_character_names:
                if re.search(r'\b' + re.escape(character_name.replace("_", " ")) + r'\b', dialogue, re.IGNORECASE):
                    mentioned_characters.append(character_name)
                    break

            line_dict["mentioned_characters"] = mentioned_characters
            
            # Add the line_dict to the formatted_lines list
            formatted_lines.append(line_dict)

            # Reset the current_character, current_text, and notes
            current_character = ""
            dialogue = ""

        elif line.strip() and not line.strip().split()[0] in new_character_names:
            action = line.strip()
            line_dict["scene"] = current_scene
            line_dict["action"] = action
            mentioned_characters = []
            for character_name in new_character_names:
                if re.search(r'\b' + re.escape(character_name.replace("_", " ")) + r'\b', action, re.IGNORECASE):
                    mentioned_characters.append(character_name)
                    break
            line_dict["mentioned_characters"] = mentioned_characters
            formatted_lines.append(line_dict)
        else:
            pass

    with open('formatted_lines.json', 'w') as json_file:
        json.dump(formatted_lines, json_file)