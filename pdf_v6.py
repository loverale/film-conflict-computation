import re
from PyPDF2 import PdfReader
import spacy


def clean_line(line):
    """
    Clean the text by removing random symbols, extra spaces, and invalid characters.
    """
    line = re.sub(r'[^a-zA-Z0-9.,!?\'"()\-\s:]', '', line)
    line = re.sub(r'\s+', ' ', line).strip()
    return line


def classify_line(line, nlp_model, previous_classification=None):
    """
    Classify the line as either a location, character, dialogue, or description using heuristics and NLP.
    """
    # Predefined patterns
    location_regex = r'^(INT\.|EXT\.).+$'
    character_regex = r'^[A-Z][A-Z ()\'\-]{2,}$'
    
    # Check for location
    if re.match(location_regex, line):
        return "location"
    
    # Check for character name
    if re.match(character_regex, line):
        return "character"
    
    # Use NLP to differentiate dialogue from description
    doc = nlp_model(line)
    if len(doc) > 0:
        # Dialogue typically starts with pronouns, proper nouns, or verbs
        if doc[0].pos_ in {"PRON", "PROPN", "VERB"} or '"' in line:
            return "dialogue"
    
    # If previous classification was "character", this could be a continuation of the character's dialogue
    if previous_classification == "character":
        return "dialogue"
    
    # If none of the above, classify as description
    return "description"


def merge_continued_lines(filtered_lines):
    """
    Merge lines with (CONT'D) or (cont'd) into the previous dialogue.
    """
    merged_lines = []
    for line in filtered_lines:
        if "(CONT'D)" in line or "(cont'd)" in line:
            if merged_lines:
                # Merge with the last line
                merged_lines[-1] = f"{merged_lines[-1]} {line}"
        else:
            merged_lines.append(line)
    return merged_lines


def extract_script_content_with_advanced_handling(pdf_path, output_path):
    """
    Extract character names, dialogue, and locations from a screenplay PDF
    while handling special cases like (CONT'D), two-column dialogues, and misclassified scene descriptions.
    """
    reader = PdfReader(pdf_path)
    nlp = spacy.load("en_core_web_sm")
    filtered_lines = []
    
    current_location = None
    current_character = None
    previous_classification = None

    for page in reader.pages:
        lines = page.extract_text().split("\n")
        for line in lines:
            line = clean_line(line)
            if not line:
                continue
            
            # Classify the line
            classification = classify_line(line, nlp, previous_classification)
            previous_classification = classification
            
            if classification == "location":
                current_location = line
            elif classification == "character":
                current_character = line
            elif classification == "dialogue" and current_character and current_location:
                filtered_lines.append(f"[{current_character}] {line} [{current_location}]")
    
    # Merge continued lines
    filtered_lines = merge_continued_lines(filtered_lines)

    # Save to output file
    with open(output_path, "w") as output_file:
        output_file.write("\n".join(filtered_lines))
    print(f"Enhanced script content saved to {output_path}")


# Paths for input PDF and output .txt file
pdf_path = "./scripts/knives.pdf"  # Replace with your PDF file path
output_path = "./temp_outputs/advanced_output_script.txt"  # Desired output file name

# Execute the script
extract_script_content_with_advanced_handling(pdf_path, output_path)