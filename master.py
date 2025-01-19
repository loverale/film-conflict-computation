from transcriber import * #this is lazy of me and a bad practice, refactor to be more explicit
from appender import *
from corrected_pdf_parser_v3 import * #todo:/ rename
from pdf_v4 import *

# this script was run on 5 movies, to save time changing the names individually for this multi-temp output solution, this is the easiest way to change what movie is ran
movie = "fargo"

# ASSEMBLY AI TRANSCRIPTION || TRANSCRIBER.PY
input_movie = "./movies/" + movie + ".flac"
transcription_output = "./temp_outputs/trans_" + movie + ".txt"
#basic_transcription(input_movie, transcription_output) #sometimes temp commented out to avoid re transcribing over and over again to save cost

# # PDF SCRIPT CONVERSION TO .TXT || CORRECTED_PDF_PARSER_V3
pdf_path = "./scripts/" + movie + ".pdf"  # Path to the uploaded PDF file
script_output = "./temp_outputs/script_" + movie + ".txt"

# pdf parsing tests v3
text = extract_text_from_pdf(pdf_path)
parse_script(text, script_output)

#pdf parsing tests v4
#extract_script_info(pdf_path, script_output)

# APPEND THE TWO || APPENDER.PY
final_output = "./output/" + movie + ".txt"
append_timestamps_to_script(transcription_output, script_output, final_output)

