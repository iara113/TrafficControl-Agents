import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import Interface
import sys
import pygame
import random
import string
import aiosasl.common



# Guarda todas as estradas
class Ambiente():
    def __init__(self, estradas):
        self.estradas = estradas



# Guarda os carros de cada estrada
class Estrada():
    def __init__(self, jid, carros=None):
        self.jid = jid
        self.carros = carros if carros is not None else []



# Agente Central
class CentralAgente(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)

    # Envia mensagem ao semáforo
    class MensagemSemaforo(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(2)
            semaforos_copy = semaforos.copy()
            lista_mudados = [] # Lista com semaforos que ja foram mudados

            # Passa por todos os semáforos
            for semaforo in semaforos_copy:
                jid_estrada, parte = estrada_semaforo(semaforo)
                intersecao = semaforos_intersecao(semaforo)

                # Sinais que serão modificados
                oposto = intersecao[0]
                contrario1 = intersecao[1]
                contrario2 = intersecao[2]

                # Se tiver uma ambulancia na estrada com semaforo vermelho, mudar para verde
                if semaforo.cor == Interface.semaforo_vermelho and estrada_com_ambulancia(jid_estrada, parte):
                    # Mensagem para estrada com semaforo vermelho e ambulancia, muda para verde
                    msg = Message(to= str(semaforo.jid)) 
                    msg.set_metadata("performative", "inform")
                    msg.body = f"{str(semaforo.jid)}_verde"
                    await self.send(msg)
                    lista_mudados.append(semaforo)

                    # Muda estrada oposta para verde
                    if oposto != ' ': 
                        msg = Message(to=str(oposto.jid))
                        msg.set_metadata("performative", "inform")
                        msg.body = f"{str(oposto.jid)}_verde"
                        await self.send(msg)
                        lista_mudados.append(oposto)
                    
                    # Mudam estradas contrarias para amarelo
                    if contrario1 != ' ': 
                        msg = Message(to=str(contrario1.jid))
                        msg.set_metadata("performative", "inform")
                        msg.body = f"{str(contrario1.jid)}_amarelo"
                        await self.send(msg)
                        lista_mudados.append(contrario1)
                    if contrario2 != ' ': 
                        msg = Message(to=str(contrario2.jid))
                        msg.set_metadata("performative", "inform")
                        msg.body = f"{str(contrario2.jid)}_amarelo"
                        await self.send(msg)
                        lista_mudados.append(contrario2)
                else:
                    # Semaforo com mais carros
                    mais_carros = semaforo_mais_carros(semaforo, oposto, contrario1, contrario2) 

                    # Garantir que os contrarios que se vão mudar para amarelo não tem ambulâncias
                    if contrario1!=' ': 
                        jid_estrada, parte = estrada_semaforo(contrario1)
                        if estrada_com_ambulancia(jid_estrada, parte):
                            mais_carros = contrario1
                    if contrario2!=' ': 
                        jid_estrada, parte = estrada_semaforo(contrario2)
                        if estrada_com_ambulancia(jid_estrada, parte):
                            mais_carros = contrario2

                    # Se todas as interseçoes tiverem o mesmo numero de carros na estrada total
                    # ou se a estrada com mais carros ja estiver a verde, nao muda nada
                    if mais_carros!="igual" and mais_carros.cor != Interface.semaforo_verde and semaforo not in lista_mudados:
                        intersecao = semaforos_intersecao(mais_carros)

                        oposto = intersecao[0]
                        contrario1 = intersecao[1]
                        contrario2 = intersecao[2]

                        # Mensagem para estrada com mais carros parados, muda para verde
                        msg = Message(to= str(mais_carros.jid)) 
                        msg.set_metadata("performative", "inform")
                        msg.body = f"{str(mais_carros.jid)}_verde"
                        await self.send(msg)
                        lista_mudados.append(mais_carros)

                        # Muda estrada oposta para verde
                        if oposto!=' ': 
                            msg = Message(to=str(oposto.jid))
                            msg.set_metadata("performative", "inform")
                            msg.body = f"{str(oposto.jid)}_verde"
                            await self.send(msg)
                            lista_mudados.append(oposto)

                        # Muda estrada contraria para amarelo
                        if contrario1!=' ': 
                            msg = Message(to=str(contrario1.jid))
                            msg.set_metadata("performative", "inform")
                            msg.body = f"{str(contrario1.jid)}_amarelo"
                            await self.send(msg)
                            lista_mudados.append(contrario1)
                        if contrario2!=' ': 
                            msg = Message(to=str(contrario2.jid))
                            msg.set_metadata("performative", "inform")
                            msg.body = f"{str(contrario2.jid)}_amarelo"
                            await self.send(msg)
                            lista_mudados.append(contrario2)


    async def setup(self):
        print("{} começou.".format(str(self.jid)))
        template = Template()
        template.set_metadata("performative", "inform")
        c = self.MensagemSemaforo()
        self.add_behaviour(c, template)


#Retorna o jid da estrada do semaforo e a parte da estrada
def estrada_semaforo(semaforo):
    if semaforo.posicao in Interface.cima():
        lista = Interface.cima()
        dir = "cima"
    elif semaforo.posicao in Interface.baixo():
        lista = Interface.baixo()
        dir = "baixo"
    elif semaforo.posicao in Interface.esquerda():
        lista = Interface.esquerda()
        dir = "esquerda"
    elif semaforo.posicao in Interface.direita():
        lista = Interface.direita()
        dir = "direita"

    for i in range(0, len(lista), Interface.num_estradas):
        intervalo = lista[i:i+Interface.num_estradas]

        if semaforo.posicao in intervalo:
            if dir=="esquerda":
                parte = Interface.num_estradas - intervalo.index(semaforo.posicao) - 1
                pos =  i // Interface.num_estradas
            if dir=="direita":
                parte = intervalo.index(semaforo.posicao)
                pos = i // Interface.num_estradas
            elif dir=="cima":
                parte = Interface.num_estradas - i // Interface.num_estradas - 1
                pos = intervalo.index(semaforo.posicao)
            if dir=="baixo":
                parte = i // Interface.num_estradas
                pos = intervalo.index(semaforo.posicao)
            break

    jid_estrada =  f"estrada_{dir}_{pos}@localhost"
    return jid_estrada, parte


#Retorna true se tiver ambulancias na estrada do semaforo
def estrada_com_ambulancia(jid_estrada, parte):
    for estrada in ambiente.estradas:
        if jid_estrada == str(estrada.jid):
            for c in estrada.carros:
                if c.carro.tipo=="ambulancia":
                    if parte_estrada(c) == parte:
                        return True
    return False


#Retorna uma lista com os os semaforos que estao na mesma intersecao que o semaforo dado
def semaforos_intersecao(semaforo):
    lista = []
    intervalo1 = (Interface.num_estradas * 4) - (Interface.num_estradas * 2 - 1)
    intervalo2 = Interface.num_estradas * 2 - 1

    pos = semaforo.posicao
    if pos in Interface.cima():
        lista.append(semaforos[pos - intervalo1] if pos - intervalo1 >= 0 and semaforos[pos - intervalo1].posicao in Interface.baixo() else " ")
        lista.append(semaforos[pos - intervalo1 + 1] if pos - intervalo1 >= 0 and semaforos[pos - intervalo1 + 1].posicao in Interface.esquerda() else " ")
        lista.append(semaforos[pos - 1] if pos - 1 >= 0 and semaforos[pos - 1].posicao in Interface.direita() else " ")

    elif pos in Interface.baixo():
        lista.append(semaforos[pos + intervalo1] if pos + intervalo1 < len(Interface.coordenadas_semaforos) and semaforos[pos + intervalo1].posicao in Interface.cima() else " ")
        lista.append(semaforos[pos + 1] if pos + 1 < len(Interface.coordenadas_semaforos) and semaforos[pos + 1].posicao in Interface.esquerda() else " ")
        lista.append(semaforos[pos + intervalo1 - 1] if pos + intervalo1 - 1 < len(Interface.coordenadas_semaforos) and semaforos[pos + intervalo1 - 1].posicao in Interface.direita() else " ")

    elif pos in Interface.esquerda():
        lista.append(semaforos[pos + intervalo2] if pos + intervalo2 < len(Interface.coordenadas_semaforos) and semaforos[pos + intervalo2].posicao in Interface.direita() else " ")
        lista.append(semaforos[pos - 1] if pos - 1 >=0 and semaforos[pos - 1].posicao in Interface.baixo() else " ")
        lista.append(semaforos[pos + intervalo2 + 1] if pos + intervalo2 + 1 < len(Interface.coordenadas_semaforos) and semaforos[pos + intervalo2 + 1].posicao in Interface.cima() else " ")

    elif pos in Interface.direita():
        lista.append(semaforos[pos - intervalo2] if pos - intervalo2 >=0 and semaforos[pos - intervalo2].posicao in Interface.esquerda() else " ")
        lista.append(semaforos[pos - intervalo2 - 1] if pos - intervalo2 - 1 >= 0 and semaforos[pos - intervalo2 - 1].posicao in Interface.baixo() else " ")
        lista.append(semaforos[pos + 1] if pos + 1 < len(Interface.coordenadas_semaforos)and semaforos[pos + 1].posicao in Interface.cima() else " ")

    return lista


# Retorna o semaforo com mais carros na parte da rua
def semaforo_mais_carros(s1, s2, s3, s4):
    jid_estrada1, jid_estrada2, jid_estrada3, jid_estrada4 = " ", " ", " ", " "
    parte1, parte2, parte3, parte4 = " ", " ", " ", " "

    if s1!= ' ':
        jid_estrada1, parte1 = estrada_semaforo(s1)
    if s2!= ' ':
        jid_estrada2, parte2 = estrada_semaforo(s2)
    if s3!= ' ':
        jid_estrada3, parte3 = estrada_semaforo(s3)
    if s4!= ' ':
        jid_estrada4, parte4 = estrada_semaforo(s4)

    n1, n2, n3, n4 = 0, 0, 0, 0
    len_s1, len_s2, len_s3, len_s4 = 0, 0, 0, 0

    
    for estrada in ambiente.estradas:
        if str(estrada.jid) == jid_estrada1:
            for c in estrada.carros:
                len_s1 = len(estrada.carros)
                if parte_estrada(c) == parte1:
                    n1 += 1
        if str(estrada.jid) == jid_estrada2:
            for c in estrada.carros:
                len_s2 = len(estrada.carros)
                if parte_estrada(c) == parte2:
                    n2 += 1
        if str(estrada.jid) == jid_estrada3:
            for c in estrada.carros:
                len_s3 = len(estrada.carros)
                if parte_estrada(c) == parte3:
                    n3 += 1
        if str(estrada.jid) == jid_estrada4:
            for c in estrada.carros:
                len_s4 = len(estrada.carros)
                if parte_estrada(c) == parte4:
                    n4 += 1

    semaforos = [s1, s2, s3, s4]
    contagens = [n1, n2, n3, n4]
    lens = [len_s1, len_s2, len_s3, len_s4]

    if (n1 == n2 == n3 == n4) : #Caso de empate, escolhe-se o que tem mais carros no total da rua
        if len_s1 == len_s2 == len_s3 == len_s4:
            return "igual"
        
        semaforo_mais_carros = semaforos[lens.index(max(lens))]
        return semaforo_mais_carros

    semaforo_mais_carros = semaforos[contagens.index(max(contagens))]
    return semaforo_mais_carros



#Agente semáforo
class SemaforoAgente(Agent):
    def __init__(self, jid, password, coordenadas, cor, posicao):
        super().__init__(jid, password)
        self.cor = cor
        self.x = coordenadas[0]
        self.y = coordenadas[1]
        self.posicao = posicao


    # Recebe mensagem da central para mudar cor do semaforo
    class MensagemCentral(CyclicBehaviour):
        async def run(self):
            reply = await self.receive(timeout=100)

            # Só recebe a mensagem que a central enviou para este semaforo
            while not str(reply.body).startswith(str(self.agent.jid)):
                reply = await self.receive(timeout=100)

            cor = reply.body.split("_")[-1]

            # Muda o semaforo para a cor que a central enviou
            if cor=="amarelo":
                if self.agent.cor==Interface.semaforo_verde:
                    self.agent.cor = Interface.semaforo_amarelo
                    Interface.liga_semaforo(self.agent.posicao, self.agent.cor)
                    await asyncio.sleep(2) #2 segundos para o semaforo amarelo
                self.agent.cor = Interface.semaforo_vermelho
            
            if cor=="verde":
                if Interface.num_estradas >= 3:
                    tempo = 1
                elif Interface.num_estradas == 2:
                    tempo = 2
                elif Interface.num_estradas == 1:
                    tempo = 3
                await asyncio.sleep(tempo)
                self.agent.cor = Interface.semaforo_verde
            Interface.liga_semaforo(self.agent.posicao, self.agent.cor)


    # Recebe mensagens dos carros a perguntar se pode avançar
    class RecebeCarros(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=500)

            #Só recebe mensagens de carros
            while msg.body != str(self.agent.posicao):
                msg = await self.receive(timeout=100)

            # Aguarda até que o semáforo fique verde
            while self.agent.cor != Interface.semaforo_verde:
                pygame.display.update()
                print(f'O carro {str(msg.sender)} está a aguardar que o semáforo {self.agent.posicao} fique verde...')
                await asyncio.sleep(1)

            # Agora o semáforo está verde, pode responder
            if msg:
                reply_body = f"A luz está verde no semáforo {self.agent.posicao}. O carro {str(msg.sender)} pode avançar!"

                # Manda mensagem para o carro
                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.body = reply_body
                await self.send(reply)


    async def setup(self):
        print("{} começou.".format(str(self.jid)))
        Interface.liga_semaforo(self.posicao, self.cor)
        pygame.display.update()

        # Começa ciclo de receber mensagens de carros
        b = self.RecebeCarros()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)

        # Começa ciclo de receber mensagens da central
        c = self.MensagemCentral()
        self.add_behaviour(c, template)



# Agente Carro
class CarroAgente(Agent):
    def __init__(self, jid, password, carro, direcao, x, y, estrada, estado=0, anterior=None):
        super().__init__(jid, password)
        self.carro = carro # interface
        self.direcao = direcao
        self.x = x
        self.y = y
        self.estrada = estrada
        self.estado = estado # 1: em movimento; 0: parado
        self.anterior = anterior # carro atras


    # Comportamento ciclico do carro
    class Comportamento(CyclicBehaviour):
        async def run(self):
            # Em movimento
            self.agent.estado = 1 

            # Se as coordenadas passarem os limites do ecrã
            if self.agent.x > Interface.largura\
            or self.agent.y > Interface.altura\
            or self.agent.x < - Interface.alt_carro or self.agent.y < - Interface.alt_carro:
                # Remove carro dos veiculos em circulacao
                veiculos_em_circulacao.remove(self.agent) 
                jid_estrada =  f"estrada_{self.agent.direcao}_{self.agent.estrada}@localhost"

                for estrada in ambiente.estradas:
                    if str(estrada.jid) == jid_estrada:
                        estrada.carros.remove(self.agent) # Remove carro da estrada

                # Veiculo parado
                self.agent.estado = 0 
                await self.agent.stop()
                self.kill(exit_code=10)
                return

            # Para desenhar retangulo cinza ("apagar veiculo anterior")
            prev_x, prev_y = self.agent.x, self.agent.y 
            jid_estrada =  f"estrada_{self.agent.direcao}_{self.agent.estrada}@localhost"

            veiculo_frente = veiculo_a_frente(self.agent)

            # Se tiver um veiculo parado à frente, parar atras dele 
            if veiculo_frente != None and veiculo_frente.estado==0 and\
            ((self.agent.direcao=="direita" and self.agent.x == veiculo_frente.x - Interface.alt_carro - 0.1*Interface.alt_carro) or\
            (self.agent.direcao=="esquerda" and self.agent.x == veiculo_frente.x + Interface.alt_carro + 0.1*Interface.alt_carro) or\
            (self.agent.direcao=="cima" and self.agent.y == veiculo_frente.y + Interface.alt_carro + 0.1*Interface.alt_carro) or\
            (self.agent.direcao=="baixo" and self.agent.y == veiculo_frente.y - Interface.alt_carro - 0.1*Interface.alt_carro)):
                # Veiculo parado
                self.agent.estado = 0 
                # Carro é o atributo anterior do veiculo da frente
                veiculo_frente.anterior = self.agent 

            # Se estiver num semaforo 
            if ((self.agent.direcao == "cima" or self.agent.direcao == "baixo")and\
            self.agent.y in Interface.paragem_carro(self.agent.direcao)) or\
            ((self.agent.direcao == "direita" or self.agent.direcao == "esquerda") and\
            self.agent.x in Interface.paragem_carro(self.agent.direcao)):
                    self.agent.estado = 0
                    semaforo = identifica_semaforo(self.agent.x, self.agent.y, self.agent.direcao)

                    # Mensagem para o semaforo
                    msg = Message(to=f"semaforo_{semaforo}@localhost") 
                    msg.set_metadata("performative", "inform")
                    msg.body = str(semaforo)
                    await self.send(msg)

                    # Só recebe respostas do semaforo em que está parado
                    reply = await self.receive(timeout=100)
                    while str(reply.sender) != f"semaforo_{semaforo}@localhost":
                        reply = await self.receive(timeout=100)
                    print(f"{reply.body}")

                    self.agent.estado = 1
                    if self.agent.anterior!=None and self.agent.anterior.estado == 0:
                        self.agent.anterior.estado = 1

            #Mudar as coordenadas para a frente e desenhar retangulo cinzento por cima do carro anterior (Animação)
            if self.agent.estado ==1:
                if self.agent.direcao == "direita":
                    self.agent.x += 1
                    pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.alt_carro, Interface.larg_carro))
                elif self.agent.direcao == "esquerda":
                    self.agent.x -= 1
                    pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.alt_carro, Interface.larg_carro))
                elif self.agent.direcao == "cima":
                    self.agent.y -= 1
                    pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.larg_carro, Interface.alt_carro))
                elif self.agent.direcao == "baixo":
                    self.agent.y += 1
                    pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.larg_carro, Interface.alt_carro))

            Interface.desenha_carro(self.agent)

            await asyncio.sleep(0.01)
            pygame.display.update()


    async def setup(self):
        print("O carro {} começou.".format(str(self.jid)))
        pygame.display.update()
        self.comportamento_carro = self.Comportamento()
        self.add_behaviour(self.comportamento_carro)


# Limites para cada parte da estrada 
def limites(direcao):
    limites_set = set()
    for i in range(len(Interface.coordenadas_semaforos)):
        if direcao == "cima" and i in Interface.cima():
            limites_set.add(Interface.coordenadas_semaforos[i][1])
        elif direcao == "baixo" and i in Interface.baixo():
            limites_set.add(Interface.coordenadas_semaforos[i][1])
        elif direcao == "esquerda" and i in Interface.esquerda():
            limites_set.add(Interface.coordenadas_semaforos[i][0])
        elif direcao == "direita" and i in Interface.direita():
            limites_set.add(Interface.coordenadas_semaforos[i][0])

    limites_sorted = sorted(list(limites_set), reverse=(direcao in ["cima", "esquerda"]))
    return limites_sorted


# Retorna a parte da estrada onde o carro se encontra 
def parte_estrada(carro):
    if carro.direcao == "cima":
        for limite in limites_cima:
            if carro.y >= limite:
                return limites_cima.index(limite)
    elif carro.direcao == "baixo":
        for limite in limites_baixo:
            if carro.y <= limite:
                return limites_baixo.index(limite)
    elif carro.direcao == "direita":
        for limite in limites_direita:
            if carro.x <= limite:
                return limites_direita.index(limite)
    elif carro.direcao == "esquerda":
        for limite in limites_esquerda:
            if carro.x >= limite:
                return limites_esquerda.index(limite)
    return Interface.num_estradas


# Se tiver algum veiculo à frente do carro, retorna qual é 
def veiculo_a_frente(carro):
    jid_estrada = f"estrada_{carro.direcao}_{carro.estrada}@localhost"
    possiveis = []
    parte_carro = parte_estrada(carro)

    for estrada in ambiente.estradas:
        if str(estrada.jid) == jid_estrada and len(estrada.carros) > 1:
            for c in estrada.carros:
                if parte_carro == parte_estrada(c):
                    if carro != c and\
                    ((carro.direcao=="direita" and c.x > carro.x) or\
                    (carro.direcao=="esquerda" and c.x < carro.x) or\
                    (carro.direcao=="cima" and c.y < carro.y) or\
                    (carro.direcao=="baixo" and c.y > carro.y)):
                        possiveis.append(c)

    if possiveis:
        if carro.direcao=="direita":
            carro_a_frente = min(possiveis, key=lambda c: c.x)
        elif carro.direcao=="esquerda":
            carro_a_frente = max(possiveis, key=lambda c: c.x)
        elif carro.direcao=="cima":
            carro_a_frente = max(possiveis, key=lambda c: c.y)
        elif carro.direcao=="baixo":
            carro_a_frente = min(possiveis, key=lambda c: c.y)
        return carro_a_frente

    return None


# Identifica a posicao do semáforo onde o carro está parado 
def identifica_semaforo(x, y, direcao):
    lista_coord = []
    if direcao=="cima" or direcao=="baixo":
        lista_y = []

        for i in range(len(Interface.coordenadas_semaforos)):
            if int(y-Interface.tamanho_semaforo//4) == int(Interface.coordenadas_semaforos[i][1])\
            and direcao=="cima" and i in Interface.cima():
                lista_y.append(i)
                lista_coord.append(Interface.coordenadas_semaforos[i])
            if int(y+Interface.tamanho_semaforo//4) == int(Interface.coordenadas_semaforos[i][1])\
            and direcao=="baixo" and i in Interface.baixo():
                lista_y.append(i)
                lista_coord.append(Interface.coordenadas_semaforos[i])

        distancia_min_x = abs(lista_coord[0][0] - x)
        pos = lista_y[0]
        for i in range(len(lista_coord)):
            distancia = abs(lista_coord[i][0] - x)
            if distancia < distancia_min_x:
                distancia_min_x = distancia
                pos = lista_y[i]

    if direcao=="esquerda" or direcao=="direita":
        lista_x = []
        for i in range(len(Interface.coordenadas_semaforos)):
            if int(x-Interface.tamanho_semaforo//4) == int(Interface.coordenadas_semaforos[i][0])\
            and direcao=="esquerda" and i in Interface.esquerda():
                lista_x.append(i)
                lista_coord.append(Interface.coordenadas_semaforos[i])
            if int(x+Interface.tamanho_semaforo//4) == int(Interface.coordenadas_semaforos[i][0])\
            and direcao=="direita" and i in Interface.direita():
                lista_x.append(i)
                lista_coord.append(Interface.coordenadas_semaforos[i])
        distancia_min_y = abs(lista_coord[0][1] - y)
        pos = lista_x[0]
        for i in range(len(lista_coord)):
            distancia = abs(lista_coord[i][1] - y)
            if distancia < distancia_min_y:
                distancia_min_y = distancia
                pos = lista_x[i]

    return pos


#Gera combinação de 3 letras aleatória para o jid dos carros
def gerar_combinacao_aleatoria():
    #Para o caso de nao retornar porque a combinacao ja foi utilizada
    while True:
        combinacao_letras = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
        if combinacao_letras not in combinacao_letras_utilizadas:
            return combinacao_letras


#Gera veiculos aleatoriamente
async def gera_veiculos():
    while True:
        veiculos_interface = [Interface.carro_vermelho, Interface.carro_azul, Interface.carro_preto,\
                            Interface.carro_verde, Interface.mota, Interface.ambulancia]
        password = "password"

        direcoes = ["cima", "baixo", "direita", "esquerda"]
        combinacoes_utilizadas = []
        num_carros = random.randint(2*Interface.num_estradas, 3*Interface.num_estradas)

        while num_carros > 0:
            carro_interface = random.choice(veiculos_interface)
            direcao = random.choice(direcoes)
            pos_estrada = random.randint(0, Interface.num_estradas - 1)

            # Verifica se a combinação estrada-direcao já está em uso
            combinacao_atual = (pos_estrada, direcao)
            if combinacao_atual not in combinacoes_utilizadas:
                jid = gerar_combinacao_aleatoria()
                combinacao_letras_utilizadas.add(jid)
                combinacoes_utilizadas.append(combinacao_atual)

                # Agentes
                x, y = 0, 0
                carro = CarroAgente(f"{jid}@localhost", password, carro_interface, direcao, x, y, pos_estrada)

                if pode_iniciar(carro):
                    veiculos_em_circulacao.add(carro)
                    Interface.inicia_carro(carro)
                    Interface.desenha_carro(carro)

                    jid_estrada = f"estrada_{direcao}_{pos_estrada}@localhost"
                    for estrada in ambiente.estradas:
                        if str(estrada.jid) == jid_estrada:
                            estrada.carros.append(carro)

                num_carros -= 1
                pygame.display.update()

        await agentes()
        pygame.display.update()
        await asyncio.sleep(3)


#Inicia os agentes ao mesmo tempo, se ja nao tiverem sido iniciados
async def agentes():
    veiculos_copy = veiculos_em_circulacao.copy()

    for veiculo in veiculos_copy:
        if veiculo not in veiculos_iniciados:
            try:
                await veiculo.start(auto_register=True)
                veiculos_iniciados.append(veiculo)
            except aiosasl.common.AuthenticationFailure:
                veiculos_em_circulacao.remove(veiculo)


# Retorna false quando algum carro nao pode ser iniciado para nao coicidir com outros que ja estao a andar 
def pode_iniciar(carro):
    if carro.direcao == "cima":
        pos = Interface.num_estradas - 1
        estrada_verificar = f"estrada_esquerda_{pos}@localhost"
    elif carro.direcao == "baixo":
        estrada_verificar = f"estrada_direita_0@localhost"
    elif carro.direcao == "direita":
        estrada_verificar = f"estrada_cima_0@localhost"
    elif carro.direcao == "esquerda":
        pos = Interface.num_estradas - 1
        estrada_verificar = f"estrada_baixo_{pos}@localhost"

    for estrada in ambiente.estradas:
        if str(estrada.jid) == estrada_verificar:
            for c in estrada.carros:
                num = Interface.num_estradas - carro.estrada
                if ((carro.direcao == "esquerda" or carro.direcao == "baixo")\
                and( parte_estrada(c) == carro.estrada or parte_estrada(c) == carro.estrada+1)) or\
                ((carro.direcao == "cima" or carro.direcao == "direita")\
                and (parte_estrada(c) == num or\
                     parte_estrada(c) == num-1)):
                    return False

    return True



async def main():
    # Configurações iniciais
    pygame.init()
    Interface.screen = pygame.display.set_mode((Interface.largura, Interface.altura))
    pygame.display.set_caption("Controle de Tráfego")

    # Limpar a tela
    Interface.screen.fill(Interface.Cores.BLACK)
    Interface.desenha_estrada(Interface.Cores.GREY)
    Interface.desenha_semaforos(Interface.semaforo_cinza)

    global semaforos
    semaforos = []

    for i in range(len(Interface.coordenadas_semaforos)): 
        jid = f"semaforo_{i}@localhost"
        password = f"{i}"
        if i in Interface.cima():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_verde, i)
        if i in Interface.baixo():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_verde, i)
        if i in Interface.direita():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_vermelho, i)
        if i in Interface.esquerda():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_vermelho, i)
        semaforos.append(semaforo)
    for semaforo in semaforos:
        await semaforo.start(auto_register=True)

    password = f"central"
    central = CentralAgente("central@localhost", password)
    await central.start(auto_register=True)

    global veiculos_em_circulacao
    global veiculos_iniciados
    global combinacao_letras_utilizadas

    veiculos_iniciados = []
    veiculos_em_circulacao = set()
    combinacao_letras_utilizadas = set()

    global ambiente

    estradas = [Estrada(f"estrada_cima_{i}@localhost") for i in range(Interface.num_estradas)] + \
               [Estrada(f"estrada_baixo_{i}@localhost") for i in range(Interface.num_estradas)] + \
               [Estrada(f"estrada_esquerda_{i}@localhost") for i in range(Interface.num_estradas)] + \
               [Estrada(f"estrada_direita_{i}@localhost") for i in range(Interface.num_estradas)]

    ambiente = Ambiente(estradas)

    global limites_cima
    global limites_baixo
    global limites_direita
    global limites_esquerda

    limites_cima = limites("cima")
    limites_baixo = limites("baixo")
    limites_direita = limites("direita")
    limites_esquerda = limites("esquerda")

    await gera_veiculos()

    # Loop principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

if __name__ == "__main__":
    spade.run(main())
