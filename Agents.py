import spade
import asyncio
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import Trabalho_Interface
import sys
import pygame

class SinalAgent(Agent):
    class SinalBehaviour(CyclicBehaviour):
        pass

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
                self.agent.carro.x += 1
            if self.agent.direcao == "esquerda":
                self.agent.carro.x -= 1
            if self.agent.direcao == "cima":
                self.agent.carro.y -= 1
            if self.agent.direcao == "baixo":
                self.agent.carro.y += 1
            Trabalho_Interface.desenha_carro(self.agent.screen, self.agent.carro, self.agent.direcao)
            pygame.display.update()


    async def setup(self):
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)

def renova(screen):
    Trabalho_Interface.desenha_estrada(screen, Trabalho_Interface.Cores.GREY)
    Trabalho_Interface.desenha_semaforos(screen, Trabalho_Interface.semaforo_cinza)

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

        await carro_vermelho.start()
        await carro_azul.start()
        while not carro_vermelho.my_behav.is_killed():
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        assert carro_vermelho.my_behav.exit_code == 10
        await carro_vermelho.stop()

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
