# -*- coding: utf-8 -*-
#__author__ = ""

import json
import os
import socket, sys
from threading import Thread
#import random
import time

HOST = '192.168.2.8'  # endereço IP
PORT = 20000        # Porta utilizada pelo servidor
BUFFER_SIZE = 1024  # tamanho do buffer para recepção dos dados


def nome_cliente(clientsocket):
    nome_recebido = clientsocket.recv(BUFFER_SIZE)
    nome_usuario = nome_recebido.decode('utf-8')
    print("Nome do usuario: ", nome_usuario)
    return nome_usuario

def resposta_automatica(pergunta, clientsocket, addr):
    import http.client

    import json

    pergunta_recebida = pergunta.decode('utf-8') # converte os bytes em string

    payload = json.dumps({
                "messages": [
                  {
                    "role": "user",
                    "content": pergunta_recebida
                  }
                ],
                "system_prompt": "Responda de forma breve, direta e completa, sem adicionar detalhes desnecessários, sem markdown, sem pontos, sem palavras dificeis.",
                "temperature": 0.2,
                "top_k": 30,
                "top_p": 0.4,
                "max_tokens": 40,
                "web_access": False
                })

    headers = {
        'x-rapidapi-key': "654b536e19msha5f523bc5c93f27p1d6ad4jsn34831a809905",
        'x-rapidapi-host': "chatgpt-42.p.rapidapi.com",
        'Content-Type': "application/json"
         }
    
    conn = http.client.HTTPSConnection("chatgpt-42.p.rapidapi.com")
    conn.request("POST", "/geminipro", payload, headers)

    resposta_chat = conn.getresponse()
    data_resposta_chat = resposta_chat.read()

    resposta_chat_decodificada = data_resposta_chat.decode("utf-8")

    resposta_json = json.loads(resposta_chat_decodificada)

    resposta_chat_decodificada = resposta_json.get('result')
    data_resposta_chat = resposta_chat_decodificada.encode()

    clientsocket.send(data_resposta_chat)

    print('Pergunta recebida do cliente {} na porta {}: {}'.format(addr[0], addr[1],pergunta_recebida))
                
    print('Resposta: ', resposta_chat_decodificada)

    return 'inteligência artificial'


def resposta_controlada(pergunta, clientsocket, addr):
    pergunta_recebida = pergunta.decode('utf-8') # converte os bytes em string
    print('Pergunta recebida do cliente {} na porta {}: {}'.format(addr[0], addr[1],pergunta_recebida))
    resposta_servidor = input('Digite a resposta: ')
    data_resposta_servidor = resposta_servidor.encode()
    # envia o mesmo texto ao cliente           
    clientsocket.send(data_resposta_servidor)
    
    return 'humano'


def avaliar_resposta(resposta_humano_ou_ia, clientsocket):
    humano_ou_ia = clientsocket.recv(BUFFER_SIZE).decode('utf-8')

    if humano_ou_ia == resposta_humano_ou_ia:
        return "Correto!"
    else:
        return "Incorreto"
    

def historico_perguntas(nome_cliente, pergunta, resposta, resultado):
    pergunta = pergunta.decode("utf-8")
    with open("historico_perguntas.txt", "a", encoding="utf-8") as historico:
        historico.write(f"Nome do usuário: {nome_cliente}\n")
        historico.write(f"Pergunta: {pergunta}\n")
        historico.write(f"Resposta: {resposta}\n")
        historico.write(f"Resultado: {resultado}\n")
        historico.write('---------------------------------------------------------\n')


def ranking_usuarios(nome_cliente, resultado):
    ranking = {}

    if os.path.exists("ranking_usuarios.json") and os.path.getsize("ranking_usuarios.json") > 0:
        with open("ranking_usuarios.json", "r") as r:
            ranking = json.load(r)  
    else:
        ranking = {}  
    
    if nome_cliente in ranking:
        ranking[nome_cliente]['Total'] += 1
        if resultado == 'Correto!':
            ranking[nome_cliente]['Acertos'] += 1 
            ranking[nome_cliente]['Porcentagem_de_acertos'] = (ranking[nome_cliente]['Acertos'] / ranking[nome_cliente]['Total']) * 100
        else:
            ranking[nome_cliente]['Porcentagem_de_acertos'] = (ranking[nome_cliente]['Acertos'] / ranking[nome_cliente]['Total']) * 100
    else:
        if resultado == 'Correto!':
            ranking[nome_cliente] = {'Posicao': 0, 'Total': 1, 'Acertos': 1, 'Porcentagem_de_acertos': 100}
        else:
            ranking[nome_cliente] = {'Posicao': 0,'Total': 1, 'Acertos': 0, 'Porcentagem_de_acertos': 0}
    ranking_ordenado = dict(sorted(ranking.items(), key=lambda x: (x[1]['Acertos'], x[1]['Porcentagem_de_acertos']), reverse=True))

    key = list(ranking_ordenado.keys())
    for user in ranking_ordenado:
        ranking_ordenado[user]['Posicao'] = key.index(user) + 1

    with open("ranking_usuarios.json", "w") as r:
        json.dump(ranking_ordenado, r, indent=4)

def continua_teste(clientsocket, addr, ia, humano, total_acertos):
    continuar_perguntando = clientsocket.recv(BUFFER_SIZE).decode('utf-8')
    if (continuar_perguntando.lower() == 'não' or continuar_perguntando.lower() == 'nao'):
        ia = str(ia)
        humano = str(humano)
        total_acertos = str(total_acertos)
        dados = f"Respostas por ia: {ia}\nRespostas por humano: {humano}\nTotal de acertos: {total_acertos}"
        clientsocket.send(dados.encode())
        print('vai encerrar o socket do cliente {} !'.format(addr[0]))
        clientsocket.close() 
        return False
    return True 

def resposta_ia(clientsocket, addr, tempo_espera):
    pergunta = clientsocket.recv(BUFFER_SIZE)
    if not pergunta:
        return
    time.sleep(tempo_espera)
    resposta = resposta_automatica(pergunta, clientsocket, addr)
    return resposta, pergunta

def on_new_client(clientsocket,addr):
    
    nome_usuario = nome_cliente(clientsocket)

    ia = 0
    humano = 0
    total_acertos = 0
    total_perguntas = 0
    tempo_espera = 0
    tipo = ''
    tipo_controlado = ''
    pergunta = ''
    aux_ia = False
    
    while True:
        try:
            while tipo.lower() != 'automatico' and tipo.lower() != 'automático' and tipo.lower() != 'controlado':
                tipo = input("Digite qual modo será usado: automático ou controlado? ")

                if tipo.lower() != 'automatico' and tipo.lower() != 'automático' and tipo.lower() != 'controlado':
                    print("Tipo inválido, tente novamente")


            if tipo.lower() == 'automatico' or tipo.lower() == 'automático' :
                if not aux_ia:
                    tempo_espera = float(input("Digite o tempo de espera em segundos para enviar a resposta automática: "))
                resposta, pergunta = resposta_ia(clientsocket, addr, tempo_espera)
                resposta_humano_ou_ia = 'inteligência artificial'
                ia += 1
                total_perguntas += 1
                aux_ia = True

            elif tipo.lower() == 'controlado':
                while tipo_controlado != '1' and tipo_controlado != '2':
                    tipo_controlado = input("Você deseja: 1 - Responder você ou 2 - Enviar para IA? ")

                    if tipo_controlado != '1' and tipo_controlado != '2':
                        print("Opção inválida, tente novamente")
                
                if tipo_controlado == '1':
                    if not pergunta:
                        pergunta = clientsocket.recv(BUFFER_SIZE)
                    if not pergunta:
                        break
                    resposta = resposta_controlada(pergunta, clientsocket, addr)
                    resposta_humano_ou_ia = 'humano'
                    humano += 1
                    total_perguntas +=1
                else:
                    tempo_espera = float(input("Digite o tempo de espera em segundos para enviar a resposta automática: "))
                    resposta, pergunta = resposta_ia(clientsocket, addr, tempo_espera)
                    resposta_humano_ou_ia = 'inteligência artificial'
                    ia += 1
                    total_perguntas += 1

                tipo_controlado = ''
                
            resultado = avaliar_resposta(resposta_humano_ou_ia, clientsocket)
            clientsocket.send(resultado.encode())

            if resultado == "Correto!":
                total_acertos += 1
            else:
                total_acertos = total_acertos

            historico_perguntas(nome_usuario, pergunta, resposta, resultado)
            ranking_usuarios(nome_usuario, resultado)

            pergunta = ''

            if not continua_teste(clientsocket, addr, ia, humano, total_acertos):
                break

        except Exception as error:
            print(f"Erro na conexão com o cliente!!  {error}")
            return


def main(argv):
    try:
        # AF_INET: indica o protocolo IPv4. SOCK_STREAM: tipo de socket para TCP,
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            while True:
                server_socket.listen()
                clientsocket, addr = server_socket.accept()
                print('Conectado ao cliente no endereço:', addr)
                cliente_thread = Thread(target=on_new_client, args=(clientsocket,addr))
                cliente_thread.start()   
    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)        
        return             



if __name__ == "__main__":   
    main(sys.argv[1:])