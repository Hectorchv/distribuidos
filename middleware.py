import socket
import time
import threading
import sys

MSGLEN = 1024

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
    def __init__(self, sock=None, host="127.0.0.1", port=65432):
        if sock is None:
            try:
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as err:
                print("Socket creation failed with error: %s", err)
        else:
            self.sock = sock

        self.sock.bind(("127.0.0.1", 65432))
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

def miserver(servidor):
    while True:
        servidor.accept()
        mensaje = servidor.receive()
        print(f"Mensaje recibido {mensaje}")
        servidor.send(mensaje)
    

if __name__ == "__main__":

    '''
    print("1) Servidor\n2) Enviar mensaje")
    option = input()
    option = int(option)

    if option == 1:
        servidor = ServerSocket()
        servidor.accept()
        mensaje = servidor.receive()
        print(f"Mensaje recibido {mensaje}")
        servidor.send(mensaje)
    elif option == 2:
        cliente = ClientSocket()
        if  cliente.conect("127.0.0.1", 65432):
            mensaje = input("Ingrese un mensaje: ")
            hora = time.time()
            hora = time.ctime(hora)
            cliente.send(mensaje + f" [{hora}]")
            respuesta = cliente.receive()
            print(f"Mensaje recivido como respuesta: {respuesta}")
        else:
            print("Fin del programa")
    '''

    #Server thread
    '''
    servidor = ServerSocket()
    t1 = threading.Thread(target=miserver, args=(servidor,))
    t1.start()
    '''

    print("1) Servidor\n2) Enviar mensaje")
    option = input()
    option = int(option)

    if option == 1:
        servidor = ServerSocket()
        t1 = threading.Thread(target=miserver, args=(servidor,))
        t1.start()
        t1.join()
    if option == 2:
        cliente = ClientSocket()
        if  cliente.conect("127.0.0.1", 65432):
            mensaje = input("Ingrese un mensaje: ")
            hora = time.time()
            hora = time.ctime(hora)
            cliente.send(mensaje + f" [{hora}]")
            respuesta = cliente.receive()
            print(f"Mensaje recivido como respuesta: {respuesta}")
        else:
            print("Fin del programa")