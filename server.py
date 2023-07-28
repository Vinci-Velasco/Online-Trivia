import socket
import threading
import time
import pickle
from queue import Queue
# from src.player import Player

HOST = "127.0.0.1"
PORT = 7070

NUM_PLAYERS = 5

min_players = 3
max_players = 5

player_list = []

# Thread that deals with listening to clients
def listening_thread(client_socket, addr, message_queue):
    BUFFER_SIZE = 1024 # change size when needed
    with client_socket:
        while True:
            message = client_socket.recv(BUFFER_SIZE).decode("utf8")
            
            print(f"Recieved message from {addr}")
            # receive a ping
            if message == "ping":
                    client_socket.send("pong".encode('utf-8'))
            else:
                message_queue.put((message, addr))
            # client_socket.send("Server acknowledges your message\n".encode())
         
# Custom thread class that creates new threads once connections come in
class Recieve_Connection_Thread(threading.Thread):
    def __init__(self, server, message_queue):
        super().__init__()
        self.server = server
        self.message_queue = message_queue
        self.stop_connections = False

    # Listens to connections and creates new threads. Closes once max connections achieved
    # or stop_connections is set to True (via the stop() method)
    def run(self):
        connections = 0
        MAX_CONNECTIONS = 5

        while connections < MAX_CONNECTIONS:
            print(f"Listening for connections ({connections}/{MAX_CONNECTIONS})...")
            client_socket, addr = self.server.accept()

            # terminate thread if stop_connections set to True
            if self.stop_connections:
                break

            # otherwise create new thread for connection
            client_sockets.append(client_socket)
            client_addrs.append(addr)
            thread = threading.Thread(
                target=listening_thread, args=(client_socket, addr, self.message_queue))
            thread.start()
            connections += 1

           # add a new Player object with this client's ID to global player list
            global player_list
            client_id = connections
            p = Player(client_id, client_socket, addr)
            player_list.append(p)

            PlayerNumber[addr] =  client_id, client_socket

            # client_socket.send(f"Connection to server established. You're Player #{connections}\n".encode("utf8"))

            # for client_socket in client_sockets:
               
            #     client_socket.send(str(f"Players: {client_addrs} are in the lobby!\n").encode("utf8"))


        print(f"Done with connections ({connections}/{MAX_CONNECTIONS})")


    # Stop the thread by changing the stop_connections cond to True and unblocking the
    # server.accept() call. This is safer than killing the thread as it can terminate properly
    def stop(self):
        self.stop_connections = True
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((HOST, PORT))

class Player():
    def __init__(self, id, socket, addr):
        self.id = id
        self.socket = socket
        self.addr = addr

        # initial instance values
        self.votes = 0
        self.score = 0
        self.is_host = False
        self.already_voted = False

def find_player(id): # return a player from player_list based on ID
    for p in player_list:
        if p.id == id:
            return p

def allPlayersReady(ready_clients):
    index = 0
    proceedOrNot = True

    for allClients in client_sockets:
           
        if(ready_clients[index] == False):


            for client in client_sockets:
                # send data to all clients
               
                #commented out until a solution for slowing down the rate of sending is found
                #client.send(str(f"Waiting on Player {index + 1} to ready up!\n").encode("utf8"))
                proceedOrNot = False
               
        index += 1
    return proceedOrNot


#Token functions------USE if needed-------------------------------------------------------------------------------
def send_to_player(player, msg):
    player.socket.send(str(msg).encode('utf8'))

    # TODO: add ACK?

def readyUp(ready_clients, PlayerNumber, client_sockets):
    ready_clients[PlayerNumber-1] = True
    client_sockets[PlayerNumber-1].send("Server Acknowlegdes Ready Up\n".encode("utf8"))

    return ready_clients


def hostChoice():
    pass


def voteHost():
    pass


def answer():
    pass


def buzzing():
    pass


#Token functions-------------------------------------------------------------------------------------

if __name__ == "__main__":
    # setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM = TCP
    server.bind((HOST, PORT))
    server.listen()


    # data structures to hold client sockets and message queue so main can communicate
    # with listening threads and vice versa
    client_sockets = []
    client_addrs = []
    PlayerNumber = {}


    ready_clients = [False, False, False, False, False]
    message_queue = Queue() # locks are already built in to Queue class
    recieve_connections_thread = Recieve_Connection_Thread(server, message_queue)
    recieve_connections_thread.start()

    #### Lobby loop ------------------------------------------------------------------
    host_voted = False
    all_ready = False
    while not (all_ready and host_voted):
        #gets the message and its coresponding sender adderess
        message, addr = message_queue.get()    
        print(message)

        #### Information about the Sender
        sender_id = PlayerNumber[addr][0]
        sender = find_player(sender_id)

        #### Internal States
        total_num_votes = 0
        vote_counter = [0] * NUM_PLAYERS

        # application layer protocol for lobby (parse tokens)
   
        #Token Parse
        #splitMessage[1] should be the data
        tokens = message.split('-')

        #### Handle Requests for Data from client
        if (tokens[0] == "Req_Data"):
            if tokens[1] == "player_ids": # send list of online player IDs
                player_ids = []
                for p in player_list:
                    player_ids.append(p.id)
                data = pickle.dumps(player_ids) # serialize python list with pickle
                send_to_player(sender, data)

            elif tokens[1] == "my_id": # send player's own id
                send_to_player(sender, sender_id)
                
        elif (tokens[0] == "Vote_Host"):
            P_ID = tokens[1]
            vote_ID = tokens[2]


            ## TODO: check if P_ID is valid (player exists)
            # voted_clients[P_ID] = True
            # host_votes[vote_ID] += 1


        # TODO: when all players have finished voting, calculate final Host_choice and send to client
        # then set Player(Host_Choice).isHost = True  


        elif (tokens[0] == "Ready_Up"):
            ready_Clients = readyUp(ready_clients, PlayerNumber[addr][0], client_sockets)
           
    #Token Parse------------------------------------------------------------------


        all_ready = allPlayersReady(ready_clients)
        # If all players are ready move on to the main game loop
        if all_ready == True:
 
            break

    # close ability to connect
    recieve_connections_thread.stop()
    recieve_connections_thread.join()


    # send info to clients that main game has started
    # ...


    # main game loop
    game_loop = True
    while game_loop:
        message, addr = message_queue.get()
        print(message)


         # application layer protocol for game loop (parse tokens)
         # ...


        tokens = message.split('-')


       #Token Parse------------------------------------------------------------------


        if (tokens[0] == "Buzzing"):
               pass


        elif (tokens[0] == "Host_Choice"):
            pass
        elif (tokens[0] == "Answer"):
            pass


        #Token Parse------------------------------------------------------------------