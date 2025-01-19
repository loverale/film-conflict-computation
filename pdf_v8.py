import fitz  # PyMuPDF

from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

import pdfplumber

import re

def pdf_to_text(pdf_file, txt_file):
    with fitz.open(pdf_file) as pdf:
        with open(txt_file, 'w', encoding='utf-8') as f:
            for page in pdf:
                f.write(page.get_text())

def image_pdf_to_text(pdf_file, txt_file):
    reader = PdfReader(pdf_file)
    with open(txt_file, 'w', encoding='utf-8') as f:
        for page_num, page in enumerate(reader.pages):
            # Extract images from the page
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject'].get_object()
                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                        data = xObject[obj].get_data()
                        img = Image.frombytes("RGB", size, data)
                        text = pytesseract.image_to_string(img)
                        f.write(text + '\n')

def pdfplumber_to_text(pdf_file, txt_file):
    with pdfplumber.open(pdf_file) as pdf:
        with open(txt_file, 'w', encoding='utf-8') as f:
            for page in pdf.pages:
                f.write(page.extract_text() + '\n')


def extract_dialogue(pdf_path):
    """Extracts dialogue from a screenplay PDF."""

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Regular expressions for dialogue extraction
    character_pattern = r"^([A-Z\s]+)\s*\n"
    dialogue_pattern = r"^\s*([^\n]+)\n"

    characters = []
    dialogues = []

    for line in text.split("\n"):
        character_match = re.match(character_pattern, line)
        if character_match:
            characters.append(character_match.group(1).strip())
        else:
            dialogue_match = re.match(dialogue_pattern, line)
            if dialogue_match:
                dialogues.append(dialogue_match.group(1).strip())

    return characters, dialogues

# Extract raw text from PDF
def pdf_vtexter(pdf_path):
    print("Extracting Text from PDF")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def pdf_v100000(text):
    character_pattern = r"^\s*\b([A-Z]+)\b\s*\n(.*(?:\n.+)*)"
    dialogue_pattern = r"^(INT\.|EXT\.)\s+(.+)"

    characters = []
    dialogues = []

    for line in text:
        character_match = re.match(character_pattern, line)
        if character_match:
            characters.append(character_match.group(1).strip())
        else:
            dialogue_match = re.match(dialogue_pattern, line)
            if dialogue_match:
                dialogues.append(dialogue_match.group(1).strip())

    with open(output, 'w+') as f:
        for character, dialogue in zip(characters, dialogues):
            f.write(f"{character}: {dialogue}\n")


path = "./scripts/knives.pdf"
output = "./output/knives.txt"

#pdf_to_text("./scripts/knives.pdf", "./output/knives.txt")
#image_pdf_to_text("./scripts/knives.pdf", "./output/knives.txt")
#pdfplumber("./scripts/knives.pdf", "./output/knives.txt")

#temp = extract_dialogue(path)
# characters, dialogues = extract_dialogue(path)

# with open(output, 'w+') as f:
#     for character, dialogue in zip(characters, dialogues):
#         f.write(f"{character}: {dialogue}\n")

text = pdf_vtexter(path)
pdf_v100000(text)