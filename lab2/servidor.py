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
        print (f"Conectado com {endereco}")

    msg = novoSock.recv(1024).decode("utf-8")
    if msg:
        print(f"Mensagem recebida: {msg}")

    # Quando o cliente encerra conexão, o loop deve ser interrompido
    if not msg:
        novoSock.close()
        novoSock = None
        print (f"Conexão com {endereco} fechada")
        continue

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
        novoSock.send(str(total).encode("utf-8"))

    # Quando o arquivo não é encontrado, é disparada uma exceção
    except:
        print(f"Falha ao abrir o arquivo {arquivo}.")
        novoSock.send("erro ao abrir o arquivo".encode('utf-8'))
    print()