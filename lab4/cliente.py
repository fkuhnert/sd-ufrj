import socket

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000       # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

while True:
    arquivo = ""
    # Não permite o usuário de tentar enviar uma string vazia
    while arquivo == "":
        arquivo = input("Digite o nome do arquivo de texto (ou \"exit\" para sair): ")
    
    palavra = ""
    if arquivo != "exit":
        while palavra == "":
            palavra = input("Digite a palavra a ser buscada: ")
        print() # Print vazio para melhorar visibilidade
    
    # Se o nome do arquivo for "exit", fecha a conexão e encerra o programa
    if arquivo == "exit":
        sock.close()
        break

    else:
        # Envio da mensagem ao servidor
        mensagem = f"{arquivo}/{palavra}".encode('utf-8')
        sock.send(mensagem)

        # Recebimento da resposta do servidor
        response = sock.recv(1024).decode('utf-8')

        # Tratamento e exibição da mensagem ao usuário
        if "erro" in response:
            print("O arquivo solicitado não foi encontrado no servidor.")
        else:
            vez_str = "vez" if int(response) == 1 else "vezes"
            print(f"A palavra \"{palavra}\" foi encontrada {response} {vez_str}.")
        print()