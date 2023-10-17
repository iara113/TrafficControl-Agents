import sys
import pygame

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
tamanho_espessura = largura // (num_linhas*3) #espessura da estrada

class Sinal():
    def __init__(self, normal, invertido, direita, esquerda):
        self.normal = normal
        self.invertido = invertido
        self.direita = direita
        self.esquerda = esquerda


    def transforma(self, tamanho):
        self.normal = pygame.transform.scale(self.normal, (tamanho, tamanho))
        self.invertido = pygame.transform.scale(self.invertido, (tamanho, tamanho))
        self.direita = pygame.transform.scale(self.direita, (tamanho, tamanho))
        self.esquerda = pygame.transform.scale(self.esquerda, (tamanho, tamanho))


class Carro():
    def __init__(self, normal, invertido, direita, esquerda):
        self.normal = normal
        self.invertido = invertido
        self.direita = direita
        self.esquerda = esquerda


    def transforma(self, alt, larg):
        self.normal = pygame.transform.scale(self.normal, (alt, larg))
        self.invertido = pygame.transform.scale(self.invertido, (alt, larg))
        self.direita = pygame.transform.scale(self.direita, (larg, alt))
        self.esquerda = pygame.transform.scale(self.esquerda, (larg, alt))

#Sinais de transito
tamanho_sinal = largura // (num_linhas*6)
Sinal_vermelho = Sinal(pygame.image.load('Imagens/sinais/red.png'), pygame.image.load('Imagens/sinais/red_upsidedown.png'),\
                       pygame.image.load('Imagens/sinais/red_right.png'), pygame.image.load('Imagens/sinais/red_left.png'))
Sinal_vermelho.transforma(tamanho_sinal)

Sinal_amarelo = Sinal(pygame.image.load('Imagens/sinais/yellow.png'), pygame.image.load('Imagens/sinais/yellow_upsidedown.png'),\
                       pygame.image.load('Imagens/sinais/yellow_right.png'), pygame.image.load('Imagens/sinais/yellow_left.png'))
Sinal_amarelo.transforma(tamanho_sinal)

Sinal_verde = Sinal(pygame.image.load('Imagens/sinais/green.png'), pygame.image.load('Imagens/sinais/green_upsidedown.png'),\
                       pygame.image.load('Imagens/sinais/green_right.png'), pygame.image.load('Imagens/sinais/green_left.png'))
Sinal_verde.transforma(tamanho_sinal)

#Carro
larg_carro = largura // (num_linhas*8)
alt_carro = largura // (num_linhas*5)
Carro_vermelho = Carro(pygame.image.load('Imagens/carros/red.png'), pygame.image.load('Imagens/carros/red_upsidedown.png'),\
                       pygame.image.load('Imagens/carros/red_right.png'), pygame.image.load('Imagens/carros/red_left.png'))
Carro_vermelho.transforma(larg_carro, alt_carro)

def restricao(x):
    tamanho_preto = (largura - (num_linhas*tamanho_espessura)) // num_linhas
    areas_excluidas = [False] * largura

    exclusoes = []
    y = tamanho_espessura//2
    while y < largura:
        exclusoes.append(y)
        y += tamanho_preto + tamanho_espessura

    # Marque as áreas de exclusão
    for exclusao in exclusoes:
        inicio_exclusao = exclusao
        fim_exclusao = exclusao + tamanho_preto
        for i in range(inicio_exclusao, fim_exclusao):
            if i < largura:
                areas_excluidas[i] = True

    if areas_excluidas[x]:
        return True
    else:
        return False

def desenha_linha_tracejada_horizontal(screen, x, y, tamanho_tracejado):
    while x < largura:
        if restricao(x):
            pygame.draw.line(screen, Cores.BLACK, (x, y), (x + tamanho_tracejado, y), 2)
        x += tamanho_tracejado * 3

def desenha_linha_tracejada_vertical(screen, x, tamanho_tracejado):
    y=0
    while y < altura:
        pygame.draw.line(screen, Cores.BLACK, (x, y), (x, y + tamanho_tracejado), 2)
        y += tamanho_tracejado * 3

def desenha_estrada(screen, cor):
    espessura_linha = largura // num_linhas
    for x in range(0, largura + 1, espessura_linha):
        pygame.draw.line(screen, cor, (x, 0), (x, altura), tamanho_espessura)
        desenha_linha_tracejada_vertical(screen, x, 5)
        for y in range(0, altura + 1, espessura_linha):
            pygame.draw.line(screen, cor, (0, y), (largura, y), tamanho_espessura)
            desenha_linha_tracejada_horizontal(screen, 0, y, 5)

def desenha_sinais(screen, sinal):
    tamanho_preto_ = (largura - (num_linhas*tamanho_espessura)) // num_linhas
    tamanho_preto = tamanho_preto_ - 0.1*tamanho_preto_
    tamanho_preto = int(tamanho_preto)
    for x in range(tamanho_espessura//3, largura, tamanho_espessura+tamanho_preto_):
        for y in range(tamanho_espessura//3, largura, tamanho_espessura+tamanho_preto_):
            # Calcula a posição das imagens nas interseções da grade
            x_normal = x
            y_normal = y
            x_invertido = x+tamanho_preto
            y_invertido = y+tamanho_preto
            x_esquerda = x
            y_esquerda = y+tamanho_preto
            x_direita = x+tamanho_preto
            y_direita = y
            # Desenha as imagens
            screen.blit(sinal.normal, (x_normal, y_normal))
            screen.blit(sinal.invertido, (x_invertido, y_invertido))
            screen.blit(sinal.esquerda, (x_esquerda, y_esquerda))
            screen.blit(sinal.direita, (x_direita, y_direita))

def desenha_carros(screen, carro):
    tamanho_preto_ = (largura - (num_linhas*tamanho_espessura)) // num_linhas
    tamanho_preto1 = tamanho_preto_ - 0.3*tamanho_preto_
    tamanho_preto1 = int(tamanho_preto1)
    tamanho_preto2 = tamanho_preto_ + 0.25*tamanho_preto_
    tamanho_preto2 = int(tamanho_preto2)
    tamanho_preto3 = tamanho_preto_ + 0.3*tamanho_preto_
    tamanho_preto3 = int(tamanho_preto3)
    tamanho_preto4 = tamanho_preto_ - 0.1*tamanho_preto_
    tamanho_preto4 = int(tamanho_preto4)
    for x in range(tamanho_espessura//10, largura, tamanho_espessura+tamanho_preto_):
        for y in range(tamanho_espessura//2, largura, tamanho_espessura+tamanho_preto_):
            # Calcula a posição das imagens nas interseções da grade
            x_normal = x
            y_normal = y
            x_invertido = x+tamanho_preto2
            y_invertido = y+tamanho_preto1
            x_esquerda = x+tamanho_preto4
            y_esquerda = y+tamanho_preto3
            x_direita = x - tamanho_preto3
            y_direita = y+tamanho_preto_
            #Desenha as imagens
            screen.blit(carro.normal, (x_normal, y_normal))
            screen.blit(carro.invertido, (x_invertido, y_invertido))
            screen.blit(carro.esquerda, (x_esquerda, y_esquerda))
            screen.blit(carro.direita, (x_direita, y_direita))



def main():
    # Configurações iniciais
    pygame.init()
    screen = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Controle de Tráfego")

    # Loop principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Limpar a tela
        screen.fill(Cores.BLACK)

        desenha_estrada(screen, Cores.GREY)
        desenha_sinais(screen, Sinal_vermelho)
        desenha_carros(screen, Carro_vermelho)


        pygame.display.update()

if __name__ == "__main__":
    main()
