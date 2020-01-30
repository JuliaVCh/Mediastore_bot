# Telegram bot storing photos and voice messages 

This is a repository for telegram bot functionality (without server).

Programming language: Python 3.

Tested OS compatibility: Windows 10.

## Functionality

Functionality includes following features:

* Voice messages are converted to ..wav with frequency 16kHz then stored to MySQL DB as user_id —> [audio_message_0, ..., audio_message_N].

* Photo messages are run through MTCNN to detected faces and if result is positive image is saved.

Uses as submodule an efficient pretrained PyTorch implementation of MTCNN for face detection from Tim Esler's [facenet-pytorch](https://github.com/timesler/facenet-pytorch) repo.

## Guideline to make a working bot

1. Clone this repo with its submodule:
    ```bash
    git clone --recurse-submodules https://github.com/JuliaVCh/Mediastore_bot
    ```

2. Make sure that you have required python packages. Site-packages additional to Anaconda distribution are listed in *requirements.txt*. Install them using command
    ```cmd
    conda install --file requirements.txt
    ```

3. Look into **main.py** in section config and change it if needed. Filenames and paths described in following steps are from current configuration.

4. Create new Telegram bot and save its token in root cataloge of repo as *secret_bot_credentials.txt*

5. Create *MySQL DB* with name *'audio_storage_db'* and save its credentials as *'user_name, password'* in *db_credentials.txt* in root cataloge of repo.

5. Start bot
    ```cmd
    python main.py
    ```
