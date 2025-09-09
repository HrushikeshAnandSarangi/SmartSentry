import time
import socket

file_paths = [
    "data/train_FD001.txt",
    "data/train_FD002.txt",
    "data/train_FD003.txt"
]  

HOST = "127.0.0.1"
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
print(f"Waiting for a connection on {HOST}:{PORT}...")
conn, addr = sock.accept()
print(f"Connected by {addr}")

try:
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            for line in f:
                data_str = line.strip()
                if not data_str:
                    continue
                conn.sendall(data_str.encode() + b'\n')
                print(f"Sent: {data_str}")
                time.sleep(5)
finally:
    conn.close()
    sock.close()
