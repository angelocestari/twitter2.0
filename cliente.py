# Bibliotecas

from socket import *

# Código principal
id = input('Id de usuário: ')
nome_de_usuário = input('Nome de usuário: ')
ip = input('Endereço de IP: ')
porta = input('Porta utilizada: ')
timeout = 1

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.settimeout(timeout)

porta = int(porta)

data = f'0 {id} 0 0 {nome_de_usuário}'

try:
    serverSocket.sendto(data.encode(), (ip, porta))
    message = serverSocket.recvfrom(1024)
    print(message)

except:
    print('ERRROOOO!')

serverSocket.close()
