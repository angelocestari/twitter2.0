import streamlit as st
from socket import *


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

def pagina_criar_conexao():
    st.title("Insira os dados do cliente")

    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = ''

    st.session_state['user_id'] = st.text_input("Digite seu ID (Entre 1 e 999)", value=st.session_state['user_id'])

    username_input = st.text_input("Digite o seu nome de usuário (Máximo: 20 caracteres)")
    
    if 'server_ip' not in st.session_state:
        st.session_state['server_ip'] = ''
    if 'server_port' not in st.session_state:
        st.session_state['server_port'] = ''

    st.session_state['server_ip'] = st.text_input("Endereço IP do servidor", value=st.session_state['server_ip'])
    st.session_state['server_port'] = st.text_input("Porta do servidor", value=st.session_state['server_port'])

    if st.button('Enviar'):

        user_id = limited_userId_input(st.session_state['user_id'])
        username = limited_username_input(username_input)

        if user_id and username and st.session_state['server_ip'] and st.session_state['server_port']:
            try:
                serverSocket = socket(AF_INET, SOCK_DGRAM)
                serverSocket.settimeout(1)
                data = f'0 {user_id} 0 0 {username}'
                serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))

                message, _ = serverSocket.recvfrom(1024)
                st.success(f"Resposta do servidor: {message.decode()}")
                serverSocket.close()

            except Exception as e:
                st.error(f"Erro ao conectar ao servidor: {e}")
        else:
            st.error('Por favor, preencha todos os campos corretamente.')

def pagina_enviar_mensagem():
    st.title('ENVIAR MENSAGEM')

    # if st.button("Listar Usuários Ativos"):
    #     try:
    #         serverSocket = socket(AF_INET, SOCK_DGRAM)
    #         serverSocket.settimeout(1)
    #         data = 'list'
    #         serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))

    #         lista_usuarios,_ = serverSocket.recvfrom(1024)
    #         st.write("Usuários Ativos:")
    #         st.text(lista_usuarios.decode())
    #         serverSocket.close()

    #     except Exception as e:
    #         st.error(f'Erro ao conectar ao servidor: {e}')

    destino = st.text_input("ID de destino")
    mensagem = st.text_input("Digite sua mensagem")

    if st.button("Enviar Mensagem"):
        try:
            serverSocket = socket(AF_INET, SOCK_DGRAM)
            serverSocket.settimeout(1)
            tamanho_mensagem = len(mensagem)
            data = f"2 {st.session_state['user_id']} {destino} {tamanho_mensagem} angelo {mensagem}"
            serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))

            resposta, _ = serverSocket.recvfrom(1024)
            st.write("Resposta do servidor ao enviar mensagem:")
            st.text(resposta.decode())
            serverSocket.close()
        
        except Exception as e:
            st.error(f'Erro ao conectar ao servidor: {e}')

def pagina_encerrar_conexao():
    st.title("Encerrar conexão")

    try:
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.settimeout(2)
        if st.button("Encerrar conexão"):
            data = f"1 {st.session_state['user_id']} 0 0 angelo"
            serverSocket.sendto(data.encode(), (st.session_state['server_ip'], int(st.session_state['server_port'])))
            resposta,_ = serverSocket.recvfrom(1024)
            st.text(resposta.decode())
            serverSocket.close()

    except Exception as e:
        st.error(f"Erro ao encerrar conexão: {e}")

def mudar_pagina(pagina):
    st.session_state['pagina'] = pagina

paginas = {
    "Criar Conexão": pagina_criar_conexao,
    "Enviar Mensagem": pagina_enviar_mensagem,
    "Encerrar Conexão": pagina_encerrar_conexao
}

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = "Criar Conexão"

with st.sidebar:
    selecao = st.radio("Navegação", list(paginas.keys()))
    mudar_pagina(selecao)

paginas[st.session_state['pagina']]()


