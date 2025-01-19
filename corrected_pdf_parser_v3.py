
import re
from PyPDF2 import PdfReader

# Extract raw text from PDF
def extract_text_from_pdf(pdf_path):
    print("Extracting Text from PDF")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Write raw text to file for debugging
    with open("./temp_outputs/temp.txt", 'w') as f:
        f.write(text)

    return text

# Parse the script into structured dialogue
def parse_script(text, output_path):
    print("Parsing the Script")
    # Initialize variables
    lines = text.splitlines()
    parsed_lines = []
    current_location = ""
    current_character = None
    current_dialogue = []

    # Flush the current dialogue block to the output
    def flush_dialogue():
        if current_character and current_dialogue:
            parsed_lines.append(f"[{current_character}] {' '.join(current_dialogue)} [{current_location}]")

    # Handle cases where multiple characters speak simultaneously
    def handle_simultaneous_dialogue(line):
        segments = re.split(r'(?<=[A-Z])\s{2,}(?=[A-Z])', line)  # Split by large spaces between uppercase names
        dialogue_blocks = []
        for segment in segments:
            character_match = re.match(r'^([A-Z\s#\'\d]+):', segment.strip())
            if character_match:
                character = character_match.group(1).strip()
                dialogue = segment[len(character_match.group(0)):].strip()
                dialogue_blocks.append((character, dialogue))
        return dialogue_blocks

    for line in lines:
        line = line.strip()

        # Detect location (e.g., INT. or EXT.)
        location_match = re.match(r'^(INT\.|EXT\.)\s+(.+)', line)
        if location_match:
            flush_dialogue()
            current_location = location_match.group(0)
            current_character = None
            current_dialogue = []
            continue

        # Detect simultaneous dialogue
        if len(re.findall(r'[A-Z]{2,}', line)) > 1 and "  " in line:
            flush_dialogue()
            simultaneous_dialogues = handle_simultaneous_dialogue(line)
            for character, dialogue in simultaneous_dialogues:
                parsed_lines.append(f"[{character}] {dialogue} [{current_location}]")
            current_character = None
            current_dialogue = []
            continue

        # Detect character name in uppercase
        character_match = re.match(r'^([A-Z\s#\'\d]+)(\(.+\))?$', line)
        if character_match:
            flush_dialogue()
            current_character = character_match.group(1).strip()
            current_dialogue = []
            continue

        # Add dialogue lines
        if current_character:
            current_dialogue.append(line)

    # Final flush of remaining dialogue
    flush_dialogue()

    # Write parsed output to file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for parsed_line in parsed_lines:
            output_file.write(parsed_line + '\n')

text = extract_text_from_pdf('./scripts/knives.pdf')
parse_script(text, './temp_outputs/pleasework.txt')
