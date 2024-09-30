import socket
import tqdm
import os

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


class Client:
    def __init__(self, data_dir: str):
        """

        :param data_dir: абсолютный путь к директории для синхронизации
        """

        self.s = socket.socket()
        self.abs_dir_path = data_dir

    def connect(self, host: str) -> None:
        """Подключается к серверу по указанному хосту

        :param host: хост подключения
        :return: none
        """

        print(f"[+] Подключение к {host}:{SERVER_PORT}")
        self.s.connect((host, SERVER_PORT))
        print("[+] Подключено.")

    def verify_code(self, code: int) -> bool:
        """

        :param code:
        :return:
        """

        self.s.send(str(code).encode())
        if not self.s.recv(2).decode() == 'Ok':
            print('Неверный код доступа')
            return False
        return True

    def receive_file_count(self) -> int:
        received = self.s.recv(128).decode()
        count = received
        self.s.send(b'Ok')
        print(f'Await {count} files')
        return int(count)

    def send_file_count(self, count: int) -> None:
        self.s.send(str(count).encode())
        self.s.recv(2).decode()

    def receive_file(self) -> None:
        received = self.s.recv(128).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = f'{self.abs_dir_path}/{filename}'

        if os.path.exists(filename):
            self.s.send(b'Ex')
            print(f'File {filename} is already exist')
            return
        self.s.send(b'Nw')
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
                bytes_read = self.s.recv(p)
                if not bytes_read:
                    break
                f.write(bytes_read)
                progress.update(len(bytes_read))

    def send_file(self, filename: str) -> None:
        filesize = os.path.getsize(filename)
        filename_for_message = filename.replace(self.abs_dir_path, '')[1:]
        self.s.send(f"{filename_for_message}{SEPARATOR}{filesize}".encode())
        if self.s.recv(2).decode() == 'Ex':
            return

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                self.s.sendall(bytes_read)
                progress.update(len(bytes_read))

    def receive_all(self):
        count_of_files = self.receive_file_count()
        for _ in range(count_of_files):
            self.receive_file()

    def send_all(self) -> None:
        filenames = get_files_for_sending(self.abs_dir_path)
        self.send_file_count(len(filenames))
        for filename in filenames:
            self.send_file(filename)

    def close(self):
        self.s.close()


if __name__ == '__main__':
    client = Client('C:/Users/musta/PycharmProjects/OpSysFileSync/data_dir')
    client.connect(host)
    client.send_all()
    client.receive_all()
    client.close()

