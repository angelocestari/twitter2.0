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

def resposta_servidor(mensagem_cliente, endereco_cliente, copia_clientes_ativos):

    #Decodifica a mensagem recebida
    mensagem = mensagem_cliente.decode()

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
        if partes_mensagem[1] != '0' and not(partes_mensagem[1] in clientes_ativos):
            #Id disponível, responde e salva
            clientes_ativos[partes_mensagem[1]] = endereco_cliente
            serverSocket.sendto(mensagem.encode(), endereco_cliente)
        else:
            #Erro: Id indisponível, somente responde
            texto = f"Id {partes_mensagem[1]} indisponivel"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'

            serverSocket.sendto(mensagem.encode(), endereco_cliente)

    elif partes_mensagem[0] == '1':
        #Apaga registro do cliente
        del clientes_ativos[partes_mensagem[1]]

    elif partes_mensagem[0] == '2':

        #Destino registrado
        if partes_mensagem[2] in copia_clientes_ativos:
            texto = ""
            nome_origem = partes_mensagem[4] 
            if contem_texto:
                texto = partes_mensagem[5:]
                texto = ' '.join(texto)
                texto = texto[:min(int(partes_mensagem[3]),140)]

            clientes_destino = {}
            if partes_mensagem[2] == '0':
                #Envia para todos os clientes
                clientes_destino = copia_clientes_ativos
            else:
                #Enviar somente para um cliente especificado
                clientes_destino[partes_mensagem[2]] = copia_clientes_ativos[partes_mensagem[2]]

            for id, cliente in clientes_destino.items():
                mensagem = f"2 {partes_mensagem[1]} {id} {len(texto)} {nome_origem} {texto}"
                serverSocket.sendto(mensagem.encode(), cliente)
        
        #Destino não registrado
        else:
            texto = "Destino da mensagem nao registrado"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
            serverSocket.sendto(mensagem.encode(), endereco_cliente)

    else:
        texto = f"Mensagem enviada nao definida"
        mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'

    # print(copia_clientes_ativos)

def verifica_desconecta(mensagem_cliente, endereco_cliente):

    #Decodifica a mensagem
    mensagem = mensagem_cliente.decode()

    #Quebra a mensagem para tratamento
    partes_mensagem = mensagem.split(' ')

    if len(partes_mensagem) > 1 and partes_mensagem[1] in clientes_ativos and clientes_ativos[partes_mensagem[1]] == endereco_cliente:
        del clientes_ativos[partes_mensagem[1]]


while True:
    try:
        #Espera receber uma mensagem
        mensagem, endereco = serverSocket.recvfrom(1024)

        #Copia lista de clientes para evitar conflitos de thread
        copia_clientes_ativos = clientes_ativos.copy()

        #Cria thread para responder a mensagem
        threading.Thread(target=resposta_servidor,
            args=(mensagem,endereco,copia_clientes_ativos)
        ).start()
    except ConnectionResetError:
        print(f"Conexão com {mensagem} cortada subtamente")
        verifica_desconecta(mensagem,endereco)

        
    print(clientes_ativos)