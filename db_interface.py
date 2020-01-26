# -*- coding: utf-8 -*-
import mysql.connector as connector
"""
MySQL DB - Python interface for DB that stores Telegram voice messages as
user_id —> [audio_message_0, audio_message_1, ..., audio_message_N].
"""

class DB_connection:
    def __init__(self, db, user, password, host='localhost', charset='utf8mb4'):
        self.connection = connector.connect(host=host, user=user, password=password,\
                                            db=db, charset=charset, dictionary=True)
        self.cursor = self.connection.cursor()
        self.create_tables()
        
    def create_tables(self):
        sql_script = """
        create table if not exists `telegram_users` (
            `user_id` int not null,
            primary key(`user_id`))
        engine = InnoDB;
        
        create table if not exists `audiolibrary` (
            `id` int not null auto_increment,            
            `user_id` int not null,
            `audio_file` blob not null,
            primary key(`id`),
            index `fk_audiolibrary_user_idx` (`user_id`),
            constrain `fk_audiolibrary_user`
                foreign key (`user_id`)
                references `telegram_users` (`user_id`)
                on delete no action
                on update no action)
        engine = InnoDB;
        """
        
        self.cursor.executescript(sql_script)
        self.connection.commit()
        
    def store_audio(self, user_id, filename):
        data = self.read_file(filename)
        
        sql_script = """
        insert ignore into
            telegram_users
        values
            %s;
        
        insert into
            audiolibrary (user_id, audio_file)
        values (
            %s
            %s
        );
        """
        
        args = (user_id, user_id, data)
        self.cursor.executescript(sql_script, args)
        self.connection.commit()
    
    def read_file(self, filename):
        with open(filename, 'rb') as f:
            audio = f.read()
        
        return audio
    
    def __del__(self):
        self.cursor.close()
        self.connection.close()