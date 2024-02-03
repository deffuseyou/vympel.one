import datetime
import locale
import logging
import threading
from datetime import *
from threading import Thread, Event
from sqlighter import SQLighter
import paho.mqtt.client as mqtt
import psycopg2
import requests
import telegram
from flask import Flask, request, redirect, send_from_directory, jsonify
from flask import render_template, send_file
from flask_images import Images
from flask_socketio import SocketIO
from rsc_py import RSCPy
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data_processing import *

last_message_time = 0
locale.setlocale(locale.LC_TIME, 'ru')

__author__ = 'deffuseyou'

# TODO: обновить README


logging.basicConfig(handlers=[logging.StreamHandler(),
                              logging.FileHandler('vympel.one.log')],
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

db = SQLighter(database=config_read()['db']['database'],
               user=config_read()['db']['user'],
               password=os.environ['ADMIN_PASSWORD'],
               host=config_read()['db']['host'],
               port=config_read()['db']['port'])

import pygame

# Инициализация pygame
pygame.init()

# Загрузка звукового файла
sound_file = "bip.mp3"
pygame.mixer.music.load(sound_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False

images = Images(app)

token = os.environ['TG_BOT_TOKEN']
bot = telegram.Bot(token=token)

socketio = SocketIO(app, async_mode=None)
thread = Thread()
thread_stop_event = Event()
mqtt_broker = "localhost"
mqtt_topic = "buttons"

import time


# Создаем middleware для установки request.remote_addr на основе X-Real-IP
class XRealIPMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        real_ip = environ.get('HTTP_X_REAL_IP')
        if real_ip:
            environ['REMOTE_ADDR'] = real_ip
        return self.app(environ, start_response)


app.wsgi_app = XRealIPMiddleware(app.wsgi_app)


def on_connect(client, userdata, flags, rc):
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    global last_message_time
    current_time = time.time()  # Получаем текущее время в секундах
    message = msg.payload.decode("utf-8")
    if message == '1':
        # Координаты щелчка
        x = 30
        y = 300

        # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
        pyautogui.moveTo(x, y)
        pyautogui.click()

        # Нажимаем правый Ctrl
        pyautogui.keyDown('up')
        pyautogui.keyUp('up')

    if message == '2':
        # Координаты щелчка
        x = 900
        y = 300

        # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
        pyautogui.moveTo(x, y)
        pyautogui.click()

        # Нажимаем правый Ctrl
        pyautogui.keyDown('down')
        pyautogui.keyUp('down')

    if message == '3':
        # Координаты щелчка
        x = 300
        y = 750

        # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
        pyautogui.moveTo(x, y)
        pyautogui.click()

        # Нажимаем правый Ctrl
        pyautogui.keyDown('left')
        pyautogui.keyUp('left')

    if message == '4':
        # Координаты щелчка
        x = 900
        y = 750

        # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
        pyautogui.moveTo(x, y)
        pyautogui.click()

        # Нажимаем правый Ctrl
        pyautogui.keyDown('right')
        pyautogui.keyUp('right')
    # Проверяем разницу между текущим временем и временем последнего сообщения

    if current_time - last_message_time >= 5:
        if message in '12':
            # pygame.mixer.music.play()
            last_message_time = current_time
            if message == '1':
                socketio.emit('mqtt_message', {'message': 'девочки'}, namespace='/updater')
            if message == '2':
                socketio.emit('mqtt_message', {'message': 'мальчики'}, namespace='/updater')
        else:
            last_message_time = current_time
            socketio.emit('mqtt_message', {'message': message}, namespace='/updater')


mqtt_client = mqtt.Client()
username = "server"
password = "pusdes69"
mqtt_client.username_pw_set(username, password)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, 1883, 60)
@app.route('/send_songs', methods=['POST'])
def send_songs():
    data = request.json
    songs = data['songs']
    # Обработайте данные о песнях здесь. Например, сохраните их в базу данных.
    print(request.json)  # Пример вывода в консоль для проверки
    return jsonify({'status': True, 'message': 'Песни успешно получены'})

@app.context_processor
def inject_os():
    return {'os': os}


def perform_action(action, path=None):
    controller = RSCPy('192.180.0.18', protocol='TCP')

    if action == "run-presentation":
        if path:
            path = config_read()[f'presentation-path'] + '/' + path
            path = path.replace('/', '\\')
            controller.run_presentation(path)

    elif action == "next-slide":
        controller.next_slide()

    elif action == "prev-slide":
        controller.prev_slide()

    elif action == "stop-presentation":
        if path:
            path = config_read()[f'presentation-path'] + '/' + path
            path = path.replace('/', '\\')
            controller.stop_presentation(path)

    response_data = {"success": True}
    return jsonify(response_data)


@app.route("/run-presentation", methods=["POST"])
def run_presentation():
    path = request.get_json().get("path")
    return perform_action("run-presentation", path)


@app.route("/next-slide", methods=["POST"])
def next_slide():
    return perform_action("next-slide")


@app.route("/prev-slide", methods=["POST"])
def prev_slide():
    return perform_action("prev-slide")


@app.route("/stop-presentation", methods=["POST"])
def stop_presentation():
    path = request.get_json().get("path")
    return perform_action("stop-presentation", path)


@app.route('/', methods=['GET', 'POST'])
def index():
    ip = request.remote_addr
    print(ip)
    if ip != '127.0.0.1':
        try:
            logger.info(f'[{ip}] открыл главную страницу')
            if not db.client_exist(ip):
                logger.info(f'[{ip}] добавлен в базу')
                db.add_address(ip)

            # считываем сообщение
            if len(request.args) != 0:
                name = dict(request.args)['name']
                message = dict(request.args)['message']

                if len(name) != 0:
                    db.add_message(f'{name}: {message}', datetime.now(tz=timezone(timedelta(hours=3), name='МСК')))
                    logger.info(f'[{ip} ({name})] отправил сообщение {message}')

                    # проверяем подключение к интернету и отправляет оповещение в тг
                    if is_connected():
                        keyboard = [[InlineKeyboardButton("транслировать", callback_data='transmit_massage')]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        for telegram_id in config_read()['admin-telegram-id']:
                            bot.send_message(telegram_id, f'Сообщение от {name}:\n{message}', reply_markup=reply_markup)
                        logger.info(f'[{ip} ({name})] сообщение в тг отправлено ')
                    else:
                        logger.info(
                            f'[{ip} ({name})] сообщение в тг не отправлено, отсутствует подключение к интернету')
                else:
                    db.add_message(message, datetime.now(tz=timezone(timedelta(hours=3),
                                                                     name='МСК')))
                    if 'message' in dict(request.args):
                        logger.info(f'[{ip}] отправил сообщение {message}')

                    # проверяем подключение к интернету и отправляет оповещение в тг
                    if is_connected():
                        keyboard = [[InlineKeyboardButton("транслировать", callback_data='transmit_massage')]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        for telegram_id in config_read()['admin-telegram-id']:
                            bot.send_message(telegram_id, f'Сообщение:\n{message}', reply_markup=reply_markup)
                        logger.info(f'[{ip}] сообщение в тг отправлено ')
                    else:
                        logger.info(f'[{ip}] сообщение в тг не отправлено, отсутствует подключение к интернету')

                return redirect(request.path, code=302)

            # обрабатываем отправленные песни
            if request.method == 'POST' and db.is_votable(ip):
                form = dict(request.form.lists())
                if 'song' in form:
                    songs = form['song']
                    if 'squad' in form:
                        squad = form['squad'][0]
                    else:
                        squad = '5'

                    if ip not in config_read()['admin-ip']:
                        db.set_vote_status(ip, False)

                    if squad in '1234':
                        for song in songs:
                            print(song, squad)
                            if db.squad_song_exist(song, squad):
                                db.increase_squad_song_wight(song, squad)
                            else:
                                db.add_song_to_squad(song, squad)
                            db.increase_song_wight(song)
                        logger.info(f'[{ip}] проголосовал как отрядник')
                    else:
                        for song in songs:
                            db.increase_song_wight(song)
                        logger.info(f'[{ip}] проголосовал как работник')

                    return redirect(request.path, code=302)
            return render_template('index.html', data=db.get_songs(), is_voteable=db.is_votable(ip),
                                   is_ph=ip in config_read()['ph-ip'],
                                   is_admin=ip in config_read()['admin-ip'],
                                   disco_date=closest_disco_date(config_read()['disco-dates']))
        except requests.exceptions.InvalidHeader:
            logger.error('неудачная аутентификация')
    logger.info('сервер использовал localhost подключение')
    return redirect('http://' + config_read()['host'])


@app.route('/aa')
def aa():
    # Путь к папке с фотографиями
    photo_path = r'z:\фото\2022\2 поток\день 03 (тропа доверия)'

    # Список файлов в папке
    files = os.listdir(photo_path)

    # Фильтрация только файлов изображений (можете добавить другие расширения файлов по вашему выбору)
    image_files = [file for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # Создание списка эскизов
    thumbnails = []
    for file in image_files:
        image_path = os.path.join(photo_path, file)
        with Image.open(image_path) as image:
            image.thumbnail((200, 200))

            # Создание папки 'thumbnails', если она не существует
            thumbnail_dir = os.path.join('thumbnails')
            if not os.path.exists(thumbnail_dir):
                os.makedirs(thumbnail_dir)

            thumbnail_path = os.path.join(thumbnail_dir, file)
            image.save(thumbnail_path)
            thumbnails.append(thumbnail_path)

    return render_template('aa.html', thumbnails=thumbnails)


@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    if request.remote_addr in config_read()['admin-ip'] or request.remote_addr in config_read()['ph-ip']:
        threading.Thread(target=photo_uploader).start()
        # threading.Thread(target=zip_photo).start()
        return 'success'
    return 'error'


@app.route('/reset-buttons', methods=['POST'])
def reset_buttons():
    if request.remote_addr in config_read()['admin-ip']:
        mqtt_client.publish('buttons/wait', '0')
        mqtt_client.publish('buttons', 'ожидание...')
        return 'success'
    return 'error'


@app.route('/chime', methods=['POST'])
def chime():
    if request.remote_addr in config_read()['admin-ip']:
        mqtt_client.publish('chime', '1')
        return 'success'
    return 'error'


@app.route('/ml', methods=['POST'])
def ml():
    if request.remote_addr in config_read()['admin-ip']:
        mqtt_client.publish("buttons/squad", "ml")
        return 'success'
    return 'error'


@app.route('/st', methods=['POST'])
def st():
    if request.remote_addr in config_read()['admin-ip']:
        mqtt_client.publish("buttons/squad", "st")
        return 'success'
    return 'error'


@app.route('/reset-vote', methods=['POST'])
def reset_vote():
    if request.remote_addr in config_read()['admin-ip']:
        db.reset()
        return 'success'
    return 'error'


@app.route('/add-songs', methods=['POST'])
def add_songs():
    if request.remote_addr in config_read()['admin-ip']:
        path = fr'{config_read()["music-path"]}'
        songs = next(os.walk(path), (None, None, []))[2]

        for song in songs:
            try:
                db.add_song(song.replace('.mp3', ''))
                print(f'Песня "{song.replace(".mp3", "")}" добавлена')
            except psycopg2.errors.UniqueViolation:
                print(f'Песня "{song.replace(".mp3", "")}" уже добавлена')

        return 'success'
    return 'error'


@app.route('/balance-editor', methods=['GET', 'POST'])
def balance_editor():
    ip = request.remote_addr

    if request.method == 'POST':
        squads = list(set(transform_tuple(request.form.getlist('squad'))))

        try:
            amount = int(request.form['amount'])
        except ValueError:
            amount = 0

        print(squads, amount)
        db.update_balances(squads, amount)

    if ip in config_read()['admin-ip']:
        return render_template('balance_editor.html')
    return redirect('http://' + config_read()['host'])


@app.route('/karaoke', methods=['GET', 'POST'])
def karaoke():
    if request.method == 'POST':
        download_and_play_karaoke(request.form['query'])
    return render_template('karaoke.html')


@app.route('/internet', methods=['GET', 'POST'])
def internet():
    if request.method == 'POST':
        password = request.form['password']
        if password == os.environ['INTERNET_ACCESS_PASSWORD']:
            give_internet_access(request.remote_addr)
            return redirect('https://vk.com/dol_vympel')
        else:
            return redirect('/')
    return render_template('internet.html')


@app.route('/send-files')
def send_files():
    return redirect('http://' + config_read()['snapdrop-host'] + ':81')


@app.route('/wallet')
def wallet():
    return render_template('wallet.html')

@app.route('/qw')
def ddddd():
    return render_template('fds.html')


@app.route('/speech')
def speech():
    return render_template('speech.html')


@app.route('/library')
def library():
    chart = []
    for i in db.get_songs():
        chart.append(i[0])
    return render_template('library.html', chart=chart)


@app.route('/music/<path:filename>')
def get_music(filename):
    return send_from_directory(config_read()['music-path'], filename)


@app.route('/wallet/5-old')
def wallet_5_old():
    return render_template('buttons.html')


@app.route('/wallet/')
def wallet_slash():
    return redirect('http://' + config_read()['host'] + '/wallet')


@app.route('/wallet/<squad>')
def personal_wallet(squad):
    if squad in '12345':
        return render_template('squad_wallet.html',
                               squad=squad,
                               name=config_read()['squads'][f'squad_{squad}']['name'],
                               logo=config_read()['squads'][f'squad_{squad}']['logo'],
                               slogan=config_read()['squads'][f'squad_{squad}']['slogan'],
                               registration_date=config_read()['squads'][f'squad_{squad}']['registration-date'],
                               squad_size=config_read()['squads'][f'squad_{squad}']['squad-size'],
                               balance=config_read()['squads'][f'squad_{squad}']['balance'])
    else:
        return render_template('404.html'), 404


@app.route('/squad-rating', methods=['GET'])
def squad_rating():
    squad_dict = {1: [], 2: [], 3: [], 4: []}

    for squad in db.get_squad_rating():
        squad_dict[squad[1]].append([squad[2], squad[0]])

    return render_template('squad_rating.html',
                           sq1=squad_dict[1],
                           sq2=squad_dict[2],
                           sq3=squad_dict[3],
                           sq4=squad_dict[4])


import json


@app.route('/post', methods=['POST'])
def main():
    ## Создаем ответ
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    ## Заполняем необходимую информацию
    handle_dialog(response, request.json)
    return json.dumps(response)


def handle_dialog(res, req):
    if req['request']['original_utterance']:
        # Проверяем, есть ли содержимое
        res['response']['text'] = req['request']['original_utterance']
        res['response'][
            'tts'] = '<speaker audio="dialogs-upload/3cad9f02-98b5-4605-bfe9-eac4783d0994/e47a15b9-36c8-40ae-856c-a55819cd139b.opus">'
    else:
        from datetime import datetime, time

        current_time = datetime.now().time()
        print(current_time)

        if time(7, 0) <= current_time <= time(13, 0):
            res['response']['text'] = ''
            res['response'][
                'tts'] = '<speaker audio="dialogs-upload/3cad9f02-98b5-4605-bfe9-eac4783d0994/ef3b6c63-a5d1-4342-9b20-379c8b779755.opus">'
        elif time(13, 0) <= current_time <= time(15, 0):
            res['response']['text'] = ''
            res['response'][
                'tts'] = '<speaker audio="dialogs-upload/3cad9f02-98b5-4605-bfe9-eac4783d0994/dfa62415-861c-4354-8a36-ddbc1d1dd30b.opus">'
        elif time(15, 0) <= current_time <= time(20, 0):
            res['response']['text'] = ''
            res['response'][
                'tts'] = '<speaker audio="dialogs-upload/3cad9f02-98b5-4605-bfe9-eac4783d0994/de4ef247-0094-4926-8931-37a1a9d44c84.opus">'
        elif time(20, 0) <= current_time <= time(3, 0):
            res['response']['text'] = ''
            res['response'][
                'tts'] = '<speaker audio="dialogs-upload/3cad9f02-98b5-4605-bfe9-eac4783d0994/fb558ffc-e429-45a7-b7ff-ec9b10c068cf.opus">'
        else:
            res['response']['text'] = ''


@app.route('/song-rating', methods=['GET'])
def song_rating():
    return render_template('song_rating.html', chart=[[song, rating] for rating, song in reversed(db.get_songs_top())])


@app.route('/download-photo')
def download_photo():
    path = config_read()[f'archives-path']
    if not os.path.exists(path):
        os.makedirs(path)
    return render_template('download_photo.html',
                           folders=[f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))],
                           files=[f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))],
                           dir='', )


@app.route('/download-photo/<path:path>')
def sub_download_photo(path):
    new_path = config_read()[f'archives-path'] + '/' + path
    if os.path.isdir(new_path):
        return render_template('download_photo.html',
                               folders=[f for f in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, f))],
                               files=[f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))],
                               dir=path)
    elif os.path.isfile(new_path):
        return send_file(os.path.join(new_path), as_attachment=True, download_name='')
    else:
        return render_template('404.html'), 404


@app.route('/clicker')
def clicker():
    path = config_read()[f'presentation-path']
    if not os.path.exists(path):
        os.makedirs(path)
    return render_template('clicker.html',
                           folders=[f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))],
                           files=[f for f in os.listdir(path) if
                                  os.path.isfile(os.path.join(path, f)) and f.endswith('ppt') or f.endswith(
                                      'pptx')],
                           dir='', )


@app.route('/clicker/<path:path>')
def sub_clicker(path):
    new_path = config_read()[f'presentation-path'] + '/' + path
    if os.path.isdir(new_path):
        return render_template('clicker.html',
                               folders=[f for f in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, f))],
                               files=[f for f in os.listdir(new_path) if
                                      os.path.isfile(os.path.join(new_path, f)) and f.endswith('ppt') or f.endswith(
                                          'pptx')],
                               dir=path)
    elif os.path.isfile(new_path):
        return send_file(os.path.join(new_path), as_attachment=True, download_name='')
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
def disconnect():
    pass


@app.errorhandler(404)
def not_found_error(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    mqtt_client.loop_start()
    socketio.run(app, host='0.0.0.0', port=80)
