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
novoSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
print ('Conectado com: ', endereco)

while True:
	msg = novoSock.recv(1024)
	if not msg: break 
	else:
		print(f"Recebi do ativo: {str(msg, encoding='utf-8')}")
		novoSock.send(msg) # envia a mensagem que acabou de receber de volta
		print("Ecoei a mensagem de volta ao ativo")

# fecha o socket da conexao
novoSock.close() 
# fecha o socket principal
sock.close() 
print("Conexões foram encerradas. Terminando execução.")