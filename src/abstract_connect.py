import socket

import tqdm
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


def get_files_for_sending(path_from: str) -> list[str]:
    """Подготавливает список абсолютный тупей файлов для синхронизации

    :param path_from: путь к директории для синхронизации
    :return: список абсолютных путей к файлам
    """

    filenames = []
    # рекурсивный проход по файлам
    for dir_info in os.walk(path_from):
        for file in dir_info[2]:
            # замена символов '\' на '/'
            dr = '/'.join(dir_info[0].split('\\'))
            filenames.append(f'{dr}/{file}')
    return filenames


class BaseSocket:
    def __init__(self, data_dir):
        """Инициализация сокет-соединения в режиме сервера.

        :param data_dir: абсолютный путь директории для синхронизации.
        """

        self.socket = socket.socket()
        self.abs_dir_path = data_dir
        self.connect_socket = self.socket

    def receive_file_count(self) -> int:
        """Получение количества передаваемых файлов.

        :return: количество файлов.
        """

        received = self.connect_socket.recv(1024).decode()
        count = received
        self.connect_socket.send(b'Ok')
        print(f'Await {count} files')
        return int(count)

    def send_file_count(self, count: int) -> None:
        """ Отправка количества передаваемых файлов.

        :param count: количество файлов.
        :return: none.
        """

        self.connect_socket.send(str(count).encode())
        self.connect_socket.recv(2).decode()

    def receive_file(self) -> None:
        """Получение одного файла по сокет-соединению.

        :return: none.
        """

        received = self.connect_socket.recv(1024).decode('utf-8')
        filename, filesize = received.split(SEPARATOR)
        filename = f'{self.abs_dir_path}/{filename}'

        if os.path.exists(filename):
            self.connect_socket.send(b'Ex')
            return
        self.connect_socket.send(b'Nw')

        *path, filename = filename.split('/')
        path = '/'.join(path)
        if not os.path.exists(path):
            os.mkdir(path)
        filename = f'{path}/{filename}'
        filesize = int(filesize)

        downloaded_bytes = 0
        with open(filename, "wb") as f:
            while downloaded_bytes < filesize:
                downloaded_bytes += BUFFER_SIZE
                bytes_read = self.connect_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
        self.connect_socket.send(b'Ok')

    def send_file(self, filename: str) -> None:
        """Отправка одного файла по сокет-соединению.

        :param filename: имя отправляемого файла.
        :return: none.
        """

        filesize = os.path.getsize(filename)
        filename_for_message = filename.replace(self.abs_dir_path, '')[1:]
        self.connect_socket.send(f"{filename_for_message}{SEPARATOR}{filesize}".encode('utf-8'))
        if self.connect_socket.recv(2).decode() == 'Ex':
            return

        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                self.connect_socket.sendall(bytes_read)
        self.connect_socket.recv(2)

    def receive_all(self) -> None:
        """Получение всех файлов по сокет-соединению.

        :return: none.
        """

        count_of_files = self.receive_file_count()
        progress = tqdm.tqdm(range(count_of_files), f"Receiving files", unit="B", unit_scale=True, unit_divisor=1)
        for _ in range(int(count_of_files)):
            self.receive_file()
            progress.update()

    def send_all(self) -> None:
        """Отправка всех файлов по сокет-соединению.

        :return: none.
        """

        filenames = get_files_for_sending(self.abs_dir_path)
        self.send_file_count(len(filenames))
        progress = tqdm.tqdm(range(len(filenames)), f"Sending files", unit="B", unit_scale=True, unit_divisor=1)
        for filename in filenames:
            self.send_file(filename)
            progress.update()
