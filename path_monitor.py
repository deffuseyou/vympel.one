import time
import telegram
from watchdog.events import *
from watchdog.observers import Observer
from data_processing import config_read

token = os.environ['TG_BOT_TOKEN']
bot = telegram.Bot(token=token)


class PathHandler(FileSystemEventHandler):
    def on_created(self, event):
        path = event.src_path.replace(config_read()["monitor-path"] + "\\", "")
        if 'TeraCopy' not in path:
            for telegram_id in config_read()['admin-telegram-id']:
                bot.send_message(telegram_id, f'<b>{path}</b>', parse_mode='html')

    # def on_modified(self, event):
    #     path = event.src_path.replace(config_read()["monitor-path"] + "\\", "")
    #     if 'TeraCopy' not in path:
    #         for telegram_id in config_read()['admin-telegram-id']:
    #             bot.send_message(telegram_id, f'изменено:\n<b>{path}\n</b>', parse_mode='html')


if __name__ == "__main__":
    print(config_read()['album_ids'])
    path = config_read()["monitor-path"]
    path_handler = PathHandler()
    observer = Observer()
    observer.schedule(path_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()
