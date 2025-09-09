import time
import socket

# Path to your .txt file
file_path = "data.txt"

# Socket configuration
HOST = "127.0.0.1"  # Localhost
PORT = 9999         # Port to send data

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
print(f"Waiting for a connection on {HOST}:{PORT}...")
conn, addr = sock.accept()
print(f"Connected by {addr}")

try:
    with open(file_path, 'r') as f:
        for line in f:
            data_str = line.strip()
            if not data_str:
                continue  # skip empty lines

            conn.sendall(data_str.encode() + b'\n')
            print(f"Sent: {data_str}")
            time.sleep(5)
finally:
    conn.close()
    sock.close()
