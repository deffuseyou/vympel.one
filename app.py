import datetime
import io
import locale
import logging
import threading
from datetime import *
from threading import Thread, Event
from flask import Flask, render_template, request, redirect, url_for, flash
from playsound import playsound
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pydub import AudioSegment
from pydub.playback import play
import schedule
import sounddevice as sd
import time
import numpy as np
import os
import threading
import paho.mqtt.client as mqtt
import psycopg2
import requests
import telegram
from flask import Flask, request, redirect, send_from_directory, jsonify, make_response
from flask import render_template, send_file
from flask_socketio import SocketIO
from rsc_py import RSCPy
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from flask_httpauth import HTTPBasicAuth
from data_processing import *

update_config_key('is-uploading', False)
last_message_time = 0
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

__author__ = 'deffuseyou'

# TODO: обновить README
output_device = None  # Задайте имя устройства воспроизведения

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

# import pygame
# # Инициализация всех модулей Pygame
# pygame.init()
#
# # Инициализация модуля mixer
# pygame.mixer.init()
#
# # Теперь можно загружать и воспроизводить звуки
# sound_file = "bip.mp3"
# pygame.mixer.music.load(sound_file)
#
auth = HTTPBasicAuth()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False

# Настройка логгирования для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

token = os.environ['TG_BOT_TOKEN']
bot = telegram.Bot(token=token)

socketio = SocketIO(app)
thread = Thread()
thread_stop_event = Event()

mqtt_broker = config_read()['mqtt']['host']
mqtt_topic = config_read()['mqtt']['buttons-topic']

import time


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
        # pyautogui.moveTo(x, y)
        # pyautogui.click()
        #
        # # Нажимаем правый Ctrl
        # pyautogui.keyDown('up')
        # pyautogui.keyUp('up')

    if message == '2':
        # Координаты щелчка
        x = 900
        y = 300

        # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
        # pyautogui.moveTo(x, y)
        # pyautogui.click()
        #
        # # Нажимаем правый Ctrl
        # pyautogui.keyDown('down')
        # pyautogui.keyUp('down')

    if message == '3':
        # Координаты щелчка
        x = 300
        y = 750

        # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
        # pyautogui.moveTo(x, y)
        # pyautogui.click()
        #
        # # Нажимаем правый Ctrl
        # pyautogui.keyDown('left')
        # pyautogui.keyUp('left')

    if message == '4':
        # Координаты щелчка
        x = 900
        y = 750

        # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
        # pyautogui.moveTo(x, y)
        # pyautogui.click()
        #
        # # Нажимаем правый Ctrl
        # pyautogui.keyDown('right')
        # pyautogui.keyUp('right')
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
username = "user"
password = "1"
mqtt_client.username_pw_set(username, password)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, 1883, 60)


@auth.verify_password
def verify_password(username, password):
    return username == '5' and password == 'vympel5'


@app.route('/send_songs', methods=['POST'])
def send_songs():
    ip = request.remote_addr
    if db.is_votable(ip):
        data = request.json
        squad = data['squad']
        songs = data['songs']

        if 'songs' in data:
            if ip not in config_read()['admin-ip']:
                db.set_vote_status(ip, False)

            if squad in '12345':
                for song in songs:
                    full_song_name = f"{song['artist']} - {song['title']}"
                    if db.squad_song_exist(full_song_name, squad):
                        db.increase_squad_song_wight(full_song_name, squad)
                    else:
                        db.add_song_to_squad(full_song_name, squad)
                    db.increase_song_wight(full_song_name)
                logger.info(f'[{ip}] проголосовал')
        return jsonify({'status': True, 'message': 'твой голос учтен ✅'})
    return jsonify({'status': False, 'message': 'ты уже голосовал 😞\nтеперь ты сможешь после дискотеки'})


@app.context_processor
def inject_os():
    return {'os': os}


def perform_action(action, path=None):
    controller = RSCPy(get_local_ip(), protocol='TCP')

    if action == "run-presentation":
        if path:
            path = config_read()[f'presentation-path'].format(year=year, shift=shift) + '/' + path
            path = path.replace('/', '\\')
            controller.run_presentation(path)

    elif action == "next-slide":
        controller.next_slide()

    elif action == "prev-slide":
        controller.prev_slide()

    elif action == "stop-presentation":
        if path:
            path = config_read()[f'presentation-path'].format(year=year, shift=shift) + '/' + path
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


@app.route('/', methods=['GET'])
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
            return render_template('index.html', data=db.get_songs(), is_voteable=db.is_votable(ip),
                                   is_ph=ip in config_read()['ph-ip'],
                                   is_admin=ip in config_read()['admin-ip'],
                                   disco_date=closest_disco_date(config_read()['disco-dates']))
        except requests.exceptions.InvalidHeader:
            logger.error('неудачная аутентификация')
    logger.info('сервер использовал localhost подключение')
    return redirect('http://' + config_read()['host'])


@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    if (request.remote_addr in config_read()['admin-ip'] or request.remote_addr in config_read()['ph-ip']) and not \
            config_read()['is-uploading']:
        print(config_read()['is-uploading'])
        update_config_key('is-uploading', True)
        threading.Thread(target=photo_uploader).start()
        return 'success'
    return 'нет доступа или фото уже загружаются'


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
        return jsonify(status=True, message='запрос на chime отправлен')
    return jsonify(status=False, message='доступ запрещен')


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
        parse_music_folder()
        # path = fr'{config_read()["music-path"]}'
        # songs = next(os.walk(path), (None, None, []))[2]
        #
        # for song in songs:
        #     try:
        #         db.add_song(song.replace('.mp3', ''))
        #         print(f'Песня "{song.replace(".mp3", "")}" добавлена')
        #     except psycopg2.errors.UniqueViolation:
        #         print(f'Песня "{song.replace(".mp3", "")}" уже добавлена')

        return 'success'
    return 'error'


@auth.login_required
@app.route('/balance-editor', methods=['GET', 'POST'])
def balance_editor():
    ip = request.remote_addr
    if ip in config_read()['admin-ip']:
        if request.method == 'POST':
            squads = list(set(transform_tuple(request.form.getlist('squad'))))

            try:
                amount = int(request.form['amount'])
            except ValueError:
                amount = 0

            print(squads, amount)
            db.update_balances(squads, amount)

        return render_template('balance_editor.html')
    return redirect('http://' + config_read()['host'])


@app.route('/internet', methods=['GET', 'POST'])
def internet():
    if request.method == 'POST':
        password = request.form['password']
        login = request.form['login']
        if password == os.environ['INTERNET_ACCESS_PASSWORD']:
            if give_internet_access(login, request.remote_addr):
                return redirect('https://vk.com/dol_vympel')
            return jsonify({'message': 'IP already exist'})
        else:
            return redirect('/')
    return render_template('internet.html')


@app.route('/send-files')
def send_files():
    return redirect('http://' + config_read()['snapdrop-host'])


@app.route('/wallet')
def wallet():
    return render_template('wallet.html')


@app.route('/qw')
def ddddd():
    return render_template('test.html')


@app.route('/library')
def library():
    chart = []
    for i in db.get_songs():
        chart.append(i[0])
    return render_template('library.html', chart=chart)


@app.route('/music/<path:filename>')
def get_music(filename):
    return send_from_directory(config_read()['music-path'], filename)


@app.route('/buttons')
def buttons():
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


def read_cell_state():
    try:
        with open('cell_state.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"st": {}, "ml": {}}


def write_cell_state(data):
    with open('cell_state.json', 'w') as file:
        json.dump(data, file)


@app.route('/ayariva-st', methods=['GET'])
def ayariva_st():
    ip = request.remote_addr
    if ip in config_read()['admin-ip']:
        rows = len(config_read()['ayariva-st']['categories'])
        cols = config_read()['ayariva-st']['cols'] + 1
        categories = config_read()['ayariva-st']['categories']
        cell_state = read_cell_state()
        return render_template('ayariva.html', rows=rows, cols=cols, categories=categories, squads='st',
                               cell_state=cell_state)

    return render_template('404.html'), 404


@app.route('/ayariva-ml', methods=['GET'])
def ayariva_ml():
    ip = request.remote_addr
    if ip in config_read()['admin-ip']:
        rows = len(config_read()['ayariva-ml']['categories'])
        cols = config_read()['ayariva-ml']['cols'] + 1
        categories = config_read()['ayariva-ml']['categories']
        cell_state = read_cell_state()
        return render_template('ayariva.html', rows=rows, cols=cols, categories=categories, squads='ml',
                               cell_state=cell_state)

    return render_template('404.html'), 404


@app.route('/update_cell_state', methods=['POST'])
def update_cell_state():
    data = request.json
    row = str(data['row'])
    col = str(data['col'])
    squads = data['squads']

    cell_state = read_cell_state()
    if squads not in cell_state:
        cell_state[squads] = {}
    if row not in cell_state[squads]:
        cell_state[squads][row] = []

    if col in cell_state[squads][row]:
        cell_state[squads][row].remove(col)
    else:
        cell_state[squads][row].append(col)

    write_cell_state(cell_state)
    socketio.emit('update', {'cell_state': cell_state}, namespace='/updater')
    return jsonify({"success": True})


@app.route('/squad-rating', methods=['GET'])
def squad_rating():
    squad_dict = {1: [], 2: [], 3: [], 4: [], 5: []}

    for squad_rating_info in db.get_squad_rating():
        squad_dict[squad_rating_info[1]].append([squad_rating_info[2], squad_rating_info[0]])

    return render_template('squad_rating.html',
                           sq1=squad_dict[1],
                           sq2=squad_dict[2],
                           sq3=squad_dict[3],
                           sq4=squad_dict[4],
                           sq5=squad_dict[5])


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


@app.route('/ped', methods=['GET'])
@auth.login_required
def ped():
    return render_template('ped.html')


@app.route('/download-photo')
def download_photo():
    path = config_read()[f'archives-path'].format(year=year, shift=shift)
    logger.info(path)
    logger.info(os.path.exists(path))

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
@auth.login_required
def clicker():
    path = config_read()[f'presentation-path'].format(year=year, shift=shift)
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)
    return render_template('clicker.html',
                           folders=[f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))],
                           files=[f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
                                  and not f.startswith('~$') and (f.endswith('ppt') or f.endswith('pptx'))],
                           dir='')


@app.route('/clicker/<path:path>')
@auth.login_required
def sub_clicker(path):
    new_path = config_read()[f'presentation-path'].format(year=year, shift=shift) + '/' + path
    print(new_path)
    if os.path.isdir(new_path):
        return render_template('clicker.html',
                               folders=[f for f in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, f))],
                               files=[f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))
                                      and not f.startswith('~$') and (f.endswith('ppt') or f.endswith('pptx'))],
                               dir=path)
    elif os.path.isfile(new_path):
        return send_file(os.path.join(new_path), as_attachment=True, download_name='')
    else:
        return render_template('404.html'), 404


def content_update():
    while not thread_stop_event.is_set():
        cell_state = read_cell_state()
        socketio.emit('update', {'balance': db.get_balance(), 'cell_state': cell_state}, namespace='/updater')
        socketio.sleep(1)


@app.route('/heic-datetime', methods=['POST'])
def heic_datetime():
    print(request.files)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.lower().endswith('.heic'):
        return make_response(str(get_heic_datetime(io.BytesIO(file.read()))), 200)
    else:
        return jsonify({'error': 'Invalid file format'}), 400


@app.route('/wheel', methods=['GET'])
def wheel():
    days = config_read().get('days', {})
    today_date = datetime.today().strftime('%d.%m.%Y')

    for key, value in days.items():
        if value == today_date:
            first_digit = key.split('_')[0]
            return jsonify({'sector': first_digit})
    return jsonify({'sector': '0'})


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


folders = []
BASE_PATH = config_read()['sound-folder']


def get_folders_with_time_format(base_path=BASE_PATH):
    folders = []
    for item in os.listdir(base_path):
        folder_path = os.path.join(base_path, item)
        if os.path.isdir(folder_path) and item.isdigit() and len(item) == 4:
            folders.append(item)
    folders.sort()
    return folders


def play_music(file):
    # Загрузка аудио с помощью pydub
    audio = AudioSegment.from_file(file)

    # Конвертация аудио в numpy массив
    samples = np.array(audio.get_array_of_samples())
    samples = samples.reshape((-1, audio.channels))

    # Определение частоты дискретизации
    sample_rate = audio.frame_rate

    # Воспроизведение аудио через sounddevice
    try:
        sd.play(samples, samplerate=sample_rate, device=output_device)
        sd.wait()  # Ждем завершения воспроизведения
    except Exception as e:
        logger.error(f"Error playing {file}: {e}")


def update_folders():
    global folders
    folders = get_folders_with_time_format(BASE_PATH)
    logger.info(f"Folders updated: {folders}")


def main_loop():
    global folders
    while True:
        current_time = datetime.now().strftime("%H%M")
        if current_time in folders:
            logger.info(f"It's {current_time}. Time to play music from folder {current_time}.")
            folder_path = os.path.join(BASE_PATH, current_time)
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                     f.endswith(('.mp3', '.wav', '.flac'))]
            files.sort()
            for file in files:
                # Воспроизведение музыки
                play_music(file)
                time.sleep(1)  # Добавим небольшую задержку, чтобы не запускать все сразу
            time.sleep(60)  # Ждем минуту, чтобы избежать повторного запуска в ту же минуту
        elif datetime.now().minute == 59:
            update_folders()
            time.sleep(60)  # Ждем минуту, чтобы не обновлять несколько раз в 59 минуту
        else:
            time.sleep(1)  # Проверяем каждую секунду


def start_main_loop():
    threading.Thread(target=main_loop, daemon=True).start()


@app.route('/autosound')
def autosound():
    return render_template('autosound.html')


@app.route('/update_folders', methods=['POST'])
def update_folders_route():
    update_folders()
    return jsonify({"status": "Folders updated"}), 200


if __name__ == "__main__":
    path_monitor_thread = threading.Thread(target=path_monitor)
    path_monitor_thread.start()

    mqtt_client.loop_start()

    devices = sd.query_devices()
    for device in devices:
        print([device])
    # Установка устройства воспроизведения по его идентификатору
    output_device_name = "amplifier (Realtek(R) Audio)"  # Замените на имя вашего устройства
    output_device_id = None

    for idx, device in enumerate(devices):
        if output_device_name in device['name']:
            output_device_id = idx
            print(output_device_id)
            break

    if output_device_id is None:
        print(f"Output device '{output_device_name}' not found")
    else:
        output_device = output_device_id
        print(f"Using output device ID: {output_device}")

    folders = get_folders_with_time_format()
    start_main_loop()
    socketio.run(app, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)
