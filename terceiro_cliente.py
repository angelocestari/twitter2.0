# Bibliotecas

from socket import *

# Código principal
id = 3
nome_de_usuário = 'teste'
ip = '192.168.15.12'
porta = 12000
timeout = 61

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.settimeout(timeout)

porta = int(porta)

data = f'4 {id} 0 0 {nome_de_usuário}'

# try:
serverSocket.sendto(data.encode(), (ip, porta))
message, endereco = serverSocket.recvfrom(1024)
print(message)


# data = f'2 {id} 1 11 {nome_de_usuário} salve salve'
# serverSocket.sendto(data.encode(), (ip, porta))

# data = f'2 {id} 0 17 {nome_de_usuário} salve salve geral'
# serverSocket.sendto(data.encode(), (ip, porta))

# message, endereco = serverSocket.recvfrom(1024)
# print(message)

# data = f'1 {id} 0 0 {nome_de_usuário}'
# serverSocket.sendto(data.encode(), (ip, porta))

# data = f'0 {3} 0 0 {nome_de_usuário}'

# # try:
# serverSocket.sendto(data.encode(), (ip, porta))

# except:
#     print('ERRROOOO!')

# serverSocket.close()
