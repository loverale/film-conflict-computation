import re
import os
import json
from api import * #PATHS TO LOCAL SYSTEM - this is where we store the extracted files and such

def character_name_parser():
    with open(truman_extracted, "r") as file:
        text_data = file.read()
    # print(text_data)

    # Regex pattern to find all character names
    # This pattern matches sequences of capital letters that represent character names.
    # Breakdown of the pattern:
    # - \b: Asserts a word boundary, ensuring the match is at the start of a word.
    # - [A-Z]{3,}: Matches a sequence of three or more uppercase letters (A-Z).
    # - (?:\'[A-Z]+)?: Optionally matches an apostrophe followed by one or more uppercase letters (e.g., "O'NEIL").
    # - (?:\s[A-Z]{2,})*: Optionally matches a space followed by two or more uppercase letters, allowing for multi-part names (e.g., "JOHN DOE").
    # - \b: Asserts a word boundary at the end of the match.

    pattern = r'\b[A-Z]{3,}(?:\'[A-Z]+)?(?:\s[A-Z]{2,})*\b'

    # Find all matches in the script text
    character_names = re.findall(pattern, text_data)

    # Remove duplicates by converting to a set, then back to a list
    unique_character_names = list(set(character_names))

    # Print the character names
    #print(unique_character_names) #useful for debugging

    new_character_names = []
    for name in unique_character_names:
        # Create a modified name with spaces replaced by underscores
        modified_name = name.replace(" ", "_")
        new_character_names.append(modified_name)

        # Replace the name in the text_data with the modified name
        text_data = re.sub(r'\b' + re.escape(name) + r'\b', modified_name, text_data)

        # Add a line break before the name (modified or original)
        text_data = re.sub(
            r'(?<!\n)(' + re.escape(modified_name) + r')', r'\n\n\1', text_data)

    # Write the updated content back to a new file
    with open(truman_extracted_cleaned, "w") as file:
        file.write(text_data)

# todo:// better function name
def text_to_json():
    # extraced from LLM (todo:// look into generalizable regex to automate this)
    scene_locations = [
        "The Lunar Room",
        "Truman's Bathroom",
        "On Truman's Porch",
        "Truman's Car",
        "Newspaper Stand",
        "In Front of Chicken Ad",
        "At the Revolving Door, Truman's Office",
        "Truman's Office",
        "At the Docks",
        "Truman's Lawn",
        "Unfinished Bridge",
        "Flashback to Ocean",
        "Beach",
        "Truman Home",
        "Security Garage",
        "On the Street",
        "Truman's Mother's House",
        "Truman's Basement",
        "The Truman Bar",
        "Flashback: In Front of Truman's College",
        "College Dance",
        "Library",
        "Beach",
        "Truman's Living Room",
        "Hospital",
        "Travel Agent's Office",
        "Bus Station",
        "On the Bus",
        "Truman Bar",
        "Driving in Circles",
        "At the Bridge Out of Seahaven",
        "On the Road",
        "Truman's Home",
        "Nuclear Power Plant Emergency",
        "In the Forest",
        "Truman's Home - Later",
        "Unfinished Bridge",
        "Control Room",
        "Truman's Lawn",
        "Around the Town",
        "At River Bridge - Blockaded",
        "The Santa Maria (Truman's Boat)",
        "Man in Bathtub",
        "Control Room and Exit Door",
        "Truman Bar/Bathtub/Old Lady's Living Room/etc.",
        "Security Garage"
    ]

    with open(truman_extracted_cleaned, "r") as file:
        lines = file.readlines()

    formatted_lines = []
    current_scene = ""
    current_character = ""
    current_text = ""
    notes = ""
    for line in lines:
        line_dict = {}
        if not line.strip():
            continue
        if line.strip() in scene_locations:
            current_scene = line.strip()
        elif line.strip().split()[0] in new_character_names:
            current_character = line.strip().split()[0]
            current_text = line.strip().replace(current_character + " ", "")

            # Remove parenthetical notes from the text
            if current_text.startswith("("):
                notes = current_text[current_text.find("(") + 1:current_text.find(")")]
                current_text = current_text.replace(f"({notes})", "")

            # Add the current scene, character, and text to the line_dict
            line_dict["scene"] = current_scene
            line_dict["character"] = current_character
            line_dict["text"] = current_text
            line_dict["notes"] = notes
            
            # Add the line_dict to the formatted_lines list
            formatted_lines.append(line_dict)

            # Reset the current_character, current_text, and notes
            current_character = ""
            current_text = ""
            notes = ""

        else:
            pass

    with open(truman_json, 'w') as json_file:
        json.dump(formatted_lines, json_file)

