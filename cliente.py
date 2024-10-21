import streamlit as st
from socket import *
import threading

# FUNÇÕES
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
            mensagem_decodificada = message.decode()

            if 'mensagem_recebidas' not in st.session_state:
                st.session_state['mensagens_recebidas'] = []
            
            st.session_state['mensagens_recebidas'].append(mensagem_decodificada)
        except Exception as e:
            st.error(f"Erro ao receber mensagem: {e}")

serverSocket = socket(AF_INET, SOCK_DGRAM)
# serverSocket.settimeout(10)

if 'escutando_mensagens' not in st.session_state:
    st.session_state['escutando_mensagens'] = False

if not st.session_state['escutando_mensagens']:
    threading.Thread(target=escutar_mensagem, daemon=True).start()
    st.session_state['escutando_mensagens'] = True

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
        username = limited_username_input(st.session_state['username_input']) + '\0'

        if user_id and username and st.session_state['server_ip'] and st.session_state['server_port']:
            try:
                data = f'0 {user_id} 0 0 {username}'
                serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))

                message, _ = serverSocket.recvfrom(1024)
                st.success(f"Resposta do servidor: {message.decode()}")

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
            data = f'1 {userId} 0 0 {username}'
            serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))

            message, _ = serverSocket.recvfrom(1024)
            st.success(f"Resposta do servidor: {message.decode()}")
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
            data = f'2 {st.session_state['user_id']} {st.session_state['id_destino']} {len(st.session_state['mensagem'])} {st.session_state['username_input']} {st.session_state['mensagem']}'
            serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))
        except Exception as e:
            st.error(f"Erro ao conectar ao servidor: {e}")

def pagina_receber_mensagens():
    st.title("Receber mensagens")

    if 'mensagens_recebidas' not in st.session_state:
        st.session_state['mensagens_recebidas'] = []
    
    st.subheader("Mensagens recebidas:")

    if len(st.session_state['mensagens_recebidas']) == 0:
        st.write("Nenhuma mensagem recebida.")
        print('NADA')
    else:
        print('TUDO')
        for msg in st.session_state['mensagens_recebidas']:
            st.write(msg)
    

def pagina_listar_clientes():
    st.title("Solicitar lista de clientes conectados")

    if st.button("Obter lista de clientes"):
        try:
            user_id = st.session_state['user_id']
            data = f'4 {user_id} 0 0 servidor'
            serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))

            message, _ = serverSocket.recvfrom(1024)
            mensagem_decodificada = message.decode()

            st.success(f"Resposta do servidor: {mensagem_decodificada}")

        except Exception as e:
            st.error(f"Erro ao conectar ao servidor: {e}")

def mudar_pagina(pagina):
    st.session_state['pagina'] = pagina

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


