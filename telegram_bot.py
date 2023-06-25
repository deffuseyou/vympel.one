import os
from data_processing import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging

logging.basicConfig(handlers=[logging.StreamHandler(),
                              logging.FileHandler('telegram_bot.log')],
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def start(update, context):
    message = f"Telegram ID: <code>{update.message.chat_id}</code>"
    update.message.reply_html(message)


def button_click(update, context):
    if update.callback_query.data == 'transmit_massage':
        logging.info(f'транслируется: {update.callback_query.message.text}')
        logging.info(f'кнопка нажата @{update.callback_query.message.chat.username}')
        transmit_message(update.callback_query.message.text)


# Создаем экземпляр Updater и регистрируем обработчики
updater = Updater(token=os.environ['TG_BOT_TOKEN'], use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button_click))

# Запускаем бота
updater.start_polling()
