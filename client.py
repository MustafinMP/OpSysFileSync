import socket
import tqdm
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


host = get_local_ip()  # input('Введите хост подключения')
SERVER_PORT = 5001


def get_files_for_sending(path_from):
    filenames = []
    for dir_info in os.walk(path_from):
        for file in dir_info[2]:
            dr = '/'.join(dir_info[0].split('\\'))
            filenames.append(f'{dr}/{file}')
    return filenames


class Client:
    def __init__(self, data_dir='save_dir'):
        self.s = socket.socket()
        self.data_dir = data_dir

    def connect(self, host: str) -> None:
        print(f"[+] Connecting to {host}:{SERVER_PORT}")
        self.s.connect((host, SERVER_PORT))
        print("[+] Connected.")

    def verify_code(self, code: int) -> bool:
        self.s.send(str(code).encode())
        if not self.s.recv(2).decode() == 'Ok':
            print('Неверный код доступа')
            return False
        return True

    def send_file_count(self, count: int) -> None:
        self.s.send(str(count).encode())
        self.s.recv(2).decode()

    def receive_file_count(self) -> int:
        received = self.s.recv(128).decode()
        count = received
        self.s.send(b'Ok')
        print(f'Await {count} files')
        return int(count)

    def send_file(self, filename: str) -> None:
        filesize = os.path.getsize(filename)
        self.s.send(f"{filename}{SEPARATOR}{filesize}".encode())
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

    def receive_file(self) -> None:
        received = self.s.recv(128).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = filename[filename.index("/") + 1:]
        if self.data_dir:
            filename = f'{self.data_dir}/' + filename
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

    def send_all(self) -> None:
        filenames = get_files_for_sending(self.data_dir)
        self.send_file_count(len(filenames))
        for filename in filenames:
            self.send_file(filename)

    def receive_all(self):
        count_of_files = self.receive_file_count()
        for _ in range(count_of_files):
            self.receive_file()

    def close(self):
        self.s.close()


if __name__ == '__main__':
    client = Client()
    client.connect(host)
    client.send_all()
    client.receive_all()
    client.close()

