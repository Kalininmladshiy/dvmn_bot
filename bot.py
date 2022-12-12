import requests
import os
import telegram
import time
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()
    dvmn_token = os.getenv("DVMN_TOKEN")
    tg_token = os.getenv("TG_BOT_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    bot = telegram.Bot(token=tg_token)
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
            if response.json()['status'] == 'found':
                lesson_title = response.json()['new_attempts'][0]['lesson_title']
                bot.send_message(
                    chat_id=tg_chat_id,
                    text=f"Преподаватель проверил работу '{lesson_title}'!",
                 )
                if response.json()['new_attempts'][0]['is_negative']:
                    lesson_url = response.json()['new_attempts'][0]['lesson_url']
                    bot.send_message(
                        chat_id=tg_chat_id,
                        text=f"К сожалению в работе'{lesson_url}' нашлись ошибки!",
                     )
                else:
                    bot.send_message(
                        chat_id=tg_chat_id,
                        text="Преподавателю все понравилось!",
                     )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            print('Произошел разрыв сетевого соединения. Ожидаем 10 секунд.')
            time.sleep(10)
            continue
        timestamp = response.json()['last_attempt_timestamp']
        payload = {"timestamp": timestamp}
