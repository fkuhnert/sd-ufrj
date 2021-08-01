import socket

HOST = ''     # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

# cria um socket para comunicacao
sock = socket.socket() # valores default: socket.AF_INET, socket.SOCK_STREAM  

# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(5) 

# aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
novoSock = None
while True:
    # Se nenhuma conexão existe, estabelece uma nova
    if novoSock is None:
        novoSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
        print ('Conectado com: ', endereco)

    msg = novoSock.recv(1024).decode('utf-8')
    print(msg)
    if msg == "exit":
        novoSock.close()
        novoSock = None
        print (f"Conexão com {endereco} fechada")