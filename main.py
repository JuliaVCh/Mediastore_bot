# -*- coding: utf-8 -*-
import os
# --------------------costom code--------------------
from bot import BotHandler
from audio_converter import audio_converter
from db_interface import DB_connection
from face_detector import Facenet

"""
Telegram Bot which functionality includes following features

1. Saves voice messages from chats to DB where stores it as
    user_id —> [audio_message_0, audio_message_1, ..., audio_message_N].
All audio files are converted to wav with frequency 16kHz.
2. Saves photo messages if face is detected on them.
"""
#--------------------config begin--------------------
with open('secret_bot_credentials.txt','r') as token:
    bot_token = token.read()
input_path = './temp/input/'
output_path = './temp/output/'
photos_path = './photos/'
db_name = 'audio_storage_db'
with open('db_credentials.txt','r') as db_credentials:
    db_cred = db_credentials.read()
    [db_user, db_password] = db_cred.spit(', ')
#---------------------config end---------------------

if not os.path.exists(input_path):
    os.mkdir(input_path)

if not os.path.exists(output_path):
    os.mkdir(output_path)

if not os.path.exists(photos_path):
    os.mkdir(photos_path)

collectioner_bot = BotHandler(bot_token)
db_connection = DB_connection(db_name, db_user, db_password)
db_connection.create_tables()
fd_net = Facenet()

def main():  
    new_offset = None

    while True:
        updates_list = collectioner_bot.get_updates(new_offset)
        
        for update in updates_list:
            if new_offset is None:
                new_offset = update['update_id'] + 1
            elif new_offset <= update['update_id']:
                new_offset = update['update_id'] + 1
            
            # checking if post contains message       
            message = update.get('message', 0)
            if not message:
                message = update.get('channel_post', 0)
            if not message:
                continue
            
            # checking for types of interest               
            voice_message = message.get('voice', 0)
            photo_message = message.get('photo', 0)
            
            user = message.get('from', 0)
 
            if user:
                user_id = user[id]
            else:
                user_id = ''
            
            if voice_message:
                # if user id cannot be identified DB is not updated       
                if not user:
                    continue
                
                raw_audiofile = collectioner_bot.get_file(voice_message['file_id'])
                if not raw_audiofile is None:
                    # converting audio
                    file_name = f"{message['message_id']}_voice"
                    audio_converter(raw_audiofile, output_path + file_name + '.wav')
                    # send converted audio to DB    
                    db_connection.store_audio(user_id, output_path + file_name + '.wav')
                
            elif photo_message:
                for idx, img in enumerate(photo_message):
                    img_file = collectioner_bot.get_file(img['file_id'])
                    if not img_file is None:
                        img_sizes = img['width'], img['height']
                        face = fd_net.detect_face(img_file, img_sizes)
                        if face:
                            file_name = f"{user_id}_{message['message_id']}_{idx}.jpg"
                            with open(photos_path + file_name, 'w') as mediafile:
                                mediafile.write(img_file)
            else:
                continue

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()