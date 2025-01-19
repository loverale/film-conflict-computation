import re
from PyPDF2 import PdfReader

# gets raw text
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # this isn't needed for actual parsing, but i used this to quick see what to check for in formatting/regex
    with open("./output/test.txt", 'w') as f:
        f.write(text)
    ### 

    return text

# organizes said text a lil better
def parse_script(text, output_path):
    # initialization
    lines = text.splitlines()
    parsed_lines = []
    current_location = ""
    current_character = None
    current_dialogue = []

    # not used to in-function function defs, but seems to be common in python?
    # AI recommended this to solve an issue, so use i shall
    def flush_dialogue():
        if current_character and current_dialogue:
            parsed_lines.append(f"[{current_character}] {' '.join(current_dialogue)} [{current_location}]")

    for line in lines:
        line = line.strip()

        # detect location: INT. or EXT. indicates a location
        location_match = re.match(r'^(INT\.|EXT\.)\s+(.+)', line)
        if location_match:
            flush_dialogue()  # finalizes a characters dialgoue (until reaches a location) - if reaches other character, that logic is handled later

            #reset
            current_location = location_match.group(0)
            current_character = None
            current_dialogue = []
            continue

        # detect character name in uppercase followed by optional parenthetical
        #character_match = re.match(r'^([A-Z\s]+)(\(.+\))?$', line) # OLD REGEX, KEEPING SAFE FOR NOW
        #character_match = re.match(r'^([A-Z\s#]+)(\(.+\))?$', line) # some character names will have #, adding to parse
        #character_match = re.match(r'^([A-Z\s#\d]+)(\(.+\))?$', line) # some character names have too many spaces, checks for that as well?
        character_match = re.match(r'^([A-Z\s#\'\d]+)(\(.+\))?$', line) # and looks for '

        if character_match: # and len(line.split()) <= 30:  # length of character name (probably needs manual checking, keeping long for now)
            flush_dialogue()  # finalizes a characters dialgoue (until reaches another character)
            #reset
            current_character = character_match.group(1).strip()
            current_dialogue = []
            continue

        # keeps adding lines of dialogue
        if current_character:
            current_dialogue.append(line)

    # catch all flush, should really catch end of script
    flush_dialogue()

    # output writing
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for parsed_line in parsed_lines:
            output_file.write(parsed_line + '\n')

# does the thing
pdf_path = './scripts/knives.pdf'  # Path to the uploaded PDF file
output_path = './output/parsed_knives.txt'

# Extract text from PDF and parse the script
text = extract_text_from_pdf(pdf_path)
parse_script(text, output_path)
