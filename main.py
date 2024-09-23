import socket


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
        server = Server()
        server.receive_all()
        server.send_all()
        server.close()


if __name__ == '__main__':
    main()


