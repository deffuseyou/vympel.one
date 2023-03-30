import os
import sqlite3
from sqlighter import SQLighter

db = SQLighter(database='vympel.one',
               user='postgres',
               password=os.environ['admin_password'],
               host='192.168.0.100',
               port=5432)
path = r'z:\музыка'

songs = next(os.walk(path), (None, None, []))[2]


for song in songs:
    try:
        db.add_song(song.replace('.mp3', ''))
        print(f'Песня "{song.replace(".mp3", "")}" добавлена')
    except sqlite3.IntegrityError:
        pass
