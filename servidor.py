import socket
import threading
import time
import struct

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

def monta_mensagem(tipo:str, id_origem:str, id_destino:str, nome:str, texto:str='') -> str:

    if texto!='':
        texto = texto[:140]
        texto = ' ' + texto + '\0'
    nome = nome[:20]

    mensagem = struct.pack('!IIII20s141s', int(tipo), int(id_origem), int(id_destino), len(texto), nome.encode(), texto.encode())

    return mensagem

def desmonta_mensagem(mensagem_cliente:str) -> dict:

    try:

        tipo, origem, destino, tamanho, nome, texto = struct.unpack('!IIII20s141s', mensagem_cliente)

        mensagem_desmontada = {
            'tipo': str(tipo), 
            'id_origem': str(origem), 
            'id_destino': str(destino), 
            'nome': nome.decode().replace('\0',''), 
            'texto': texto.decode().replace('\0',''),
            'valida': True
        }
        print(mensagem_desmontada)

        return mensagem_desmontada
    
    except Exception as e:
        print(f"Erro inesperado: {e}")
        mensagem_desmontada = {
            'valida': False
        }
        return mensagem_desmontada

def monta_erro(id_cliente:str, mensagem_erro:str) -> str:

    mensagem = monta_mensagem('3', '0', id_cliente, "servidor", mensagem_erro)

    return mensagem

def envia_mensagem(mensagem, endereco):
    try:
        serverSocket.sendto(mensagem, endereco)
    except:
        erro = "Erro ao tentar enviar mensagem"
        print(erro)
        logs.append(erro)

#Realiza o tratamento das dados recebidos
def resposta_servidor(mensagem_cliente, endereco_cliente, copia_clientes_ativos):

  #Trata a mensagem
    mensagem = desmonta_mensagem(mensagem_cliente)
    print(mensagem)

    #ERRO Mensagens inválidas
    if not mensagem['valida']:
        resposta = monta_erro('0', "Formato da mensagem invalido")
        envia_mensagem(resposta, endereco_cliente)
        return

    contem_texto = 0
    if mensagem['texto'] != "":
        contem_texto = 1

    #OI
    if mensagem['tipo'] == '0':
        id_origem_num = int(mensagem['id_origem'])
        possivel_emissor = f"{id_origem_num + 1000}"
        if mensagem['id_origem'] != '0' and not(mensagem['id_origem'] in clientes_ativos) and id_origem_num < 2000 \
                and (id_origem_num > 999 or (id_origem_num > 0 and not(possivel_emissor in clientes_ativos))):
            #Id disponível, responde e salva
            clientes_ativos[mensagem['id_origem']] = endereco_cliente
            mensagem = monta_mensagem('0', mensagem['id_origem'], mensagem['id_destino'], mensagem['texto'])
            envia_mensagem(mensagem_cliente,endereco_cliente)
            tempo_atual = time.time() - tempo_inicial
            tempo_atual = round(tempo_atual, 2)
            log_atualizacao = f"conectado id:{mensagem['id_origem']} tempo:{tempo_atual}s"
            logs.append(log_atualizacao)
            print(log_atualizacao)
        else:
            #ERRO Id indisponível, somente responde
            texto = f"Id {mensagem['id_origem']} indisponivel"
            mensagem = monta_mensagem('3', '0', mensagem['id_origem'], 'servidor', texto=texto)
            envia_mensagem(mensagem,endereco_cliente)

    #TCHAU
    elif mensagem['tipo'] == '1':

        #Apaga registro do cliente
        if mensagem['id_origem'] in clientes_ativos:
            del clientes_ativos[mensagem['id_origem']]
            tempo_atual = time.time() - tempo_inicial
            tempo_atual = round(tempo_atual, 2)
            log_atualizacao = f"desconectado id:{mensagem['id_origem']} tempo:{tempo_atual}s"
            logs.append(log_atualizacao)
            print(log_atualizacao)

            #Verifica se existe e apaga um exibidor associado
            possivel_exibidor = f"{int(mensagem['id_origem']) - 1000}"
            if possivel_exibidor in clientes_ativos:
                del clientes_ativos[possivel_exibidor]
                log_atualizacao = f"desconectado id:{possivel_exibidor} tempo:{tempo_atual}s"
                logs.append(log_atualizacao)
                print(log_atualizacao)

        #ERRO cliente não registrado
        else:
            texto = f"Id informado para TCHAU nao registrado"
            mensagem = monta_erro('0', texto)
            envia_mensagem(mensagem,endereco_cliente)

    #MSG
    elif mensagem['tipo'] == '2':

        #Destino registrado
        if (mensagem['id_destino'] in copia_clientes_ativos or mensagem['id_destino'] == '0') and mensagem['id_origem'] in copia_clientes_ativos:
            
            clientes_destino = {}
            if mensagem['id_destino'] == '0':
                #Envia para todos os clientes
                clientes_destino = copia_clientes_ativos.copy()
            else:
                #Enviar somente para um cliente especificado
                clientes_destino[mensagem['id_destino']] = copia_clientes_ativos[mensagem['id_destino']]

            for id, cliente in clientes_destino.items():
                mensagem = monta_mensagem('2', mensagem['id_origem'], mensagem['id_destino'], mensagem['nome'], texto=mensagem['texto'])
                envia_mensagem(mensagem,cliente)
        
        #ERRO Origem não registrada
        elif not (mensagem['id_origem'] in copia_clientes_ativos):
            texto = "Origem da mensagem nao registrada"
            mensagem = monta_erro('0', texto)
            envia_mensagem(mensagem,endereco_cliente)

        #ERRO Destino não registrado
        else:
            texto = "Destino da mensagem nao registrado"
            mensagem = monta_erro(mensagem['id_origem'], texto)
            envia_mensagem(mensagem,endereco_cliente)

    #LISTA CLIENTES
    elif mensagem['tipo'] == '4':
        texto = f"Clientes: {','.join(list(copia_clientes_ativos.keys()))}"
        mensagem = monta_mensagem('2', '0', mensagem['id_origem'], 'servidor', texto=texto)
        envia_mensagem(mensagem,endereco_cliente)

    else:
        texto = f"Tipo de mensagem nao esperado"
        mensagem = monta_erro(mensagem['id_origem'], texto)
        envia_mensagem(mensagem,endereco_cliente)


def envia_status():
    clientes_destino = clientes_ativos.copy()

    tempo_atual = time.time() - tempo_inicial
    tempo_atual = round(tempo_atual, 2)

    for id, cliente in clientes_destino.items():
        texto = f"{len(clientes_destino)} clientes, servidor ativo a {tempo_atual}s"
        mensagem = monta_mensagem('2', '0', id, 'servidor', texto)
        envia_mensagem(mensagem,cliente)

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
        logs.append(f"Conexão cortada subtamente")