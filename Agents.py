import spade
import asyncio
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import Trabalho


class SinalAgent(Agent):
    class SinalBehaviour(CyclicBehaviour):
        pass
        
    
class CarAgent(Agent):
    class CarBehaviour(CyclicBehaviour): 
        async def on_start(self,x,y):
            #movimento, somar valores as coordenadas
            #velocidade
            
            print("Obter as coordenadas . . .")
            self.x = x
            self.y=y

        async def run(self,direcao):
            #interface(?)
            print("Counter: {}".format(self.counter))
            
            if direcao=="frente":
                self.x += 1
                if self.x > Trabalho.largura:
                    self.kill(exit_code=10)
                    return
            await asyncio.sleep(1)

        async def on_end(self):
            print("Behaviour finished with exit code {}.".format(self.exit_code))

    async def setup(self):
        print("Agent starting . . .")
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav) 
        
        pass
      
async def main():
    
    sinal_vermelho = SinalAgent("vermelho@localhost", "red")
    await sinal_vermelho.start()
    await wait_until_finished(sinal_vermelho)

if __name__ == "__main__":
    spade.run(main())