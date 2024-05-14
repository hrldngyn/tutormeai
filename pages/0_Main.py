import streamlit as st
import ffmpeg
import requests
from google.cloud import firestore
from google.oauth2 import service_account
import json
import subprocess
import re

# key_dict = json.loads(st.secrets["textkey"])
# creds = service_account.Credentials.from_service_account_info(key_dict)
# db = firestore.Client(credentials=creds, project="tutormeai")

# # Create a reference to the Google post.
# doc_ref = db.collection("users").document("Harold")

# # Then get the data at that reference.
# doc = doc_ref.get()

# # Let's see what we got!
# st.write("The id is: ", doc.id)
# st.write("The contents are: ", doc.to_dict())

# def download_file(url):
#     #local_filename = url.split('/')[-1]
#     local_filename = "test.mp4"
#     # NOTE the stream=True parameter below
#     with requests.get(url, stream=True) as r:
#         r.raise_for_status()
#         with open(local_filename, 'wb') as f:
#             for chunk in r.iter_content(chunk_size=8192): 
#                 f.write(chunk)
#     return local_filename

#https://d2y36twrtb17ty.cloudfront.net/sessions/f5a0f0c6-f822-40bb-9505-b101011dac3e/3ed66eff-754c-4772-8a0c-b101011dac47-d599fc22-9b27-494b-9ca7-b10101227e35.hls/master.m3u8?InvocationID=d7be0d9f-a80c-ef11-8291-12c206d2fd2b&tid=00000000-0000-0000-0000-000000000000&StreamID=6000a32c-5051-4235-9a29-b101011dad9f&ServerName=uscpharmacyschool.hosted.panopto.com

def convert_m3u8_to_mp4(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, c='copy').run()
    )


def trim_silence(input_file, output_file):
    silence_start_re = re.compile(r' silence_start: (?P<start>[0-9]+(\.?[0-9]*))')
    silence_end_re = re.compile(r' silence_end: (?P<end>[0-9]+(\.?[0-9]*)) ')
    total_duration_re = re.compile(
        r'size=[^ ]+ time=(?P<hours>[0-9]{2}):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9\.]{5}) bitrate=')

    print("trimming")
    # Run ffmpeg command with silencedetect filter and pipe stdout
    process = subprocess.Popen(['ffmpeg', '-i', input_file, '-af', 'silencedetect=noise=-30dB:d=0.5', '-f', 'null', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Capture stdout and stderr
    stdout, stderr = process.communicate()
    stderr

    # Decode and split stdout
    stderr_lines = stderr.decode().split('\n')
    st.write(len(stderr_lines))
    # Extract non-silence chunks
    chunk_starts = []
    chunk_ends = []
    for line in stderr_lines:
        silence_start_match = silence_start_re.search(line)
        silence_end_match = silence_end_re.search(line)
        total_duration_match = total_duration_re.search(line)
        if silence_start_match:
            chunk_ends.append(float(silence_start_match.group('start')))
            if len(chunk_starts) == 0:
                # Started with non-silence.
                chunk_starts.append(0.)
        elif silence_end_match:
            chunk_starts.append(float(silence_end_match.group('end')))
        elif total_duration_match:
            hours = int(total_duration_match.group('hours'))
            minutes = int(total_duration_match.group('minutes'))
            seconds = float(total_duration_match.group('seconds'))
            end_time = hours * 3600 + minutes * 60 + seconds

    if len(chunk_starts) == 0:
        # No silence found.
        chunk_starts.append(0)

    if len(chunk_starts) > len(chunk_ends):
        # Finished with non-silence.
        chunk_ends.append(end_time or 10000000.)

    chunk_times = list(zip(chunk_starts, chunk_ends))
    st.write("Chunk Starts: " + str(len(chunk_starts)))
    st.write("Chunk Ends: " + str(len(chunk_ends)))
    st.write("Chunk list length: " + str(len(chunk_times)))

    chunk_times
    inputs = []
    for s, e in chunk_times:
        inputs.append(ffmpeg.input(input_file).trim(start=s, end=e))
        st.write("Appended to inputs")
    inputs
    # Concatenate segments to keep and output
    st.write("Concatenating")
    concat = ffmpeg.concat(*inputs[:100])
    st.write("Done Concatenating")
    output = ffmpeg.output(concat, output_file, c='copy')
    ffmpeg.run(output)
    st.write("Ran output")


    # # Generate trim command based on silence timestamps
    # trim_cmd = ''
    # if silence_timestamps:
    #     trim_cmd += '-i ' + input_file
    #     for start, end in silence_timestamps:
    #         trim_cmd += f' -ss {start} -to {end}'
    #     trim_cmd += ' -c copy ' + output_file
    # else:
    #     trim_cmd = f'ffmpeg -i {input_file} -c copy {output_file}'

    # # Execute the trim command
    # subprocess.run(trim_cmd, shell=True)

    # # Check for errors in stderr
    # if stderr:
    #     print("Errors:", stderr.decode())


video_url = st.text_input(label="Enter a video link to download")



if(video_url):
    video_response = requests.get(video_url)
    video_response.headers
    convert_m3u8_to_mp4(video_url, "test2ffmpeg.mp4")
    trim_silence("test2ffmpeg.mp4", "trimmed2.mp4")


st.sidebar.header("Main")
