import re
from PyPDF2 import PdfReader

# Extract raw text from PDF
def extract_text(pdf_path):
    print("Extracting Text from PDF")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Write raw text to file for debugging
    with open("./temp_outputs/temp.txt", 'w') as f:
        f.write(text)

    return text

def please_parse_the_script(text):
    rx = r"^\s*\b([A-Z]+)\b\s*\n(.*(?:\n.+)*)"
    #print( re.findall(rx, text, re.M) )

    dialogues = re.findall(rx, text, re.M)
    output_file = "./output/knives.txt"
    with open(output_file, "w") as file:
        for dialogue in dialogues:
            file.write(f"{dialogue}\n")

script_text = extract_text("./scripts/knives.pdf")
please_parse_the_script(script_text)