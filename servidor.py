import socket
import threading
import time

tempo_inicial = time.time()

#Prepara o endereço do servidor que será usado
server_address = socket.gethostbyname(socket.gethostname())
port = 12000
print(f"Endereço do servidor: {server_address}:{port}")

#Prepara os sockets do servidor
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serverSocket.bind(('', port))

clientes_ativos = {}
logs = []

#Realiza o tratamento das dados recebidos
def resposta_servidor(mensagem_cliente, endereco_cliente, copia_clientes_ativos):

    #Decodifica a mensagem recebida
    mensagem = mensagem_cliente.decode()

    #DEBUG
    # print(mensagem)

    #Particiona a mensagem para tratamento dos dados
    partes_mensagem = mensagem.split(' ')

    #ERRO Mensagens inválidas
    if len(partes_mensagem) < 5:
        texto = f"Mensagem sem a quantidade minima de campos\0"
        mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
        serverSocket.sendto(mensagem.encode(), endereco_cliente)
        return
    elif not (partes_mensagem[0].isdigit() and partes_mensagem[1].isdigit() and partes_mensagem[2].isdigit() and partes_mensagem[3].isdigit()):
        texto = f"Algum dos campos inteiros nao esta correto\0"
        mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
        serverSocket.sendto(mensagem.encode(), endereco_cliente)
        return

    contem_texto = 0
    if len(partes_mensagem) > 5 and partes_mensagem[4] != '0':
        contem_texto = 1

    #OI
    if partes_mensagem[0] == '0':
        numero_origem = int(partes_mensagem[1])
        possivel_emissor = f"{numero_origem + 1000}"
        if partes_mensagem[1] != '0' and not(partes_mensagem[1] in clientes_ativos) and numero_origem < 2000 \
                and (numero_origem > 999 or (numero_origem > 0 and not(possivel_emissor in clientes_ativos))):
            #Id disponível, responde e salva
            clientes_ativos[partes_mensagem[1]] = endereco_cliente
            serverSocket.sendto(mensagem.encode(), endereco_cliente)
            tempo_atual = time.time() - tempo_inicial
            tempo_atual = round(tempo_atual, 2)
            log_atualizacao = f"conectado id:{partes_mensagem[1]} tempo:{tempo_atual}s"
            logs.append(log_atualizacao)
            print(log_atualizacao)
        else:
            #ERRO Id indisponível, somente responde
            texto = f"Id {partes_mensagem[1]} indisponivel\0"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'

            serverSocket.sendto(mensagem.encode(), endereco_cliente)

    #TCHAU
    elif partes_mensagem[0] == '1':

        #Apaga registro do cliente
        if partes_mensagem[1] in clientes_ativos:
            del clientes_ativos[partes_mensagem[1]]
            tempo_atual = time.time() - tempo_inicial
            tempo_atual = round(tempo_atual, 2)
            log_atualizacao = f"desconectado id:{partes_mensagem[1]} tempo:{tempo_atual}s"
            logs.append(log_atualizacao)
            print(log_atualizacao)

            #Verifica se existe e apaga um exibidor associado
            possivel_exibidor = f"{int(partes_mensagem[1]) - 1000}"
            if possivel_exibidor in clientes_ativos:
                del clientes_ativos[possivel_exibidor]
                log_atualizacao = f"desconectado id:{possivel_exibidor} tempo:{tempo_atual}s"
                logs.append(log_atualizacao)
                print(log_atualizacao)

        #ERRO cliente não registrado
        else:
            texto = f"Id informado para TCHAU nao registrado\0"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
            serverSocket.sendto(mensagem.encode(), endereco_cliente)

    #MSG
    elif partes_mensagem[0] == '2':

        #Destino registrado
        if (partes_mensagem[2] in copia_clientes_ativos or partes_mensagem[2] == '0') and partes_mensagem[1] in copia_clientes_ativos:
            texto = ""
            nome_origem = partes_mensagem[4] 
            if contem_texto:
                texto = partes_mensagem[5:]
                texto = ' '.join(texto)
                texto = texto[:min(int(partes_mensagem[3]),140)]

            clientes_destino = {}
            if partes_mensagem[2] == '0':
                #Envia para todos os clientes
                clientes_destino = copia_clientes_ativos.copy()
            else:
                #Enviar somente para um cliente especificado
                clientes_destino[partes_mensagem[2]] = copia_clientes_ativos[partes_mensagem[2]]

            for id, cliente in clientes_destino.items():
                mensagem = f"2 {partes_mensagem[1]} {id} {len(texto)} {nome_origem} {texto}"
                serverSocket.sendto(mensagem.encode(), cliente)
        
        #ERRO Origem não registrada
        elif not (partes_mensagem[1] in copia_clientes_ativos):
            texto = "Origem da mensagem nao registrada\0"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
            serverSocket.sendto(mensagem.encode(), endereco_cliente) 

        #ERRO Destino não registrado
        else:
            texto = "Destino da mensagem nao registrado\0"
            mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
            serverSocket.sendto(mensagem.encode(), endereco_cliente)

    #LISTA CLIENTES
    elif partes_mensagem[0] == '4':
        texto = f"Clientes: {','.join(list(copia_clientes_ativos.keys()))}\0"
        mensagem = f'4 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'
        serverSocket.sendto(mensagem.encode(), endereco_cliente)  

    else:
        texto = f"Mensagem enviada nao definida\0"
        mensagem = f'3 0 {partes_mensagem[1]} {len(texto)} servidor {texto}'

    # print(clientes_ativos)


def verifica_desconecta(mensagem_cliente, endereco_cliente):

    #Decodifica a mensagem
    mensagem = mensagem_cliente.decode()

    #Quebra a mensagem para tratamento
    partes_mensagem = mensagem.split(' ')

    if len(partes_mensagem) > 1 and partes_mensagem[1] in clientes_ativos and clientes_ativos[partes_mensagem[1]] == endereco_cliente:
        del clientes_ativos[partes_mensagem[1]]

def envia_status():
    clientes_destino = clientes_ativos.copy()

    tempo_atual = time.time() - tempo_inicial
    tempo_atual = round(tempo_atual, 2)

    for id, cliente in clientes_destino.items():
        texto = f"{len(clientes_destino)} clientes, servidor ativo a {tempo_atual}s\0"
        mensagem = f"2 0 {id} {len(texto)} servidor {texto}"
        serverSocket.sendto(mensagem.encode(), cliente)

def periodicamente_envia_status():
    while True:
        envia_status()
        time.sleep(60)

threading.Thread(target=periodicamente_envia_status).start()

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
        print(f"Conexão cortada subtamente")