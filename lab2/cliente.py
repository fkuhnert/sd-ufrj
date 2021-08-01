import socket

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000       # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

print("Digite as mensagens a serem enviadas, ou digite \"exit\" para sair")
text = ""
while True:
    text = input("# ")
    if len(text):               # nao envia mensagem vazia
        sock.send(text.encode(encoding='utf-8'))
    if text == "exit": break
sock.close() 
