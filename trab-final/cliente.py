import socket
import select
import sys
import json
from shutil import get_terminal_size
from datetime import datetime
from math import ceil, floor

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5001       # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA))
print(f"Conectado com {HOST}:{PORTA}")

entradas = [sys.stdin, sock]
while True:
    r, _, _ = select.select(entradas, [], [], 0.5)
    for ready in r:
        if ready == sock:
            msgs = ready.recv(1024).decode("utf-8").split("\r\n\r\n") # Separa mensagens baseado no CRLFCRLF
            now = datetime.now()
            for msg in msgs:
                if len(msg):
                    if msg[0] == "{":
                        # Noticia com JSON
                        info = json.loads(msg)

                        width, _ = get_terminal_size()     #Tamanhos do terminal para formatação
                        
                        counter = 0
                        for label in info:
                            tam = ((width - (len(label)+4))/2)
                            size = width-4
                            if counter == 0:
                                print(f'┏{"━"*(floor(tam))} {label} {"━"*ceil(tam)}┓')
                            else:
                                print(f'┣{"━"*(floor(tam))} {label} {"━"*ceil(tam)}┫')
                            iterations = ceil(len(info[label])/size)
                            for i in range(iterations):
                                sliced_msg = info[label][size*i:size*(i+1)]
                                print(f"┃ {sliced_msg.strip()}{' '*(size-len(sliced_msg.strip()))} ┃")
                            counter += 1
                        print(f'┗{"━"*(width-2)}┛')
                        print()
                    else:
                        print(msg)

        elif ready == sys.stdin:
            cmd = input()
            if not len(cmd): continue

            # Comando que lista tópicos
            if cmd == "/list":
                sock.send("/list".encode("utf-8"))
                print("Lista de tópicos disponíveis:")
                topic_list = sock.recv(1024).decode("utf-8")
                print(topic_list)

            # Comando para encerrar execução
            elif cmd == "/quit":
                sock.close()
                sys.exit()

            # Comando para listar comandos disponíveis
            elif cmd == "/help":
                print("Comandos disponíveis:")
                print("/list, /quit, /help, >topic msg, +topic, -topic")

            # Publicar mensagem em tópico
            elif cmd[0] == ">":
                if " " not in cmd:
                    print("Você deve inserir uma mensagem após o nome do tópico.")
                    continue

                sock.send(cmd.replace(" ", "-", 1).encode("utf-8"))

            elif cmd[0] == "+" or cmd[0] == "-":
                name = cmd[1:]
                if len(name):
                    sock.send(cmd.encode('utf-8'))
                else:
                    print("Você deve escrever o nome do tópico após o +/-")