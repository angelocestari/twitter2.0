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

    if len(partes_mensagem) < 5:
        #Retorna erro de mensagem inválida
        texto = f"Mensagem sem a quantidade minima de campos"
        mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
        serverSocket.sendto(mensagem.encode(), endereco_cliente)

        return

    contem_texto = 0
    if len(partes_mensagem) > 5 and partes_mensagem[4] != '0':
        contem_texto = 1

    if partes_mensagem[0] == '0':
        if not (partes_mensagem[1] in clientes_ativos) and partes_mensagem[1] != '0':
            #Id disponível, responde e salva
            serverSocket.sendto(mensagem.encode(), endereco_cliente)
            clientes_ativos[partes_mensagem[1]] = endereco_cliente
        else:
            #Erro: Id indisponível, somente responde
            texto = f"Id {partes_mensagem[1]} indisponivel"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'

            serverSocket.sendto(mensagem.encode(), endereco_cliente)

    elif partes_mensagem[0] == '1':
        #Apaga registro do cliente
        del clientes_ativos[partes_mensagem[1]]

    elif partes_mensagem[0] == '2':
        texto = ""
        nome_origem = partes_mensagem[4] 
        if contem_texto:
            texto = partes_mensagem[5:]
            texto = ' '.join(texto)
            texto = texto[:min(int(partes_mensagem[3]),140)]
        
        clientes_destino = {}
        if partes_mensagem[2] == '0':
            #Envia para todos os clientes
            clientes_destino = clientes_ativos
        else:
            #Enviar somente para um cliente especificado
            clientes_destino[partes_mensagem[2]] = clientes_ativos[partes_mensagem[2]]

        for id, cliente in clientes_destino.items():
            mensagem = f"2 {partes_mensagem[1]} {id} {len(texto)} {nome_origem} {texto}"
            serverSocket.sendto(mensagem.encode(), cliente)
    else:
        texto = f"Mensagem enviada nao definida"
        mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'

    print(clientes_ativos)

while True:
    #Espera receber uma mensagem
    mensagem, endereco_cliente = serverSocket.recvfrom(1024)

    #responde a mensagem
    resposta_servidor(mensagem.decode(), endereco_cliente)

    

    

