from watchdog.observers import Observer
from watchdog.events import *
import time
import telegram

token = '5452169304:AAGqKxXhwlEuurWY9F-hxbepZK3k_iPz3tY'
bot = telegram.Bot(token=token)

a = r"D:\c ноута"


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        bot.send_message(518325236, f'<b>{event.src_path[18:]}</b>', parse_mode='html')
        bot.send_message(873142541, f'<b>{event.src_path[18:]}</b>', parse_mode='html')
        bot.send_message(864662054, f'<b>{event.src_path[18:]}</b>', parse_mode='html')

    def on_modified(self, event):
        bot.send_message(518325236, f'файл изменен:\n<b>{event.src_path[18:]}</b>', parse_mode='html')
        bot.send_message(873142541, f'<b>{event.src_path[18:]}</b>', parse_mode='html')
        bot.send_message(864662054, f'<b>{event.src_path[18:]}</b>', parse_mode='html')


if __name__ == "__main__":
    path = a
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()
