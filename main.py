import os
from pathlib import Path
import time
from datetime import datetime
from random import randrange
import configparser
import logging

from telethon.sync import TelegramClient, errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors.rpcerrorlist import SessionPasswordNeededError, ChannelsTooMuchError, ChannelInvalidError, ChannelPrivateError

# Configure logging
logs_directory = './logs'
os.makedirs(logs_directory, exist_ok=True)
logging.basicConfig(filename=os.path.join(logs_directory, 'errors.log'), level=logging.ERROR)

# Load configuration from config.ini
config = configparser.ConfigParser()
config_file = './config.ini'

if not os.path.exists(config_file):
    config['Telegram'] = {
        'api_id': '',
        'api_hash': ''
    }

    with open(config_file, 'w') as configfile:
        config.write(configfile)

config.read(config_file)
api_id = int(config['Telegram']['api_id'])
api_hash = config['Telegram']['api_hash']

BASE_DIR = Path(__file__).resolve().parent
CHANNELS_DIRECTORY = './channels'
SESSIONS_DIRECTORY = './sessions'
FILE_PATH = os.path.join(CHANNELS_DIRECTORY, 'channels.txt')
LOG_FILE = os.path.join(logs_directory, 'logs.log')


def sleep():
    const = randrange(120, 300, 60)
    print(f'{datetime.now()}: Засыпаю на {const} секунд.')
    time.sleep(const)


def error_processing(channel, message):
    logging.error(f'{datetime.now()}: Канал {channel}, {message}.')


def joining_a_group(client, num, phone):
    li = read_channel_list()

    const = len(li) // num
    count_step = 0
    count_sub_chats = 0
    list_nosub_chats = []

    logging.info(f'{datetime.now()}: Начал вступление в группы для номера телефона {phone}.')

    for e in range(0, len(li), num):
        count_step += 1
        if count_step <= const:
            count_sub_chats, list_nosub_chats = join_channels(client, li[e:e + num], count_sub_chats, list_nosub_chats, phone)
            sleep()
        else:
            count_sub_chats, list_nosub_chats = join_channels(client, li[e:e + num], count_sub_chats, list_nosub_chats, phone)
            sleep()

    write_nosub_channels(list_nosub_chats)

    end = datetime.now()
    logging.info(f'{datetime.now()}: Завершил вступление в группы для номера телефона {phone}. '
                 f'Потрачено времени: {end - start}. Вступил в {count_sub_chats} чатов из {len(li)}.')


def read_channel_list():
    with open(FILE_PATH) as file_channels:
        return file_channels.read().split('\n')


def join_channels(client, channels, count_sub_chats, list_nosub_chats, phone):
    for i in channels:
        try:
            result = client(JoinChannelRequest(channel=i))
            count_sub_chats += 1
            status = f'{datetime.now()}: ({count_sub_chats}) Подписался на канал {i}'
            print(status)
            log_status(phone, i, status)
            time.sleep(randrange(10, 20, 1))
        except ChannelsTooMuchError:
            error_processing(i, 'Много входов в группы.')
            sleep()
            client(JoinChannelRequest(channel=i))
            count_sub_chats += 1
            status = f'{datetime.now()}: ({count_sub_chats}) Подписался на канал {i}'
            print(status)
            log_status(phone, i, status)
            time.sleep(randrange(10, 20, 1))
        except errors.FloodWaitError as e:
            error_processing(i, 'Не прошел по таймингам. Вступит в чат чуть-чуть позднее!')
            print(f'{datetime.now()}: Уснет сейчас на {e.seconds + 10}')
            time.sleep(e.seconds + 10)
            client(JoinChannelRequest(channel=i))
            count_sub_chats += 1
            status = f'{datetime.now()}: ({count_sub_chats}) Подписался на канал {i}'
            print(status)
            log_status(phone, i, status)
            time.sleep(randrange(10, 20, 1))
        except ChannelInvalidError:
            error_processing(i, 'Неверный объект канала.')
            list_nosub_chats.append(i)
            continue
        except ChannelPrivateError:
            error_processing(i, 'Канал является приватным.')
            list_nosub_chats.append(i)
            continue
        except errors.UsernameInvalidError as e:
            error_processing(i, 'Неверное название канала.')
            list_nosub_chats.append(i)
            continue
        except Exception as e:
            error_processing(i, f'Название канала {i} неверно, либо не существует')
            list_nosub_chats.append(i)
            continue

    return count_sub_chats, list_nosub_chats


def write_nosub_channels(channels):
    with open(os.path.join(CHANNELS_DIRECTORY, 'nosub_channels.txt'), 'w') as file_nosub_channels:
        for i in channels:
            file_nosub_channels.write(f'{i}\n')


def log_status(phone, channel, status):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f'{datetime.now()}: Номер телефона {phone}, Канал {channel}, {status}\n')


if __name__ == '__main__':
    start = datetime.now()
    print(f'{datetime.now()}: Начал работу')

    # Create a directory for storing sessions
    os.makedirs(SESSIONS_DIRECTORY, exist_ok=True)

    phone = input('Введите номер телефона: ')
    session_file = os.path.join(SESSIONS_DIRECTORY, f'{phone}.session')

    client = TelegramClient(session_file, api_id, api_hash)
    client.connect()

    if not client.is_user_authorized():
        client.send_code_request(phone)
        try:
            client.sign_in(phone, input('Введите код, который прислал телеграм: '))
        except SessionPasswordNeededError:
            client.sign_in(password=input('Введите код 2FA телеграм: '))

    joining_a_group(client, 5, phone)
    client.disconnect()

    print(f'{datetime.now()}: Завершил работу')
