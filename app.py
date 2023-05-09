from flask_socketio import SocketIO
from flask import Flask, render_template, send_file, request, redirect
from threading import Thread, Event
import telegram
import requests
import logging
from data_processing import *
from datetime import *

__author__ = 'deffuseyou'

# TODO: cделать нормальную страницу отряда
# TODO: обновить README
# TODO: добавить иконки и title


logging.basicConfig(handlers=[logging.StreamHandler(),
                              logging.FileHandler('vympel.one.log')],
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

db = SQLighter(database='vympel.one',
               user='postgres',
               password=os.environ['admin_password'],
               host='192.168.0.100',
               port=5432)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

token = os.environ['vm_bot_token']
bot = telegram.Bot(token=token)

socketio = SocketIO(app, async_mode=None)
thread = Thread()
thread_stop_event = Event()


@app.context_processor
def inject_os():
    return {'os': os}


@app.route('/', methods=['GET', 'POST'])
def index():
    ip = request.remote_addr
    if ip != '127.0.0.1':
        try:
            logger.info(f'[{ip}] открыл главную страницу')
            if not db.client_exist(ip):
                logger.info(f'[{ip}] добавлен в базу')
                db.add_address(ip)

            # считываем сообщение
            if len(request.args) != 0:
                for text in dict(request.args).values():
                    db.add_message_to_rubka(text, datetime.now(tz=timezone(timedelta(hours=3), name='МСК')))
                    logger.info(f'[{ip}] отправил сообщение {text}')

                    # проверяем подключение к интернету и отправляет оповещение в тг
                    if is_connected():
                        for telegram_id in config_read()['admin-telegram-id']:
                            bot.send_message(telegram_id, f'{text}')
                        logger.info(f'[{ip}] сообщение в тг отправлено ')
                    else:
                        logger.info(f'[{ip}] сообщение в тг не отправлено, отсутствует подключение к интернету')

                return redirect(request.path, code=302)

            # обрабатываем отправленные песни
            if request.method == 'POST' and db.is_votable(ip):
                form = list(dict(request.form.lists()).values())
                squad = form[-1][0]
                songs = form[0]

                if ip not in config_read()['admin-ip']:
                    db.set_vote_status(ip, False)

                if squad in '1234':
                    for song in songs:
                        if db.squad_song_exist(song, squad):
                            db.increase_squad_song_wight(song, squad)
                        else:
                            db.add_song_to_squad(song, squad)
                        db.increase_song_wight(song)
                        logger.info(f'[{ip}] проголосовал как отрядник')
                else:
                    for song in form[0]:
                        db.increase_song_wight(song)
                        logger.info(f'[{ip}] проголосовал как работник')

                return redirect(request.path, code=302)
            return render_template('index.html', data=db.get_songs(), is_voteable=db.is_votable(ip))
        except requests.exceptions.InvalidHeader:
            logger.error('неудачная аутентификация')
    logger.info('сервер использовал localhost подключение')
    return 'использование localhost или 127.0.0.1 не допускается'


@app.route('/internet', methods=['GET', 'POST'])
def internet():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'qwerty':
            # add_ip(request.remote_addr)
            return redirect('https://vk.com/dol_vympel')
        else:
            return redirect('/')
    return render_template('internet.html')


@app.route('/send-files')
def send_files():
    return redirect('http://192.168.0.100:81')


@app.route('/wallet')
def wallet():
    return render_template('wallet.html')


@app.route('/wallet/')
def wallet_slash():
    return render_template('wallet_slash.html')


@app.route('/wallet/<squad>')
def personal_wallet(squad):
    if squad in '12345':
        page = f'balance_{squad}_squad.html'
        return render_template(page)
    else:
        return render_template('404.html'), 404


@app.route('/squad-rating', methods=['GET'])
def squad_rating():
    squads_rating = db.get_squad_rating()
    return render_template('squad_rating.html',
                           sq1=[[i[2], i[0]] for i in squads_rating if i[1] == 1],
                           sq2=[[i[2], i[0]] for i in squads_rating if i[1] == 2],
                           sq3=[[i[2], i[0]] for i in squads_rating if i[1] == 3],
                           sq4=[[i[2], i[0]] for i in squads_rating if i[1] == 4])


@app.route('/song-rating', methods=['GET'])
def song_rating():
    chart = []
    for i in db.get_songs_top()[::-1]:
        chart.append([i[1], i[0]])
    return render_template('song_rating.html', chart=chart)


@app.route('/files')
def files():
    path = config_read()['files-path']
    return render_template('files.html',
                           folders=[f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))],
                           files=[f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))],
                           dir='', )


@app.route('/files/<path:path>')
def sub_files(path):
    new_path = config_read()['files-path'] + path
    if os.path.isdir(new_path):
        return render_template('files.html',
                               folders=[f for f in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, f))],
                               files=[f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))],
                               dir=path)
    elif os.path.isfile(new_path):
        return send_file(os.path.join(new_path), as_attachment=True)
    else:
        return render_template('404.html'), 404


def content_update():
    while not thread_stop_event.is_set():
        socketio.emit('update', {'balance': db.get_balance()}, namespace='/updater')
        socketio.sleep(1)


@socketio.on('connect', namespace='/updater')
def test_connect():
    global thread
    if not thread.is_alive():
        thread = socketio.start_background_task(content_update)


@socketio.on('disconnect', namespace='/updater')
def test_disconnect():
    pass


@app.errorhandler(404)
def not_found_error(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=80)
