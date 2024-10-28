import socket

from abstract_connect import AbstractConnect


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


SERVER_HOST = get_local_ip()
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


class Server(AbstractConnect):
    def __init__(self, data_dir):
        """Инициализация сокет-соединения в режиме сервера.

        :param data_dir: абсолютный путь директории для синхронизации.
        """

        super().__init__(data_dir)
        self.socket.bind((SERVER_HOST, SERVER_PORT))
        self.socket.listen(1)

        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
        self.connect_socket, address = self.socket.accept()
        print(f"[+] {address} is connected.")

    def close(self):
        """Закрытие сокет-соединения.

        :return: none.
        """

        self.connect_socket.close()
        self.socket.close()


if __name__ == '__main__':
    server = Server('C:/Users/musta/PycharmProjects/OpSysFileSync/save_dir')
    server.receive_all()
    server.send_all()
    server.close()
