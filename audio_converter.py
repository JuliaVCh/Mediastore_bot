# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
"""
Pipeline to convert Telegram voice messages data to .wav 16 kHz mono 16 bit
and save to file.
"""
def audio_converter(input_data, output_file_name):        
    pipe = Popen([ 'ffmpeg',
           '-y', # overwrite the output file if it already exists.
           "-f", 's16le', # 16bit input
           "-acodec", "pcm_s16le", # raw 16bit input
           '-ar', "16000", # the output will have 16 kHz
           '-ac', '1', # the input will have 1 channel (mono)
           '-i', '-', # the input will arrive from the pipe
           '-vn', # means "don't expect any video input"
           '-acodec', "libfdk_aac" # output audio codec
           '-b', "3000k", # output bitrate (=quality). Here, 3000kb/second
           output_file_name],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
    
    try:
        pipe.stdin.write(input_data)
    except Exception as err:
        print(f'Error occurred: {err}')
