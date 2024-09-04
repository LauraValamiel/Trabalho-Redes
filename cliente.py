# -*- coding: utf-8 -*-
#__author__ = ""

import socket, sys
import time


HOST = '192.168.5.104'  # endereço IP
PORT = 20000        # Porta utilizada pelo servidor
BUFFER_SIZE = 1024  # tamanho do buffer para recepção dos dados


def main(argv): 
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("Servidor executando!")
            nome_cliente = input("Digite o seu nome: ") 
            s.send(nome_cliente.encode()) 

            while(True):   
                pergunta = input("Digite a pergunta a ser enviada ao servidor: ")
                s.send(pergunta.encode()) #texto.encode - converte a string para bytes
                resposta = s.recv(BUFFER_SIZE)
                #texto_recebido = repr(data) #converte de bytes para um formato "printável"
                resposta_string = resposta.decode("utf-8") #converte os bytes em string
                print('Resposta: ', resposta_string)

                humano_ou_ia = input("A resposta é proveniente de um humano ou de alguma inteligência artificial? ")
                s.send(humano_ou_ia.encode())
                resposta_certa = s.recv(BUFFER_SIZE).decode('utf-8')
                #resposta_certa_decodificada = resposta_certa.decode('utf-8')
                print(resposta_certa)

                continuar_perguntando = input("Deseja fazer uma nova pergunta? ")
                s.send(continuar_perguntando.encode())

                if continuar_perguntando.lower() == 'não' or continuar_perguntando.lower() == 'nao':
                    total_ia = s.recv(BUFFER_SIZE).decode('utf-8')
                    total_humano = s.recv(BUFFER_SIZE).decode('utf-8')
                    total_acertos = s.recv(BUFFER_SIZE).decode('utf-8')
                    print("Total de respostas provenientes de inteligência artificial: ", total_ia)
                    print("Total de respostas provenientes de humano: ", total_humano)
                    print("Total de acertos: ", total_acertos)
                    print('vai encerrar o socket cliente!')
                    s.close()
                    break
    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return


if __name__ == "__main__":   
    main(sys.argv[1:])