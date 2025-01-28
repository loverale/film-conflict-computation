import json
import csv
from fuzzywuzzy import fuzz
from api import *

# Load JSON file
def load_json(json_file_path):
    with open(json_file_path, 'r') as file:
        return json.load(file)

# Load subtitle file
def load_subtitles(sub_file_path):
    subtitles = []
    with open(sub_file_path, 'r') as file:
        for line in file:
            subtitle = eval(line.strip())  # Convert string representation of dict to dict
            subtitles.append(subtitle)
    return subtitles

# Match subtitle text to JSON dialogue using fuzzy matching
def match_subtitles_to_json(subtitles, json_data, threshold=80):
    matched_data = []
    seen_dialogues = set()  # To track unique dialogues

    imworking = 0
    for subtitle in subtitles:
        print(imworking)
        imworking += 1
        best_match = None
        best_score = 0

        for entry in json_data:
            if 'dialogue' in entry:
                score = fuzz.partial_ratio(subtitle['text'], entry['dialogue'])
                if score > best_score and score >= threshold:
                    best_match = entry
                    best_score = score

        if best_match:
            dialogue = best_match['dialogue']
            if dialogue not in seen_dialogues:  # Ensure uniqueness
                seen_dialogues.add(dialogue)
                matched_data.append({
                    'start_time': subtitle['start_time'],
                    'end_time': subtitle['end_time'],
                    'character_name': best_match.get('character', 'Unknown'),
                    'dialogue': dialogue,
                    'location': best_match.get('scene', 'Unknown')
                })

    return matched_data

# Save matched data to TSV
def save_to_tsv(matched_data, output_file_path):
    with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['start_time', 'end_time', 'character_name', 'dialogue', 'location'], delimiter='\t')
        writer.writeheader()
        writer.writerows(matched_data)

# Main function
def main():
    json_file_path = fargo_json  # Replace with your JSON file path
    sub_file_path = './hidden_output/other/fargo_sub_output.txt'  # Replace with your subtitle file path
    output_file_path = './final_output/matched_output.tsv'  # Replace with desired output file path

    json_data = load_json(json_file_path)
    subtitles = load_subtitles(sub_file_path)

    matched_data = match_subtitles_to_json(subtitles, json_data)
    save_to_tsv(matched_data, output_file_path)

    print(f"Matched data saved to {output_file_path}")

if __name__ == '__main__':
    main()
