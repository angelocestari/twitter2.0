import socket
import threading
import time

#Prepara o endereço do servidor que será usado
server_address = socket.gethostbyname(socket.gethostname())
port = 12000
print(f"Endereço do servidor: {server_address}:{port}")

#Prepara os sockets do servidor
serverSocket = socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', port))

clientes_ativos = {}

def resposta_servidor(mensagem, endereco_cliente):
    
    #Particiona a mensagem para tratamento dos dados
    partes_mensagem = mensagem.split(' ')
    contem_texto = 0
    if len(partes_mensagem) > 4:
        contem_texto = 1

    if partes_mensagem[0] == '0':
        if not clientes_ativos[partes_mensagem[1]]:
            serverSocket.sendto(mensagem.encode(), endereco_cliente)
            clientes_ativos[partes_mensagem[1]] = endereco_cliente
        else:
            texto = f"Id {partes_mensagem[1]} indisponivel"
            mensagem = f'3 0 {len(texto)} {texto}'

    elif partes_mensagem[0] == '1':
        del clientes_ativos[partes_mensagem[1]]
    

while True:
    #Espera receber uma mensagem
    mensagem, endereco_cliente = serverSocket.recvfrom(1024)

    

    

