from app import *
import psycopg2

path = fr'{config_read()["music-path"]}'
songs = next(os.walk(path), (None, None, []))[2]

for song in songs:
    try:
        db.add_song(song.replace('.mp3', ''))
        print(f'Песня "{song.replace(".mp3", "")}" добавлена')
    except psycopg2.errors.UniqueViolation:
        print(f'Песня "{song.replace(".mp3", "")}" уже добавлена')
