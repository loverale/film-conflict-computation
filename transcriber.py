import assemblyai as aai # assemblyai
from api import api_key # api key privacy

aai.settings.api_key = api_key #api key 

# just a single file (base assemblyai)
def basic_transcription(audio_path, file_path):
    print("Starting Full Transcription")
    config = aai.TranscriptionConfig(speaker_labels=True, speakers_expected=10)
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(
        audio_path,
        config=config
    )

    print("Writing Transcription to .txt File")
    with open(file_path, 'w') as f:
        for utterance in transcript.utterances:
            start_time_transcript = utterance.start/1000
            end_time_transcript = utterance.end/1000
            calc_start = "%.2f" % (start_time_transcript) # round to two decimal
            calc_end = "%.2f" % (end_time_transcript)
            f.write(f"{calc_start} - {calc_end}: Speaker {utterance.speaker}: {utterance.text}\n")

basic_transcription("./movies/truman_eng.flac", "./assembly_truman.txt")
