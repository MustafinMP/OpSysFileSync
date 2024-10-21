import socket
import tqdm
import os


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


SERVER_HOST = get_local_ip()
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


def get_files_for_sending(path_from):
    filenames = []
    for dir_info in os.walk(path_from):
        for file in dir_info[2]:
            dr = '/'.join(dir_info[0].split('\\'))
            filenames.append(f'{dr}/{file}')
    return filenames


class Server:
    def __init__(self, data_dir):
        """Инициализация сокет-соединения в режиме сервера.

        :param data_dir: абсолютный путь директории для синхронизации.
        """

        self.s = socket.socket()
        self.s.bind((SERVER_HOST, SERVER_PORT))
        self.s.listen(1)
        self.abs_dir_path = data_dir

        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
        self.client_socket, address = self.s.accept()
        print(f"[+] {address} is connected.")

    def receive_file_count(self) -> int:
        """Получение количества передаваемых файлов.

        :return: количество файлов.
        """

        received = self.client_socket.recv(128).decode()
        count = received
        self.client_socket.send(b'Ok')
        print(f'Await {count} files')
        return int(count)

    def send_file_count(self, count: int) -> None:
        """ Отправка количества передаваемых файлов.

        :param count: количество файлов.
        :return: none.
        """

        self.client_socket.send(str(count).encode())
        self.client_socket.recv(2).decode()

    def receive_file(self) -> None:
        """Получение одного файла по сокет-соединению.

        :return: none.
        """

        received = self.client_socket.recv(128).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = f'{self.abs_dir_path}/{filename}'

        if os.path.exists(filename):
            self.client_socket.send(b'Ex')
            print(f'File {filename} is already exist')
            return
        self.client_socket.send(b'Nw')
        *path, filename = filename.split('/')
        path = '/'.join(path)
        if not os.path.exists(path):
            os.mkdir(path)
        filename = f'{path}/{filename}'
        filesize = int(filesize)

        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        downloaded_bytes_count = 0
        with open(filename, "wb") as f:
            while downloaded_bytes_count < filesize:
                p = BUFFER_SIZE if filesize - downloaded_bytes_count >= BUFFER_SIZE else filesize - downloaded_bytes_count
                downloaded_bytes_count += p
                bytes_read = self.client_socket.recv(p)
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
        self.client_socket.send(f"{filename_for_message}{SEPARATOR}{filesize}".encode())
        if self.client_socket.recv(2).decode() == 'Ex':
            return

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                self.client_socket.sendall(bytes_read)
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

    def close(self):
        """Закрытие сокет-соединения.

        :return: none.
        """

        self.client_socket.close()
        self.s.close()


if __name__ == '__main__':
    server = Server('C:/Users/musta/PycharmProjects/OpSysFileSync/save_dir')
    server.receive_all()
    server.send_all()
    server.close()
