import pygame
import sys

# Inicializando o Pygame
pygame.init()

# Configurações da tela
largura_tela = 800
altura_tela = 600
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Jogo Estilo Celeste - Níveis e Obstáculos")

# Cores
azul_claro = (135, 206, 235)
branco = (255, 255, 255)
preto = (0, 0, 0)
vermelho = (255, 0, 0)

# Música e sons
pygame.mixer.music.load("som_fundo.mp3")  # Música de fundo
pygame.mixer.music.play(-1)  # Música toca em loop (-1)
som_pulo = pygame.mixer.Sound("som_pulo.mp3")
som_dash = pygame.mixer.Sound("som_dash.mp3")
som_colisao = pygame.mixer.Sound("som_colisao.mp3")
som_morte = pygame.mixer.Sound("som_morte.mp3")

# Configurações do jogador
largura_jogador = 50
altura_jogador = 50
velocidade_jogador = 5
velocidade_pulo = -15
gravidade = 1
velocidade_dash = 20
tempo_dash = 10  # Quanto tempo (em frames) o dash dura

# Configurações de vida do jogador
vidas_iniciais = 3

# Classe do jogador
class Jogador:
    def __init__(self):
        self.rect = pygame.Rect(100, altura_tela - altura_jogador - 100, largura_jogador, altura_jogador)
        self.vel_x = 0
        self.vel_y = 0
        self.no_chao = False
        self.pulos_disponiveis = 1  # Um pulo duplo, estilo Celeste
        self.dash_disponivel = True
        self.dash_count = 0
        self.ultimo_checkpoint = (100, altura_tela - altura_jogador - 100)  # Posição do último checkpoint
        self.vidas = vidas_iniciais

    def mover(self, teclas):
        # Movimento horizontal
        self.vel_x = 0
        if teclas[pygame.K_LEFT]:
            self.vel_x = -velocidade_jogador
        if teclas[pygame.K_RIGHT]:
            self.vel_x = velocidade_jogador

        # Pular
        if teclas[pygame.K_SPACE] and self.no_chao:
            self.vel_y = velocidade_pulo
            self.no_chao = False
            self.pulos_disponiveis -= 1
            som_pulo.play()
        elif teclas[pygame.K_SPACE] and self.pulos_disponiveis > 0:
            self.vel_y = velocidade_pulo
            self.pulos_disponiveis -= 1
            som_pulo.play()

        # Dash (impulso)
        if teclas[pygame.K_LSHIFT] and self.dash_disponivel:
            if teclas[pygame.K_LEFT]:
                self.vel_x = -velocidade_dash
            elif teclas[pygame.K_RIGHT]:
                self.vel_x = velocidade_dash
            elif teclas[pygame.K_UP]:
                self.vel_y = -velocidade_dash
            elif teclas[pygame.K_DOWN]:
                self.vel_y = velocidade_dash
            self.dash_disponivel = False
            self.dash_count = tempo_dash  # O dash dura um certo tempo
            som_dash.play()

    def aplicar_gravidade(self):
        if not self.no_chao:
            self.vel_y += gravidade
        else:
            self.vel_y = 0

    def atualizar(self, plataformas, espinhos, inimigos, plataformas_desaparecendo, checkpoints):
        # Aplica a movimentação e a gravidade
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Check para resetar dash após tocar o chão
        if self.no_chao:
            self.dash_disponivel = True
            self.pulos_disponiveis = 1  # Reseta o pulo duplo

        # Impede que o jogador saia da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > largura_tela:
            self.rect.right = largura_tela

        # Verifica colisão com o chão (plataforma)
        self.no_chao = False
        for plataforma in plataformas + plataformas_desaparecendo:
            if self.rect.colliderect(plataforma.rect) and plataforma.visivel:
                # Se o jogador está caindo
                if self.vel_y > 0:
                    self.rect.bottom = plataforma.rect.top
                    self.no_chao = True
                    self.vel_y = 0

        # Verifica colisão com os espinhos
        for espinho in espinhos:
            if self.rect.colliderect(espinho.rect):
                # Se colidir com espinhos, o jogador "morre"
                self.morrer()

        # Verifica colisão com os inimigos
        for inimigo in inimigos:
            inimigo.mover()  # Move os inimigos
            if self.rect.colliderect(inimigo.rect):
                # Se colidir com inimigos, o jogador "morre"
                self.morrer()

        # Verifica se o jogador passou por um checkpoint
        for checkpoint in checkpoints:
            if self.rect.colliderect(checkpoint.rect):
                self.ultimo_checkpoint = (self.rect.x, self.rect.y)

        # Contagem de dash
        if self.dash_count > 0:
            self.dash_count -= 1
        elif self.dash_count == 0:
            self.dash_disponivel = True

    def desenhar(self):
        pygame.draw.rect(tela, branco, self.rect)

    def morrer(self):
        # Reduz uma vida
        self.vidas -= 1
        som_morte.play()

        # Se o jogador ainda tiver vidas, volta ao checkpoint
        if self.vidas > 0:
            self.rect.x, self.rect.y = self.ultimo_checkpoint
            self.vel_x = 0
            self.vel_y = 0
        else:
            # Se não tiver mais vidas, exibe a tela de "Game Over"
            tela_game_over()

# Classe para plataformas
class Plataforma:
    def __init__(self, x, y, largura, altura, desaparecendo=False):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.desaparecendo = desaparecendo
        self.visivel = True
        self.timer = 0

    def desenhar(self):
        if self.visivel:
            pygame.draw.rect(tela, preto, self.rect)

    def atualizar(self):
        if self.desaparecendo:
            self.timer += 1
            if self.timer % 100 == 0:  # Alterna visibilidade mais rapidamente em níveis mais difíceis
                self.visivel = not self.visivel

# Classe para espinhos (obstáculos)
class Espinho:
    def __init__(self, x, y, largura, altura):
        self.rect = pygame.Rect(x, y, largura, altura)

    def desenhar(self):
        pygame.draw.rect(tela, vermelho, self.rect)

# Classe para inimigos móveis
class Inimigo:
    def __init__(self, x, y, largura, altura, limite_esquerda, limite_direita, velocidade):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.limite_esquerda = limite_esquerda
        self.limite_direita = limite_direita
        self.velocidade = velocidade
        self.direcao = 1  # 1 para direita, -1 para esquerda

    def mover(self):
        self.rect.x += self.velocidade * self.direcao
        if self.rect.right >= self.limite_direita or self.rect.left <= self.limite_esquerda:
            self.direcao *= -1  # Inverte a direção

    def desenhar(self):
        pygame.draw.rect(tela, (255, 165, 0), self.rect)  # Cor dos inimigos: laranja

# Classe para checkpoints
class Checkpoint:
    def __init__(self, x, y, largura, altura):
        self.rect = pygame.Rect(x, y, largura, altura)

    def desenhar(self):
        pygame.draw.rect(tela, (0, 255, 0), self.rect)  # Checkpoint será verde

# Função para carregar as plataformas, espinhos, inimigos e checkpoints de um nível
def carregar_nivel(nivel):
    # Aumenta a dificuldade conforme o nível
    velocidade_inimigo = 2 + nivel  # Aumenta a velocidade dos inimigos a cada nível
    plataformas_desaparecendo_rapidez = max(100 - (nivel * 10), 50)  # Diminui o tempo de visibilidade das plataformas que desaparecem

    if nivel == 0:
        plataformas = [
            Plataforma(0, altura_tela - 30, largura_tela, 30),  # Chão
            Plataforma(200, altura_tela - 150, 200, 20),  # Plataforma no meio
        ]
        espinhos = [
            Espinho(400, altura_tela - 40, 30, 30),  # Espinho no chão
        ]
        inimigos = [
            Inimigo(300, altura_tela - 180, 50, 50, 200, 400, velocidade_inimigo),  # Inimigo móvel
        ]
        plataformas_desaparecendo = []
        checkpoints = [
            Checkpoint(550, altura_tela - 350, 20, 20),  # Checkpoint no final
        ]
    elif nivel == 1:
        plataformas = [
            Plataforma(0, altura_tela - 30, largura_tela, 30),  # Chão
            Plataforma(100, altura_tela - 150, 150, 20),  # Plataforma 1
            Plataforma(500, altura_tela - 350, 150, 20),  # Plataforma 3
        ]
        espinhos = [
            Espinho(250, altura_tela - 160, 30, 30),  # Espinho em uma plataforma
        ]
        inimigos = [
            Inimigo(400, altura_tela - 180, 50, 50, 300, 600, velocidade_inimigo),  # Inimigo móvel
        ]
        plataformas_desaparecendo = [
            Plataforma(500, altura_tela - 350, 150, 20, desaparecendo=True),  # Plataforma que desaparece
        ]
        checkpoints = [
            Checkpoint(700, altura_tela - 470, 20, 20),  # Checkpoint no final
        ]
    elif nivel == 2:
        plataformas = [
            Plataforma(0, altura_tela - 30, largura_tela, 30),  # Chão
            Plataforma(150, altura_tela - 150, 100, 20),  # Plataforma 1
            Plataforma(400, altura_tela - 300, 150, 20),  # Plataforma 2
        ]
        espinhos = [
            Espinho(200, altura_tela - 160, 50, 30),  # Espinhos largos
        ]
        inimigos = [
            Inimigo(400, altura_tela - 180, 50, 50, 200, 600, velocidade_inimigo),  # Inimigo móvel
        ]
        plataformas_desaparecendo = []
        checkpoints = [
            Checkpoint(600, altura_tela - 620, 20, 20),  # Checkpoint no final
        ]
    else:
        plataformas = []
        espinhos = []
        inimigos = []
        plataformas_desaparecendo = []
        checkpoints = []

    return plataformas, espinhos, inimigos, plataformas_desaparecendo, checkpoints

# Função para a tela de início
def tela_inicio():
    tela.fill(azul_claro)
    fonte = pygame.font.SysFont("Arial", 50)
    texto = fonte.render("Pressione ENTER para começar", True, branco)
    tela.blit(texto, (100, altura_tela // 2 - 50))
    pygame.display.flip()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False

# Função para a tela de "Game Over"
def tela_game_over():
    tela.fill(preto)
    fonte = pygame.font.SysFont("Arial", 50)
    texto = fonte.render("Game Over", True, vermelho)
    texto2 = fonte.render("Pressione R para reiniciar ou ESC para sair", True, branco)
    tela.blit(texto, (300, altura_tela // 2 - 100))
    tela.blit(texto2, (100, altura_tela // 2 + 50))
    pygame.display.flip()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:  # Reinicia o jogo
                    esperando = False
                    jogo()
                elif evento.key == pygame.K_ESCAPE:  # Sai do jogo
                    pygame.quit()
                    sys.exit()

# Função principal do jogo
def jogo():
    jogador = Jogador()
    nivel_atual = 0

    # Carrega as plataformas, espinhos, inimigos e checkpoints do nível atual
    plataformas, espinhos, inimigos, plataformas_desaparecendo, checkpoints = carregar_nivel(nivel_atual)

    relogio = pygame.time.Clock()
    jogando = True

    while jogando:
        # Processa eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Captura as teclas pressionadas
        teclas = pygame.key.get_pressed()

        # Movimenta o jogador
        jogador.mover(teclas)

        # Aplica a gravidade ao jogador
        jogador.aplicar_gravidade()

        # Atualiza a posição do jogador e verifica colisões
        jogador.atualizar(plataformas, espinhos, inimigos, plataformas_desaparecendo, checkpoints)

        # Verifica se o jogador atingiu o final do nível (lado direito da tela)
        if jogador.rect.right >= largura_tela:
            nivel_atual += 1
            # Se não houver mais níveis, o jogo termina
            if nivel_atual > 2:
                print("Você completou todos os níveis!")
                jogando = False
            else:
                # Carrega o próximo nível
                jogador.rect.x = 50  # Reseta a posição do jogador
                jogador.rect.y = altura_tela - altura_jogador - 100
                plataformas, espinhos, inimigos, plataformas_desaparecendo, checkpoints = carregar_nivel(nivel_atual)

        # Preenche o fundo da tela
        tela.fill(azul_claro)

        # Atualiza e desenha as plataformas desaparecendo
        for plataforma in plataformas_desaparecendo:
            plataforma.atualizar()

        # Desenha o jogador, plataformas, espinhos, inimigos e checkpoints
        jogador.desenhar()
        for plataforma in plataformas:
            plataforma.desenhar()
        for espinho in espinhos:
            espinho.desenhar()
        for inimigo in inimigos:
            inimigo.desenhar()
        for plataforma in plataformas_desaparecendo:
            plataforma.desenhar()
        for checkpoint in checkpoints:
            checkpoint.desenhar()

        # Atualiza a tela
        pygame.display.flip()

        # Define a taxa de quadros
        relogio.tick(60)

# Tela de início
tela_inicio()

# Executa o jogo
jogo()