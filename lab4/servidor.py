# Alunos:
# Felipe Ventura Kuhnert - DRE 117059590
# Pedro Novaes Possato - DRE 117053803

import socket
import select
import sys
import threading
import queue

HOST = ''     # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

def initserver():
    # cria um socket para comunicacao
    sock = socket.socket() # valores default: socket.AF_INET, socket.SOCK_STREAM  
    # vincula a interface e porta para comunicacao
    sock.bind((HOST, PORTA))
    # define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
    sock.listen(5)
    return sock

def requestloop(sock, address):
        username = sock.recv(1024).decode("utf-8")  # Cliente precisa indicar seu username ao servidor
        if not username:
            sock.close()
            return

        if username not in connected_users:
            sock.send("username_ok".encode("utf-8"))            # Username disponível
            new_queue = queue.Queue()                           # Cria fila interna
            connected_users[username] = {"status": "active", "queue": new_queue, "address": address}   # Atualiza mapa de users conectados
        else:   # Username indisponível
                print (f"Endereço {address} tentou se conectar mas o username \"{username}\" estava indisponível")
                sock.send("username_unavailable".encode("utf-8"))
                sock.close()
                return

        while True:
            if not new_queue.empty():
                msg_content = new_queue.get()
                print(f"Enviei \"{msg_content}\" ao {username}")
                sock.send(msg_content.encode('utf-8'))
            else:
                r, _, _ = select.select([sock], [], [], 0.2)
                for ready in r:
                    msg = ready.recv(1024).decode("utf-8")
                    if not msg: # Cliente usou /quit
                        sock.close()
                        print (f"Conexão com {address} fechada")
                        del connected_users[username]
                        print (f"Mapa do user \"{username}\" apagado com sucesso")
                        return # Quando o cliente encerra conexão, o loop deve ser interrompido

                    # Tratamento da mensagem
                    else:
                        # Separa a mensagem em arquivo a ser aberto e palavra a ser buscada
                        if msg == "/offline":
                            connected_users[username]["queue"].queue.clear()
                            connected_users[username]["status"] = "inactive"

                        elif msg == "/online":
                            connected_users[username]["status"] = "active"

                        elif msg == "/list":
                            ready.send(",".join(connected_users.keys()).encode('utf-8'))

                        elif msg[0] == ">":
                            dest, msg_content = msg[1:].split("-", 1)           # Separa username e mensagem
                            print(f"{username}->{dest}: {msg_content}")

                            if dest in connected_users and connected_users[dest]["status"] == "active":
                                connected_users[dest]["queue"].put(f"<{username}: {msg_content}")
                                ready.send("msg_ok".encode('utf-8'))            # Dá o ok ao cliente

                            else:
                                ready.send("user_unavailable".encode('utf-8'))  # Caso destinatário esteja inativo ou não exista, retorna falha


def main():
    entradas = [sys.stdin]
    sock = initserver()
    entradas.append(sock)
    global connected_users
    connected_users = dict()    # Lista de clientes
    thread_list = []            # Lista de threads

    while True:
        # Se nenhuma conexão existe, utiliza select para realizar a próxima ação, podendo ser
        # do stdin ou uma conexão do socket
        r, _, _ = select.select(entradas, [], [])
        for ready in r:
            if ready == sock:
                novoSock, endereco = sock.accept()              # Retorna um novo socket e o endereco do par conectado
                print (f"Conectado com {endereco}")

                # Cria uma thread, chamando a func. requestloop() com os args
                client = threading.Thread(target=requestloop, args=(novoSock, endereco))                
                client.start()                  # Inicia a exec. da thread
                thread_list.append(client)      # Guarda a ref. da thread na lista de clientes

            else: # ready == sys.stdin
                cmd = input()
                # Caso o comando digitado seja "exit", encerra a exec. do servidor

                if cmd == "exit":
                    for c in thread_list:
                        c.join()            # Para cada thread, espera a thread encerrar
                    print("Encerrando execução.")
                    sock.close()
                    sys.exit()

                if cmd == "list":
                    for user in connected_users:
                        print(f"{user}: {connected_users[user]}")
main()