import assemblyai as aai # assemblyai
from pydub import AudioSegment # breaks apart film file
import math # math
import os  # easier to make / write / store files onto pc
from api import api_key # api key privacy

# generally unused anymore, since claude wasn't accurate
import json # parses claudes json response
import assemblyai.types # limits claudes response
import re # claude regex parsing

# check out tool in visual studio code cursor

# api key 
aai.settings.api_key = api_key

# global vars to keep consistent bt functions
chunk_count = 1
actual_file = True
start_time = 0
end_time = 0
first_run = True # lazy of me
warmup = True

def split_audio(audio_path, movie_name, length=300000):

    #grab file
    audio = AudioSegment.from_file(audio_path)
    audio_length_ms = len(audio)

    # initialize chunks
    chunks = []
    num_chunks = math.ceil(audio_length_ms/length)

    for i in range(num_chunks):
        print(f"    Creating Chunk #: {i+1}")
        global start_time, end_time
        start_time = i * length
        end_time = min((i + 1) * length, audio_length_ms)
        chunk = audio[start_time:end_time]
        chunk_new_file = f"./split_movies/{movie_name}/{movie_name}_{i+1}.flac"
        chunk.export(chunk_new_file, format="flac")
        chunks.append({
            "filename": chunk_new_file,
            "start_time_ms": start_time,
            "end_time_ms": end_time
        })

    return chunks

def transcribe_chunk(chunk_file):
    # warmup sequence
    global warmup
    if(warmup):
        config = aai.TranscriptionConfig(speaker_labels=True)
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(
            chunk_file,
            config=config
        )
        warmup = False
        return transcript

    global chunk_count
    print(f"\nTranscribing/Diarizing Chunk #: {chunk_count}")

    config = aai.TranscriptionConfig(speaker_labels=True)
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(
        chunk_file['filename'],
        config=config
    )

    with open(f"./raw_transcriptions/raw_transcription_{chunk_count}.txt", 'w') as f:
        for utterance in transcript.utterances:
            global start_time, end_time # i think isn't needed anymore
            chunk_start = chunk_file['start_time_ms']/1000
            #chunk_end = chunk_file['end_time_ms']/1000
            start_time_transcript = utterance.start/1000
            end_time_transcript = utterance.end/1000
            #start_time_transcript = sentence.start / 1000
            #end_time_transcript = sentence.end / 1000
            calc_start = "%.2f" % (chunk_start + start_time_transcript) # round to two decimal
            calc_end = "%.2f" % (chunk_start + end_time_transcript)

            f.write(f"{calc_start} - {calc_end}: Speaker {utterance.speaker}: {utterance.text}\n")
            #f.write(f"{calc_start} - {calc_end}: Speaker {sentence.speaker}: {sentence.text}\n")


    chunk_count += 1
    return transcript

def fixing_claude(response):

    json_start_index = response.find('{')

    if json_start_index != -1:

        # Trim the response from the first '{' to the end
        response = response[json_start_index:]

        trimmed_response = response.replace("\\n", "")
        trimmed_response = trimmed_response.replace("'", "") # bandaid solution, random ' at end of claude response

    else:
        print("     should never see me")
        trimmed_response = "ERROR"

    return trimmed_response

def claude_replacement(transcript, film_script):
    print("Summoning Claude")

    with open(film_script, 'r') as f:
        temp_script = f.read()

    # first attempt
    # prompt = (f"""After my request, I've pasted a new script for reference.
    #               I would like you to ONLY respond in JSON format, meaning no introductory comments, just the raw output from your response.
    #               I would like you to take the transcription created, and provide a list with text replacements using the provided script.
    #               The transcription will include lines such as Speaker A, Speaker B, etc., for 10 total speakers (up to Speaker J).
    #               Please reference the script, and provide a JSON file that has replacements for speaker to character name.
    #               If you are unsure of a given line, please just list UNSURE for the specific speaker, as the transcription won't be 100% accurate.
    #               If there are no speakers detected (as this request is repeated across segments), please just still list out the JSON format, and list NO SPEAKER for each speaker letter.
    #               The JSON file doesn't need to be readable to humans, so don't focus on formatting and just provide a collapsed JSON structure.
    #               \n{temp_script}""")

    prompt = (f"""I would like you to ONLY respond in JSON format, meaning no introductory comments, just the raw output from your response.
                  I would like you to take the transcription created, and provide a list with text replacements using the provided text that I have pasted below. 
                  The transcription will include lines such as Speaker A, Speaker B, etc., for 10 total speakers (up to Speaker J).
                  Please reference the script, and provide a JSON file that has replacements for speaker to character name.
                  These characters normally have their own line.
                  If you are unsure of a sentence, please just list UNSURE for the specific speaker, as the transcription won't be 100% accurate.
                  The JSON file doesn't need to be readable to humans, so don't focus on formatting and just provide a collapsed JSON structure. 
                  \n{temp_script}""")

    # for blank files, throws error, we are just ignoring them and pushing forward
    global actual_file, chunk_count
    try:
        result = transcript.lemur.task(prompt, final_model=aai.LemurModel.claude3_5_sonnet)

        # claude doesn't listen to my benevolent wisdom
        with open(f"./temp_claude/temp_{chunk_count-1}.txt", 'w') as f:
            f.write(f"{result}\n")
        actual_file = True # isn't needed

    except assemblyai.types.LemurError as e:
        print(f"    Error Bypass (Bad Practice): {e}")
        actual_file = False # still isn't needed anymore

    # herding claude is like herding a large swarm of cats
    if(actual_file):
        with open(f"./temp_claude/temp_{chunk_count-1}.txt", 'r') as f:
            claude_bribe = f.read()
            trimmed_result = fixing_claude(claude_bribe)

        # wildly inefficient
        with open(f"./claude_suggestions/claude_suggestion_{chunk_count-1}.json", 'w+') as f:
            f.write(f"{trimmed_result}\n")

    # os.remove(f"./temp_claude/temp_{chunk_count-1}.txt")

def master_transcription():
    print("Taking Claudes Infinite Wisdom and Replacing/Appending")

    # to stop from master_transcript bleeding into other attempts
    global first_run
    if(first_run):
        first_run = False
        print("    deleting og master file")
        open('master_transcription.txt', 'w').close()

    global actual_file
    if(actual_file):
        with open(f"./claude_suggestions/claude_suggestion_{chunk_count-1}.json", 'r') as f:
            claude_text = json.load(f)

        ## NEW PLAN -- GO WITH MAKING MULTIPLE FILES, RATHER THAN 1 PIPELINE

        with open(f"./raw_transcriptions/raw_transcription_{chunk_count-1}.txt", 'r') as f:
            master_temp = f.read()

        for key, value in claude_text.items():
            # IF KEY EXISTS IN FILE
            if(key in master_temp):
                master_temp = master_temp.replace(key, value)
                # print(f"    replaced {key} with {value}")

        with open('master_transcription.txt', 'a') as f:
            f.write(f"{master_temp}")
    else:
        print("    Skipping Empty File")

    os.remove(f"./temp_claude/temp_{chunk_count-1}.txt")
    os.remove(f"./claude_suggestions/claude_suggestion_{chunk_count-1}.json")
    os.remove(f"./raw_transcriptions/raw_transcription_{chunk_count-1}.txt")

def warmup_sequence():
    transcript = transcribe_chunk("./warmup.flac")

def gpt4o_replacement(transcript):
    print("placeholder")

def single_transcription(audio_path, file_path):
    print("Starting Full Transcription")
    config = aai.TranscriptionConfig(speaker_labels=True)
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(
        audio_path,
        config=config
    )

    print("Writing to .txt File")
    with open(file_path, 'w') as f:
        for utterance in transcript.utterances:
            start_time_transcript = utterance.start/1000
            end_time_transcript = utterance.end/1000
            f.write(f"{start_time_transcript} - {end_time_transcript}: Speaker {utterance.speaker}: {utterance.text}\n")

def iterative_process_audio(audio_path, film_script, movie_name):
    print("Starting Audio Processing")
    chunks = split_audio(audio_path, movie_name)

    #### PRE-NEW PLAN
    # global warmup
    # if(warmup):
    #     print("     Warming up diarization")
    #     warmup_sequence() # hopefully to avoid speaker diarization issues for actual content
    #     #throwaway = transcribe_chunk("./warmup.flac")
    #
    for chunk_filename in chunks:
        transcript = transcribe_chunk(chunk_filename)
        # claude_replacement(transcript, film_script)
        # master_transcription()

        os.remove(chunk_filename['filename']) # this is probably for the best -> removes chunk after use

## Start of Code to run everything ##

#iterative_process_audio('./knives.flac', 'script_conversion.txt', "knives")
#single_transcription("./movies/knives.flac", "./output/knives.txt")
print("compile testing")



