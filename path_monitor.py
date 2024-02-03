import time
import telegram
from watchdog.events import *
from watchdog.observers import Observer
from data_processing import *

token = os.environ['TG_BOT_TOKEN']
bot = telegram.Bot(token=token)


class PathHandler(FileSystemEventHandler):
    def on_created(self, event):
        path = event.src_path.replace(config_read()[f"monitor-path"] + "\\", "")
        if 'TeraCopy' not in path:
            for telegram_id in config_read()['admin-telegram-id']:
                bot.send_message(telegram_id, f'<b>{path}</b>', parse_mode='html')

    # def on_modified(self, event):
    #     path = event.src_path.replace(config_read()[f"monitor-path"] + "\\", "")
    #     if 'TeraCopy' not in path:
    #         for telegram_id in config_read()['admin-telegram-id']:
    #             bot.send_message(telegram_id, f'изменено:\n<b>{path}\n</b>', parse_mode='html')



path = config_read()[f"monitor-path"]
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
