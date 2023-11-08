import spade
import asyncio
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import Trabalho_Interface
import sys
import pygame
import time
import math

class TrafficLightAgent(Agent):
    def __init__(self, jid, password, coordenadas, cor):
        self.cor = cor
        self.x = coordenadas[0]
        self.y = coordenadas[1]

    def muda_cor(self, cor):
        if self.cor == Trabalho_Interface.semaforo_verde:
            self.cor = Trabalho_Interface.semaforo_amarelo
        if self.cor == Trabalho_Interface.semaforo_amarelo:
            self.cor = Trabalho_Interface.semaforo_vermelho
        else:
            self.cor = Trabalho_Interface.semaforo_verde

class CarAgent(Agent):
    def __init__(self, jid, password, carro, direcao, screen):
        super().__init__(jid, password)
        self.carro = carro
        self.screen = screen
        self.direcao = direcao

    class MyBehav(CyclicBehaviour):
        async def run(self):
            renova(self.agent.screen)
            if self.agent.carro.x >= Trabalho_Interface.largura\
            or self.agent.carro.y >= Trabalho_Interface.altura\
            or self.agent.carro.x < 0 or self.agent.carro.y < 0:
                self.kill(exit_code=10)
                return
            if self.agent.direcao == "direita":
                if self.agent.carro.x in Trabalho_Interface.paragem_carro(self.agent.direcao):
                    semaforo = identifica_semaforo(self.agent.carro.x, self.agent.carro.y, self.agent.direcao)
                    time.sleep(5)
                self.agent.carro.x += 1
            if self.agent.direcao == "esquerda":
                if self.agent.carro.x in Trabalho_Interface.paragem_carro(self.agent.direcao):
                    semaforo = identifica_semaforo(self.agent.carro.x, self.agent.carro.y, self.agent.direcao)
                    time.sleep(5)
                self.agent.carro.x -= 1
            if self.agent.direcao == "cima":
                if self.agent.carro.y in Trabalho_Interface.paragem_carro(self.agent.direcao):
                    semaforo = identifica_semaforo(self.agent.carro.x, self.agent.carro.y, self.agent.direcao)
                    time.sleep(5)
                self.agent.carro.y -= 1
            if self.agent.direcao == "baixo":
                if self.agent.carro.y in Trabalho_Interface.paragem_carro(self.agent.direcao):
                    semaforo = identifica_semaforo(self.agent.carro.x, self.agent.carro.y, self.agent.direcao)
                    time.sleep(5)
                self.agent.carro.y += 1
            Trabalho_Interface.desenha_carro(self.agent.screen, self.agent.carro, self.agent.direcao)
            pygame.display.update()


    async def setup(self):
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)

def renova(screen):
    Trabalho_Interface.desenha_estrada(screen, Trabalho_Interface.Cores.GREY)
    Trabalho_Interface.desenha_semaforos(screen, Trabalho_Interface.semaforo_cinza)

def identifica_semaforo(x, y, direcao):
    lista_coord = []
    if direcao=="cima" or direcao=="baixo":
        lista_y = []
        for i in range(len(Trabalho_Interface.coordenadas_semaforos)):
            if y-Trabalho_Interface.tamanho_semaforo//2 == Trabalho_Interface.coordenadas_semaforos[i][1]\
            and direcao=="cima" and i in Trabalho_Interface.cima():
                lista_y.append(i)
                lista_coord.append(Trabalho_Interface.coordenadas_semaforos[i])
            if y+Trabalho_Interface.tamanho_semaforo//2 == Trabalho_Interface.coordenadas_semaforos[i][1]\
            and direcao=="baixo" and i in Trabalho_Interface.baixo():
                lista_y.append(i)
                lista_coord.append(Trabalho_Interface.coordenadas_semaforos[i])
        distancia_min_x = abs(lista_coord[0][0] - x)
        pos = lista_y[0]
        for i in range(len(lista_coord)):
            distancia = abs(lista_coord[i][0] - x)
            if distancia < distancia_min_x:
                distancia_min_x = distancia
                pos = lista_y[i]
    if direcao=="esquerda" or direcao=="direita":
        lista_x = []
        for i in range(len(Trabalho_Interface.coordenadas_semaforos)):
            if x-Trabalho_Interface.tamanho_semaforo//2 == Trabalho_Interface.coordenadas_semaforos[i][0]\
            and direcao=="esquerda" and i in Trabalho_Interface.direita():
                lista_x.append(i)
                lista_coord.append(Trabalho_Interface.coordenadas_semaforos[i])
            if x+Trabalho_Interface.tamanho_semaforo//2 == Trabalho_Interface.coordenadas_semaforos[i][0]\
            and direcao=="direita" and i in Trabalho_Interface.esquerda():
                lista_x.append(i)
                lista_coord.append(Trabalho_Interface.coordenadas_semaforos[i])
        distancia_min_y = abs(lista_coord[0][1] - y)
        pos = lista_x[0]
        for i in range(len(lista_coord)):
            distancia = abs(lista_coord[i][1] - y)
            if distancia < distancia_min_y:
                distancia_min_y = distancia
                pos = lista_x[i]
    return pos

async def main():
    # Configurações iniciais
    pygame.init()
    screen = pygame.display.set_mode((Trabalho_Interface.largura, Trabalho_Interface.altura))
    pygame.display.set_caption("Controle de Tráfego")

    # Loop principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Limpar a tela
        screen.fill(Trabalho_Interface.Cores.BLACK)

        #Agentes
        carro_vermelho = CarAgent("carro_vermelho@localhost", "red", Trabalho_Interface.carro_vermelho, "direita", screen)
        carro_azul = CarAgent("carro_azul@localhost", "blue", Trabalho_Interface.carro_azul, "cima", screen)
        carro_preto = CarAgent("carro_preto@localhost", "black", Trabalho_Interface.carro_preto, "baixo", screen)

        Trabalho_Interface.desenha_estrada(screen, Trabalho_Interface.Cores.GREY)
        Trabalho_Interface.desenha_semaforos(screen, Trabalho_Interface.semaforo_cinza)
        Trabalho_Interface.liga_semaforo(screen, 17, Trabalho_Interface.semaforo_amarelo)

        Trabalho_Interface.inicia_carro(screen, Trabalho_Interface.carro_vermelho, 1, carro_vermelho.direcao)
        Trabalho_Interface.inicia_carro(screen, Trabalho_Interface.carro_azul, 2, carro_azul.direcao)
        Trabalho_Interface.inicia_carro(screen, Trabalho_Interface.carro_preto, 1, carro_preto.direcao)
        #print(Trabalho_Interface.coordenadas_semaforos)

        semaforos = []
        for i in range(len(Trabalho_Interface.coordenadas_semaforos)):
            jid = f"semaforo_{i}@localhost"
            password = f"{i}"
            semaforo = TrafficLightAgent(jid, password, Trabalho_Interface.coordenadas_semaforos[i], Trabalho_Interface.semaforo_verde)
            semaforos.append(semaforo)

        for semaforo in semaforos:
            semaforo.start()

        await carro_vermelho.start()
        while not carro_vermelho.my_behav.is_killed():
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        assert carro_vermelho.my_behav.exit_code == 10
        await carro_vermelho.stop()

        await carro_azul.start()
        while not carro_azul.my_behav.is_killed():
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        assert carro_azul.my_behav.exit_code == 10
        await carro_azul.stop()

        await carro_preto.start()
        while not carro_preto.my_behav.is_killed():
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        assert carro_preto.my_behav.exit_code == 10
        await carro_preto.stop()

        pygame.display.update()

if __name__ == "__main__":
    spade.run(main())
