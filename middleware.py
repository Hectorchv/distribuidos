import socket
import time
import threading
import sys
import re
from getLocalIP import getLocalIP

MSGLEN = 1024
localIP = getLocalIP()
masterIP = "0.0.0.0"


IP1 = ""
HOSTNAME = socket.gethostname()
NODES = {"arch" : "192.168.1.74", "arch-lap" : "192.168.1.69", "pc3" : "192.168.1.77"}
NODES.pop(HOSTNAME, -1)

def electionMaster():

    thisNodeIsMaster = True
    candidates = []

    with open("nodes.txt", "r") as nodes:
        ipNodes  = [line.strip() for line in nodes.readlines()]

        for ip in ipNodes:
            if ip > localIP:
                candidates.append(ip)
    
    for ip in candidates:
        cliente = ClientSocket()
        if cliente.conect(ip, 65432):
            cliente.send("ELECTION", "New election")
            ip, _, tipo, mensaje = cliente.receive()
            print(mensaje)
            if mensaje[1] == "ok":
                thisNodeIsMaster = False
        del cliente

    if thisNodeIsMaster:
        print("Yo soy el nodo maestro")
        for ip in ipNodes:
            cliente = ClientSocket()
            if cliente.conect(ip, 65432):
                cliente.send("COORDINATOR", "New coordinator")
                _, timestamp, tipo, mensaje = cliente.receive()
        masterIP = localIP

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
            self.addr = host
            self.port = port
            self.sock.connect((host, port))
            return True
        except ConnectionRefusedError :
            print(f"Conection refused by ({host}, {port})")
            self.sock.close()
            return False

    def send(self, command, msg):
        totalsent = 0
        timestamp = time.time()
        timestamp = time.ctime(timestamp)
        msg = f"[{timestamp}][{command}][{msg}]"
        msglen = len(msg)
        msg = msg.encode()
        
        while totalsent < msglen:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
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

        mensaje = f"[{self.addr}]" + "".join(chunks)
        elementos =  re.findall(r'\[(.*?)\]', mensaje)
        return elementos[0], elementos[1], elementos[2], elementos[3]

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
        self.conn, self.addr = self.sock.accept()
        print(f"\nConnected by : {self.addr}")

    def send(self, command, msg):
        totalsent = 0
        timestamp = time.time()
        timestamp = time.ctime(timestamp)
        msg = f"[{timestamp}][{command}][{msg}]"
        msglen = len(msg)
        msg = msg.encode()

        while totalsent < msglen:
            sent = self.conn.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
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

        mensaje = f"[{self.addr}]" + "".join(chunks)
        elementos =  re.findall(r'\[(.*?)\]', mensaje)
        return elementos[0], elementos[1], elementos[2], elementos[3]

def miserver():

    servidor = ServerSocket()
    while True:
        servidor.accept()
        ip, timestamp, tipo, mensaje = servidor.receive()
        if tipo == "MENSAJE":
            print(mensaje)
            servidor.send("MENSAJE", "OK")
        elif tipo == "ELECTION":
            servidor.send("OK", "ok")
            print("Nueva eleccion de nodo maestro")
            electionMaster()
        elif tipo == "COORDINATOR":
            print(f"Nuevo coordinador con IP: {ip}")
            masterIP = ip
            servidor.send("OK", "ok")

        register = open("register.txt", "a+")
        register.write(f"[{ip}][{timestamp}][{tipo}][{mensaje}]\n")
        register.close()
    

if __name__ == "__main__":

    #Server thread

    t1 = threading.Thread(target=miserver)
    t1.start()

    while True:
        ipNodes = []
        i = 1
        print("Enviar mensaje a:")
        with open("nodes.txt", "r") as nodes:
            ipNodes  = [line.strip() for line in nodes.readlines()]
        

        for ip in ipNodes:
            print(f"{i}) {ip}")
            i += 1
        
        while True:
            option = input("Ingrese una opcion: ")
            try:
                option = int(option)
                if option > len(ipNodes):
                    print("Valor fuera de rango")
                else:
                    break
            except ValueError:
                if option != "":
                    print("Ingrese una opcioin valida")

        cliente = ClientSocket()

        if cliente.conect(ipNodes[option - 1], 65432):
            mensaje = input("Ingrese el mensaje: ")
            cliente.send("MENSAJE", mensaje)
            ip, timestamp, command, contenido = cliente.receive()

            print(f"La respuesta de: {ip} con timestamp: {timestamp} de tipo: {command} es: {mensaje}")
        else:
            print("No se logro conectar con el host")

    t1.join()
    register.close()


    #t1.join()
