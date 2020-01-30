# -*- coding: utf-8 -*-
import os.path
import json
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
#---------------------config begin---------------------
with open('secret_bot_credentials.txt','r') as token:
    bot_token = token.read()
output_location = './temp/audioconverter_output/'
photos_location = './photos/'
offset_file_name = './offset.json'
log_location = './temp/'
db_name = 'audio_storage_db'
with open('db_credentials.txt','r') as db_credentials:
    db_cred = db_credentials.read()
    [db_user, db_password] = db_cred.split(', ')
debug = False
#----------------------config end----------------------

if not os.path.exists(output_location):
    os.makedirs(output_location)

if not os.path.exists(photos_location):
    os.makedirs(photos_location)

if debug:
    logs = open(os.path.join(log_location, 'log.txt'), "w")
    logs.write('-----Telegram Bot log-----\n')
else:
    logs = None

collectioner_bot = BotHandler(bot_token, logs)
db_connection = DB_connection(db_name, db_user, db_password)
db_connection.create_tables()
fd_net = Facenet(logs)

new_offset = None
if os.path.exists(offset_file_name):
    with open(offset_file_name, "r") as offset_file:
        new_offset = json.load(offset_file)

def main():
    global new_offset
    
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
            
            if debug:
                logs.write('Got new message ')
            
            # checking for types of interest               
            voice_message = message.get('voice', 0)
            photo_message = message.get('photo', 0)
            
            user = message.get('from', 0)
 
            if user:
                user_id = user['id']
                if debug:
                    logs.write(f'from user with id {user_id}.\n')
            else:
                user_id = ''
            
            if voice_message:
                if debug:
                    logs.write('Message appears to be a voice audiofile.\n')
                # if user id cannot be identified DB is not updated       
                if not user:
                    continue
                
                raw_audiofile = collectioner_bot.get_file(voice_message['file_id'])
                if not raw_audiofile is None:
                    # converting audio
                    file_name = f"{message['message_id']}_voice"
                    file_path = os.path.join(output_location, file_name + '.wav')
                    audio_converter(raw_audiofile, file_path)
                    
                    if debug:
                        logs.write('Audiofile succesfully converted.\n')
                    
                    # send converted audio to DB    
                    db_connection.store_audio(user_id, file_path)
                    if debug:
                        logs.write('Audiofile succesfully stored in DB.\n')
                
            elif photo_message:
                if debug:
                    logs.write('Message appears to be an image.\n')
                
                max_size_img = max([photo for photo in photo_message\
                                    if photo.get('file_size', 0) != 0],\
                                   key = lambda p: p['file_size'])
                img_file = collectioner_bot.get_file(max_size_img['file_id'])
                
                if not img_file is None:
                    img_sizes = max_size_img['width'], max_size_img['height']
                    face, prob = fd_net.detect_face(img_file, img_sizes)
                    
                    if debug:
                        logs.write(f"Facenet reports that face is present with probability {round(prob * 100, 5)}% therefore face presence considered to be {face}.\n")
                    
                    if face:
                        file_name = f"{user_id}_{message['message_id']}.jpg"
                        file_path = os.path.join(photos_location, file_name)
                        with open(file_path, 'wb') as mediafile:
                            mediafile.write(img_file)
                            
                            if debug:
                                logs.write('Photo is saved.\n')                        
            else:
                continue
            
            if debug:
                logs.write('#---------next message----------\n')
                logs.flush()

if __name__ == '__main__':  
    try:
        main()
    except Exception as err:
        print("Error occured: {} ".format(err))
    finally:
        db_connection.connection.close()
        
        if debug:
            logs.write('DB connection closed.\n')
            logs.close()
        
        with open(offset_file_name, 'w') as offset_file:
            json.dump(new_offset, offset_file)
