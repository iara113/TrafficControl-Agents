import sys
import pygame
import spade
import asyncio
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from queue import Queue

#sudo service prosody start

#Cores a serem usadas
class Cores:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    GREY = (128, 128, 128)
    FOREST_GREEN = (34,139,34)

#Medidas Constantes
altura = 600
largura = 600
num_linhas = 3
#espessura da estrada
tamanho_espessura = largura // (num_linhas*3)

#Classe de um Semáforo
class Semaforo():
    def __init__(self, cor, direcao):
        self.cor = cor
        self.direcao = direcao

#Classe de um Veículo
class Veiculo():
    def __init__(self, x, y, tipo, direcao):
        self.x = x
        self.y = y
        self.tipo = tipo #Vê se é carro/ambulância
        self.direcao = direcao

#Classe da Direcao do semáforo/veículo
class Direcao():
    def __init__(self, cima, baixo, esquerda, direita):
        self.cima = cima
        self.baixo = baixo
        self.esquerda = esquerda
        self.direita = direita

    def transforma(self, alt, larg):
        self.cima = pygame.transform.scale(self.cima, (alt, larg))
        self.baixo = pygame.transform.scale(self.baixo, (alt, larg))
        self.esquerda = pygame.transform.scale(self.esquerda, (larg, alt))
        self.direita = pygame.transform.scale(self.direita, (larg, alt))

    def download_imagens(cor, tipo, alt, larg):
        cima    = pygame.image.load(f"imagens/{tipo}/{cor}.png")
        direita = pygame.image.load(f"imagens/{tipo}/{cor}_right.png")

        if cor != "grey":
            baixo  = pygame.image.load(f"imagens/{tipo}/{cor}_upsidedown.png")
            esquerda  = pygame.image.load(f"imagens/{tipo}/{cor}_left.png")
            direcao = Direcao(cima, baixo, esquerda, direita)
        else:
            direcao = Direcao(cima, cima, direita, direita)
        direcao.transforma(alt, larg)
        return direcao

# Direções para cada semaforo
tamanho_semaforo = largura // (num_linhas*6)
verde    = Direcao.download_imagens("green", "sinais", tamanho_semaforo, tamanho_semaforo)
amarelo  = Direcao.download_imagens("yellow", "sinais", tamanho_semaforo, tamanho_semaforo)
vermelho = Direcao.download_imagens("red", "sinais", tamanho_semaforo, tamanho_semaforo)
cinza    = Direcao.download_imagens("grey", "sinais", tamanho_semaforo, tamanho_semaforo)

# Semaforo para cada cor
semaforo_verde = Semaforo("verde", verde)
semaforo_vermelho = Semaforo("vermelho", vermelho)
semaforo_amarelo = Semaforo("amarelo", amarelo)
semaforo_cinza = Semaforo("cinza", cinza)

# Direções para cada carro
larg_carro = largura // (num_linhas*8)
alt_carro = largura // (num_linhas*5)
carro_v = Direcao.download_imagens("red", "carros", larg_carro, alt_carro)
carro_a = Direcao.download_imagens("blue", "carros", larg_carro, alt_carro)
carro_p = Direcao.download_imagens("black", "carros", larg_carro, alt_carro)

#Veículos
x,y = 0, 0
carro_vermelho = Veiculo(x, y, "carro", carro_v)
carro_azul = Veiculo(x, y, "carro", carro_a)
carro_preto = Veiculo(x, y, "carro", carro_p)

# Restrição para a área onde desenhar o tracejado
def restricao(x):
    tamanho_preto = (largura - (num_linhas*tamanho_espessura)) // num_linhas
    areas_excluidas = [False] * largura

    exclusoes = []
    y = tamanho_espessura//2
    while y < largura:
        exclusoes.append(y)
        y += tamanho_preto + tamanho_espessura

    # Marca as áreas de exclusão
    for exclusao in exclusoes:
        inicio_exclusao = exclusao
        fim_exclusao = exclusao + tamanho_preto
        for i in range(inicio_exclusao, fim_exclusao):
            if i < largura:
                areas_excluidas[i] = True

    return areas_excluidas[x]

# Desenha a linha tracejada na horizontal
def desenha_linha_tracejada_horizontal(screen, x, y, tamanho_tracejado):
    while x < largura:
        if restricao(x):
            pygame.draw.line(screen, Cores.BLACK, (x, y), (x + tamanho_tracejado, y), 2)
        x += tamanho_tracejado * 3

# Desenha a linha tracejada na vertical
def desenha_linha_tracejada_vertical(screen, x, tamanho_tracejado):
    y=0
    while y < altura:
        pygame.draw.line(screen, Cores.BLACK, (x, y), (x, y + tamanho_tracejado), 2)
        y += tamanho_tracejado * 3

# Desenha a estrada
def desenha_estrada(screen, cor):
    espessura_linha = largura // num_linhas
    for x in range(0, largura + 1, espessura_linha):
        pygame.draw.line(screen, cor, (x, 0), (x, altura), tamanho_espessura)
        desenha_linha_tracejada_vertical(screen, x, 5)
        for y in range(0, altura + 1, espessura_linha):
            pygame.draw.line(screen, cor, (0, y), (largura, y), tamanho_espessura)
            desenha_linha_tracejada_horizontal(screen, 0, y, 5)

#Retorna uma lista com o indice dos semaforos na posicao cima
def cima():
    x=(2*num_linhas)-1
    resultado = []
    inicio_intervalo = 0
    fim_intervalo = x

    while inicio_intervalo < (x + 1) ** 2:
        for numero in range(inicio_intervalo, fim_intervalo + 1):
            if numero % 2 == 0:
                resultado.append(numero)

        inicio_intervalo = fim_intervalo + x + 2
        fim_intervalo = inicio_intervalo + x

    return resultado

#Retorna uma lista com o indice dos semaforos na posicao direita
def direita():
    x=(2*num_linhas)-1
    lista_cima = cima()
    numeros_pares = []
    for numero in range(2, (x + 1) ** 2, 2):
        if numero not in lista_cima:
            numeros_pares.append(numero)

    return numeros_pares

#Retorna uma lista com o indice dos semaforos na posicao esquerda
def esquerda():
    x=(2*num_linhas)-1
    resultado = []
    inicio_intervalo = 0
    fim_intervalo = x

    while inicio_intervalo < (x + 1) ** 2:
        for numero in range(inicio_intervalo, fim_intervalo + 1):
            if numero % 2 != 0:
                resultado.append(numero)

        inicio_intervalo = fim_intervalo + x + 2
        fim_intervalo = inicio_intervalo + x

    return resultado

#Retorna uma lista com o indice dos semaforos na posicao invertida
def baixo():
    x = (2 * num_linhas) - 1
    lista_esquerda = esquerda()
    numeros_impares = []
    for numero in range(1, (x + 1) ** 2, 2):
        if numero not in lista_esquerda:
            numeros_impares.append(numero)

    return numeros_impares

#Retorna uma lista com as coordenadas para todos os semaforos
def calcula_coordenadas_semaforos():
    tamanho_preto_ = (largura - (num_linhas * tamanho_espessura)) // num_linhas
    tamanho_preto = tamanho_preto_ - 0.15 * tamanho_preto_
    tamanho_preto = int(tamanho_preto)
    coordenadas = []

    for x in range(int(tamanho_espessura / 2.7), largura, tamanho_espessura + tamanho_preto_):
        for y in range(int(tamanho_espessura / 2.2), largura, tamanho_espessura + tamanho_preto_):
            x_cima = x
            y_cima = y
            x_baixo = x + tamanho_preto
            y_baixo = y + tamanho_preto
            x_direita = x
            y_direita = y + tamanho_preto
            x_esquerda = x + tamanho_preto
            y_esquerda = y

            coordenadas.append((x_cima, y_cima))
            coordenadas.append((x_baixo, y_baixo))
            coordenadas.append((x_direita, y_direita))
            coordenadas.append((x_esquerda, y_esquerda))

    coordenadas_ordenadas = sorted(coordenadas, key=lambda tupla: (tupla[1], tupla[0]))
    for i in esquerda():
        tupla = coordenadas_ordenadas[i]
        nova = list(tupla)
        nova[1] -= 0.05*tamanho_preto
        coordenadas_ordenadas[i] = tuple(nova)
    for i in direita():
        tupla = coordenadas_ordenadas[i]
        nova = list(tupla)
        nova[0] += 0.05*tamanho_preto
        coordenadas_ordenadas[i] = tuple(nova)
    for i in baixo():
        tupla = coordenadas_ordenadas[i]
        nova = list(tupla)
        nova[0] += 0.07*tamanho_preto
        nova[1] -= 0.03*tamanho_preto
        coordenadas_ordenadas[i] = tuple(nova)
    return coordenadas_ordenadas

# Lista com todas as coordenadas dos semáforos
coordenadas_semaforos = calcula_coordenadas_semaforos()

#Desenha todos os semaforos
def desenha_semaforos(screen, semaforo):
    posicao = 0
    while posicao< len(coordenadas_semaforos):
        x,y = coordenadas_semaforos[posicao]
        if posicao in cima():
            screen.blit(semaforo.direcao.cima, (x, y))
        elif posicao in esquerda():
            screen.blit(semaforo.direcao.esquerda, (x, y))
        elif posicao in direita():
            screen.blit(semaforo.direcao.direita, (x, y))
        elif posicao in baixo():
            screen.blit(semaforo.direcao.baixo, (x, y))
        posicao +=1

#Liga o semaforo da posicao pedida
def liga_semaforo(screen, posicao, semaforo):
    x,y = coordenadas_semaforos[posicao]
    if posicao in cima():
        screen.blit(semaforo.direcao.cima, (x, y))
    if posicao in esquerda():
        screen.blit(semaforo.direcao.esquerda, (x, y))
    if posicao in direita():
        screen.blit(semaforo.direcao.direita, (x, y))
    if posicao in baixo():
        screen.blit(semaforo.direcao.baixo, (x, y))

#Desenha o carro no inicio da estrada pedida
def inicia_carro(screen, carro, estrada, direcao):
    tamanho_preto_ = (largura - (num_linhas*tamanho_espessura)) // num_linhas
    tamanho_preto1 = tamanho_preto_ - 0.3*tamanho_preto_
    tamanho_preto1 = int(tamanho_preto1)
    tamanho_preto2 = tamanho_preto_ + 0.25*tamanho_preto_
    tamanho_preto2 = int(tamanho_preto2)
    tamanho_preto3 = tamanho_preto_ + 0.3*tamanho_preto_
    tamanho_preto3 = int(tamanho_preto3)
    tamanho_preto4 = tamanho_preto_ - 0.1*tamanho_preto_
    tamanho_preto4 = int(tamanho_preto4)
    if direcao == "cima":
        carro.x = tamanho_espessura//10 + estrada*(tamanho_espessura+tamanho_preto_)
        carro.y = altura - alt_carro
    if direcao == "esquerda":
        carro.x = largura - alt_carro
        carro.y = tamanho_espessura//2 + tamanho_preto_ + estrada*(tamanho_espessura+tamanho_preto_)
    if direcao == "direita":
        carro.x = 0
        carro.y = tamanho_espessura//2 + tamanho_preto3 + estrada*(tamanho_espessura+tamanho_preto_)
    if direcao == "baixo":
        carro.x = tamanho_espessura//10 + tamanho_preto2 + estrada*(tamanho_espessura+tamanho_preto_)
        carro.y = 0

# Desenha o carro nas suas coordenadas
def desenha_carro(screen, carro, direcao):
    if direcao == "cima":
        screen.blit(carro.direcao.cima, (carro.x, carro.y))
    if direcao == "esquerda":
        screen.blit(carro.direcao.esquerda, (carro.x, carro.y))
    if direcao == "direita":
        screen.blit(carro.direcao.direita, (carro.x, carro.y))
    if direcao == "baixo":
        screen.blit(carro.direcao.baixo, (carro.x, carro.y))

# Lista de coordenadas onde o carro encontra semáforos
def paragem_carro(direcao):
    coordenadas=set()
    if direcao=="cima":
        coord = cima()
        for c in coord:
            y_coord = coordenadas_semaforos[c][1]
            coordenadas.add(int(y_coord+tamanho_semaforo//2))
    if direcao=="baixo":
        coord = baixo()
        for c in coord:
            y_coord = coordenadas_semaforos[c][1]
            coordenadas.add(int(y_coord-tamanho_semaforo//2))
    if direcao=="direita":
        coord = esquerda()
        for c in coord:
            x_coord = coordenadas_semaforos[c][0]
            coordenadas.add(int(x_coord-tamanho_semaforo//2))
    if direcao=="esquerda":
        coord = direita()
        for c in coord:
            x_coord = coordenadas_semaforos[c][0]
            coordenadas.add(int(x_coord+tamanho_semaforo//2))
    coordenadas_ordenadas = sorted(coordenadas)
    return coordenadas_ordenadas

'''
async def main():
    # Configurações iniciais
    pygame.init()
    screen = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Controle de Tráfego")
    # Limpar a tela
    screen.fill(Cores.BLACK)

    desenha_estrada(screen, Cores.GREY)
    desenha_semaforos(screen, semaforo_cinza)
    liga_semaforo(screen, 10, semaforo_verde)
    liga_semaforo(screen, 17, semaforo_amarelo)
    liga_semaforo(screen, 5, semaforo_vermelho)
    pygame.display.update()

    # Loop principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #inicia_carro(screen, carro_vermelho, 1, "direita")
        #desenha_carro(screen, carro_vermelho, "direita")
        #desenha_carro(screen, carro_preto, 1, "esquerda")
        #desenha_carro(screen, carro_azul, 0, "cima")

if __name__ == "__main__":
    spade.run(main())
'''
