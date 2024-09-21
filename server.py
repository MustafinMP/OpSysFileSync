import socket
import tqdm
import os

SERVER_HOST = "localhost"
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

received = client_socket.recv(128).decode()
count_of_files = received
client_socket.send(b'Ok')
print(f'Await {count_of_files} files')

for _ in range(int(count_of_files)):
    received = client_socket.recv(128).decode()
    filename, filesize = received.split(SEPARATOR)
    client_socket.send(b'Ok')
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

# close the client socket
client_socket.close()
# close the server socket
s.close()
