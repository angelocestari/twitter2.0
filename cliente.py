# Bibliotecas

from socket import *

# Funções

def limited_userId_input(prompt):
    user_input = int(input(prompt))
    while user_input < 1 or user_input > 999:
        print(f'Entrada inválida! Intervalo de ids entre 1 e 999 ')
        user_input = int(input(prompt))
    return user_input

def limited_username_input(prompt, max_length):
    user_input = input(prompt).strip()
    while len(user_input) > max_length or '' in user_input:
        print(f"Entrada inválida! Máximo de {max_length} caracteres permitidos e sem espaços.")
        user_input = input(prompt).strip()
    return user_input


# Código principal
id = limited_userId_input("Digite seu id (Entre 1 e 999) ")
nome_de_usuário = limited_username_input("Digite o seu nome de usuário (Max: 20 caracteres):", 20)
ip = input('Endereço de IP: ')
porta = input('Porta utilizada: ')
timeout = 1

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.settimeout(timeout)

porta = int(porta)

# Criando conexão
data = f'0 {id} 0 0 {nome_de_usuário}' 

try:
    serverSocket.sendto(data.encode(), (ip, porta))
    message = serverSocket.recvfrom(1024)
    print(message)

except:
    print('ERRROOOO!')

serverSocket.close()
