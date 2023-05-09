import psycopg2


class SQLighter:
    def __init__(self, database, user, password, host, port):
        self.connection = psycopg2.connect(database=database,
                                           user=user,
                                           password=password,
                                           host=host,
                                           port=port)
        self.cursor = self.connection.cursor()

    def client_exist(self, ip_address):
        with self.connection:
            self.cursor.execute('SELECT ip_address FROM client WHERE ip_address = %s', (ip_address,))
            return bool(len(self.cursor.fetchall()))

    def squad_song_exist(self, title, squad):
        with self.connection:
            self.cursor.execute('SELECT * FROM squad_rating WHERE song = %s AND squad = %s', (title, squad))
            return bool(len(self.cursor.fetchall()))

    def add_message_to_rubka(self, content, datetime):
        with self.connection:
            self.cursor.execute("INSERT INTO message_to_rubka (content, datetime) VALUES(%s, %s)", (content, datetime))

    def add_song_to_squad(self, song, squad):
        with self.connection:
            self.cursor.execute("INSERT INTO squad_rating (song, squad) VALUES(%s,%s)", (song, squad))

    def add_song(self, title):
        with self.connection:
            self.cursor.execute("INSERT INTO music_library (song) VALUES(%s)", (title,))

    def add_address(self, ip_address):
        with self.connection:
            self.cursor.execute("INSERT INTO client (ip_address) VALUES(%s)", (ip_address,))

    def add_uploaded_photo(self, path, url):
        with self.connection:
            self.cursor.execute("INSERT INTO uploaded_photo (path, url) VALUES(%s, %s)", (path, url))

    def get_uploaded_photo(self):
        with self.connection:
            self.cursor.execute("SELECT path FROM uploaded_photo")
            return self.cursor.fetchall()

    def get_songs(self):
        with self.connection:
            self.cursor.execute("SELECT song FROM music_library ORDER BY song")
            return self.cursor.fetchall()

    def get_songs_top(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM music_library WHERE weight > 0 ORDER BY weight")
            return self.cursor.fetchall()

    def get_squad_rating(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM squad_rating ORDER BY squad, weight DESC")
            return self.cursor.fetchall()

    def is_votable(self, ip_address):
        with self.connection:
            self.cursor.execute("SELECT is_voteable FROM client WHERE ip_address = %s", (ip_address,))
            return self.cursor.fetchone()[0]

    def increase_song_wight(self, title):
        with self.connection:
            return self.cursor.execute("UPDATE music_library SET weight = weight + 1 WHERE song = %s", (title,))

    def increase_squad_song_wight(self, title, squad):
        with self.connection:
            return self.cursor.execute("UPDATE squad_rating SET weight = weight + 1 WHERE song = %s AND "
                                       "squad = %s", (title, squad))

    def set_vote_status(self, ip_address, status):
        with self.connection:
            return self.cursor.execute("UPDATE client SET is_voteable = %s WHERE ip_address = %s", (status, ip_address))

    def get_balance(self, ):
        with self.connection:
            self.cursor.execute("SELECT balance FROM wallet ORDER BY squad")
            return self.cursor.fetchall()

    def update_balance(self, squad, value):
        with self.connection:
            return self.cursor.execute("UPDATE wallet SET balance = balance + %s WHERE squad = %s", (value, squad))

    def reset(self, ):
        with self.connection:
            return self.cursor.execute("UPDATE client SET is_voteable = %s", (True,))
