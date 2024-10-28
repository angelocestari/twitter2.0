import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx,get_script_run_ctx
from socket import *
import threading
import struct

serverSocket = socket(AF_INET, SOCK_DGRAM)
# serverSocket.settimeout(10)

# FUNÇÕES

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

        return mensagem_desmontada
    
    except Exception as e:
        print(f"Erro inesperado: {e}")
        mensagem_desmontada = {
            'valida': False
        }
        return mensagem_desmontada
    
def envia_mensagem(mensagem, endereco_cliente):
    try:
        serverSocket.sendto(mensagem, endereco_cliente)
    except:
        erro = "Erro ao tentar enviar mensagem"
        print(erro)

def limited_userId_input(user_input):
    try:
        user_id = int(user_input)
        if 1 <= user_id <= 999:
            return user_id
        else:
            st.error("ID inválido! O ID deve estar entre 1 e 999.")
            return None
    except ValueError:
        st.error("ID inválido! Por favor, insira um número.")
        return None

def limited_username_input(user_input):
    if len(user_input) > 20 or ' ' in user_input:
        st.error("Nome de usuário inválido! Deve ter, no máximo, 20 caracteres e sem espaços.")
        return None
    return user_input.strip()

def escutar_mensagem():   
    while True:
        try:
            message, _ = serverSocket.recvfrom(1024)

            mensagem_decodificada = desmonta_mensagem(message)
            if mensagem_decodificada['valida'] and mensagem_decodificada['texto']!="":
                st.session_state['mensagens_recebidas'].append(mensagem_decodificada)
        except Exception as e:
            st.error(f"Erro ao receber mensagem: {e}")

def formata_mensagem_chat(msg: dict) -> str:
    
    texto_ajustado = f'**{msg['nome']}({msg['id_origem']}):** {msg['texto']}'

    return texto_ajustado

# PÁGINAS
def pagina_criar_conexao():
    st.title("Insira os dados do cliente")

    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = ''

    st.session_state['user_id'] = st.text_input("Digite seu ID (Entre 1 e 999)", value=st.session_state['user_id'])

    if 'username_input' not in st.session_state:
        st.session_state['username_input'] = ''

    st.session_state['username_input'] = st.text_input("Digite o seu nome de usuário (Máximo: 20 caracteres)")
    
    if 'server_ip' not in st.session_state:
        st.session_state['server_ip'] = ''
    if 'server_port' not in st.session_state:
        st.session_state['server_port'] = ''

    st.session_state['server_ip'] = st.text_input("Endereço IP do servidor", value=st.session_state['server_ip'])
    st.session_state['server_port'] = st.text_input("Porta do servidor", value=st.session_state['server_port'])

    if st.button('Criar conexão'):

        user_id = limited_userId_input(st.session_state['user_id'])
        username = limited_username_input(st.session_state['username_input'])

        if user_id and username and st.session_state['server_ip'] and st.session_state['server_port']:
            try:
                data = monta_mensagem('0', str(user_id), '0', '0', username)
                envia_mensagem(data, (st.session_state['server_ip'], int(st.session_state['server_port'])))

                message, _ = serverSocket.recvfrom(1024)
                message = desmonta_mensagem(message)
                if message['tipo'] == '0':
                    st.success(f"Conectado com o id {message['id_origem']}")

                    ajusta_mensagens_salvas()

                    #Cria thread para leitura das mensagens
                    ctx = get_script_run_ctx(suppress_warning=True)
                    thread = threading.Thread(target=escutar_mensagem, daemon=True)
                    thread = add_script_run_ctx(thread,ctx)
                    thread.start()
                else:
                    st.error(f"Erro: {message['texto']}")

            except Exception as e:
                st.error(f"Erro ao conectar ao servidor: {e}")
        else:
            st.error('Por favor, preencha todos os campos corretamente.')

def pagina_encerrar_conexao():
    st.title("Encerrar conexão")

    if st.button('Encerrar conexão'):
        username = st.session_state['username_input']
        userId = st.session_state['user_id']
        try:
            data = monta_mensagem('1', str(userId), '0', '0', username)
            envia_mensagem(data, (st.session_state['server_ip'], int(st.session_state['server_port'])))

        except Exception as e:
            st.error(f"Erro ao conectar ao servidor: {e}")
    
def pagina_enviar_mensagem():
    st.title("Enviar mensagem")

    if 'id_destino' not in st.session_state:
        st.session_state['id_destino'] = ''

    if 'mensagem' not in st.session_state:
        st.session_state['mensagem'] = ''

    st.session_state['id_destino'] = st.text_input("Digite ID do destino (Entre 1 e 999)", value=st.session_state['id_destino'])
    st.session_state['mensagem'] = st.text_input("Digite a mensagem que deseja enviar", value=st.session_state['mensagem'])

    if st.button('Enviar mensagem'):
        try:
            data = monta_mensagem('2', str(st.session_state['user_id']), str(st.session_state['id_destino']), st.session_state['username_input'], texto=st.session_state['mensagem'])
            envia_mensagem(data, (st.session_state['server_ip'], int(st.session_state['server_port'])))
        except Exception as e:
            st.error(f"Erro ao conectar ao servidor: {e}")

def pagina_receber_mensagens():
    st.title("Receber mensagens")
    
    st.subheader("Mensagens recebidas:")

    with st.container():
        try:
            if len(st.session_state['mensagens_recebidas']) == 0:
                st.write("Nenhuma mensagem recebida.")
            else:
                for msg in st.session_state['mensagens_recebidas']:
                    st.write(formata_mensagem_chat(msg))
        except:
            st.write("Conecte-se com o servidor antes de receber as mensagens")
    

def pagina_listar_clientes():
    st.title("Solicitar lista de clientes conectados")

    if st.button("Obter lista de clientes"):
        try:
            user_id = st.session_state['user_id']
            data = monta_mensagem('4', str(user_id), '0', 'servidor')
            envia_mensagem(data, (st.session_state['server_ip'], int(st.session_state['server_port'])))

            message, _ = serverSocket.recvfrom(1024)
            mensagem_decodificada = desmonta_mensagem(message)
            mensagem_decodificada = mensagem_decodificada['texto']

            st.success(f"Resposta do servidor: {mensagem_decodificada}")

        except Exception as e:
            st.error(f"Erro ao conectar ao servidor: {e}")

def mudar_pagina(pagina):
    st.session_state['pagina'] = pagina

def ajusta_mensagens_salvas():
    if 'escutando_mensagens' not in st.session_state:
        st.session_state['escutando_mensagens'] = False

    if not st.session_state['escutando_mensagens']:
        st.session_state['escutando_mensagens'] = True
        if 'mensagens_recebidas' not in st.session_state:
            st.session_state['mensagens_recebidas'] = []

def apresenta_pagina():
    paginas = {
        "Criar Conexão": pagina_criar_conexao,
        "Encerrar Conexão": pagina_encerrar_conexao,
        "Enviar Mensagem": pagina_enviar_mensagem,
        "Receber Mensagens": pagina_receber_mensagens,
        "Solicitar Lista de Clientes": pagina_listar_clientes
    }

    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = "Criar Conexão"

    with st.sidebar:
        selecao = st.radio("Navegação", list(paginas.keys()))
        mudar_pagina(selecao)

    paginas[st.session_state['pagina']]()

def main():
    apresenta_pagina()

if __name__ == '__main__':
    main()

