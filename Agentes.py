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

#Agente semáforo
class TrafficLightAgent(Agent):
    def __init__(self, jid, password, coordenadas, cor, posicao):
        super().__init__(jid, password)
        self.cor = cor
        self.x = coordenadas[0]
        self.y = coordenadas[1]
        self.posicao = posicao

    class MyBehav(CyclicBehaviour):
        async def run(self):
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

            Interface.liga_semaforo(self.agent.posicao, self.agent.cor)
            pygame.display.update()
            await asyncio.sleep(0.1)  # Garante que o loop seja assíncrono


    class RecvBehav(OneShotBehaviour):
        async def run(self):
            # Agora o semáforo está verde, pode responder
            msg = await self.receive(timeout=500)
            if msg:
                print("Mensagem recebida: {}".format(msg.body))

            # Aguarda até que o semáforo fique verde
            while self.agent.cor != Interface.semaforo_verde:
                pygame.display.update()
                print('A aguardar que o semáforo fique verde...')
                await asyncio.sleep(1)
            if msg:
                reply_body = "A luz está verde. Pode avançar!"

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


class CarAgent(Agent):
    def __init__(self, jid, password, carro, direcao):
        super().__init__(jid, password)
        self.carro = carro
        self.direcao = direcao

    class MyBehav(CyclicBehaviour):
        async def run(self):
            if self.agent.carro.x >= Interface.largura\
            or self.agent.carro.y >= Interface.altura\
            or self.agent.carro.x < - Interface.alt_carro or self.agent.carro.y < - Interface.alt_carro:
                self.kill(exit_code=10)
                return
            prev_x, prev_y = self.agent.carro.x, self.agent.carro.y
            if self.agent.direcao == "cima" or self.agent.direcao == "baixo":
                if self.agent.carro.y in Interface.paragem_carro(self.agent.direcao):
                    semaforo = identifica_semaforo(self.agent.carro.x, self.agent.carro.y, self.agent.direcao)
                    msg = Message(to=f"semaforo_{semaforo}@localhost")
                    msg.set_metadata("performative", "inform")
                    msg.body = f"Carro parado no semáforo {semaforo}. Pode avançar?"
                    await self.send(msg)
                    reply = await self.receive(timeout=20)
                    print(f"Mensagem recebida: {reply.body}")
            if self.agent.direcao == "direita" or self.agent.direcao == "esquerda":
                if self.agent.carro.x in Interface.paragem_carro(self.agent.direcao):
                    semaforo = identifica_semaforo(self.agent.carro.x, self.agent.carro.y, self.agent.direcao)
                    msg = Message(to=f"semaforo_{semaforo}@localhost")
                    msg.set_metadata("performative", "inform")
                    msg.body = f"Carro parado no semáforo {semaforo}. Pode avançar?"
                    await self.send(msg)
                    reply = await self.receive(timeout=20)
                    print(f"Mensagem recebida: {reply.body}")
            if self.agent.direcao == "direita":
                self.agent.carro.x += 1
                pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.alt_carro, Interface.larg_carro))
            elif self.agent.direcao == "esquerda":
                self.agent.carro.x -= 1
                pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.alt_carro, Interface.larg_carro))
            elif self.agent.direcao == "cima":
                self.agent.carro.y -= 1
                pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.larg_carro, Interface.alt_carro))
            elif self.agent.direcao == "baixo":
                self.agent.carro.y += 1
                pygame.draw.rect(Interface.screen, Interface.Cores.GREY, (prev_x, prev_y, Interface.larg_carro, Interface.alt_carro))

            Interface.desenha_carro(self.agent.carro, self.agent.direcao)
            pygame.display.update()
            await asyncio.sleep(0.01)

    async def setup(self):
        print("{} começou".format(str(self.jid)))
        pygame.display.update()
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)

#Identifica a posicao do semáforo onde o carro está parado
def identifica_semaforo(x, y, direcao):
    lista_coord = []
    if direcao=="cima" or direcao=="baixo":
        lista_y = []
        for i in range(len(Interface.coordenadas_semaforos)):
            if int(y-Interface.tamanho_semaforo//2) == int(Interface.coordenadas_semaforos[i][1])\
            and direcao=="cima" and i in Interface.cima():
                lista_y.append(i)
                lista_coord.append(Interface.coordenadas_semaforos[i])
            if int(y+Interface.tamanho_semaforo//2) == int(Interface.coordenadas_semaforos[i][1])\
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
            if int(x-Interface.tamanho_semaforo//2) == int(Interface.coordenadas_semaforos[i][0])\
            and direcao=="esquerda" and i in Interface.direita():
                lista_x.append(i)
                lista_coord.append(Interface.coordenadas_semaforos[i])
            if int(x+Interface.tamanho_semaforo//2) == int(Interface.coordenadas_semaforos[i][0])\
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

#Inicia os agentes ao mesmo tempo e para-os
async def agentes(semaforos, carros):
    for semaforo in semaforos:
        await semaforo.start()
    for carro in carros:
        await carro.start()
    i = 0
    while len(carros)>0:
        if i==len(carros):
            i = 0
        if not carros[i].my_behav.is_killed():
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        else:
            assert carros[i].my_behav.exit_code == 10
            await carros[i].stop()
            carros.remove(carros[i])
        i +=1
    for semaforo in semaforos:
        await semaforo.stop()


async def main():
    # Configurações iniciais
    pygame.init()
    Interface.screen = pygame.display.set_mode((Interface.largura, Interface.altura))
    pygame.display.set_caption("Controle de Tráfego")
    # Limpar a tela
    Interface.screen.fill(Interface.Cores.BLACK)

    #Agentes
    carro_vermelho = CarAgent("carro_vermelho@localhost", "red", Interface.carro_vermelho, "direita")
    carro_azul = CarAgent("carro_azul@localhost", "blue", Interface.carro_azul, "cima")
    carro_preto = CarAgent("carro_preto@localhost", "black", Interface.carro_preto, "baixo")
    carros = [carro_azul, carro_preto, carro_vermelho]

    Interface.inicia_carro(Interface.carro_vermelho, 1, carro_vermelho.direcao)
    Interface.inicia_carro(Interface.carro_azul, 2, carro_azul.direcao)
    Interface.inicia_carro(Interface.carro_preto, 1, carro_preto.direcao)

    Interface.desenha_estrada(Interface.Cores.GREY)
    Interface.desenha_semaforos(Interface.semaforo_cinza)
    semaforos = []
    for i in range(len(Interface.coordenadas_semaforos)):
        jid = f"semaforo_{i}@localhost"
        password = f"{i}"
        if i in Interface.cima():
            semaforo = TrafficLightAgent(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_verde, i)
        if i in Interface.baixo():
            semaforo = TrafficLightAgent(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_verde, i)
        if i in Interface.esquerda():
            semaforo = TrafficLightAgent(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_vermelho, i)
        if i in Interface.direita():
            semaforo = TrafficLightAgent(jid, password, Interface.coordenadas_semaforos[i], Interface.semaforo_amarelo, i)
        semaforos.append(semaforo)

    await agentes(semaforos, carros)
    pygame.display.update()

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
