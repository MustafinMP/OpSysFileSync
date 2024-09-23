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


def format_path(path: str) -> str:
    return '/'.join(path.split('\\'))


def get_files_for_sending():
    filenames = []
    for dir_info in os.walk('test_dir'):
        for file in dir_info[2]:
            dr = format_path(dir_info[0])
            filenames.append(f'{dr}/{file}')
    return filenames


filenames = get_files_for_sending()


class Server:
    def __init__(self):
        self.s = socket.socket()
        self.s.bind((SERVER_HOST, SERVER_PORT))
        self.s.listen(1)

        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
        self.client_socket, address = self.s.accept()
        print(f"[+] {address} is connected.")

    def receive_file(self) -> None:
        received = self.client_socket.recv(128).decode()
        filename, filesize = received.split(SEPARATOR)
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
        filesize = os.path.getsize(filename)
        self.client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())
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

    def receive_file_count(self) -> int:
        received = self.client_socket.recv(128).decode()
        count = received
        self.client_socket.send(b'Ok')
        print(f'Await {count} files')
        return int(count)

    def send_file_count(self) -> None:
        count = str(len(filenames))
        self.client_socket.send(count.encode())
        self.client_socket.recv(2).decode()

    def receive_all(self) -> None:
        count_of_files = self.receive_file_count()
        for _ in range(int(count_of_files)):
            self.receive_file()

    def send_all(self) -> None:
        self.send_file_count()
        for filename in filenames:
            self.send_file(filename)

    def close(self):
        self.client_socket.close()
        self.s.close()



# close the client socket
# close the server socket