import socket
import threading
import logging
import sys
from p2pfl.node_connection import NodeConnection
from p2pfl.pinger import Pinger

#XQ SOCKETS? -> received at any time (async)

#Si fuese pa montar una red distribuida elixir de 1

# https://github.com/GianisTsol/python-p2p/blob/master/pythonp2p/node.py

# socket.sendall is a high-level Python-only method



BUFFER_SIZE = 1024
HI_MSG = "hola"
SUCCES_MSG = b"pecfect"

"""
from p2pfl.node import Node

n1 = Node("localhost",6777)
n1.start()

from p2pfl.node import Node

n2 = Node("localhost",6778)
n2.start()
n2.connect_to("localhost",6777)
"""
#que extienda de thread?
class Node(threading.Thread):
    def __init__(self, host, port):

        threading.Thread.__init__(self)

        self.terminate_flag = threading.Event()
        self.host = host
        self.port = port

        # Setting Up Node Socket (listening)
        self.node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        #self.node_socket.settimeout(0.2)
        self.node_socket.bind((host, port))
        
        self.node_socket.listen(5)# no mas de 5 peticones a la cola

        # Neightboors
        self.neightboors = []

        #Loggin ? por ver
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

        self.pinger = Pinger(self)
        self.pinger.start()


    def get_addr(self):
        return self.host,self.port

    #Objetivo: Agregar vecinos a la lista -> CREAR POSIBLES SOCKETS 
    def run(self):
        logging.info('Nodo a la escucha en {} {}'.format(self.host, self.port))
        while not self.terminate_flag.is_set(): 
            try:
                (node_socket, (h,p)) = self.node_socket.accept()
                
                # MSG
                msg = node_socket.recv(BUFFER_SIZE).decode("UTF-8")
                splited = msg.split("\n")
                head = splited[0]
                rest = "\n".join(splited[1:])
                print(str(self.get_addr()) + "|" + head + "|" + rest + "|")
                
                #
                # EL HI SERÁ en un futuro la encriptación
                #
                if head == HI_MSG:
                    logging.info('Conexión aceptada con {}:{}'.format(h,p))

                    #
                    # CHECKEAR SI NODO YA ESTÁ EN LA LISTA
                    #
                    #node_socket.sendall(SUCCES_MSG)
                    nc = NodeConnection(self,node_socket,rest,(h,p))
                    nc.start()
                    self.add_neighbor(nc)

                else:
                    logging.info('Conexión rechazada con {}:{}'.format(h,p))
                    node_socket.close()
           
            except Exception as e:
                #revisar excepciones de timeout y configurarlas
                print(e)

        #Detenemos nodo
        #self.pinger.stop()
        print("nos vamos")
        logging.info('Dejando de escuchar en {} {}'.format(self.host, self.port))
        for n in self.neightboors:
            n.stop()
        self.node_socket.close()

    def stop(self): 
        self.terminate_flag.set()
        # Enviamos mensaje al loop para evitar la espera del recv
        try:
            self.send(self.host,self.port,b"")
        except:
            pass

    def send(self, h, p, data, persist=False): 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  
        s.settimeout(10000000)
        s.connect((h, p))
        s.sendall(data) #SEND ALL?? QUE DIFERENCIA CON SEND??
        if persist:
            return s
        else:
            print("se cierra en el send")
            s.close()
            return None

    #Seguramente tenga que cambiarlo en futuro x si los nodos tienen listas finitas
    def connect_to(self, h, p): 
        msg=(HI_MSG + "\n").encode("utf-8")
        s = self.send(h,p,msg,persist=True)

        #Checkear de alguna forma la respuesta
        print((h,p))
        nc = NodeConnection(self,s,"",(h,p))
        nc.start()
        self.add_neighbor(nc)

    def broadcast(self, msg, exc=None):
        for n in self.neightboors:
            if n != exc:
                n.send(msg)

    #############################
    #  Neighborhood management  #
    #############################

    def get_neighbors(self):pass
    def add_neighbor(self, n):
        self.neightboors.append(n)

    def rm_neighbor(self,n):
        try:
            self.neightboors.remove(n)
        except:
            pass
  