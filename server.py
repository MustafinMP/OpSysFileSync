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
s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))

# enabling our server to accept connections
# 5 here is the number of unaccepted connections that
# the system will allow before refusing new connections
s.listen(5)

print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
client_socket, address = s.accept()
print(f"[+] {address} is connected.")


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


def receive_file() -> None:
    received = client_socket.recv(128).decode()
    filename, filesize = received.split(SEPARATOR)
    if os.path.exists(filename):
        client_socket.send(b'Ex')
        print(f'File {filename} is already exist')
        return
    client_socket.send(b'Nw')
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
            bytes_read = client_socket.recv(p)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))


def send_file(filename: str) -> None:
    filesize = os.path.getsize(filename)
    client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())
    if client_socket.recv(2).decode() == 'Ex':
        return

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)
            progress.update(len(bytes_read))


def receive_file_count() -> int:
    received = client_socket.recv(128).decode()
    count = received
    client_socket.send(b'Ok')
    print(f'Await {count} files')
    return int(count)


def send_file_count() -> None:
    global client_socket
    count = str(len(filenames))
    client_socket.send(count.encode())
    client_socket.recv(2).decode()


count_of_files = receive_file_count()

for _ in range(int(count_of_files)):
    receive_file()


send_file_count()
for filename in filenames:
    send_file(filename)

# close the client socket
client_socket.close()
# close the server socket
s.close()
