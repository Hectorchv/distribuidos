import socket

def getLocalIP():
    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return(s.getsockname()[0])
    except Exception as e:
        print(e)
        return None
    finally:
        s.close()

if __name__ == "__main__":
    localIP = getLocalIP()
    print(localIP)