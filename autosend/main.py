import configparser
import os
import logging
from telethon.sync import TelegramClient, errors
from time import sleep
from telethon.errors.rpcerrorlist import MessageTooLongError, PeerIdInvalidError
from datetime import datetime

logging.basicConfig(filename='./logs/errors.log', level=logging.ERROR,
                    format='%(asctime)s: %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')

config = configparser.ConfigParser()
config_file = 'config.ini'

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

delay = int(input('Введите значение таймера в секундах: '))


def dialog_sort(dialog):
    return dialog.unread_count


def log_delivery_status(phone, dialog_name, status, channel_link=None):
    log_file = f'./logs/{phone}.log'  
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f'Дата: {datetime.now()}, Диалог: {dialog_name}, Статус: {status}\n')
        if channel_link:
            log.write(f'Ссылка на канал: {channel_link}\n')


def spammer(client, phone):
    k = 0
    j = 0

    def create_groups_list(groups=[]):
        for dialog in client.iter_dialogs():
            if dialog.is_group and dialog.unread_count >= 1:
                groups.append(dialog)
        return groups

    with client:
        for m in client.iter_messages('me', 1):
            msg = m

        while True:
            groups = create_groups_list()
            groups.sort(key=dialog_sort, reverse=True)
            for g in groups[:10000]:
                try:
                    forward_message = client.forward_messages(g, msg, 'me')
                    forward_message_id = forward_message.id

                    delivered_message = client.get_messages(g, ids=forward_message_id)
                    try:
                        if delivered_message and delivered_message.date:
                            log_delivery_status(phone, g.name, 'Доставлено', channel_link=g.username)
                            k = k + 1
                        else:
                            log_delivery_status(phone, g.name, 'Не доставлено', channel_link=g.username)
                    except AttributeError:
                        log_delivery_status(phone, g.name, 'Не доставлено', channel_link=g.username)

                except errors.ForbiddenError as o:
                    client.delete_dialog(g)
                    if g.entity.username:
                        error_message = f'Error: {o.message} Аккаунт покинул @{g.entity.username}'
                        logging.error(error_message)
                        print(error_message)
                    else:
                        error_message = f'Error: {o.message} Аккаунт покинул {g.name}'
                        logging.error(error_message)
                        print(error_message)
                except errors.FloodError as e:
                    if e.seconds > 80:
                        continue
                    else:
                        error_message = f'Error: {e.message} Требуется ожидание {e.seconds} секунд'
                        logging.error(error_message)
                        print(error_message)
                        sleep(e.seconds)
                except PeerIdInvalidError:
                    client.delete_dialog(g)
                except MessageTooLongError:
                    error_message = f'Message was too long ==> {g.name}'
                    logging.error(error_message)
                    print(error_message)
                except errors.BadRequestError as i:
                    error_message = f'Error: {i.message}'
                    logging.error(error_message)
                    print(error_message)
                except errors.RPCError as a:
                    error_message = f'Error: {a.message}'
                    logging.error(error_message)
                    print(error_message)

            j = k + j
            k = 0
            print('Отправлено сообщений: ', j)
            sleep(delay)
            groups.clear()


if __name__ == '__main__':
    phone = input('Введите номер телефона: ')
    session_file = os.path.join('sessions', f'{phone}.session')

    try:
        client = TelegramClient(session_file, api_id, api_hash)
        client.connect()

        if not client.is_user_authorized():
            client.send_code_request(phone)
            try:
                client.sign_in(phone, input('Введите код, который прислал телеграм: '))
            except errors.SessionPasswordNeededError:
                client.sign_in(password=input('Введите код 2FA телеграм: '))

        spammer(client, phone)
    except ConnectionError:
        error_message = "Требуется сменить api_hash, api_id"
        logging.error(error_message)
        print(error_message)
