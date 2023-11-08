#definir agente de semaforo: cada agente de transito gere a luz do mesmo(vermelho, amarelo, verde)
#definir agentes de veiculos: tem que se aproximar das intersecoes e reagir aos semaforos. podem relatar o tempo de espera
#coordenacao: coordenao entre os agentes de semaforos para otimizar o fluxo
#prioridade para veiculos de emergencia: ambulancias, policia e bombeiros



#criar agente semaforo

import asyncio
import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour



import asyncio
import spade
from spade import wait_for_agents
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class TrafficLightAgent(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour...")
            print("Traffic Light Agent is starting.")
            self.state = 0  # 0->vermelho 1->verde

        async def run(self):
            if self.state == 0:
                print("Red Light")
                self.state = 1
                await asyncio.sleep(5)
            else:
                print("Green Light")
                self.state = 0
                await asyncio.sleep(5)

    async def setup(self):
        print("Agente starting...")
        b = self.MyBehav()
        self.add_behaviour(b)

class CarAgent(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting Behaviour...")
            print("Car Agent is starting.")
            self.carstate = 0  # 0->not moving #1->moving

        async def run(self):
            print("Car is approaching the intersection")
            request = spade.message.Message(to="traffic1@localhost", body="Request Green Light")
            await self.send(request)
            response = await self.receive(timeout=5)

            if response:
                print(f"Received response: {response.body}")
                if response.body == "Green Light Granted":
                    print("Car can pass the intersection.")
                else:
                    print("Car must wait for the green light.")
            else:
                print("No response received. Car must wait.")

    async def setup(self):
        print("Car Agent starting...")
        b = self.MyBehav()
        self.add_behaviour(b)

async def main():
    traffic_light_agent = TrafficLightAgent("traffic1@localhost", "password1")
    await traffic_light_agent.start()

    car_agent = CarAgent("car1@localhost", "password2")
    await car_agent.start()

    print("Traffic Light Agent and Car Agent started. Check their consoles for the output.")
    print("Wait until the user interrupts with Ctrl+C")

if __name__ == "__main__":
    spade.run(main())

# class TrafficLightAgent(Agent):
#     class MyBehav(CyclicBehaviour):
#         async def on_start(self):
#             print("Starting behaviour...")
#             print(f"Traffic Light Agent is starting.")
#             self.state=0 #0->vermelhor 1->verde
        
#         async def run(self):
#             if self.state==0:
#                 print("Red Light")
#                 self.state=1
#                 await asyncio.sleep(5)
#             else:
#                 print("Green Light")
#                 self.state=0
#                 await asyncio.sleep(5)
#     async def setup(self):
#         print("Agente starting...")
#         b=self.MyBehav()
#         self.add_behaviour(b)
        
# class CarAgent(Agent):
#     class MyBehav(CyclicBehaviour):
#         async def on_start(self):
#             print("Starting Behaviour...")
#             print(f"Car Agent is starting.")
#             self.carstate=0 #0->not moving #1->moving
#         async def run(self):
#             print("Car is approching the intersection")
#             request = spade.message.Message(to="traffic1@localhost", body="Request Green Light")
#             await self.send(request)
#             response = await self.receive(timeout=5)  # Aguarde uma resposta por até 5 segundos

#             if response:
#                 print(f"Received response: {response.body}")
#                 if response.body == "Green Light Granted":
#                     print("Car can pass the intersection.")
#                 else:
#                     print("Car must wait for the green light.")
#             else:
#                 print("No response received. Car must wait.")

#     async def setup(self):
#         print("Car Agent starting...")
#         b = self.MyBehav() 
#         self.add_behaviour(b)
             
# async def main():
#     Traffic_LightAgent1 = TrafficLightAgent("traffic1@localhost", "password1")
#     await Traffic_LightAgent1.start()
#     print("TrafficAgent started. Check its console to see the output")
#     print("Wait until the user interrupts with ctrl+C")
#     await wait_until_finished(Traffic_LightAgent1)

#     car_agent = CarAgent("car1@localhost", "password2")
#     await car_agent.start()

#     print("Traffic Light Agent and Car Agent started. Check their consoles for the output.")
#     print("Wait until the user interrupts with Ctrl+C")

#     while True:
#         # Aqui, você pode adicionar a lógica para iniciar o comportamento do carro
#         await asyncio.sleep(1)  # Adicione um pequeno atraso
#         await car_agent.MyBehav().on_start()
#         await car_agent.MyBehav().run()

# if __name__ == "__main__":
#     spade.run(main())
 
        
# # async def main():
# #     Traffic_LightAgent1=TrafficLightAgent("traffic1@localhost","password1")
# #     await Traffic_LightAgent1.start()
# #     print("TrafficAgent started. Check its console to see the output")
# #     print("Wait until user interrups with ctrl+C")
# #     await wait_until_finished(Traffic_LightAgent1)
    
# #     car_agent = CarAgent("car1@localhost", "password2")

# #     await car_agent.start()

# #     print("Traffic Light Agent and Car Agent started. Check their consoles for the output.")
# #     print("Wait until the user interrupts with Ctrl+C")
# #     await wait_until_finished(Traffic_LightAgent1)
# #     await wait_until_finished(car_agent)

    
# # if __name__ =="__main__":
# #     spade.run(main())
    






