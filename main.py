import random
import socket
import sys
import tkinter
from time import sleep
from tkinter import filedialog

from verification import Verification


def get_local_ip() -> str:
    """Определяет локальный хост сервера

    :return: локальный хост сервера
    """

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


SERVER_HOST = get_local_ip()
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
s = socket.socket()


def get_absolute_path() -> str:
    """Получает абсолютный путь к директории для синхронизации через диалогое окно.

    :return: путь к директории.
    """

    print('[>] В открывшемся диалоговом окне выберите директорию для синхронизации')
    root = tkinter.Tk()
    root.withdraw()
    path_to_dir = filedialog.askdirectory()
    return path_to_dir


def choice_mode() -> str:
    """Получает от пользователя режим запуска программы (Primary или Secondary).

    :return: буква-код (p или s) режима запуска.
    """

    print('Выберите режим запуска - Primary или Secondary')
    mode = input('[p/s]: ')
    while mode not in ['p', 's']:
        print('Некорректный ввод, выберите режим снова')
        mode = input('[p/s]: ')
    return mode


def main() -> None:
    """Главная функция программы.

    :return: none.
    """

    print('[+] Запуск программы')
    abs_dir_path = get_absolute_path()
    print(f'[+] Выбрана директория {abs_dir_path}')
    mode = choice_mode()
    # работа в режиме сервера
    if mode == 'p':
        from server import Server
        server = Server(abs_dir_path)
        server.receive_all()
        server.send_all()
        server.close()
    # работа в режиме клиента
    elif mode == 's':
        from client import Client
        client = Client(abs_dir_path)
        host = input('[>] Укажите хост подключения: ')
        # Три попытки подключения
        for i in range(3):
            try:
                if i > 0:
                    print('[+] Повторная попытка подключения')
                client.connect(host)
                break
            except ConnectionRefusedError as e:
                print(e)
                sleep(1)
        # Если три попытки подключения не удались, завершаем программу
        else:
            print('[*] Подключение не установлено.')
            print(
                '[*] Проверьте, что второе устройство запущено в режиме Primary и подключено к Вашей сети,'
                ' и перезапустите программу.'
            )
            sys.exit(0)
        client.send_all()
        client.receive_all()
        client.close()


if __name__ == '__main__':
    main()
