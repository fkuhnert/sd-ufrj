import socket
import select
import sys

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000       # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA))

user_ok = False
while not user_ok:
    username = input("Insira o seu username: ")
    if not len(username): continue
    if " " in username or "-" in username:
        print("Username não pode conter espaços ou hífens. Tente novamente.")
        continue
    sock.send(username.encode("utf-8"))
    result = sock.recv(1024).decode("utf-8")
    if result == "username_ok":
        print("Conectado com sucesso.")
        user_ok = True
    else:
        print("Username já está em uso. Tente novamente.")

entradas = [sys.stdin, sock]
status = "active"
while True:
    r, _, _ = select.select(entradas, [], [], 0.5)
    for ready in r:
        if ready == sock:
            msg = ready.recv(1024).decode("utf-8")
            print(msg)
        elif ready == sys.stdin: # stdin
            cmd = input()
            if not len(cmd): continue

            # Comando que lista usuários
            if cmd == "/list":
                sock.send("/list".encode("utf-8"))
                user_list = sock.recv(1024).decode("utf-8")
                print(user_list)

            # Comando para ficar inativo
            elif cmd == "/offline":
                sock.send("/offline".encode("utf-8"))
                status = "inactive"

            # Comando para ficar ativo
            elif cmd == "/online":
                sock.send("/online".encode("utf-8"))
                status = "active"

            elif cmd == "/quit":
                sock.close()
                sys.exit()

            elif cmd[0] == ">" and status == "active":
                sock.send(cmd.replace(" ", "-", 1).encode("utf-8"))
                result = sock.recv(1024).decode("utf-8")
                if result != "msg_ok":
                    print(f"Erro: {result}")
                    print("Usuário não está disponível ou não existe")
            elif cmd[0] == ">" and status == "inactive":
                print("Você não pode enviar mensagens enquanto estiver inativo.")
