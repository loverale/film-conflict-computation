from PyPDF2 import PdfReader

import re  # Import the regex module at the top of the script

def extract_script_info(pdf_path, output_path):
    print("Parsing the Script File for Salient Info")
    reader = PdfReader(pdf_path)
    dialogues = []
    current_location = None

    for page in reader.pages:
        text = page.extract_text()
        lines = text.split("\n")
        skip_next = False

        for i, line in enumerate(lines):
            # Detect and update location (INT./EXT.)
            if line.startswith("INT.") or line.startswith("EXT."):
                current_location = line.strip()

            # Ignore page numbers or blank lines
            if line.isdigit() or not line.strip():
                continue

            # Capture character name followed by dialogue
            if line.isupper() and not skip_next:
                # Avoid false positives for scene descriptions
                if i + 1 < len(lines) and lines[i + 1].strip():
                    dialogue = lines[i + 1].strip()
                    if not dialogue.isupper():  # Check next line isn't scene description
                        # Remove text within parentheses using regex
                        dialogue = re.sub(r"\(.*?\)", "", dialogue).strip()
                        dialogues.append(f"[{line.strip()}] {dialogue} [{current_location}]")
                        skip_next = True
            else:
                skip_next = False

# def extract_script_info(pdf_path, output_path):
#     reader = PdfReader(pdf_path)
#     dialogues = []
#     current_location = None

#     for page in reader.pages:
#         text = page.extract_text()
#         lines = text.split("\n")
#         skip_next = False

#         for i, line in enumerate(lines):
#             # Detect and update location (INT./EXT.)
#             if line.startswith("INT.") or line.startswith("EXT."):
#                 current_location = line.strip()

#             # Ignore page numbers or blank lines
#             if line.isdigit() or not line.strip():
#                 continue

#             # Capture character name followed by dialogue
#             if line.isupper() and not skip_next:
#                 # Avoid false positives for scene descriptions
#                 if i + 1 < len(lines) and lines[i + 1].strip():
#                     dialogue = lines[i + 1].strip()
#                     if not dialogue.isupper():  # Check next line isn't scene description
#                         dialogues.append(f"[{line.strip()}] {dialogue} [{current_location}]")
#                         skip_next = True
#             else:
#                 skip_next = False

    with open(output_path, "w") as f:
        for dialogue in dialogues:
            f.write(dialogue + "\n")
