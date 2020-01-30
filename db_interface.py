# -*- coding: utf-8 -*-
import mysql.connector as connector
from contextlib import contextmanager
import os
"""
MySQL DB - Python interface for DB that stores Telegram voice messages as
user_id —> [audio_message_0, audio_message_1, ..., audio_message_N].
"""

class DB_connection:
    def __init__(self, db, user, password, host='localhost', charset='utf8mb4'):
        self.connection = connector.connect(host=host, user=user, password=password,\
                                            database=db, charset=charset)
        
        self.create_tables()
        
    @contextmanager
    def cursor(self, commit: bool = False):
        """
        A context manager style of using a DB cursor for database operations. 
        This function should be used for any database queries or operations that 
        need to be done. 

        :param commit:
        A boolean value that says whether to commit any database changes to the database. Defaults to False.
        :type commit: bool
        """
        cursor = self.connection.cursor()
        try:
            yield cursor
        except connector.Error as err:
            print("DatabaseError {} ".format(err))
            self.connection.rollback()
            raise err
        else:
            if commit:
                self.connection.commit()
        finally:
            cursor.close()
        
    def create_tables(self):
        sql_query = """
        create table if not exists `telegram_users` (
            `user_id` int not null,
            primary key(`user_id`))
        engine = InnoDB
        """
        with self.cursor() as cursor:
            cursor.execute(sql_query)
       
        sql_query = """
        create table if not exists `audiolibrary` (
            `id` int not null auto_increment,            
            `user_id` int not null,
            `audio_file` mediumblob not null,
            primary key(`id`),
            index `fk_audiolibrary_user_idx` (`user_id`),
            constraint `fk_audiolibrary_user`
                foreign key (`user_id`)
                references `telegram_users` (`user_id`)
                on delete no action
                on update no action)
        engine = InnoDB
        """
        
        with self.cursor(commit = True) as cursor:
            cursor.execute(sql_query)
        
    def store_audio(self, user_id, filename):
        data = self.read_file(filename)
        
        sql_query = "insert ignore into telegram_users (`user_id`) values (%s)"
        with self.cursor() as cursor:
            cursor.execute(sql_query, (user_id,))
        
        sql_query = """
        insert into
            audiolibrary (`user_id`, `audio_file`)
        values (
            %s,
            %s
        )
        """       
        with self.cursor(commit = True) as cursor:
            args = (int(user_id), data)
            cursor.execute(sql_query, args)
            os.remove(filename)
    
    def read_file(self, filename):
        with open(filename, 'rb') as f:
            audio = f.read()
        
        return audio
