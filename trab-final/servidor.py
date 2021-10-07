# Alunos:
# Felipe Ventura Kuhnert - DRE 117059590
# Pedro Novaes Possato - DRE 117053803

import socket
import select
import sys
import threading

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
        my_topics = {}

        while True:
            for name in my_topics:
                # Loop de envio de mensagens; para cada tópico,
                # envia todas as mensagens que ainda não foram enviadas
                if my_topics[name] < (tam := len(topic_lists[name])):
                    while my_topics[name] < tam:
                        my_topics[name] += 1
                        content = topic_lists[name][my_topics[name]-1] 
                        sock.send((content + "\r\n\r\n").encode('utf-8')) # CRLFCRLF para terminar mensagem
                        print(f'Enviei "{content}" a {address}')

            r, _, _ = select.select([sock], [], [], 0.2)
            for ready in r:
                msg = ready.recv(1024).decode("utf-8")
                if not msg: # Cliente usou /quit
                    sock.close()
                    print(f"Conexão com {address} fechada")
                    user_list.remove(str(address))
                    return # Quando o cliente encerra conexão, o loop deve ser interrompido

                # Tratamento da mensagem
                else:
                    if msg == "/list":
                        # Lista todos os tópicos ao cliente
                        ready.send(
                            ", ".join(list(topic_lists.keys())).encode('utf-8')
                        )
                        print(f'Listei todos os tópicos para o cliente {address}')

                    elif msg[0] == ">":
                        # Publicar em tópico
                        name, content = msg[1:].split("-", 1)
                        print(f'{address} enviou mensagem com conteúdo: {content}')
                        if name in topic_lists:
                            topic_lists[name].append(content)
                        else:
                            # Caso o tópico não exista ainda, o cria
                            print(f'{address} criou novo tópico com nome "{name}"')
                            topic_lists[name] = [content]

                    elif msg[0] == "+":
                        # Se inscrever em tópico
                        name = msg[1:]
                        if name not in my_topics:   # Cria contador de mensagens caso não existir
                            my_topics[name] = 0
                            print(f'{address} se inscreveu no tópico {name}')
                        if name not in topic_lists: # Cria tópico caso tópico não exista
                            topic_lists[name] = []
                            print(f'{address} criou novo tópico com nome "{name}"')
                    
                    elif msg[0] == "-":
                        # Se desinscrever em tópico
                        name = msg[1:]
                        if name in my_topics:
                            del my_topics[name]
                            print(f'{address} se deinscreveu no tópico {name}')

def main():
    entradas = [sys.stdin]
    sock = initserver()
    entradas.append(sock)
    global topic_lists
    topic_lists = {}           # Lista de tópicos
    global user_list
    user_list = []             # Lista de usuários conectados 
    thread_list = []           # Lista de threads

    while True:
        # Se nenhuma conexão existe, utiliza select para realizar a próxima ação, podendo ser
        # do stdin ou uma conexão do socket
        r, _, _ = select.select(entradas, [], [])
        for ready in r:
            if ready == sock:
                novoSock, endereco = sock.accept()    # Retorna um novo socket e o endereco do par conectado
                print (f"Conectado com {endereco}")
                user_list.append(str(endereco))

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
                    print(", ".join(user_list))

                if cmd == "topics":
                    print(", ".join(topic_lists.keys()))

                if cmd[:9] == "broadcast":
                    _, message = cmd.split(" ", 1)
                    print("Realizando broadcast de mensagem a todos os tópicos.")
                    for name in topic_lists:
                        topic_lists[name].append("SERVER:" + message)

                # Mostra no console todas as mensagens de um tópico
                if cmd[:5] == "print":
                    _, name = cmd.split(" ", 1)
                    for message in topic_lists[name]:
                        print(message)
main()