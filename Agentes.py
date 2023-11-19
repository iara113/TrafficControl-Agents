import spade
import asyncio
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import Interface
import sys
import pygame
import time
import math
import random
import string

class Ambiente():
    def __init__(self, jid, carros=None):
        self.jid = jid
        self.carros = carros if carros is not None else []

#Agente semáforo
class SemaforoAgente(Agent):
    def __init__(self, jid, password, coordenadas, cor, posicao):
        super().__init__(jid, password)
        self.cor = cor
        self.x = coordenadas[0]
        self.y = coordenadas[1]
        self.posicao = posicao

    class MensagemCentral(CyclicBehaviour):
        async def run(self):
            Interface.liga_semaforo(self.agent.posicao, self.agent.cor)
            pygame.display.update()
            # Muda para verde
            if self.agent.cor == Interface.semaforo_vermelho:
                await asyncio.sleep(10)
                self.agent.cor = Interface.semaforo_verde

            # Muda para amarelo
            elif self.agent.cor == Interface.semaforo_verde:
                await asyncio.sleep(10)
                self.agent.cor = Interface.semaforo_amarelo

            # Muda para vermelho
            elif self.agent.cor == Interface.semaforo_amarelo:
                await asyncio.sleep(2)
                self.agent.cor = Interface.semaforo_vermelho

            await asyncio.sleep(0)  # Garante que o loop seja assíncrono


    class RecvBehav(CyclicBehaviour):
        async def run(self):
            # Agora o semáforo está verde, pode responder
            msg = await self.receive(timeout=500)
            #Só recebe mensagens de carros
            while msg.body != str(self.agent.posicao) and not msg.body.startswith("estrada_"):
                msg = await self.receive(timeout=100)

            # É um carroo: aguarda até que o semáforo fique verde
            if msg.body == str(self.agent.posicao):
                while self.agent.cor != Interface.semaforo_verde:
                    pygame.display.update()
                    print(f'O carro {str(msg.sender)} está a aguardar que o semáforo {self.agent.posicao} fique verde...')
                    await asyncio.sleep(1)
                if msg:
                    reply_body = f"A luz está verde no semáforo {self.agent.posicao}. Pode avançar!"

                    # Manda  mensagem para o carro
                    reply = Message(to=str(msg.sender))
                    reply.set_metadata("performative", "inform")
                    reply.body = reply_body
                    await self.send(reply)

            # É uma ambulancia: aguarda até que o semáforo fique verde ou nao tenha nenhum carro na intersecao
            if msg.body.startswith("estrada_"):
                for estrada in estradas:
                    if str(estrada.jid) == msg.body:
                        for c in estrada.carros:
                            if str(c.jid) == str(msg.sender):
                                ambulancia = c
                while self.agent.cor != Interface.semaforo_verde and ambulancia_para(ambulancia):
                    pygame.display.update()
                    print(f'A ambulancia {str(msg.sender)} está a aguardar que o semáforo {self.agent.posicao} fique verde ou que não tenha carros a passar...')
                    await asyncio.sleep(1)
                if msg:
                    if self.agent.cor == Interface.semaforo_verde:
                        reply_body = f"A luz está verde no semáforo {self.agent.posicao}. Pode avançar!"
                    else:
                        reply_body = f"Não está nenhum carro a passar. A ambulancia {self.agent.posicao} pode avançar!"

                    # Manda  mensagem para o carro
                    reply = Message(to=str(msg.sender))
                    reply.set_metadata("performative", "inform")
                    reply.body = reply_body
                    await self.send(reply)

    async def setup(self):
        print("{} começou".format(str(self.jid)))
        Interface.liga_semaforo(self.posicao, self.cor)
        pygame.display.update()
        '''self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)'''
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
        c = self.MensagemCentral()
        self.add_behaviour(c, template)


class CarroAgente(Agent):
    def __init__(self, jid, password, carro, direcao, x, y, estrada, estado=0, anterior=None):
        super().__init__(jid, password)
        self.carro = carro
        self.direcao = direcao
        self.x = x
        self.y = y
        self.estrada = estrada
        self.estado = estado
        self.anterior = anterior

    class MyBehav(CyclicBehaviour):
        async def run(self):
            self.agent.estado = 1
            if self.agent.x > Interface.largura\
            or self.agent.y > Interface.altura\
            or self.agent.x < - Interface.alt_carro or self.agent.y < - Interface.alt_carro:
                veiculos_em_circulacao.remove(self.agent)
                jid_estrada =  f"estrada_{self.agent.direcao}_{self.agent.estrada}@localhost"
                for estrada in estradas:
                    if str(estrada.jid) == jid_estrada:
                        estrada.carros.remove(self.agent)
                self.agent.estado = 0
                await self.agent.stop()
                self.kill(exit_code=10)
                return
            prev_x, prev_y = self.agent.x, self.agent.y
            jid_estrada =  f"estrada_{self.agent.direcao}_{self.agent.estrada}@localhost"
            veiculo_frente = veiculo_a_frente(self.agent)
            if veiculo_frente != None and veiculo_frente.estado==0 and\
            ((self.agent.direcao=="direita" and self.agent.x == veiculo_frente.x - Interface.alt_carro - 0.1*Interface.alt_carro) or\
            (self.agent.direcao=="esquerda" and self.agent.x == veiculo_frente.x + Interface.alt_carro + 0.1*Interface.alt_carro) or\
            (self.agent.direcao=="cima" and self.agent.y == veiculo_frente.y + Interface.alt_carro + 0.1*Interface.alt_carro) or\
            (self.agent.direcao=="baixo" and self.agent.y == veiculo_frente.y - Interface.alt_carro - 0.1*Interface.alt_carro)):
                self.agent.estado = 0
                veiculo_frente.anterior = self.agent
            if (((self.agent.direcao == "cima" or self.agent.direcao == "baixo")and\
            self.agent.y in Interface.paragem_carro(self.agent.direcao)) or\
            ((self.agent.direcao == "direita" or self.agent.direcao == "esquerda") and\
            self.agent.x in Interface.paragem_carro(self.agent.direcao))) and\
            (self.agent.carro.tipo != "ambulance" or ambulancia_para(self.agent)):
                    self.agent.estado = 0
                    semaforo = identifica_semaforo(self.agent.x, self.agent.y, self.agent.direcao)
                    msg = Message(to=f"semaforo_{semaforo}@localhost")
                    msg.set_metadata("performative", "inform")
                    if self.agent.carro.tipo == "carro":
                        msg.body = str(semaforo)
                    else:
                        msg.body = jid_estrada
                    await self.send(msg)
                    #Só recebe respostas do semaforo em que está parado
                    reply = await self.receive(timeout=100)
                    while str(reply.sender) != f"semaforo_{semaforo}@localhost":
                        reply = await self.receive(timeout=100)
                    print(f"Mensagem recebida pelo carro {str(self.agent.jid)}: {reply.body}")
                    self.agent.estado = 1
                    if self.agent.anterior == 0:
                        self.agent.anterior.estado = 1
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
        print("{} começou".format(str(self.jid)))
        pygame.display.update()
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)

'''class CentralAgente(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)

    class MyBehav(CyclicBehaviour):
        async def run(self):
            # Process messages received by the central agent
            msg = await self.receive(timeout=1000)  # Timeout of 1000ms (1 second)
            if msg:
                performative = msg.get_metadata("performative")

                if performative == "inform" and "semaphore_data" in msg.body:
                    # Process data received from Traffic Light Agents
                    semaphore_data = msg.body["semaphore_data"]
                    print(f"Central received semaphore data: {semaphore_data}")

                    # You can add coordination logic here based on semaphore data

                elif performative == "request" and "vehicle_data" in msg.body:
                    # Process data received from Vehicle Agents
                    vehicle_data = msg.body["vehicle_data"]
                    print(f"Central received vehicle data: {vehicle_data}")

                    # You can add coordination logic here based on vehicle data

    async def setup(self):
        print("{} começou".format(str(self.jid)))
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)'''

#Limites para cada parte da estrada
def limites(direcao):
    limites_set = set()
    for i in range(len(Interface.coordenadas_semaforos)):
        if direcao == "cima" and i in Interface.cima():
            limites_set.add(Interface.coordenadas_semaforos[i][1])
        elif direcao == "baixo" and i in Interface.baixo():
            limites_set.add(Interface.coordenadas_semaforos[i][1])
        elif direcao == "esquerda" and i in Interface.direita():
            limites_set.add(Interface.coordenadas_semaforos[i][0])
        elif direcao == "direita" and i in Interface.esquerda():
            limites_set.add(Interface.coordenadas_semaforos[i][0])

    limites_sorted = sorted(list(limites_set), reverse=(direcao in ["cima", "esquerda"]))
    return limites_sorted

#Retorna a parte da estrada onde o carro se encontra
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
    return Interface.num_linhas

#Se tiver algum veiculo à frente do carro, retorna qual é
def veiculo_a_frente(carro):
    jid_estrada = f"estrada_{carro.direcao}_{carro.estrada}@localhost"
    possiveis = []
    parte_carro = parte_estrada(carro)
    for estrada in estradas:
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


# Retorna true se a ambulancia tiver que parar porque vêm carros do lado
def ambulancia_para(ambulancia):
    parte_ambulancia = parte_estrada(ambulancia)
    aux = Interface.num_linhas-1
    jid_estrada1 = 0
    jid_estrada2 = 0
    if ambulancia.direcao == "direita":
        jid_estrada1= f"estrada_baixo_{parte_ambulancia}@localhost"
        parte_estrada1 = ambulancia.estrada
        if (parte_ambulancia)<Interface.num_linhas:
            jid_estrada2= f"estrada_cima_{parte_ambulancia + 1}@localhost"
            parte_estrada2 = aux - ambulancia.estrada + 1
    elif ambulancia.direcao == "esquerda":
        jid_estrada1= f"estrada_cima_{aux - parte_ambulancia}@localhost"
        parte_estrada1 = aux - ambulancia.estrada
        if (aux - parte_ambulancia - 1)>=0:
            jid_estrada2= f"estrada_baixo_{aux - parte_ambulancia - 1}@localhost"
            parte_estrada2 = ambulancia.estrada + 1
    elif ambulancia.direcao == "cima":
        jid_estrada1= f"estrada_direita_{aux - parte_ambulancia}@localhost"
        parte_estrada1 = ambulancia.estrada
        if (aux - parte_ambulancia - 1)>=0:
            jid_estrada2= f"estrada_esquerda_{aux - parte_ambulancia - 1}@localhost"
            parte_estrada2 = aux - ambulancia.estrada + 1
    elif ambulancia.direcao == "baixo":
        jid_estrada1= f"estrada_esquerda_{parte_ambulancia}@localhost"
        parte_estrada1 = aux - ambulancia.estrada
        if (parte_ambulancia)<Interface.num_linhas:
            jid_estrada2= f"estrada_direita_{parte_ambulancia + 1}@localhost"
            parte_estrada2 = ambulancia.estrada + 1
    for estrada in estradas:
        if str(estrada.jid) == jid_estrada1:
            for c in estrada.carros:
                if (parte_estrada(c) == parte_estrada1 and na_intersecao(c)) or parte_estrada(c) == parte_estrada1-1:
                    return True
    if jid_estrada2 != 0:
        for estrada in estradas:
            if str(estrada.jid) == jid_estrada2:
                for c in estrada.carros:
                    if (parte_estrada(c) == parte_estrada2 and na_intersecao(c)) or parte_estrada(c) == parte_estrada2-1:
                        return True
    return False


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
            and direcao=="esquerda" and i in Interface.direita():
                lista_x.append(i)
                lista_coord.append(Interface.coordenadas_semaforos[i])
            if int(x+Interface.tamanho_semaforo//4) == int(Interface.coordenadas_semaforos[i][0])\
            and direcao=="direita" and i in Interface.esquerda():
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
    while True:
        combinacao_letras = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
        if combinacao_letras not in combinacao_letras_utilizadas:
            return combinacao_letras
        else:
            print(f'Combinação {combinacao_letras} já utilizada. Tentando outra.')

#Gera veiculos aleatoriamente
async def gera_veiculos():
    while True:
        veiculos_interface = [Interface.carro_vermelho, Interface.carro_azul, Interface.carro_preto,\
                            Interface.carro_verde, Interface.mota, Interface.ambulancia]
        password = "password"
        direcoes = ["cima", "baixo", "direita", "esquerda"]
        combinacoes_utilizadas = []
        num_carros = random.randint(Interface.num_linhas, 2*Interface.num_linhas)
        while num_carros > 0:
            carro_interface = random.choice(veiculos_interface)
            direcao = random.choice(direcoes)
            pos_estrada = random.randint(0, Interface.num_linhas - 1)
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
                    for estrada in estradas:
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
            await veiculo.start(auto_register=True)
            veiculos_iniciados.append(veiculo)

'''async def verifica(carro):
    while True:
        #print(parte_estrada(carro))
        print(na_intersecao(carro))
        for carro in veiculos_em_circulacao:
            if carro.anterior is not None:
                ant = str(carro.anterior.jid)
            else:
                ant = "None"
            print(f"Estado do veículo {carro.jid}: x={carro.x}, y={carro.y}, direcao={carro.direcao}, estado={carro.estado}, carro anterior={ant}")'
        await asyncio.sleep(0.1)'''

#Retorna true se um carro se encontrar numa intersecao
def na_intersecao(carro):
    parte_atual = parte_estrada(carro)
    tamanho_preto = (Interface.largura - (Interface.num_linhas*Interface.tamanho_espessura)) // Interface.num_linhas
    if parte_atual==0:
        if carro.direcao == "cima":
            limite_superior = float('+inf')
            limite_inferior = limites_cima[parte_atual] + tamanho_preto
            return limite_inferior <= carro.y <= limite_superior
        elif carro.direcao == "baixo":
            limite_inferior = float('-inf')
            limite_superior = Interface.tamanho_espessura//2
            return limite_inferior <= carro.y <= limite_superior
        elif carro.direcao == "direita":
            limite_direito = Interface.tamanho_espessura//2
            limite_esquerdo =  float('-inf')
            return limite_esquerdo <= carro.x <= limite_direito
        elif carro.direcao == "esquerda":
            limite_esquerdo = limites_esquerda[parte_atual] + tamanho_preto
            limite_direito = float('+inf')
            return limite_esquerdo <= carro.x <= limite_direito
    if parte_atual>0 and parte_atual<Interface.num_linhas:
        if carro.direcao == "cima":
            limite_superior = limites_esquerda[parte_atual-1]
            limite_inferior = limites_esquerda[parte_atual-1] - Interface.tamanho_espessura
            return limite_inferior <= carro.y <= limite_superior
        elif carro.direcao == "baixo":
            limite_inferior = limites_baixo[parte_atual-1]
            limite_superior = limites_baixo[parte_atual-1] + Interface.tamanho_espessura
            return limite_inferior <= carro.y <= limite_superior
        elif carro.direcao == "direita":
            limite_direito = limites_direita[parte_atual-1] + Interface.tamanho_espessura
            limite_esquerdo = limites_direita[parte_atual-1]
            return limite_esquerdo <= carro.x <= limite_direito
        elif carro.direcao == "esquerda":
            limite_esquerdo = limites_esquerda[parte_atual-1] - Interface.tamanho_espessura
            limite_direito = limites_esquerda[parte_atual-1]
            return limite_esquerdo <= carro.x <= limite_direito
    if parte_atual==Interface.num_linhas:
        if carro.direcao == "cima":
            limite_superior = limites_esquerda[parte_atual-1]
            limite_inferior = float('-inf')
            return limite_inferior <= carro.y <= limite_superior
        elif carro.direcao == "baixo":
            limite_inferior = limites_baixo[parte_atual-1]
            limite_superior = float('+inf')
            return limite_inferior <= carro.y <= limite_superior
        elif carro.direcao == "direita":
            limite_direito = float('+inf')
            limite_esquerdo = limites_direita[parte_atual-1]
            return limite_esquerdo <= carro.x <= limite_direito
        elif carro.direcao == "esquerda":
            limite_esquerdo = float('-inf')
            limite_direito = limites_esquerda[parte_atual-1]
            return limite_esquerdo <= carro.x <= limite_direito
    return False

#Retorna false quando algum carro nao pode ser iniciado para nao coicidir com outros que ja estao a andar
def pode_iniciar(carro):
    if carro.direcao == "cima":
        estrada_verificar = f"estrada_esquerda_2@localhost"
    elif carro.direcao == "baixo":
        estrada_verificar = f"estrada_direita_0@localhost"
    elif carro.direcao == "direita":
        estrada_verificar = f"estrada_cima_0@localhost"
    elif carro.direcao == "esquerda":
        estrada_verificar = f"estrada_baixo_2@localhost"
    for estrada in estradas:
        if str(estrada.jid) == estrada_verificar:
            for c in estrada.carros:
                num = Interface.num_linhas - carro.estrada
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

    '''password = f"central"
    central = CentralAgente("central@localhost", password)
    await central.start()'''

    semaforos = []
    for i in range(len(Interface.coordenadas_semaforos)):
        jid = f"semaforo_{i}@localhost"
        password = f"{i}"
        if i in Interface.cima():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_verde, i)
        if i in Interface.baixo():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_verde, i)
        if i in Interface.esquerda():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_vermelho, i)
        if i in Interface.direita():
            semaforo = SemaforoAgente(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_vermelho, i)
        semaforos.append(semaforo)
    for semaforo in semaforos:
        await semaforo.start()

    global veiculos_em_circulacao
    global veiculos_iniciados
    global combinacao_letras_utilizadas

    veiculos_iniciados = []
    veiculos_em_circulacao = set()
    combinacao_letras_utilizadas = set()

    global estradas
    estradas = [Ambiente(f"estrada_cima_{i}@localhost") for i in range(Interface.num_linhas)] + \
               [Ambiente(f"estrada_baixo_{i}@localhost") for i in range(Interface.num_linhas)] + \
               [Ambiente(f"estrada_esquerda_{i}@localhost") for i in range(Interface.num_linhas)] + \
               [Ambiente(f"estrada_direita_{i}@localhost") for i in range(Interface.num_linhas)]

    global limites_cima
    global limites_baixo
    global limites_direita
    global limites_esquerda
    limites_cima = limites("cima")
    limites_baixo = limites("baixo")
    limites_direita = limites("direita")
    limites_esquerda = limites("esquerda")

    '''x, y = 0, 0
    carro2 = CarroAgente("vermelho@localhost", "red", Interface.carro_vermelho, "direita", x, y, 1)
    carro1 = CarroAgente("ambulancia@localhost", "black", Interface.ambulancia, "baixo", x, y, 0)
    carro3 = CarroAgente("azul@localhost", "blue", Interface.carro_azul, "baixo", x, y, 1)
    veiculos_em_circulacao.add(carro1)
    jid_estrada = "estrada_direita_2@localhost"
    Interface.inicia_carro(carro1)
    Interface.inicia_carro(carro2)
    #Interface.inicia_carro(carro3)
    #pygame.display.update()
    while True:
        await asyncio.sleep(6)
        jid_estrada = f"estrada_{carro1.direcao}_{carro1.estrada}@localhost"
        for estrada in estradas:
            if str(estrada.jid) == jid_estrada:
                estrada.carros.append(carro1)
                break
        await agentes()
        #asyncio.create_task(verifica(carro1))
        #await asyncio.sleep(20)
        while not pode_iniciar(carro2):
            await asyncio.sleep(1)
        veiculos_em_circulacao.add(carro2)
        jid_estrada = f"estrada_{carro2.direcao}_{carro2.estrada}@localhost"
        for estrada in estradas:
            if str(estrada.jid) == jid_estrada:
                estrada.carros.append(carro2)
                break
        await agentes()
        #await asyncio.sleep(3)
        #veiculos_em_circulacao.append(carro3)
        #await agentes()
        pygame.display.update()
        #asyncio.create_task(print_veiculos_info())'''

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
