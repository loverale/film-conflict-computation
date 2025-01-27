import re
import json
from fuzzywuzzy import fuzz
import csv

def parse_subtitles(file_path):
    subtitles = []
    with open(file_path, 'r') as file:
        current_sub = {"start_time": "", "end_time": "", "text": ""}
        for line in file:
            if re.match(r'^\d+$', line):  # Skip indices
                continue
            line = line.strip()
            # If the line matches the timecode pattern
            if re.match(r'\d{2}:\d{2}:\d{2}[.,]\d{3} --> \d{2}:\d{2}:\d{2}[.,]\d{3}', line):
                times = line.split(" --> ")
                if current_sub["text"]:  # Save the current subtitle before starting a new one
                    subtitles.append(current_sub)
                    current_sub = {"start_time": "", "end_time": "", "text": ""}
                current_sub["start_time"] = times[0]
                current_sub["end_time"] = times[1]
            elif line == "":  # Empty line signals the end of a subtitle block
                if current_sub["text"]:  # Save the completed subtitle
                    subtitles.append(current_sub)
                    current_sub = {"start_time": "", "end_time": "", "text": ""}
            else:
                current_sub["text"] += f"{line} "  # Accumulate text, maintaining whitespace

        if current_sub["text"]:  # Add the last subtitle
            subtitles.append(current_sub)

    # Validate subtitles
    for sub in subtitles:
        if not sub["start_time"] or not sub["end_time"]:
            print(f"DEBUG: Invalid Subtitle Found: {sub}")
            #sub["start_time"] = "00:00:00,000"  # Fallback start time
            #sub["end_time"] = "00:00:01,000"    # Fallback end time

    return subtitles

def match_subtitles_to_json(subtitles, json_file_path, output_tsv_path, threshold=20, length_match_cutoff=0.9,
                            length_buffer=1.1):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    matches = []
    for entry in json_data:
        character = entry.get("character", "Unknown")
        dialogue = entry.get("text", "").strip()
        setting = entry.get("scene", "Unknown")

        clean_dialogue = re.sub(r'[^\w\s]', '', dialogue.lower())  # Clean dialogue text
        dialogue_length = len(clean_dialogue)

        # Skip processing if the dialogue is empty
        if dialogue_length == 0:
            #print(f"Skipping entry with empty dialogue for character: {character}")
            #print("")
            continue

        merged_text = ""
        start_time = None  # Initialize start_time
        end_time = None
        found_match = False

        # Step through the subtitles
        for idx in range(len(subtitles)):
            sub = subtitles[idx]
            subtitle_text = re.sub(r'[^\w\s]', '', sub["text"].lower())  # Clean subtitle text

            # Capture start_time only for the first subtitle in the group
            if start_time is None and sub.get("start_time"):
                start_time = sub["start_time"]

            # Update end_time for each subtitle merged
            if sub.get("end_time"):
                end_time = sub["end_time"]
            #else:
                #print(f"DEBUG: Missing End Time for Subtitle: {sub}")
                #print("")

            merged_text += subtitle_text

            # Check match progress
            score = fuzz.ratio(merged_text.strip(), clean_dialogue.strip())
            match_length_ratio = len(merged_text.strip()) / dialogue_length  # Progress tracking

            #print(f"DEBUG: Start Time = {start_time}, End Time = {end_time}, Score = {score}, Match Length Ratio = {match_length_ratio:.2f}, Merged Text = {merged_text.strip()}")

            # Allow further merging if match improves or length cutoff isn't exceeded
            if score >= threshold and match_length_ratio >= length_match_cutoff:
                found_match = True
            elif len(merged_text.strip()) > dialogue_length * length_buffer:  # Exceeded reasonable length
                break

            # Continue extending the match if the next subtitle contributes to the dialogue
            if found_match and idx + 1 < len(subtitles):
                next_sub = subtitles[idx + 1]
                next_text = re.sub(r'[^\w\s]', '', next_sub["text"].lower())
                extended_text = merged_text + next_text
                extended_score = fuzz.ratio(extended_text.strip(), clean_dialogue.strip())
                if extended_score > score:  # If including the next subtitle improves the match
                    merged_text = extended_text
                    end_time = next_sub.get("end_time", end_time)  # Safely update end_time
                    #print(f"DEBUG: Extended Match with Next Subtitle: Extended Score = {extended_score}, End Time = {end_time}")
                    continue
                else:
                    break  # Stop merging if the next subtitle doesn't improve the match

        # If a match is found, add it to the results
        if found_match:
            if not end_time:  # Fallback for missing end_time
                end_time = start_time
            matches.append({
                "start_time": start_time,  # Use the captured start_time
                "end_time": end_time,
                "character": character,
                "text": dialogue,
                "scene": setting,
                "score": score
            })
            # Remove used subtitles up to the current index
            subtitles = subtitles[idx + 1:]

    # Write results to a TSV file
    with open(output_tsv_path, "w", newline="", encoding="utf-8") as tsvfile:
        writer = csv.writer(tsvfile, delimiter="\t")
        # Write header row
        writer.writerow(["Start", "End", "Character", "Dialogue", "Scene"])
        # Write matches
        for match in matches:
            writer.writerow(
                [match["start_time"], match["end_time"], match["character"], match["text"], match["scene"]])

    print(f"Output written to {output_tsv_path}")

subtitles_file = './truman_subtitles.txt'
json_file = './truman_full.json'
final_output = './trauman_output.tsv'

# Parse subtitles
subtitles = parse_subtitles(subtitles_file)

# Match subtitles to JSON dialogues
match_subtitles_to_json(subtitles, json_file, final_output)