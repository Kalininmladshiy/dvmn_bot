import requests
import os
import telegram
import time
import logging
from dotenv import load_dotenv

logger = logging.getLogger('dvmn_bot')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_logger_token, tg_chat_id):
        super().__init__()
        self.tg_chat_id = tg_chat_id
        self.tg_logger_token = tg_logger_token
        self.bot_logger = telegram.Bot(token=self.tg_logger_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.bot_logger.send_message(chat_id=self.tg_chat_id, text=log_entry)

if __name__ == '__main__':
    load_dotenv()
    dvmn_token = os.getenv("DVMN_TOKEN")
    tg_token = os.getenv("TG_BOT_TOKEN")
    tg_logger_token = os.getenv("TG_BOT_LOGGER_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")

    bot = telegram.Bot(token=tg_token)
    
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(process)d %(levelname)s %(filename)s %(lineno)d %(asctime)s %(message)s"
     )
    tg_handler = TelegramLogsHandler(tg_logger_token, tg_chat_id)
    tg_handler.setLevel(logging.DEBUG)
    tg_handler.setFormatter(formatter)
    logger.addHandler(tg_handler)
    logger.debug('Бот запущен')

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        "Authorization": f"Token {dvmn_token}",
    }
    payload = {}
    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                params=payload,
                timeout=5,
             )
            response.raise_for_status()
            task = response.json()
            if task['status'] == 'found':
                timestamp = task['last_attempt_timestamp']
                lesson_title = task['new_attempts'][0]['lesson_title']
                logger.info('Работа проверена')
                bot.send_message(
                    chat_id=tg_chat_id,
                    text=f"Преподаватель проверил работу '{lesson_title}'!",
                 )
                if task['new_attempts'][0]['is_negative']:
                    lesson_url = task['new_attempts'][0]['lesson_url']
                    bot.send_message(
                        chat_id=tg_chat_id,
                        text=f"К сожалению в работе'{lesson_url}' нашлись ошибки!",
                     )
                else:
                    bot.send_message(
                        chat_id=tg_chat_id,
                        text="Преподавателю все понравилось!",
                     )
            else:
                timestamp = task['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError as err:
            logging.error(err, exc_info=True)
            time.sleep(10)
            continue
        payload = {"timestamp": timestamp}
