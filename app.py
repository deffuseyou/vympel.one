import locale
import logging
import threading
from datetime import *
from threading import Thread, Event
import time
import paho.mqtt.client as mqtt
import requests
import telegram
from PIL import Image
from flask import Flask, request, redirect, send_from_directory
from flask import render_template, send_file
from flask_images import Images
from flask_socketio import SocketIO
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

images = Images(app)

token = os.environ['TG_BOT_TOKEN']
bot = telegram.Bot(token=token)

socketio = SocketIO(app, async_mode=None)
thread = Thread()
thread_stop_event = Event()
mqtt_broker = "vympel.one"
mqtt_topic = "buttons"


import pyautogui
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
    if current_time - last_message_time >= 1:
        socketio.emit('mqtt_message', {'message': message}, namespace='/updater')
        last_message_time = current_time

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, 1883, 60)


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
    threading.Thread(target=photo_uploader).start()
    threading.Thread(target=zip_photo).start()
    return 'success'


@app.route('/reset-buttons', methods=['POST'])
def reset_buttons():
    mqtt_client.publish('buttons/wait', '0')
    mqtt_client.publish('buttons', 'ожидание...')
    return 'success'

@app.route('/ml', methods=['POST'])
def ml():
    mqtt_client.publish("buttons/wait", "b")
    return 'success'

@app.route('/st', methods=['POST'])
def st():
    mqtt_client.publish("buttons/wait", "a")
    return 'success'


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
        return render_template('balance_editor.html')
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


@app.route('/speech')
def speech():
    return render_template('speech.html')


@app.route('/library')
def library():
    chart = []
    for i in db.get_songs():
        print(i[0])
        chart.append(i[0])
    print(chart)
    return render_template('library.html', chart=chart)


@app.route('/music/<path:filename>')
def get_music(filename):
    return send_from_directory(config_read()['music-path'], filename)


@app.route('/wallet/5-old')
def wallet_5_old():
    return render_template('wallet_5_old.html')


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


@app.route('/song-rating', methods=['GET'])
def song_rating():
    return render_template('song_rating.html', chart=[[song, rating] for rating, song in reversed(db.get_songs_top())])


@app.route('/download-photo')
def download_photo():
    path = config_read()['archives-path']
    if not os.path.exists(path):
        os.makedirs(path)
    return render_template('download_photo.html',
                           folders=[f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))],
                           files=[f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))],
                           dir='', )


@app.route('/download-photo/<path:path>')
def sub_download_photo(path):
    new_path = config_read()['archives-path'] + path
    if os.path.isdir(new_path):
        return render_template('download_photo.html',
                               folders=[f for f in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, f))],
                               files=[f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))],
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
