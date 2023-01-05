import sqlite3


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def mac_exist(self, mac):
        with self.connection:
            return bool(len(self.cursor.execute('SELECT * FROM mac WHERE `mac_address` = ?', (mac,)).fetchall()))

    def squad_song_exist(self, title, squad):
        with self.connection:
            return bool(len(self.cursor.execute('SELECT * FROM squad_rating WHERE `song` = ? AND `squad` = ?',
                                                (title, squad)).fetchall()))

    def add_message(self, data):
        with self.connection:
            self.cursor.execute("INSERT INTO `message` (`data`) VALUES(?)", (data,))

    def add_song_to_squad(self, song, squad):
        with self.connection:
            self.cursor.execute("INSERT INTO `squad_rating` (`song`, `squad`) VALUES(?,?)", (song, squad))

    def add_song(self, title):
        with self.connection:
            self.cursor.execute("INSERT INTO `song` (`title`) VALUES(?)", (title,))

    def add_addresses(self, mac, ip):
        with self.connection:
            self.cursor.execute("INSERT INTO `mac` (`mac_address`, `ip_address`) VALUES(?,?)", (mac, ip))

    def get_songs(self):
        with self.connection:
            return self.cursor.execute("SELECT `title` FROM `song` ORDER BY `title`").fetchall()

    def get_songs_top(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `song` WHERE `weight` > 0 ORDER BY `weight`").fetchall()

    def get_squad_rating(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `squad_rating` ORDER BY `squad`").fetchall()

    def is_votable(self, mac):
        with self.connection:
            mac_list = self.cursor.execute("SELECT * FROM `mac` WHERE `mac_address` = ?", (mac,)).fetchall()
            if len(mac_list) != 0:
                return mac_list[0][1]
            return True

    def increase_song_wight(self, title):
        with self.connection:
            return self.cursor.execute("UPDATE `song` SET `weight` = `weight` + 1 WHERE `title` = ?", (title,))

    def increase_squad_song_wight(self, title, squad):
        def increase_squad_song_wight(self, title, squad):
            with self.connection:
                return self.cursor.execute("UPDATE `squad_rating` SET `weight` = `weight` + 1 WHERE `song` = ? AND "
                                           "`squad` = ?", (title, squad))

    def set_vote_status(self, mac, status):
        with self.connection:
            return self.cursor.execute("UPDATE `mac` SET `available` = ? WHERE `mac_address` = ?", (status, mac))

    def reset(self, ):
        with self.connection:
            return self.cursor.execute("UPDATE `mac` SET `available` = ?", (True,))
