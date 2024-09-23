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

print(filenames)

s = socket.socket()
def connect(host: str) -> None:
    global s
    print(f"[+] Connecting to {host}:{SERVER_PORT}")
    s.connect((host, SERVER_PORT))
    print("[+] Connected.")


def send_file_count() -> None:
    global s
    count = str(len(filenames))
    s.send(count.encode())
    s.recv(2).decode()


def receive_file_count() -> int:
    received = s.recv(128).decode()
    count = received
    s.send(b'Ok')
    print(f'Await {count} files')
    return int(count)


def send_file(filename: str) -> None:
    filesize = os.path.getsize(filename)
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
    if s.recv(2).decode() == 'Ex':
        return

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))


def receive_file() -> None:
    received = s.recv(128).decode()
    filename, filesize = received.split(SEPARATOR)
    if os.path.exists(filename):
        s.send(b'Ex')
        print(f'File {filename} is already exist')
        return
    s.send(b'Nw')
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
            bytes_read = s.recv(p)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))


connect(host)

send_file_count()
for filename in filenames:
    send_file(filename)

count_of_files = receive_file_count()

for _ in range(count_of_files):
    receive_file()

s.close()
