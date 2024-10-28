import socket

from abstract_connect import AbstractConnect

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096


def get_local_ip() -> str:
    """Определяет локальный хост сервера

    :return: локальный хост сервера
    """

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


host = get_local_ip()  # input('Введите хост подключения')
SERVER_PORT = 5001


class Client(AbstractConnect):
    def __init__(self, data_dir: str):
        """Инициализация сокет-соединения в режиме клиента.

        :param data_dir: абсолютный путь директории для синхронизации.
        """

        super().__init__(data_dir)

    def connect(self, host: str) -> None:
        """Подключение к серверу по указанному хосту.

        :param host: хост подключения.
        :return: none
        """

        print(f"[+] Подключение к {host}:{SERVER_PORT}")
        self.connect_socket.connect((host, SERVER_PORT))
        print("[+] Подключено.")

    def close(self):
        """Закрытие сокет-соединения.

        :return: none.
        """

        self.connect_socket.close()


if __name__ == '__main__':
    client = Client('C:/Users/musta/PycharmProjects/OpSysFileSync/save_dir')
    client.connect(host)
    client.send_all()
    client.receive_all()
    client.close()
