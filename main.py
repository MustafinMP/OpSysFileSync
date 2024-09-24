import random
import socket
import tkinter
from tkinter import filedialog


from verification import Verification


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


SERVER_HOST = get_local_ip()
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
s = socket.socket()


def get_absolute_path() -> str:
    print('В открывшемся диалоговом окне выберите директорию для синхронизации')
    root = tkinter.Tk()
    root.withdraw()
    dir_ = filedialog.askdirectory()
    return dir_


def choice_mode() -> str:
    print('Выберите режим запуска - Primary или Secondary')
    mode = input('[p/s]: ')
    while mode not in ['p', 's']:
        print('Некорректный ввод, выберите режим снова')
        mode = input('[p/s]: ')
    return mode


def main() -> None:
    print('Запуск программы')
    abs_dir_path = get_absolute_path()
    print(f'выбрана директория {abs_dir_path}')
    mode = choice_mode()
    if mode == 'p':
        from server import Server
        server = Server(abs_dir_path)
        code = random.randint(100, 999)
        # print(f'Введите код верификации на другом устройстве: {code}')
        if True:  # server.verify_code(code):
            server.receive_all()
            server.send_all()
        server.close()
    elif mode == 's':
        from client import Client
        client = Client(abs_dir_path)
        host = input('Укажите хост подключения: ')
        client.connect(host)
        # code = input('Введите трехзначный код, указанный на экране другого устройства: ')
        if True:  # client.verify_code(code):
            client.send_all()
            client.receive_all()
        client.close()


if __name__ == '__main__':
    main()


