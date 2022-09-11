from flask import render_template
from sqlighter import SQLighter
from flask import Flask, request, redirect
import arp
import telegram
import os
import requests

db = SQLighter('database.db')
app = Flask(__name__)
token = os.environ['vm_bot_token']
bot = telegram.Bot(token=token)


@app.route('/', methods=['GET', 'POST'])
def index():
    ip = request.remote_addr
    try:
        mac = arp.get_mac_by_ip(ip)
        if not db.mac_exist(mac):
            db.add_addresses(mac, ip)
        if len(request.args) != 0:
            for text in dict(request.args).values():
                db.add_message(text)
                bot.send_message(518325236, text)
            return redirect(request.path, code=302)
        if request.method == 'POST':
            form = list(dict(request.form.lists()).values())
            if db.is_voteable(mac):
                db.set_vote_status(mac, False)
                if form[-1][0] == '1' or form[-1][0] == '2' or form[-1][0] == '3' or form[-1][0] == '4':
                    squad = int(form[-1][0])
                    for song in form[0]:
                        print(song, type(song))
                        if song == '1' or song == '2' or song == '3' or song == '4':
                            return render_template('index.html')
                        if db.squad_song_exist(song, squad):
                            db.increase_squad_song_wight(song, squad)
                        else:
                            db.add_song_to_squad(song, squad)
                        db.increase_song_wight(song)
                else:
                    for song in form[0]:
                        db.increase_song_wight(song)
            return redirect(request.path, code=302)
        return render_template('index.html', data=db.get_songs(), is_voteable=db.is_voteable(mac))

    except requests.exceptions.InvalidHeader:
        print('неудачная аутентификация')


@app.errorhandler(404)
def not_found_error(e):
    return render_template('404.html'), 404


@app.route('/squad-rating', methods=['GET'])
def squad_rating():
    sq1 = []
    sq2 = []
    sq3 = []
    sq4 = []
    for i in db.get_squad_rating():
        if i[1] == 1:
            sq1.append(f'({i[2]}) {i[0]}')
        if i[1] == 2:
            sq2.append(f'({i[2]}) {i[0]}')
        if i[1] == 3:
            sq3.append(f'({i[2]}) {i[0]}')
        if i[1] == 4:
            sq4.append(f'({i[2]}) {i[0]}')

    return render_template('squad_rating.html', sq1=sq1, sq2=sq2, sq3=sq3, sq4=sq4)


@app.route('/song-rating', methods=['GET'])
def song_rating():
    chart = []
    for j in db.get_songs_top()[::-1]:
        chart.append(f'({j[1]}) {j[0]}')

    return render_template('song_rating.html', chart=chart)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
