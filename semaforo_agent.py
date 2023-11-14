import asyncio
import spade
import asyncio
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import Trabalho_Interface
import sys
import pygame
import time
import math


class TrafficLightAgent(Agent):
    def __init__(self, jid, password, coordenadas, cor, posicao, screen):
        super().__init__(jid, password)
        self.cor = cor
        self.x = coordenadas[0]
        self.y = coordenadas[1]
        self.posicao = posicao
        self.screen = screen
        print("{} cor: {}".format(str(self.jid), cor.cor))

    class MyBehav(CyclicBehaviour):
        async def run(self):
            # Muda para verde
            if self.agent.cor == Trabalho_Interface.semaforo_vermelho:
                await asyncio.sleep(10)
                self.agent.cor = Trabalho_Interface.semaforo_verde

            # Muda para amarelo
            elif self.agent.cor == Trabalho_Interface.semaforo_verde:
                await asyncio.sleep(10)
                self.agent.cor = Trabalho_Interface.semaforo_amarelo

            # Muda para vermelho
            elif self.agent.cor == Trabalho_Interface.semaforo_amarelo:
                await asyncio.sleep(2)
                self.agent.cor = Trabalho_Interface.semaforo_vermelho

            Trabalho_Interface.liga_semaforo(self.agent.screen, self.agent.posicao, self.agent.cor)
            pygame.display.update()

    async def setup(self):
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)

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

        Trabalho_Interface.desenha_estrada(screen, Trabalho_Interface.Cores.GREY)
        Trabalho_Interface.desenha_semaforos(screen, Trabalho_Interface.semaforo_cinza)

        semaforos = []
        for i in range(len(Trabalho_Interface.coordenadas_semaforos)):
            jid = f"semaforo_{i}@localhost"
            password = f"{i}"
            semaforo = TrafficLightAgent(jid, password, Trabalho_Interface.coordenadas_semaforos[i], Trabalho_Interface.semaforo_verde, i, screen)
            semaforos.append(semaforo)

        
        await semaforos[2].start()
        while not semaforos[2].my_behav.is_killed():
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        assert semaforos[2].my_behav.exit_code == 10
        await semaforos[2].stop()

        #await asyncio.gather(*(semaforo.start() for semaforo in semaforos))

        pygame.display.update()

if __name__ == "__main__":
    spade.run(main())
