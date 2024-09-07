# -*- coding: utf-8 -*-
#__author__ = ""

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

    print("Nome do usuario:   ", nome_usuario)

def resposta_automatica(pergunta, clientsocket, addr):
    import http.client

    import json

    pergunta_recebida = pergunta.decode('utf-8') # converte os bytes em string

    #tempo_espera = float(input("Digite o tempo de espera em segundos para enviar a resposta automática: "))

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
        'x-rapidapi-key': "b6c836e2ddmsh31618408073819cp19a7cajsnda690adc24f9",
        'x-rapidapi-host': "chatgpt-42.p.rapidapi.com",
        'Content-Type': "application/json"
         }
    
    conn = http.client.HTTPSConnection("chatgpt-42.p.rapidapi.com")
    conn.request("POST", "/geminipro", payload, headers)

    resposta_chat = conn.getresponse()
    data_resposta_chat = resposta_chat.read()

    resposta_chat_decodificada = data_resposta_chat.decode("utf-8")

    #time.sleep(tempo_espera)#tirar dessa funçao

    clientsocket.send(data_resposta_chat)

    print('Pergunta recebida do cliente {} na porta {}: {}'.format(addr[0], addr[1],pergunta_recebida))
                
    print('Resposta: ', resposta_chat_decodificada)

    return 'inteliência artificial'


def resposta_controlada(pergunta, clientsocket, addr):
    pergunta_recebida = pergunta.decode('utf-8') # converte os bytes em string
    print('Pergunta recebida do cliente {} na porta {}: {}'.format(addr[0], addr[1],pergunta_recebida))
    resposta_servidor = input('Digite a resposta: ')
    #data_resposta = resposta.read()
    data_resposta_servidor = resposta_servidor.encode()
    # envia o mesmo texto ao cliente           
    clientsocket.send(data_resposta_servidor)
    #resposta_humano_ou_ia = 'humano'#ficar fora, no if controlado
    #humano += 1#igual o comentário de cima
    return 'humano'


def avaliar_resposta(resposta_humano_ou_ia, clientsocket):
    humano_ou_ia = clientsocket.recv(BUFFER_SIZE).decode('utf-8')
    #if not humano_ou_ia:
     #   break

    if humano_ou_ia == resposta_humano_ou_ia:
        return "Correto!"
    else:
        return "Incorreto"
    

def historico_perguntas(nome_cliente, pergunta, resposta, resultado):
    with open("historico_perguntas.txt", "a", encoding="utf-8") as historico:
        historico.write(f"Nome do usuário: {nome_cliente}\n")
        historico.write(f"Pergunta: {pergunta}\n")
        historico.write(f"Resposta: {resposta}\n")
        historico.write(f"Resultado: {resultado}\n")
        historico.write('---------------------------------------------------------\n')


def ranking_usuarios(nome_cliente, resultado, total_perguntas):
    ranking = {}

    with open("ranking_usuarios.txt", "a", encoding='utf-8') as r:
        ranking[nome] = {'total': 1, 'acertos': 1 if acertou else 0}
        #Er.write(f"{nome_cliente}: [Resultado = {resultado}][Total de perguntas = {total_perguntas}]")

    #lendo o ranking:
    with open("ranking_usuarios.txt", "r", encoding="utf-8") as r:
        for linha in r:
            cliente, resultado, total_perguntas = linha.strip().split(";")
            ranking[cliente] = {'Resultado': int(resultado), 'Total de perguntas' : int(total_perguntas)}
        
    #atualizando os dados do usuario:
    if nome_cliente in ranking:
        ranking[cliente][total_perguntas] += total_perguntas
        if resultado == "Correto!":
            ranking[cliente][resultado] += 1
    else:
        ranking[cliente] = [resultado][total_perguntas]

    ranking_ordenado = sorted(ranking.items(), key=lambda x: (x[1][1] / x[1][0])*100, reverse=True)

    with open("ranking_usuarios.txt", "w", encoding='utf-8') as r:
        for cliente, (resultado, total_perguntas) in ranking.items():
            r.write(f"{cliente}: {resultado}; {total_perguntas}\n")

def continua_teste(clientsocket, addr):
    continuar_perguntando = clientsocket.recv(BUFFER_SIZE).decode('utf-8')
    if (continuar_perguntando.lower() == 'não' or continuar_perguntando.lower() == 'nao'):
        print('vai encerrar o socket do cliente {} !'.format(addr[0]))
        clientsocket.close() 
        return False
    return True 


def on_new_client(clientsocket,addr):
    
    nome_usuario = nome_cliente(clientsocket)
    print("Nome do usuário: ", nome_usuario)

    ia = 0
    humano = 0
    total_acertos = 0
    total_perguntas = 0

    while True:
        try:
            tipo = input("Digite qual modo será usado: automático ou controlado? ")

            if tipo.lower() == 'automatico' or tipo.lower() == 'automático':
                tempo_espera = float(input("Digite o tempo de espera em segundos para enviar a resposta automática: "))
                
            pergunta = clientsocket.recv(BUFFER_SIZE)
            if not pergunta:
                break

            if tipo.lower() == 'automatico' or tipo.lower() == 'automático':
                time.sleep(tempo_espera)
                resposta = resposta_automatica(pergunta, clientsocket, addr)
                resposta_humano_ou_ia = 'inteligência artificial'
                ia += 1
                total_perguntas += 1

            elif tipo.lower() == 'controlado':
                resposta = resposta_controlada(pergunta, clientsocket, addr)
                resposta_humano_ou_ia = 'humano'
                humano += 1
                total_perguntas +=1

            else:
                print("Tipo inválido, tente novamente")
                continue

            resultado = avaliar_resposta(resposta_humano_ou_ia, clientsocket)
            clientsocket.send(resultado.encode())

            if resultado == "Correto!":
                total_acertos += 1
            else:
                total_acertos = total_acertos

            ia = str(ia)
            humano = str(humano)
            total_acertos = str(total_acertos)

            dados = f"Respostas por ia: {ia}\nRespostas por humano: {humano}\nTotal de acertos: {total_acertos}"
            clientsocket.send(dados.encode())

            historico_perguntas(nome_usuario, pergunta, resposta, resultado)
            ranking_usuarios(nome_usuario, resultado, total_perguntas)

            if not continua_teste(clientsocket, addr):
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