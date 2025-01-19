import re
from PyPDF2 import PdfReader
import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

def clean_text(line):
    """Remove unwanted characters and normalize text."""
    return re.sub(r"[^a-zA-Z0-9.,?!\s'-]", "", line).strip()

def is_scene_heading(line):
    """Identify scene headings dynamically."""
    # Matches "INT." / "EXT." or similar headings
    return bool(re.match(r"^(INT|EXT|SCENE|LOCATION|SETTING)[ .]", line, re.IGNORECASE))

def is_character_name(line):
    """Identify character names (e.g., isolated names with no punctuation)."""
    return line.isupper() and len(line.split()) <= 3

def extract_script_info(pdf_path):
    reader = PdfReader(pdf_path)
    dialogues = []
    current_location = "Unknown"
    skip_next = False

    for page in reader.pages:
        text = page.extract_text()
        lines = text.split("\n")

        for i, line in enumerate(lines):
            line = clean_text(line)
            if not line:
                continue  # Skip empty lines

            # Check for scene heading
            if is_scene_heading(line):
                current_location = line
                continue

            # Check for character dialogue
            if is_character_name(line):
                # Look at the next line for dialogue
                if i + 1 < len(lines):
                    next_line = clean_text(lines[i + 1])
                    if next_line:
                        dialogues.append(f"[{line}] {next_line} [{current_location}]")
                        skip_next = True
                        continue

            # Skip lines immediately following captured dialogues
            if skip_next:
                skip_next = False
                continue

    return dialogues

def save_to_txt(output_path, dialogues):
    with open(output_path, "w") as f:
        for dialogue in dialogues:
            f.write(dialogue + "\n")

# Usage Example
pdf_path = "./scripts/fargo.pdf"
output_path = "./temp_outputs/cleaned_script_output.txt"
dialogues = extract_script_info(pdf_path)
save_to_txt(output_path, dialogues)