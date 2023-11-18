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

    class MyBehav(CyclicBehaviour):
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
            while msg.body != str(self.agent.posicao):
                msg = await self.receive(timeout=100)

            # Aguarda até que o semáforo fique verde
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

    async def setup(self):
        print("{} começou".format(str(self.jid)))
        Interface.liga_semaforo(self.posicao, self.cor)
        pygame.display.update()
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


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
            if ((self.agent.direcao == "cima" or self.agent.direcao == "baixo")and\
            self.agent.y in Interface.paragem_carro(self.agent.direcao)) or\
            ((self.agent.direcao == "direita" or self.agent.direcao == "esquerda") and\
            self.agent.x in Interface.paragem_carro(self.agent.direcao)):
                    self.agent.estado = 0
                    semaforo = identifica_semaforo(self.agent.x, self.agent.y, self.agent.direcao)
                    msg = Message(to=f"semaforo_{semaforo}@localhost")
                    msg.set_metadata("performative", "inform")
                    msg.body = str(semaforo)
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
            await asyncio.sleep(0.02)
            pygame.display.update()

    async def setup(self):
        print("{} começou".format(str(self.jid)))
        pygame.display.update()
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)

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


#Identifica a posicao do semáforo onde o carro está parado
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

def gerar_combinacao_aleatoria(combinacoes_utilizadas):
    while True:
        combinacao_letras = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
        if combinacao_letras not in combinacoes_utilizadas:
            return combinacao_letras

async def gera_veiculos():
    while True:
        carros_interface = [Interface.carro_vermelho, Interface.carro_azul, Interface.carro_preto]
        password = "password"
        direcoes = ["cima", "baixo", "direita", "esquerda"]
        combinacoes_utilizadas = set()
        num_carros = random.randint(Interface.num_linhas, 2*Interface.num_linhas)
        while num_carros > 0:
            carro_interface = random.choice(carros_interface)
            direcao = random.choice(direcoes)
            pos_estrada = random.randint(0, Interface.num_linhas - 1)

            # Verifica se a combinação estrada-direcao já está em uso
            combinacao_atual = (pos_estrada, direcao)
            if combinacao_atual not in combinacoes_utilizadas:
                jid = gerar_combinacao_aleatoria(combinacoes_utilizadas)
                combinacoes_utilizadas.add(combinacao_atual)

                # Agentes
                x, y = 0, 0
                carro = CarroAgente(f"{jid}@localhost", password, carro_interface, direcao, x, y, pos_estrada)
                veiculos_em_circulacao.add(carro)
                Interface.inicia_carro(carro)
                num_carros -= 1
                Interface.desenha_carro(carro)
                jid_estrada = f"estrada_{direcao}_{pos_estrada}@localhost"
                for estrada in estradas:
                    if str(estrada.jid) == jid_estrada:
                        estrada.carros.append(carro)
                pygame.display.update()
        await agentes()
        pygame.display.update()
        await asyncio.sleep(3)
        for carro in veiculos_em_circulacao:
            if carro.anterior!=None:
                ant = str(carro.anterior.jid)
            else:
                ant = "None"
            print(f"Estado do veículo {carro.jid}: x={carro.x}, y={carro.y}, direcao={carro.direcao}, estado={carro.estado}, carro anterior={ant}")
#Inicia os agentes ao mesmo tempo, se ja nao tiverem sido iniciados
async def agentes():
    for veiculo in veiculos_em_circulacao:
        if veiculo not in veiculos_iniciados:
            await veiculo.start()
            veiculos_iniciados.append(veiculo)

async def print_veiculos_info():
    while True:
        for carro in veiculos_em_circulacao:
            if carro.anterior is not None:
                ant = str(carro.anterior.jid)
            else:
                ant = "None"
            print(f"Estado do veículo {carro.jid}: x={carro.x}, y={carro.y}, direcao={carro.direcao}, estado={carro.estado}, carro anterior={ant}")
        await asyncio.sleep(1)

async def main():
    # Configurações iniciais
    pygame.init()
    Interface.screen = pygame.display.set_mode((Interface.largura, Interface.altura))
    pygame.display.set_caption("Controle de Tráfego")
    # Limpar a tela
    Interface.screen.fill(Interface.Cores.BLACK)

    Interface.desenha_estrada(Interface.Cores.GREY)
    Interface.desenha_semaforos(Interface.semaforo_cinza)

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
    global combinacoes_utilizadas
    veiculos_iniciados = []
    veiculos_em_circulacao = set()

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
    carro1 = CarroAgente("vermelho@localhost", "red", Interface.carro_vermelho, "cima", x, y, 2)
    carro2 = CarroAgente("preto@localhost", "black", Interface.carro_preto, "esquerda", x, y, 0)
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
        await asyncio.sleep(4)
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
        asyncio.create_task(print_veiculos_info())'''

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
