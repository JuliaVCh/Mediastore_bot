# -*- coding: utf-8 -*-
import requests
from urllib.error import HTTPError

class BotHandler:
    """
    Telegram bot handler able to receive incoming updates using long polling 
    """
    def __init__(self, token, logfile):
        self.token = token
        self.api_url = f'https://api.telegram.org/bot{token}/'
        self.file_download_url = f'https://api.telegram.org/file/bot{self.token}/'
        self.logs = logfile

    def get_updates(self, offset=None, timeout=30,\
                    update_types=['message', 'channel_post']):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset, 'allowed_updates': update_types}
        try:
            resp = requests.get(self.api_url + method, params)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Error while getting updates occurred: {err}')

        result_json = resp.json()['result']
        
        return result_json
    
    def get_file(self, file_id):
        method = 'getFile'
        params = {'file_id': file_id}
        file = None
        try:
            resp = requests.get(self.api_url + method, params)
            
            if not self.logs is None:
                self.logs.write('Succesfully recieved File object ')
            
            fileinfo = resp.json()['result']
            file_path = fileinfo.get('file_path', 0)
            
            if not self.logs is None:
                self.logs.write(f'with following file path: {file_path}\n')
            
            if file_path:
                file = requests.get(self.file_download_url + file_path, stream=True).content
                
                if not self.logs is None:
                    self.logs.write(f"File succesfully downloaded, its size is {fileinfo.get('file_size', 0)} B.\n")
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Error while downloading file occurred: {err}')
        
        return file
