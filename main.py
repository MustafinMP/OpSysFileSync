import random
import socket

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


def choice_mode() -> str:
    print('Запуск программы')
    print('Выберите режим запуска - Primary или Secondary')
    mode = input('[p/s]: ')
    while mode not in ['p', 's']:
        print('Некорректный ввод, выберите режим снова')
        mode = input('[p/s]: ')
    return mode


def main() -> None:
    mode = choice_mode()
    if mode == 'p':
        from server import Server
        server = Server('data_dir')
        code = random.randint(100, 999)
        # print(f'Введите код верификации на другом устройстве: {code}')
        if True:  # server.verify_code(code):
            server.receive_all()
            server.send_all()
        server.close()
    elif mode == 's':
        from client import Client
        client = Client('save_dir')
        host = input('Укажите хост подключения: ')
        client.connect(host)
        # code = input('Введите трехзначный код, указанный на экране другого устройства: ')
        if True:  # client.verify_code(code):
            client.send_all()
            client.receive_all()
        client.close()


if __name__ == '__main__':
    main()


