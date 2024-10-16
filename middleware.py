import socket
import time
import threading
import sys

MSGLEN = 1024
IP1 = ""
HOSTNAME = socket.gethostname()
NODES = {"pc1" : "", "pc2" : "", "pc3" : ""}
NODES.pop(HOSTNAME, -1)
class ClientSocket:
    def __init__(self, sock=None):
        if sock is None:
            try:
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as err:
                print("Socket creation failed with error: %s", err)
        
        else:
            self.sock = sock
    
    def conect(self, host, port):
        try:
            self.sock.connect((host, port))
            return True
        except ConnectionRefusedError :
            print(f"Conection refused by ({host}, {port})")
            self.sock.close()
            return False

    def send(self, msg):
        msglen = len(msg)
        msg = msg.encode()
        totalsent = 0
        while totalsent < msglen:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Scoket connection broken")
            totalsent = totalsent + sent
        self.sock.shutdown(socket.SHUT_WR)
    
    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk =  self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                break
            chunks.append(chunk.decode())
            bytes_recd = bytes_recd + len(chunk)
        return "".join(chunks)

class ServerSocket:
    def __init__(self, sock=None, host='', port=65432):
        if sock is None:
            try:
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as err:
                print("Socket creation failed with error: %s", err)
        else:
            self.sock = sock

        self.sock.bind(('', 65432))
        self.sock.listen(5)
    
    def accept(self):
        conn, addr = self.sock.accept()
        print(f"Connected by : {addr}")
        self.conn = conn

    def send(self, msg):
        totalsent = 0
        msglen = len(msg)
        while totalsent < msglen:
            sent = self.conn.send(msg[totalsent:].encode())
            if sent == 0:
                raise RuntimeError("Scoket connection broken")
            totalsent = totalsent + sent
        self.conn.close()
    
    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk =  self.conn.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                break
            chunks.append(chunk.decode())
            bytes_recd = bytes_recd + len(chunk)
        return "".join(chunks)

def miserver():
    register = open("register.txt", "a+")

    servidor = ServerSocket()
    while True:
        servidor.accept()
        mensaje = servidor.receive()
        register.write(f"{mensaje}")
        servidor.send("Ok")
    

if __name__ == "__main__":

    #Server thread
    t1 = threading.Thread(target=miserver)
    t1.start()

    while True:
        i = 1
        print("Enviar mensaje a:")
        for j in NODES:
            print(f"{i}) {j}")
            i = i + 1
        
        while True:
            try:
                option = int(input("Ingrese una opcion: "))
                if option > len(NODES):
                    print("Valor fuera de rango")
                else:
                    break
            except ValueError:
                option = print("Ingrese una opcioin valida")

        cliente = ClientSocket()
        if cliente.conect(NODES[list(NODES.keys())[option-1]], 65432):
            mensaje = input("Ingrese el mensaje: ")
            hora = time.time()
            hora = time.ctime(hora)
            cliente.send(f"[{hora}] " + mensaje)
            respuesta = cliente.receive()
            print(f"La respuesta fue: {respuesta}")
        else:
            print("No se logro conectar con el host")

    t1.join()
    register.close()