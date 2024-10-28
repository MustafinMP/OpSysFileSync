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


class AbstractConnect:
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

        received = self.connect_socket.recv(128).decode()
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

        received = self.connect_socket.recv(128).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = f'{self.abs_dir_path}/{filename}'

        if os.path.exists(filename):
            self.connect_socket.send(b'Ex')
            print(f'File {filename} is already exist')
            return
        self.connect_socket.send(b'Nw')
        *path, filename = filename.split('/')
        path = '/'.join(path)
        if not os.path.exists(path):
            os.mkdir(path)
        filename = f'{path}/{filename}'
        filesize = int(filesize)

        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        downloaded_bytes = 0
        with open(filename, "wb") as f:
            while downloaded_bytes < filesize:
                p = BUFFER_SIZE if filesize - downloaded_bytes >= BUFFER_SIZE else filesize - downloaded_bytes
                downloaded_bytes += p
                bytes_read = self.connect_socket.recv(p)
                if not bytes_read:
                    break
                f.write(bytes_read)
                progress.update(len(bytes_read))

    def send_file(self, filename: str) -> None:
        """Отправка одного файла по сокет-соединению.

        :param filename: имя отправляемого файла.
        :return: none.
        """

        filesize = os.path.getsize(filename)
        filename_for_message = filename.replace(self.abs_dir_path, '')[1:]
        self.connect_socket.send(f"{filename_for_message}{SEPARATOR}{filesize}".encode())
        if self.connect_socket.recv(2).decode() == 'Ex':
            return

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                self.connect_socket.sendall(bytes_read)
                progress.update(len(bytes_read))

    def receive_all(self) -> None:
        """Получение всех файлов по сокет-соединению.

        :return: none.
        """

        count_of_files = self.receive_file_count()
        for _ in range(int(count_of_files)):
            self.receive_file()

    def send_all(self) -> None:
        """Отправка всех файлов по сокет-соединению.

        :return: none.
        """

        filenames = get_files_for_sending(self.abs_dir_path)
        self.send_file_count(len(filenames))
        for filename in filenames:
            self.send_file(filename)
