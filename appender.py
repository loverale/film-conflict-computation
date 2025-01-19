"""
Append timestamps from the timestamp file to the corresponding lines in the script file.

:param timestamp_file: Path to the file containing timestamps.
:param script_file: Path to the script file.
:param output_file: Path to the output file with timestamps appended.
"""
def append_timestamps_to_script(timestamp_file, script_file, output_file):
    print("Appending Files Together")

    with open(timestamp_file, 'r') as ts_file:
        timestamps = ts_file.readlines()

    with open(script_file, 'r') as script_file:
        script_lines = script_file.readlines()

    # parse timestamps and their corresponding text
    parsed_timestamps = []
    for line in timestamps:
        if line.strip():
            try:
                time_range, text = line.split(': ', 1)
                parsed_timestamps.append((time_range.strip(), text.strip()))
            except ValueError:
                continue

    # Prepare output with appended timestamps
    output_lines = []
    for idx, script_line in enumerate(script_lines):
        if idx < len(parsed_timestamps):
            time_range, _ = parsed_timestamps[idx]
            output_lines.append(f"[{time_range}] {script_line.strip()}\n")
        else:
            output_lines.append(script_line)

    # Write output to file
    with open(output_file, 'w') as out_file:
        out_file.writelines(output_lines)
