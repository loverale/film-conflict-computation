import re
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from api import * # personal file paths
from datetime import datetime, timedelta # for fargo short dialogue


# Normalize text for comparison
def normalize_text(text):
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# ASSUMES .SRT SUBTITLE FILE TYPE
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

# assumes .srt
# fargo needs a separate one as multi-dialogue appears in file, which previous attempt doesnt handle
def fargo_parse_subtitles_with_characters(file_path):
    subtitles = []
    with open(file_path, 'r', encoding='utf-8') as file:
        current_sub = {"start_time": "", "end_time": "", "text": ""}
        for line in file:
            line = line.strip()
            # Skip blank lines
            if not line:
                if current_sub["start_time"] and current_sub["end_time"] and current_sub["text"]:
                    # Split text by "-" if multiple characters are present
                    lines = [l.strip() for l in current_sub["text"].split("-") if l.strip()]
                    for l in lines:
                        subtitles.append({
                            "start_time": current_sub["start_time"],
                            "end_time": current_sub["end_time"],
                            "text": l
                        })
                current_sub = {"start_time": "", "end_time": "", "text": ""}
                continue

            # Match timestamps
            if re.match(r'\d{2}:\d{2}:\d{2}[.,]\d{3} --> \d{2}:\d{2}:\d{2}[.,]\d{3}', line):
                times = line.split(" --> ")
                current_sub["start_time"] = times[0]
                current_sub["end_time"] = times[1]
            elif re.match(r"^\d+$", line):  # Skip index numbers
                continue
            else:
                # Accumulate subtitle text
                current_sub["text"] += f" {line}" if current_sub["text"] else line

        # Add the last subtitle if it exists
        if current_sub["start_time"] and current_sub["end_time"] and current_sub["text"]:
            lines = [l.strip() for l in current_sub["text"].split("-") if l.strip()]
            for l in lines:
                subtitles.append({
                    "start_time": current_sub["start_time"],
                    "end_time": current_sub["end_time"],
                    "text": l
                })

    return subtitles

"""
param settings:
truman show - threshold = 20, length_match_cutoff=.9, length_buffer=1.1
"""
def match_subtitles_to_json(subtitles, json_file_path, output_tsv_path, threshold=25, length_match_cutoff=1.0, length_buffer=1.0):
    
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    matches = []
    for entry in json_data:

        # skips non-dialogue for truman
        # # skipping non dialogue entries
        # if not entry.get("text", ""):
        #     continue

        # skips non-dialogue for fargo
        if not entry.get("dialogue", ""):
            continue

        character = entry.get("character", "Unknown")
        #dialogue = entry.get("text", "").strip() #truman json uses text to indicate dialogue
        dialogue = entry.get("dialogue", "").strip() # fargo uses dialogue to indicate dialogue
        setting = entry.get("scene", "Unknown")

        clean_dialogue = re.sub(r'[^\w\s]', '', dialogue.lower())  # Clean dialogue text
        #clean_dialogue = dialogue
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
            #subtitle_text = sub["text"]
            subtitle_text = re.sub(r'[^\w\s]', '', sub["text"].lower())  # Clean subtitle text
            #print(subtitle_text)
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

# Helper function to parse subtitle time into a datetime object
def parse_timecode(timecode):
    return datetime.strptime(timecode, "%H:%M:%S,%f")

def fargo_match_subtitles_to_json(subtitles, json_file_path, output_tsv_path, threshold=30, time_buffer=15):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    matches = []
    json_index = 0  # Start at the beginning of the JSON data

    for sub in subtitles:
        subtitle_text = normalize_text(sub["text"])
        subtitle_start = parse_timecode(sub["start_time"])
        subtitle_end = parse_timecode(sub["end_time"])
        found_match = False

        while json_index < len(json_data):
            entry = json_data[json_index]
            dialogue = entry.get("dialogue", "").strip()
            character = entry.get("character", "Unknown")
            setting = entry.get("scene", "Unknown")

            if not dialogue:
                # Skip entries without dialogue
                print(f"DEBUG: Skipping JSON Entry with No Dialogue: {entry}")
                json_index += 1
                continue

            clean_dialogue = normalize_text(dialogue)

            # Skip JSON entries that are too early
            if "timestamp" in entry:
                json_time = parse_timecode(entry["timestamp"])
                if json_time + timedelta(seconds=time_buffer) < subtitle_start:
                    print(f"Skipping JSON Entry Too Early: {entry}")
                    json_index += 1
                    continue

            # Stop matching if JSON entry is too late
            if "timestamp" in entry:
                json_time = parse_timecode(entry["timestamp"])
                if subtitle_end + timedelta(seconds=time_buffer) < json_time:
                    print(f"Stopping JSON Match Too Late: {entry}")
                    break

            # Fuzzy matching between subtitle and JSON dialogue
            score = fuzz.ratio(subtitle_text, clean_dialogue)
            print(f"DEBUG: Subtitle = {subtitle_text}, JSON Dialogue = {clean_dialogue}, Score = {score}")

            if score >= threshold:
                matches.append({
                    "start_time": sub["start_time"],
                    "end_time": sub["end_time"],
                    "character": character,
                    "dialogue": dialogue,
                    "scene": setting,
                    "score": score
                })
                json_index += 1  # Move to the next JSON entry after a match
                found_match = True
                break

            # If no match, increment the JSON index
            json_index += 1

        # If no match was found for this subtitle, log it
        if not found_match:
            print(f"DEBUG: No Match Found for Subtitle: {subtitle_text}")

    # Write results to a TSV file
    with open(output_tsv_path, "w", newline="", encoding="utf-8") as tsvfile:
        writer = csv.writer(tsvfile, delimiter="\t")
        writer.writerow(["Start", "End", "Character", "Line", "Scene", "Score"])
        for match in matches:
            writer.writerow([match["start_time"], match["end_time"], match["character"], match["dialogue"], match["scene"], match["score"]])

    print(f"Output written to {output_tsv_path}")


# Parse subtitles
subtitles = fargo_parse_subtitles_with_characters(fargo_subtitles)

with open("./hidden_output/other/fargo_sub_output.txt", "w") as f:
    for sub in subtitles:
        f.write(f"{sub}\n")

#print(subtitles)

# Match subtitles to JSON dialogues
fargo_match_subtitles_to_json(subtitles, fargo_json, fargo_final)