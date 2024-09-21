import socket
import tqdm
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
host = "localhost"
port = 5001


def format_path(path: str) -> str:
    return '/'.join(path.split('\\'))


filenames = []
for dir_info in os.walk('test_dir'):
    for file in dir_info[2]:
        dr = format_path(dir_info[0])
        filenames.append(f'{dr}/{file}')
print(filenames)

s = socket.socket()
print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")
count = str(len(filenames))
s.send(count.encode())
s.recv(2).decode()

for filename in filenames:
    filesize = os.path.getsize(filename)
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
    s.recv(2).decode()

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))


s.close()
