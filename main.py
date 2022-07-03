import requests
import telegram
import time
import datetime
import os

TELEGRAM_TOKEN = os.environ.get("TOKEN")
TELEGRAM_ID = os.environ.get("ID")


def auth() -> dict | bool:
    token_url = "https://konta1.ksdo.gov.pl/connect/token"
    payload = {
        "grant_type": "password",
        "scope": "openid offline_access",
        "username": os.environ.get("USERNAME"),
        "password": os.environ.get("PASSWORD"),
        "client_id": "pass",
        "client_secret": os.environ.get("SECRET"),
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        return response.json()
    return False


def get_results():
    authinfo = auth()
    if not authinfo:
        return False
    token = authinfo['access_token']
    token_type = authinfo['token_type']

    headers = {
        "Authorization": " ".join([token_type, token])
    }
    url = "https://wyniki.edu.pl/api/ZIUZM/Wynik"
    response = requests.get(url, headers=headers)

    print('results', response)

    if response.json():
        telegram_send_message(response.json())
        return True
    return False


def telegram_send_message(message):
    bot = telegram.bot.Bot(TELEGRAM_TOKEN)
    channel_id = -1001505111561
    message = str(message)
    try:
        if len(message) > 4096:
            for x in range(0, len(message), 4096):
                bot.send_message(channel_id, message[x:x+4096])
        else:
            bot.send_message(channel_id, message)

        return True
    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    while True:
        try:
            results_time = datetime.datetime.fromtimestamp(1657002600)
            if results_time > datetime.datetime.now():
                time.sleep(int((results_time - datetime.datetime.now()).total_seconds()))

            telegram_send_message("Za moment wyniki")

            try:
                if get_results():
                    break
            except Exception as e:
                print(e)
                time.sleep(5)
                continue
        except Exception as e:
            print("error in main loop", e)
            time.sleep(10)
