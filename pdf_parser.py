import re
import json
import pymupdf
from PyPDF2 import PdfReader

# Parse the PDF and extract content
def parse_script(pdf_path):
    reader = PdfReader(pdf_path)
    json_output = []
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text().splitlines()
        scene_data = {
            "page": page_num,
            "scene_info": {},
            "scene": {
                "dialogue": [],
            }
        }
        
        current_scene_info = None
        current_character = None
        for line in page_text:
            line = line.strip()
            if not line:
                continue

            # Check for scene headings (INT./EXT. etc.)
            scene_info = classify_scene(line)
            if scene_info:
                if current_scene_info:
                    # Store the previous scene
                    json_output.append(current_scene_info)
                # Start a new scene
                current_scene_info = {
                    "page": page_num,
                    "scene_info": scene_info,
                    "scene": []
                }
            elif is_dialogue(line):
                # If it's a character name, set current_character
                current_character = line
            elif current_character:
                # Dialogue lines follow character names
                current_scene_info["scene"].append({
                    "type": "CHARACTER",
                    "content": {
                        "character": current_character,
                        "dialogue": line
                    }
                })
                current_character = None  # Reset after dialogue
            else:
                # Otherwise, treat it as action information
                current_scene_info["scene"].append({
                    "type": "ACTION",
                    "content": {
                        "action_description": line
                    }
                })
        
        if current_scene_info:
            json_output.append(current_scene_info)
        else:
            pass

    return json_output

# Save the output as JSON
def save_as_json(parsed_data, output_path):
    with open(output_path, 'w') as outfile:
        json.dump(parsed_data, outfile, indent=4)    

pdf_path = "./scripts/social.pdf"  # Replace this with the actual path to your PDF
output_json = "./output/parsed_script.json"  # Output JSON file
    
parsed_data = parse_script(pdf_path)

print(parsed_data)

#save_as_json(parsed_data, output_json)
print(f"Script has been parsed and saved to {output_json}")