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
    while True:
        msg = sock.recv(1024).decode("utf-8")
        if msg:
            print(f"Mensagem recebida: {msg}")

        # Quando o cliente encerra conexão, o loop deve ser interrompido
        if not msg:
            sock.close()
            print (f"Conexão com {address} fechada")
            return
        
        # Tratamento da mensagem
        else:
            # Separa a mensagem em arquivo a ser aberto e palavra a ser buscada
            arquivo, palavra = msg.split("/")
            print(f"Arquivo: {arquivo}")
            print(f"Palavra: {palavra}")

            # Print vazio para melhorar visibilidade
            print()

            try:
                total = 0
                file = open(arquivo, "r")
                print(f"Arquivo {arquivo} aberto corretamente.")

                # Para cada linha no arquivo, conta quantas vezes a palvra aparece na linha
                for line in file:
                    total += line.count(palavra)
                print(f"Encontrei a palavra {palavra} {total} vez(es).")
                
                # Transforma em texto e envia de volta ao cliente
                sock.send(str(total).encode("utf-8"))

            # Quando o arquivo não é encontrado, é disparada uma exceção
            except:
                print(f"Falha ao abrir o arquivo {arquivo}.")
                sock.send("erro ao abrir o arquivo".encode('utf-8'))
            print()

def main():
    entradas = [sys.stdin]
    sock = initserver()
    entradas.append(sock)
    addrlist = []       # Lista de conexões
    clientlist = []     # Lista de threads

    while True:
        # Se nenhuma conexão existe, utiliza select para realizar a próxima ação, podendo ser
        # do stdin ou uma conexão do socket
        r, _, _ = select.select(entradas, [], [])
        for ready in r:
            if ready == sock:
                novoSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
                print (f"Conectado com {endereco}")
                addrlist.append(endereco)

                # Cria uma thread, chamando a func. requestloop() com os args
                client = threading.Thread(target=requestloop, args=(novoSock, endereco))                
                client.start()              # Inicia a exec. da thread
                clientlist.append(client)   # Guarda a ref. da thread na lista de clientes

            else: # ready == sys.stdin
                cmd = input()
                # Caso o comando digitado seja "exit", encerra a exec. do servidor
                if cmd == "exit":
                    for c in clientlist:
                        c.join()            # Para cada thread, espera a thread encerrar
                    print("Encerrando execução.")
                    sock.close()
                    sys.exit()

                # Comando "list" mostra todas as conexões ativas e as antigas que já encerraram
                elif cmd == "list":
                    print("Lista de conexões passadas:")
                    for addr in addrlist:
                        print(addr)
main()