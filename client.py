import socket, sys, os, time, threading
from queue import Queue
ENCODING = 'UTF-8'

host = "10.101.126.186" #sys.argv[1]
port = 50000 #sys.argv[2]

s = socket.socket()
s.bind((host, port))
s.listen(5)
print("En attente du client...")

conn, addr = s.accept()

print("Client : %s" %(str(addr[0])))

while True:
    command = input("#>")
    if command != "exit()":
        if command == "":
            continue

        conn.send(command.encode(ENCODING))
        result = conn.recv(1024).decode(ENCODING)
        total_size = len(result[:16])
        result = result[16:]

        while total_size > len(result):
            data = conn.recv(1024)
            result += data
        print(result)
        print("\n")

    else:
        conn.send("exit()")
        print("Connexion fermée")
        break

s.close()


