import socket
import threading
import time

#Prepara o endereço do servidor que será usado
server_address = socket.gethostbyname(socket.gethostname())
port = 12000
print(f"Endereço do servidor: {server_address}:{port}")

#Prepara os sockets do servidor
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serverSocket.bind(('', port))

clientes_ativos = {}

def resposta_servidor(mensagem, endereco_cliente):
    
    #Particiona a mensagem para tratamento dos dados
    partes_mensagem = mensagem.split(' ')
    contem_texto = 0
    if len(partes_mensagem) > 5:
        contem_texto = 1

    if partes_mensagem[0] == '0':
        #Id disponível
        if partes_mensagem[1] not in clientes_ativos and partes_mensagem[1] != '0':
            serverSocket.sendto(mensagem.encode(), endereco_cliente)
            clientes_ativos[partes_mensagem[1]] = endereco_cliente
        #Erro: Id indisponível
        else:
            texto = f"Id {partes_mensagem[1]} indisponivel"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} {texto}'

    elif partes_mensagem[0] == '1':
        #Apaga registro do cliente
        del clientes_ativos[partes_mensagem[1]]

    elif partes_mensagem[0] == '2':
        texto = ""
        if contem_texto:
            texto = mensagem[5:]
            texto = ' '.join(texto)
            texto = texto[:min(int(partes_mensagem[3]),140)]
        
        clientes = {}
        if partes_mensagem[2] == '0':
            clientes = clientes_ativos
        else:
            clientes[partes_mensagem[2]] = clientes_ativos[partes_mensagem[2]]
        for id, cliente in clientes.items():
            mensagem = f"2 {partes_mensagem[1]} {id} {len(texto)} {texto}"
            serverSocket.sendto(mensagem.encode(), cliente)
    else:
        texto = f"Mensagem enviada nao definida"
        mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} {texto}'     

while True:
    #Espera receber uma mensagem
    mensagem, endereco_cliente = serverSocket.recvfrom(1024)

    #responde a Mensagem
    resposta_servidor(mensagem.decode(), endereco_cliente)

    

    

