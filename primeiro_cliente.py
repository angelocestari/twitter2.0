# Bibliotecas

from socket import *

# Código principal
id = 1
nome_de_usuário = "teste"
ip = '192.168.15.12'
porta = 12000
timeout = 10

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.settimeout(timeout)

porta = int(porta)

data = f'0 {id} 0 0 {nome_de_usuário}'

try:
    #Manda OI
    serverSocket.sendto(data.encode(), (ip, porta))
    message, endereco = serverSocket.recvfrom(1024)
    print(message)

    # #Espera mensagem
    # message, endereco = serverSocket.recvfrom(1024)
    # print(message)

    # message, endereco = serverSocket.recvfrom(1024)
    # print(message)

    # #Manda TCHAU
    # data = f'1 {id} 0 0 {nome_de_usuário}'
    # serverSocket.sendto(data.encode(), (ip, porta))



except:
    print('ERRROOOO!')

serverSocket.close()
