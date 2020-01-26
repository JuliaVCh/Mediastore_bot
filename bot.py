# -*- coding: utf-8 -*-
import requests
from urllib.error import HTTPError

class BotHandler:
    """
    Telegram bot handler able to receive incoming updates using long polling 
    """
    def __init__(self, token):
        self.token = token
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)

    def get_updates(self, offset=None, timeout=30,\
                    update_types=['message', 'channel_post']):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset, 'allowed_updates': update_types}
        try:
            resp = requests.get(self.api_url + method, params)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

        result_json = resp.json()['result']
        
        return result_json
    
    def get_file(self, file_id):
        method = 'getFile'
        params = {'file_id': file_id}
        file = None
        try:
            resp = requests.get(self.api_url + method, params)
            fileinfo_json = resp.json()
            file_path = fileinfo_json.get('file_path', 0)
            if file_path:
                file = requests.get(f'https://api.telegram.org/file/bot{self.token}/{file_path}')
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        
        return file
