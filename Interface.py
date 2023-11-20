import pygame

# Cores a serem usadas
class Cores:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    GREY = (128, 128, 128)


# Medidas Constantes
num_estradas = int(input('Indique quantas estradas deseja: '))
altura = 600
largura = 600
tamanho_espessura = largura // (num_estradas*3) # Espessura da estrada
global screen


# Classe de um Semáforo
class Semaforo():
    def __init__(self, cor, direcao):
        self.cor = cor
        self.direcao = direcao


# Classe de um Veículo
class Veiculo():
    def __init__(self, tipo, direcao):
        self.tipo = tipo #Vê se é carro/ambulância
        self.direcao = direcao


# Classe da Direcao do semáforo/veículo
class Direcao():
    def __init__(self, cima, baixo, esquerda, direita):
        self.cima     = cima
        self.baixo    = baixo
        self.esquerda = esquerda
        self.direita  = direita

    def transforma(self, alt, larg):
        self.cima     = pygame.transform.scale(self.cima, (alt, larg))
        self.baixo    = pygame.transform.scale(self.baixo, (alt, larg))
        self.esquerda = pygame.transform.scale(self.esquerda, (larg, alt))
        self.direita  = pygame.transform.scale(self.direita, (larg, alt))

    def download_imagens(cor, tipo, alt, larg):
        cima    = pygame.image.load(f"imagens/{tipo}/{cor}.png")
        direita = pygame.image.load(f"imagens/{tipo}/{cor}_right.png")

        # Semáforo cinza só apresenta duas direções
        if cor != "grey":
            baixo    = pygame.image.load(f"imagens/{tipo}/{cor}_upsidedown.png")
            esquerda = pygame.image.load(f"imagens/{tipo}/{cor}_left.png")
            direcao  = Direcao(cima, baixo, esquerda, direita)
        else:
            direcao = Direcao(cima, cima, direita, direita)
        direcao.transforma(alt, larg)
        return direcao


# Criação da representação dos semáforos
tamanho_semaforo = largura // (num_estradas*6)
verde    = Direcao.download_imagens("green", "sinais", tamanho_semaforo, tamanho_semaforo)
amarelo  = Direcao.download_imagens("yellow", "sinais", tamanho_semaforo, tamanho_semaforo)
vermelho = Direcao.download_imagens("red", "sinais", tamanho_semaforo, tamanho_semaforo)
cinza    = Direcao.download_imagens("grey", "sinais", tamanho_semaforo, tamanho_semaforo)

semaforo_verde    = Semaforo("verde", verde)
semaforo_vermelho = Semaforo("vermelho", vermelho)
semaforo_amarelo  = Semaforo("amarelo", amarelo)
semaforo_cinza    = Semaforo("cinza", cinza)


# Criação da representação dos carros
larg_carro = largura // (num_estradas*8)
alt_carro  = altura // (num_estradas*5)

dir_vemelho    = Direcao.download_imagens("red", "carros", larg_carro, alt_carro)
dir_amarelo    = Direcao.download_imagens("blue", "carros", larg_carro, alt_carro)
dir_preto      = Direcao.download_imagens("black", "carros", larg_carro, alt_carro)
dir_verde      = Direcao.download_imagens("green", "carros", larg_carro, alt_carro)
dir_mota       = Direcao.download_imagens("motorcycle", "carros", larg_carro, alt_carro)
dir_ambulancia = Direcao.download_imagens("ambulance", "ambulancias", larg_carro, alt_carro)

carro_vermelho = Veiculo("carro", dir_vemelho)
carro_azul     = Veiculo("carro", dir_amarelo)
carro_preto    = Veiculo("carro", dir_preto)
carro_verde    = Veiculo("carro", dir_verde)
mota           = Veiculo("carro", dir_mota)
ambulancia     = Veiculo("ambulancia", dir_ambulancia)


# Restrição para a área onde desenhar o tracejado
def restricao(x):
    tamanho_asfalto = (largura - (num_estradas*tamanho_espessura)) // num_estradas
    areas_excluidas = [False] * largura

    exclusoes = []

    y = tamanho_espessura // 2
    while y < largura:
        exclusoes.append(y)
        y += tamanho_asfalto + tamanho_espessura

    # Marca as áreas de exclusão
    for exclusao in exclusoes:
        inicio_exclusao = exclusao
        fim_exclusao    = exclusao + tamanho_asfalto

        for i in range(inicio_exclusao, fim_exclusao):
            if i < largura:
                areas_excluidas[i] = True

    return areas_excluidas[x]


def desenha_linha_tracejada_horizontal(x, y, tamanho_tracejado):
    while x < largura:
        if restricao(x):
            pygame.draw.line(screen, Cores.BLACK, (x, y), (x + tamanho_tracejado, y), 2)
        x += tamanho_tracejado * 3


def desenha_linha_tracejada_vertical(x, tamanho_tracejado):
    y=0
    while y < altura:
        pygame.draw.line(screen, Cores.BLACK, (x, y), (x, y + tamanho_tracejado), 2)
        y += tamanho_tracejado * 3


def desenha_estrada(cor):
    espessura_linha = largura // num_estradas
    for x in range(0, largura + 1, espessura_linha):
        pygame.draw.line(screen, cor, (x, 0), (x, altura), tamanho_espessura)
        desenha_linha_tracejada_vertical(x, 5)
        for y in range(0, altura + 1, espessura_linha):
            pygame.draw.line(screen, cor, (0, y), (largura, y), tamanho_espessura)
            desenha_linha_tracejada_horizontal(0, y, 5)


# Retorna uma lista com o indice dos semaforos na posicao cima
def cima():
    x=(2*num_estradas)-1
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

# Retorna uma lista com o indice dos semaforos na posicao esquerda
def esquerda():
    x=(2*num_estradas)-1
    lista_cima = cima()
    numeros_pares = []
    for numero in range(2, (x + 1) ** 2, 2):
        if numero not in lista_cima:
            numeros_pares.append(numero)

    return numeros_pares

# Retorna uma lista com o indice dos semaforos na posicao direita
def direita():
    x=(2*num_estradas)-1
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

# Retorna uma lista com o indice dos semaforos na posicao invertida
def baixo():
    x = (2 * num_estradas) - 1
    lista_esquerda = direita()
    numeros_impares = []
    for numero in range(1, (x + 1) ** 2, 2):
        if numero not in lista_esquerda:
            numeros_impares.append(numero)

    return numeros_impares


# Retorna uma lista com as coordenadas para todos os semaforos
def calcula_coordenadas_semaforos():
    aux_asfalto = (largura - (num_estradas * tamanho_espessura)) // num_estradas
    tamanho_asfalto = int(aux_asfalto - 0.15 * aux_asfalto)
    coordenadas = []

    for x in range(int(tamanho_espessura / 2.7), largura, tamanho_espessura + aux_asfalto):
        for y in range(int(tamanho_espessura / 2.2), largura, tamanho_espessura + aux_asfalto):
            # De cima para baixo: Coordenadas de cima, baixo, esquerda e direita
            coordenadas.append((x, y))
            coordenadas.append((x + tamanho_asfalto, y + tamanho_asfalto))
            coordenadas.append((x, y + tamanho_asfalto))
            coordenadas.append((x + tamanho_asfalto, y))

    coordenadas_ordenadas = sorted(coordenadas, key=lambda tupla: (tupla[1], tupla[0]))

    for i in direita():
        tupla = coordenadas_ordenadas[i]
        nova = list(tupla)
        nova[1] -= 0.05*tamanho_asfalto
        coordenadas_ordenadas[i] = tuple(nova)

    for i in esquerda():
        tupla = coordenadas_ordenadas[i]
        nova = list(tupla)
        nova[0] += 0.05*tamanho_asfalto
        coordenadas_ordenadas[i] = tuple(nova)

    for i in baixo():
        tupla = coordenadas_ordenadas[i]
        nova = list(tupla)
        nova[0] += 0.07*tamanho_asfalto
        nova[1] -= 0.03*tamanho_asfalto
        coordenadas_ordenadas[i] = tuple(nova)

    return coordenadas_ordenadas

# Lista com todas as coordenadas dos semáforos
coordenadas_semaforos = calcula_coordenadas_semaforos()

#Desenha todos os semaforos
def desenha_semaforos(semaforo):
    posicao = 0
    while posicao< len(coordenadas_semaforos):
        x,y = coordenadas_semaforos[posicao]
        if posicao in cima():
            screen.blit(semaforo.direcao.cima, (x, y))
        elif posicao in direita():
            screen.blit(semaforo.direcao.direita, (x, y))
        elif posicao in esquerda():
            screen.blit(semaforo.direcao.esquerda, (x, y))
        elif posicao in baixo():
            screen.blit(semaforo.direcao.baixo, (x, y))
        posicao +=1


#Liga o semaforo da posicao pedida
def liga_semaforo(posicao, semaforo):
    x,y = coordenadas_semaforos[posicao]
    if posicao in cima():
        screen.blit(semaforo.direcao.cima, (x, y))
    if posicao in esquerda():
        screen.blit(semaforo.direcao.esquerda, (x, y))
    if posicao in direita():
        screen.blit(semaforo.direcao.direita, (x, y))
    if posicao in baixo():
        screen.blit(semaforo.direcao.baixo, (x, y))


# Coloca o carro no inicio da estrada pedida (altera-lhe as coordenadas)
def inicia_carro(carro):
    aux_asfalto = (largura - (num_estradas*tamanho_espessura)) // num_estradas
    tamanho_asfalto1 = int(aux_asfalto + 0.05*aux_asfalto)
    tamanho_asfalto2 = int(aux_asfalto + 0.25*aux_asfalto)
    tamanho_asfalto3 = int(aux_asfalto + 0.3*aux_asfalto)

    if carro.direcao == "cima":
        carro.x = tamanho_espessura//10 + carro.estrada * (tamanho_espessura+aux_asfalto)
        carro.y = altura
    if carro.direcao == "esquerda":
        carro.x = largura
        carro.y = tamanho_espessura//2 + tamanho_asfalto1 + carro.estrada * (tamanho_espessura+aux_asfalto)
    if carro.direcao == "direita":
        carro.x = -alt_carro
        estrada = carro.estrada
        estrada -= 1
        carro.y = tamanho_espessura//2 + tamanho_asfalto3 + estrada * (tamanho_espessura+aux_asfalto)
    if carro.direcao == "baixo":
        carro.x = tamanho_espessura//10 + tamanho_asfalto2 + carro.estrada * (tamanho_espessura+aux_asfalto)
        carro.y = -alt_carro


# Desenha o carro nas suas coordenadas
def desenha_carro(carro):
    if carro.direcao == "cima":
        screen.blit(carro.carro.direcao.cima, (carro.x, carro.y))
    if carro.direcao == "esquerda":
        screen.blit(carro.carro.direcao.esquerda, (carro.x, carro.y))
    if carro.direcao == "direita":
        screen.blit(carro.carro.direcao.direita, (carro.x, carro.y))
    if carro.direcao == "baixo":
        screen.blit(carro.carro.direcao.baixo, (carro.x, carro.y))


# Lista de coordenadas onde o carro encontra semáforos
def paragem_carro(direcao):
    coordenadas=set()
    if direcao=="cima":
        coord = cima()
        for c in coord:
            y_coord = coordenadas_semaforos[c][1]
            coordenadas.add(int(y_coord+tamanho_semaforo//4))

    if direcao=="baixo":
        coord = baixo()
        for c in coord:
            y_coord = coordenadas_semaforos[c][1]
            coordenadas.add(int(y_coord-tamanho_semaforo//4))

    if direcao=="direita":
        coord = direita()
        for c in coord:
            x_coord = coordenadas_semaforos[c][0]
            coordenadas.add(int(x_coord-tamanho_semaforo//4))

    if direcao=="esquerda":
        coord = esquerda()
        for c in coord:
            x_coord = coordenadas_semaforos[c][0]
            coordenadas.add(int(x_coord+tamanho_semaforo//4))

    coordenadas_ordenadas = sorted(coordenadas)
    return coordenadas_ordenadas
